# LIFEOS-P0-007｜AI 权限与信任模型条件整改 / 冻结补充

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P0-007
- 任务名称：AI 权限与信任模型条件整改 / 冻结补充
- 优先级：P0
- 任务类型：AI Trust & Safety / Remediation Addendum
- 主责角色：AI 信任与安全负责人
- 协审角色：数据 / 领域模型负责人、技术架构负责人、产品架构负责人
- 必须通过的评审关卡：Gate 3 AI 权限与信任评审；辅助检查 Gate 2 数据与来源评审、Gate 4 技术可行性评审、Gate 1 产品一致性评审
- 状态：Ready

## 背景

`LIFEOS-P0-004` 已被 PM 接受为 AI 权限与信任模型工作版本，但尚未冻结。`LIFEOS-P0-006` 独立评审给出 `Pass with Conditions` 结论：P0-004 骨架有效，但在冻结为 V0.1 原则与语义基线前，必须补齐 M-01 至 M-06。

本任务不是推倒重写 P0-004，也不是做完整 PRD 或技术实现，而是产出一份可被 PM 验收的“冻结补充规范”，用于修正 P0-004 的条件缺口，并明确哪些内容可冻结、哪些仍需等待 Spike / PRD / 用户验证。

## 目标

本任务完成后，需要回答：

1. P0-006 提出的 M-01 至 M-06 是否已被逐项补齐？
2. AI 权限模型如何采用“六维 Authorization 核心 + 强制政策包络”？
3. `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 四类命令的效果矩阵是什么？
4. L3 候选白名单的冻结边界是什么？哪些情况下必须降级为 L1 Derivation 展示？
5. 审计、日志、遥测如何做到最小化且防止反向识别？
6. 第三方处理者发送前资格门槛是什么？哪些情况必须 fail closed？
7. SP-04 至 SP-08 需要补充哪些验收要求？
8. 条件整改后，P0-004 能否建议冻结为 V0.1 原则与语义基线？

## 范围

本任务必须覆盖：

- P0-006 的 M-01：Authorization 强制政策包络。
- P0-006 的 M-02：四类撤回 / 删除命令及效果矩阵。
- P0-006 的 M-03：L3 冻结范围限定为候选上限。
- P0-006 的 M-04：审计隐私规范。
- P0-006 的 M-05：第三方发送前资格门槛。
- P0-006 的 M-06：SP-04、SP-05、SP-06、SP-07、SP-08 的补充验收缺口。
- 明确冻结范围：只能建议冻结 V0.1 原则与语义基线，不冻结具体实现、删除 SLA、供应商能力、授权 UI 或 L3 上线范围。
- 明确哪些内容仍需后续 PRD、Spike 或用户验证。

## 非范围

本任务暂时不要做：

- 不重写 `LIFEOS-P0-004` 原文件。
- 不直接修改 `LIFEOS-P0-005` Spike 计划原文件。
- 不执行技术 Spike。
- 不设计完整 PRD、设置页、授权 UI 或今日页交互。
- 不设计最终数据库表、API、模型网关实现或供应商清单。
- 不修改代码。
- 不修改 Stitch。
- 不选择云供应商或模型供应商。
- 不把任何 L3 能力写成 V1 默认上线能力。
- 不宣称 P0-004 已冻结；冻结决策由 PM 主会话完成。

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
- `lifeos/reviews/LIFEOS-P0-006_ai_trust_independent_review.md`
- `lifeos/reviews/LIFEOS-P0-006_pm_review.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：AI 信任与安全负责人必须重点回答：

- 授权判定是否同时满足六维 Authorization 与强制政策包络？
- 第三方处理者不合格时是否 fail closed？
- AI 输出、派生、建议、候选对象和用户确认是否仍清楚区分？
- L3 是否被严格限制为候选上限？
- 用户撤回、删除、断开、反馈撤回是否有清晰可执行语义？
- 审计是否能解释事故，同时不成为新的隐私泄露源？

协审角色必须重点检查：

数据 / 领域模型负责人：

- 四类命令是否能映射到 Source、Artifact、Derivation、Feedback、Authorization、AuditEntry、Link、Action、Decision、Assertion。
- 用户确认对象、证据失效、删除、撤回和导出之间是否存在语义冲突。
- Derivation 限制继承、跨 Project 传播和导出不复活是否表达清楚。

技术架构负责人：

- SP-04 至 SP-08 的补充验收要求是否可验证。
- 是否避免把“规范好看”误认为“技术已通过”。
- 是否明确哪些内容必须等待 SP-04 / SP-05 / SP-06 / SP-07 / SP-08 实测。

产品架构负责人：

- 补充规则是否仍服务个人终身外脑，不滑向企业权限后台。
- 是否避免把长期全自动愿景提前塞进 V1。
- 哪些规则需要在 Stage 1 PRD / 原型中转译为用户可理解的体验。

## 核心问题

请重点回答：

1. 六维 Authorization 与强制政策包络如何组合判定？给出最小规则表。
2. 强制政策包络至少包含哪些字段或门槛？哪些是硬拒绝？
3. 四类命令分别如何影响原文、来源指针、可识别快照、Derivation、索引/向量/缓存、用户确认对象、审计、备份、离线设备、第三方副本？
4. 用户已确认的 Action / Decision / Assertion 在证据撤回或删除后如何处理？
5. L3 候选白名单的上限、不变量、降级条件和后续进入 V1 的前置条件是什么？
6. 审计允许记录什么，不允许记录什么？如何降低路径、时间、对象 ID、错误详情组合造成的反向识别？
7. 第三方发送前资格门槛是什么？政策未知、政策变更、训练/评估默认开启、删除能力不足、高敏内容分别如何处理？
8. Derivation 如何继承输入限制？跨 Project 展示、保存、再派生如何重新判定？
9. SP-04 至 SP-08 分别需要补充哪些验收项？
10. 条件整改后，是否建议 PM 将 P0-004 冻结为 V0.1 原则与语义基线？请说明冻结范围和仍未冻结内容。

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`

请输出的文件内容包括：

- 文档状态与范围声明
- 对 P0-006 M-01 至 M-06 的逐项回应
- 六维 Authorization + 强制政策包络规则
- 四类命令效果矩阵
- L3 候选白名单冻结边界与降级规则
- 审计隐私规范
- 第三方发送前资格门槛
- Derivation 限制继承与跨 Project 传播规则
- SP-04 至 SP-08 补充验收清单
- 可冻结内容
- 仍需等待 Spike / PRD / 用户验证的内容
- 风险与待确认问题
- 是否建议 PM 冻结 P0-004 为 V0.1 原则与语义基线

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整交付物已保存到指定路径。
- 明确逐项覆盖 M-01 至 M-06。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 明确说明 Gate 3 是否可通过，Gate 2 / Gate 4 / Gate 1 是否存在条件。
- 不重写主交付物原文件。
- 不修改代码、Stitch 或外部系统。
- 不把 Spike 计划当作已实测。
- 不擅自冻结 P0-004；只提出是否建议冻结及冻结范围。
- 会话回复只输出摘要和交付物路径。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、AI 权限模型或数据模型。
- 不扩大 V1 AI 主动性边界。
- 不把长期愿景中的全自动 Agent 能力提前纳入 V1。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、阻塞或异常说明。
