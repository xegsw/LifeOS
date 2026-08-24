# LIFEOS-P0-004 AI 权限与信任模型

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

任务 ID：LIFEOS-P0-004

任务名称：AI 权限与信任模型

优先级：P0

任务类型：[AI] [Product] [Data] [Safety]

主责角色：AI 信任与安全负责人

协审角色：数据 / 领域模型负责人、产品架构负责人

必须通过的评审关卡：

- Gate 3：AI 权限与信任评审
- Gate 2：数据与来源评审
- Gate 1：产品一致性评审

状态：Ready

## 背景

LifeOS 已完成 001、002、003：

- 001 确认了项目章程、产品宪法和 AI 不得静默改写用户原文等底线。
- 002 确认了 V1 第一目标用户、第一场景、Obsidian 只读来源和外部来源边界。
- 003 产出了核心领域语义工作模型，包括 `Artifact`、`Source`、`Derivation`、`Feedback`、`Authorization`、`AuditEntry` 等。

当前关键问题是：AI 在 LifeOS 中到底可以读取什么、生成什么、主动到什么程度、什么时候必须用户确认、用户纠正后如何生效、权限撤回后派生物如何处理。

如果这个模型不清楚，后续 PRD、技术 Spike、首页/今日页和 Obsidian 接入都会摇摆。

## 目标

产出一份 AI 权限与信任模型报告，帮助 PM 判断：

- V1 AI 能做什么、不能做什么？
- AI 使用数据的授权边界是什么？
- AI 输出如何区分整理、生成、推断、建议、候选行动？
- 哪些 AI 输出可以自动出现，哪些必须用户确认？
- 用户如何确认、拒绝、纠正、撤回？
- 权限撤回、来源删除、原文变化后，派生物、缓存、索引和审计如何处理？
- 高风险场景如何限制？
- 首页/今日页如何可信地展示 AI 建议？

## 范围

本任务必须覆盖：

- AI 主动性 L0-L5 的 V1 适用规则
- V1 允许的 AI 能力清单
- V1 禁止的 AI 能力清单
- `Authorization` 的授权维度：主体、范围、动作、目的、位置、时效
- `Derivation` 的输入、输出、证据、状态、失效和重建规则
- `Feedback` 的确认、拒绝、纠正、忽略、完成、延期、撤回规则
- AI 输出内容身份：整理/生成、推断、建议、候选行动、候选决定、候选关系
- 用户原文、用户确认事实、AI 推断、AI 建议、外部来源之间的转换规则
- 权限撤回后的派生物、缓存、索引、历史审计处理方向
- Obsidian Vault 只读来源下，AI 可读取、索引、摘要和建议的权限边界
- 首页/今日页中 AI 建议的最低可信展示要求
- 高风险场景边界：心理、医疗、法律、财务等
- 需要独立评审前不能冻结的事项

## 非范围

本任务暂时不要做：

- 不写 V1 PRD
- 不设计页面 UI
- 不修改 Stitch
- 不修改代码
- 不设计数据库表
- 不冻结模型供应商或技术架构
- 不设计完整企业权限系统
- 不允许 AI 自动对外发送消息、付款、改重要日程、删除重要数据或自动执行高风险建议
- 不把长期 Agent 自动执行作为 V1 能力

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-001_project_charter_product_constitution.md`
- `lifeos/reviews/LIFEOS-P0-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-002_target_users_core_problems_research.md`
- `lifeos/reviews/LIFEOS-P0-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/reviews/LIFEOS-P0-003_pm_review.md`

如果使用外部资料，请标明来源链接和检索日期。不要把外部资料当作 LifeOS 已验证事实。

## 角色检查点

主责角色必须重点回答：

- AI 在 V1 中可以读取、生成、建议和创建什么？
- AI 何时必须停止、请求确认或降低主动性？
- AI 输出错了以后，用户如何看见、纠正、撤回或让其失效？
- 权限撤回、删除和来源失效后，AI 派生物如何处理？
- 高风险场景如何限制？

协审角色必须重点检查：

- 数据 / 领域模型负责人：是否正确使用 `Authorization`、`Derivation`、`Feedback`、`AuditEntry`、`Source`、`Artifact`、`Assertion`、`Decision`、`Action` 等语义。
- 产品架构负责人：是否仍然服务 V1 第一场景和个人终身外脑定位，是否避免把 AI 做成自动执行代理或企业后台。

## 核心问题

请重点回答：

- V1 AI 能力上限到底是什么？
- L0、L1、L2、L3 在 LifeOS 中分别对应哪些真实行为？
- 哪些 L3 小范围内部动作可以进入 V1 候选？哪些必须排除？
- AI 生成摘要、分类、候选项目归属、候选下一步、候选决定、候选关系时，分别需要什么证据和状态？
- AI 推断如何变成用户确认事实？用户确认后是否保留 AI 来源历史？
- AI 候选 Action 如何变成用户确认 Action？
- AI 候选 Decision 如何变成用户确认 Decision？
- 用户纠正 AI 后，系统应该记住什么、不应该自动泛化什么？
- 权限撤回后，摘要、向量、索引、缓存、历史 Derivation 和 AuditEntry 怎么处理？
- Obsidian Vault 只读接入时，哪些处理可以默认本地，哪些需要明确授权，哪些不能发给第三方模型？
- 首页/今日页展示 AI 建议时，最低需要显示哪些来源、理由、不确定性和确认入口？

## 交付物

请将完整交付物保存为 Markdown 文件：

`lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`

文件内容建议包含：

- 执行摘要
- 角色与关卡覆盖情况
- AI 信任原则
- AI 主动性 L0-L5 规则
- V1 允许能力清单
- V1 禁止能力清单
- Authorization 授权模型
- Derivation 派生模型
- Feedback 反馈模型
- AI 输出身份与状态规则
- 从 AI 候选到用户确认的转换规则
- 权限撤回、删除、来源失效后的处理规则
- Obsidian 只读来源的 AI 权限边界
- 首页/今日页 AI 建议展示要求
- 高风险场景边界
- 对技术 Spike 的影响
- 对 V1 PRD 的影响
- 对独立评审的建议
- 待 PM 确认问题

## 验收标准

只有满足以下条件，任务才算完成：

- 明确 V1 AI 允许能力和禁止能力。
- 明确 L0-L5 在 LifeOS 中的行为边界。
- 明确 `Authorization`、`Derivation`、`Feedback`、`AuditEntry` 的使用规则。
- 明确 AI 输出身份与状态，不混淆用户原文、用户确认事实、AI 推断、AI 建议和外部来源。
- 明确 AI 候选 Action / Decision 如何转为用户确认。
- 明确权限撤回、来源失效、删除后的派生物、缓存、索引和审计处理方向。
- 明确 Obsidian Vault 只读接入下的 AI 处理权限。
- 明确首页/今日页 AI 建议的可信展示要求。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 3、Gate 2、Gate 1 是否通过。
- 完整交付物已保存到 `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`。
- 会话回复只包含摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策，不粘贴完整正文。
- 输出时使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的结构。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号。
- 不调用付费资源。
- 不冻结技术架构。
- 不冻结 V1 PRD。
- 不设计完整企业权限系统。
- 不扩大 V1 AI 主动性边界。
- 不允许 AI 自动执行 L4-L5。
- 不把“用户授权过一次”作为所有未来重大操作的默认许可。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

在“交付物”部分提供完整文档路径，不要在聊天中粘贴完整正文。

## PM 提醒

本任务可以被 PM 验收为 Accepted，但 AI 权限与信任模型属于关键冻结事项。正式冻结前必须另开独立评审会话，使用 `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`。

本任务的核心不是让 AI 做更多，而是让 AI 在用户掌控、来源可追溯、错误可纠正、权限可撤回的前提下，做少而可信的事情。
