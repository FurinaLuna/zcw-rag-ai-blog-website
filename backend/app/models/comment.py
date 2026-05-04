from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), nullable=False)
    nickname: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side="Comment.id", cascade="all, delete-orphan")
