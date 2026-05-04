from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ArticleTag(Base):
    __tablename__ = "article_tag"

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
