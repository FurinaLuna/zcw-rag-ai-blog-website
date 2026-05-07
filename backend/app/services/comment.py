from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment


async def get_comments_by_article(
    db: AsyncSession, article_id: int, page: int = 1, page_size: int = 20
) -> tuple[list[Comment], int]:
    count_stmt = select(func.count(Comment.id)).where(Comment.article_id == article_id)
    total = await db.scalar(count_stmt)

    stmt = (
        select(Comment)
        .where(Comment.article_id == article_id)
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    comments = list(result.scalars().all())

    return comments, total or 0


async def create_comment(
    db: AsyncSession, article_id: int, nickname: str, content: str, parent_id: int | None = None
) -> Comment:
    comment = Comment(
        article_id=article_id,
        nickname=nickname,
        content=content,
        parent_id=parent_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def like_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        return None
    comment.likes += 1
    await db.flush()
    await db.refresh(comment)
    return comment
