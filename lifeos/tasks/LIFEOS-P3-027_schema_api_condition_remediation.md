# LIFEOS-P3-027｜Schema / API 条件整改包

## 任务信息

- 任务 ID：LIFEOS-P3-027
- 任务名称：Schema / API 条件整改包
- 优先级：P0
- 任务类型：条件整改 / 设计补丁型任务
- 建议篇幅：2500-4000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要把 P3-026 独立评审提出的 7 个 P1 条件转成精确、可执行、可供后续 migration / Tauri 壳任务引用的设计补丁；Codex 更适合结构化技术合同、伪代码、约束表达和边界文字修订。
- 是否需要后续独立评审：Conditional。若 P3-027 仅补齐 P3-026 指定 P1 条件且未引入新实体 / 新权限边界，PM 可验收后决定是否需要轻量复核；若改变核心领域实体、AI 权限边界、Tauri capability 结构或 Schema/API 冻结范围，必须另行独立评审。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 数据模型负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：Codex 技术 / 数据设计会话
- 推荐复用的会话：可复用 P3-025 的 Codex 技术 / 数据设计会话，前提是该会话已完成 P3-025、不再修改旧任务、上下文未混淆且能重新读取本任务卡；否则新建 Codex 专项设计会话。
- 会话判断理由：P3-027 是 P3-025 的条件整改，适合由技术 / 数据设计 Agent 处理；但不得由 P3-026 独立评审会话执行，以保持评审独立性。
- 是否需要独立性隔离：Yes。P3-026 独立评审会话不得执行本整改任务；P3-027 执行会话不得自行评审自己的整改结论。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
- 可复用既有读取结果：
  - 若同一会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
  - P3-025 主交付物中与 Schema / API / 错误码 / IPC DTO / `semantic_object` 相关章节
- 任务完成后是否建议保留会话：Yes，作为 Schema / API 条件整改与后续 migration 设计线会话保留。

## 背景

P3-025 生产 Schema / API 设计草案已通过 PM 验收，状态为 Accepted but Not Frozen。P3-026 对 P3-025 做了独立反例评审，结论为 Accepted / Pass with Conditions：未发现 P0 级设计漏洞，但提出 7 个 P1 条件和 5 个 P2 清洁项。

PM 已确认后续顺序必须收紧：在 P1 条件整改完成前，不得进入 SQL migration 编写、最小 Tauri 壳搭建或真实 IPC 验证。本任务就是把 P3-026 的 7 个 P1 条件转成可执行的设计补丁。

## 目标

本任务完成后，PM 应能判断：

- P3-026 的 P1-1 至 P1-7 是否已被逐项澄清。
- P3-025 是否可继续作为后续 migration 设计输入。
- 哪些内容仍是设计候选，不是冻结 Schema / API。
- `semantic_object` 聚合是否可继续，以及拆表触发条件是否清楚。
- `lifeos_control` 是否应拆分为 `lifeos_mutate` / `lifeos_destruct`，或保留三命令但强化 DTO 约束。
- P2 清洁项是否有最低处理口径，且未扩大任务范围。

## 范围

本任务必须覆盖 P3-026 提出的 7 个 P1 条件：

1. **P1-1 授权 scope 解析形式化算法**
   - 明确 deny 是否在任意 scope 级别全局阻断。
   - 明确多 allow 匹配时是否冲突、何时可接受。
   - 明确 project / source / artifact 级 scope 优先关系。
   - 输出可供测试实现的伪代码或判定表。
2. **P1-2 Feedback retract 级联规则**
   - 明确 retract confirm 是否影响 correct / complete / defer。
   - 明确级联是自动还是需要显式 retract 链。
   - 明确已确认 Link / Action / Derivation 的反馈撤回后状态。
3. **P1-3 `lifeos_control` DTO 联合验证边界**
   - 明确 discriminated union / Rust enum 的 action-parameter 绑定。
   - 明确未知 action、参数错配、未知字段、额外字段如何 fail closed。
   - 明确是否拆分为 `lifeos_mutate` 与 `lifeos_destruct`；若不拆，给出安全理由与能力约束。
4. **P1-4 `details_token` 生命周期与脱敏规则**
   - 明确 token 可检索内容、可检索主体、有效期和一次性 / 会话绑定规则。
   - 明确禁止返回路径、SQL、对象 ID、内部状态、原始错误。
5. **P1-5 `semantic_object` 类型 schema 与拆表条件**
   - 给出 Assertion / Decision / Action / Event 的最小 JSON schema 草案或字段清单。
   - 给出 schema version / migration 规则。
   - 固化拆表触发条件：任一类型专属字段超过 5 个，或类型间不变量冲突无法用 JSON schema 表达时必须拆表。
6. **P1-6 DerivationInput 列互斥 DB 级约束**
   - 给出 SQLite CHECK 或触发器表达。
   - 明确应用层校验不替代 DB 级约束。
7. **P1-7 `content_identity.origin_actor_ref` 按身份可空规则**
   - 明确 external_original / external_reference / quoted_excerpt 必填。
   - 明确 user_original / user_edited 可空。
   - 明确 AI 类由 derivation_id 承担溯源，必要时禁止 origin_actor_ref 混用。

本任务还应以 Should 级别覆盖 P3-026 的 5 个 P2 清洁项：

- `idempotency_key` 命名空间。
- FTS 命中计数与可见结果差异泄露。
- `health_check.detail_level` 允许值。
- `semantic_object_version` 清理规则。
- `capture_original` 去重与相同内容新版本语义。

## 非范围

本任务暂时不要做：

- 不修改 P3-025 主交付物；本任务产出独立条件整改包。
- 不写 SQL migration。
- 不修改工程代码。
- 不创建 Tauri IPC handler。
- 不安装、配置或运行真实 Tauri。
- 不复跑或扩展工程测试。
- 不处理真实数据、低敏真实数据、真实 Vault、真实用户文件或外部用户。
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
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/reviews/LIFEOS-P3-025_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-026_pm_review.md`
- 可按需定向参考：`lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- 可按需定向参考：`lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- P0-007 / P0-009 仅在判断 `semantic_object`、ContentIdentity 或 AI 权限边界是否冲突时定向读取相关章节。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`，只读任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 7 个 P1 条件是否全部被明确处理。
- 每项处理结果是否足以作为后续 migration / API DTO / IPC handler 设计输入。
- 是否引入了新实体、新权限边界或新冻结范围。
- `semantic_object` 聚合是否仍安全，拆分条件是否可执行。

协审角色必须重点检查：

- 是否仍清楚区分用户原文、AI 生成、AI 推断 / 建议、外部引用来源和用户确认事实。
- 是否没有把设计补丁写成 Schema / API 冻结。
- 是否没有暗中启用真实 Tauri / IPC、真实 Vault、真实文件导出或 R-0040 关闭。
- P2 清洁项是否被合理纳入而没有扩大范围。

## 核心问题

请重点回答：

- P3-026 的 P1-1 至 P1-7 是否全部关闭？
- 哪些项仍需 PM 判断？
- `lifeos_control` 是否拆分？为什么？
- `semantic_object` 是否继续聚合？拆表触发条件是什么？
- P3-027 完成后，是否允许进入 SQL migration 设计任务？是否仍需要独立复核？
- P3-027 是否改变了核心领域模型、AI 权限边界或技术架构冻结合同？

## 交付物

请将完整交付物保存为 Markdown 文件，路径建议：

`lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`

请输出的文件内容包括：

- 结论摘要
- 非冻结声明
- P1 条件整改总表
- P1-1 至 P1-7 逐项整改方案
- P2 清洁项处理口径
- 对 P3-025 的补充合同文本
- Must / Should / Later 分层
- 是否允许后续 migration 设计的判断
- 角色检查点结果
- 需要 PM / 用户确认的问题
- 后续任务建议

篇幅控制：

- 条件整改 / 设计补丁型任务建议 2500-4000 字。
- 超出当前任务范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确声明本任务不冻结 Schema / API、不写 migration、不运行 Tauri、不启用真实能力、不关闭 R-0040。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改项目账本。
- 不写 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不自行启动后续任务。

## 给专项会话的可复制启动提示词

请先读取当前项目根目录的 `AGENTS.md`，并按其中规则执行 LifeOS 专项任务。

任务文件：

`lifeos/tasks/LIFEOS-P3-027_schema_api_condition_remediation.md`

请注意：你是专项技术 / 数据设计会话，不是 PM 主会话，也不是独立评审会话。只做 Schema / API 条件整改包，不写 SQL migration、不改代码、不安装、不配置、不运行真实 Tauri，不修改工程文件、Stitch 或项目账本；不得关闭 R-0040，不得启用真实能力，不得冻结 Schema / API 或工程基线，不得进入下一阶段。完整交付物写入任务卡指定路径，聊天回复只输出摘要、交付物路径、预检路径和是否需要 PM 决策。
