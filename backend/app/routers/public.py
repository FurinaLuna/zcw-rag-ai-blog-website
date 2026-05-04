from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.article import ArticleDetailResponse, ArticleListResponse, PaginatedResponse, SlugCheckResponse
from app.schemas.category import CategoryResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.tag import TagResponse
from app.services.article import (
    calculate_reading_time,
    check_slug_available,
    get_article_by_slug,
    get_articles,
    increment_view_count,
)
from app.services.category import get_categories_with_count, get_category_by_slug
from app.services.comment import create_comment, get_comments_by_article, like_comment
from app.services.dashboard import get_home_data
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
