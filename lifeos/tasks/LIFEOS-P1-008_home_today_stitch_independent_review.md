# LIFEOS-P1-008｜首页 / 今日页关键原型独立评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立评审会话，不是 PM 主会话，也不是 P1-007 执行会话。请只完成下方评审任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P1-008
- 任务名称：首页 / 今日页关键原型独立评审
- 优先级：P0
- 任务类型：评审型任务
- 建议篇幅：2000-4000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-004` 与 `LIFEOS-P1-006` 已共同冻结为首页 / 今日页 PRD V0.1。  
`LIFEOS-P1-007` 已按冻结 PRD 修改 Stitch 首页 / 今日页，并通过 PM 验收为 **Accepted but Not Frozen**。

P1-007 形成三张本次评审候选状态：

- `今日 - 默认恢复态 (LifeOS)`
- `今日 - 暂无可靠建议 (LifeOS)`
- `今日 - 权限受限·离线 (LifeOS)`

本任务是关键原型冻结前的独立评审。评审结论只能是：

- Pass
- Pass with Conditions
- Rework
- Blocked

注意：即使本任务结论为 Pass，也不代表 PM 已冻结 Stitch 原型；原型冻结仍需 PM 主会话和用户确认。

## 目标

本任务需要判断：

1. P1-007 的三张首页 / 今日页状态是否足以作为关键原型冻结候选。
2. 修改后的首页是否真正从 IT 运维 / Kubernetes 叙事回到个人终身外脑定位。
3. 用户是否能快速理解“从哪里继续”“AI 建议是否未确认”“哪些内容来自用户原文 / 外部来源 / AI 整理 / AI 推断建议 / 用户确认”。
4. 无建议、权限受限、离线和保存状态是否表达诚实、不过载、不制造失败感。
5. 原型是否可进入下一步条件整改、冻结确认或用户验证。

## 评审范围

本任务只评审以下对象：

- `lifeos/deliverables/LIFEOS-P1-007_home_today_stitch_revision_report.md`
- `lifeos/reviews/LIFEOS-P1-007_pm_review.md`
- P1-007 截图证据：
  - `lifeos/deliverables/evidence/LIFEOS-P1-007/00_three_states_overview.jpg`
  - `lifeos/deliverables/evidence/LIFEOS-P1-007/01_default_recovery.jpg`
  - `lifeos/deliverables/evidence/LIFEOS-P1-007/02_permission_offline.jpg`
  - `lifeos/deliverables/evidence/LIFEOS-P1-007/03_no_reliable_suggestion.jpg`
- 当前 Stitch 中与上述三张状态同名的首页 / 今日页画面。

若你能访问 Stitch，请只查看上述三张状态，确认画面与报告是否一致。  
若无法访问 Stitch，请基于 P1-007 报告和截图证据进行评审，并在评审中说明证据限制。

## 非范围

本任务暂时不要做：

- 不修改 Stitch。
- 不修改任何原型页面。
- 不新增页面或状态。
- 不重写 P1-007。
- 不重写首页 / 今日页 PRD。
- 不输出新的设计方案或完整改版稿。
- 不检查 Stitch 的其他页面。
- 不执行真实用户测试。
- 不执行技术 Spike。
- 不冻结原型。
- 不允许进入 Stage 2 或 MVP 开发。

如果发现需要修改的地方，请写为“必须整改项”或“条件通过项”，不要直接修改。

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
- `lifeos/deliverables/LIFEOS-P1-007_home_today_stitch_revision_report.md`
- `lifeos/reviews/LIFEOS-P1-007_pm_review.md`
- `lifeos/deliverables/evidence/LIFEOS-P1-007/`
- 当前 Stitch 原型：https://stitch.withgoogle.com/projects/7778510350051176390
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：体验设计负责人必须重点评审：

- 三张状态是否一眼回答“今天从哪里继续”。
- 页面是否安静、可核对，不像后台、监控台、全局任务墙或 IT 运维台。
- 默认恢复态是否有清楚的信息层级：当前 Project / 恢复上下文 / 一个候选下一步 / 快速捕获 / 近期变化 / 已确认安排 / 最近痕迹。
- 暂无可靠建议态是否让用户安心继续，而不是暗示系统失败。
- 权限受限 / 离线态是否诚实但不过载。
- 截图证据是否足以作为原型冻结候选评审依据，是否需要无编辑器外壳的预览截图。

协审角色必须重点检查：

- 产品架构负责人：是否继承个人终身外脑、V1 第一目标用户、V1 第一场景和首页 PRD V0.1；是否仍有 IT 运维 / 开发者工具化误读。
- 数据 / 领域模型负责人：Project、Source、Artifact、Derivation、Feedback、Authorization 等语义是否被混淆；用户原文与派生内容是否可辨。
- AI 信任与安全负责人：AI 候选是否清楚保持未确认；证据、时效、缺口、确认 / 编辑 / 拒绝 / 忽略入口是否足够；权限 / 离线降级是否不伪造建议。
- 用户研究 / 市场验证负责人：三张状态是否足以用于后续真实 / 等价中断 Project 恢复测试；是否有明显会误导测试结果的问题。

## 核心评审问题

请重点回答：

1. 三张状态是否足够覆盖 P1-007 的验收目标？
2. 首页默认主叙事是否已经摆脱 IT 运维 / Kubernetes？
3. 五类内容身份是否足够清楚：
   - 用户原文
   - 外部来源
   - AI 整理
   - AI 推断 / 建议
   - 用户确认内容
4. AI 候选下一步是否可能被误读为已安排 / 已承诺？
5. “暂无可靠建议”是否是正向、可接受、可继续操作的状态？
6. 权限受限 / 离线 / 保存状态是否诚实、不过载、不过度技术化？
7. 旧历史画面、截图外壳、静态交互限制是否影响冻结判断？
8. 是否建议进入条件整改、PM 冻结确认、用户验证或返工？

## 交付物

请将完整独立评审保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P1-008_home_today_stitch_independent_review.md`

请使用 `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md` 的结构，至少包含：

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
- 不要重写 P1-007 或 PRD；超出评审范围的建议放入“后续任务建议”或“风险”。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整评审 P1-007 三张候选状态。
- 明确给出 Pass / Pass with Conditions / Rework / Blocked 之一。
- 明确说明是否建议冻结、条件整改、返工或进入用户验证。
- 覆盖 Gate 1、Gate 2、Gate 3、Gate 5。
- 明确说明 Gate 4 是否不在本任务范围。
- 明确区分事实、推断、建议和需 PM 确认事项。
- 不修改 Stitch、不修改 PRD、不修改项目代码。
- 不擅自冻结原型。
- 完整评审文件已保存到指定路径。
- 会话回复严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径、是否需要 PM 决策。

## 限制条件

- 只做独立评审，不做执行修改。
- 只评审首页 / 今日页三张候选状态，不检查或扩展其他页面。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。
- 不进入 Stage 2 或 MVP 开发。
- 不把“静态原型表达”误认为技术能力或交互实现已完成。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评审正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
