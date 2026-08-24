# LIFEOS-P0-009｜核心领域模型条件整改 / 冻结补丁

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/TASK_BRIEF_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方补丁任务，不要自行扩大范围，不要重写 P0-003，不要修改代码、Stitch 或外部系统。

## 任务信息

- 任务 ID：LIFEOS-P0-009
- 任务名称：核心领域模型条件整改 / 冻结补丁
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字
- 主责角色：数据 / 领域模型负责人
- 协审角色：AI 信任与安全负责人、技术架构负责人、产品架构负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审；辅助检查 Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审、Gate 1 产品一致性评审
- 状态：Ready

## 背景

`LIFEOS-P0-003` 已被 PM 接受为核心领域模型工作版本。`LIFEOS-P0-008` 独立评审结论为 `Pass with Conditions`：11 个对象 + `Link` 的语义骨架足够，不需要新增、合并、拆分或改名；但 P0-003 当前文本早于已冻结的 AI 权限与信任模型 V0.1 基线，因此必须补齐 M-01 至 M-05 后，才能由 PM 判断是否冻结为核心领域模型 V0.1 语义基线。

本任务是轻量补丁 / 条件整改型任务，不是研究型任务，不重写 P0-003，不设计数据库、API 或 UI。

## 目标

本任务完成后，需要回答：

1. P0-008 提出的 M-01 至 M-05 是否已被逐项补齐？
2. P0-003 如何以最小语义补丁承接 P0-007 已冻结的 AI 权限与信任基线？
3. 补丁完成后，是否建议 PM 将 `P0-003 + P0-009` 共同冻结为核心领域模型 V0.1 语义基线？

## 范围

本任务必须覆盖：

- M-01：四类命令的最低领域效果矩阵。
- M-02：Derivation 约束继承合同。
- M-03：分离来源身份、用户认可、业务状态、证据状态与派生状态。
- M-04：墓碑优先与导出不复活不变量。
- M-05：AuditEntry 语义收紧与防反向识别。
- 明确补丁不新增核心对象，不改名，不删除对象。
- 明确补丁不冻结 Schema、API、UI、存储、事件流、L3 上线范围、删除 SLA、供应商或技术架构。

## 非范围

本任务暂时不要做：

- 不重写 `LIFEOS-P0-003`。
- 不新增、合并、拆分或改名 11 个对象 + `Link`。
- 不设计最终数据库表、ERD、API、事件流、索引或技术架构。
- 不设计完整 PRD、首页/今日页或授权 UI。
- 不执行技术 Spike。
- 不修改代码。
- 不修改 Stitch。
- 不改变 LifeOS 产品定位。
- 不扩大 V1 范围。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/reviews/LIFEOS-P0-003_pm_review.md`
- `lifeos/reviews/LIFEOS-P0-008_core_domain_model_independent_review.md`
- `lifeos/reviews/LIFEOS-P0-008_pm_review.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

## 角色检查点

主责角色：数据 / 领域模型负责人必须重点回答：

- 四类命令如何映射到 Source、Artifact、Derivation、Feedback、Authorization、AuditEntry、Link、Action、Decision、Assertion？
- Derivation 如何继承输入限制，并在跨 Project 展示、保存、再派生时重新判定？
- 用户确认对象在证据失效后如何保留历史，同时退出自动依据？
- 删除、撤回、备份恢复、离线重连、导出和重导入如何避免复活？
- AuditEntry 如何解释关键操作，同时不通过路径、ID、时间、错误详情反向识别敏感内容？

协审角色必须重点检查：

- AI 信任与安全负责人：是否继承 P0-007，不削弱 AI 权限基线。
- 技术架构负责人：是否保持最小实现可验证，不引入 11 张表、图数据库或事件溯源冻结。
- 产品架构负责人：是否服务个人终身外脑和 V1 第一场景，不滑向企业后台或通用知识图谱。

## 核心问题

请重点回答：

1. M-01 至 M-05 的最小补丁内容分别是什么？
2. 四类命令的领域效果矩阵如何表达？注意处理许可与保留许可要分离。
3. Derivation 的输出约束包络包含哪些最低字段或语义？多输入如何取最严格约束？
4. 如何分离 AI 来源身份、用户认可、业务状态、证据状态和派生状态？
5. 墓碑优先和导出不复活如何成为领域不变量？
6. AuditEntry 允许记录什么、不允许记录什么？
7. 补丁后哪些内容可建议冻结，哪些仍必须等待 Spike / PRD？

## 交付物

请将完整交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`

请输出的文件内容包括：

- 文档状态与范围声明
- M-01 至 M-05 逐项补丁
- 可冻结内容
- 仍未冻结内容
- 对后续 PRD / Spike 的影响
- 风险与待确认问题
- 是否建议 PM 将 `P0-003 + P0-009` 共同冻结为核心领域模型 V0.1 语义基线

## 验收标准

只有满足以下条件，任务才算完成：

- 完整回答所有核心问题。
- 完整交付物已保存到指定路径。
- 篇幅控制在 1500-3000 字左右；超出内容放入后续任务建议。
- 明确逐项覆盖 M-01 至 M-05。
- 明确区分事实、推断、建议、风险和需 PM 确认事项。
- 明确说明 Gate 2 是否可通过，Gate 3 / Gate 4 / Gate 1 是否存在条件。
- 不重写 P0-003。
- 不新增、合并、拆分或改名核心对象。
- 不修改代码、Stitch 或外部系统。
- 不擅自冻结核心领域模型，只提出冻结建议与冻结范围。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、AI 权限模型或数据模型。
- 不把 11 个对象 + `Link` 误读为数据库表、API 或 UI 模块冻结。
- 不把技术 Spike 计划误认为已经实测通过。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出任务 ID、当前状态、3-8 条摘要、角色与关卡覆盖情况、交付物路径、是否需要 PM 决策、后续任务建议、阻塞或异常说明。
