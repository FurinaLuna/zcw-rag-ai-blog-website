# 智能内容平台最终开发文档

文档版本：V2.0
更新日期：2026-05-06
适用范围：本地开发、联调测试、数据库变更、RAG 开发、前后端协作、Docker 部署、上线验收
文档定位：本文件是项目唯一主开发手册；其他文档作为接口、数据库、前端规范等专题补充

## 1. 你先看什么

如果你现在要开始开发，按下面顺序阅读和执行：

1. 先看本文的“快速开始”和“开发流程”。
2. 启动本地环境，确认前后端、数据库、Redis 都可用。
3. 根据任务类型跳到对应章节：前端、后端、数据库、RAG、监控、测试。
4. 需要查接口细节时看 `docs/backend/API接口规范-V1.0.md`。
5. 需要查表结构细节时看 `docs/backend/数据库设计详细文档-V1.0.md`。
6. 需要查页面和组件规范时看 `docs/frontend/前端设计规范-V1.0.md` 与 `docs/frontend/前端组件规范-V1.0.md`。

## 2. 项目目标

本项目是一个基于 Nuxt 3 + FastAPI + PostgreSQL + pgvector 的智能内容平台，核心目标不是单纯做博客，而是落地一条完整的“内容分发 + 运营后台 + RAG 问答 + 前端监控 + 容器化交付”开发链路。

当前代码已经具备以下主能力：

- 前台内容站：首页、文章列表、文章详情、专题、搜索、关于页、问答页。
- 后台管理：管理员登录、文章管理、知识库运维、监控页、概览页。
- 后端 API：公开内容接口、后台管理接口、RAG 接口、监控接口。
- 数据层：PostgreSQL 16、pgvector、Redis、Alembic 迁移。
- AI 能力：文本清洗、切片、向量化、检索、生成、向量同步与重建。
- 质量保障：pytest、Vitest、Playwright、类型检查。
- 交付方式：Docker Compose 一键启动。

## 3. 当前技术基线

### 3.1 版本基线

| 项 | 当前基线 |
|---|---|
| 前端应用版本 | `0.1.0` |
| 后端应用版本 | `0.1.0` |
| 后端 API 版本 | `1.0.0` |
| Python | `>=3.12` |
| Node.js | 建议 `20 LTS` |
| npm | 建议 `10+` |
| PostgreSQL | `16` |
| Redis | `7` |
| Docker Compose 文件格式 | `3.9` |
| Embedding 模型 | `BAAI/bge-small-zh-v1.5` |

### 3.2 核心技术栈

| 层 | 技术 |
|---|---|
| 前端 | Nuxt 3、Vue 3、TypeScript、TailwindCSS、Pinia |
| 后端 | FastAPI、SQLAlchemy 2.0 async、Pydantic |
| 数据库 | PostgreSQL 16 + pgvector |
| 缓存 | Redis |
| AI | Sentence Transformers、OpenAI-compatible LLM API |
| 测试 | pytest、Vitest、Playwright |
| 部署 | Docker、Docker Compose |

## 4. 仓库结构

```text
zcw-rag-ai-blog-website/
├── frontend/                     # Nuxt 3 前端
│   ├── pages/                    # 页面路由
│   ├── components/               # 业务组件与通用组件
│   ├── composables/              # 请求封装
│   ├── stores/                   # Pinia 状态
│   ├── plugins/                  # 监控插件
│   ├── styles/                   # 设计 token 与全局样式
│   ├── tests/                    # 前端单测
│   ├── e2e/                      # Playwright 测试
│   ├── types/                    # 前端类型定义
│   ├── package.json
│   └── nuxt.config.ts
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── routers/              # public / admin / rag / monitor
│   │   ├── services/             # 业务服务与 RAG 管线
│   │   ├── models/               # SQLAlchemy ORM 模型
│   │   ├── schemas/              # 请求/响应模型
│   │   ├── dependencies/         # 鉴权与 DB 依赖
│   │   ├── middleware/           # CORS / 限流 / 异常
│   │   ├── core/                 # 配置 / 安全 / 日志 / 数据库 / Redis
│   │   └── main.py               # 应用入口
│   ├── alembic/versions/         # 数据库迁移
│   ├── scripts/                  # seed_db / rebuild_vectors
│   ├── tests/                    # 后端测试
│   ├── pyproject.toml
│   └── .env.example
├── docs/                         # 项目文档
├── docker-compose.yml            # 本地 / 演示环境编排
└── README.md                     # 仓库入口
```

## 5. 架构与职责边界

### 5.1 前端渲染策略

Nuxt 当前渲染策略以 `frontend/nuxt.config.ts` 为准：

- `prerender`：`/`、`/articles`、`/topics`、`/about`
- `SSR`：`/articles/**`、`/topics/**`
- `CSR`：`/search`、`/ask`、`/admin/**`

开发原则：

- SEO 关键页尽量维持 SSG 或 SSR。
- 依赖浏览器 API 的逻辑放在 `.client.vue`、`onMounted` 或客户端插件中。
- 后台与监控页默认按 CSR 思路开发，不要强行引入服务端依赖。

### 5.2 后端模块边界

后端分层按职责拆分：

- `routers/`：只负责路由、参数提取、调用服务、返回响应。
- `services/`：承载业务逻辑，禁止把复杂业务堆进 router。
- `models/`：数据库模型定义。
- `schemas/`：接口入参与出参。
- `dependencies/`：鉴权、数据库会话等复用依赖。
- `middleware/`：限流、异常、CORS、请求级横切逻辑。
- `core/`：配置、安全、日志、数据库、Redis。

### 5.3 RAG 链路

当前 RAG 主链路位于 `backend/app/services/rag/`：

- `cleaner.py`：文本清洗
- `splitter.py`：文本切片
- `embedder.py`：向量化
- `retriever.py`：相似度检索
- `generator.py`：生成回答
- `sync.py`：文章与向量分片同步

开发原则：

- 改清洗或切片规则时，必须评估对历史向量数据的影响。
- 改 embedding 维度或模型时，必须同步更新环境变量和向量数据。
- 改生成逻辑时，不能破坏“无命中兜底”和“基于检索内容回答”的边界。

## 6. 环境变量

### 6.1 后端环境变量

配置文件：`backend/.env`

| 变量 | 必填 | 说明 |
|---|---|---|
| `DATABASE_URL` | 是 | 异步数据库连接 |
| `DATABASE_URL_SYNC` | 是 | 同步数据库连接，Alembic 使用 |
| `REDIS_URL` | 是 | Redis 连接 |
| `JWT_SECRET_KEY` | 是 | JWT 密钥，生产环境必须更换 |
| `JWT_ALGORITHM` | 否 | 默认 `HS256` |
| `JWT_EXPIRE_MINUTES` | 否 | Token 有效期 |
| `ADMIN_USERNAME` | 否 | 初始管理员账号 |
| `ADMIN_PASSWORD` | 否 | 初始管理员密码 |
| `CORS_ORIGINS` | 是 | 允许跨域来源 |
| `LLM_API_KEY` | 否 | 使用 RAG 生成时需要 |
| `LLM_API_BASE` | 否 | OpenAI-compatible 接口地址 |
| `LLM_MODEL` | 否 | 大模型名称 |
| `EMBEDDING_MODEL` | 否 | 向量模型名称 |
| `EMBEDDING_DIM` | 否 | 向量维度，默认 512 |
| `LOG_LEVEL` | 否 | 日志级别 |
| `RATE_LIMIT_PER_MINUTE` | 否 | 基础限流参数 |

### 6.2 前端环境变量

配置文件：`frontend/.env`

| 变量 | 必填 | 说明 |
|---|---|---|
| `NUXT_PUBLIC_API_BASE` | 是 | 前端请求后端 API 基础地址 |
| `NUXT_PUBLIC_MONITOR_ENDPOINT` | 是 | 监控上报地址 |
| `NUXT_PUBLIC_SITE_NAME` | 否 | 站点名称 |

## 7. 快速开始

### 7.1 使用 Docker 启动

在项目根目录执行：

```bash
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_db.py
```

启动后访问：

- 前台首页：`http://localhost:3000`
- 后台登录：`http://localhost:3000/admin/login`
- API 文档：`http://localhost:8000/docs`
- OpenAPI：`http://localhost:8000/openapi.json`
- 健康检查：`http://localhost:8000/api/v1/health`

### 7.2 本地开发启动

#### PowerShell

```powershell
# 后端
cd .\backend
Copy-Item .env.example .env
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed_db.py
uvicorn app.main:app --reload
```

新开一个终端：

```powershell
# 前端
cd .\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

#### Bash

```bash
# backend
cd backend
cp .env.example .env
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed_db.py
uvicorn app.main:app --reload
```

```bash
# frontend
cd frontend
cp .env.example .env
npm install
npm run dev
```

## 8. 日常开发流程

### 8.1 推荐流程

1. 先明确本次需求属于前端、后端、数据库、RAG、监控还是部署。
2. 先改数据结构和接口契约，再改页面和交互，避免反复返工。
3. 每次开发只覆盖一条清晰主链路，例如“新增文章字段”或“新增问答来源展示”。
4. 改完先跑最小必要测试，再跑全链路验证。
5. 完成后同步更新文档、示例环境变量和必要截图。

### 8.2 功能开发顺序建议

- 改数据库：先 `models`，再 Alembic，再 service/router。
- 改接口：先 `schemas` 与 service，再 router，再前端类型和页面。
- 改页面：先页面数据流，再组件拆分，再样式和状态。
- 改 RAG：先离线处理链路，再在线检索，再问答 UI。
- 改监控：先前端采集，再后端接收，再后台展示。

## 9. 前端开发说明

### 9.1 前端目录使用约定

- `pages/`：页面级路由；页面负责数据装配，不要塞过多展示细节。
- `components/common/`：通用组件。
- `components/article/`、`components/comment/`、`components/layout/`、`components/rag/`、`components/admin/`：按业务域拆分。
- `composables/useApi.ts`：统一请求入口。
- `stores/`：只放跨页面共享状态，如登录态。
- `plugins/monitor.client.ts`：浏览器监控逻辑。
- `styles/tokens.css`：设计 token；新增视觉变量优先放这里。

### 9.2 前端开发规则

- 页面优先复用已有组件，不重复造轮子。
- 新接口优先通过 `useApi` 接入，不直接散落 `$fetch`。
- 任何管理后台页面都要考虑未登录跳转、加载态、空态、失败态。
- 任何文章与问答页面都要考虑首屏、滚动体验和移动端布局。
- 新增类型时优先维护 `frontend/types/api.d.ts`，避免继续扩散 `any`。

### 9.3 前端新增页面的标准步骤

1. 在 `pages/` 新建页面。
2. 若涉及公共块，优先提取到 `components/`。
3. 需要接口时，通过 `useApi.ts` 统一封装调用。
4. 需要共享状态时，再决定是否进入 `stores/`。
5. 补充单测或 E2E，至少覆盖核心交互。
6. 路由若涉及渲染模式变化，更新 `nuxt.config.ts` 的 `routeRules`。

## 10. 后端开发说明

### 10.1 后端目录使用约定

- `routers/`：只处理路由层。
- `services/`：按业务实体拆分服务。
- `schemas/`：请求体、响应体、分页结构统一管理。
- `models/`：表结构和关系定义。
- `middleware/rate_limit.py`：限流逻辑。
- `middleware/exception.py`：统一异常处理。
- `dependencies/auth.py`：管理员鉴权。
- `core/config.py`：所有配置读取入口。

### 10.2 后端开发规则

- API 返回格式保持统一，不要单个接口自定义返回壳。
- router 不直接写复杂 SQL，复杂查询放到 service。
- schema 变更后，前端契约和接口文档必须同步关注。
- 新增后台接口默认要考虑鉴权、限流、错误返回。
- 任何数据库写操作都要考虑事务边界与回滚。

### 10.3 新增接口的标准步骤

1. 在 `schemas/` 增加入参与出参。
2. 在 `services/` 写业务逻辑。
3. 在 `routers/` 暴露接口。
4. 需要鉴权时接入 `dependencies/auth.py`。
5. 补充或更新测试。
6. 联调前检查 `/docs` 和 `/openapi.json` 是否正确反映变更。

## 11. 数据库与迁移

### 11.1 当前核心表

当前核心表包括：

- `admin`
- `article`
- `category`
- `tag`
- `article_tag`
- `comment`
- `monitor_log`
- `vector_chunk`

### 11.2 迁移规范

改模型后按以下顺序执行：

```bash
cd backend
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
```

要求：

- 自动生成后必须人工检查迁移脚本。
- 不允许直接手改线上库结构而不写迁移。
- 影响历史数据的字段变更必须写清数据迁移策略。
- 变更 `vector_chunk` 相关结构时，评估是否需要执行向量重建。

## 12. RAG 开发与知识库运维

### 12.1 典型开发场景

- 改文本清洗规则。
- 改切片长度或分段策略。
- 改 embedding 模型。
- 改检索阈值、TopK、排序逻辑。
- 改回答生成提示词与兜底策略。

### 12.2 开发与验证顺序

1. 先改 `services/rag/` 对应模块。
2. 先跑单元测试，确保 cleaner / splitter / retriever 等基础逻辑不回退。
3. 必要时执行向量重建脚本。
4. 再到前端问答页和后台知识库页做联调。
5. 确认无命中场景、异常场景、引用来源展示都正常。

### 12.3 常用命令

```bash
cd backend
python scripts/rebuild_vectors.py
```

适用场景：

- 初次导入知识库
- 批量修改文章正文后
- 调整 embedding 模型或切片策略后
- 历史向量数据异常需要修复时

## 13. 前端监控开发

监控链路由前端采集、后端接收、后台可视化三段组成。

开发时注意：

- 前端采集逻辑在客户端执行，不要放到 SSR 阶段。
- 异常、性能、PV 等事件结构要稳定，避免后端统计口径频繁漂移。
- 新增埋点字段时，同时检查监控接口与后台展示是否兼容。
- 监控上报地址默认使用 `NUXT_PUBLIC_MONITOR_ENDPOINT`。

## 14. 测试与质量门禁

### 14.1 后端测试

```bash
cd backend
pytest tests/ -v
```

适用场景：

- 改 service、router、middleware、security、RAG 链路后必跑。

### 14.2 前端单测

```bash
cd frontend
npm run test
```

适用场景：

- 改 store、工具函数、组件交互逻辑后必跑。

### 14.3 前端类型检查

```bash
cd frontend
npm run typecheck
```

适用场景：

- 改接口类型、组合式函数、页面数据流后必跑。

### 14.4 E2E 测试

```bash
cd frontend
npx playwright test
```

说明：

- Playwright 会自行拉起前端开发服务。
- 后端服务、数据库和 Redis 仍需预先可用。
- 关键流程建议至少覆盖：首页、文章详情、后台登录、问答主链路。

### 14.5 提交前最小检查集

每次提交前至少完成：

1. 受影响模块测试通过。
2. 前端 `typecheck` 通过。
3. 核心页面或核心接口完成一次人工验证。
4. 环境变量、文档、迁移脚本同步完成。

## 15. Docker 开发与部署

### 15.1 当前服务

`docker-compose.yml` 当前编排 4 个服务：

- `db`
- `redis`
- `backend`
- `frontend`

### 15.2 常用命令

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose exec backend alembic upgrade head
docker compose down
```

### 15.3 发布前检查

- `JWT_SECRET_KEY` 已替换默认值。
- 前后端环境变量已切到目标环境。
- API 文档、首页、后台、问答页均可访问。
- 数据库迁移已执行。
- 如有 RAG 相关变更，向量数据已同步或重建。

## 16. 常见开发任务模板

### 16.1 新增文章字段

1. 改 `backend/app/models/article.py`
2. 改对应 `schemas/article.py`
3. 改 service 与 router
4. 生成并执行 Alembic 迁移
5. 改前端类型与编辑页 / 详情页 / 列表页
6. 跑后端测试、前端类型检查、关键页面验证

### 16.2 新增后台页面

1. 在 `frontend/pages/admin/` 新建页面
2. 接入鉴权逻辑和加载态
3. 复用 `components/admin/` 与 `components/common/`
4. 接入 `useApi.ts`
5. 补充测试与必要文档

### 16.3 新增公开接口

1. 新建 schema
2. 新建 service 逻辑
3. 在 `routers/public.py` 暴露路由
4. 联调前检查 `/docs`
5. 更新前端类型和页面调用

### 16.4 优化 RAG 检索效果

1. 明确要改的是清洗、切片、向量化还是召回逻辑
2. 先做离线验证，再做在线联调
3. 评估是否需要全量重建向量
4. 验证命中、无命中、边界问题与响应时延

## 17. 验收标准

一次完整开发完成后，至少满足以下条件：

- 能在本地按文档启动项目。
- 改动模块具备清晰代码落点，不破坏原有结构分层。
- 数据库变更有迁移脚本。
- 前后端契约没有明显脱节。
- RAG 变更有基本验证。
- 测试、类型检查或人工回归至少完成其中必要组合。
- 文档、环境变量和运行命令仍然准确。

## 18. 相关文档

开发过程中如需深入细节，配合下面文档使用：

- `docs/README.md`
- `docs/backend/API接口规范-V1.0.md`
- `docs/backend/数据库设计详细文档-V1.0.md`
- `docs/backend/后端开发规范-V1.0.md`
- `docs/backend/后端开发任务清单.md`
- `docs/frontend/前端设计规范-V1.0.md`
- `docs/frontend/前端组件规范-V1.0.md`
- `docs/frontend/前端开发任务清单.md`
- `docs/frontend/前端页面原型-V0.1.md`

## 19. 最终建议

如果你只是想高效推进开发，不需要反复读所有文档。你只要遵循下面这条主线即可：

1. 用本文启动环境并理解目录。
2. 先改数据和接口，再改页面和交互。
3. 每次只完成一条清晰主链路。
4. 改完先测，再联调，再补文档。
5. 涉及数据库、RAG、监控时，务必检查是否影响全链路。

这份文档的目标不是“解释项目有多厉害”，而是让你拿到仓库后可以直接开始开发，并且少走弯路。
