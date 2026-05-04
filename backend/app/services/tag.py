from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article_tag import ArticleTag
from app.models.tag import Tag


async def get_tags(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(
            Tag,
            func.count(ArticleTag.article_id).label("article_count"),
        )
        .outerjoin(ArticleTag, ArticleTag.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    rows = result.all()
    return [
        {
            **{k: v for k, v in row[0].__dict__.items() if not k.startswith("_")},
            "article_count": row[1],
        }
        for row in rows
    ]


async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, name: str) -> Tag:
    tag = Tag(name=name)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def update_tag(db: AsyncSession, tag_id: int, name: str) -> Tag | None:
    tag = await get_tag_by_id(db, tag_id)
    if tag is None:
        return None
    tag.name = name
    await db.flush()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
    await db.execute(delete(ArticleTag).where(ArticleTag.tag_id == tag_id))
    result = await db.execute(delete(Tag).where(Tag.id == tag_id))
    return result.rowcount > 0
