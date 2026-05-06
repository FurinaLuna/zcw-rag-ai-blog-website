# teammate.md

文档版本：V2.0  
更新日期：2026-05-06  
适用环境：Claude Code + DeepSeek 接入 + 多 Agent 协同开发  
适用仓库：`zcw-rag-ai-blog-website`  
文档定位：本文件是 Claude Code 多 Agent 协作的最高执行协议，优先级高于普通开发习惯。

---

## 1. 目标

本文件用于让 Claude Code 在接入 DeepSeek 后，以多 Agent 协作方式高效完成本仓库的前端、后端、数据库、AI/RAG、测试、运维、安全与文档工作。

目标不是“让所有 Agent 都会做所有事情”，而是：

- 明确分工，减少重复思考和重复读仓库。
- 明确交接，避免前后端、AI、数据库口径不一致。
- 明确协议，让任务可以被拆分、分发、恢复、回滚。
- 明确门禁，让合并、发布、验收可控。
- 明确模型路由，让 DeepSeek 在 Claude Code 中用在最适合的地方。

---

## 2. 总执行原则

所有 Agent 都必须遵守以下原则：

1. 单一职责：每个 Agent 只处理自己边界内的问题。
2. 先规划后动手：大于 30 分钟的任务必须先输出简要执行计划。
3. 契约优先：接口、Schema、数据结构变更先对齐，再动实现。
4. 上下文最小化：只读取当前任务真正需要的文件与片段。
5. 工件落盘：中间结论、评审结论、测试结果必须进入共享上下文目录。
6. 先测试再合并：没有质量门禁通过，任务不能进入合并阶段。
7. 可恢复：所有破坏性动作必须具备回滚路径。
8. 安全默认开启：敏感信息、密钥、认证、权限逻辑一律高优先级审查。

---

## 3. Claude Code + DeepSeek 运行模式

### 3.1 运行模式

默认采用以下拓扑：

- `orch`：总调度 Agent，唯一任务编排入口。
- `spec`：需求澄清 Agent，负责把自然语言目标转成可执行任务。
- `arch`：架构 Agent，负责系统边界、依赖、并发可行性判断。
- `fe`：前端 Agent。
- `be`：后端 API Agent。
- `db`：数据库 Agent。
- `ai`：AI/RAG Agent。
- `qa`：测试 Agent。
- `ops`：运维与部署 Agent。
- `sec`：安全 Agent。
- `doc`：文档 Agent。

### 3.2 DeepSeek 模型路由策略

如果 Claude Code 环境可选择不同 DeepSeek 能力，默认按以下规则路由：

| 场景 | 推荐模型 | 原因 |
|---|---|---|
| 需求拆解、复杂方案、冲突仲裁 | `deepseek-reasoner` | 推理更强，适合 DAG、边界分析、复杂排障 |
| 常规代码实现、文档写作、低风险改动 | `deepseek-chat` | 响应更快，成本更低，适合高吞吐执行 |
| RAG 检索策略、提示词优化、复杂缺陷定位 | `deepseek-reasoner` | 需要更强链路分析能力 |
| 大量样板代码、测试补齐、格式整理 | `deepseek-chat` | 适合快速生成与迭代 |
| 安全评审、迁移风险评估 | `deepseek-reasoner` | 风险判断更稳 |

若运行环境只有一个 DeepSeek 模型：

- 由 `orch` 控制上下文大小与任务粒度。
- 复杂任务必须拆成多个小任务，避免单次上下文过大。
- 所有 Specialist 输出都必须使用结构化结果，降低推理漂移。

### 3.3 高效执行规则

为了让 Claude Code + DeepSeek 运行更稳定，所有 Agent 必须遵守：

- 不一次性读取整个仓库，优先读目录、目标文件、关联配置。
- 单次任务上下文目标控制在 `6-12` 个文件以内。
- 单文件读取优先按片段读取，只有必要时再读全量。
- 所有交接结论先写摘要，再附工件路径。
- 输出先给结论，再给证据，避免长篇铺垫。
- 遇到跨前后端任务，必须先生成契约摘要，不允许直接各写各的。

### 3.4 上下文裁剪策略

每个 Agent 在执行前必须对上下文做分层处理：

1. `L1` 必读：当前任务直接相关文件。
2. `L2` 选读：配置、Schema、测试、调用方。
3. `L3` 参考：历史文档、补充材料、截图。
4. `L4` 禁止默认读取：无关模块、大量锁文件、无关产物目录。

推荐限制：

- `spec` / `arch`：最多 20 个文件。
- `fe` / `be` / `db` / `ai`：最多 12 个文件。
- `qa`：根据测试矩阵读取，不超过 15 个主要文件。
- `doc`：只读取已变更模块与入口文档。

---

## 4. Agent 分工

### 4.1 Agent 总表

| Agent ID | 名称 | 主要职责 | 不负责内容 | 主要输入 | 主要输出 |
|---|---|---|---|---|---|
| `orch` | Orchestrator Agent | 拆解、调度、锁管理、仲裁、放行 | 大规模直接编码 | 用户目标、上下文快照 | 任务图、调度决议、合并决议 |
| `spec` | Specification Agent | 需求澄清、验收条件、范围裁剪 | 实现代码 | 原始需求、历史约束 | 任务说明、验收条件 |
| `arch` | Architecture Agent | 架构影响、依赖分析、并发可行性 | 业务实现细节 | 需求、目录结构、约束 | 设计决议、拆分建议 |
| `fe` | Frontend Agent | Nuxt 页面、组件、状态、样式、类型消费 | 后端接口定义、迁移 | 页面需求、API 契约 | 前端补丁、前端测试 |
| `be` | Backend API Agent | FastAPI Router、Service、Schema、依赖、OpenAPI | 前端展示、数据库最终裁决 | 接口需求、设计决议 | 后端补丁、接口变更说明 |
| `db` | Database Agent | SQLAlchemy 模型、Alembic、索引、数据风险 | 页面与交互 | 模型需求、迁移请求 | 模型补丁、迁移脚本、回滚说明 |
| `ai` | AI/RAG Agent | 清洗、切片、向量化、检索、生成、评估 | 通用业务 CRUD | RAG 需求、检索问题、模型约束 | RAG 补丁、评估报告 |
| `qa` | QA Agent | 单测、集成测试、E2E、回归判断 | 主业务开发 | 候选补丁、测试命令 | 质量门禁、缺陷报告 |
| `ops` | DevOps Agent | Docker、环境变量、发布、性能、可观测性 | 业务规则设计 | 运行环境、部署需求 | 部署方案、性能报告 |
| `sec` | Security Agent | 权限、认证、密钥、脱敏、审计 | UI 与功能交互 | 候选补丁、敏感配置 | 安全审查、风险清单 |
| `doc` | Documentation Agent | README、开发文档、运行说明、发布说明 | 主业务编码 | 变更说明、测试结果 | 文档补丁、交付说明 |

### 4.2 前后端 AI 的协作边界

#### `fe` Frontend Agent

负责：

- `frontend/pages/`
- `frontend/components/`
- `frontend/composables/`
- `frontend/stores/`
- `frontend/styles/`
- `frontend/tests/`
- `frontend/e2e/` 中与页面行为强相关的部分

必须关注：

- 路由渲染模式是否匹配 `nuxt.config.ts`
- 类型消费是否与接口契约一致
- 加载态、空态、错误态、移动端状态是否完整

不得擅自做的事：

- 修改后端返回字段名
- 绕过 `useApi.ts` 新建散乱请求层
- 引入未评审的跨模块状态耦合

#### `be` Backend API Agent

负责：

- `backend/app/routers/`
- `backend/app/services/` 中非 RAG 业务
- `backend/app/schemas/`
- `backend/app/dependencies/`
- `backend/app/middleware/`
- `backend/tests/` 中 API 与业务测试

必须关注：

- OpenAPI 契约是否稳定
- 统一响应结构是否一致
- 后台接口的鉴权、限流、错误响应是否完整

不得擅自做的事：

- 绕过 `db` 直接做高风险数据结构变更
- 改动前端约定但不输出契约变化说明

#### `db` Database Agent

负责：

- `backend/app/models/`
- `backend/alembic/versions/`
- 与索引、迁移、数据兼容性有关的逻辑

必须关注：

- 迁移是否可执行、可回滚
- 历史数据兼容性
- 是否需要执行数据修复或向量重建

不得擅自做的事：

- 在没有迁移脚本的情况下要求直接改库
- 在未评估数据影响时修改核心表关系

#### `ai` AI/RAG Agent

负责：

- `backend/app/services/rag/`
- 与 RAG 质量、召回、生成、引用相关的接口协作
- RAG 评测、无命中策略、回答边界控制

必须关注：

- 相似度阈值、TopK、回答边界
- 生成答案与引用来源一致性
- 清洗、切片、向量化链路闭环

不得擅自做的事：

- 仅通过 prompt 掩盖检索质量问题
- 在未给出评估报告时切换 Embedding 模型或关键阈值

---

## 5. 任务输入输出协议

### 5.1 统一输入包

每个任务必须封装成标准输入包：

```json
{
  "task_id": "task_ai_001",
  "title": "优化问答结果的引用来源展示",
  "owner": "ai",
  "priority": "P1",
  "goal": "提升 RAG 回答可信度与来源可追溯性",
  "scope": [
    "backend/app/services/rag/",
    "backend/app/routers/rag.py"
  ],
  "constraints": [
    "不破坏现有 ask 接口兼容性",
    "必须补齐测试或评估报告"
  ],
  "dependencies": [
    "task_be_003"
  ],
  "acceptance": [
    "返回结构可包含来源摘要",
    "无命中场景保持兜底逻辑"
  ],
  "context_version": "ctx_v20260506_21"
}
```

### 5.2 统一输出包

每个 Agent 完成任务后必须输出：

```json
{
  "task_id": "task_ai_001",
  "agent": "ai",
  "status": "DONE",
  "risk_level": "medium",
  "completed": [
    "已调整检索结果拼装逻辑",
    "已补充评估脚本输出"
  ],
  "pending": [
    "等待 FE 接入来源渲染"
  ],
  "blockers": [],
  "artifacts": [
    ".claude/coordination/artifacts/task_ai_001/ai/rag_eval_20260506.json"
  ],
  "next_action": "交给 fe 对来源 UI 做消费",
  "handoff_to": "fe"
}
```

### 5.3 Claude Code 友好输出要求

为了让 Claude Code 与 DeepSeek 更高效协作，输出必须遵循：

- 先结论，后细节。
- 多用列表，少写长段落。
- 引用文件路径而不是大段重复代码。
- 交接只带必要上下文，不重复整份文档。
- 工件路径必须可直接定位。

---

## 6. 通信协议

### 6.1 消息类型

| 类型 | 用途 | 发送方 | 接收方 |
|---|---|---|---|
| `TASK_ASSIGN` | 下发任务 | `orch` | 任一 Agent |
| `TASK_ACCEPT` | 接受任务 | 任一 Agent | `orch` |
| `TASK_REJECT` | 拒绝任务 | 任一 Agent | `orch` |
| `TASK_PROGRESS` | 进度同步 | 任一 Agent | `orch` |
| `TASK_BLOCKED` | 阻塞上报 | 任一 Agent | `orch` |
| `HANDOFF_REQUEST` | 请求交接 | 任一 Agent | 下游 Agent |
| `HANDOFF_ACK` | 确认交接 | 下游 Agent | 上游 Agent |
| `REVIEW_REQUEST` | 发起评审 | 任一 Agent | `qa` / `sec` / `doc` |
| `REVIEW_RESULT` | 返回评审 | `qa` / `sec` / `doc` | `orch` |
| `MERGE_READY` | 允许进入合并 | `qa` / `sec` / `doc` | `orch` |
| `INCIDENT` | 上报异常事件 | 任一 Agent | `orch` |
| `ROLLBACK_REQUEST` | 请求回滚 | `qa` / `sec` / `ops` | `orch` |
| `ROLLBACK_DONE` | 回滚完成 | `orch` / `ops` | 相关 Agent |

### 6.2 状态码

| 状态码 | 含义 |
|---|---|
| `100` | CREATED |
| `101` | QUEUED |
| `102` | ASSIGNED |
| `103` | ACCEPTED |
| `200` | RUNNING |
| `201` | WAITING_DEPENDENCY |
| `202` | WAITING_REVIEW |
| `203` | WAITING_HANDOFF |
| `204` | RETRYING |
| `300` | DONE |
| `301` | PARTIAL_DONE |
| `400` | BLOCKED |
| `401` | INVALID_INPUT |
| `402` | LOCK_CONFLICT |
| `403` | SECURITY_DENIED |
| `404` | ARTIFACT_MISSING |
| `408` | TIMEOUT |
| `409` | MERGE_CONFLICT |
| `422` | CONTRACT_MISMATCH |
| `429` | RATE_LIMITED |
| `500` | INTERNAL_ERROR |
| `503` | AGENT_UNAVAILABLE |

### 6.3 错误处理

所有错误必须包含：

- `error_code`
- `summary`
- `recoverable`
- `retry_after_sec`
- `recommended_action`

错误示例：

```json
{
  "error_code": "CONTRACT_MISMATCH",
  "status_code": 422,
  "summary": "FE 消费字段 source_list，但 BE 当前返回 sources",
  "recoverable": true,
  "retry_after_sec": 0,
  "recommended_action": "先由 be 输出契约变更摘要，再由 fe 调整消费代码"
}
```

### 6.4 重试策略

统一重试规则：

- 第 1 次：30 秒后重试
- 第 2 次：2 分钟后重试
- 第 3 次：5 分钟后重试
- 第 4 次失败：自动转入失败转移或人工评审

特殊规则：

- `SECURITY_DENIED`：不允许自动重试
- `CONTRACT_MISMATCH`：最多 1 次自动重试
- `LOCK_CONFLICT`：最多 3 次重试
- `TIMEOUT`：必须附加阶段性快照

---

## 7. 共享上下文机制

### 7.1 目录规范

```text
.claude/
└── coordination/
    ├── context/
    │   ├── current.json
    │   ├── snapshots/
    │   └── versions/
    ├── tasks/
    │   ├── queue/
    │   ├── active/
    │   ├── blocked/
    │   ├── done/
    │   └── failed/
    ├── locks/
    ├── artifacts/
    ├── reviews/
    ├── incidents/
    └── audit/
```

### 7.2 状态存储要求

共享上下文必须至少存储：

- 当前任务队列
- 任务依赖图
- 文件锁状态
- 当前分支和基线提交
- 正在进行的评审
- 当前质量门禁状态
- 最近一次回滚点

### 7.3 上下文版本控制

每次发生以下事件时都必须提升 `context_version`：

- 任务新建或状态流转
- 文件锁变化
- 评审结果写入
- 合并决策写入
- 回滚执行

推荐命名：

- `ctx_vYYYYMMDD_seq`
- 示例：`ctx_v20260506_21`

### 7.4 并发锁

锁级别：

| 锁级别 | 说明 | 示例 |
|---|---|---|
| `FILE_LOCK` | 单文件写锁 | `frontend/pages/ask.vue` |
| `MODULE_LOCK` | 目录级写锁 | `backend/app/services/rag/` |
| `GLOBAL_LOCK` | 发布或回滚窗口锁 | `release-window` |

规则：

- 写入前必须申请锁。
- 同一路径同一时间只能有一个写锁。
- 锁必须带 TTL。
- 超时锁由 `orch` 回收。
- 破坏性数据变更默认要求 `MODULE_LOCK`。

### 7.5 回滚策略

回滚分三类：

1. 代码回滚：恢复到 `baseline_commit`
2. 数据回滚：执行对应回退迁移或数据修复脚本
3. 配置回滚：恢复环境变量模板与部署配置

必须触发回滚的场景：

- 主链路集成测试失败
- 迁移脚本造成数据风险
- 发布后出现 P0 / P1 回归
- 安全规则被突破

---

## 8. 任务拆分与调度

### 8.1 标准拆分原则

任务必须满足：

- 单任务目标清晰
- 可独立验证
- 可独立回滚
- 修改文件集尽量不重叠
- 默认在 90 分钟内能完成

### 8.2 推荐拆分模板

面向本仓库，推荐使用以下任务域：

- `spec-*`：需求澄清与验收条件
- `fe-*`：页面、组件、交互、状态
- `be-*`：接口、业务、鉴权、中间件
- `db-*`：模型、迁移、索引、数据兼容
- `ai-*`：RAG、Embedding、检索、生成、评估
- `qa-*`：单测、集测、E2E、冒烟
- `ops-*`：Compose、Docker、环境、部署、性能
- `doc-*`：README、开发文档、发布说明

### 8.3 优先级算法

```text
PriorityScore =
  0.35 * BusinessImpact +
  0.25 * DependencyCriticality +
  0.20 * RiskReduction +
  0.15 * Urgency +
  0.05 * ExecutionCostInverse
```

优先级区间：

- `P0`：>= 90
- `P1`：75 - 89
- `P2`：50 - 74
- `P3`：< 50

### 8.4 调度规则

`orch` 必须优先分发：

1. 阻塞其他任务的依赖任务
2. 风险高但修改范围小的基础修复
3. 当前合并窗口内必须完成的功能
4. 文档与非阻塞优化任务

### 8.5 负载均衡规则

默认并发上限：

- `fe` / `be` / `db` / `ai`：每个 Agent 最多 2 个活动任务
- `qa`：最多并行验证 4 个任务
- `doc`：最多并行 3 个文档同步任务
- `orch`：不直接承担业务实现任务

调度器必须考虑：

- 最近失败率
- 当前活动任务数
- 平均完成时长
- 文件集冲突概率
- 是否占用高价值锁

### 8.6 超时阈值

| 任务类型 | 默认超时 |
|---|---|
| 文档/配置微调 | 15 分钟 |
| 单模块功能改动 | 45 分钟 |
| 跨前后端联动 | 90 分钟 |
| 数据迁移 / RAG 链路改动 | 120 分钟 |
| 部署验证 | 60 分钟 |

### 8.7 失败转移

失败转移顺序：

1. 同角色备用 Agent
2. 邻接角色协助 Agent
3. `orch` 降级接管
4. 人工评审

示例：

- `be` 失败可转 `arch + be_backup`
- `ai` 失败可转 `arch + db + ai_backup`
- `fe` 失败可转 `fe_backup` 或 `orch` 收口小改动

---

## 9. Claude Code 高效执行模板

### 9.1 Agent 启动模板

每个 Agent 在开始工作时，先输出：

```md
角色：FE Agent
任务：task_fe_004
目标：为 ask 页面增加来源列表展示
锁范围：frontend/pages/ask.vue, frontend/components/rag/
依赖：task_be_003 已完成
计划：
1. 读取 ask 页面与 rag 组件
2. 对齐返回字段
3. 实现 UI 与空态
4. 补充测试
```

### 9.2 Agent 完成模板

```md
状态：DONE
已完成：
- 已在 ask 页面渲染来源列表
- 已补充空来源兜底
- 已补充前端测试
未完成：
- 无
阻塞项：
- 无
工件：
- .claude/coordination/artifacts/task_fe_004/fe/ui_test_20260506.md
建议下一步：
- 交由 qa 做回归验证
```

### 9.3 DeepSeek 任务提示词约束

为了提升稳定性，所有 Agent 的任务提示都应包含：

- 角色
- 任务目标
- 允许修改的路径
- 禁止修改的路径
- 验收条件
- 输出格式
- 需要落盘的工件

不应包含：

- 与当前任务无关的大段仓库背景
- 不可执行的泛泛建议
- 没有验收口径的开放式目标

### 9.4 Handoff 摘要规则

跨 Agent 交接摘要建议控制在以下范围：

- 目标：1 行
- 已完成：3 行内
- 风险：2 行内
- 工件路径：不超过 5 个
- 待读文件：不超过 8 个

原则：

- 交接是为了继续执行，不是重复聊天记录。
- 优先给“结论 + 文件 + 风险”。

---

## 10. 代码合并与冲突处理

### 10.1 分支命名规范

```text
<type>/<agent>/<task-id>/<short-slug>
```

示例：

- `feat/fe/task_fe_004/ask-source-list`
- `fix/be/task_be_003/rag-response-schema`
- `chore/doc/task_doc_002/update-teammate`
- `refactor/ai/task_ai_001/retriever-ranking`

### 10.2 自动合并条件

同时满足以下条件才允许自动合并：

1. 文件集无锁冲突
2. 单元测试通过
3. 集成测试主链路通过
4. 文档同步完成
5. 安全评审为 `pass` 或 `pass_with_notice`
6. 无破坏性迁移或已人工批准
7. 无公共接口破坏性变更或已完成下游适配

### 10.3 人工评审触发条件

以下任意一项成立必须人工评审：

- 修改认证、权限、JWT、密钥逻辑
- 修改 `docker-compose.yml`、部署脚本、环境变量结构
- 涉及 Alembic 迁移
- 涉及 OpenAPI 破坏性变更
- 涉及 Embedding 模型切换、RAG 核心阈值修改
- 单任务修改超过 20 个文件
- 任一 Agent 风险等级为 `high` 或 `critical`

### 10.4 冲突解决流程

1. `orch` 检测文件冲突
2. 判断是否可顺序重放补丁
3. 若是契约冲突，交由 `arch + fe + be` 仲裁
4. 若是数据冲突，交由 `db + be + qa` 仲裁
5. 若是 RAG 口径冲突，交由 `ai + be + fe` 仲裁
6. 冲突处理后重新跑最小测试集

---

## 11. 日志、监控与可观测性

### 11.1 日志等级

| 等级 | 用途 |
|---|---|
| `DEBUG` | 本地调试、锁细节、协议细节 |
| `INFO` | 任务流转、完成、交接、合并 |
| `WARN` | 重试、退化、非阻塞风险 |
| `ERROR` | 任务失败、评审失败、合并失败 |
| `FATAL` | 数据风险、安全突破、不可恢复事故 |

### 11.2 必填日志字段

每条日志必须包含：

- `timestamp`
- `agent_id`
- `task_id`
- `correlation_id`
- `event_type`
- `status_code`
- `duration_ms`
- `risk_level`
- `artifact_ref`

### 11.3 采样率

| 日志类型 | 采样率 |
|---|---|
| 状态流转日志 | 100% |
| 错误日志 | 100% |
| 锁申请与释放 | 100% |
| 常规心跳 | 20% |
| Debug 日志 | 10%，故障期可升到 100% |

### 11.4 指标维度

必须至少采集：

- Agent 成功率、失败率、平均耗时
- 任务超时率、重试率、失败转移率
- 锁冲突率、合并失败率、回滚率
- 单测通过率、集成测试通过率、E2E 通过率
- 健康检查耗时、公开接口 P95、RAG 响应 P95

### 11.5 告警阈值

| 指标 | 阈值 | 等级 |
|---|---|---|
| 单 Agent 连续失败 | >= 3 次 | High |
| 锁冲突率 | > 15% / 1h | Medium |
| 任务超时率 | > 10% / 4h | High |
| 自动合并失败率 | > 5% / 日 | Medium |
| 单元测试通过率 | < 95% | High |
| 主链路集成测试失败 | 任意 1 项 | Critical |
| RAG 平均响应时间 | > 5s | High |
| 回滚次数 | >= 2 / 日 | Critical |

---

## 12. 安全与权限控制

### 12.1 最小权限模型

| 权限级别 | 含义 |
|---|---|
| `READ_ONLY` | 仅读代码与上下文 |
| `WRITE_SCOPED` | 仅允许修改分配路径 |
| `MERGE_CONTROLLED` | 可进入合并流程，但不可绕过评审 |
| `ADMIN_ORCH` | 仅 `orch` 和人工维护者可持有 |

默认权限：

- `fe` / `be` / `db` / `ai` / `doc`：`WRITE_SCOPED`
- `qa`：`READ_ONLY + review access`
- `ops`：受限写权限
- `sec`：只读 + 审计 + 阻断权限

### 12.2 密钥与敏感信息

必须遵守：

- 所有密钥只允许存在于环境变量或密钥管理器中。
- 不允许在日志、对话、评审结论中输出完整密钥。
- `Authorization`、JWT、数据库密码必须脱敏。
- 生产密钥每 90 天轮换一次。

### 12.3 审计要求

以下行为必须写入审计日志：

- 任务分配
- 锁申请与释放
- 合并动作
- 权限升级
- 迁移执行
- 回滚执行
- 敏感配置读取
- 安全阻断

### 12.4 阻断规则

发现以下问题时必须阻断：

- 明文密钥
- 越权修改路径
- 审计链断裂
- 无迁移脚本的结构变更
- 无脱敏的敏感输出

---

## 13. 验收标准

### 13.1 基础门槛

所有交付物必须满足：

- 单元测试覆盖率 `>= 90%`
- 新增或修改的核心逻辑必须有测试
- 前端类型检查通过
- 主链路集成测试通过
- 文档同步完成
- 回滚路径存在且可执行

### 13.2 集成测试清单

至少覆盖：

1. 管理员登录成功与失败
2. 文章新增、编辑、删除
3. 分类 / 专题 / 标签联动
4. 评论提交与读取
5. RAG 命中路径
6. RAG 无命中兜底路径
7. 向量重建执行与校验
8. 监控日志上报与后台查询
9. Docker Compose 启动成功
10. 健康检查、OpenAPI、关键页面冒烟通过

### 13.3 性能基线

| 指标 | 基线 |
|---|---|
| 健康检查响应 | < 300ms |
| 公开内容接口 P95 | < 800ms |
| RAG 问答响应 P95 | < 5s |
| 关键页面首屏可用 | < 3s，本地开发基线 |
| Docker 全量启动到健康 | < 180s |
| 单模块测试时长 | < 120s |

### 13.4 文档完整性

交付时必须同步：

- 变更范围
- 启动命令
- 环境变量变化
- 接口变化
- 数据结构变化
- 回滚说明
- 测试结果

---

## 14. 标准工作流

### 14.1 正常路径

1. `orch` 接收需求
2. `spec` 产出验收标准与范围裁剪
3. `arch` 产出影响分析与并行方案
4. `orch` 拆分任务并分发到 `fe` / `be` / `db` / `ai`
5. Specialist Agent 申请锁并实施
6. `qa` / `sec` / `doc` 进行评审
7. `orch` 决定合并
8. `ops` 做部署验证
9. `qa` 做最终冒烟
10. 归档工件、日志、快照

### 14.2 前后端联动路径

适用于页面 + 接口联动：

1. `spec` 定义用户动作和验收结果
2. `arch` 产出契约变更范围
3. `be` 先输出接口摘要或 Schema 变更
4. `fe` 基于契约消费实现页面
5. `qa` 跑联动测试
6. `doc` 更新开发文档和接口说明

### 14.3 AI / RAG 联动路径

适用于问答、知识库、向量检索相关需求：

1. `spec` 定义命中效果、来源展示、兜底逻辑
2. `arch` 判断是否涉及模型、阈值、重建成本
3. `ai` 优化检索与生成逻辑
4. `db` 评估是否需要迁移或重建向量
5. `be` 保证接口兼容性
6. `fe` 消费新字段并展示来源与兜底
7. `qa` 跑命中、无命中、异常场景
8. `doc` 更新运行和维护说明

---

## 15. 最终执行约束

所有 Agent 必须遵守以下硬规则：

- 未拿到锁，不得写文件。
- 未拿到契约，不得实现跨模块功能。
- 未通过测试，不得进入合并。
- 未通过安全评审，不得发布。
- 未更新文档，不得视为完成。
- 未给回滚路径的破坏性变更，不得落地。

若任何行为与本文件冲突，按以下优先级裁定：

1. 安全规则
2. 数据一致性规则
3. 回滚规则
4. 协议与上下文规则
5. 性能与效率规则

本文件的目标只有一个：让 Claude Code 在接入 DeepSeek 后，能够把本仓库的前端、后端、数据库、AI 与测试协作做快、做稳、做可控。
