# LIFEOS-P1-007｜首页 / 今日页 Stitch 原型修改

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P1-007
- 任务名称：首页 / 今日页 Stitch 原型修改
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；辅助检查 Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-004` 与 `LIFEOS-P1-006` 已共同冻结为首页 / 今日页 PRD V0.1。  
当前 Stitch 高保真原型仍存在 IT 运维 / Kubernetes 叙事占比过高、内容身份区分不足、AI 建议缺少证据和反馈入口、状态表达不足等问题。

本任务是首次授权修改 Stitch，但授权范围极窄：**只修改首页 / 今日页，不修改其他页面，不扩展产品范围，不冻结原型。**

当前 Stitch 原型：

https://stitch.withgoogle.com/projects/7778510350051176390

## 目标

本任务完成后，需要：

1. 按首页 / 今日页 PRD V0.1 修改 Stitch 首页 / 今日页。
2. 将首页主叙事从 IT 运维 / Kubernetes 默认叙事调整为个人外脑的 Project 恢复与下一步确认。
3. 至少形成一个非运维 Project 的默认恢复画面。
4. 至少补充一个未选 / 空态或“暂无可靠建议”关键画面 / 状态表达。
5. 至少补充一个权限受限或离线代表态的关键画面 / 状态表达。
6. 输出修改报告，说明改了什么、没有改什么、仍待评审什么。

## 范围

本任务可以做：

- 修改当前 Stitch 的首页 / 今日页内容、模块、文案和必要状态画面。
- 将“领域 / IT 运维”改为当前 Project 语义。
- 将 Kubernetes / 运维样例降为普通 Project 样例，或替换为非运维 Project 主样例。
- 调整首页信息优先级为：当前 Project 与恢复上下文 → 零或一个候选下一步 → 快速捕获 → 近期有意义变化 → 用户已确认安排 → 最近痕迹。
- 表达用户原文、外部来源、AI 整理、AI 推断 / 建议、用户确认内容的身份区分。
- 为 AI 候选下一步补充身份、简短理由、时效 / 缺口、关键证据入口和确认 / 编辑 / 拒绝 / 忽略入口。
- 按 P1-006 采用渐进披露：首屏必显 / 详情可达 / 仅异常时显。
- 表达 Project 来源四态中的必要状态：用户本次选择、最近确认延续、系统候选、未选态。
- 表达快速捕获的耐久保存语义：保存中、已耐久保存、离线待同步 / 未耐久、失败重试。
- 表达“暂无可靠建议”不是失败状态。
- 表达权限受限或离线代表态，但不做完整设置页或清理控制台。

## 非范围

本任务暂时不要做：

- 不修改 Stitch 中首页 / 今日页以外的任何页面。
- 不新增其他产品页面。
- 不重写 PRD。
- 不冻结原型。
- 不写代码。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不执行真实用户测试。
- 不把首页做成企业后台、IT 运维台、KPI 面板、全局任务墙、完整日历或自动化运行台。
- 不放行 L3；首页候选下一步仍保持 L1 / L2 展示。
- 不把完整删除、撤回、断源、副本处置和清理流程放进首页主信息面。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`
- `lifeos/reviews/LIFEOS-P1-006_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- 当前 Stitch 原型：https://stitch.withgoogle.com/projects/7778510350051176390
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：体验设计负责人必须重点回答：

- 修改后的首页是否一眼回答“今天从哪里继续”？
- 是否明显降低 IT 运维 / Kubernetes 默认叙事？
- 首页首屏是否更轻，不被身份、权限、审计或清理状态压垮？
- 是否体现“零或一个候选下一步”和“暂无可靠建议”？
- 状态画面是否足以支持后续原型独立评审？

协审角色必须重点检查：

- 产品架构负责人：是否继承个人终身外脑、V1 第一用户 / 场景和首页 PRD V0.1，不扩大范围。
- 数据 / 领域模型负责人：内容身份、Project、Source、Artifact、Derivation、Feedback、Authorization 等语义是否未被混淆。
- AI 信任与安全负责人：AI 候选、证据、确认、撤回入口和权限 / 离线状态是否不误导。
- 用户研究 / 市场验证负责人：原型是否可用于后续真实 / 等价中断 Project 恢复测试。

## 核心问题

请重点回答：

1. 实际修改了 Stitch 首页 / 今日页的哪些模块、文案或状态？
2. 哪些旧内容被保留，保留理由是什么？
3. 哪些 IT 运维 / Kubernetes / 自动化 / 后台化内容被移除、降级或替换？
4. 修改后是否覆盖默认恢复、未选 / 空态或暂无可靠建议、权限 / 离线代表态？
5. 修改后是否清楚区分用户原文、外部来源、AI 整理、AI 推断 / 建议和用户确认内容？
6. 修改后是否仍有无法在 Stitch 静态原型中充分表达的交互状态？
7. 是否建议进入首页 / 今日页原型独立评审？

## 交付物

请将完整修改报告保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-007_home_today_stitch_revision_report.md`

请输出的文件内容包括：

- 任务状态与修改范围声明
- 修改前问题摘要
- 修改后页面 / 状态清单
- 模块级修改说明
- 内容身份与 AI 规则落实说明
- Stitch 未能充分表达的交互状态
- 未修改内容和原因
- 风险与待确认问题
- 是否建议进入原型独立评审

如工具允许，请在交付物中附上修改后关键画面的截图路径或说明；若无法截图，应说明原因。

篇幅控制：

- 本任务为补丁 / 条件整改型任务，建议 1500-3000 字。
- 超出当前首页 / 今日页原型修改范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 仅修改首页 / 今日页，不修改其他页面。
- 完成至少一个非运维 Project 默认恢复画面。
- 完成至少一个未选 / 空态或“暂无可靠建议”关键画面 / 状态表达。
- 完成至少一个权限受限或离线代表态关键画面 / 状态表达。
- 首页不再以 IT 运维 / Kubernetes 作为默认主叙事。
- AI 候选下一步在确认前不进入用户已安排 / 已承诺状态。
- 用户原文、外部来源、AI 整理、AI 推断 / 建议、用户确认内容有可见区分。
- 快速捕获有耐久保存 / 离线待同步 / 失败重试等诚实状态表达。
- 完整修改报告已保存到指定路径。
- 明确说明是否建议进入原型独立评审。
- 不写代码、不修改其他页面、不擅自冻结原型。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 只允许修改 Stitch 首页 / 今日页。
- 不允许修改 Stitch 的其他页面。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。
- 不擅自冻结首页 / 今日页原型。
- 不把 PRD 冻结误认为用户验证或技术 Spike 已通过。
- 不进入 Stage 2 或 MVP 开发。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整修改报告正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
