from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.article import ArticleDetailResponse, ArticleListResponse, SemanticSearchRequest
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.article import (
    calculate_reading_time,
    get_article_by_slug,
    get_articles,
    get_articles_by_ids,
    get_related_articles,
    increment_view_count,
)
from app.services.category import get_categories_with_count, get_category_by_slug
from app.services.comment import create_comment, get_comments_by_article, like_comment
from app.services.dashboard import get_home_data
from app.services.rag.embedder import get_embedder
from app.services.rag.retriever import retrieve_similar_chunks
from app.services.tag import get_tags, get_tag_by_id
from app.utils.response import success_response

router = APIRouter()


# Home
@router.get("/home")
async def home(db: AsyncSession = Depends(get_db)):
    data = await get_home_data(db)
    return success_response(data=data)


# Categories
@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    categories = await get_categories_with_count(db, category_type="category")
    return success_response(data=categories)


@router.get("/topics")
async def list_topics(db: AsyncSession = Depends(get_db)):
    topics = await get_categories_with_count(db, category_type="topic")
    return success_response(data=topics)


@router.get("/topics/{slug}")
async def topic_detail(slug: str, db: AsyncSession = Depends(get_db)):
    topic = await get_category_by_slug(db, slug)
    if topic is None or topic.type != "topic":
        raise HTTPException(status_code=404, detail="Topic not found")
    return success_response(data=topic)


# Tags
@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    tags = await get_tags(db)
    return success_response(data=tags)


@router.get("/tags/{tag_id}")
async def tag_detail(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return success_response(data=tag)


# Articles
@router.get("/articles")
async def list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    category_slug: str | None = None,
    topic_slug: str | None = None,
    tag_id: int | None = None,
    keyword: str | None = None,
    sort_by: str = "published_at",
    db: AsyncSession = Depends(get_db),
):
    articles, total = await get_articles(
        db,
        page=page,
        page_size=page_size,
        category_slug=category_slug,
        topic_slug=topic_slug,
        tag_id=tag_id,
        keyword=keyword,
        sort_by=sort_by,
    )
    items = []
    for a in articles:
        items.append(
            ArticleListResponse(
                id=a.id,
                title=a.title,
                summary=a.summary,
                slug=a.slug,
                cover_url=a.cover_url,
                category=a.category,
                tags=a.tags,
                view_count=a.view_count,
                reading_time=calculate_reading_time(a.content_md),
                published_at=a.published_at,
                created_at=a.created_at,
            ).model_dump()
        )
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )


@router.get("/articles/{slug}")
async def article_detail(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_slug(db, slug)
    if article is None or article.status != "published":
        raise HTTPException(status_code=404, detail="Article not found")

    related = await get_related_articles(db, article.id, article.category_id, limit=4)
    related_data = [
        ArticleListResponse(
            id=r.id, title=r.title, summary=r.summary, slug=r.slug,
            cover_url=r.cover_url, category=r.category, tags=r.tags,
            view_count=r.view_count, reading_time=calculate_reading_time(r.content_md),
            published_at=r.published_at, created_at=r.created_at,
        ).model_dump()
        for r in related
    ]

    return success_response(
        data=ArticleDetailResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            slug=article.slug,
            content_md=article.content_md,
            cover_url=article.cover_url,
            category=article.category,
            tags=article.tags,
            view_count=article.view_count,
            reading_time=calculate_reading_time(article.content_md),
            comment_count=len(article.comments) if hasattr(article, "comments") else 0,
            seo_title=article.seo_title,
            seo_description=article.seo_description,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            related_articles=related_data,
        ).model_dump()
    )


@router.post("/articles/{slug}/view")
async def article_view(slug: str, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_slug(db, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await increment_view_count(db, article.id)
    return success_response(message="ok")


# Comments
@router.get("/articles/{slug}/comments")
async def list_comments(
    slug: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    article = await get_article_by_slug(db, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    comments, total = await get_comments_by_article(db, article.id, page, page_size)
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data={
            "items": [CommentResponse.model_validate(c).model_dump() for c in comments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )


@router.post("/articles/{slug}/comments", status_code=201)
async def add_comment(slug: str, data: CommentCreate, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_slug(db, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    comment = await create_comment(db, article.id, data.nickname, data.content, data.parent_id)
    return success_response(data=CommentResponse.model_validate(comment).model_dump(), message="Comment created")


@router.post("/comments/{comment_id}/like")
async def like_comment_endpoint(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await like_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return success_response(data=CommentResponse.model_validate(comment).model_dump())


# Search
@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    articles, total = await get_articles(db, page=page, page_size=page_size, keyword=q)
    items = []
    for a in articles:
        items.append(
            ArticleListResponse(
                id=a.id,
                title=a.title,
                summary=a.summary,
                slug=a.slug,
                cover_url=a.cover_url,
                category=a.category,
                tags=a.tags,
                view_count=a.view_count,
                reading_time=calculate_reading_time(a.content_md),
                published_at=a.published_at,
                created_at=a.created_at,
            ).model_dump()
        )
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )


# Semantic search
@router.post("/search/semantic")
async def semantic_search(data: SemanticSearchRequest, db: AsyncSession = Depends(get_db)):
    embedder = get_embedder()
    query_embedding = embedder.encode_single(data.q)
    if query_embedding is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")

    chunks = await retrieve_similar_chunks(
        db, query_embedding, top_k=50, threshold=data.threshold
    )

    seen: dict[int, dict] = {}
    for c in chunks:
        aid = c["article_id"]
        if aid not in seen or c["similarity"] > seen[aid]["relevance"]:
            seen[aid] = {
                "article_id": aid,
                "relevance": c["similarity"],
                "snippet": c["content"][:200],
            }

    scored = sorted(seen.values(), key=lambda x: x["relevance"], reverse=True)
    total = len(scored)
    total_pages = max(1, (total + data.page_size - 1) // data.page_size)
    start = (data.page - 1) * data.page_size
    page_scores = scored[start : start + data.page_size]

    article_ids = [s["article_id"] for s in page_scores]
    articles = await get_articles_by_ids(db, article_ids)
    article_map = {a.id: a for a in articles}

    items = []
    for s in page_scores:
        a = article_map.get(s["article_id"])
        if a is None:
            continue
        items.append({
            **ArticleListResponse(
                id=a.id, title=a.title, summary=a.summary, slug=a.slug,
                cover_url=a.cover_url, category=a.category, tags=a.tags,
                view_count=a.view_count, reading_time=calculate_reading_time(a.content_md),
                published_at=a.published_at, created_at=a.created_at,
            ).model_dump(),
            "relevance": s["relevance"],
            "snippet": s["snippet"],
        })

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": data.page,
            "page_size": data.page_size,
            "total_pages": total_pages,
        }
    )
