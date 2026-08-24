# LIFEOS-P3-036｜真实 DB migration 前置验证清单

## 任务信息

- 任务 ID：LIFEOS-P3-036
- 任务名称：真实 DB migration 前置验证清单
- 优先级：P0
- 任务类型：技术验证前置任务 / 检查清单 / 决策输入
- 建议篇幅：1500-3000 字；清单、失败处理和证据路径要完整，但不要展开完整历史或测试日志
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要把候选 SQL、合成空库合同测试、残留 P2 项和未来真实 SQLite 验证步骤整理成可执行前置清单；Codex 更适合技术验证拆解、命令边界、evidence 结构和失败处理设计。
- 是否需要后续独立评审：Conditional；本任务本身不执行真实 DB、不关闭风险、不冻结资产，PM 验收即可；若后续准备执行真实 DB migration、关闭 R-0040、冻结 Schema / API 或进入下一阶段，必须另行独立评审。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 技术规划 / 工程验证前置会话
- 推荐复用的会话：可复用此前 P3 SQL migration / 合同测试工程线 Codex 会话，前提是上一任务已结束、没有未完成修改、上下文未混淆，并且能重新读取本任务卡；否则新建 Codex 技术规划会话。
- 会话判断理由：本任务与 P3-029 至 P3-035 属于同一 SQL migration / DB 验证线，但它不要求独立评审，也不修改工程代码；复用可降低上下文成本。
- 是否需要独立性隔离：No；但不得由本任务会话在后续直接独立评审自己产出的真实 DB 执行结果。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
  - `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
  - `lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P3-034_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-035_r0043_r0044_r0045_risk_closure_decision_package.md`
  - `lifeos/reviews/LIFEOS-P3-035_pm_review.md`
- 可复用既有读取结果：
  - 若同一 Codex 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - R-0040 / R-0043 / R-0044 / R-0045 风险行
  - P3-035 决策包与 PM Review
  - P3-031 evidence manifest
- 任务完成后是否建议保留会话：Yes，作为后续真实 DB 前置验证 / 候选 SQL 验证线会话保留。

## 背景

P3-031 至 P3-034 已在候选 SQL 与合成空库合同测试层形成证据；P3-035 已由 PM 验收并经用户确认，R-0043 / R-0044 / R-0045 已关闭。关闭范围非常克制：仅限候选 SQL、合成空库合同测试、当前 evidence 和有限 Stage 3 受控边界。

P3-035 同时把三个残留 P2 项转入后续真实 DB 验证前置任务：

- P2-2：Tombstone DELETE+INSERT 旁路需在真实 DB 验证前确认。
- P2-3：Tombstone status INSERT 旁路需在真实 DB 验证前确认。
- P2-4：Authorization 激活后子表 DELETE 的审计完整性需在真实 DB 验证前确认。

本任务用于把这些残留项整理成未来真实 SQLite / migration 验证前必须满足的检查清单、命令边界、evidence 结构、失败处理和 PM 验收口径。它不是执行真实 DB 验证本身。

## 授权边界

本任务明确授权：

- 只读审查 P3-029 至 P3-035 的相关设计、候选 SQL、合同测试、评审、PM Review 和 evidence manifest。
- 只读分析 P2-2 / P2-3 / P2-4 如何进入未来真实 DB 前置验证。
- 设计未来真实 DB 验证的最小清单、数据准备原则、命令边界、evidence 目录结构、通过 / 失败标准和回滚 / 停止规则。
- 输出完整交付物到 `lifeos/deliverables/LIFEOS-P3-036_real_db_migration_preflight_checklist.md`。
- 可调用本地预检脚本检查交付物完整性。

本任务不授权：

- 不修改工程代码、候选 SQL、测试脚本、复跑脚本、evidence 或真实数据。
- 不创建、连接、迁移或写入真实数据库。
- 不执行真实 SQL migration。
- 不安装、配置或运行真实 Tauri / IPC。
- 不连接真实 Vault、真实用户文件、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040，不重新打开或关闭 R-0043 / R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不修改 `lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md`、`lifeos/RISK_LOG.md` 或其他 PM 账本。
- 不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- 未来真实 DB migration 验证前，必须先检查哪些对象、命令、数据状态和证据路径。
- P2-2 / P2-3 / P2-4 分别应如何验证、如何判定通过、如何判定失败。
- 哪些验证必须在临时副本或受控测试 DB 中完成，哪些仍禁止触碰真实用户数据。
- evidence 包应如何组织，才能让 PM 和后续独立评审快速复核。
- 一旦出现失败、hash 不匹配、fixture 越权、真实能力误启用或语义冲突，应如何停止并回到 PM。
- 本任务是否足以作为后续“真实 DB 验证执行任务”的输入，还是还需要补充设计 / 评审任务。

## 范围

本任务必须覆盖：

1. **真实 DB 验证前置边界**
   - 明确本任务只设计清单，不执行真实 migration。
   - 区分候选 SQL、合成空库、临时测试 DB、真实用户 DB、真实 Vault。
   - 明确哪些能力仍必须关闭。
2. **P2-2 / P2-3 / P2-4 检查清单**
   - P2-2：Tombstone DELETE+INSERT 旁路。
   - P2-3：Tombstone status INSERT 旁路。
   - P2-4：Authorization 激活后子表 DELETE 审计完整性。
   - 每项必须包含验证目的、输入前置、最小反例、预期阻断 / 审计行为、失败判定、证据要求。
3. **真实 DB 执行任务前的准入条件**
   - 候选 SQL / 测试 / MANIFEST hash 一致性。
   - 迁移前备份、临时副本、只读源、隔离路径、回滚策略。
   - 不使用真实敏感数据的替代 fixture 原则。
   - 失败时不继续、不修补账本、不关闭风险。
4. **evidence 结构**
   - 建议未来任务使用的 evidence 目录结构。
   - 必须包含 `MANIFEST.md` 或 `README.md`。
   - 聊天中只输出摘要，完整日志写文件。
5. **PM 验收和独立评审口径**
   - PM 应复核哪些最小证据。
   - 哪些失败触发 P0 / P1 / P2。
   - 哪些情况必须退出快车道并要求独立评审。
6. **后续任务建议**
   - 如本清单成立，建议下一步创建何种执行任务。
   - 如发现缺口，建议先补何种设计 / 评审任务。

## 非范围

本任务暂时不要做：

- 不执行真实 DB migration。
- 不创建真实 SQLite 数据库验证包。
- 不修改候选 SQL、测试脚本、工程代码或 evidence。
- 不运行真实 Tauri / IPC、真实 Vault、真实文件导出或真实用户数据。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不重新打开或关闭 R-0043 / R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
- `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-030_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- `lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-034_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-035_r0043_r0044_r0045_risk_closure_decision_package.md`
- `lifeos/reviews/LIFEOS-P3-035_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- `RISK_LOG.md` 只需定向读取 R-0040、R-0043、R-0044、R-0045。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0194 至 D-0206 或任务卡指定决策。
- 不主动读取无关 Review、Deliverable 或 Evidence。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 真实 DB 验证前置边界是否足够克制、可执行、可审计。
- P2-2 / P2-3 / P2-4 是否都有明确验证方法、通过标准和失败处理。
- 清单是否能支撑后续执行任务，而不误启用真实能力。
- 是否避免把候选 SQL / 合成空库证据误读为生产 migration 通过。

协审角色必须重点检查：

- 删除 / 撤回、授权、AI 派生、来源身份和证据链是否仍 fail closed。
- 用户原始数据、真实 Vault 和真实 DB 是否仍未被触碰。
- evidence 结构是否足以让 PM 与独立评审复核。
- 是否清楚区分事实、推断、建议和待确认决策。

## 核心问题

请重点回答：

- 未来真实 DB migration 验证前，最小准入条件是什么？
- P2-2 / P2-3 / P2-4 各自如何验证？
- 每项验证的 PASS / FAIL / P0 / P1 / P2 判定是什么？
- evidence 包最小应包含哪些文件？
- 哪些情况必须立即停止并回到 PM？
- 本任务完成后，是否建议创建真实 DB 验证执行任务？如果建议，执行任务的边界是什么？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 Tauri / IPC 通过、R-0040 关闭、正式 MVP 准入或下一阶段准入？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-036_real_db_migration_preflight_checklist.md`

交付物内容必须包括：

- 任务信息
- 执行摘要
- 前置验证边界
- P2-2 / P2-3 / P2-4 检查清单
- 真实 DB 执行任务前准入条件
- 建议验证命令 / 目录 / evidence 结构
- PASS / FAIL / P0 / P1 / P2 判定
- 停止规则与回到 PM 条件
- 不可外推声明
- 后续任务建议
- 风险与待确认事项

## 验收标准

只有满足以下条件，任务才算完成：

- 完整交付物已保存到指定路径。
- 已覆盖 P2-2 / P2-3 / P2-4。
- 已明确本任务不执行真实 DB migration。
- 已明确真实 DB 执行任务前的准入条件。
- 已明确 evidence 结构、通过 / 失败标准和停止规则。
- 已明确 R-0040 仍不可关闭。
- 已明确不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改工程文件、SQL、测试、脚本或 evidence。
- 不创建、连接、迁移或写入真实数据库。
- 不执行真实 SQL migration。
- 不连接真实 Vault、真实用户数据、真实 Tauri / IPC 或真实文件能力。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不重新打开或关闭 R-0043 / R-0044 / R-0045。
- 不修改 PM 账本或风险状态。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整交付物，只输出摘要、交付物路径、本地预检路径和是否需要 PM 决策。
