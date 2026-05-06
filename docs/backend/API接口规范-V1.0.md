# 智能内容平台 API 接口规范

版本：V1.1
日期：2026-05-06
关联文档：`后端开发规范`、`数据库设计详细文档`、`docs/README.md`
Base URL：`/api/v1`

---

# 一、通用约定

## 1.1 统一响应格式

成功响应：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

分页列表响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

错误响应：
```json
{
  "code": 40401,
  "message": "文章不存在",
  "detail": null
}
```

## 1.2 鉴权与限流矩阵

| 接口域 | 路径前缀 | 鉴权方式 | 限流策略 | 说明 |
|-------|---------|---------|---------|------|
| 公开业务 | `/api/v1/public/*` | 无需鉴权 | 100次/分钟/IP | 供前端渲染与游客访问 |
| 智能问答 | `/api/v1/rag/*` | 无需鉴权 | 10次/分钟/IP | 供前端悬浮窗/问答页调用，严格限流防滥用 |
| 埋点监控 | `/api/v1/monitor/report` | 无需鉴权 | 300次/分钟/IP | 供前端 SDK 上报，高吞吐 |
| 运营后台 | `/api/v1/admin/*` | JWT Bearer | 60次/分钟/User | 管理员专属操作 |
| 登录接口 | `/api/v1/admin/login` | 无需鉴权 | 5次/分钟/IP | 防止暴力破解 |

- 后台操作接口需要 `Authorization: Bearer <token>` 请求头。
- Token 过期或未授权返回 `40100` 或 `40300`。
- 超过限流返回 `42900`。

## 1.3 分页

- 请求参数：`page`（默认 1）、`page_size`（默认 20，最大 100）
- 响应包含：`items`、`total`、`page`、`page_size`、`total_pages`

## 1.4 时间格式

所有时间字段使用 ISO 8601 格式：`"2026-05-04T12:00:00Z"`

---

# 二、前台公开接口 `/api/v1/public`

## 2.1 获取首页数据

```
GET /api/v1/public/home
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "featured_articles": [
      {
        "id": 1,
        "title": "Nuxt3 混合渲染实践",
        "summary": "深入探讨 SSR、SSG 与 CSR 的取舍策略...",
        "slug": "nuxt3-hybrid-rendering",
        "cover_url": "/uploads/covers/nuxt3.png",
        "tags": [{"id": 1, "name": "Nuxt"}],
        "category": {"id": 1, "name": "前端工程化", "slug": "frontend-engineering", "type": "category"},
        "reading_time": 8,
        "view_count": 1234,
        "published_at": "2026-05-01T10:00:00Z"
      }
    ],
    "topics": [
      {
        "id": 2,
        "name": "Nuxt 实践指南",
        "slug": "nuxt-guide",
        "description": "构建工具、性能优化、监控体系",
        "cover_url": "/uploads/covers/topic-nuxt.png",
        "article_count": 12,
        "updated_at": "2026-05-03T08:00:00Z"
      }
    ],
    "stats": {
      "total_articles": 25,
      "total_chunks": 520,
      "last_sync_at": "2026-05-04T02:00:00Z",
      "avg_rag_time_ms": 1200
    }
  }
}
```

## 2.2 获取文章列表

```
GET /api/v1/public/articles
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20，最大 100 |
| category_slug | string | 否 | 分类或专题的 slug 筛选 |
| tag_ids | string | 否 | 标签 ID 列表，逗号分隔 |
| sort | string | 否 | `latest`(默认) / `popular` / `updated` |
| keyword | string | 否 | 标题模糊搜索（简单筛选，区别于 2.9 搜索接口） |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Nuxt3 混合渲染实践",
        "summary": "深入探讨 SSR、SSG 与 CSR 的取舍策略...",
        "slug": "nuxt3-hybrid-rendering",
        "cover_url": "/uploads/covers/nuxt3.png",
        "tags": [{"id": 1, "name": "Nuxt"}],
        "category": {"id": 1, "name": "前端工程化", "slug": "frontend-engineering", "type": "category"},
        "reading_time": 8,
        "view_count": 1234,
        "published_at": "2026-05-01T10:00:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
  }
}
```

## 2.3 获取文章详情

```
GET /api/v1/public/articles/{slug}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "Nuxt3 混合渲染实践",
    "summary": "深入探讨 SSR、SSG 与 CSR 的取舍策略...",
    "slug": "nuxt3-hybrid-rendering",
    "content_md": "# Nuxt3 混合渲染实践\n\n## 背景\n...",
    "cover_url": "/uploads/covers/nuxt3.png",
    "tags": [
      {"id": 1, "name": "Nuxt"},
      {"id": 2, "name": "Vue"}
    ],
    "category": {"id": 1, "name": "前端工程化", "slug": "frontend-engineering", "type": "category"},
    "reading_time": 8,
    "view_count": 1234,
    "seo_title": "Nuxt3 混合渲染实践 | 智能内容平台",
    "seo_description": "深入探讨 SSR、SSG 与 CSR 的取舍策略...",
    "published_at": "2026-05-01T10:00:00Z",
    "updated_at": "2026-05-02T10:00:00Z",
    "related_articles": [
      {
        "id": 5,
        "title": "从零实现前端监控 SDK",
        "slug": "frontend-monitor-sdk",
        "summary": "...",
        "published_at": "2026-04-28T10:00:00Z"
      }
    ]
  }
}
```

错误码：
- `40401`：文章不存在
- `40402`：文章未发布

> `reading_time` 为服务端计算字段，计算公式：`max(1, ceil(len(content_md) / 500))`（约 500 字/分钟）。

## 2.4 获取分类列表

```
GET /api/v1/public/categories
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "前端工程化",
        "slug": "frontend-engineering",
        "type": "category",
        "description": "构建工具、性能优化、监控体系",
        "sort_order": 1,
        "article_count": 12
      }
    ]
  }
}
```

## 2.5 获取标签列表

```
GET /api/v1/public/tags
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 标签名称搜索 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {"id": 1, "name": "Nuxt", "article_count": 8},
      {"id": 2, "name": "Vue", "article_count": 10}
    ]
  }
}
```

## 2.6 获取标签详情

```
GET /api/v1/public/tags/{tag_id}
```
响应包含标签信息和关联的文章列表（分页）。

## 2.7 获取专题列表

```
GET /api/v1/public/topics
```

说明：专题数据复用 `category` 表，通过 `type='topic'` 区分。专题可以配置封面图。

响应类似分类列表，但返回的是专题数据：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 2,
        "name": "Nuxt 实践指南",
        "slug": "nuxt-guide",
        "type": "topic",
        "description": "从入门到混合渲染的最佳实践",
        "cover_url": "/uploads/covers/topic-nuxt.png",
        "sort_order": 1,
        "article_count": 8
      }
    ]
  }
}
```

## 2.8 获取专题详情

```
GET /api/v1/public/topics/{slug}
```
响应包含专题信息（带封面图和描述）和关联的文章列表（分页）。前端通过 `slug` 进行路由匹配。

## 2.9 文章搜索

```
GET /api/v1/public/search
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 搜索关键词 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

搜索范围：标题 + 摘要全文检索，使用 PostgreSQL `ilike` 或 `to_tsvector` 全文检索。与文章列表的 `keyword` 参数区别：`/search` 是独立的全文搜索入口，不附带分类/标签筛选逻辑；`/articles?keyword=` 是在列表页内对标题做轻量关键字匹配。

响应：分页文章列表（同文章列表接口格式）。

## 2.10 提交评论

```
POST /api/v1/public/articles/{slug}/comments
```

请求体：
```json
{
  "nickname": "访客小王",
  "content": "写得非常好，SSR 和 SSG 的选型讲得很清楚！"
}
```

校验：
- `nickname`：1-20 字符，必填
- `content`：1-500 字符，必填

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "nickname": "访客小王",
    "content": "写得非常好！",
    "likes": 0,
    "created_at": "2026-05-04T12:00:00Z"
  }
}
```

## 2.11 获取文章评论

```
GET /api/v1/public/articles/{slug}/comments
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量，默认 20 |

## 2.12 评论点赞

```
POST /api/v1/public/comments/{comment_id}/like
```
响应：
```json
{"code": 0, "message": "success", "data": {"likes": 1}}
```

## 2.13 增加文章浏览量

```
POST /api/v1/public/articles/{slug}/view
```
无需请求体。基于 IP 去重（Redis 缓存 30 分钟）。

---

# 三、后台管理接口 `/api/v1/admin`

所有后台接口需要 `Authorization: Bearer <token>` 请求头。

## 3.1 管理员登录

```
POST /api/v1/admin/login
```

请求体：
```json
{
  "username": "admin",
  "password": "your-password"
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 7200
  }
}
```

错误码：
- `40101`：账号或密码错误
- `42900`：登录频率过高

## 3.2 获取当前管理员信息

```
GET /api/v1/admin/me
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "last_login_at": "2026-05-04T10:00:00Z",
    "created_at": "2026-04-01T00:00:00Z"
  }
}
```

## 3.3 文章管理

### 3.3.1 获取文章列表（管理端）

```
GET /api/v1/admin/articles
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |
| keyword | string | 否 | 标题搜索 |
| category_id | int | 否 | 分类或专题筛选 |
| tag_ids | string | 否 | 标签 ID 列表 |
| status | string | 否 | `draft` / `published` / `archived` |
| vector_status | string | 否 | `pending` / `syncing` / `synced` / `failed` |

响应（相比前台多了管理字段）：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Nuxt3 混合渲染实践",
        "slug": "nuxt3-hybrid-rendering",
        "category": {"id": 1, "name": "前端工程化", "type": "category"},
        "tags": [{"id": 1, "name": "Nuxt"}],
        "status": "published",
        "vector_status": "synced",
        "vector_chunk_count": 15,
        "view_count": 1234,
        "published_at": "2026-05-01T10:00:00Z",
        "updated_at": "2026-05-02T10:00:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
  }
}
```

### 3.3.2 获取单篇文章（管理端）

```
GET /api/v1/admin/articles/{article_id}
```
返回文章全部字段，包括 SEO 字段和向量状态。

### 3.3.3 新建文章

```
POST /api/v1/admin/articles
```

请求体：
```json
{
  "title": "Nuxt3 混合渲染实践",
  "summary": "深入探讨 SSR、SSG 与 CSR 的取舍策略...",
  "slug": "nuxt3-hybrid-rendering",
  "content_md": "# Nuxt3 混合渲染实践\n\n...",
  "cover_url": "/uploads/covers/nuxt3.png",
  "category_id": 1,
  "tag_ids": [1, 2],
  "status": "draft",
  "seo_title": "Nuxt3 混合渲染实践",
  "seo_description": "深入探讨...取舍得当的渲染策略选择指南。"
}
```

校验规则：
| 字段 | 规则 |
|------|------|
| title | 必填，1-200 字符 |
| slug | 必填，1-200 字符，正则 `^[a-z0-9]+(?:-[a-z0-9]+)*$`，唯一 |
| content_md | status=published 时必填 |
| summary | 可选，最大 160 字符 |
| category_id | status=published 时必选，必须存在于 category 表 |
| tag_ids | 可选，最多 10 个 |
| seo_title | 可选，最大 60 字符 |
| seo_description | 可选，最大 160 字符 |

响应（201 Created）：
```json
{
  "code": 0,
  "message": "success",
  "data": {"id": 2, "slug": "nuxt3-hybrid-rendering"}
}
```

错误码：
- `40901`：slug 已存在

### 3.3.4 更新文章

```
PUT /api/v1/admin/articles/{article_id}
```
请求体同新建。slug 唯一性校验排除自身。

### 3.3.5 删除文章

```
DELETE /api/v1/admin/articles/{article_id}
```
级联删除关联的向量分片和评论。

响应：
```json
{"code": 0, "message": "success", "data": null}
```

### 3.3.6 发布文章

```
POST /api/v1/admin/articles/{article_id}/publish
```
将状态改为 `published`，执行发布前校验（标题、分类必填等），成功后自动触发向量同步。

### 3.3.7 下架文章

```
POST /api/v1/admin/articles/{article_id}/archive
```
将状态改为 `archived`。

### 3.3.8 手动同步向量

```
POST /api/v1/admin/articles/{article_id}/sync-vector
```
异步触发向量同步任务，立即返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {"status": "syncing"}
}
```

### 3.3.9 Slug 唯一性校验

```
GET /api/v1/admin/articles/check-slug?slug=xxx&exclude_id=1
```

响应：
```json
{"code": 0, "message": "success", "data": {"available": true}}
```

## 3.4 分类与专题管理

统一管理 `category` 表中的数据，通过 `type` 字段区分是普通分类还是专题。

### 3.4.1 获取分类/专题列表（管理端）

```
GET /api/v1/admin/categories
```
查询参数：
- `type`: 可选，`category` 或 `topic`。如果不传则返回所有。

响应包含文章数量统计，不分页。

### 3.4.2 新建分类/专题

```
POST /api/v1/admin/categories
```

请求体：
```json
{
  "name": "Nuxt 实践指南",
  "slug": "nuxt-guide",
  "type": "topic",
  "description": "从入门到混合渲染的最佳实践",
  "cover_url": "/uploads/covers/topic-nuxt.png",
  "sort_order": 1
}
```
校验：
- `name` 必填，1-50 字符，唯一。
- `slug` 必填，1-100 字符，正则验证，唯一。
- `type` 必填，只能是 `category` 或 `topic`。

### 3.4.3 更新分类/专题

```
PUT /api/v1/admin/categories/{category_id}
```

### 3.4.4 删除分类/专题

```
DELETE /api/v1/admin/categories/{category_id}
```
有关联文章时禁止删除，返回 `40902`。

### 3.4.5 更新分类/专题排序

```
PUT /api/v1/admin/categories/sort
```

请求体：
```json
{"items": [{"id": 1, "sort_order": 1}, {"id": 2, "sort_order": 2}]}
```

## 3.5 标签管理

### 3.5.1 获取标签列表（管理端）

```
GET /api/v1/admin/tags
```
包含文章数量统计。

### 3.5.2 新建标签

```
POST /api/v1/admin/tags
```

请求体：
```json
{"name": "Nuxt"}
```
校验：`name` 必填，1-30 字符，唯一。

### 3.5.3 更新标签

```
PUT /api/v1/admin/tags/{tag_id}
```

### 3.5.4 删除标签

```
DELETE /api/v1/admin/tags/{tag_id}
```
级联删除 article_tag 关联记录。

---

# 四、RAG 问答接口 `/api/v1/rag`

## 4.1 问答（非流式）

```
POST /api/v1/rag/ask
```

请求体：
```json
{
  "question": "Nuxt3 中 SSR 和 SSG 如何选择？",
  "conversation_id": "uuid-string",
  "source_article_slug": null
}
```

校验：
- `question`：必填，1-500 字符
- `conversation_id`：可选，用于多轮对话（首版可为 null）
- `source_article_slug`：可选，限定在某篇文章内检索

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "Nuxt3 中 SSR 和 SSG 如何选择？",
    "answer": "根据知识库内容，SSR 适用于需要动态数据且关注 SEO 的页面...",
    "sources": [
      {
        "chunk_id": 42,
        "article_id": 1,
        "article_title": "Nuxt3 混合渲染实践",
        "article_slug": "nuxt3-hybrid-rendering",
        "content": "SSR 适用于文章详情页等需要动态数据且关注 SEO 的页面...",
        "similarity": 0.92,
        "relevance": "high"
      },
      {
        "chunk_id": 45,
        "article_id": 1,
        "article_title": "Nuxt3 混合渲染实践",
        "article_slug": "nuxt3-hybrid-rendering",
        "content": "SSG 适用于首页、分类页等不常变化的内容页面...",
        "similarity": 0.85,
        "relevance": "high"
      }
    ],
    "no_match": false
  }
}
```

兜底响应（无匹配片段）：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conversation_id": "...",
    "question": "...",
    "answer": "未找到相关内容，请尝试其他问题",
    "sources": [],
    "no_match": true
  }
}
```

错误码：
- `42900`：提问频率过高（10次/分钟/IP）
- `50200`：LLM API 不可用

## 4.2 问答（流式输出，P1 增强）

```
POST /api/v1/rag/ask/stream
```
请求体同非流式。

响应使用 SSE（Server-Sent Events）：
```
data: {"type": "sources", "data": [...]}
data: {"type": "token", "content": "根据"}
data: {"type": "token", "content": "知识库"}
...
data: {"type": "done"}
data: {"type": "error", "message": "..."}
```

## 4.3 获取示例问题

```
GET /api/v1/rag/suggestions
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      "Nuxt3 中 SSR 和 SSG 如何选择？",
      "这个项目如何实现前端监控？",
      "pgvector 在 RAG 里负责什么？"
    ]
  }
}
```
示例问题从环境变量或配置文件读取，或从高频问题自动提取。

---

# 五、监控上报接口 `/api/v1/monitor`

## 5.1 批量上报

```
POST /api/v1/monitor/report
```

请求体（支持单条或批量）：
```json
{
  "events": [
    {
      "type": "pv",
      "timestamp": "2026-05-04T12:00:00.000Z",
      "data": {
        "page_url": "/articles/nuxt3-hybrid-rendering",
        "referrer": "https://www.google.com",
        "session_id": "uuid"
      }
    },
    {
      "type": "web_vital",
      "timestamp": "2026-05-04T12:00:01.000Z",
      "data": {
        "page_url": "/articles/nuxt3-hybrid-rendering",
        "metric": "LCP",
        "value": 1234.5,
        "rating": "good"
      }
    },
    {
      "type": "error",
      "timestamp": "2026-05-04T12:00:02.000Z",
      "data": {
        "page_url": "/articles/nuxt3-hybrid-rendering",
        "error_type": "js_error",
        "message": "Uncaught TypeError: Cannot read property 'foo' of undefined",
        "filename": "/_nuxt/app.js",
        "lineno": 42,
        "colno": 15,
        "stack": "TypeError: ..."
      }
    },
    {
      "type": "exposure",
      "timestamp": "2026-05-04T12:00:03.000Z",
      "data": {
        "page_url": "/",
        "element_id": "article-card-1",
        "element_type": "article_card",
        "duration_ms": 3500
      }
    },
    {
      "type": "resource_error",
      "timestamp": "2026-05-04T12:00:04.000Z",
      "data": {
        "page_url": "/articles/nuxt3-hybrid-rendering",
        "resource_type": "img",
        "resource_url": "/uploads/covers/missing.png",
        "element_tag": "img"
      }
    }
  ]
}
```

校验：
- 单次最多上报 50 条事件
- `type` 必须是已注册的事件类型
- `timestamp` 必填，ISO 8601 格式
- `data.page_url` 必填

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {"received": 5, "accepted": 5}
}
```

事件类型枚举：
| type | 说明 |
|------|------|
| `pv` | 页面访问 |
| `duration` | 页面停留时长 |
| `web_vital` | Core Web Vitals（LCP/CLS/INP） |
| `error` | JS 异常 / Promise 异常 |
| `resource_error` | 静态资源加载失败 |
| `api_error` | 接口异常（由 $fetch 拦截器上报） |
| `exposure` | 元素曝光 |

## 5.2 监控数据查询（管理端）

```
GET /api/v1/monitor/stats
```

查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 否 | 开始日期，ISO 8601 |
| end_date | string | 否 | 结束日期 |
| event_type | string | 否 | 事件类型筛选 |
| page_url | string | 否 | 页面路径筛选 |
| page | int | 否 | 页码 |

---

# 六、运营大盘接口 `/api/v1/admin/dashboard`

## 6.1 获取大盘概览

```
GET /api/v1/admin/dashboard/overview
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "today": {
      "pv": 1234,
      "uv": 567,
      "rag_questions": 15,
      "avg_rag_time_ms": 1200
    },
    "articles": {
      "total": 25,
      "published": 20,
      "draft": 5,
      "synced": 18,
      "sync_failed": 2
    },
    "performance": {
      "lcp_avg_ms": 1500,
      "cls_avg": 0.05,
      "inp_avg_ms": 80,
      "error_count_7d": 12
    }
  }
}
```

## 6.2 访问趋势

```
GET /api/v1/admin/dashboard/trends
```
查询参数：`days`（默认 7）

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "pv_trend": [
      {"date": "2026-05-01", "pv": 1200, "uv": 500},
      {"date": "2026-05-02", "pv": 1350, "uv": 520}
    ],
    "popular_articles": [
      {"id": 1, "title": "...", "slug": "...", "views": 1234}
    ]
  }
}
```

## 6.3 知识库状态

```
GET /api/v1/admin/dashboard/knowledge-status
```

---

# 七、知识库运维接口 `/api/v1/admin/knowledge`

所有接口需鉴权。

## 7.1 获取知识库状态

```
GET /api/v1/admin/knowledge/status
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_articles": 25,
    "synced_articles": 18,
    "failed_articles": 2,
    "total_chunks": 520,
    "last_sync_at": "2026-05-04T02:00:00Z"
  }
}
```

## 7.2 获取文章向量状态列表

```
GET /api/v1/admin/knowledge/articles
```

响应（分页）：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "article_id": 1,
        "title": "Nuxt3 混合渲染实践",
        "slug": "nuxt3-hybrid-rendering",
        "vector_status": "synced",
        "chunk_count": 15,
        "last_sync_at": "2026-05-04T02:00:00Z"
      },
      {
        "article_id": 5,
        "title": "从零实现前端监控 SDK",
        "slug": "frontend-monitor-sdk",
        "vector_status": "failed",
        "chunk_count": 0,
        "last_sync_at": null
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
  }
}
```

## 7.3 全量向量重建

```
POST /api/v1/admin/knowledge/rebuild
```

异步启动全量重建任务，立即返回任务 ID：
```json
{
  "code": 0,
  "message": "success",
  "data": {"task_id": "uuid", "status": "running"}
}
```

## 7.4 查询重建进度

```
GET /api/v1/admin/knowledge/rebuild/{task_id}/progress
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "uuid",
    "status": "running",
    "total": 25,
    "completed": 10,
    "failed": 0,
    "progress_pct": 40
  }
}
```

status 枚举：`pending` / `running` / `success` / `failed` / `partial_failed`

## 7.5 同步失败文章重试

```
POST /api/v1/admin/knowledge/retry-failed
```
批量重试所有 vector_status=failed 的文章。

---

# 八、健康检查接口

```
GET /api/v1/health
```

无需鉴权，用于 Docker 健康检查和负载均衡探测。

响应：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "embedding_model": "loaded"
  }
}
```

---

# 九、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| V1.0 | 2026-05-04 | 补齐全部 API 接口规范，覆盖前台、后台、RAG、监控、大盘、知识库运维 |
| V1.1 | 2026-05-04 | 修正鉴权口径，统一专题与分类建模设计，提供明确的限流矩阵 |
