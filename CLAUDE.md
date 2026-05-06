# CLAUDE.md

文档版本：V2.0
更新日期：2026-05-06
适用环境：Claude Code + DeepSeek 接入 + 多 Agent 协同开发
适用仓库：zcw-rag-ai-blog-website

---

## 1. 概述

本文档定义 Claude Code 如何根据 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 中指定的 Agent 配置信息，实现多 Agent 的**动态加载、参数传递、任务分配、执行监控和结果整合**的完整流程。

### 1.1 核心流程

```
用户目标
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  CLAUDE.md 引导层                                             │
│  1. 读取 teammate.md 获取 Agent 配置                          │
│  2. 加载 coordination/context/current.json 获取系统状态       │
│  3. 根据任务模板创建任务                                       │
│  4. 按协议调度 Agent                                          │
│  5. 监控执行并整合结果                                        │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  teammate.md 配置层                                          │
│  - Agent 分工定义                                            │
│  - 通信协议                                                  │
│  - 任务输入输出协议                                          │
│  - 共享上下文机制                                            │
│  - 调度与负载均衡规则                                        │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  .claude/coordination/ 运行时层                               │
│  - context/current.json 系统状态                             │
│  - tasks/ 任务队列与状态                                     │
│  - locks/ 文件锁                                             │
│  - artifacts/ 工件存储                                       │
│  - reviews/ 评审记录                                         │
│  - incidents/ 异常事件                                       │
│  - audit/ 审计日志                                           │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 文件依赖关系

| 文件 | 作用 | 被谁读取 |
|---|---|---|
| [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) | Agent 配置、协议、分工定义 | CLAUDE.md 引导层、所有 Agent |
| [current.json](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/context/current.json) | 系统当前状态、资源分配、任务上下文 | orch Agent、调度逻辑 |
| [task_template.json](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/tasks/task_template.json) | 通用任务模板 | 所有 Agent |
| [task_template_*.json](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/tasks/) | 领域专用任务模板 | 对应 Agent |

---

## 2. Agent 动态加载机制

### 2.1 Agent 注册与发现

Claude Code 从 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 4 节读取 Agent 配置表，动态注册可用 Agent。每个 Agent 包含以下属性：

| 属性 | 来源 | 说明 |
|---|---|---|
| `agent_id` | teammate.md 4.1 | Agent 唯一标识，如 `fe`, `be`, `ai` |
| `name` | teammate.md 4.1 | Agent 名称 |
| `responsibilities` | teammate.md 4.1 | 主要职责描述 |
| `boundaries` | teammate.md 4.1 | 不负责内容 |
| `allowed_paths` | teammate.md 4.2 | 允许操作的路径范围 |
| `max_concurrent` | teammate.md 8.5 | 最大并发任务数 |
| `default_timeout` | teammate.md 8.6 | 默认超时阈值 |
| `fallback_order` | teammate.md 8.7 | 失败转移顺序 |

### 2.2 动态加载流程

```
步骤 1: 读取 teammate.md
    │
    ▼
步骤 2: 解析 Agent 配置表（第 4.1 节）
    │
    ▼
步骤 3: 读取 current.json 获取 Agent 当前状态
    │
    ▼
步骤 4: 检查 Agent 可用性（状态 != UNAVAILABLE）
    │
    ▼
步骤 5: 检查并发限制（active_tasks < max_concurrent）
    │
    ▼
步骤 6: 注册 Agent 到调度池
```

### 2.3 加载示例

当 Claude Code 收到一个前端页面开发需求时，加载流程如下：

```
1. 读取 teammate.md → 发现 fe Agent 配置
2. 读取 current.json → fe 状态 AVAILABLE, active_tasks: []
3. 检查并发限制 → 0 < 2, 允许分配
4. 加载 task_template_fe.json 作为任务模板
5. 创建任务并分配给 fe Agent
```

---

## 3. 参数传递机制

### 3.1 统一输入包格式

所有 Agent 任务使用标准输入包，定义见 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 5.1 节：

```json
{
  "task_id": "task_fe_001",
  "title": "实现文章详情页来源展示",
  "owner": "fe",
  "priority": "P1",
  "goal": "在文章详情页展示 RAG 引用来源列表",
  "scope": [
    "frontend/pages/articles/[slug].vue",
    "frontend/components/article/"
  ],
  "constraints": [
    "不破坏现有文章详情页布局",
    "必须处理空来源场景"
  ],
  "dependencies": [
    "task_be_003"
  ],
  "acceptance": [
    "来源列表在文章详情页正确渲染",
    "无来源时显示兜底文案",
    "移动端适配正常"
  ],
  "context_version": "ctx_v20260506_01"
}
```

### 3.2 参数传递规则

| 参数 | 传递方式 | 说明 |
|---|---|---|
| `task_id` | 直接赋值 | 由 orch 按 `task_{domain}_{seq}` 格式生成 |
| `goal` | 从需求解析 | 由 spec 或 orch 从用户目标提取 |
| `scope` | 路径限定 | 必须与 Agent 的 allowed_paths 交集非空 |
| `constraints` | 继承+追加 | 继承 teammate.md 中的全局约束，追加任务特定约束 |
| `dependencies` | DAG 分析 | 由 orch 根据任务依赖图计算 |
| `acceptance` | 从验收条件映射 | 由 spec 从需求验收条件映射 |
| `context_version` | 从 current.json 读取 | 每次任务创建时锁定当前上下文版本 |
| `extra` | 领域扩展 | 各 Agent 模板定义的扩展参数 |

### 3.3 领域特定参数

各 Agent 模板定义了自己的扩展参数，通过 `extra` 字段传递：

| Agent | 扩展参数 | 说明 |
|---|---|---|
| spec | `raw_requirement`, `historical_constraints` | 原始需求和历史约束 |
| fe | `api_contract`, `design_reference` | API 契约和设计参考 |
| be | `data_contract`, `auth_required` | 数据契约和鉴权要求 |
| db | `migration_type`, `backward_compatible` | 迁移类型和向后兼容性 |
| ai | `model_config`, `evaluation_criteria` | 模型配置和评估标准 |
| qa | `test_scope`, `test_matrix` | 测试范围和矩阵 |
| ops | `environment_changes`, `performance_targets` | 环境变更和性能目标 |
| doc | `change_summary`, `target_docs` | 变更摘要和目标文档 |

### 3.4 参数验证

参数传递时执行以下验证：

1. **必填字段检查**：`task_id`, `goal`, `scope`, `acceptance` 必须存在
2. **路径合法性检查**：`scope` 中的路径必须在 Agent 的 `allowed_paths` 范围内
3. **依赖完整性检查**：`dependencies` 中引用的任务必须已存在
4. **上下文版本检查**：`context_version` 必须与 current.json 中的版本一致

---

## 4. 任务分配机制

### 4.1 任务分配流程

```
用户目标输入
    │
    ▼
spec Agent: 需求澄清与任务拆分
    │
    ▼
arch Agent: 架构影响评估与依赖分析
    │
    ▼
orch Agent: 任务调度决策
    │
    ├── 优先级计算 (teammate.md 8.3)
    ├── 依赖顺序排序 (teammate.md 8.4)
    ├── 负载均衡检查 (teammate.md 8.5)
    └── 锁冲突检测 (teammate.md 7.4)
    │
    ▼
写入任务到 tasks/queue/
    │
    ▼
更新 current.json 中的 task_queue
    │
    ▼
发送 TASK_ASSIGN 消息给目标 Agent
```

### 4.2 优先级计算

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 8.3 节的算法计算：

```
PriorityScore =
  0.35 * BusinessImpact +
  0.25 * DependencyCriticality +
  0.20 * RiskReduction +
  0.15 * Urgency +
  0.05 * ExecutionCostInverse
```

优先级映射：
- `P0`：>= 90 — 立即执行
- `P1`：75 - 89 — 当前轮次执行
- `P2`：50 - 74 — 排入队列
- `P3`：< 50 — 待资源空闲时执行

### 4.3 调度规则

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 8.4 节，orch 按以下优先级分发任务：

1. **阻塞依赖任务**：被最多任务依赖的优先
2. **高风险小改动**：风险高但修改范围小的基础修复
3. **合并窗口任务**：当前合并窗口内必须完成的功能
4. **文档与优化**：非阻塞优化任务最后分配

### 4.4 负载均衡

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 8.5 节，调度器考虑以下因素：

- 每个 Agent 的 `active_tasks` 数量不超过 `max_concurrent`
- 最近失败率（`recent_failure_rate`）高的 Agent 减少分配
- 平均完成时长（`avg_completion_minutes`）长的任务避开高负载 Agent
- 文件集冲突概率高的任务错开分配

### 4.5 分配示例

```json
// orch 的调度决策示例
{
  "decision_id": "sched_20260506_001",
  "timestamp": "2026-05-06T21:30:00+08:00",
  "pending_tasks": [
    {"task_id": "task_be_003", "priority": "P1", "owner": "be", "dependencies": []},
    {"task_id": "task_fe_001", "priority": "P1", "owner": "fe", "dependencies": ["task_be_003"]},
    {"task_id": "task_ai_002", "priority": "P2", "owner": "ai", "dependencies": []}
  ],
  "assignments": [
    {
      "task_id": "task_be_003",
      "assigned_to": "be",
      "reason": "P1 优先级，无前置依赖，可立即执行"
    },
    {
      "task_id": "task_ai_002",
      "assigned_to": "ai",
      "reason": "P2 优先级，与 task_be_003 无文件冲突，可并行"
    }
  ],
  "deferred": [
    {
      "task_id": "task_fe_001",
      "reason": "依赖 task_be_003 未完成，等待依赖就绪"
    }
  ]
}
```

---

## 5. 执行监控机制

### 5.1 状态跟踪

任务状态定义见 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 6.2 节。状态流转如下：

```
CREATED → QUEUED → ASSIGNED → ACCEPTED → RUNNING → DONE
                                        → WAITING_DEPENDENCY
                                        → WAITING_REVIEW
                                        → WAITING_HANDOFF
                                        → RETRYING
                                        → BLOCKED
                                        → TIMEOUT
```

### 5.2 状态同步机制

Agent 在执行过程中通过以下方式同步状态：

| 事件 | 触发时机 | 更新内容 |
|---|---|---|
| `TASK_ACCEPT` | Agent 接受任务 | 任务移至 `tasks/active/`，更新 Agent `active_tasks` |
| `TASK_PROGRESS` | 执行中定期同步 | 更新任务状态和进度信息 |
| `TASK_BLOCKED` | 遇到阻塞 | 任务移至 `tasks/blocked/`，记录阻塞原因 |
| `TASK_COMPLETE` | 任务完成 | 任务移至 `tasks/done/`，释放锁，更新 Agent 统计 |
| `TASK_FAILED` | 任务失败 | 任务移至 `tasks/failed/`，触发重试或失败转移 |

### 5.3 超时监控

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 8.6 节的超时阈值执行监控：

| 任务类型 | 默认超时 | 监控频率 |
|---|---|---|
| 文档/配置微调 | 15 分钟 | 每 3 分钟检查 |
| 单模块功能改动 | 45 分钟 | 每 5 分钟检查 |
| 跨前后端联动 | 90 分钟 | 每 10 分钟检查 |
| 数据迁移 / RAG 链路改动 | 120 分钟 | 每 15 分钟检查 |
| 部署验证 | 60 分钟 | 每 10 分钟检查 |

超时处理流程：

```
超时触发
    │
    ▼
检查是否有阶段性快照
    │
    ├── 有 → 保存快照，触发 RETRYING
    │
    └── 无 → 标记 TIMEOUT，触发失败转移
```

### 5.4 锁监控

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 7.4 节的锁机制执行监控：

| 锁级别 | 监控内容 | 超时回收 |
|---|---|---|
| `FILE_LOCK` | 单文件写锁，TTL 30 分钟 | 超时由 orch 回收 |
| `MODULE_LOCK` | 目录级写锁，TTL 60 分钟 | 超时由 orch 回收 |
| `GLOBAL_LOCK` | 发布窗口锁，TTL 120 分钟 | 超时由 orch 回收 |

锁状态记录在 [locks/](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/locks/) 目录中：

```json
// .claude/coordination/locks/current.json 示例
{
  "locks": [
    {
      "lock_id": "lock_fe_001",
      "level": "FILE_LOCK",
      "path": "frontend/pages/ask.vue",
      "holder": "fe",
      "task_id": "task_fe_001",
      "acquired_at": "2026-05-06T21:30:00+08:00",
      "ttl_sec": 1800,
      "status": "ACTIVE"
    }
  ]
}
```

### 5.5 监控指标

orch 持续跟踪以下指标用于调度决策：

| 指标 | 来源 | 用途 |
|---|---|---|
| `active_tasks` | current.json | 并发控制 |
| `recent_failure_rate` | current.json | 负载均衡 |
| `avg_completion_minutes` | current.json | 任务时长预估 |
| `lock_conflict_count` | locks/ | 冲突检测 |
| `queue_depth` | tasks/queue/ | 队列积压监控 |
| `blocked_count` | tasks/blocked/ | 阻塞率监控 |

---

## 6. 结果整合机制

### 6.1 统一输出包

每个 Agent 完成任务后输出标准结果包，定义见 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 5.2 节：

```json
{
  "task_id": "task_fe_001",
  "agent": "fe",
  "status": "DONE",
  "risk_level": "low",
  "completed": [
    "已在文章详情页渲染来源列表",
    "已补充空来源兜底文案",
    "已补充前端组件测试"
  ],
  "pending": [],
  "blockers": [],
  "artifacts": [
    ".claude/coordination/artifacts/task_fe_001/fe/ui_test_20260506.md"
  ],
  "next_action": "交由 qa 做回归验证",
  "handoff_to": "qa"
}
```

### 6.2 结果整合流程

```
各 Agent 输出结果包
    │
    ▼
orch 收集所有结果
    │
    ├── 检查 status 是否为 DONE
    ├── 检查 risk_level 是否可接受
    ├── 检查 artifacts 是否完整
    └── 检查 handoff_to 链是否闭合
    │
    ▼
触发质量门禁
    │
    ├── qa: 回归测试验证
    ├── sec: 安全审查
    └── doc: 文档同步
    │
    ▼
结果汇总报告
    │
    ▼
更新 current.json
    │
    ├── 更新 task_execution_context
    ├── 更新 resource_allocation
    ├── 更新 audit_trail
    └── 提升 context_version
```

### 6.3 工件落盘

所有 Agent 的输出工件必须写入 [artifacts/](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/artifacts/) 目录，路径规范：

```
.claude/coordination/artifacts/
└── {task_id}/
    └── {agent_id}/
        ├── {artifact_type}_{date}.json
        ├── {artifact_type}_{date}.md
        └── ...
```

工件类型包括：

| 类型 | 说明 | 示例 |
|---|---|---|
| `test_report` | 测试报告 | `test_report_20260506.json` |
| `eval_report` | 评估报告 | `rag_eval_20260506.json` |
| `contract_diff` | 契约变更 | `api_contract_diff_20260506.md` |
| `migration_script` | 迁移脚本 | `migration_v2_20260506.py` |
| `performance_report` | 性能报告 | `perf_report_20260506.json` |
| `security_review` | 安全审查 | `security_review_20260506.md` |

### 6.4 结果整合示例

```json
// orch 的结果整合报告示例
{
  "integration_id": "int_20260506_001",
  "timestamp": "2026-05-06T22:00:00+08:00",
  "context_version": "ctx_v20260506_02",
  "tasks": [
    {
      "task_id": "task_be_003",
      "agent": "be",
      "status": "DONE",
      "risk_level": "low",
      "artifacts": [".claude/coordination/artifacts/task_be_003/be/contract_diff.md"]
    },
    {
      "task_id": "task_fe_001",
      "agent": "fe",
      "status": "DONE",
      "risk_level": "low",
      "artifacts": [".claude/coordination/artifacts/task_fe_001/fe/ui_test.md"]
    }
  ],
  "quality_gates": {
    "unit_tests": "PASSED",
    "integration_tests": "PASSED",
    "e2e_tests": "PASSED",
    "security_review": "PASSED"
  },
  "summary": "文章详情页来源展示功能已完成开发、测试和安全审查",
  "next_action": "准备合并到主分支"
}
```

---

## 7. 接口说明

### 7.1 Claude Code 调用接口

Claude Code 通过以下接口与多 Agent 系统交互：

#### 7.1.1 任务提交接口

```
提交方式：自然语言描述目标
处理流程：
  1. Claude Code 读取 CLAUDE.md 获取引导
  2. 读取 teammate.md 获取 Agent 配置
  3. 调用 spec Agent 进行需求澄清
  4. 调用 arch Agent 进行架构评估
  5. orch Agent 进行任务分配
  6. 各 Agent 执行任务
  7. 结果整合与输出
```

#### 7.1.2 状态查询接口

```
查询方式：读取 current.json
  - system_state: 系统整体状态
  - resource_allocation.agents: 各 Agent 状态
  - task_execution_context: 任务队列和执行状态

查询方式：读取 tasks/ 目录
  - tasks/queue/: 排队中的任务
  - tasks/active/: 执行中的任务
  - tasks/blocked/: 阻塞的任务
  - tasks/done/: 已完成的任务
  - tasks/failed/: 失败的任务
```

#### 7.1.3 结果查询接口

```
查询方式：读取 artifacts/ 目录
  - 按 task_id 查找对应工件
  - 按 agent_id 查找对应 Agent 的输出

查询方式：读取 reviews/ 目录
  - 评审记录和结果

查询方式：读取 audit/ 目录
  - 审计日志和操作记录
```

### 7.2 Agent 间通信接口

Agent 间通过消息协议通信，消息类型定义见 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 6.1 节。

#### 7.2.1 消息格式

```json
{
  "message_type": "TASK_ASSIGN",
  "sender": "orch",
  "receiver": "fe",
  "timestamp": "2026-05-06T21:30:00+08:00",
  "payload": {
    "task_id": "task_fe_001",
    "goal": "实现文章详情页来源展示",
    "scope": ["frontend/pages/articles/[slug].vue"],
    "acceptance": ["来源列表正确渲染", "空来源兜底"]
  },
  "context_version": "ctx_v20260506_01"
}
```

#### 7.2.2 消息路由

消息通过以下路径路由：

```
orch → Agent: TASK_ASSIGN, REVIEW_REQUEST
Agent → orch: TASK_ACCEPT, TASK_REJECT, TASK_PROGRESS, TASK_BLOCKED, INCIDENT
Agent → Agent: HANDOFF_REQUEST, HANDOFF_ACK
Agent → qa/sec/doc: REVIEW_REQUEST
qa/sec/doc → orch: REVIEW_RESULT, MERGE_READY
```

### 7.3 上下文管理接口

#### 7.3.1 上下文快照

```json
// 创建上下文快照
{
  "action": "snapshot_create",
  "context_version": "ctx_v20260506_02",
  "snapshot_path": ".claude/coordination/context/snapshots/ctx_v20260506_02.json",
  "includes": [
    "current.json",
    "tasks/active/*.json",
    "tasks/blocked/*.json",
    "locks/current.json"
  ]
}
```

#### 7.3.2 上下文版本提升

每次以下事件发生时提升 `context_version`：

- 任务新建或状态流转
- 文件锁变化
- 评审结果写入
- 合并决策写入
- 回滚执行

版本命名格式：`ctx_v{YYYYMMDD}_{seq}`

---

## 8. 异常处理指南

### 8.1 异常分类

| 类别 | 错误码 | 可恢复 | 处理方式 |
|---|---|---|---|
| 输入异常 | `INVALID_INPUT` | 是 | 修正输入后重试 |
| 锁冲突 | `LOCK_CONFLICT` | 是 | 等待锁释放后重试（最多 3 次） |
| 安全拒绝 | `SECURITY_DENIED` | 否 | 立即上报 orch，触发安全评审 |
| 契约不匹配 | `CONTRACT_MISMATCH` | 是 | 输出契约变更摘要后重试（最多 1 次） |
| 超时 | `TIMEOUT` | 是 | 附加阶段性快照后重试 |
| 合并冲突 | `MERGE_CONFLICT` | 是 | 解决冲突后重试 |
| 限流 | `RATE_LIMITED` | 是 | 等待后重试 |
| 内部错误 | `INTERNAL_ERROR` | 否 | 触发失败转移 |
| Agent 不可用 | `AGENT_UNAVAILABLE` | 是 | 等待或触发失败转移 |
| 工件缺失 | `ARTIFACT_MISSING` | 是 | 重新生成工件 |

### 8.2 重试策略

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 6.4 节的统一重试规则：

```
第 1 次失败 → 等待 30 秒后重试
第 2 次失败 → 等待 2 分钟后重试
第 3 次失败 → 等待 5 分钟后重试
第 4 次失败 → 转入失败转移或人工评审
```

特殊规则：
- `SECURITY_DENIED`：不允许自动重试
- `CONTRACT_MISMATCH`：最多 1 次自动重试
- `LOCK_CONFLICT`：最多 3 次重试
- `TIMEOUT`：必须附加阶段性快照

### 8.3 失败转移

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 8.7 节的失败转移顺序：

```
同角色备用 Agent → 邻接角色协助 Agent → orch 降级接管 → 人工评审
```

各 Agent 的失败转移路径：

| Agent | 第一顺位 | 第二顺位 | 第三顺位 |
|---|---|---|---|
| fe | fe_backup | orch | 人工评审 |
| be | arch + be_backup | orch | 人工评审 |
| db | db_backup | arch | 人工评审 |
| ai | arch + db + ai_backup | orch | 人工评审 |
| qa | qa_backup | orch | 人工评审 |
| ops | ops_backup | arch | 人工评审 |
| doc | doc_backup | orch | 人工评审 |

### 8.4 回滚流程

按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 7.5 节的回滚策略：

```
回滚请求触发
    │
    ▼
判断回滚类型
    │
    ├── 代码回滚 → 恢复到 baseline_commit
    ├── 数据回滚 → 执行回退迁移或数据修复脚本
    └── 配置回滚 → 恢复环境变量模板与部署配置
    │
    ▼
执行回滚
    │
    ▼
验证回滚结果
    │
    ▼
更新 current.json
    ├── 更新 last_rollback_point
    ├── 更新 system_state
    └── 提升 context_version
```

必须触发回滚的场景：
- 主链路集成测试失败
- 迁移脚本造成数据风险
- 发布后出现 P0 / P1 回归
- 安全规则被突破

### 8.5 异常处理示例

```json
// 锁冲突异常处理示例
{
  "error_code": "LOCK_CONFLICT",
  "status_code": 402,
  "summary": "fe 尝试获取 frontend/pages/ask.vue 的 FILE_LOCK，但该锁当前被 fe_backup 持有",
  "recoverable": true,
  "retry_after_sec": 120,
  "recommended_action": "等待 fe_backup 释放锁后重试，或请求 orch 介入回收超时锁",
  "retry_count": 1,
  "max_retries": 3
}
```

```json
// 契约不匹配异常处理示例
{
  "error_code": "CONTRACT_MISMATCH",
  "status_code": 422,
  "summary": "fe 消费字段 source_list，但 be 当前返回 sources",
  "recoverable": true,
  "retry_after_sec": 0,
  "recommended_action": "先由 be 输出契约变更摘要，再由 fe 调整消费代码",
  "retry_count": 0,
  "max_retries": 1
}
```

---

## 9. 调用示例

### 9.1 完整调用流程示例

**场景**：用户要求"优化 RAG 问答结果的引用来源展示"

```
步骤 1: Claude Code 读取 CLAUDE.md 获取引导
步骤 2: 读取 teammate.md 获取 Agent 配置
步骤 3: 读取 current.json 获取系统状态
         → 系统 IDLE，所有 Agent AVAILABLE
步骤 4: 调用 spec Agent 进行需求澄清
         → 输出: 3 个需求条目，2 个可执行任务
步骤 5: 调用 arch Agent 进行架构评估
         → 输出: 无架构冲突，建议 fe + be 协作
步骤 6: orch 创建任务并分配
         → task_be_003: 调整检索结果拼装逻辑 (be)
         → task_fe_001: 实现来源列表 UI 展示 (fe)
         → task_ai_002: 优化引用来源一致性 (ai)
步骤 7: 更新 current.json，提升 context_version
步骤 8: be Agent 执行 task_be_003
         → 输出: DONE, 工件: contract_diff.md
步骤 9: ai Agent 执行 task_ai_002
         → 输出: DONE, 工件: rag_eval_report.md
步骤 10: fe Agent 执行 task_fe_001 (依赖 task_be_003 完成)
          → 输出: DONE, 工件: ui_test_report.md
步骤 11: qa Agent 执行回归验证
          → 输出: PASSED, 无回归
步骤 12: orch 整合结果
          → 输出: 整合报告，准备合并
```

### 9.2 Agent 启动模板

每个 Agent 开始工作时，按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 9.1 节输出启动声明：

```markdown
角色：FE Agent
任务：task_fe_001
目标：为文章详情页增加来源列表展示
锁范围：frontend/pages/articles/[slug].vue, frontend/components/article/
依赖：task_be_003 已完成
计划：
1. 读取文章详情页与相关组件
2. 对齐返回字段（sources）
3. 实现来源列表 UI 与空态
4. 补充前端测试
```

### 9.3 Agent 完成模板

Agent 完成任务后，按 [teammate.md](file:///d:/项目/zcw-rag-ai-blog-website/teammate.md) 第 9.2 节输出完成声明：

```markdown
状态：DONE
已完成：
- 已在文章详情页渲染来源列表
- 已补充空来源兜底文案
- 已补充前端组件测试
未完成：
- 无
阻塞项：
- 无
工件：
- .claude/coordination/artifacts/task_fe_001/fe/ui_test_20260506.md
建议下一步：
- 交由 qa 做回归验证
```

### 9.4 上下文更新示例

任务完成后更新 [current.json](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/context/current.json)：

```json
{
  "context_version": "ctx_v20260506_02",
  "updated_at": "2026-05-06T22:00:00+08:00",
  "system_state": {
    "status": "IDLE",
    "quality_gates": {
      "unit_tests": "PASSED",
      "integration_tests": "PASSED",
      "e2e_tests": "PASSED",
      "security_review": "PASSED",
      "lint_check": "PASSED"
    }
  },
  "resource_allocation": {
    "agents": {
      "fe": { "status": "AVAILABLE", "active_tasks": [], "recent_failure_rate": 0.0 },
      "be": { "status": "AVAILABLE", "active_tasks": [], "recent_failure_rate": 0.0 },
      "ai": { "status": "AVAILABLE", "active_tasks": [], "recent_failure_rate": 0.0 }
    }
  },
  "task_execution_context": {
    "recently_completed": [
      { "task_id": "task_be_003", "status": "DONE", "completed_at": "2026-05-06T21:50:00+08:00" },
      { "task_id": "task_ai_002", "status": "DONE", "completed_at": "2026-05-06T21:55:00+08:00" },
      { "task_id": "task_fe_001", "status": "DONE", "completed_at": "2026-05-06T22:00:00+08:00" }
    ]
  },
  "audit_trail": [
    { "timestamp": "2026-05-06T21:26:00+08:00", "event": "CONTEXT_INITIALIZED", "actor": "orch" },
    { "timestamp": "2026-05-06T22:00:00+08:00", "event": "TASK_BATCH_COMPLETED", "actor": "orch",
      "summary": "RAG 引用来源展示功能的三项任务全部完成" }
  ]
}
```

---

## 10. 目录结构参考

```
.claude/
├── settings.json                    # Claude Code 权限配置
├── settings.local.json              # 本地权限覆盖
└── coordination/
    ├── context/
    │   ├── current.json             # 系统当前状态（本文档管理）
    │   ├── snapshots/               # 上下文快照
    │   └── versions/                # 上下文版本历史
    ├── tasks/
    │   ├── task_template.json       # 通用任务模板
    │   ├── task_template_spec.json  # 需求澄清模板
    │   ├── task_template_fe.json    # 前端模板
    │   ├── task_template_be.json    # 后端模板
    │   ├── task_template_db.json    # 数据库模板
    │   ├── task_template_ai.json    # AI/RAG 模板
    │   ├── task_template_qa.json    # 测试模板
    │   ├── task_template_ops.json   # 运维模板
    │   ├── task_template_doc.json   # 文档模板
    │   ├── queue/                   # 排队中的任务
    │   ├── active/                  # 执行中的任务
    │   ├── blocked/                 # 阻塞的任务
    │   ├── done/                    # 已完成的任务
    │   └── failed/                  # 失败的任务
    ├── locks/                       # 文件锁状态
    ├── artifacts/                   # 任务输出工件
    ├── reviews/                     # 评审记录
    ├── incidents/                   # 异常事件记录
    └── audit/                       # 审计日志
```

---

## 11. 自动化调度引擎

为实现"持续自动完成任务"，提供了 [scheduler.py](file:///d:/项目/zcw-rag-ai-blog-website/.claude/coordination/scheduler.py) 自动化调度脚本，作为 orch Agent 的自动化执行引擎。

### 11.1 初始化

首次使用前运行初始化脚本：

```bash
python .claude/coordination/init.py
```

这将创建完整的 coordination 目录结构和初始上下文状态。

### 11.2 调度器命令

```bash
# 创建任务（从 JSON 文件）
python .claude/coordination/scheduler.py task-create -f task_def.json

# 列出各状态任务
python .claude/coordination/scheduler.py task-list queue
python .claude/coordination/scheduler.py task-list active
python .claude/coordination/scheduler.py task-list blocked
python .claude/coordination/scheduler.py task-list done

# 移动任务状态
python .claude/coordination/scheduler.py task-move task_fe_001 done

# 自动调度就绪任务（按优先级和负载均衡）
python .claude/coordination/scheduler.py dispatch --max 4

# 锁管理
python .claude/coordination/scheduler.py lock-acquire lock_fe_001 \
    --path frontend/pages/ask.vue --holder fe --task-id task_fe_001
python .claude/coordination/scheduler.py lock-release lock_fe_001 --holder fe
python .claude/coordination/scheduler.py lock-cleanup

# 查看上下文
python .claude/coordination/scheduler.py context-show
python .claude/coordination/scheduler.py context-show --section agents
python .claude/coordination/scheduler.py context-show --section tasks
python .claude/coordination/scheduler.py context-show --section audit

# 添加审计日志
python .claude/coordination/scheduler.py audit \
    --event TASK_COMPLETED --actor fe --summary "task_fe_001 已完成"
```

### 11.3 持续运行模式

结合调度器和 CLAUDE.md 引导，实现持续任务处理：

```
1. 用户提出目标
2. Claude Code 读取 CLAUDE.md 获取引导
3. 使用 task-create 创建任务到 queue/
4. 使用 dispatch 自动调度就绪任务到 active/
5. Agent 执行任务并更新状态
6. 使用 task-move 将完成的任务移至 done/
7. 调度器自动检查依赖就绪的下一个任务
8. 循环直到所有任务完成
```

## 12. 快速参考

### 12.1 启动新任务

```
1. 确认 teammate.md 中的 Agent 配置
2. 检查 current.json 中的系统状态
3. 选择对应的 task_template_*.json
4. 填写输入参数
5. 写入 tasks/queue/（或使用 scheduler.py task-create）
6. 更新 current.json
```

### 12.2 检查任务状态

```
1. 读取 current.json 中的 task_execution_context
2. 检查 tasks/active/ 中的执行中任务
3. 检查 tasks/blocked/ 中的阻塞任务
4. 检查 tasks/done/ 和 tasks/failed/ 中的已完成任务
5. 或使用 scheduler.py task-list 快速查看
```

### 12.3 处理异常

```
1. 确定错误码和异常类型
2. 检查 teammate.md 6.4 节的重试策略
3. 如可恢复，按重试间隔等待后重试
4. 如不可恢复，触发失败转移
5. 记录到 incidents/ 目录
6. 更新 current.json 中的 incident_log
```

### 12.4 执行回滚

```
1. 确认回滚类型（代码/数据/配置）
2. 读取 current.json 中的 last_rollback_point
3. 执行回滚操作
4. 验证回滚结果
5. 更新 current.json
6. 提升 context_version
```
