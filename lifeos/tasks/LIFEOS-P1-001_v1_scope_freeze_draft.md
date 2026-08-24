# LIFEOS-P1-001｜V1 范围冻结草案

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P1-001
- 任务名称：V1 范围冻结草案
- 优先级：P0
- 任务类型：决策型任务
- 建议篇幅：1000-2000 字
- 主责角色：产品架构负责人
- 协审角色：体验设计负责人、数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人、用户研究 / 市场验证负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；辅助检查 Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审、Gate 5 用户价值验证评审
- 状态：Ready

## 背景

LifeOS 已完成 Stage 0 底层定义，并进入 Stage 1 V1 定义。当前已冻结：

- 产品定位
- 目标用户
- V1 第一场景
- AI 权限与信任模型 V0.1 原则与语义基线
- 核心领域模型 V0.1 语义基线

技术 Spike 计划已被 PM 接受，但技术架构和关键能力尚未实测。因此 V1 范围草案可以写“条件性需求”，但不能把未验证能力写成已实现承诺。

## 目标

本任务完成后，需要回答：

1. LifeOS V1 到底做什么、不做什么？
2. V1 如何服务第一目标用户“技术型独立产品构建者”？
3. V1 如何服务第一场景“开工 / 切换项目时的 5 分钟上下文恢复与下一步确认”？
4. 哪些能力是 V1 必须有，哪些是条件性需求，哪些明确不进入 V1？
5. V1 成功验收应看哪些用户价值、信任和护栏指标？

## 范围

本任务必须覆盖：

- V1 用户与场景边界。
- V1 核心闭环：捕获 → 保存 → 整理 → 找回 / 今日 → 确认行动 → 反馈。
- V1 Must Have / Should Have / Could Have / Non-goals。
- 条件性需求列表：依赖哪些 Spike 或后续用户验证。
- Obsidian 只读来源在 V1 中的范围边界。
- AI 能力边界：可读、可整理、可建议，不可替用户确认。
- 首页 / 今日页后续 PRD 的输入边界。
- V1 成功指标与反证指标。

## 非范围

本任务暂时不要做：

- 不写完整 PRD。
- 不设计首页 / 今日页详细交互。
- 不修改 Stitch。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不扩大 V1 为全知全能 Agent。
- 不把技术候选栈写成冻结结论。
- 不冻结 V1 范围；本任务只输出冻结草案和 PM 决策建议。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-001_project_charter_product_constitution.md`
- `lifeos/deliverables/LIFEOS-P0-002_target_users_core_problems_research.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：产品架构负责人必须重点回答：

- V1 是否服务个人终身外脑，而不是企业后台、IT 运维、开发者工具、普通笔记或普通任务工具？
- V1 是否聚焦第一目标用户和第一场景？
- V1 是否围绕“找回上下文 > 下一步/减少遗漏 > 今日重点”排序？
- 哪些长期愿景必须明确后置？

协审角色必须重点检查：

- 体验设计负责人：范围是否足以支撑首页 / 今日页 PRD，但不过早写交互细节。
- 数据 / 领域模型负责人：范围是否继承核心领域模型 V0.1。
- AI 信任与安全负责人：范围是否继承 AI 权限与信任模型 V0.1。
- 技术架构负责人：条件性需求是否标明 Spike 依赖，不把未验证能力写死。
- 用户研究 / 市场验证负责人：指标是否能验证真实价值，而非表面活跃。

## 核心问题

请重点回答：

1. V1 的一句话范围是什么？
2. V1 Must Have、Should Have、Could Have、Non-goals 分别是什么？
3. 哪些需求是条件性需求？对应依赖哪个 Spike 或用户验证？
4. V1 首页 / 今日页后续 PRD 应承接哪些范围边界？
5. V1 成功指标和反证指标是什么？
6. 哪些内容必须明确不进入 V1？
7. 是否建议 PM 后续冻结 V1 范围？冻结前还缺什么？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`

请输出的文件内容包括：

- 文档状态与范围声明
- V1 一句话范围
- 目标用户与核心场景
- Must Have / Should Have / Could Have / Non-goals
- 条件性需求与验证依赖
- 首页 / 今日页 PRD 输入边界
- 成功指标与反证指标
- 风险与待确认问题
- 是否建议 PM 冻结 V1 范围及冻结前条件

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整交付物已保存到指定路径。
- 篇幅控制在 1000-2000 字左右；超出内容放入后续任务建议。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 明确区分 Must Have、Should Have、Could Have、Non-goals。
- 条件性需求必须标明验证依赖和失败降级方向。
- 不修改代码、Stitch 或外部系统。
- 不擅自冻结 V1 范围，只提出冻结建议和条件。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 为全知全能 Agent。
- 不擅自冻结 V1 范围、技术架构或产品原型。
- 不把技术 Spike 计划误认为已经实测通过。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
