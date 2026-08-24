# LIFEOS-P1-012｜首页 / 今日页用户验证计划与测试脚本

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

- 任务 ID：LIFEOS-P1-012
- 任务名称：首页 / 今日页用户验证计划与测试脚本
- 优先级：P0
- 任务类型：研究型任务
- 建议篇幅：3000-6000 字
- 主责角色：用户研究 / 市场验证负责人
- 协审角色：产品架构负责人、体验设计负责人、数据 / 领域模型负责人、AI 信任与安全负责人
- 必须通过的评审关卡：Gate 5 用户价值验证评审；辅助检查 Gate 1 产品一致性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审
- 状态：Ready

## 背景

`LIFEOS-P1-004` 与 `LIFEOS-P1-006` 已共同冻结为首页 / 今日页 PRD V0.1。  
`LIFEOS-P1-007` 至 `LIFEOS-P1-011` 已完成首页 / 今日页 Stitch 原型修改、独立评审、有限返工、重新评审和冻结条件补丁。  
用户已确认“采纳，冻结并继续”，三张 `LifeOS 精修版` 已冻结为首页 / 今日页静态关键原型 V0.1。

冻结对象为：

- `今日 - 默认恢复态 (LifeOS 精修版)`
- `今日 - 暂无可靠建议 (LifeOS 精修版)`
- `今日 - 权限受限·离线 (LifeOS 精修版)`

注意：冻结只覆盖静态关键原型和证据链，不覆盖动态交互、响应式、可访问性、技术实现、用户验证结果、Stage 2 准入或 MVP 开发准入。

本任务的目标是设计用户验证计划和测试脚本，不执行真实用户测试。

## 目标

本任务完成后，需要形成一份可执行的用户验证计划，用于验证：

1. 用户是否能在 5-10 秒内理解 LifeOS 首页不是 IT 运维台、后台或任务墙，而是个人外脑的 Project 恢复入口。
2. 用户是否能区分用户原文、外部来源、AI 整理、AI 建议 / 未确认、用户确认内容。
3. 用户是否理解 AI 候选下一步不是已安排 / 已承诺事项。
4. 用户是否接受“暂无可靠建议”作为诚实、可继续的状态。
5. 用户是否理解权限受限 / 离线态中的原因、影响和仍可继续的动作。
6. 原型是否足以支持后续真实 / 等价中断 Project 恢复测试。

## 范围

本任务必须覆盖：

- 目标用户样本定义。
- 招募筛选条件。
- 测试场景与任务脚本。
- 5-10 秒首屏理解测试设计。
- 三张状态逐张验证问题。
- 真实 / 等价中断 Project 恢复测试设计。
- 观察指标、判定标准和反证信号。
- 记录模板。
- 访谈提纲。
- 测试材料清单。
- 风险、伦理和隐私注意事项。
- 测试后如何进入 PM 验收或下一轮原型调整的决策规则。

## 非范围

本任务暂时不要做：

- 不执行真实用户测试。
- 不招募真实用户。
- 不联系外部人员。
- 不修改 Stitch。
- 不修改 PRD。
- 不新增页面或状态。
- 不设计技术实现。
- 不进入 Stage 2。
- 不进入 MVP 开发。
- 不冻结新的产品范围、技术方案或商业指标。
- 不设置没有证据支持的留存率、付费率或增长目标。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-002_target_users_core_problems_research.md`
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P1-006_home_today_prd_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P1-009_home_today_stitch_rework_report.md`
- `lifeos/reviews/LIFEOS-P1-010_home_today_stitch_re_review.md`
- `lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`
- `lifeos/reviews/LIFEOS-P1-011_pm_review.md`
- 当前 Stitch 原型：https://stitch.withgoogle.com/projects/7778510350051176390
- 冻结截图证据：
  - `lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg`
  - `lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg`
  - `lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：用户研究 / 市场验证负责人必须重点回答：

- 这次验证要证明或推翻什么？
- 找哪些用户测，为什么是这些用户？
- 用户看到什么材料、完成什么任务、回答什么问题？
- 什么结果算通过、什么结果算需要返工、什么结果会推翻当前原型方向？
- 如何避免诱导用户、让用户只是迎合测试者？
- 如何避免把“看得懂”误判为“有真实价值”？

协审角色必须重点检查：

- 产品架构负责人：测试是否仍围绕 V1 第一用户和第一场景，不扩成泛 LifeOS 愿景测试。
- 体验设计负责人：测试是否能检验首屏理解、状态理解、内容身份和压力感。
- 数据 / 领域模型负责人：测试是否能观察用户对 Project、Source、用户原文、AI 派生、用户确认内容的理解。
- AI 信任与安全负责人：测试是否能观察 AI 建议未确认、权限受限、离线和“无建议”的信任边界。

## 核心问题

请重点回答：

1. 本轮用户验证的核心假设是什么？
2. 样本应该如何选择？
3. 5-10 秒理解测试怎么做？
4. 三张状态分别要验证什么？
5. Project 恢复测试怎么设计？
6. 如何记录用户原话、行为和误读？
7. 什么结果允许进入下一步？
8. 什么结果要求原型返工？
9. 什么结果会影响 V1 范围或首页 / 今日页 PRD？

## 交付物

请将完整用户验证计划保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-012_home_today_user_validation_plan.md`

请输出的文件内容包括：

- 任务状态与范围声明
- 验证目标
- 关键假设
- 参与者画像与筛选条件
- 测试材料
- 测试流程
- 5-10 秒理解测试脚本
- 三状态逐张测试脚本
- Project 恢复测试脚本
- 访谈提纲
- 观察指标与判定标准
- 记录模板
- 通过 / 条件通过 / 返工 / 阻塞判定规则
- 风险、伦理与隐私注意事项
- 需要 PM 决策的问题
- 后续任务建议

篇幅控制：

- 本任务为研究型任务，建议 3000-6000 字。
- 超出用户验证计划的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整交付物已保存到指定路径。
- 不执行真实用户测试。
- 明确目标用户样本与筛选条件。
- 提供可执行测试脚本。
- 覆盖三张冻结状态。
- 覆盖内容身份、AI 未确认建议、无建议、权限 / 离线、Project 恢复。
- 明确记录模板和判定标准。
- 明确哪些结果会触发原型返工、PRD 调整或范围调整。
- 明确区分事实、推断、建议和需 PM 确认事项。
- 不修改 Stitch、不修改 PRD、不进入开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不允许改变 LifeOS 产品定位。
- 不允许扩大 V1 范围。
- 不允许修改原型。
- 不允许执行真实用户测试。
- 不允许把测试计划视为用户验证已经通过。
- 不允许进入 Stage 2 或 MVP 开发。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整计划正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
