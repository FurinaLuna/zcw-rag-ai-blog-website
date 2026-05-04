from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.category import CategorySimple
from app.schemas.tag import TagResponse


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    summary: str | None = Field(None, max_length=160)
    slug: str = Field(..., min_length=1, max_length=200)
    content_md: str | None = None
    cover_url: str | None = Field(None, max_length=500)
    category_id: int | None = None
    tag_ids: list[int] = []
    seo_title: str | None = Field(None, max_length=60)
    seo_description: str | None = Field(None, max_length=160)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    summary: str | None = Field(None, max_length=160)
    slug: str | None = Field(None, min_length=1, max_length=200)
    content_md: str | None = None
    cover_url: str | None = Field(None, max_length=500)
    category_id: int | None = None
    tag_ids: list[int] | None = None
    seo_title: str | None = Field(None, max_length=60)
    seo_description: str | None = Field(None, max_length=160)


class ArticleListResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    slug: str
    cover_url: str | None = None
    category: CategorySimple | None = None
    tags: list[TagResponse] = []
    view_count: int = 0
    reading_time: int = 0
    published_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleDetailResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    slug: str
    content_md: str | None = None
    cover_url: str | None = None
    category: CategorySimple | None = None
    tags: list[TagResponse] = []
    view_count: int = 0
    reading_time: int = 0
    comment_count: int = 0
    seo_title: str | None = None
    seo_description: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    related_articles: list["ArticleListResponse"] = []

    model_config = {"from_attributes": True}


class ArticleAdminResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    slug: str
    content_md: str | None = None
    cover_url: str | None = None
    category: CategorySimple | None = None
    tags: list[TagResponse] = []
    status: str
    vector_status: str
    view_count: int = 0
    reading_time: int = 0
    seo_title: str | None = None
    seo_description: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SlugCheckRequest(BaseModel):
    slug: str
    exclude_id: int | None = None


class SlugCheckResponse(BaseModel):
    available: bool


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
