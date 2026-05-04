from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class MonitorEvent(BaseModel):
    event_type: str = Field(..., pattern="^(pv|duration|web_vital|error|resource_error|api_error|exposure)$")
    page_url: str = Field(..., max_length=500)
    event_data: dict[str, Any]
    session_id: str | None = Field(None, max_length=100)


class MonitorBatchRequest(BaseModel):
    events: list[MonitorEvent]


class MonitorQuery(BaseModel):
    event_type: str | None = None
    page_url: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class MonitorLogResponse(BaseModel):
    id: int
    event_type: str
    page_url: str
    event_data: dict
    session_id: str | None = None
    client_ip: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
