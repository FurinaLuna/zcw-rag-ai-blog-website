from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(db: AsyncSession, category_type: str | None = None) -> list[Category]:
    stmt = select(Category).order_by(Category.sort_order)
    if category_type:
        stmt = stmt.where(Category.type == category_type)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_categories_with_count(
    db: AsyncSession, category_type: str | None = None
) -> list[dict]:
    stmt = (
        select(
            Category,
            func.count(Article.id).label("article_count"),
        )
        .outerjoin(Article, Article.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.sort_order)
    )
    if category_type:
        stmt = stmt.where(Category.type == category_type)
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            **{k: v for k, v in row[0].__dict__.items() if not k.startswith("_")},
            "article_count": row[1],
        }
        for row in rows
    ]


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category | None:
    category = await get_category_by_id(db, category_id)
    if category is None:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    article_count = await db.scalar(
        select(func.count(Article.id)).where(Article.category_id == category_id)
    )
    if article_count and article_count > 0:
        return False
    result = await db.execute(delete(Category).where(Category.id == category_id))
    return result.rowcount > 0


async def update_sort_orders(
    db: AsyncSession, items: list[dict]
) -> None:
    for item in items:
        await db.execute(
            update(Category).where(Category.id == item["id"]).values(sort_order=item["sort_order"])
        )
    await db.flush()
