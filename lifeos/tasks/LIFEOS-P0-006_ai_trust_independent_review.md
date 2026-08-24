# LIFEOS-P0-006｜AI 权限与信任模型独立评审

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

- 任务 ID：LIFEOS-P0-006
- 任务名称：AI 权限与信任模型独立评审
- 优先级：P0
- 任务类型：Independent Review / AI Trust & Safety
- 主责角色：AI 信任与安全负责人
- 协审角色：数据 / 领域模型负责人、产品架构负责人、技术架构负责人
- 必须通过的评审关卡：Gate 3 AI 权限与信任评审；辅助检查 Gate 2 数据与来源评审、Gate 4 技术可行性评审、Gate 1 产品一致性评审
- 状态：Ready

## 背景

LifeOS 是个人长期使用的终身外脑。项目已完成并由 PM 接受：

- `LIFEOS-P0-001` 项目章程与产品宪法
- `LIFEOS-P0-002` 目标用户与核心问题研究
- `LIFEOS-P0-003` 核心领域模型前置研究
- `LIFEOS-P0-004` AI 权限与信任模型
- `LIFEOS-P0-005` 技术可行性 Spike 计划

其中 `LIFEOS-P0-004` 已被 PM 接受为工作模型，但尚未冻结。根据项目规则，AI 权限与信任模型属于关键冻结事项，必须由独立评审会话专门审查后，PM 主会话才能判断是否冻结、条件冻结或返工。

本任务的目的不是产出新版 AI 权限模型，而是站在独立 AI 信任与安全负责人的角度，对 `LIFEOS-P0-004` 进行压力测试式评审。

## 目标

本任务完成后，需要回答：

1. `LIFEOS-P0-004` 是否足以作为 LifeOS V1 AI 权限与信任模型 V0.1 的冻结基础？
2. 它是否清楚区分用户原文、AI 生成内容、AI 推断 / 建议、外部引用来源和用户确认事实？
3. 它是否守住“AI 可读、可整理、可建议，但不能替用户确认”的 V1 边界？
4. 六维 Authorization 是否足以表达 Obsidian、本地、云、第三方模型、目的、位置、时效和撤回？
5. 撤回、删除、派生失效、审计、导出和第三方副本限制是否存在致命漏洞？
6. P0-005 中 SP-04、SP-05、SP-06 是否足以验证该模型的核心风险？
7. 如果不能冻结，必须整改哪些内容？

## 范围

本任务必须覆盖：

- 对 `LIFEOS-P0-004_ai_permission_trust_model.md` 的独立评审。
- 对 `LIFEOS-P0-004_pm_review.md` 的 PM 验收意见复核。
- 对 `LIFEOS-P0-005_technical_feasibility_spike_plan.md` 中 SP-04、SP-05、SP-06、SP-07、SP-08 的相关验证标准复核。
- AI 主动性 L0-L5 边界。
- 六维 Authorization：主体、范围、动作、目的、位置、时效。
- AI 输出身份：整理、生成、推断、建议、候选 Action、候选 Decision、候选 Link。
- 用户确认、拒绝、纠正、撤回、失效、审计和导出。
- Obsidian Vault 只读来源的授权边界。
- 本地处理、LifeOS 云处理、第三方模型处理的边界。
- 高风险场景：心理、医疗、法律、财务等内容的限制。
- 是否存在 consent fatigue、授权过粗、授权过碎、AI 越界、删除假象、审计反向泄露等风险。

## 非范围

本任务暂时不要做：

- 不重写 `LIFEOS-P0-004`。
- 不设计完整 PRD。
- 不设计最终数据库表、API 或权限 UI。
- 不修改 Stitch 原型。
- 不修改代码。
- 不执行技术 Spike。
- 不选择模型供应商或云供应商。
- 不扩大 V1 自动化能力。
- 不冻结技术架构。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/reviews/LIFEOS-P0-004_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-005_pm_review.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：AI 信任与安全负责人必须重点回答：

- AI 在 V1 到底能做什么，不能做什么？
- AI 使用数据的授权是否清楚、可撤回、可解释？
- AI 输出身份是否清楚，不会被误认为用户事实？
- AI 候选 Action / Decision / Link 是否必须经过用户确认？
- 权限撤回后，派生物、缓存、索引、队列、备份、第三方副本是否有处理规则？
- 审计是否能解释事故，同时不反向保存可还原的敏感内容？
- 高风险场景是否被严格限制？

协审角色必须重点检查：

数据 / 领域模型负责人：

- Source、Artifact、Derivation、Feedback、Authorization、AuditEntry、Link 的语义是否足够支撑 AI 信任模型。
- 用户原文、外部来源、AI 派生、用户确认事实是否混淆。
- 撤回、删除、导出、失效是否能被领域模型表达。

产品架构负责人：

- AI 权限模型是否仍服务个人终身外脑，不滑向企业权限后台。
- 授权和确认机制是否会压垮 V1 用户体验。
- 是否把长期“全知全能”愿景提前塞进 V1。

技术架构负责人：

- P0-005 的 SP-04、SP-05、SP-06 是否足以验证该模型。
- 是否存在模型很好看但无法执行的授权、撤回或审计规则。
- 哪些结论必须等待技术 Spike 后才能冻结。

## 核心问题

请重点回答：

1. `LIFEOS-P0-004` 的哪些内容可以直接进入冻结候选？
2. 哪些内容只能作为工作假设，必须等待 Spike？
3. 有没有 AI 越权、权限歧义、撤回假象、审计泄密、用户确认不清的问题？
4. 六维授权是否够用？是否缺少“数据敏感级别、供应商保留策略、模型训练/评估用途、跨项目传播”等维度或规则？
5. L3 内部动作白名单是否安全？哪些必须降级为 L1 派生展示？
6. 高风险场景边界是否足够清楚？
7. Obsidian 接入是否存在“连接即默认授权”的误解风险？
8. 用户纠正、拒绝、撤回是否会被系统错误泛化为长期记忆？
9. 若建议 Pass with Conditions，条件是什么？
10. 若建议 Rework，必须返工哪些部分？

## 交付物

请将完整独立评审保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P0-006_ai_trust_independent_review.md`

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
- 明确说明是否建议冻结 `LIFEOS-P0-004`。
- 明确列出冻结前必须整改或等待 Spike 的内容。
- 明确区分事实、推断、建议和风险。
- 明确说明 Gate 3 是否通过，以及 Gate 2 / Gate 4 的关联风险。
- 不重写主交付物。
- 不修改代码、Stitch 或外部系统。
- 会话回复只输出摘要和评审文件路径。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构或数据模型。
- 不把长期愿景中的全自动 Agent 能力提前纳入 V1。
- 不把 `P0-005` 的 Spike 计划误认为已经实测通过。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评审正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、评审文件路径、是否需要 PM 决策、阻塞或异常说明。
