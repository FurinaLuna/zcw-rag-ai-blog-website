"""API集成测试：语义搜索端点"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch

from app.main import app


@pytest.mark.asyncio
async def test_semantic_search_empty_query():
    """空查询应返回422"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/public/search/semantic", json={"q": ""})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_semantic_search_query_too_long():
    """超长查询应返回422"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/public/search/semantic", json={"q": "x" * 501})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_semantic_search_invalid_threshold():
    """无效阈值应返回422"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/public/search/semantic",
            json={"q": "test", "threshold": 1.5})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_semantic_search_embedder_unavailable():
    """Embedder未加载应返回503"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routers.public.get_embedder") as mock_embedder:
            mock_embedder.return_value.encode_single = lambda _: None
            response = await client.post("/api/v1/public/search/semantic",
                json={"q": "测试语义搜索"})
            assert response.status_code == 503


@pytest.mark.asyncio
async def test_semantic_search_empty_results():
    """无匹配结果时返回空列表"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routers.public.get_embedder") as mock_embedder, \
             patch("app.routers.public.retrieve_similar_chunks") as mock_retrieve:
            mock_embedder.return_value.encode_single = lambda _: [0.1, 0.2, 0.3]
            mock_retrieve.return_value = []
            response = await client.post("/api/v1/public/search/semantic",
                json={"q": "不存在的内容"})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["items"] == []
            assert data["data"]["total"] == 0
            assert data["data"]["total_pages"] == 1
            assert data["data"]["page"] == 1


@pytest.mark.asyncio
async def test_semantic_search_returned_data_structure():
    """测试返回数据结构正确（mocked）"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routers.public.get_embedder") as mock_embedder, \
             patch("app.routers.public.retrieve_similar_chunks") as mock_retrieve, \
             patch("app.routers.public.get_articles_by_ids") as mock_get_articles:

            mock_embedder.return_value.encode_single = lambda _: [0.1, 0.2, 0.3]

            mock_retrieve.return_value = [
                {"article_id": 1, "similarity": 0.85, "content": "测试内容片段" * 5,
                 "article_title": "测试文章", "article_slug": "test-article"},
                {"article_id": 2, "similarity": 0.72, "content": "另一篇内容" * 5,
                 "article_title": "另一篇", "article_slug": "another"},
            ]

            mock_article1 = type("Article", (), {
                "id": 1, "title": "测试文章", "summary": "摘要", "slug": "test-article",
                "cover_url": None, "category": None, "tags": [],
                "view_count": 10, "content_md": "内容", "published_at": None,
                "created_at": "2025-01-01T00:00:00",
            })()
            mock_article2 = type("Article", (), {
                "id": 2, "title": "另一篇", "summary": "摘要2", "slug": "another",
                "cover_url": None, "category": None, "tags": [],
                "view_count": 5, "content_md": "内容2", "published_at": None,
                "created_at": "2025-01-02T00:00:00",
            })()
            mock_get_articles.return_value = [mock_article1, mock_article2]

            response = await client.post("/api/v1/public/search/semantic",
                json={"q": "测试搜索", "page": 1, "page_size": 20, "threshold": 0.3})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["items"]) == 2
            assert data["data"]["total"] == 2
            assert data["data"]["page"] == 1

            # 第一个结果相关度更高
            item0 = data["data"]["items"][0]
            assert item0["relevance"] == 0.85
            assert "snippet" in item0
            assert item0["title"] == "测试文章"


@pytest.mark.asyncio
async def test_semantic_search_pagination():
    """分页参数正常工作"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routers.public.get_embedder") as mock_embedder, \
             patch("app.routers.public.retrieve_similar_chunks") as mock_retrieve, \
             patch("app.routers.public.get_articles_by_ids") as mock_get_articles:

            mock_embedder.return_value.encode_single = lambda _: [0.1]
            mock_retrieve.return_value = [
                {"article_id": i, "similarity": 0.9 - i * 0.1, "content": "x" * 50,
                 "article_title": f"Article {i}", "article_slug": f"article-{i}"}
                for i in range(1, 6)
            ]
            mock_get_articles.return_value = []

            response = await client.post("/api/v1/public/search/semantic",
                json={"q": "test", "page": 1, "page_size": 2})
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total"] == 5
            assert data["data"]["total_pages"] == 3
            assert data["data"]["page_size"] == 2


@pytest.mark.asyncio
async def test_semantic_search_default_values():
    """默认分页和阈值参数"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routers.public.get_embedder") as mock_embedder, \
             patch("app.routers.public.retrieve_similar_chunks") as mock_retrieve, \
             patch("app.routers.public.get_articles_by_ids") as mock_get_articles:
            mock_embedder.return_value.encode_single = lambda _: [0.1]
            mock_retrieve.return_value = []
            mock_get_articles.return_value = []

            response = await client.post("/api/v1/public/search/semantic",
                json={"q": "test"})
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["page"] == 1
            assert data["data"]["page_size"] == 20
