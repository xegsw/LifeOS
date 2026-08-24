# LIFEOS-P1-005｜首页 / 今日页 PRD 独立评审

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

- 任务 ID：LIFEOS-P1-005
- 任务名称：首页 / 今日页 PRD 独立评审
- 优先级：P0
- 任务类型：评审型任务
- 建议篇幅：2000-4000 字
- 主责角色：体验设计负责人
- 协审角色：产品架构负责人、数据 / 领域模型负责人、AI 信任与安全负责人、用户研究 / 市场验证负责人、技术架构负责人
- 必须通过的评审关卡：Gate 1 产品一致性评审；Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；辅助检查 Gate 4 技术可行性评审、Gate 5 用户价值验证评审
- 状态：Ready

## 背景

`LIFEOS-P1-004` 已产出首页 / 今日页 PRD 草案，并通过 PM 验收，当前任务状态为 Accepted。  
但首页 / 今日页 PRD 属于关键冻结事项，根据 LifeOS 项目规则，正式冻结前必须完成独立评审。

本任务只评审 P1-004 是否适合作为首页 / 今日页 PRD 冻结基线，不重写 PRD，不修改 Stitch，不扩展其他页面。

## 目标

本任务完成后，需要回答：

1. P1-004 是否适合进入首页 / 今日页 PRD 冻结流程？
2. 首页 / 今日页是否真正回答“今天从哪里继续”？
3. PRD 是否继承 V1 范围 V0.1、核心领域模型 V0.1 和 AI 权限与信任模型 V0.1？
4. PRD 是否足以指导后续 Stitch 首页原型修改，但又没有提前冻结视觉和交互实现？
5. 如果不能直接冻结，冻结前必须补哪些条件？

## 范围

本任务必须覆盖：

- 对 P1-004 一句话定义、用户目标和产品目标的评审。
- 对首页模块、信息优先级和核心流程的评审。
- 对“Project 恢复主角 + 候选下一步 + 快速捕获”的信息结构评审。
- 对当前 Stitch 继承 / 调整 / 移出清单的评审，特别是 IT 运维占比问题。
- 对用户原文、外部来源、AI 整理、AI 推断 / 建议、用户确认内容区分规则的评审。
- 对 AI 建议的证据、理由、时效、缺口、确认状态和反馈入口的评审。
- 对四类命令在首页最低表达的评审：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback`。
- 对默认态、空态、加载态、错误态、离线态、权限不足态、AI 生成中、AI 待确认、用户确认 / 驳回、来源不可达、证据不足、无可靠建议等状态的评审。
- 对桌面优先、窄屏和移动端可阅读降级的响应式要求评审。
- 对 PRD 验收标准、指标和验证合同的评审。

## 非范围

本任务暂时不要做：

- 不重写 P1-004 PRD。
- 不产出新的首页 / 今日页 PRD。
- 不修改 Stitch。
- 不产出视觉设计稿。
- 不写代码。
- 不设计数据库、API、技术架构或工程排期。
- 不执行技术 Spike。
- 不执行真实用户测试。
- 不扩展其他页面。
- 不直接冻结首页 / 今日页 PRD；只输出独立评审结论和冻结建议。
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
- `lifeos/deliverables/LIFEOS-P1-001_v1_scope_freeze_draft.md`
- `lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 当前 Stitch 原型首页 / 今日页：https://stitch.withgoogle.com/projects/7778510350051176390

## 角色检查点

主责角色：体验设计负责人必须重点回答：

- 首页是否真的以最小信息量回答“今天从哪里继续”？
- 页面是否避免焦虑式堆叠、后台感、IT 运维感和任务墙化？
- 内容身份、来源、AI 建议、用户确认状态是否一眼可区分？
- 空状态、无可靠建议、证据不足、权限受限、离线状态是否清楚且不误导？
- 响应式要求是否足以支撑桌面优先，同时不误承诺完整移动端？

协审角色必须重点检查：

- 产品架构负责人：PRD 是否继承 V1 范围 V0.1，不扩大为企业后台、全局任务墙或全知 Agent。
- 数据 / 领域模型负责人：页面模块是否能正确映射 Project、Source、Artifact、Derivation、Feedback、Authorization、AuditEntry、Action、Decision、Event、Link 等语义。
- AI 信任与安全负责人：AI 输出身份、证据、确认、纠正、撤回、权限和高风险边界是否清楚；四类命令是否被误用。
- 用户研究 / 市场验证负责人：PRD 是否能支持真实 / 等价中断 Project 的恢复测试，是否有可观察的价值和反证。
- 技术架构负责人：条件性能力是否标注 Spike 依赖与失败降级，是否避免把未验证能力写成上线承诺。

## 核心问题

请重点回答：

1. P1-004 是否建议冻结？如果不建议，原因是什么？
2. 首页 / 今日页是否真正服务 V1 第一场景和价值排序？
3. 页面模块和信息优先级是否过重、过轻或顺序不当？
4. “一个主候选下一步”是否合理？是否需要更强调“可无可靠建议”？
5. 内容身份区分是否足够可理解，是否会造成标签、权限和状态信息过载？
6. 四类命令是否适合在首页出现，还是应只保留入口和影响预览？
7. 当前 Stitch 继承项是否仍可能保留运维 / 后台感？
8. 响应式要求是否清楚，是否误承诺完整移动端？
9. 哪些内容必须在冻结前整改？
10. 哪些内容可留到原型修改、用户验证或技术 Spike？

## 交付物

请将完整评审交付物保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P1-005_home_today_prd_independent_review.md`

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
- 不要重写 P1-004。
- 超出当前评审范围的内容，请放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整评审文件已保存到指定路径。
- 评审结论明确为 Pass / Pass with Conditions / Rework / Blocked 之一。
- 明确说明首页 / 今日页 PRD 是否建议冻结，以及冻结前条件。
- 明确检查产品一致性、数据与来源、AI 权限与信任、交互状态、响应式要求和 Stitch 调整方向。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
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

注意：会话回复不要粘贴完整评审正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
