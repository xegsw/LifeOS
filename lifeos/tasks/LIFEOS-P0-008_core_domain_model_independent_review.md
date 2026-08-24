# LIFEOS-P0-008｜核心领域模型独立评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的独立评审专项会话，不是 PM 主会话。请只完成下方评审任务，不要自行扩大范围，不要重写原交付物，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P0-008
- 任务名称：核心领域模型独立评审
- 优先级：P0
- 任务类型：Independent Review / Data & Domain Model
- 主责角色：数据 / 领域模型负责人
- 协审角色：AI 信任与安全负责人、技术架构负责人、产品架构负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审；辅助检查 Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审、Gate 1 产品一致性评审
- 状态：Ready

## 背景

`LIFEOS-P0-003` 已被 PM 接受为核心领域模型前置研究，但尚未正式冻结。根据项目规则，核心领域模型属于关键冻结事项，必须经过独立评审后，PM 主会话才能决定是否冻结为 V0.1 语义基线。

当前 AI 权限与信任模型已完成独立评审和条件整改，`LIFEOS-P0-004` 与 `LIFEOS-P0-007` 已共同冻结为 AI 权限与信任模型 V0.1 原则与语义基线。因此，本次领域模型独立评审必须检查 P0-003 是否能承接这些已冻结规则，尤其是四类命令、Derivation 约束继承、L3 默认 L1、导出不复活、审计最小化和第三方资格边界。

本任务不是产出新版领域模型，而是站在独立数据 / 领域模型负责人的角度，对 `LIFEOS-P0-003` 进行冻结前评审。

## 目标

本任务完成后，需要回答：

1. `LIFEOS-P0-003` 是否足以作为 LifeOS 核心领域模型 V0.1 语义基线的冻结基础？
2. 11 个对象 + `Link` 是否表达充分，还是存在过度实体化、缺失语义或边界混淆？
3. `Source` 与 `Artifact` 的分离是否足以支撑 Obsidian、外部来源、版本、权限、断开、删除和导出？
4. `Derivation`、`Feedback`、`Authorization`、`AuditEntry`、`Link` 是否足以承接 P0-007 的 AI 权限与信任基线？
5. 四类命令 `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 是否能被领域模型清楚表达？
6. 用户原文、外部来源、AI 派生、AI 推断/建议、用户确认事实是否始终可区分？
7. `Action`、`Decision`、`Assertion`、`Project`、`Event` 的边界是否清楚，是否服务 V1 第一场景？
8. 若不能冻结，必须整改哪些内容？

## 范围

本任务必须覆盖：

- 对 `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md` 的独立评审。
- 对 `lifeos/reviews/LIFEOS-P0-003_pm_review.md` 的 PM 验收意见复核。
- 对已冻结 AI 权限与信任基线的兼容性检查：
  - `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
  - `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P0-006_ai_trust_independent_review.md`
  - `lifeos/reviews/LIFEOS-P0-007_pm_review.md`
- 对 `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md` 中 SP-02、SP-03、SP-05、SP-06、SP-07、SP-08 的领域模型相关要求复核。
- 11 个对象 + `Link` 的语义边界。
- Source / Artifact / version / Derivation / Feedback / Authorization / AuditEntry / Link 的生命周期。
- Project 恢复包、Action、Decision、Assertion、Event 与 V1 第一场景的关系。
- Obsidian 只读来源、来源断开、删除、导出、撤回、派生失效、证据失效和用户确认对象待复核状态。
- 领域语义是否被误读为数据库表、API 或 UI 模块冻结的风险。

## 非范围

本任务暂时不要做：

- 不重写 `LIFEOS-P0-003`。
- 不设计最终数据库表、ERD、API、索引或事件流。
- 不设计完整 PRD。
- 不修改代码。
- 不修改 Stitch。
- 不执行技术 Spike。
- 不冻结技术架构。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/reviews/LIFEOS-P0-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-006_ai_trust_independent_review.md`
- `lifeos/reviews/LIFEOS-P0-007_pm_review.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：数据 / 领域模型负责人必须重点回答：

- 用户原文在哪里？
- 外部来源在哪里？
- AI 派生在哪里？
- 用户确认事实在哪里？
- 来源、版本、权限、删除、撤回、断开、导出如何表达？
- Derivation 如何继承输入限制？
- Feedback 如何表达确认、拒绝、纠正、撤回、完成、延期？
- AuditEntry 如何解释关键操作，同时不反向泄露内容？
- Link 何时需要重型化，何时可以轻量展示？
- 领域模型是否能支撑 V1 第一场景“开工/切换项目时的 5 分钟上下文恢复与下一步确认”？

协审角色必须重点检查：

AI 信任与安全负责人：

- P0-003 是否继承 P0-007 的 AI 权限与信任基线。
- AI 候选、用户确认、证据失效、撤回、删除和 L3 默认 L1 是否能被模型表达。
- 高风险内容与第三方资格边界是否有领域承载点。

技术架构负责人：

- 领域语义是否能被最小实现验证，而不是被误读成 11 张表或重型图数据库。
- 是否能支持 SP-02、SP-03、SP-05、SP-06、SP-07、SP-08。
- 是否存在后续不可实现或成本过高的语义设计。

产品架构负责人：

- 模型是否服务个人终身外脑和 V1 第一场景。
- 是否滑向企业后台、开发者工具、IT 运维或通用知识图谱。
- 是否把长期愿景提前塞进 V1。

## 核心问题

请重点回答：

1. 哪些 P0-003 内容可以直接进入冻结候选？
2. 哪些内容只能作为工作假设，必须等待 Spike 或 PRD？
3. 11 个对象 + `Link` 是否足够？是否有对象应合并、降级、拆分或重新命名？
4. `Source` 与 `Artifact` 分离是否清楚？是否覆盖 Obsidian 只读、来源断开、外部许可、版本和导出？
5. `Derivation` 是否足以表达 AI 整理、推断、建议、候选对象、输入版本、授权、政策包络、处理位置、有效状态和限制继承？
6. 四类命令效果矩阵是否能被当前模型表达？缺少哪些生命周期状态？
7. `Action`、`Decision`、`Assertion`、`Feedback` 的边界是否清楚，是否会导致用户确认状态混淆？
8. `Link` 的来源、确认状态、有效期和重要性分层是否足够？
9. 审计、删除、导出、重导入、不复活是否有最低领域语义？
10. 若建议 Pass with Conditions，条件是什么？若建议 Rework，必须整改哪些部分？

## 交付物

请将完整独立评审保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P0-008_core_domain_model_independent_review.md`

请使用 `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md` 的结构，文件内容必须包括：

- 评审信息
- 评审摘要
- 已通过内容
- 关键问题
- 必须整改项
- 条件通过项
- Gate 1 / Gate 2 / Gate 3 / Gate 4 / Gate 5 检查
- 风险
- 需要 PM 决策
- 最终建议

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 独立评审文件已保存到指定路径。
- 明确给出评审结论：Pass / Pass with Conditions / Rework / Blocked。
- 明确说明是否建议冻结 `LIFEOS-P0-003`。
- 明确列出冻结前必须整改或等待 Spike / PRD 的内容。
- 明确区分事实、推断、建议和风险。
- 明确说明 Gate 2 是否通过，以及 Gate 3 / Gate 4 的关联风险。
- 不重写主交付物。
- 不修改代码、Stitch 或外部系统。
- 会话回复只输出摘要和评审文件路径。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、AI 权限模型或数据模型。
- 不把 11 个对象 + `Link` 误读为数据库表、API 或 UI 模块冻结。
- 不把 P0-005 的 Spike 计划误认为已经实测通过。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评审正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、评审文件路径、是否需要 PM 决策、阻塞或异常说明。
