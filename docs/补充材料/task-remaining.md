# 智能内容平台 -- 剩余任务清单

日期: 2026-05-04
分析方式: 对比前后端任务清单与实际代码实现，识别高价值缺口

---

## 实现概况

| 阶段 | 后端 | 前端 | 状态 |
|------|------|------|------|
| Phase 0 (骨架/基础设施) | 完成 | 完成 | 全链路可运行 |
| Phase 1 (内容主链路) | 完成 | 完成 | CRUD/登录/编辑器就绪 |
| Phase 2 (RAG/监控闭环) | 完成 | 完成 | 问答/监控/Docker 就绪 |
| Phase 3 (展示增强) | 完成 | 完成 | Dashboard/监控/知识库就绪 |
| Phase 4 (质量/部署) | 部分完成 | 部分完成 | 测试覆盖率不足 |

当前状态: 14 个前端页面 + 21 个组件 + 49 条 API 路由 + 104 个后端测试 + 24 个前端测试 + 9 个 E2E 测试

---

## 剩余任务 (按优先级排列)

### ~~任务 1: RAG 流式输出 (SSE) 端点~~ ✅ 已完成

**优先级**: P0 -- 面试演示的核心差异化功能

**当前状态**: 已完成。后端 `POST /api/v1/rag/ask/stream` SSE 端点已实现 (`backend/app/routers/rag.py:56`)，`generate_answer_stream` 异步生成器就绪 (`backend/app/services/rag/generator.py`)，前端 `pages/ask.vue` 已集成 SSE 消费逻辑（含流中断降级为非流式请求）。

---

### 任务 2: OpenAPI 生成 TypeScript 类型定义

**优先级**: P0 -- 代码质量和开发体验基线

**当前状态**: `frontend/types/` 目录为空。所有 API 调用 (`useApi().get<any>()`) 均使用 `any` 类型，无编译时类型检查。Nuxt3 + TypeScript 项目实际缺失类型安全。

**缺失内容**:
- `frontend/types/api.d.ts` 文件 (任务清单 0.4 明确要求)
- 请求参数和响应体的 TS 接口定义
- 枚举类型 (article status, vector status, event type 等)

**建议方案**:
1. 从 `http://localhost:8000/openapi.json` 获取 OpenAPI schema
2. 使用 `openapi-typescript` 生成 `api.d.ts`
3. 更新 `useApi.ts` 的泛型参数使用生成的类型，例如：
   - `ArticleListResponse` / `ArticleDetailResponse`
   - `TokenResponse` / `LoginRequest`
   - `AskRequest` / `AskResponse`

**验收标准**:
- `npm run typecheck` 通过
- `useApi().get<ArticleListResponse>("/public/articles")` 有完整的字段类型提示
- 至少 5 个页面的 `any` 类型调用替换为具体类型

**预估时间**: 30 分钟

---

### 任务 3: 文章编辑器草稿自动保存

**优先级**: P0 -- 内容创作者核心体验

**当前状态**: `pages/admin/articles/[id].vue` 编辑器的 `form` 数据仅存在于 Vue reactive 对象中，刷新页面或意外关闭后内容丢失。任务清单 1.6 明确要求 "草稿刷新页面后可恢复"。

**缺失内容**:
- localStorage 草稿读写逻辑
- 防抖自动保存 (输入停止后 2 秒)
- 草稿恢复提示 UI
- 保存成功后清理草稿

**实现要点**:
- 在 `admin/articles/[id].vue` 中使用 `watchDebounced` 监听 `form` 变化
- 草稿 key 格式: `draft_article_{id}` (新建用 `draft_article_new`)
- 页面加载时检查 `localStorage` 是否有草稿，有则提示"检测到未保存的草稿，是否恢复？"
- 发布/保存成功后 `localStorage.removeItem(draftKey)`

**验收标准**:
- 编辑文章时输入内容，刷新页面后提示恢复草稿
- 点击"恢复"后表单数据完整还原
- 点击"放弃"后清除草稿且表单为空
- 保存成功或发布成功后不再提示草稿恢复

**预估时间**: 30 分钟

---

### 任务 4: RAG 检索器集成测试

**优先级**: P1 -- 核心差异化功能质量保障

**当前状态**: RAG 测试仅覆盖 `cleaner.py` (14 个用例) 和 `splitter.py` (9 个用例)。`retriever.py`、`embedder.py`、`sync.py` 均无测试。项目的技术核心 (pgvector 向量检索) 缺少自动化验证。

**缺失的测试**:
- `test_rag_retriever.py`: mock AsyncSession + raw SQL 结果，验证 top_k 截断、threshold 过滤、空结果处理
- `test_rag_sync.py`: mock Article + VectorChunk 写入，验证 sync 流程状态转换 (pending -> syncing -> synced/failed)
- `test_rag_embedder.py`: mock SentenceTransformer 加载，验证 encode_single 返回 512 维向量

**建议先做 retriever (最高价值/最低依赖)**:
- 测试 0 结果场景 (相似度低于 threshold)
- 测试 top_k 限制 (请求 10 条只返回 ≤ top_k)
- 测试仅返回已发布文章的向量
- 测试数据库异常时的空列表兜底

**验收标准**:
- 新增 `backend/tests/test_rag_retriever.py`，至少 6 个用例
- `pytest backend/tests/test_rag_retriever.py -v` 全部通过
- 覆盖: 正常检索、无匹配、低相似度过滤、top_k 限制、空数据库、SQL 异常

**预估时间**: 30 分钟

---

### 任务 5: 后端 API 限流中间件集成测试

**优先级**: P1 -- 安全防护功能验证

**当前状态**: `app/middleware/rate_limit.py` 实现了基于 Redis 滑动窗口的限流 (可降级到内存)。但该中间件没有任何测试覆盖。限流逻辑的准确性 (窗口边界、429 响应、降级路径) 完全依赖于人工验证。

**缺失内容**:
- 测试 Redis 可用时的正常限流计数
- 测试超限返回 429 状态码
- 测试窗口过期后计数重置
- 测试 Redis 不可用时的内存降级
- 测试不同路由的限流配置 (登录接口更严格)

**实现要点**:
- Mock Redis client (或使用 fakeredis)
- 使用 `httpx.AsyncClient` + `ASGITransport` 连续发送请求
- 验证第 N+1 次请求返回 429
- 验证 429 响应体包含 `Retry-After` 头或重试提示

**验收标准**:
- 新增 `backend/tests/test_rate_limit.py`，至少 6 个用例
- `pytest backend/tests/test_rate_limit.py -v` 全部通过
- 覆盖: 正常请求通过、超限返回 429、窗口重置、Redis 降级、登录接口独立限制

**预估时间**: 30 分钟

---

## 选做任务 (如果时间允许)

### S1: 前端 Vitest 测试补充
- 当前仅 2 个测试文件 (auth store + monitor queue)
- 建议添加: `useApi` 错误处理测试 (401 跳转)、`RAGFloatingButton` 键盘交互测试 (Esc 关闭 + 焦点管理)

### S2: 文章详情页图片懒加载
- `pages/articles/[slug].vue` 渲染的 Markdown 图片可能导致 CLS
- 为 `<img>` 添加 `loading="lazy"` 和宽高比占位

### S3: 后端健康检查增强
- 当前 `/api/v1/health` 仅返回静态状态
- 建议增加数据库连通性检查和 Redis 连通性检查

---

## 不推荐现在做的

以下任务在当前阶段投入产出比低:

1. **Lighthouse 报告与截图**: 需要本地或 CI 环境启动完整服务，应在部署验证后统一产出
2. **README 补充**: 等待截图和部署验证完成后一次性完成
3. **专题页 SEO 优化**: 页面已存在且基本 SEO 信息就绪，细化可后续迭代
4. **全量 E2E Playwright**: 当前 6 个 E2E 用例已覆盖核心流程，增加更多用例边际收益递减
5. **前端的独立 MarkdownRenderer 组件抽离**: 当前内联实现功能完整，抽离不产生用户可见价值
