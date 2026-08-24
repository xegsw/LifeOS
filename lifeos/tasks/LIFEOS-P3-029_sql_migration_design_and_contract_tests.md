# LIFEOS-P3-029｜SQL migration 设计 / 合同测试任务

## 任务信息

- 任务 ID：LIFEOS-P3-029
- 任务名称：SQL migration 设计 / 合同测试任务
- 优先级：P0
- 任务类型：设计型任务 / 技术合同任务
- 建议篇幅：3000-5000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要把 P3-025 / P3-027 / P3-028 已通过的 Schema / API 设计约束转成可评审的 migration 设计、约束清单和合同测试草案；Codex 更适合结构化数据模型、约束表达、测试矩阵和工程边界文档。
- 是否需要后续独立评审：Yes。P3-029 完成后，应安排轻量独立评审，确认 migration 设计没有漏掉授权、撤回、来源身份、派生输入、ContentIdentity、`semantic_object` 拆表门和四 invoke DTO 合同。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：数据 / 领域模型负责人、技术架构负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：Codex 技术 / 数据设计会话
- 推荐复用的会话：可复用此前承担 P3-025 或 P3-027 的 Codex 技术 / 数据设计会话，前提是该会话已完成旧任务、不参与后续独立评审、上下文未混淆且能重新读取本任务卡；否则新建 Codex 专项设计会话。
- 会话判断理由：P3-029 是 Schema / API 设计线的后续技术合同任务，适合复用同一技术 / 数据设计线；但不得由 P3-028 独立评审会话执行，以保持后续评审独立性。
- 是否需要独立性隔离：Yes。P3-028 独立评审会话不得执行本任务；P3-029 执行会话不得自行评审自己的设计。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P3-027_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-028_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- 可复用既有读取结果：
  - 若同一会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-027 / P3-028 交付物与 PM Review
  - P3-025 中与 Schema / API / 错误码 / IPC DTO / `semantic_object` 相关章节
  - P3-024 中与 M-01 / M-04 / M-20 / capability / invoke 验证相关章节
- 任务完成后是否建议保留会话：Yes，作为后续 migration 设计整改、合同测试细化或候选 SQL 实现前任务线会话保留。

## 背景

P3-025 已形成生产 Schema / API 设计草案，状态为 Accepted but Not Frozen。P3-026 独立评审提出 7 个 P1 条件。P3-027 已在设计层完成整改，P3-028 轻量独立复核结论为 Pass，并确认：

- P3-026 的 7 个 P1 条件已在设计层关闭。
- 未发现新增 P0 / P1。
- 四 invoke 拆分（`lifeos_read` / `lifeos_export_candidate` / `lifeos_mutate` / `lifeos_destruct`）可作为后续候选输入。
- 3 个 P2 清洁项必须进入下一步 migration 设计检查清单。

本任务的作用是把这些设计约束转成可执行前的 SQL migration 设计和合同测试草案。注意：本任务不是写 migration、不是执行 migration、不是修改工程代码。

## 目标

本任务完成后，PM 应能判断：

- P3-025 + P3-027 + P3-028 是否已被转成清晰的 migration 设计输入。
- 哪些表、字段、约束、索引、触发器或事务校验需要进入后续真实 migration。
- 哪些合同测试必须在正式写 migration 前先定义。
- P3-028 的 3 个 P2 清洁项是否已被明确处理。
- Decision / Action 是否因字段数触发 `semantic_object` 拆表门。
- 四 invoke 拆分如何影响 DTO / capability / P3-024 M-01 / M-04 / M-20 合同测试。
- 是否允许后续启动“候选 SQL migration 编写任务”或是否仍需返工 / 独立评审。

## 范围

本任务必须覆盖：

1. **Migration 设计总览**
   - 按权威数据、来源 / 版本、AI 派生、反馈、授权、审计、搜索 / 派生索引、任务队列、IPC DTO 支撑等分层整理候选 schema。
   - 标记每一组约束来自 P3-025、P3-027、P3-028 中哪一项。
2. **DB 级约束设计**
   - DerivationInput 恰一非空与 type / column 一致性。
   - ContentIdentity 按 `identity_kind` 的 `origin_actor_ref` / `derivation_id` 条件约束。
   - Feedback retract、`feedback_dependency` 与跨 target fail closed 强制方式。
   - Authorization scope、deny 优先、allow strict intersection 的持久化支撑。
   - `semantic_object` schema version、current pointer、migration_required 与 tombstone / active_blocked 语义。
3. **P3-028 P2 清洁项处理**
   - 明确 retract-of-retract 是否允许，以及状态效果。
   - 明确 `feedback_dependency` 跨 target 依赖由 DB CHECK、触发器还是事务级校验强制。
   - 形式化定义 authorization `strict_intersection`。
4. **`semantic_object` 拆表门复查**
   - 复核 Assertion / Decision / Action / Event 的持久化顶层专属字段数。
   - 若 Decision / Action 因新增字段超过 5，必须提出拆表建议；若仍聚合，说明原因和失效条件。
5. **四 invoke / DTO 合同测试草案**
   - `lifeos_read`
   - `lifeos_export_candidate`
   - `lifeos_mutate`
   - `lifeos_destruct`
   - 对每个 invoke 列出正测、未知 action、未知字段、跨 variant 字段、错误 contract version、destruct 缺少 preview token / expected generation / idempotency key 等反例。
6. **P3-024 矩阵影响**
   - 将 M-01 / M-04 / M-20 从三 invoke 调整为四 invoke 的设计补丁建议。
   - 明确本任务不运行 Tauri、不创建 handler、不验证真实 capability。
7. **合同测试清单**
   - 按 P0 / P1 / P2 分级列出后续必须实现的测试。
   - 每条测试说明目标、输入、期望结果、覆盖风险、对应约束。
8. **后续任务判断**
   - 是否建议下一步做独立评审。
   - 是否允许进入候选 SQL migration 编写任务。
   - 仍然阻塞最小 Tauri shell / handler 的条件。

## 非范围

本任务暂时不要做：

- 不创建 `.sql` migration 文件。
- 不执行任何 SQL migration。
- 不修改工程代码。
- 不修改 `lifeos/engineering/` 下任何文件。
- 不创建或修改 Tauri IPC handler。
- 不安装、配置或运行真实 Tauri。
- 不连接真实数据库、真实 Vault 或真实用户数据。
- 不处理真实敏感数据、真实用户文件或外部用户。
- 不启用真实文件导出、路径扩权、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不修改 P3-025、P3-027 或 P3-028 主交付物。
- 不修改项目账本。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

允许在交付物中写“候选 DDL 片段 / 约束伪代码 / 测试伪代码”用于表达设计，但不得将其保存为可执行 migration 文件，也不得运行。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-027_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-028_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- P3-025 可按 Schema / API / IPC DTO / `semantic_object` / 错误码相关章节定向读取。
- P3-024 可按 M-01 / M-04 / M-20 / capability / invoke 验证相关章节定向读取。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 每个关键领域对象是否有清楚的持久化语义、生命周期、来源和版本表达。
- 哪些约束必须由 DB 层强制，哪些只能由事务 / 应用层配合。
- 是否存在把领域语义误写成表结构冻结的风险。
- 是否存在会导致后续真实 migration 难以实现、无法回滚或无法验证的设计缺口。

协审角色必须重点检查：

- 用户原文、AI 生成、AI 推断 / 建议、外部引用来源和用户确认事实是否不会在 schema 中混淆。
- 授权、撤回、删除、导出、候选建议、恢复包是否仍 fail closed。
- 四 invoke 拆分是否有可测试的 DTO / capability 合同。
- P3-024 M-01 / M-04 / M-20 调整是否清楚，但没有被误写成真实 Tauri 已验证。

## 核心问题

请重点回答：

- 是否已经形成足够清晰的 SQL migration 设计输入？
- P3-028 的 3 个 P2 清洁项是否已被明确处理？
- `semantic_object` 是否继续聚合，还是触发拆表？
- 哪些 DB CHECK / trigger / partial index / unique index / transaction guard 是 Must？
- 哪些合同测试是正式写 migration 前必须先定义的 P0？
- 四 invoke 拆分如何进入 DTO / capability 合同测试？
- 是否允许进入后续候选 SQL migration 编写任务？
- 是否仍阻塞最小 Tauri shell / handler？

## 交付物

请将完整交付物保存为 Markdown 文件，路径建议：

`lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`

请输出的文件内容包括：

- 结论摘要
- 非实现 / 非冻结声明
- Migration 设计总览
- 表 / 字段 / 约束 / 索引 / 触发器候选清单
- P3-028 P2 清洁项处理
- `semantic_object` 聚合 / 拆表复查
- 四 invoke / DTO 合同测试草案
- P3-024 M-01 / M-04 / M-20 调整建议
- P0 / P1 / P2 合同测试清单
- 后续任务建议
- 角色检查点结果
- Gate 2 / Gate 3 / Gate 4 结论
- 需要 PM / 用户确认的问题

篇幅控制：

- 设计型 / 技术合同任务建议 3000-5000 字。
- 超出当前任务范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确列出是否存在 P0 / P1 / P2 问题。
- 明确声明本任务不写、不执行 SQL migration，不改代码，不运行 Tauri，不启用真实能力，不冻结 Schema / API，不关闭 R-0040。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改 P3-025、P3-027 或 P3-028。
- 不修改项目账本。
- 不创建 `.sql` migration 文件。
- 不执行 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。

