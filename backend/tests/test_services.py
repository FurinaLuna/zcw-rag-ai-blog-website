"""Service 层集成测试 — 用 mock AsyncSession 验证业务逻辑"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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
