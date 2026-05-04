from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.vector_chunk import VectorChunk


async def retrieve_similar_chunks(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float = 0.4,
) -> list[dict]:
    embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"

    sql = text("""
        SELECT
            vc.id AS chunk_id,
            vc.article_id,
            vc.content,
            vc.chunk_index,
            1 - (vc.embedding <=> :query_embedding) AS similarity,
            a.title AS article_title,
            a.slug AS article_slug
        FROM vector_chunk vc
        JOIN article a ON vc.article_id = a.id
        WHERE a.status = 'published'
            AND 1 - (vc.embedding <=> :query_embedding) >= :threshold
        ORDER BY vc.embedding <=> :query_embedding
        LIMIT :top_k
    """)

    try:
        result = await db.execute(
            sql,
            {
                "query_embedding": embedding_str,
                "threshold": threshold,
                "top_k": top_k,
            },
        )
        rows = result.all()
        return [
            {
                "chunk_id": row[0],
                "article_id": row[1],
                "content": row[2],
                "chunk_index": row[3],
                "similarity": round(float(row[4]), 4),
                "article_title": row[5],
                "article_slug": row[6],
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Vector retrieval failed: {e}")
        return []
