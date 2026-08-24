# LIFEOS-P1-004｜首页 / 今日页 PRD

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/PRD_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P1-004
- 任务名称：首页 / 今日页 PRD
- 优先级：P0
- 任务类型：研究型任务
- 建议篇幅：3000-6000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；辅助检查 Gate 4 技术可行性评审、Gate 5 用户价值验证评审
- 状态：Ready

## 背景

LifeOS 已完成 Stage 0 底层定义，并已将 `LIFEOS-P1-001 + LIFEOS-P1-003` 冻结为 V1 范围 V0.1 产品范围与条件合同。

首页 / 今日页是 V1 第一场景的核心入口：用户在开工、午后恢复、跨项目切换、离开数日后返回或收到新反馈后，需要快速回答“今天从哪里继续”。

当前已有 Stitch 高保真原型：

https://stitch.withgoogle.com/projects/7778510350051176390

本任务可以读取并参考当前 Stitch 首页 / 今日页原型，但不得修改 Stitch，不得检查或扩展其他页面。

## 目标

本任务完成后，需要产出首页 / 今日页 PRD 草案，回答：

1. 首页 / 今日页在 V1 中服务什么用户目标？
2. 首页 / 今日页应包含哪些模块、信息和状态？
3. 如何让页面回答“今天从哪里继续”，而不是变成任务墙、后台或 IT 运维面板？
4. 如何区分用户原文、用户确认内容、AI 生成内容、AI 推断 / 建议和外部引用来源？
5. 用户如何确认、忽略、纠正、撤回和反馈 AI 建议？
6. 首页 / 今日页需要哪些空状态、错误态、权限态、离线态、证据不足态和响应式状态？
7. 当前 Stitch 首页哪些内容可继承，哪些必须调整或移出？

## 范围

本任务必须覆盖：

- 首页 / 今日页的产品定位与用户目标。
- 首页 / 今日页的核心使用场景和触发时机。
- 页面模块清单与信息层级。
- Project 恢复入口、近期有意义变化、候选重点 / 下一步、快速捕获的需求边界。
- 首页中用户原文、外部来源、AI 整理、AI 推断、AI 建议、用户确认状态的区分规则。
- AI 建议的来源、理由、时效、证据缺口、确认状态和反馈入口。
- 确认、忽略、纠正、完成、延期、撤回等用户动作。
- 四类命令在首页 / 今日页中的最低表达要求：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback`。
- 首页 / 今日页的交互状态：默认态、空状态、加载态、错误态、离线态、权限不足态、AI 生成中、AI 结果待确认、用户已确认、用户已驳回、来源不可达、证据不足、无可靠建议。
- 响应式要求：桌面优先、窄屏、移动端或窗口缩放的布局原则。
- 当前 Stitch 首页 / 今日页原型的继承项与调整项。
- 验收标准、指标、风险和开放问题。

## 非范围

本任务暂时不要做：

- 不修改 Stitch。
- 不产出视觉设计稿。
- 不写代码。
- 不设计数据库、API 或技术架构。
- 不执行技术 Spike。
- 不执行真实用户测试。
- 不扩展其他页面。
- 不把首页 / 今日页做成企业后台、IT 运维台、KPI 面板或全局任务墙。
- 不扩大 V1 为全知全能 Agent。
- 不冻结首页 / 今日页 PRD；本任务只产出 PRD 草案，后续仍需 PM 验收和必要独立评审。

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
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/reviews/LIFEOS-P1-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/PRD_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 当前 Stitch 原型首页 / 今日页：https://stitch.withgoogle.com/projects/7778510350051176390

## 角色检查点

主责角色：体验设计负责人必须重点回答：

- 用户进入首页后是否能快速理解“今天从哪里继续”？
- 页面是否避免焦虑式堆叠、后台感、IT 运维感和任务墙化？
- 原文、来源、AI 整理、AI 推断 / 建议、用户确认状态是否一眼可区分？
- 用户是否能确认、忽略、纠正、撤回和追溯来源？
- 空状态、无可靠建议、证据不足、权限受限和离线状态是否清楚？

协审角色必须重点检查：

- 产品架构负责人：首页是否继承 V1 范围 V0.1，不扩大为全知全能 Agent 或企业后台。
- 数据 / 领域模型负责人：首页模块是否能对应 Project、Source、Artifact、Derivation、Feedback、Authorization、AuditEntry、Action、Decision、Event、Link 等语义。
- AI 信任与安全负责人：AI 输出身份、证据、确认、纠正、撤回、权限和高风险边界是否清楚。
- 用户研究 / 市场验证负责人：PRD 是否支持后续真实项目恢复测试，而不是只定义美观页面。
- 技术架构负责人：需求是否明确条件性能力，不把未通过 Spike 的能力写成已实现承诺。

## 核心问题

请重点回答：

1. 首页 / 今日页的一句话 PRD 定义是什么？
2. 首页 / 今日页的核心用户目标是什么？
3. 页面必须包含哪些模块？每个模块服务什么用户目标？
4. 当前 Stitch 首页哪些模块可以保留、哪些需要调整、哪些应移出？
5. 如何表达 Project 恢复、近期变化、候选重点 / 下一步和快速捕获？
6. 如何清楚区分用户原文、AI 生成内容、AI 推断 / 建议、外部引用来源和用户确认内容？
7. AI 建议必须呈现哪些证据、理由、时效、状态和操作？
8. 首页 / 今日页需要哪些交互状态和响应式状态？
9. 首页 / 今日页如何避免 IT 运维占比过高？
10. 本 PRD 哪些内容仍需 PM 确认或后续独立评审？

## 交付物

请将完整 PRD 草案保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`

请输出的文件内容包括：

- 文档信息
- 背景
- 用户与场景
- 用户目标
- 产品目标
- 范围
- 非范围
- 核心流程
- 信息结构
- 当前 Stitch 继承 / 调整 / 移出清单
- AI 规则
- 数据与权限
- 交互状态
- 响应式要求
- 验收标准
- 指标
- 风险与开放问题
- 是否建议进入首页 / 今日页独立评审

篇幅控制：

- 本任务为研究型任务，建议 3000-6000 字。
- 超出当前首页 / 今日页 PRD 范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整 PRD 草案已保存到指定路径。
- 明确继承 V1 范围 V0.1。
- 明确区分用户原文、外部来源、AI 整理、AI 推断 / 建议和用户确认内容。
- 明确列出页面模块、用户目标、信息层级、交互状态和响应式状态。
- 明确处理当前 Stitch 首页的 IT 运维占比问题。
- 明确说明哪些是条件性需求，依赖哪些 Spike 或后续验证。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 不修改代码、Stitch 或外部系统。
- 不扩展其他页面。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。
- 不擅自冻结首页 / 今日页 PRD。
- 不把技术 Spike 计划误认为已经实测通过。
- 不把用户验证合同误认为已经完成用户验证。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整 PRD 正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
