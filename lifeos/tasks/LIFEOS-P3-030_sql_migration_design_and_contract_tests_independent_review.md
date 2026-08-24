# LIFEOS-P3-030｜SQL migration 设计 / 合同测试独立评审

## 任务信息

- 任务 ID：LIFEOS-P3-030
- 任务名称：SQL migration 设计 / 合同测试独立评审
- 优先级：P0
- 任务类型：评审型任务 / 独立反例评审
- 建议篇幅：2000-4000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：P3-029 由 Codex 技术 / 数据设计会话产出，本任务需要独立攻击 migration 设计、DB 约束、四 invoke 合同测试、授权 / 撤回 / 删除 / 来源身份边界和 P3-024 矩阵影响，WorkBuddy 更适合作为外部反例评审视角，避免执行者自证。
- 是否需要后续独立评审：No。本任务本身就是独立评审；若发现 P0 / P1，应由 PM 决定是否创建整改任务。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：数据 / 领域模型负责人、AI 信任与安全负责人
- 协审角色：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：WorkBuddy 独立评审
- 推荐复用的会话：可复用此前承担 P3-026 / P3-028 的 WorkBuddy 独立评审线会话，前提是该会话未参与 P3-029 执行、上一任务已完成、上下文未混淆且能重新读取本任务卡；否则新建 WorkBuddy 独立评审会话。
- 会话判断理由：P3-030 是对 P3-029 的独立评审，必须与 P3-029 执行会话隔离；复用既有独立评审线可以继承反例攻击风格并降低上下文成本，但不能复用 P3-029 的执行会话。
- 是否需要独立性隔离：Yes。P3-029 执行会话不得执行本任务；本任务不得修改 P3-029 或任何工程文件。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-029_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-028_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- 可复用既有读取结果：
  - 若同一独立评审会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-029 交付物与 PM Review
  - P3-028 独立评审与 PM Review
  - P3-027 中与 P1 条件整改、四 invoke、ContentIdentity、DerivationInput、Feedback、Authorization、`semantic_object` 相关章节
  - P3-025 中与 Schema / API / IPC DTO / 错误码 / `semantic_object` 相关章节
  - P3-024 中与 M-01 / M-04 / M-20 / capability / invoke 验证相关章节
- 任务完成后是否建议保留会话：Yes，作为后续 Schema / API / migration / Tauri capability 独立评审线会话保留。

## 背景

P3-025 已形成生产 Schema / API 设计草案，P3-026 独立评审提出 7 个 P1 条件，P3-027 已在设计层完成条件整改，P3-028 独立复核结论为 Pass。P3-029 在此基础上产出 SQL migration 设计 / 合同测试草案，并由 PM 验收为 Accepted / Pass with Conditions。

P3-029 仍不是可执行 migration，不冻结 Schema / API，也不允许直接进入真实 Tauri / IPC。为了避免 SQL schema、trigger、transaction guard、DTO 合同测试和安全边界在进入实现前存在未发现漏洞，本任务需要以独立反例方式审查 P3-029 是否足够成为后续候选 SQL migration 编写输入。

## 目标

本任务完成后，PM 应能判断：

- P3-029 是否准确承接 P3-025 / P3-027 / P3-028 的关键约束。
- P3-029 是否遗漏 DB 层必须强制的不变量。
- P3-029 的 CHECK / trigger / partial index / unique index / transaction guard 分责是否可实现、可测试、可 fail closed。
- P3-028 的 3 个 P2 清洁项是否已被 P3-029 充分处理。
- `semantic_object` 继续聚合是否仍成立，拆表门是否足够硬。
- 四 invoke / DTO 合同测试是否足以支撑后续 P3-024 M-01 / M-04 / M-20 矩阵调整。
- 是否允许在后续另立任务进入候选 SQL migration 编写，或必须先返工。

## 范围

本任务必须覆盖：

1. **承接关系复核**
   - 核对 P3-029 是否准确继承 P3-025、P3-027、P3-028 的 Schema / API / 权限 / 来源 / 派生 / 反馈 / 四 invoke 口径。
   - 检查是否把候选设计误写成已实现、已冻结或风险已关闭。
2. **DB 约束反例攻击**
   - ContentIdentity 条件约束：用户原文、用户编辑、外部来源、quoted excerpt、AI generated / inference / suggestion 是否不会混淆。
   - DerivationInput：恰一引用、type / column 一致性、typed partial unique、activation completeness 是否不能被绕过。
   - Feedback / retract / dependency：retract-of-retract、分叉、乱序、跨 actor、跨 target、basis 被撤回、dependency 环是否 fail closed。
   - Authorization / strict_intersection：deny 优先、多 allow 交集、空集、未知 policy、多分组、缓存 canonical hash、过期授权是否 fail closed。
   - Tombstone / Outbox / FTS：删除、撤权、旧 generation、旧 lease、旧索引、恢复包是否不能复活或泄露存在性。
3. **`semantic_object` 聚合 / 拆表门复核**
   - 复查 Assertion / Decision / Action / Event 顶层专属字段计数。
   - 判断“Decision / Action 新增任一持久化顶层字段即拆表复查”是否足够硬。
   - 检查是否存在通过嵌套 JSON 规避拆表门的风险。
4. **Migration 可实现性复核**
   - 创建顺序、循环激活、两步激活、schema migration meta、checksum、rollback、foreign key check、migration_required 是否可落地。
   - 区分 DB CHECK、trigger、partial index、transaction guard 和应用层重复校验，检查是否把只能应用层完成的事情错误放入 CHECK，或把必须 DB 强制的事情只交给应用层。
5. **四 invoke / DTO 合同测试复核**
   - `lifeos_read`、`lifeos_export_candidate`、`lifeos_mutate`、`lifeos_destruct` 是否覆盖正测与未知 action、未知字段、跨 variant、错误 contract version、destruct 缺 preview token / expected generation / idempotency key 等反例。
   - 检查是否存在 mutate 路由 destruct、read 携带 destructive action、export candidate 产生真实写入、错误详情泄露等漏洞。
6. **P0 / P1 / P2 分级判断**
   - 标记 P3-029 中发现的问题级别。
   - P0：会导致原文静默改写、AI/来源身份混淆、删除 / 撤回 / 权限绕过、恢复复活、真实能力误启用、migration 半提交不可识别或安全边界失守。
   - P1：不立即越权但会阻塞候选 SQL migration 编写、合同测试实现或 P3-024 后续验证。
   - P2：文档清洁、命名、证据引用或测试矩阵补充项，可后置但需记录。
7. **后续准入建议**
   - 是否建议 P3-029 通过、条件通过、返工或阻塞。
   - 是否允许后续另立“候选 SQL migration 编写 + 合成空库合同测试实现”任务。
   - 是否仍阻塞最小 Tauri shell / handler。

## 非范围

本任务暂时不要做：

- 不重写 P3-029。
- 不修改 P3-025、P3-027、P3-028 或 P3-029。
- 不写 SQL migration。
- 不创建 `.sql` migration 文件。
- 不执行 SQL migration。
- 不修改工程代码。
- 不修改 `lifeos/engineering/` 下任何文件。
- 不创建或修改 Tauri IPC handler。
- 不安装、配置或运行真实 Tauri。
- 不复跑工程测试，除非只读检查任务卡直接输入中的静态 evidence 文件。
- 不连接真实数据库、真实 Vault 或真实用户数据。
- 不处理真实敏感数据、真实用户文件或外部用户。
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
- `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-029_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-028_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- P3-029 必须完整读取。
- P3-027、P3-025、P3-024 可按本任务核心问题定向读取相关章节。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- P3-029 是否保护用户原文、来源身份、外部引用、AI 派生、用户确认事实之间的边界。
- 授权、撤回、删除、导出、恢复包、FTS、outbox 和候选建议是否仍 fail closed。
- DB 约束、触发器、事务 guard 是否足够表达 LifeOS 核心领域语义。
- `semantic_object` 继续聚合是否不会变成未来 schema 失控或语义混淆。

协审角色必须重点检查：

- P3-029 是否已经足以成为候选 SQL migration 编写输入。
- 合同测试是否能在真实实现前捕获 P0 / P1 越界。
- P3-024 M-01 / M-04 / M-20 的四 invoke 调整是否清楚但未被误认为真实 Tauri 已验证。
- 是否存在需要新增风险、阻塞后续任务或要求返工的问题。

## 核心问题

请重点回答：

- P3-029 是否可作为候选 SQL migration 编写输入？
- P3-029 是否遗漏任何 P0 / P1 级 DB 或 DTO 合同测试？
- P3-028 的 3 个 P2 清洁项是否处理充分？
- `semantic_object` 是否继续聚合，还是必须拆表？
- CHECK / trigger / partial index / transaction guard 分责是否合理？
- 四 invoke / DTO 合同测试是否足以支撑后续 P3-024 矩阵调整？
- 是否允许后续启动“候选 SQL migration 编写 + 合成空库合同测试实现”任务？
- 是否仍阻塞最小 Tauri shell / handler？
- 是否改变核心领域模型、AI 权限边界或技术架构 V0.1 冻结合同？

## 交付物

请将完整独立评审保存为 Markdown 文件，路径建议：

`lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`

请输出的文件内容包括：

- 评审信息
- 评审摘要
- 已通过内容
- 关键问题
- DB 约束反例攻击
- `semantic_object` 聚合 / 拆表门复核
- 四 invoke / DTO 合同测试复核
- P3-024 M-01 / M-04 / M-20 影响复核
- 新发现问题：P0 / P1 / P2 分级
- 必须整改项
- 条件通过项
- 关卡检查
- 风险
- 需要 PM 决策
- 最终建议

篇幅控制：

- 独立评审型任务建议 2000-4000 字。
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
- 不修改 P3-025、P3-027、P3-028 或 P3-029。
- 不修改项目账本。
- 不写 SQL migration。
- 不创建 `.sql` migration 文件。
- 不执行 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
