import asyncio
from typing import AsyncIterator

import httpx
from loguru import logger

from app.core.config import settings

SYSTEM_PROMPT = """你是一个智能技术内容平台的AI助手。请严格基于以下提供的知识库内容回答用户问题。

规则：
1. 只能基于提供的知识库内容回答问题，不得编造或使用外部知识。
2. 如果知识库中没有相关信息，请明确告诉用户"抱歉，站内知识库中暂未收录该问题的相关内容"。
3. 回答时请引用具体的来源文章。
4. 保持回答简洁、准确、专业。
5. 回答使用中文。

知识库内容：
{context}"""


async def generate_answer(
    question: str,
    chunks: list[dict],
) -> str:
    if not chunks:
        return "抱歉，站内知识库中暂未收录该问题的相关内容，您可以尝试换个问题或查阅站内文章获取更多信息。"

    context_parts = []
    for i, chunk in enumerate(chunks):
        source = f"来源《{chunk['article_title']}》"
        context_parts.append(f"[{i + 1}] {source}\n{chunk['content']}")
    context = "\n\n---\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": question},
    ]

    if not settings.llm_api_key:
        return _generate_simple_answer(question, chunks)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.llm_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return _generate_simple_answer(question, chunks)


def _generate_simple_answer(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return "抱歉，站内知识库中暂未收录该问题的相关内容。"

    lines = ["根据站内知识库，为您找到以下相关信息：\n"]
    for i, chunk in enumerate(chunks[:3]):
        lines.append(f"**来自《{chunk['article_title']}》**：")
        lines.append(f"> {chunk['content'][:200]}...")
        lines.append("")

    lines.append("如需查看完整内容，请点击来源文章链接。")
    return "\n".join(lines)


async def generate_answer_stream(
    question: str,
    chunks: list[dict],
) -> AsyncIterator[str]:
    """Async generator that streams answer characters one at a time.

    Uses the same logic as generate_answer() to produce the full answer,
    then yields it character by character with a small delay to simulate
    token-by-token streaming.
    """
    answer = await generate_answer(question, chunks)
    for char in answer:
        yield char
        await asyncio.sleep(0.01)
