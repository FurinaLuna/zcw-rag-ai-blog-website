from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.article import Article
from app.models.category import Category
from app.models.monitor_log import MonitorLog
from app.models.vector_chunk import VectorChunk


async def get_home_data(db: AsyncSession) -> dict:
    # Featured articles (latest published, limit 6)
    featured_result = await db.execute(
        select(Article)
        .options(joinedload(Article.category), joinedload(Article.tags))
        .where(Article.status == "published")
        .order_by(Article.published_at.desc())
        .limit(6)
    )
    featured = list(featured_result.unique().scalars().all())

    # Topics
    topics_result = await db.execute(
        select(Category).where(Category.type == "topic").order_by(Category.sort_order).limit(4)
    )
    topics = list(topics_result.scalars().all())

    # System metrics
    total_articles = await db.scalar(
        select(func.count(Article.id)).where(Article.status == "published")
    ) or 0

    total_chunks = await db.scalar(select(func.count(VectorChunk.id))) or 0

    return {
        "featured_articles": featured,
        "topics": topics,
        "metrics": {
            "total_articles": total_articles,
            "total_chunks": total_chunks,
        },
    }


async def get_today_overview(db: AsyncSession) -> dict:
    today_start = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    pv = await db.scalar(
        select(func.count(MonitorLog.id)).where(
            MonitorLog.event_type == "pv",
            MonitorLog.created_at >= today_start,
        )
    ) or 0

    # UV by unique client_ip
    uv_result = await db.execute(
        select(func.count(func.distinct(MonitorLog.client_ip))).where(
            MonitorLog.event_type == "pv",
            MonitorLog.created_at >= today_start,
        )
    )
    uv = uv_result.scalar() or 0

    rag_questions = await db.scalar(
        select(func.count(MonitorLog.id)).where(
            MonitorLog.event_type == "exposure",
            MonitorLog.created_at >= today_start,
        )
    ) or 0

    error_count = await db.scalar(
        select(func.count(MonitorLog.id)).where(
            MonitorLog.event_type.in_(["error", "api_error", "resource_error"]),
            MonitorLog.created_at >= today_start,
        )
    ) or 0

    return {
        "pv": pv,
        "uv": uv,
        "rag_questions": rag_questions,
        "error_count": error_count,
    }


async def get_trends(db: AsyncSession, days: int = 7) -> list[dict]:
    start_date = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days - 1)

    result = await db.execute(
        select(
            func.date(MonitorLog.created_at).label("date"),
            func.count(MonitorLog.id).label("pv"),
        )
        .where(
            MonitorLog.event_type == "pv",
            MonitorLog.created_at >= start_date,
        )
        .group_by(func.date(MonitorLog.created_at))
        .order_by("date")
    )
    rows = result.all()
    return [{"date": str(row[0]), "pv": row[1]} for row in rows]


async def get_hot_articles(db: AsyncSession, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(
            Article.id,
            Article.title,
            Article.slug,
            Article.view_count,
            func.count(MonitorLog.id).label("comment_count"),
        )
        .outerjoin(MonitorLog, MonitorLog.event_type == "pv")
        .where(Article.status == "published")
        .group_by(Article.id)
        .order_by(Article.view_count.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": row[0],
            "title": row[1],
            "slug": row[2],
            "view_count": row[3],
            "comment_count": row[4] if row[4] else 0,
        }
        for row in rows
    ]
