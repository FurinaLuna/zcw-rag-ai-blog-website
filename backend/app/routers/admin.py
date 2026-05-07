from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_admin
from app.dependencies.db import get_db
from app.models.admin import Admin
from app.schemas.article import (
    ArticleAdminResponse,
    ArticleCreate,
    ArticleUpdate,
)
from app.schemas.auth import AdminInfo, LoginRequest, TokenResponse
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate, SortOrderRequest
from app.schemas.tag import TagCreate, TagResponse
from app.services.article import (
    archive_article,
    calculate_reading_time,
    check_slug_available,
    create_article,
    delete_article,
    get_article_by_id,
    get_articles,
    publish_article,
    update_article,
)
from app.services.auth import authenticate_admin
from app.services.category import (
    create_category,
    delete_category,
    get_categories,
    update_category,
    update_sort_orders,
)
from app.services.dashboard import get_hot_articles, get_today_overview, get_trends
from app.services.rag.sync import get_knowledge_status, rebuild_all_vectors, sync_article_vector
from app.services.tag import create_tag, delete_tag, get_tags, update_tag
from app.utils.response import success_response

router = APIRouter()


# Auth
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await authenticate_admin(db, data.username, data.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return success_response(data=TokenResponse(access_token=token).model_dump(), message="Login successful")


@router.get("/me")
async def admin_me(admin: Admin = Depends(get_current_admin)):
    return success_response(data=AdminInfo.model_validate(admin).model_dump())


# Categories
@router.get("/categories")
async def list_categories_admin(db: AsyncSession = Depends(get_db), _: Admin = Depends(get_current_admin)):
    categories = await get_categories(db)
    return success_response(data=categories)


@router.post("/categories", status_code=201)
async def create_category_admin(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    category = await create_category(db, data)
    return success_response(data=CategoryResponse.model_validate(category).model_dump(), message="Category created")


@router.put("/categories/{category_id}")
async def update_category_admin(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    category = await update_category(db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response(data=CategoryResponse.model_validate(category).model_dump(), message="Category updated")


@router.delete("/categories/{category_id}")
async def delete_category_admin(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    deleted = await delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Cannot delete: category has associated articles or not found")
    return success_response(message="Category deleted")


@router.put("/categories/sort")
async def sort_categories(
    data: SortOrderRequest,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    await update_sort_orders(db, [item.model_dump() for item in data.items])
    return success_response(message="Sort order updated")


# Tags
@router.get("/tags")
async def list_tags_admin(db: AsyncSession = Depends(get_db), _: Admin = Depends(get_current_admin)):
    tags = await get_tags(db)
    return success_response(data=tags)


@router.post("/tags", status_code=201)
async def create_tag_admin(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    tag = await create_tag(db, data.name)
    return success_response(data=TagResponse.model_validate(tag).model_dump(), message="Tag created")


@router.put("/tags/{tag_id}")
async def update_tag_admin(
    tag_id: int,
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    tag = await update_tag(db, tag_id, data.name)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return success_response(data=TagResponse.model_validate(tag).model_dump(), message="Tag updated")


@router.delete("/tags/{tag_id}")
async def delete_tag_admin(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    deleted = await delete_tag(db, tag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tag not found")
    return success_response(message="Tag deleted")


# Articles
@router.get("/articles")
async def list_articles_admin(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    status: str | None = None,
    category_id: int | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    articles, total = await get_articles(
        db, page=page, page_size=page_size, status=status or "published"
    )
    if keyword:
        articles, total = await get_articles(db, page=page, page_size=page_size, keyword=keyword)
    items = []
    for a in articles:
        items.append(
            ArticleAdminResponse(
                id=a.id,
                title=a.title,
                summary=a.summary,
                slug=a.slug,
                content_md=a.content_md,
                cover_url=a.cover_url,
                category=a.category,
                tags=a.tags,
                status=a.status,
                vector_status=a.vector_status,
                view_count=a.view_count,
                reading_time=calculate_reading_time(a.content_md),
                seo_title=a.seo_title,
                seo_description=a.seo_description,
                published_at=a.published_at,
                created_at=a.created_at,
                updated_at=a.updated_at,
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


@router.get("/articles/{article_id}")
async def get_article_admin(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    article = await get_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return success_response(
        data=ArticleAdminResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            slug=article.slug,
            content_md=article.content_md,
            cover_url=article.cover_url,
            category=article.category,
            tags=article.tags,
            status=article.status,
            vector_status=article.vector_status,
            view_count=article.view_count,
            reading_time=calculate_reading_time(article.content_md),
            seo_title=article.seo_title,
            seo_description=article.seo_description,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
        ).model_dump()
    )


@router.post("/articles", status_code=201)
async def create_article_admin(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    article = await create_article(db, data.model_dump())
    return success_response(
        data=ArticleAdminResponse.model_validate(article).model_dump(),
        message="Article created",
    )


@router.put("/articles/{article_id}")
async def update_article_admin(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    article = await update_article(db, article_id, data.model_dump(exclude_unset=True))
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return success_response(
        data=ArticleAdminResponse.model_validate(article).model_dump(),
        message="Article updated",
    )


@router.delete("/articles/{article_id}")
async def delete_article_admin(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    deleted = await delete_article(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return success_response(message="Article deleted")


@router.post("/articles/{article_id}/publish")
async def publish_article_admin(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    article = await publish_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await sync_article_vector(db, article_id)
    article = await get_article_by_id(db, article_id)
    return success_response(
        data=ArticleAdminResponse.model_validate(article).model_dump(),
        message="Article published",
    )


@router.post("/articles/{article_id}/archive")
async def archive_article_admin(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    article = await archive_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return success_response(
        data=ArticleAdminResponse.model_validate(article).model_dump(),
        message="Article archived",
    )


@router.get("/articles/check-slug")
async def check_slug(
    slug: str = Query(...),
    exclude_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    available = await check_slug_available(db, slug, exclude_id)
    return success_response(data={"available": available})


@router.post("/articles/{article_id}/sync-vector")
async def sync_article_vector_endpoint(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    ok = await sync_article_vector(db, article_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Vector sync failed")
    return success_response(message="Vector sync completed")


# Dashboard
@router.get("/dashboard/overview")
async def dashboard_overview(db: AsyncSession = Depends(get_db), _: Admin = Depends(get_current_admin)):
    data = await get_today_overview(db)
    return success_response(data=data)


@router.get("/dashboard/trends")
async def dashboard_trends(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    data = await get_trends(db, days)
    return success_response(data=data)


@router.get("/dashboard/popular-articles")
async def dashboard_popular(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    data = await get_hot_articles(db, limit)
    return success_response(data=data)


# Knowledge
@router.get("/knowledge/status")
async def knowledge_status(db: AsyncSession = Depends(get_db), _: Admin = Depends(get_current_admin)):
    data = await get_knowledge_status(db)
    return success_response(data=data)


@router.get("/knowledge/articles")
async def knowledge_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    articles, total = await get_articles(db, page=page, page_size=page_size, status=None)
    items = []
    for a in articles:
        items.append({
            "id": a.id,
            "title": a.title,
            "slug": a.slug,
            "status": a.status,
            "vector_status": a.vector_status,
        })
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}
    )


@router.post("/knowledge/rebuild")
async def knowledge_rebuild(db: AsyncSession = Depends(get_db), _: Admin = Depends(get_current_admin)):
    result = await rebuild_all_vectors(db)
    return success_response(data=result, message=f"Rebuilt {result['success']}/{result['total']} articles")


@router.get("/knowledge/rebuild/{task_id}/progress")
async def rebuild_progress(task_id: str, _: Admin = Depends(get_current_admin)):
    return success_response(data={"task_id": task_id, "status": "completed"})
