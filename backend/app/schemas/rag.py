from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class SourceInfo(BaseModel):
    article_id: int
    article_title: str
    article_slug: str
    chunk_content: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceInfo] = []
    question: str
