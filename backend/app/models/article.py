from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(160), nullable=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    content_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    vector_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    seo_title: Mapped[str | None] = mapped_column(String(60), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(160), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary="article_tag", back_populates="articles")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    vector_chunks = relationship("VectorChunk", back_populates="article", cascade="all, delete-orphan")
