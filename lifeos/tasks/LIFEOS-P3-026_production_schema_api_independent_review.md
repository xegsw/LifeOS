# LIFEOS-P3-026｜生产 Schema / API 独立反例评审

## 任务信息

- 任务 ID：LIFEOS-P3-026
- 任务名称：生产 Schema / API 独立反例评审
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2000-4000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要从执行者外部视角攻击 P3-025 Schema / API 草案，重点寻找越权、复活、来源混淆、反馈撤回、授权冲突、错误泄露和 IPC dispatcher 风险；不应由 P3-025 执行 Agent 自评。
- 是否需要后续独立评审：No，本任务自身即为独立评审。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：数据 / 领域模型负责人、AI 信任与安全负责人
- 协审角色：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 独立评审会话
- 推荐复用的会话：如已有独立评审线 WorkBuddy 会话且未参与 P3-025 执行、上下文可靠，可复用；否则新建独立评审会话。
- 会话判断理由：P3-026 要评审 P3-025 的生产 Schema / API 草案，必须与 P3-025 执行会话隔离，避免执行者自证。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
- 可复用既有读取结果：
  - 若同一独立评审会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md` 中与 M-01～M-26 相关章节
  - `lifeos/reviews/LIFEOS-P3-024_pm_review.md`
- 任务完成后是否建议保留会话：Yes，作为后续 Schema / API / Tauri 安全评审线会话保留。

## 背景

P3-025 已完成生产 Schema / API 设计草案，并经 PM 验收为 Accepted but Not Frozen。该草案提出候选 SQLite Schema、Tauri IPC / 本地 API 命令、错误码、字段约束与 P3-024 M-01～M-26 验证矩阵映射。

但 P3-025 仍只是设计草案，不是冻结合同，也不是 migration、真实 Tauri / IPC 或 R-0040 关闭证据。进入 migration 设计、最小 Tauri 壳或真实 IPC 验证前，必须先由独立评审会话做反例攻击，确认草案是否存在 P0 / P1 级设计漏洞。

## 目标

本任务完成后，PM 应能判断：

- P3-025 是否可作为后续 migration 设计和最小 Tauri 壳任务的候选输入。
- P3-025 是否存在必须返工的 P0 / P1 设计问题。
- `semantic_object` 聚合承载 Assertion / Decision / Action / Event 是否可作为评审候选继续推进。
- P3-025 是否足够支撑 P3-024 M-01～M-26 真实 Tauri / IPC 前置验证矩阵。
- 哪些条件必须在 Schema / API 冻结、migration 编写、真实 Tauri 验证或 R-0040 关闭前完成。

## 范围

本任务必须覆盖：

- 对 P3-025 生产候选 Schema 的独立审查：
  - Project / Source / Artifact / ArtifactVersion / ContentIdentity
  - Authorization / AuthorizationScope / AuthorizationAction
  - Derivation / DerivationInput / DerivationConstraint
  - Feedback / ImportantLink / LinkEvidence
  - Tombstone / AuditEntry / OutboxJob / Submission
  - FTS / SearchIndex
  - Export / Restore package projection
- 对 P3-025 Tauri IPC / 本地 API 命令草案的独立审查：
  - capture / read / search / suggest / feedback / retract
  - link / revoke authorization / disconnect source / delete
  - export candidate / restore candidates read-only evaluation
  - capability status / health check
- 至少构造以下反例攻击方向：
  - 多 Project 归属与 Project scope 被误读为权限。
  - 多 Source、Source disconnect、Source generation 变化后的派生失效。
  - allow + deny、重复 allow、未知授权、过期授权、processor / purpose / location mismatch。
  - ArtifactVersion 精确版本、Artifact generation、Source generation、tombstone 的竞态组合。
  - Feedback confirm / correct / retract / duplicate / idempotency 乱序。
  - DerivationInput 不完整、evidence pointer 被误用为权威输入。
  - ImportantLink AI 候选与用户确认 Link 的身份混淆。
  - FTS 命中绕过权威回连。
  - export package / restore candidates 导致旧包复活或已删内容复活。
  - IPC 三窄命令映射滑向任意 dispatcher。
  - 错误码泄露对象存在性、路径、SQL、内部状态或可被自动重试扩大权限。
  - capability_status / health_check 泄露真实路径、真实能力或环境信息。
  - `semantic_object` 聚合稀释 Assertion / Decision / Action / Event 领域语义。
- 对 Gate 2 / Gate 3 / Gate 4 做 Pass / Pass with Conditions / Rework / Blocked 结论。
- 给出冻结前条件、实现前条件和后续任务建议。

## 非范围

本任务暂时不要做：

- 不修改 P3-025 主交付物。
- 不写 SQL migration。
- 不修改工程代码。
- 不创建 Tauri IPC handler。
- 不安装、配置或运行真实 Tauri。
- 不复跑或扩展工程测试，除非只是在临时只读分析中引用既有 evidence。
- 不处理真实数据、低敏真实数据、真实 Vault、真实用户文件或外部用户。
- 不启用真实文件导出、路径扩权、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md` 或 `OPEN_QUESTIONS.md`。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- `lifeos/reviews/LIFEOS-P3-024_pm_review.md`
- 可按需定向参考：`lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- 可按需定向参考：`lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- P0 / P0-007 / P0-009 仅在发现 P3-025 与领域模型或 AI 权限边界可能冲突时定向读取相关章节。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`，只读任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- P3-025 是否清楚区分用户原文、AI 生成、AI 推断 / 建议、外部引用来源和用户确认事实。
- P3-025 是否能表达 Source、Artifact、ArtifactVersion、ContentIdentity、DerivationInput、Feedback、Authorization、Tombstone 的独立生命周期。
- P3-025 的统一消费门是否真的能 fail closed，还是存在可以绕过的组合路径。
- `semantic_object` 聚合是否损害已冻结领域语义，是否需要拆表或设置拆分条件。

协审角色必须重点检查：

- P3-025 的 API / IPC 合同是否能支撑 P3-024 M-01～M-26。
- 错误码和 health / capability 输出是否存在信息泄露。
- FTS、导出包、恢复候选、outbox、audit 是否保持非权威、可重建或最小化。
- 是否有任何结论被误写成 Schema / API 冻结、真实 Tauri 启用、R-0040 关闭或下一阶段准入。

## 核心问题

请重点回答：

- P3-025 是否建议 Pass、Pass with Conditions、Rework 还是 Blocked？
- 若 Rework，必须返工哪些 P0 / P1 问题？
- 若 Pass with Conditions，条件是什么、适用范围是什么、失效条件是什么？
- P3-025 是否可作为 migration 设计输入？
- P3-025 是否可作为最小 Tauri 壳任务输入？
- P3-025 是否可作为 R-0040 关闭输入？如果不能，缺口是什么？
- `semantic_object` 聚合应继续、拆分，还是设条件后继续？

## 交付物

请将完整评审保存为 Markdown 文件，路径建议：

`lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`

请输出的文件内容包括：

- 评审信息
- 评审摘要
- 已通过内容
- 关键问题
- 必须整改项
- 条件通过项
- 反例攻击清单与结论
- Gate 2 / Gate 3 / Gate 4 检查
- 风险
- 需要 PM 决策
- 最终建议

篇幅控制：

- 独立评审型任务建议 2000-4000 字。
- 超出当前任务范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整独立评审已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供评审路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确声明本任务不冻结 Schema / API、不写 migration、不运行 Tauri、不启用真实能力、不关闭 R-0040。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改项目账本。
- 不写 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不自行启动后续任务。

## 给专项会话的可复制启动提示词

请先读取当前项目根目录的 `AGENTS.md`，并按其中规则执行 LifeOS 专项任务。

任务文件：

`lifeos/tasks/LIFEOS-P3-026_production_schema_api_independent_review.md`

请注意：你是独立评审会话，不是 PM 主会话，也不是 P3-025 执行会话。只做只读独立反例评审，不修改 P3-025、不写 migration、不改代码、不安装、不配置、不运行真实 Tauri，不修改工程文件、Stitch 或项目账本；不得关闭 R-0040，不得启用真实能力，不得冻结 Schema / API 或工程基线，不得进入下一阶段。完整评审写入任务卡指定路径，聊天回复只输出摘要、评审路径、预检路径和是否需要 PM 决策。
