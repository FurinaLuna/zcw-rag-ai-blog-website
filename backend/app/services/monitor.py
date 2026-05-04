from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.monitor_log import MonitorLog
from app.schemas.monitor import MonitorBatchRequest


async def report_events(db: AsyncSession, data: MonitorBatchRequest, client_ip: str, user_agent: str) -> int:
    count = 0
    for event in data.events:
        log = MonitorLog(
            event_type=event.event_type,
            page_url=event.page_url,
            event_data=event.event_data,
            session_id=event.session_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        db.add(log)
        count += 1
    await db.flush()
    logger.info(f"Recorded {count} monitor events")
    return count


async def query_monitor_logs(
    db: AsyncSession,
    event_type: str | None = None,
    page_url: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[MonitorLog], int]:
    stmt = select(MonitorLog)
    count_stmt = select(func.count(MonitorLog.id))

    if event_type:
        stmt = stmt.where(MonitorLog.event_type == event_type)
        count_stmt = count_stmt.where(MonitorLog.event_type == event_type)
    if page_url:
        stmt = stmt.where(MonitorLog.page_url == page_url)
        count_stmt = count_stmt.where(MonitorLog.page_url == page_url)
    if start_time:
        stmt = stmt.where(MonitorLog.created_at >= start_time)
        count_stmt = count_stmt.where(MonitorLog.created_at >= start_time)
    if end_time:
        stmt = stmt.where(MonitorLog.created_at <= end_time)
        count_stmt = count_stmt.where(MonitorLog.created_at <= end_time)

    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(MonitorLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    logs = list(result.scalars().all())

    return logs, total or 0


async def get_monitor_stats(
    db: AsyncSession,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> dict:
    base_filter = select(MonitorLog)
    if start_time:
        base_filter = base_filter.where(MonitorLog.created_at >= start_time)
    if end_time:
        base_filter = base_filter.where(MonitorLog.created_at <= end_time)

    pv = await db.scalar(
        select(func.count(MonitorLog.id)).where(
            MonitorLog.event_type == "pv",
            *([] if not start_time else [MonitorLog.created_at >= start_time]),
            *([] if not end_time else [MonitorLog.created_at <= end_time]),
        ) if start_time or end_time else
        select(func.count(MonitorLog.id)).where(MonitorLog.event_type == "pv")
    )

    error_count = await db.scalar(
        select(func.count(MonitorLog.id)).where(
            MonitorLog.event_type.in_(["error", "api_error", "resource_error"]),
            *([] if not start_time else [MonitorLog.created_at >= start_time]),
            *([] if not end_time else [MonitorLog.created_at <= end_time]),
        )
    )

    return {
        "pv": pv or 0,
        "error_count": error_count or 0,
    }
