# LIFEOS-P0-005 技术可行性 Spike 计划

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

任务 ID：LIFEOS-P0-005

任务名称：技术可行性 Spike 计划

优先级：P0

任务类型：[Tech] [Data] [AI] [Architecture]

主责角色：技术架构负责人

协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、PM / 项目总负责人

必须通过的评审关卡：

- Gate 4：技术可行性评审
- Gate 2：数据与来源评审
- Gate 3：AI 权限与信任评审

状态：Ready

## 背景

LifeOS 已完成 Stage 0 的四个地基任务：

- 001：项目章程与产品宪法
- 002：目标用户与核心问题
- 003：核心领域模型前置研究
- 004：AI 权限与信任模型

当前仍未进入 PRD 和开发阶段。接下来需要把产品、数据和 AI 信任模型转化为技术可行性验证计划。

本任务不是选择最终技术栈，也不是开始写代码，而是明确：

- 哪些技术风险最大？
- 哪些假设必须 Spike？
- 每个 Spike 如何验证？
- 通过/失败标准是什么？
- 哪些结果会影响 V1 范围、PRD 或架构选择？

## 目标

产出一份技术可行性 Spike 计划，帮助 PM 判断：

- LifeOS V1 最关键的技术风险有哪些？
- 每项风险应该如何用最小 Spike 验证？
- Obsidian 只读接入、本地保存、来源追踪、权限撤回、派生失效、搜索恢复是否可行？
- 现有候选技术架构是否大体合理，哪些部分还不能冻结？
- 在进入 V1 PRD 和技术架构冻结前，必须先完成哪些验证？

## 范围

本任务必须覆盖以下 Spike 方向：

- 本地可靠落盘与离线捕获
- Obsidian Vault 只读接入
- Source / Artifact / version / Link 来源追踪
- Derivation 输入版本、授权、输出身份追踪
- Authorization 六维授权判定
- 权限撤回 / 删除后的活跃阻断与派生失效
- 向量、全文索引、缓存、队列、备份的依赖发现与清理
- 混合搜索与项目恢复包
- AI 候选 Action / Decision / Link 到用户 Feedback 的状态一致性
- 首页/今日页可信建议所需证据链返回
- 导出原文、来源、版本、确认状态、派生物和重要关系
- 本地 / 云 / 第三方模型处理边界
- 容量与性能假设：100 万内容单元、约 300 万分块、重度个人使用
- 技术复杂度控制：避免过早微服务、Kubernetes、专用图数据库、重型 Agent 框架

## 非范围

本任务暂时不要做：

- 不写业务代码
- 不修改 Stitch
- 不搭建完整工程
- 不冻结技术栈
- 不设计最终数据库表
- 不写完整 API schema
- 不选择最终云供应商
- 不创建外部账号或部署服务
- 不做完整安全合规方案
- 不写 V1 PRD
- 不把 Spike 计划当作实现排期

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/reviews/LIFEOS-P0-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/reviews/LIFEOS-P0-004_pm_review.md`

如需参考技术资料，请优先使用官方文档或一手资料，并标明链接与检索日期。不要把未经验证的博客判断当成项目事实。

## 角色检查点

主责角色必须重点回答：

- 哪些技术风险会阻塞 V1？
- 每个 Spike 的最小验证路径是什么？
- 验证成功/失败标准是什么？
- 哪些技术选择可以暂定，哪些绝不能冻结？
- 如何避免早期架构过重？

协审角色必须重点检查：

- 数据 / 领域模型负责人：Spike 是否验证 Source/Artifact、版本、Derivation、Feedback、Authorization、AuditEntry、Link 的最低语义。
- AI 信任与安全负责人：Spike 是否验证授权、撤回、派生失效、第三方模型边界和高风险限制。
- PM / 项目总负责人：Spike 是否服务 V1 第一场景和范围控制，是否会推迟或扩大项目。

## 核心问题

请重点回答：

- V1 进入开发前，必须完成哪些 Spike？
- 每个 Spike 的验证目标、方法、输入、输出和验收标准是什么？
- 哪些 Spike 可以并行，哪些有依赖？
- 哪些 Spike 失败会导致 V1 范围调整？
- Obsidian 只读接入最小可行验证是什么？
- 权限撤回和删除传播最小可行验证是什么？
- 向量、全文索引、缓存和派生物清理是否可验证？
- 混合搜索与项目恢复包的最低可行体验需要哪些技术能力？
- 当前候选技术方向 Tauri + React + SQLite + Fastify + PostgreSQL + pgvector 是否仍合理？哪些部分需要保留为待验证？
- 进入 Stage 1 / Stage 2 / Stage 3 前分别需要哪些技术门槛？

## 交付物

请将完整交付物保存为 Markdown 文件：

`lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`

文件内容建议包含：

- 执行摘要
- 角色与关卡覆盖情况
- 技术风险地图
- Spike 总览表
- 每个 Spike 的目标、假设、方法、输入、产物、验收标准、失败处理
- Spike 依赖与推荐顺序
- 资源与时间粗估
- 技术架构候选项评估
- 不应提前冻结的技术选择
- 对 V1 PRD 的影响
- 对独立评审的影响
- 需要 PM 确认的问题

## 验收标准

只有满足以下条件，任务才算完成：

- 明确列出 V1 开发前必须完成的 Spike。
- 每个 Spike 都有验证目标、验证方法、交付物和通过/失败标准。
- 明确哪些 Spike 会影响 V1 范围、PRD 或技术架构。
- 明确 Obsidian、本地保存、来源追踪、授权撤回、派生失效、搜索恢复、导出等关键风险的验证路径。
- 明确哪些技术方向可以暂定，哪些不能冻结。
- 明确避免早期重型架构的策略。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 4、Gate 2、Gate 3 是否通过。
- 完整交付物已保存到 `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`。
- 会话回复只包含摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策，不粘贴完整正文。
- 输出时使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的结构。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号。
- 不调用付费资源。
- 不冻结技术架构。
- 不冻结数据库表结构。
- 不把 Spike 计划写成开发排期。
- 不推荐 Kubernetes、微服务、Kafka、专用图数据库或重型 Agent 框架作为 V1 默认方案，除非给出强证据和替代方案比较。
- 不把“可以以后解决”用于回避权限撤回、删除传播、来源追踪和原文保护风险。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

在“交付物”部分提供完整文档路径，不要在聊天中粘贴完整正文。

## PM 提醒

本任务不是让技术架构负责人炫技，而是让项目知道哪些地雷必须先踩一遍。

P0-005 完成后，PM 将根据结果决定：

- 是否需要立即做 004 AI 权限模型独立评审
- 是否启动核心领域模型独立评审
- 是否进入 Stage 1 V1 范围冻结
- 是否需要先补技术 Spike 任务或用户验证任务
