from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.rag import AskRequest, AskResponse, SourceInfo
from app.services.rag.embedder import get_embedder
from app.services.rag.generator import generate_answer
from app.services.rag.retriever import retrieve_similar_chunks

router = APIRouter()

SUGGESTIONS = [
    "Nuxt3 有哪些核心特性？",
    "什么是混合渲染？SSG 和 SSR 有什么区别？",
    "如何搭建 RAG 问答系统？",
    "前端监控体系包含哪些关键指标？",
    "pgvector 如何进行向量检索？",
]


@router.post("/ask")
async def ask_question(data: AskRequest, db: AsyncSession = Depends(get_db)):
    if not data.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty")

    embedder = get_embedder()
    query_embedding = embedder.encode_single(data.question)

    if query_embedding is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding service unavailable")

    chunks = await retrieve_similar_chunks(db, query_embedding, top_k=5, threshold=0.4)
    answer = await generate_answer(data.question, chunks)

    sources = [
        SourceInfo(
            article_id=c["article_id"],
            article_title=c["article_title"],
            article_slug=c["article_slug"],
            chunk_content=c["content"][:200],
            similarity=c["similarity"],
        )
        for c in chunks
    ]

    return {
        "success": True,
        "data": AskResponse(answer=answer, sources=sources, question=data.question).model_dump(),
        "message": "ok",
    }


@router.get("/suggestions")
async def get_suggestions():
    return {"success": True, "data": SUGGESTIONS, "message": "ok"}
