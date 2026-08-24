# LIFEOS-P1-002｜V1 范围独立评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P1-002
- 任务名称：V1 范围独立评审
- 优先级：P0
- 任务类型：评审型任务
- 建议篇幅：2000-4000 字
- 主责角色：产品架构负责人
- 协审角色：用户研究 / 市场验证负责人、体验设计负责人、数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；辅助检查 Gate 5 用户价值验证评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P1-001` 已完成 V1 范围冻结草案，并通过 PM 验收，当前状态为 Accepted。  
但 V1 范围属于关键冻结资产，根据 LifeOS 项目规则，不能因为任务验收通过就直接冻结，必须先完成独立评审。

本任务的职责是判断 P1-001 是否适合作为 V1 范围冻结基线，找出冻结前必须整改的问题，并给出 Pass / Pass with Conditions / Rework / Blocked 结论。

## 目标

本任务完成后，需要回答：

1. P1-001 是否可以作为 V1 范围冻结依据？
2. V1 Must Have / Should Have / Could Have / Non-goals 是否清晰、合理、足够克制？
3. V1 是否仍然聚焦第一目标用户与第一场景？
4. 是否存在会让 V1 过重、过窄、偏离定位或无法验证的范围风险？
5. 如果不能直接冻结，冻结前必须补哪些条件？

## 范围

本任务必须覆盖：

- 对 P1-001 V1 一句话范围的评审。
- 对 Must Have / Should Have / Could Have / Non-goals 的完整性、优先级和边界评审。
- 对 V1 第一目标用户“技术型独立产品构建者”的适配性评审。
- 对 V1 第一场景“开工 / 切换项目时的 5 分钟上下文恢复与下一步确认”的适配性评审。
- 对 Obsidian 只读来源在 V1 中位置的评审。
- 对条件性需求、Spike 依赖和失败降级路径的评审。
- 对首页 / 今日页 PRD 输入边界是否足够的评审。
- 对成功指标、反证指标和用户验证方式的评审。
- 对冻结前必须整改项、条件通过项和后续任务建议的判断。

## 非范围

本任务暂时不要做：

- 不重写 P1-001 主交付物。
- 不产出完整 V1 PRD。
- 不产出首页 / 今日页 PRD。
- 不设计首页 / 今日页详细交互。
- 不修改 Stitch。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不扩大 V1 为全知全能 Agent。
- 不直接冻结 V1 范围；只输出独立评审结论和冻结建议。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/reviews/LIFEOS-P1-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-001_project_charter_product_constitution.md`
- `lifeos/deliverables/LIFEOS-P0-002_target_users_core_problems_research.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：产品架构负责人必须重点回答：

- P1-001 是否仍然服务“个人终身外脑”，而不是企业后台、IT 运维、开发者工具、普通笔记或普通任务管理？
- P1-001 是否服务第一目标用户和第一场景？
- V1 范围是否足够小，能支持真实 MVP；又是否足够完整，能形成闭环价值？
- Must Have 是否存在“看似基础但实际过重”的内容？
- Non-goals 是否足以阻止长期愿景提前侵入 V1？

协审角色必须重点检查：

- 用户研究 / 市场验证负责人：当前范围是否对应真实高频痛点，指标是否能验证价值和反证。
- 体验设计负责人：首页 / 今日页输入边界是否足够清楚，是否避免制造焦虑或后台感。
- 数据 / 领域模型负责人：范围是否继承核心领域模型 V0.1，不混淆用户原文、AI 派生、AI 推断 / 建议和外部来源。
- AI 信任与安全负责人：AI 权限、确认、纠正、撤回、删除和高风险边界是否继承冻结基线。
- 技术架构负责人：条件性需求是否正确绑定 Spike，不把未验证能力写成上线承诺。

## 核心问题

请重点回答：

1. V1 范围是否适合冻结？如果不适合，原因是什么？
2. Must Have / Should Have / Could Have / Non-goals 是否过宽、过窄或边界不清？
3. 当前范围是否足够服务目标用户与第一场景？
4. 条件性需求和 Spike 依赖是否清楚？失败降级是否足够具体？
5. Obsidian 在 V1 中的位置是否合适：Must Have、Should Have、条件性 Must Have，还是后置？
6. 基础导出、最小审计、撤回 / 删除作为 Must Have 是否会使 MVP 过重？
7. 成功指标和反证指标是否足够支撑后续验证？
8. 冻结 V1 范围前必须修正、补充或确认什么？

## 交付物

请将完整评审交付物保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P1-002_v1_scope_independent_review.md`

请输出的文件内容包括：

- 评审信息
- 评审摘要
- 已通过内容
- 关键问题
- 必须整改项
- 条件通过项
- 关卡检查
- 风险
- 需要 PM 决策
- 最终建议

篇幅控制：

- 本任务为评审型任务，建议 2000-4000 字。
- 不要重写 P1-001。
- 超出当前评审范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整评审文件已保存到指定路径。
- 评审结论明确为 Pass / Pass with Conditions / Rework / Blocked 之一。
- 明确说明 V1 范围是否建议冻结，以及冻结前条件。
- 明确列出 Must / Should / Could / Non-goals 的问题和建议。
- 明确检查 Obsidian、导出、审计、撤回 / 删除、首页 / 今日页输入边界。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 不修改 P1-001 主交付物。
- 不修改代码、Stitch 或外部系统。
- 不擅自冻结 V1 范围。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 为全知全能 Agent。
- 不直接启动首页 / 今日页 PRD。
- 不擅自冻结 V1 范围、技术架构或产品原型。
- 不把技术 Spike 计划误认为已经实测通过。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评审正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
