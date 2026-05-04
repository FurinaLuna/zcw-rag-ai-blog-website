import math
from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.article import Article
from app.models.article_tag import ArticleTag
from app.models.category import Category
from app.models.tag import Tag


async def get_articles(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: str = "published",
    category_slug: str | None = None,
    topic_slug: str | None = None,
    tag_id: int | None = None,
    keyword: str | None = None,
    sort_by: str = "published_at",
) -> tuple[list[Article], int]:
    stmt = select(Article).where(Article.status == status)
    count_stmt = select(func.count(Article.id)).where(Article.status == status)

    if category_slug:
        cat_result = await db.execute(select(Category.id).where(Category.slug == category_slug, Category.type == "category"))
        cat_id = cat_result.scalar_one_or_none()
        if cat_id:
            stmt = stmt.where(Article.category_id == cat_id)
            count_stmt = count_stmt.where(Article.category_id == cat_id)

    if topic_slug:
        topic_result = await db.execute(select(Category.id).where(Category.slug == topic_slug, Category.type == "topic"))
        topic_id = topic_result.scalar_one_or_none()
        if topic_id:
            stmt = stmt.where(Article.category_id == topic_id)
            count_stmt = count_stmt.where(Article.category_id == topic_id)

    if tag_id:
        stmt = stmt.where(
            Article.id.in_(
                select(ArticleTag.article_id).where(ArticleTag.tag_id == tag_id)
            )
        )
        count_stmt = count_stmt.where(
            Article.id.in_(
                select(ArticleTag.article_id).where(ArticleTag.tag_id == tag_id)
            )
        )

    if keyword:
        keyword_filter = or_(
            Article.title.ilike(f"%{keyword}%"),
            Article.summary.ilike(f"%{keyword}%"),
            Article.content_md.ilike(f"%{keyword}%"),
        )
        stmt = stmt.where(keyword_filter)
        count_stmt = count_stmt.where(keyword_filter)

    sort_map = {
        "published_at": Article.published_at.desc(),
        "view_count": Article.view_count.desc(),
        "created_at": Article.created_at.desc(),
    }
    order_col = sort_map.get(sort_by, Article.published_at.desc())
    stmt = stmt.order_by(order_col)

    total = await db.scalar(count_stmt)
    stmt = (
        stmt.options(joinedload(Article.category), selectinload(Article.tags))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    articles = list(result.unique().scalars().all())

    return articles, total or 0


async def get_article_by_slug(db: AsyncSession, slug: str) -> Article | None:
    result = await db.execute(
        select(Article)
        .options(joinedload(Article.category), selectinload(Article.tags))
        .where(Article.slug == slug)
    )
    return result.unique().scalar_one_or_none()


async def get_article_by_id(db: AsyncSession, article_id: int) -> Article | None:
    result = await db.execute(
        select(Article)
        .options(joinedload(Article.category), selectinload(Article.tags))
        .where(Article.id == article_id)
    )
    return result.unique().scalar_one_or_none()


async def create_article(db: AsyncSession, data: dict) -> Article:
    tag_ids = data.pop("tag_ids", [])
    article = Article(**data)
    db.add(article)
    await db.flush()

    for tid in tag_ids:
        db.add(ArticleTag(article_id=article.id, tag_id=tid))
    await db.flush()

    article = await get_article_by_id(db, article.id)
    return article


async def update_article(db: AsyncSession, article_id: int, data: dict) -> Article | None:
    article = await get_article_by_id(db, article_id)
    if article is None:
        return None

    tag_ids = data.pop("tag_ids", None)
    update_data = {k: v for k, v in data.items() if v is not None}

    for key, value in update_data.items():
        setattr(article, key, value)
    article.updated_at = datetime.now(tz=timezone.utc)

    if tag_ids is not None:
        await db.execute(delete(ArticleTag).where(ArticleTag.article_id == article_id))
        for tid in tag_ids:
            db.add(ArticleTag(article_id=article_id, tag_id=tid))

    await db.flush()
    article = await get_article_by_id(db, article_id)
    return article


async def publish_article(db: AsyncSession, article_id: int) -> Article | None:
    article = await get_article_by_id(db, article_id)
    if article is None:
        return None
    article.status = "published"
    article.published_at = article.published_at or datetime.now(tz=timezone.utc)
    article.vector_status = "pending"
    await db.flush()
    return article


async def archive_article(db: AsyncSession, article_id: int) -> Article | None:
    article = await get_article_by_id(db, article_id)
    if article is None:
        return None
    article.status = "archived"
    await db.flush()
    return article


async def delete_article(db: AsyncSession, article_id: int) -> bool:
    result = await db.execute(delete(Article).where(Article.id == article_id))
    return result.rowcount > 0


async def check_slug_available(db: AsyncSession, slug: str, exclude_id: int | None = None) -> bool:
    stmt = select(func.count(Article.id)).where(Article.slug == slug)
    if exclude_id:
        stmt = stmt.where(Article.id != exclude_id)
    count = await db.scalar(stmt)
    return count == 0


async def increment_view_count(db: AsyncSession, article_id: int) -> None:
    await db.execute(
        update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
    )
    await db.flush()


async def get_related_articles(db: AsyncSession, article_id: int, category_id: int | None, limit: int = 4) -> list[Article]:
    if category_id is None:
        return []
    stmt = (
        select(Article)
        .options(joinedload(Article.category), selectinload(Article.tags))
        .where(
            Article.category_id == category_id,
            Article.id != article_id,
            Article.status == "published",
        )
        .order_by(Article.published_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


def calculate_reading_time(content_md: str | None) -> int:
    if not content_md:
        return 1
    return max(1, math.ceil(len(content_md) / 500))


async def get_article_status_counts(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Article.status, func.count(Article.id)).group_by(Article.status)
    )
    rows = result.all()
    counts = {"draft": 0, "published": 0, "archived": 0}
    for status, count in rows:
        counts[status] = count
    return counts
