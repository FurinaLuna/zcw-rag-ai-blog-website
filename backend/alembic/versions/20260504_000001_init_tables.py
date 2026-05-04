"""init tables

Revision ID: 000001
Revises:
Create Date: 2026-05-04 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("type", sa.String(20), nullable=False, server_default="category"),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("cover_url", sa.String(500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("idx_category_type", "category", ["type"])
    op.create_index("idx_category_sort", "category", ["sort_order"])

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "article",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(160), nullable=True),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=True),
        sa.Column("cover_url", sa.String(500), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("vector_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("seo_title", sa.String(60), nullable=True),
        sa.Column("seo_description", sa.String(160), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("idx_article_status", "article", ["status"])
    op.create_index("idx_article_category", "article", ["category_id"])
    op.create_index("idx_article_published", "article", ["published_at"], postgresql_where=sa.text("status = 'published'"))
    op.create_index("idx_article_vector_status", "article", ["vector_status"])

    op.create_table(
        "article_tag",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )

    op.create_table(
        "comment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.String(20), nullable=False),
        sa.Column("content", sa.String(500), nullable=False),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["comment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_comment_article", "comment", ["article_id", "created_at"])

    op.create_table(
        "monitor_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("page_url", sa.String(500), nullable=False),
        sa.Column("event_data", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitor_type_time", "monitor_log", ["event_type", "created_at"])
    op.create_index("idx_monitor_page_time", "monitor_log", ["page_url", "created_at"])
    op.create_index("idx_monitor_created", "monitor_log", ["created_at"])

    op.create_table(
        "vector_chunk",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(512), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_vector_article", "vector_chunk", ["article_id"])


def downgrade() -> None:
    op.drop_index("idx_vector_article", table_name="vector_chunk")
    op.drop_table("vector_chunk")
    op.drop_index("idx_monitor_created", table_name="monitor_log")
    op.drop_index("idx_monitor_page_time", table_name="monitor_log")
    op.drop_index("idx_monitor_type_time", table_name="monitor_log")
    op.drop_table("monitor_log")
    op.drop_index("idx_comment_article", table_name="comment")
    op.drop_table("comment")
    op.drop_table("article_tag")
    op.drop_index("idx_article_vector_status", table_name="article")
    op.drop_index("idx_article_published", table_name="article")
    op.drop_index("idx_article_category", table_name="article")
    op.drop_index("idx_article_status", table_name="article")
    op.drop_table("article")
    op.drop_index("idx_tag_name", table_name="tag")
    op.drop_table("tag")
    op.drop_index("idx_category_sort", table_name="category")
    op.drop_index("idx_category_type", table_name="category")
    op.drop_table("category")
    op.drop_table("admin")
