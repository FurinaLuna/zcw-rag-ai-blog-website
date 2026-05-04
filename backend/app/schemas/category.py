from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=200)
    cover_url: str | None = Field(None, max_length=500)
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    type: str = Field(default="category", pattern="^(category|topic)$")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    slug: str | None = Field(None, min_length=1, max_length=100)
    type: str | None = Field(None, pattern="^(category|topic)$")
    description: str | None = Field(None, max_length=200)
    cover_url: str | None = Field(None, max_length=500)
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    type: str
    description: str | None = None
    cover_url: str | None = None
    sort_order: int
    article_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class CategorySimple(BaseModel):
    id: int
    name: str
    slug: str
    type: str

    model_config = {"from_attributes": True}


class SortOrderItem(BaseModel):
    id: int
    sort_order: int


class SortOrderRequest(BaseModel):
    items: list[SortOrderItem]
