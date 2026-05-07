"""种子数据脚本：创建管理员、分类、标签和示例文章"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.admin import Admin
from app.models.category import Category
from app.models.tag import Tag
from app.models.article import Article
from app.models.article_tag import ArticleTag

async def seed():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 1. Create admin
        admin = Admin(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
        db.add(admin)

        # 2. Create categories
        cats = [
            Category(name="前端工程化", slug="frontend", type="category",
                     description="构建工具、性能优化、监控体系", sort_order=1),
            Category(name="后端开发", slug="backend", type="category",
                     description="API设计、数据库、架构模式", sort_order=2),
            Category(name="AI与LLM", slug="ai-llm", type="category",
                     description="大语言模型、RAG、向量检索", sort_order=3),
        ]
        db.add_all(cats)

        # 3. Create topics
        topics = [
            Category(name="Nuxt 实践指南", slug="nuxt-guide", type="topic",
                     description="从零搭建企业级Nuxt应用", sort_order=1),
            Category(name="RAG 技术深度解析", slug="rag-deep-dive", type="topic",
                     description="检索增强生成的原理与实践", sort_order=2),
            Category(name="Python 性能优化", slug="python-perf", type="topic",
                     description="异步编程、数据库调优、部署策略", sort_order=3),
        ]
        db.add_all(topics)

        # 4. Create tags
        tags = [
            Tag(name="Nuxt"), Tag(name="Vue"), Tag(name="TypeScript"),
            Tag(name="FastAPI"), Tag(name="PostgreSQL"), Tag(name="RAG"),
            Tag(name="Vector"), Tag(name="Embedding"), Tag(name="Docker"),
        ]
        db.add_all(tags)
        await db.flush()

        # 5. Create sample articles
        article1 = Article(
            title="Nuxt3 混合渲染实践：SSG、SSR 与 CSR 的取舍",
            summary="深入探讨 Nuxt3 在不同场景下的渲染策略选择，包含性能对比与最佳实践。",
            slug="nuxt3-hybrid-rendering",
            content_md="""# Nuxt3 混合渲染实践

## 什么是混合渲染

Nuxt3 支持三种渲染模式：SSG（静态生成）、SSR（服务端渲染）和 CSR（客户端渲染）。选择合适的渲染模式可以显著提升应用性能。

## SSG 适用场景

- 首页、关于页等不常变动的内容
- 博客文章列表
- 文档站点

## SSR 适用场景

- 需要 SEO 但内容动态变化的页面
- 文章详情页（需要实时数据）

## CSR 适用场景

- 管理后台
- 需要用户交互的复杂页面
- RAG 问答页

## 性能对比

| 模式 | FCP | LCP | TTI |
|------|-----|-----|-----|
| SSG  | 0.8s | 1.2s | 1.5s |
| SSR  | 1.2s | 1.8s | 2.5s |
| CSR  | 2.0s | 3.5s | 4.0s |

选择合适的渲染策略，可以让用户获得最佳的体验。
""",
            category_id=cats[0].id,
            status="published",
            vector_status="completed",
            view_count=1523,
            published_at=datetime(2026, 4, 15, 10, 0, 0, tzinfo=timezone.utc),
        )

        article2 = Article(
            title="RAG 检索增强生成：从原理到实践",
            summary="详细解析 RAG 架构的核心组件，包括文本清洗、向量化、检索与生成，并提供可运行的代码示例。",
            slug="rag-from-theory-to-practice",
            content_md="""# RAG 检索增强生成：从原理到实践

## RAG 是什么

检索增强生成（Retrieval-Augmented Generation）是一种将信息检索与文本生成相结合的技术架构。它让 LLM 在回答问题之前，先从知识库中检索相关信息，再基于检索到的内容生成回答。

## 核心组件

### 1. 文本清洗

RAG 的第一步是对原始文档进行清洗。Markdown 文档需要去除标记符号、代码块等非语义内容。

### 2. 文本切片

清洗后的文本需要按照语义边界切分成合适大小的片段（chunks）。切片质量直接影响检索效果：

- 切片太小：信息不完整
- 切片太大：检索精度下降
- 推荐：150-300 字/片段

### 3. 向量化

使用 Embedding 模型将文本片段转换为向量。常用模型：
- BGE-small-zh：中文场景效果优秀
- text-embedding-3-small：OpenAI 方案

### 4. 向量检索

使用 pgvector 进行余弦相似度检索：

```sql
SELECT * FROM vector_chunk
ORDER BY embedding <=> query_embedding
LIMIT 5
```

### 5. 生成回答

将检索到的片段作为上下文，构建 prompt 发送给 LLM 生成最终回答。
""",
            category_id=cats[2].id,
            status="published",
            vector_status="completed",
            view_count=892,
            published_at=datetime(2026, 4, 20, 8, 0, 0, tzinfo=timezone.utc),
        )

        article3 = Article(
            title="FastAPI 异步编程最佳实践",
            summary="掌握 FastAPI 的异步特性，避免常见的性能陷阱，让你的 API 服务真正发挥异步优势。",
            slug="fastapi-async-best-practices",
            content_md="""# FastAPI 异步编程最佳实践

## 为什么选择 FastAPI

FastAPI 是目前最快的 Python Web 框架之一，原生支持异步编程，自动生成 OpenAPI 文档。

## 异步 ORM

SQLAlchemy 2.0 提供了完整的异步支持：

```python
async with AsyncSession() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

## 常见陷阱

1. 在 async 函数中使用同步阻塞调用
2. 数据库连接池配置不当
3. 没有使用连接池复用

## 性能优化建议

- 使用连接池（默认 5 个连接足够大部分场景）
- 避免 N+1 查询
- 使用 Redis 缓存热点数据
""",
            category_id=cats[1].id,
            status="published",
            vector_status="completed",
            view_count=456,
            published_at=datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        db.add_all([article1, article2, article3])
        await db.flush()

        # 6. Article-Tag associations
        db.add(ArticleTag(article_id=article1.id, tag_id=tags[0].id))  # Nuxt
        db.add(ArticleTag(article_id=article1.id, tag_id=tags[1].id))  # Vue
        db.add(ArticleTag(article_id=article1.id, tag_id=tags[2].id))  # TypeScript

        db.add(ArticleTag(article_id=article2.id, tag_id=tags[5].id))  # RAG
        db.add(ArticleTag(article_id=article2.id, tag_id=tags[6].id))  # Vector
        db.add(ArticleTag(article_id=article2.id, tag_id=tags[7].id))  # Embedding

        db.add(ArticleTag(article_id=article3.id, tag_id=tags[3].id))  # FastAPI
        db.add(ArticleTag(article_id=article3.id, tag_id=tags[4].id))  # PostgreSQL

        await db.commit()
        print("种子数据创建完成！")
        print(f"  管理员: {settings.admin_username}/{settings.admin_password}")
        print(f"  分类: {len(cats)} 个")
        print(f"  专题: {len(topics)} 个")
        print(f"  标签: {len(tags)} 个")
        print(f"  文章: 3 篇（已发布）")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
