# LIFEOS-P1-006｜首页 / 今日页 PRD 冻结条件整改

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

- 任务 ID：LIFEOS-P1-006
- 任务名称：首页 / 今日页 PRD 冻结条件整改
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；辅助检查 Gate 4 技术可行性评审、Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-004` 已产出首页 / 今日页 PRD 草案，并通过 PM 验收。  
`LIFEOS-P1-005` 已完成首页 / 今日页 PRD 独立评审，结论为 `Pass with Conditions`。  
PM 已验收 P1-005，并确认首页 / 今日页 PRD 当前状态为 `Pass with Conditions`，尚未冻结。

用户已采纳 PM 建议：在修改 Stitch 或冻结首页 / 今日页 PRD 前，先启动一个有限条件整改任务，只回应独立评审提出的 M-01 至 M-04，不重写 P1-004，不扩大页面范围。

## 目标

本任务完成后，需要回答：

1. P1-005 提出的 M-01 至 M-04 是否已被逐项补齐？
2. 首页首屏信息、详情信息、异常信息的渐进披露合同是否清楚？
3. 四类命令在首页的责任边界是否收紧，是否避免变成权限 / 清理控制台？
4. Stitch 继承边界是否清楚，是否避免继承 IT 运维默认叙事？
5. 当前 Project 的来源、未选态和系统候选态是否清楚？
6. 完成整改后，是否建议 PM 冻结首页 / 今日页 PRD？

## 范围

本任务必须覆盖 P1-005 的四项必须整改项：

### M-01｜补充渐进披露合同

必须明确首页信息分三层：

- 首屏必显：用户恢复 Project 和确认下一步所必须看到的信息。
- 详情可达：为了核对证据、来源、理由、反证和输入范围而可展开查看的信息。
- 仅异常时显：权限失败、来源不可达、证据冲突、清理失败、供应商受限等异常才显著展示的信息。

必须避免把身份、权限、模型版本、审计和清理状态机全部平铺到首页首屏。

### M-02｜收紧四类命令的首页表达

必须明确首页只承担：

- 语义准确的上下文入口。
- 作用对象。
- 影响摘要。
- 完成后的最小回执。

完整范围选择、组合命令、副本保留、二次确认、清理进度和失败处理应进入详情层 / 专门流程。  
`delete_content`、扩大范围的 `revoke_processing`、断源并删除副本不得一击执行。  
`retract_feedback` 必须继续以追加历史表达。

### M-03｜限定 Stitch 继承边界

必须明确：

- 只继承当前 Stitch 的空间 / 注意力原则。
- 不继承导航广度、领域替代 Project、IT 运维 / Kubernetes 默认样例、全局任务 / 自动化状态、图片比例、视觉参数、AI 文案和现有交互。
- 后续原型至少以一个非运维 Project 为主画面。
- 后续原型至少补一个空态或无可靠建议态作为关键画面。
- 运维仅可作为普通 Project 样例，不得成为默认首页叙事。

### M-04｜明确 Project 选择来源与未选态

必须明确：

- V0.1 当前 Project 只可来自用户本次选择，或最近由用户确认的延续。
- 系统推测只能作为有依据的候选，不能静默生效。
- 页面需显示当前 Project 并可切换。
- 没有可靠 Project 时仍可捕获和手动选择，但不生成跨 Project 恢复或建议。
- Project 归属不得扩大授权。

## 非范围

本任务暂时不要做：

- 不重写 P1-004 PRD。
- 不产出新的完整首页 / 今日页 PRD。
- 不修改 Stitch。
- 不产出视觉设计稿。
- 不写代码。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不执行真实用户测试。
- 不扩展其他页面。
- 不直接冻结首页 / 今日页 PRD；只输出冻结补丁和 PM 冻结建议。
- 不扩大 V1 为全知全能 Agent。

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
- `lifeos/reviews/LIFEOS-P1-004_pm_review.md`
- `lifeos/reviews/LIFEOS-P1-005_home_today_prd_independent_review.md`
- `lifeos/reviews/LIFEOS-P1-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：体验设计负责人必须重点回答：

- 本补丁是否只关闭 M-01 至 M-04，没有重写 P1-004？
- 首页首屏是否更轻、更可理解，仍能回答“今天从哪里继续”？
- 首页是否避免变成权限 / 清理控制台、运维面板或任务墙？
- Project 选择、未选、系统候选三态是否不混淆？

协审角色必须重点检查：

- 产品架构负责人：补丁是否继承 V1 范围 V0.1，不扩大为全局任务墙、后台或全知 Agent。
- 数据 / 领域模型负责人：渐进披露和 Project 来源规则是否仍能保留 Source、Artifact、Derivation、Feedback、Authorization、AuditEntry 等语义。
- AI 信任与安全负责人：四类命令、AI 候选、证据缺口、无可靠建议和高风险边界是否保持清楚。
- 用户研究 / 市场验证负责人：补丁是否支持后续真实 / 等价中断 Project 的恢复测试，而非只优化文案。
- 技术架构负责人：补丁是否仍把未验证能力标为条件性能力，不写成上线承诺。

## 核心问题

请重点回答：

1. P1-005 的 M-01 至 M-04 是否逐项完成？
2. 首页哪些信息必须首屏必显，哪些详情可达，哪些仅异常时显？
3. 四类命令在首页的最小责任是什么？哪些必须进入详情层 / 专门流程？
4. Stitch 到底可以继承什么、不能继承什么？
5. 当前 Project 的用户选择、最近确认延续、系统候选、未选态如何区分？
6. 本补丁完成后，哪些内容建议与 P1-004 一起作为首页 / 今日页 PRD 冻结基线？
7. 哪些内容仍不应被冻结？
8. 是否建议 PM 冻结首页 / 今日页 PRD？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`

请输出的文件内容包括：

- 文档状态与补丁范围声明
- P1-005 M-01 至 M-04 逐项整改矩阵
- 首页渐进披露合同
- 四类命令首页责任边界
- Stitch 继承边界
- Project 选择来源与未选态
- 对 P1-004 的冻结补丁说明
- 建议冻结范围与不冻结范围
- 风险与待确认问题
- 是否建议 PM 冻结首页 / 今日页 PRD

篇幅控制：

- 本任务为补丁 / 条件整改型任务，建议 1500-3000 字。
- 不要重写 P1-004。
- 超出当前整改范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整交付物已保存到指定路径。
- 明确逐项回应 P1-005 的 M-01 至 M-04。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 明确说明本补丁是否建议与 P1-004 一起冻结首页 / 今日页 PRD。
- 明确说明冻结范围和不冻结范围。
- 不修改 P1-004 主交付物。
- 不修改代码、Stitch 或外部系统。
- 不擅自冻结首页 / 今日页 PRD。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。
- 不直接启动原型修改。
- 不擅自冻结首页 / 今日页 PRD、技术架构或产品原型。
- 不把技术 Spike 计划误认为已经实测通过。
- 不把用户验证合同误认为已经完成用户验证。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
