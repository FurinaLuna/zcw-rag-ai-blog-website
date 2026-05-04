from datetime import datetime
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)


class TagCreate(TagBase):
    pass


class TagResponse(BaseModel):
    id: int
    name: str
    article_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
