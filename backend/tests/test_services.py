"""Service 层集成测试 — 用 mock AsyncSession 验证业务逻辑"""
import pytest
from unittest.mock import AsyncMock, MagicMock


class TestArticleService:
    """测试 article service 纯逻辑函数"""

    def test_calculate_reading_time_empty(self):
        from app.services.article import calculate_reading_time
        assert calculate_reading_time(None) == 1
        assert calculate_reading_time("") == 1

    def test_calculate_reading_time_short(self):
        from app.services.article import calculate_reading_time
        assert calculate_reading_time("短内容") == 1

    def test_calculate_reading_time_medium(self):
        from app.services.article import calculate_reading_time
        # 500 chars = 1 minute
        assert calculate_reading_time("x" * 500) == 1
        # 501 chars = 2 minutes
        assert calculate_reading_time("x" * 501) == 2
        # 1500 chars = 3 minutes
        assert calculate_reading_time("x" * 1500) == 3

    @pytest.mark.asyncio
    async def test_slug_check_available(self):
        from app.services.article import check_slug_available
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=0)
        result = await check_slug_available(db, "my-slug")
        assert result is True

    @pytest.mark.asyncio
    async def test_slug_check_taken(self):
        from app.services.article import check_slug_available
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=1)
        result = await check_slug_available(db, "taken-slug")
        assert result is False

    @pytest.mark.asyncio
    async def test_slug_check_exclude_id(self):
        from app.services.article import check_slug_available
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=0)
        result = await check_slug_available(db, "my-slug", exclude_id=5)
        assert result is True


class TestCategoryService:
    """测试 category service 业务逻辑"""

    @pytest.mark.asyncio
    async def test_get_category_by_slug_not_found(self):
        from app.services.category import get_category_by_slug
        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result
        result = await get_category_by_slug(db, "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_category_not_found(self):
        from app.services.category import update_category
        from app.schemas.category import CategoryUpdate
        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result
        result = await update_category(db, 999, CategoryUpdate(name="new"))
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_category_with_articles_returns_false(self):
        from app.services.category import delete_category
        db = AsyncMock()
        # Mock: category has associated articles
        db.scalar = AsyncMock(return_value=3)
        result = await delete_category(db, 1)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_category_no_articles_returns_true(self):
        from app.services.category import delete_category
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=0)
        # Mock execute to return a result with rowcount=1 (deleted successfully)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        db.execute = AsyncMock(return_value=mock_result)
        result = await delete_category(db, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self):
        from app.services.category import delete_category
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=0)
        mock_result = MagicMock()
        mock_result.rowcount = 0
        db.execute = AsyncMock(return_value=mock_result)
        result = await delete_category(db, 999)
        assert result is False


class TestCommentService:
    """测试 comment service 逻辑"""

    @pytest.mark.asyncio
    async def test_create_comment(self):
        from app.services.comment import create_comment
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        result = await create_comment(db, 1, "nick", "content")
        assert result is not None
        assert result.nickname == "nick"
        assert result.article_id == 1

    @pytest.mark.asyncio
    async def test_create_comment_with_parent(self):
        from app.services.comment import create_comment
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        result = await create_comment(db, 1, "reply", "reply content", parent_id=5)
        assert result.parent_id == 5

    @pytest.mark.asyncio
    async def test_get_comments_empty(self):
        from app.services.comment import get_comments_by_article
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=0)
        exec_result = MagicMock()
        exec_result.scalars = MagicMock(return_value=exec_result)
        exec_result.all = MagicMock(return_value=[])
        db.execute = AsyncMock(return_value=exec_result)
        comments, total = await get_comments_by_article(db, 1)
        assert comments == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_like_comment_not_found(self):
        from app.services.comment import like_comment
        db = AsyncMock()
        db.execute = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = execute_result
        result = await like_comment(db, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_like_comment_increments(self):
        from app.services.comment import like_comment
        db = AsyncMock()
        mock_comment = MagicMock()
        mock_comment.likes = 5
        db.execute = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=mock_comment)
        db.execute.return_value = execute_result
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        result = await like_comment(db, 1)
        assert result is not None
        assert mock_comment.likes == 6  # incremented


class TestArticleStatusTransitions:
    """测试文章状态流转: draft → published → archived"""

    @pytest.mark.asyncio
    async def test_publish_draft_article(self):
        """草稿发布: 状态变为 published, 设置 published_at 和 vector_status"""
        from app.services.article import publish_article

        db = AsyncMock()
        mock_article = MagicMock()
        mock_article.id = 1
        mock_article.status = "draft"
        mock_article.published_at = None
        mock_article.vector_status = "completed"

        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=mock_article)
        db.execute.return_value = exec_result
        db.flush = AsyncMock()

        result = await publish_article(db, 1)
        assert result is not None
        assert mock_article.status == "published"
        assert mock_article.vector_status == "pending"
        assert mock_article.published_at is not None

    @pytest.mark.asyncio
    async def test_publish_article_not_found(self):
        """发布不存在的文章返回 None"""
        from app.services.article import publish_article

        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result

        result = await publish_article(db, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_archive_published_article(self):
        """归档已发布文章: 状态变为 archived"""
        from app.services.article import archive_article

        db = AsyncMock()
        mock_article = MagicMock()
        mock_article.id = 2
        mock_article.status = "published"

        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=mock_article)
        db.execute.return_value = exec_result
        db.flush = AsyncMock()

        result = await archive_article(db, 2)
        assert result is not None
        assert mock_article.status == "archived"

    @pytest.mark.asyncio
    async def test_archive_article_not_found(self):
        """归档不存在的文章返回 None"""
        from app.services.article import archive_article

        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result

        result = await archive_article(db, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_already_published_article(self):
        """对已发布文章再次发布: 保持原 published_at 不变"""
        from datetime import datetime, timezone
        from app.services.article import publish_article

        db = AsyncMock()
        original_published_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_article = MagicMock()
        mock_article.id = 3
        mock_article.status = "published"
        mock_article.published_at = original_published_at
        mock_article.vector_status = "completed"

        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=mock_article)
        db.execute.return_value = exec_result
        db.flush = AsyncMock()

        result = await publish_article(db, 3)
        assert result is not None
        assert mock_article.status == "published"
        assert mock_article.published_at == original_published_at
        assert mock_article.vector_status == "pending"

    @pytest.mark.asyncio
    async def test_archive_then_publish_article(self):
        """归档后再发布: 状态从 archived 变为 published"""
        from datetime import datetime, timezone
        from app.services.article import publish_article, archive_article

        db = AsyncMock()
        original_published_at = datetime(2025, 3, 15, tzinfo=timezone.utc)
        mock_article = MagicMock()
        mock_article.id = 4
        mock_article.status = "published"
        mock_article.published_at = original_published_at
        mock_article.vector_status = "completed"

        # First archive
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.unique = MagicMock(return_value=exec_result)
        exec_result.scalar_one_or_none = MagicMock(return_value=mock_article)
        db.execute.return_value = exec_result
        db.flush = AsyncMock()

        await archive_article(db, 4)
        assert mock_article.status == "archived"

        # Then re-publish
        mock_article.status = "archived"  # reset to test
        result = await publish_article(db, 4)
        assert result is not None
        assert mock_article.status == "published"
        assert mock_article.published_at == original_published_at
        assert mock_article.vector_status == "pending"


class TestTagService:
    """测试 tag service"""

    @pytest.mark.asyncio
    async def test_get_tag_by_id_not_found(self):
        from app.services.tag import get_tag_by_id
        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result
        result = await get_tag_by_id(db, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_create_tag(self):
        from app.services.tag import create_tag
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        result = await create_tag(db, "新标签")
        assert result is not None
        assert result.name == "新标签"

    @pytest.mark.asyncio
    async def test_update_tag_not_found(self):
        from app.services.tag import update_tag
        db = AsyncMock()
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = exec_result
        result = await update_tag(db, 999, "newname")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_tag_success(self):
        from app.services.tag import update_tag
        db = AsyncMock()
        mock_tag = MagicMock()
        mock_tag.name = "oldname"
        db.execute = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none = MagicMock(return_value=mock_tag)
        db.execute.return_value = exec_result
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        result = await update_tag(db, 1, "newname")
        assert result is not None
        assert mock_tag.name == "newname"

    @pytest.mark.asyncio
    async def test_delete_tag_not_found(self):
        from app.services.tag import delete_tag
        db = AsyncMock()
        delete_result = MagicMock()
        delete_result.rowcount = 0
        db.execute = AsyncMock(return_value=delete_result)
        result = await delete_tag(db, 999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_tag_success(self):
        from app.services.tag import delete_tag
        db = AsyncMock()
        delete_result = MagicMock()
        delete_result.rowcount = 1
        db.execute = AsyncMock(return_value=delete_result)
        result = await delete_tag(db, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_tags_returns_list(self):
        from app.services.tag import get_tags
        from app.models.tag import Tag
        db = AsyncMock()
        tag = Tag(name="tag1")
        tag.id = 1
        row = (tag, 3)
        exec_result = MagicMock()
        exec_result.all = MagicMock(return_value=[row])
        db.execute = AsyncMock(return_value=exec_result)
        result = await get_tags(db)
        assert len(result) == 1
        assert result[0]["article_count"] == 3


class TestDashboardService:
    """测试 dashboard service"""

    @pytest.mark.asyncio
    async def test_get_trends_empty(self):
        from app.services.dashboard import get_trends
        db = AsyncMock()
        exec_result = MagicMock()
        exec_result.all = MagicMock(return_value=[])
        db.execute = AsyncMock(return_value=exec_result)
        result = await get_trends(db, days=7)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_trends_with_data(self):
        from app.services.dashboard import get_trends
        from datetime import date
        db = AsyncMock()
        exec_result = MagicMock()
        exec_result.all = MagicMock(return_value=[(date(2026, 5, 6), 42)])
        db.execute = AsyncMock(return_value=exec_result)
        result = await get_trends(db, days=7)
        assert len(result) == 1
        assert result[0]["pv"] == 42

    @pytest.mark.asyncio
    async def test_get_hot_articles_empty(self):
        from app.services.dashboard import get_hot_articles
        db = AsyncMock()
        exec_result = MagicMock()
        exec_result.all = MagicMock(return_value=[])
        db.execute = AsyncMock(return_value=exec_result)
        result = await get_hot_articles(db, limit=5)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_today_overview_no_data(self):
        from app.services.dashboard import get_today_overview
        db = AsyncMock()
        db.scalar = AsyncMock(return_value=None)
        db.execute = AsyncMock()
        uv_result = MagicMock()
        uv_result.scalar = MagicMock(return_value=None)
        db.execute.return_value = uv_result
        result = await get_today_overview(db)
        assert result["pv"] == 0
        assert result["uv"] == 0
        assert result["rag_questions"] == 0
        assert result["error_count"] == 0


class TestAuthService:
    """测试 auth service"""

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self):
        from app.services.auth import authenticate_admin
        from app.core.security import hash_password

        db = AsyncMock()
        hashed = hash_password("correct")
        mock_admin = MagicMock()
        mock_admin.password_hash = hashed
        db.execute = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=mock_admin)
        db.execute.return_value = execute_result

        result = await authenticate_admin(db, "admin", "wrong")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        from app.services.auth import authenticate_admin

        db = AsyncMock()
        db.execute = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute.return_value = execute_result

        result = await authenticate_admin(db, "nobody", "pass")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        from app.services.auth import authenticate_admin
        from app.core.security import hash_password

        db = AsyncMock()
        hashed = hash_password("correct")
        mock_admin = MagicMock()
        mock_admin.id = 1
        mock_admin.username = "admin"
        mock_admin.password_hash = hashed
        db.execute = AsyncMock()
        execute_result = MagicMock()
        execute_result.scalar_one_or_none = MagicMock(return_value=mock_admin)
        db.execute.return_value = execute_result
        db.flush = AsyncMock()

        result = await authenticate_admin(db, "admin", "correct")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
