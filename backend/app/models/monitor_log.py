from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MonitorLog(Base):
    __tablename__ = "monitor_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    event_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
