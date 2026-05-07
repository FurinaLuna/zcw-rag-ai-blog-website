from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VectorChunk(Base):
    __tablename__ = "vector_chunk"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    # Embedding is handled via pgvector, added in Alembic migration
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="vector_chunks")
