import asyncio
import sys

sys.path.insert(0, ".")

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.admin import Admin
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag


async def seed():
    async with async_session_factory() as db:
        # 1. 创建管理员
        admin = Admin(username="admin", password_hash=hash_password("admin123"))
        db.add(admin)

        # 2. 创建分类
        categories = [
            Category(name="前端工程化", slug="frontend-engineering", type="category", sort_order=1),
            Category(name="Vue/Nuxt", slug="vue-nuxt", type="category", sort_order=2),
            Category(name="AI/RAG", slug="ai-rag", type="category", sort_order=3),
            Category(name="后端开发", slug="backend-dev", type="category", sort_order=4),
            Category(
                name="Nuxt 实践指南",
                slug="nuxt-guide",
                type="topic",
                sort_order=1,
                description="从入门到混合渲染的最佳实践",
            ),
            Category(
                name="RAG 技术探索",
                slug="rag-exploration",
                type="topic",
                sort_order=2,
                description="检索增强生成技术在内容平台中的应用",
            ),
        ]
        db.add_all(categories)
        await db.flush()

        # 3. 创建标签
        tags = [
            Tag(name="Nuxt"),
            Tag(name="Vue"),
            Tag(name="TypeScript"),
            Tag(name="FastAPI"),
            Tag(name="RAG"),
            Tag(name="PostgreSQL"),
            Tag(name="Docker"),
            Tag(name="性能优化"),
            Tag(name="前端监控"),
        ]
        db.add_all(tags)
        await db.flush()

        # 4. 创建示例文章
        articles = [
            Article(
                title="Nuxt3 混合渲染实战：从 SSG 到 SSR 的完整指南",
                summary="深入探讨 Nuxt3 混合渲染策略，涵盖预渲染、服务端渲染和客户端渲染的最佳实践。",
                slug="nuxt3-hybrid-rendering-guide",
                content_md="""# Nuxt3 混合渲染实战

## 什么是混合渲染

混合渲染是 Nuxt3 最强大的特性之一，它允许你在同一个应用中混合使用 SSG、SSR 和 CSR。

### SSG（静态站点生成）

静态站点生成在构建时将页面预渲染为 HTML 文件，适合内容变化不频繁的页面。

- 首页
- 分类列表页
- 专题页

### SSR（服务端渲染）

服务端渲染在请求时动态生成 HTML，适合需要实时数据的页面。

- 文章详情页
- 搜索结果页

### CSR（客户端渲染）

客户端渲染完全在浏览器中执行，适合强交互的后台页面。

- 管理员后台
- 监控大盘

## 配置 routeRules

```ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },
    '/articles': { prerender: true },
    '/articles/**': { ssr: true },
    '/admin/**': { ssr: false },
  }
})
```
""",
                category_id=categories[1].id,
                status="published",
                vector_status="pending",
                view_count=1280,
                published_at=None,
                seo_title="Nuxt3 混合渲染实战指南",
                seo_description="深入探讨 Nuxt3 混合渲染策略，涵盖预渲染、服务端渲染和客户端渲染的最佳实践。",
            ),
            Article(
                title="构建 RAG 问答系统：从文本处理到向量检索",
                summary="手把手教你构建基于 pgvector 的 RAG 问答系统，包含文本清洗、切片、向量化和检索全流程。",
                slug="build-rag-qa-system",
                content_md="""# 构建 RAG 问答系统

## 什么是 RAG

RAG（检索增强生成）是一种结合了信息检索和文本生成的技术架构。

### 核心流程

1. 文档预处理：清洗和分片
2. 向量化：将文本转换为向量
3. 相似度检索：找到最相关的文档片段
4. 答案生成：基于上下文调用 LLM 生成答案

## 文本清洗

文本清洗是 RAG 的第一步，需要对原始 Markdown 内容进行预处理：

- 去除 Markdown 标记符号
- 移除多余空行和空格
- 保留有意义的文本内容

## 向量检索

使用 pgvector 的余弦相似度进行向量检索，召回与问题最相关的文档片段。
""",
                category_id=categories[2].id,
                status="published",
                vector_status="pending",
                view_count=960,
                published_at=None,
                seo_title="构建 RAG 问答系统",
                seo_description="手把手教你构建基于 pgvector 的 RAG 问答系统。",
            ),
            Article(
                title="前端监控体系搭建：从采集到可视化",
                summary="自研前端监控 SDK，覆盖性能、异常、用户行为三大维度，打造完整的监控闭环。",
                slug="frontend-monitoring-system",
                content_md="""# 前端监控体系搭建

## 为什么需要前端监控

线上问题排查离不开完善的监控体系。一个合格的前端监控系统需要覆盖：

- 页面性能（LCP、CLS、INP）
- JS 异常和 Promise 异常
- 资源加载错误
- 用户行为埋点

## 监控 SDK 设计

自研监控 SDK 采用事件队列 + 批量上报的架构，避免阻塞主线程。

### 核心采集器

1. PVCollector：页面访问统计
2. WebVitalsCollector：核心性能指标
3. ErrorCollector：JS 和 Promise 异常
4. ResourceCollector：资源加载错误
""",
                category_id=categories[0].id,
                status="published",
                vector_status="pending",
                view_count=860,
                published_at=None,
                seo_title="前端监控体系搭建",
                seo_description="自研前端监控 SDK，覆盖性能、异常、用户行为三大维度。",
            ),
        ]
        import datetime

        for a in articles:
            a.published_at = datetime.datetime.now(datetime.timezone.utc)
        db.add_all(articles)
        await db.flush()

        await db.commit()
        print("Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
