# LIFEOS-P0-003 核心领域模型前置研究

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P0-003
- 任务名称：核心领域模型前置研究
- 优先级：P0
- 任务类型：[Data] [Product] [Architecture]
- 状态：Ready

## 背景

`LIFEOS-P0-001` 已确认项目章程与产品宪法。`LIFEOS-P0-002` 已确认 V1 第一目标用户、第一场景和外部来源边界。

当前关键决策包括：

- LifeOS 是由用户掌控、可追溯、可迁移的个人终身外脑。
- V1 第一目标用户是技术型独立产品构建者，但 LifeOS 不改变为开发者工具定位。
- V1 第一场景是“开工/切换项目时的 5 分钟上下文恢复与下一步确认”。
- V1 第一价值排序是“找回上下文 > 下一步/减少遗漏 > 今日重点”。
- V1 外部来源最低接入深度是文本、链接、文件、来源指针，暂不追求全量连接器。
- Obsidian Vault 可作为 V1 优先支持的本地文件型来源，采用只读接入、来源追踪、AI 派生不写回原文的策略。
- 产品必须区分用户原文、用户确认事实、AI 整理/生成、AI 推断、AI 建议、外部来源。
- V1 AI 主动性主体限制在 L0-L2；L3 仅允许小范围、明确授权、可逆的内部动作；L4-L5 不进入 V1 自动执行。

本任务要把这些产品与信任要求翻译成核心领域模型。注意：这是领域模型前置研究，不是数据库表设计。

## 目标

产出一份核心领域模型前置研究报告，帮助 PM 判断：

- LifeOS 最小但完整的核心对象是什么？
- 哪些对象必须作为独立概念，哪些可以作为属性、状态或关系？
- 如何表达原始记录、外部来源、项目上下文、决定、行动、事件、AI 派生、用户反馈和权限边界？
- 如何支撑“项目恢复”和“下一步确认”的 V1 第一场景？
- 如何避免模型退化成普通笔记/任务系统或开发者工具模型？
- 哪些模型问题必须在 V1 PRD 或技术 Spike 前确认？

## 范围

本任务必须覆盖：

- 核心领域对象候选清单
- 至少包含并分析这些语义：`Project`、`Action`、`Decision`、`Source/Artifact`、`Event`、`Derivation`、`Feedback`
- 用户原文、用户确认事实、AI 派生、AI 推断/建议、外部来源的模型表达
- Obsidian Vault 只读接入下的来源与内容表达
- 项目恢复场景中的对象关系
- 下一步确认场景中的对象关系
- 内容生命周期：创建、导入、整理、确认、纠正、失效、删除、导出
- AI 派生生命周期：生成、引用来源、用户确认/拒绝/纠正、失效、重建
- 行动生命周期：候选、待确认、已确认、进行中、完成、延期、取消、被替代
- 决定生命周期：提出、确认、被引用、被修订、被替代、失效
- 来源追踪与最小审计语义
- 权限与处理边界的领域表达
- 对后续 AI 权限模型、技术架构、首页/今日页 PRD 的影响

## 非范围

本任务暂时不要做：

- 不设计数据库表结构
- 不写 SQL、ORM、GraphQL schema 或 API schema
- 不冻结具体技术实现
- 不选择图数据库、关系数据库或向量数据库
- 不修改代码
- 不修改 Stitch 原型
- 不设计 UI
- 不写完整 V1 PRD
- 不做复杂企业权限模型
- 不把 GitHub、IDE、运维系统或团队工单作为核心模型中心

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-001_project_charter_product_constitution.md`
- `lifeos/reviews/LIFEOS-P0-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-002_target_users_core_problems_research.md`
- `lifeos/reviews/LIFEOS-P0-002_pm_review.md`

如果使用外部资料，请标明来源链接和检索日期。不要把外部资料当作 LifeOS 已验证事实。

## 核心问题

请重点回答：

- LifeOS 的最小核心领域对象应该有哪些？
- `Project` 是核心边界对象吗？它与 Area、Goal、Topic、Task 的关系是什么？
- `Source` 和 `Artifact` 应该是一个概念还是两个概念？
- 用户原始记录、Obsidian 笔记、网页链接、上传文件、AI 对话摘录应如何统一表达？
- `Decision` 是否应该作为独立对象？如果是，它如何连接来源、行动和项目？
- `Action`、`Commitment`、`Next Step` 是一个对象的不同类型/状态，还是不同对象？
- `Event` 表达发生时间、记录时间、项目变化和外部事件时应如何设计？
- `Derivation` 如何表达 AI 摘要、分类、关联、推断、建议和向量/索引等派生产物？
- `Feedback` 如何表达用户确认、纠正、拒绝、完成、延期和评价？
- 如何让 AI 建议永远不覆盖用户原文？
- 如何表达派生产物可重建？
- 如何表达来源权限、模型处理权限、本地/云端处理边界？
- 如何支持“开工/切换项目时恢复上下文”？
- 如何支持“从原文到下一步，再到结果反馈”的链路？

## 交付物

请将完整交付物保存为 Markdown 文件：

`lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`

文件内容建议包含：

- 执行摘要
- 领域模型设计原则
- 核心对象候选清单
- 推荐核心对象模型
- 对象定义表
- 对象关系说明
- 关键生命周期
- 内容身份与来源追踪模型
- AI 派生与反馈模型
- Obsidian Vault 只读接入模型
- V1 第一场景对象流
- 最小审计与权限语义
- 不建议进入 V1 的模型复杂度
- 对 AI 权限模型的影响
- 对技术架构的影响
- 对首页/今日页 PRD 的影响
- 待 PM 确认问题

## 验收标准

只有满足以下条件，任务才算完成：

- 明确推荐最小核心领域对象集合。
- 明确哪些概念是对象、属性、状态或关系。
- 明确表达 `Project`、`Action`、`Decision`、`Source/Artifact`、`Event`、`Derivation`、`Feedback` 等语义。
- 明确用户原文、AI 派生、AI 推断/建议、外部来源的模型边界。
- 明确 Obsidian Vault 只读接入如何进入来源和内容模型。
- 明确至少 3 条生命周期：内容、AI 派生、行动/决定。
- 明确如何支撑 V1 第一场景“开工/切换项目时的 5 分钟上下文恢复与下一步确认”。
- 明确模型如何避免滑向企业项目管理、IT 运维或开发者工具。
- 明确区分事实、推断、建议和待 PM 确认问题。
- 完整交付物已保存到 `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`。
- 会话回复只包含摘要、交付物路径、是否需要 PM 决策，不粘贴完整正文。
- 输出时使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的结构。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号。
- 不调用付费资源。
- 不自行冻结数据库表结构或技术选型。
- 不把技术型独立构建者误解为“开发者工具用户”。
- 不把 Obsidian 接入设计为自动写回或双向同步。
- 不把 GitHub、IDE、部署、工单或运维系统作为核心模型中心。
- 不输出泛泛的“万物皆节点”图谱设想，必须服务 V1 第一场景和产品宪法。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

在“交付物”部分提供完整文档路径，不要在聊天中粘贴完整正文。

## PM 提醒

本任务的核心不是画一个宏大的知识图谱，而是定义一个足以支撑 V1 闭环、来源可信、AI 可纠正、后续可扩展的最小领域模型。

如果某个概念是否应独立成对象无法确定，请给出推荐、理由、备选方案和对 V1 的影响。
