from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.article import Article
from app.models.vector_chunk import VectorChunk
from app.services.rag.cleaner import clean_markdown
from app.services.rag.embedder import get_embedder
from app.services.rag.splitter import split_text


async def sync_article_vector(db: AsyncSession, article_id: int) -> bool:
    article_result = await db.execute(select(Article).where(Article.id == article_id))
    article = article_result.scalar_one_or_none()
    if article is None or not article.content_md:
        return False

    try:
        await db.execute(
            update(Article).where(Article.id == article_id).values(vector_status="syncing")
        )
        await db.flush()

        await db.execute(delete(VectorChunk).where(VectorChunk.article_id == article_id))

        cleaned = clean_markdown(article.content_md)
        chunks = split_text(cleaned)

        if not chunks:
            await db.execute(
                update(Article).where(Article.id == article_id).values(vector_status="synced")
            )
            await db.flush()
            return True

        embedder = get_embedder()
        embeddings = embedder.encode(chunks)

        if embeddings is None:
            await db.execute(
                update(Article).where(Article.id == article_id).values(vector_status="failed")
            )
            await db.flush()
            return False

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            db.add(
                VectorChunk(
                    article_id=article_id,
                    chunk_index=i,
                    content=chunk,
                    token_count=len(chunk),
                )
            )

        await db.flush()

        # Update embeding via raw SQL since pgvector column isn't directly settable via ORM
        from sqlalchemy import text

        for i, embedding in enumerate(embeddings):
            emb_str = f"[{','.join(str(v) for v in embedding)}]"
            await db.execute(
                text("""
                    UPDATE vector_chunk
                    SET embedding = :embedding
                    WHERE article_id = :article_id AND chunk_index = :chunk_index
                """),
                {"embedding": emb_str, "article_id": article_id, "chunk_index": i},
            )

        await db.execute(
            update(Article).where(Article.id == article_id).values(vector_status="synced")
        )
        await db.flush()
        logger.info(f"Article {article_id} vector sync completed: {len(chunks)} chunks")
        return True

    except Exception as e:
        logger.error(f"Vector sync failed for article {article_id}: {e}")
        await db.execute(
            update(Article).where(Article.id == article_id).values(vector_status="failed")
        )
        await db.flush()
        return False


async def rebuild_all_vectors(db: AsyncSession) -> dict:
    result = await db.execute(select(Article.id).where(Article.content_md.isnot(None)))
    article_ids = [row[0] for row in result.all()]

    success = 0
    failed = 0
    for aid in article_ids:
        ok = await sync_article_vector(db, aid)
        if ok:
            success += 1
        else:
            failed += 1

    return {"total": len(article_ids), "success": success, "failed": failed}


async def get_knowledge_status(db: AsyncSession) -> dict:
    from sqlalchemy import func

    total_result = await db.execute(select(func.count(Article.id)))
    total_articles = total_result.scalar() or 0

    synced = await db.scalar(
        select(func.count(Article.id)).where(Article.vector_status == "synced")
    ) or 0
    syncing = await db.scalar(
        select(func.count(Article.id)).where(Article.vector_status == "syncing")
    ) or 0
    pending = await db.scalar(
        select(func.count(Article.id)).where(Article.vector_status == "pending")
    ) or 0
    failed_count = await db.scalar(
        select(func.count(Article.id)).where(Article.vector_status == "failed")
    ) or 0

    total_chunks = await db.scalar(select(func.count(VectorChunk.id))) or 0

    return {
        "total_articles": total_articles,
        "synced": synced,
        "syncing": syncing,
        "pending": pending,
        "failed": failed_count,
        "total_chunks": total_chunks,
    }
