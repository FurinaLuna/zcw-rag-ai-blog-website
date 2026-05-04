from pydantic import BaseModel


class TodayOverview(BaseModel):
    pv: int = 0
    uv: int = 0
    rag_questions: int = 0
    avg_lcp: float | None = None
    error_count: int = 0


class TrendItem(BaseModel):
    date: str
    pv: int = 0
    uv: int = 0


class HotArticle(BaseModel):
    id: int
    title: str
    slug: str
    view_count: int = 0
    comment_count: int = 0


class KnowledgeStatus(BaseModel):
    total_articles: int = 0
    synced: int = 0
    syncing: int = 0
    pending: int = 0
    failed: int = 0
    total_chunks: int = 0
