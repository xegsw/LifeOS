# LIFEOS-P3-028｜Schema / API 条件整改轻量独立复核

## 任务信息

- 任务 ID：LIFEOS-P3-028
- 任务名称：Schema / API 条件整改轻量独立复核
- 优先级：P0
- 任务类型：评审型任务 / 轻量独立复核
- 建议篇幅：2000-3500 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要独立攻击 P3-027 的设计补丁是否真正关闭 P3-026 的 P1 条件，尤其要检查四 invoke 拆分、权限隔离、来源身份、反馈撤回和后续 Tauri capability 矩阵影响；WorkBuddy 更适合作为独立评审与反例视角，避免 P3-027 执行会话自证。
- 是否需要后续独立评审：No。本任务本身就是独立复核；若发现 P0 或关键 P1，则后续应由 PM 决定是否创建返工任务。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：AI 信任与安全负责人 / 数据模型负责人
- 协审角色：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 独立评审
- 推荐复用的会话：可复用此前承担 P3-026 的 WorkBuddy 独立评审线会话，前提是该会话已完成 P3-026、不参与 P3-027 执行、上下文未混淆且能重新读取本任务卡；否则新建 WorkBuddy 独立评审会话。
- 会话判断理由：P3-028 是对 P3-027 条件整改包的独立复核，必须与 P3-027 执行会话隔离，避免执行者自证。若复用 P3-026 评审线，可保持同一反例视角并降低上下文成本。
- 是否需要独立性隔离：Yes。P3-027 执行会话不得执行本任务；本任务会话不得修改 P3-027 或任何工程文件。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P3-027_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- 可复用既有读取结果：
  - 若同一独立评审会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-027 交付物与 PM Review
  - P3-026 独立评审与 PM Review
  - P3-025 中与 Schema / API / IPC DTO / `semantic_object` / 错误码相关章节
  - P3-024 中与 M-01 / M-04 / M-20 / capability / invoke 验证相关章节
- 任务完成后是否建议保留会话：Yes，作为后续 Schema / API / Tauri capability 独立评审线会话保留。

## 背景

P3-025 生产 Schema / API 设计草案已通过 PM 验收，但未冻结。P3-026 独立反例评审未发现 P0，但提出 7 个 P1 条件和 5 个 P2 清洁项。P3-027 已按 PM 判断在设计层补齐这些条件，并建议将候选 `lifeos_control` 拆为 `lifeos_mutate` 与 `lifeos_destruct`。

由于 P3-027 的四 invoke 拆分会影响候选 Tauri capability / P3-024 验证矩阵，且 P3-027 后续将成为 migration 设计、API 合同测试与最小 Tauri shell 的输入，本任务需要独立复核其是否真的足够安全、完整、可测试。

## 目标

本任务完成后，PM 应能判断：

- P3-027 是否真正关闭 P3-026 的 7 个 P1 条件。
- P3-027 是否引入了新的 P0 / P1 风险。
- 四 invoke 拆分是否比保留三 invoke 更安全、更清晰、更可验证。
- P3-024 M-01 / M-04 / M-20 是否必须因四 invoke 拆分而调整。
- `semantic_object` 聚合与拆表触发器是否足以支持下一步 migration 设计。
- 是否允许在不写正式 migration 的前提下，启动后续 SQL migration 设计 / 合同测试任务。

## 范围

本任务必须覆盖：

1. 逐项复核 P3-027 对 P1-1 至 P1-7 的整改是否完整。
2. 对 P1-1 授权 scope 解析进行反例攻击：跨 Project、Project deny + Source allow、Source deny + Project allow、多 allow ambiguous、候选 Project link、已删除 / tombstone / generation mismatch、Renderer 伪造归属。
3. 对 P1-2 Feedback retract 进行反例攻击：retract confirm、correct、complete、defer、Link confirm、Derivation confirm、显式 dependency、乱序和环形 dependency。
4. 对 P1-3 DTO / invoke 拆分进行安全复核：严格联合、未知字段、未知 action、action-parameter 错配、destruct capability 独立、preview token / expected generation / idempotency key。
5. 对 P1-4 `details_token` 泄露面进行复核：是否会泄露路径、SQL、对象 ID、授权匹配数量、内部状态、Project 名或原文。
6. 对 P1-5 `semantic_object` 聚合进行复核：四类型 schema 是否足够、拆表触发器是否可执行、是否存在用嵌套 JSON 规避拆表的漏洞。
7. 对 P1-6 DerivationInput DB 约束进行复核：恰一非空、type / column 一致性、partial unique index、应用层校验不能替代 DB 约束。
8. 对 P1-7 ContentIdentity 条件约束进行复核：用户原文、外部引用、quoted excerpt、AI 生成 / 推断 / 建议是否不会混淆。
9. 判断 P3-027 是否改变核心领域模型、AI 权限边界或技术架构 V0.1 冻结合同。
10. 判断是否建议 P3-024 验证矩阵补丁、P3-025 合同补丁、或后续 migration 设计任务。

## 非范围

本任务暂时不要做：

- 不重写 P3-027。
- 不修改 P3-025。
- 不写 SQL migration。
- 不修改工程代码。
- 不创建 Tauri IPC handler。
- 不安装、配置或运行真实 Tauri。
- 不复跑工程测试，除非只读检查任务卡直接输入中的静态 evidence 文件。
- 不处理真实数据、真实 Vault、真实用户文件或外部用户。
- 不启用真实文件导出、路径扩权、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md` 或 `OPEN_QUESTIONS.md`。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-027_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- P3-025 可按 Schema / API / IPC DTO / `semantic_object` / 错误码相关章节定向读取。
- P3-024 可按 M-01 / M-04 / M-20 / capability / invoke 验证相关章节定向读取。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- P3-027 是否清楚区分用户原文、AI 生成、AI 推断 / 建议、外部引用来源和用户确认事实。
- 授权、撤回、删除、来源身份、诊断脱敏、候选建议可信度是否仍 fail closed。
- `semantic_object` 聚合和 ContentIdentity 约束是否不会破坏核心领域语义。
- 四 invoke 拆分是否降低权限风险，还是引入新的复杂度和验证缺口。

协审角色必须重点检查：

- 后续 migration 设计是否有足够清晰的 DB / DTO / API 约束输入。
- P3-024 的真实 Tauri / IPC 验证矩阵是否需要调整。
- 是否存在 P3-027 把候选规则误写成冻结资产、已实现能力或风险关闭的表述。
- 是否存在需要新增 P0 / P1 风险或必须返工的问题。

## 核心问题

请重点回答：

- P3-026 的 7 个 P1 条件是否全部关闭？若未关闭，分别是什么级别？
- P3-027 是否新增了 P0 或关键 P1 问题？
- 四 invoke 拆分是否应作为后续候选输入？是否必须先调整 P3-024 矩阵？
- `semantic_object` 是否可继续聚合？拆表触发器是否足够硬？
- 是否允许启动“SQL migration 设计 / 合同测试任务”？注意：不是写或执行 migration。
- 是否允许启动“最小 Tauri shell / handler 任务”？若不允许，阻塞条件是什么？
- P3-027 是否改变核心领域模型、AI 权限边界或技术架构 V0.1 冻结合同？

## 交付物

请将完整独立评审保存为 Markdown 文件，路径建议：

`lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`

请输出的文件内容包括：

- 评审信息
- 评审摘要
- 已通过内容
- P1-1 至 P1-7 逐项复核
- 四 invoke 拆分专项复核
- P3-024 验证矩阵影响
- `semantic_object` 聚合与拆表门复核
- 新发现问题：P0 / P1 / P2 分级
- 关卡检查
- 风险
- 需要 PM 决策
- 最终建议

篇幅控制：

- 独立评审型任务建议 2000-3500 字。
- 超出当前任务范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整评审文件已保存到 `lifeos/reviews/`。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供评审文件路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确列出是否存在 P0 / P1 / P2 问题。
- 明确声明本任务不冻结 Schema / API、不写 migration、不运行 Tauri、不启用真实能力、不关闭 R-0040。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改 P3-025 或 P3-027。
- 不修改项目账本。
- 不写 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。

