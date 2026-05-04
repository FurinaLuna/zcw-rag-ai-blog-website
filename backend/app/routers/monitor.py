from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.monitor import MonitorBatchRequest, MonitorQuery
from app.services.monitor import query_monitor_logs, report_events
from app.utils.response import success_response

router = APIRouter()


@router.post("/report")
async def report_monitor_events(data: MonitorBatchRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "")
    count = await report_events(db, data, client_ip, user_agent)
    return success_response(data={"recorded": count}, message=f"Recorded {count} events")


@router.get("/stats")
async def get_monitor_stats(
    event_type: str | None = None,
    page_url: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await query_monitor_logs(
        db,
        event_type=event_type,
        page_url=page_url,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size
    return success_response(
        data={
            "items": [
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "page_url": log.page_url,
                    "event_data": log.event_data,
                    "session_id": log.session_id,
                    "client_ip": log.client_ip,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )
