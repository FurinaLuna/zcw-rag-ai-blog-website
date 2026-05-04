from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1, max_length=500)
    parent_id: int | None = None


class CommentResponse(BaseModel):
    id: int
    article_id: int
    nickname: str
    content: str
    likes: int
    parent_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
