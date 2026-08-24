# LIFEOS-P3-026｜生产 Schema / API 独立反例评审

## 评审信息

- 对应任务 ID：LIFEOS-P3-025
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- 独立评审角色：数据 / 领域模型负责人、AI 信任与安全负责人
- 协审视角：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- 评审结论：Pass with Conditions
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-025_LIFEOS-P3-025_production_schema_api_design_local_precheck.md`
- 本地预检状态：Skipped（本地模型 502 Bad Gateway，符合允许跳过场景）
- 更新时间：2026-08-13

## 评审摘要

1. **[事实]** P3-025 生产候选 Schema/API 设计草案在核心安全不变量层面未发现 P0 级设计漏洞。不可变 `ArtifactVersion`、独立 `ContentIdentity`、完整 `DerivationInput`、追加式 `Feedback`、六维授权 + 统一消费门、双 generation/tombstone、FTS 回连权威、只读恢复评估等核心设计均可接受。
2. **[事实]** 发现 7 项 P1 级设计澄清需求，集中在：授权 scope 解析算法未完整形式化、Feedback retract 级联规则未指定、`lifeos_control` DTO 联合验证边界未限定、`details_token` 生命周期未约束、`semantic_object` 类型 schema 校验未细化、DerivationInput 列互斥约束缺 DB 级表达、`content_identity.origin_actor_ref` 可空条件未按 `identity_kind` 区分。
3. **[事实]** 发现 5 项 P2 级清洁项：`idempotency_key` 命名空间未明确、FTS 命中计数与可见结果差异可能泄露存在性、`health_check.detail_level` 允许值未枚举、`semantic_object_version` 清理规则缺失、`capture_original` 去重与"允许相同内容新版本"语义矛盾。
4. **[推断]** `semantic_object` 聚合作为 V1 评审候选可继续，但必须设置拆分条件：当任一类型的专属字段数量超过 5 个、或类型间不变量冲突无法用 JSON schema 表达时，必须拆表。
5. **[建议]** P3-025 可作为 migration 设计和最小 Tauri 壳任务的候选输入，但 7 项 P1 条件必须在 migration 编写前以补充文档或设计修订形式澄清。
6. **[事实]** P3-025 不构成 R-0040 关闭输入；真实 Tauri/IPC 验证、进程杀死耐久和目标平台验证仍需独立完成。
7. **[声明]** 本评审不冻结 Schema/API、不写 migration、不运行 Tauri、不关闭 R-0040、不启用真实能力、不进入下一阶段。

## 已通过内容

以下设计经独立审查确认可接受，可进入后续工程输入：

1. **权威内容分层**：`ArtifactVersion` 不可变正文 + `content_hash` + UPDATE 触发器禁止改正文 + DELETE 仅在 tombstone `active_blocked` 后放行——符合"用户原文不可被 AI 静默改写"。
2. **ContentIdentity 八类身份**：`user_original`/`user_edited`/`external_original`/`external_reference`/`quoted_excerpt`/`ai_generated`/`ai_inference`/`ai_suggestion` 正交且 AI 类必须有 Derivation、用户原文不得有 AI derivation——符合来源区分要求。
3. **完整 DerivationInput**：`derivation_input` 多输入列 + `input_content_hash` + 主键 `(derivation_id,input_type,input-id)` + "输入集非空、完整且用于 ID/重检"——符合"AI/算法输出必须可追到完整输入集"。
4. **追加式 Feedback**：只追加不 UPDATE + retract 指向较早有效 Feedback + `UNIQUE(idempotency_key)` + 当前认可由事件折叠得到——符合"Feedback 追加留痕"。
5. **六维授权 + policy envelope**：`authorization` 含 processor/purpose/location/status/expires_at/revoked_at + `authorization_scope` deny 优先 + `authorization_action` 白名单——符合"消费前重检六维"。
6. **统一消费门**：`authorize_and_resolve()` 在入队前、执行前、外发/保存/索引/发布关键点调用，任一项 false 或未知均拒绝——符合 fail-closed 原则。
7. **FTS 回连权威**：FTS 候选 ID 必须联结 Artifact/Version/Source/Authorization/Tombstone 做当前重检——FTS 不成为权威。
8. **只读恢复评估**：`evaluate_restore_candidates` 严格只读 + 包内状态不可信 + 当前环境 tombstone/撤回优先——不复活旧数据。
9. **Renderer 不可信**：Renderer 提交的 ID/版本/generation/purpose 全部视为不可信断言 + 服务端重建可信上下文 + 默认拒绝——符合 IPC 安全原则。
10. **错误码允许列表**：P0/P1/P2 三级分类 + "不泄露对象存在性" + "不可自动重试为更宽权限"——符合最小泄露原则。
11. **capability_status 默认关闭**：真实 Vault/Tauri 文件导出/云/向量/同步/L3 等保持 disabled——符合"Later 不是隐式授权"。
12. **非冻结声明**：明确声明不冻结 Schema/API、不写 migration、不运行 Tauri、不关闭 R-0040、不进入下一阶段。

## 关键问题

### P1-1：授权 scope 解析算法未完整形式化

**[事实]** 设计声明 `authorization_scope` "deny 优先；Project scope 不覆盖 Source/Artifact 排除"和 `authorization` "同一判定必须命中唯一当前 allow，未知/多条冲突均拒绝"。但以下场景的解析结果无法从现有文字确定推断：

- **场景 A**：Auth X scope(project=P, allow, action=read) + Auth Y scope(source=S, deny, action=read)，请求读取属于 P 且来自 S 的 Artifact → 推断为 deny 胜出，但解析路径未形式化。
- **场景 B**：Auth X scope(project=P, deny, action=read) + Auth Y scope(source=S, allow, action=read)，请求读取同一 Artifact → "Project scope 不覆盖 Source/Artifact 排除"是否意味着 project-level deny 不传播到 source 级？若如此，Y 的 allow 将胜出，这是危险的。
- **场景 C**：Auth X scope(project=P, allow, action=read) + Auth Y scope(source=S, allow, action=read) → 两个 allow 匹配，是否构成"多条冲突"而拒绝？还是互补接受？

**[风险]** 若实现者将"Project scope 不覆盖 Source/Artifact 排除"理解为"project deny 不传播到 source 级"，则 project-level deny 可被 source-level allow 绕过。

**[建议]** 在 migration 编写前，补充形式化解析算法，至少覆盖：(1) deny 在任意 scope 级别是否全局阻断；(2) 多个 allow 匹配时"冲突"的精确定义；(3) scope 级别间的优先关系。

### P1-2：Feedback retract 级联规则未指定

**[事实]** `feedback` 支持 `kind=retract`，"retract 必须指向较早有效 Feedback"。但以下级联场景未指定：

- **场景**：用户先 confirm（F1），再 correct（F2），再 retract F1。F2（correct）是否因 F1 被撤回而失效？还是 F2 独立保留？
- **场景**：用户先 confirm（F1），再 complete（F2，依赖已确认 Action），再 retract F1。F2 是否因 F1 失效而不再满足"只允许已确认 Action"前提？

**[风险]** 若 retract 不级联，已撤回 confirm 的后续 correct/complete 可能仍然有效，导致用户撤回意图未完整表达。若级联过度，可能意外撤销用户有意保留的后续反馈。

**[建议]** 明确 retract 的级联范围：(1) retract confirm 是否级联失效同一 target 上依赖该 confirm 的 correct/complete/defer；(2) 级联是自动还是需要显式 retract 链。

### P1-3：`lifeos_control` DTO 联合验证边界未限定

**[事实]** 设计将 14 个领域命令映射为 `lifeos_read`、`lifeos_export_candidate`、`lifeos_control` 三个 invoke DTO 联合。`lifeos_control` 同时包含创建类（`create_suggestion_candidate`、`create_important_link`）、追加类（`record_feedback`、`retract_feedback`）和销毁类（`revoke_authorization`、`disconnect_source`、`delete_artifact`）命令。

**[风险]** (1) 单一 capability 同时授予创建和销毁权限，违反最小权限原则。(2) 若 DTO 验证未做 discriminated union + exhaustive pattern matching，`action` 字段与参数 DTO 不匹配时可能走到错误 handler。(3) 设计声明"最终映射需独立评审"但未给出映射前的安全约束。

**[建议]** (1) 明确 DTO 联合使用 TypeScript discriminated union + Rust enum，未知 `action` 在参数反序列化前即返回 `E_UNKNOWN_COMMAND`。(2) 考虑将 `lifeos_control` 拆分为 `lifeos_mutate`（创建/追加）和 `lifeos_destruct`（撤销/断开/删除），以支持差异化 capability 授权。(3) 在 migration/壳搭建前完成映射安全约束文档。

### P1-4：`details_token` 生命周期未约束

**[事实]** 错误响应包含 `details_token?` 字段，但设计未指定：(1) token 可检索什么信息；(2) 谁可检索（仅当前请求者？任何持有 token 者？）；(3) token 有效期；(4) token 内容是否经过脱敏。

**[风险]** 若 `details_token` 可检索原始错误信息（含 SQL 错误、路径、对象 ID），则错误码允许列表的脱敏效果被旁路。

**[建议]** 明确 `details_token` 只能检索与允许列表错误码一致的安全摘要；token 有效期不超过当前请求会话；不返回路径、SQL、对象 ID 或内部状态。

### P1-5：`semantic_object` 类型 schema 校验未细化

**[事实]** `semantic_object_version.payload_json` 声明"JSON 必须有版本化 schema 校验，不允许任意未验证 payload"。但设计未指定：(1) 每个 `object_type`（Assertion/Decision/Action/Event）的 JSON schema 草案；(2) 类型间不变量差异（如 Decision 必须有 `decided_by`、Action 必须有 `due_date`）如何强制；(3) schema 版本演进规则。

**[风险]** 若 `payload_json` 缺少类型专属校验，Assertion 可能错误携带 Decision 字段，或 Action 缺少必需的截止时间，导致领域语义被稀释。

**[建议]** 在 migration 编写前，为每个 `object_type` 产出最小 JSON schema 草案（至少列出必填字段），并指定 schema 版本字段和演进规则。

### P1-6：DerivationInput 列互斥约束缺 DB 级表达

**[事实]** `derivation_input` 声明"一个输入列恰非空"（`artifact_version_id`/`semantic_object_id`/`feedback_id`/`source_id` 中恰一非空）。但 SQLite CHECK 约束无法简洁表达"恰一非空"逻辑（需要 `CASE WHEN` 或多个 `CHECK` 组合）。

**[风险]** 若该约束仅在应用层校验，直接 DB 写入（migration、调试工具、未来 CLI）可绕过，导致一个输入行同时引用多个不相关实体或全部为空。

**[建议]** 在 Schema 中显式写出等效的 `CHECK` 约束组合（如 `(artifact_version_id IS NOT NULL) + (semantic_object_id IS NOT NULL) + ... = 1`），或声明使用触发器强制，并标注应用层校验不替代 DB 级约束。

### P1-7：`content_identity.origin_actor_ref` 可空条件未按 `identity_kind` 区分

**[事实]** `content_identity` 的 `origin_actor_ref NULL` 未指定何时必填。对于 `external_original`/`external_reference`/`quoted_excerpt` 类型，外部来源引用是来源溯源的核心信息；若允许为 NULL，则无法追到外部来源。

**[风险]** 外部引用内容缺少 `origin_actor_ref` 将违反"必须区分外部引用来源"的不变量。

**[建议]** 明确 `origin_actor_ref` 在 `identity_kind` 为 `external_original`/`external_reference`/`quoted_excerpt` 时必填，在 `user_original`/`user_edited` 时可空，在 AI 类时由 `derivation_id` 承担溯源。

## 必须整改项

以下必须在 Schema/API 冻结前完成（不要求在本评审中完成，但必须作为 P3-025 补充或后续任务条件）：

1. **[P1-1]** 补充授权 scope 解析形式化算法，覆盖 deny 传播、多 allow 冲突判定和 scope 级别优先关系。
2. **[P1-2]** 补充 Feedback retract 级联规则。
3. **[P1-3]** 补充 `lifeos_control` DTO 联合安全约束文档，包括 discriminated union 验证和 action-parameter 绑定校验。
4. **[P1-4]** 约束 `details_token` 生命周期、可检索内容和脱敏规则。
5. **[P1-5]** 为每个 `semantic_object.object_type` 产出最小 JSON schema 草案。
6. **[P1-6]** 在 Schema 中显式表达 DerivationInput 列互斥约束。
7. **[P1-7]** 按 `identity_kind` 区分 `origin_actor_ref` 可空条件。

## 条件通过项

**结论：Pass with Conditions**

**条件清单：**

| # | 条件 | 适用范围 | 失效条件 |
|---|---|---|---|
| C1 | P1-1 至 P1-7 全部以补充文档或 Schema 修订形式澄清 | migration 编写、最小 Tauri 壳 DTO 定义、IPC handler 实现 | 任一条件未澄清即进入 migration 编写 |
| C2 | `semantic_object` 拆分条件被 PM 确认并记录 | V1 领域模型实现 | 专属字段超 5 个或不变量冲突时仍未拆表 |
| C3 | P3-024 M-01～M-26 真实验证未完成前，Schema/API 不冻结 | 所有后续工程任务 | 未经真实验证即冻结 |
| C4 | R-0040 保持 Open/Conditional | 全项目 | 未独立复评+用户确认即关闭 |

**适用范围：** P3-025 可作为 migration 设计和最小 Tauri 壳任务的候选输入，但不作为冻结合同、不作为 R-0040 关闭证据、不作为真实能力启用依据。

**失效条件：** 若任一 P1 条件在 migration 编写前未澄清，本评审结论自动降级为 Rework。

## 反例攻击清单与结论

### A1：多 Project 归属与 Project scope 误读为权限

**攻击**：Artifact A 同时关联 Project P1（confirmed）和 P2（candidate）。Auth X scope(project=P1, allow)。请求以 P2 为 context 读取 A。

**结果**：**通过**。设计声明"候选归属不授予权限"和"Project 仅为展示上下文"。消费门检查 authorization scope 而非 project link。P2 候选关联不构成授权。

### A2：多 Source、Source disconnect 后派生失效

**攻击**：Source S1 断开（generation 1→2）。Derivation D1 的 DerivationInput 记录 source_id=S1, source_generation=1。

**结果**：**设计层通过，实现层待验证**。设计声明"Source generation 变化会将其依赖 Derivation 标 stale"。消费门检查 `generations_match`，source_generation=1 ≠ 当前 2，拒绝。但 stale 传播的触发机制（触发器 vs 应用级级联 vs outbox job）未指定——**归入 P1-1 补充范围**。

### A3：allow + deny 冲突

**攻击**：见 P1-1 场景 A/B/C。

**结果**：**条件通过**。deny 优先的意图正确，但解析算法未形式化——**P1-1**。

### A4：ArtifactVersion 精确版本与 generation 竞态

**攻击**：读请求携带 expected_version_id=V3, expected_generation=5。同时 tombstone 写入 generation=6。

**结果**：**通过**。设计声明"写操作在事务内最后一次重检并使用 expected_generation；0 行更新视为竞态失败"。tombstone generation(6) > 请求快照(5)，消费门 `no_dominating_tombstone` 拒绝。

### A5：Feedback confirm/correct/retract 乱序

**攻击**：见 P1-2 场景。

**结果**：**条件通过**。追加式 + retract 指向较早有效 Feedback 的基础设计正确，但级联规则未指定——**P1-2**。

### A6：DerivationInput 不完整、evidence pointer 误用为权威输入

**攻击**：Derivation D1 的 `evidence_version_id` 指向 ArtifactVersion V5，但 DerivationInput 表中未记录 V5 作为输入。

**结果**：**通过**。设计声明 `evidence_version_id` "仅作显示指针，不能替代完整输入集"。消费门检查 `derivation_input` 表而非 evidence pointer。

### A7：ImportantLink AI 候选与用户确认 Link 身份混淆

**攻击**：AI 创建 Link L1（derivation_id=D1, identity=ai_suggestion）。用户确认 L1。D1 随后 stale。

**结果**：**设计层通过**。消费门检查 `link_evidence.artifact_generation` 和 `source_generation`。即使 Link 已确认，若 evidence 的 generation 不匹配，消费门拒绝。但设计未明确"已确认 Link 的 Derivation stale 后是否仍可消费"——**归入 P1-2 补充范围**，建议明确确认 Link 的 Derivation stale 不阻断消费（因用户已独立确认），但 evidence stale 仍阻断。

### A8：FTS 命中绕过权威回连

**攻击**：FTS 返回 10 候选，其中 3 个已 tombstoned 但 FTS outbox 尚未执行清理。

**结果**：**通过**。消费门 `no_dominating_tombstone` 在 FTS 回连时逐项检查，tombstoned 项被拒绝。但 FTS 命中计数(10)与实际返回(7)的差异可能泄露被拒对象存在性——**P2 清洁项**，建议搜索 API 不返回原始 hit count，只返回过滤后的结果数和 `next_cursor`。

### A9：export package / restore candidates 导致旧包复活

**攻击**：导出包 P1 在 T1 创建（含 Artifact A）。T2 时 A 被 tombstoned。T3 时 restore 评估 P1。

**结果**：**通过**。设计声明"当前环境与包内更严格且更新的 tombstone/撤回优先"。restore 评估以当前 DB 的 tombstone 为准，A 被标记 `blocked`。包内状态不可信。

**补充攻击**：包内包含的 ArtifactVersion 在当前 DB 中已被物理清理（cleaned）。restore 评估是否仍能验证其 hash？

**结果**：**条件通过**。设计声明恢复评估"先验证包结构和 hash"，若当前 DB 无对应记录，应标记 `excluded`。但未明确 cleaned vs not-found 的区分——**P2 清洁项**。

### A10：IPC 三窄命令映射滑向任意 dispatcher

**攻击**：Renderer 发送 `lifeos_control` with `action="delete_artifact"` 但参数为 `record_feedback` 的参数。

**结果**：**条件通过**。设计声明"联合内未知 action 仍返回 E_UNKNOWN_COMMAND"和"服务端重建可信上下文"。但 action-parameter 绑定校验未显式指定——**P1-3**。

### A11：错误码泄露对象存在性

**攻击**：Renderer 请求读取不存在的 Artifact A。响应为 `E_NOT_FOUND_OR_DENIED`。

**结果**：**通过**。设计将"不存在"与"无权"统一为 `E_NOT_FOUND_OR_DENIED`，不泄露对象存在性。

**补充攻击**：`E_AUTH_AMBIGUOUS` 是否泄露对象存在？

**结果**：**条件通过**。`E_AUTH_AMBIGUOUS` 暗示对象存在但授权冲突。设计声明此错误码用于"多条 allow 冲突"场景。若对象不存在，应返回 `E_NOT_FOUND_OR_DENIED` 而非 `E_AUTH_AMBIGUOUS`——这要求实现先检查存在性再检查授权，但"不泄露存在性"要求不先检查存在性。**存在轻微矛盾**——**P2 清洁项**，建议 `E_AUTH_AMBIGUOUS` 仅在对象确认存在且授权匹配多条时返回，且该错误码不区分"对象存在但授权冲突"与"对象不存在"。

### A12：capability_status / health_check 泄露环境信息

**攻击**：Renderer 调用 `health_check(detail_level="verbose")` 获取 DB 路径或对象数量。

**结果**：**条件通过**。设计声明 health_check"不返回路径、SQL、版本正文、密钥、对象数量小样本或自由错误"。但 `detail_level` 允许值未枚举——**P2 清洁项**，建议限定为 `"minimal"` 和 `"standard"` 两个值，并明确各级别返回内容。

### A13：`semantic_object` 聚合稀释领域语义

**攻击**：`semantic_object` with `object_type=assertion` 的 `payload_json` 包含 `decided_by` 字段（Decision 专属）。

**结果**：**条件通过**。设计声明"JSON 必须有版本化 schema 校验"但未给出类型专属 schema——**P1-5**。若类型 schema 未校验，领域语义将被稀释。

## 关卡检查

### Gate 2：数据与来源评审 — Pass with Conditions

**主责角色检查：**

- **P3-025 是否清楚区分用户原文、AI 生成、AI 推断/建议、外部引用来源和用户确认事实**：是。`ContentIdentity` 八类身份 + AI 类必须有 Derivation + 用户原文不得有 AI derivation + `origin_actor_ref` 溯源外部来源。但 `origin_actor_ref` 可空条件未按 `identity_kind` 区分（P1-7）。
- **P3-025 是否能表达 Source、Artifact、ArtifactVersion、ContentIdentity、DerivationInput、Feedback、Authorization、Tombstone 的独立生命周期**：是。各表均有独立 `generation`/`status`/`created_at`/`updated_at`，且消费门逐项检查。
- **P3-025 的统一消费门是否真的能 fail closed**：是。`authorize_and_resolve()` 任一项 false 或未知均拒绝；0 行更新视为竞态失败。但授权 scope 解析算法未形式化（P1-1），存在实现偏差风险。
- **`semantic_object` 聚合是否损害已冻结领域语义**：条件通过。V1 聚合可继续，但必须设置拆分条件并补充类型 schema（P1-5）。

**协审角色检查：**

- FTS、导出包、恢复候选、outbox、audit 是否保持非权威、可重建或最小化：是。FTS 回连权威；导出不写文件；恢复严格只读；outbox 队列非权威；audit 禁止正文/路径/自由错误。
- 是否有任何结论被误写成冻结：否。设计明确声明非冻结。

### Gate 3：AI 权限与信任评审 — Pass with Conditions

**主责角色检查：**

- **六维授权模型是否完整**：是。processor/purpose/location/status/expires_at/revoked_at + scope + action 白名单。
- **消费门是否覆盖所有消费入口**：是。入队前、执行前、外发/保存/索引/发布关键点均调用。
- **AI 候选是否永远未确认**：是。`create_suggestion_candidate` 声明"永远未确认"。
- **Feedback retract 是否保留历史**：是。追加写 retract，不覆盖原记录。

**协审角色检查：**

- 错误码是否存在泄露：条件通过。`E_NOT_FOUND_OR_DENIED` 统一不泄露存在性；但 `E_AUTH_AMBIGUOUS` 和 `details_token` 存在轻微泄露风险（P1-4, P2）。
- capability_status 是否泄露真实能力：否。设计声明"未知能力不枚举内部细节"，真实能力保持 disabled。
- IPC 三窄命令是否可能滑向任意 dispatcher：条件通过（P1-3）。

### Gate 4：技术可行性评审 — Pass with Conditions

**协审角色检查：**

- **P3-025 的 API/IPC 合同是否能支撑 P3-024 M-01～M-26**：条件通过。第 8 节映射表覆盖 M-01 至 M-26，但多数字段标注"尚待实际验证"。映射作为验证设计输入可接受，但不替代实测。
- **SQLite FK/触发器/约束是否可实现**：条件通过。大部分约束可实现，但 DerivationInput 列互斥约束需要显式 CHECK 组合或触发器（P1-6）。
- **DTO 双端合同是否可生成**：是。设计建议"生成 Rust/TypeScript 双端合同并做拒绝未知字段测试"，但需在壳搭建前完成。
- **是否有循环依赖**：`artifact.current_version_id` → `artifact_version` → `artifact`（延迟 FK），`derivation.output_artifact_version_id` → `artifact_version`，`content_identity.derivation_id` → `derivation`。设计已识别延迟 FK/触发器或事务校验方案，可接受。
- **是否有结论被误写成 Schema/API 冻结、真实 Tauri 启用、R-0040 关闭或下一阶段准入**：否。设计第 13 节明确声明非冻结、非启用、非关闭、非准入。

## 风险

| 风险 ID | 描述 | 级别 | 状态 |
|---|---|---|---|
| R-P3-026-01 | 授权 scope 解析算法未形式化，实现者可能将"Project scope 不覆盖 Source/Artifact 排除"误解为 project deny 不传播 | P1 | Open，需 P3-025 补充 |
| R-P3-026-02 | Feedback retract 级联规则未指定，可能导致撤回意图未完整表达或过度撤销 | P1 | Open，需 P3-025 补充 |
| R-P3-026-03 | `lifeos_control` 单一 capability 同时授予创建和销毁权限 | P1 | Open，需映射安全约束文档 |
| R-P3-026-04 | `details_token` 可能被用于旁路错误码脱敏 | P1 | Open，需生命周期约束 |
| R-P3-026-05 | `semantic_object` 类型 schema 未细化，领域语义可能被稀释 | P1 | Open，需类型 schema 草案 |
| R-P3-026-06 | `E_AUTH_AMBIGUOUS` 可能泄露对象存在性 | P2 | Open，需实现层区分 |
| R-P3-026-07 | R-0040 仍 Open/Conditional，P3-025 不构成关闭证据 | 既有 | 保持 |

## 需要 PM 决策

1. **[需 PM 确认]** 是否接受 P3-025 以 Pass with Conditions 进入 migration 设计和最小 Tauri 壳任务，条件为 P1-1 至 P1-7 在 migration 编写前以补充文档澄清？
2. **[需 PM 确认]** 是否接受 `semantic_object` 聚合继续作为 V1 评审候选，拆分条件为"任一类型专属字段超 5 个或类型间不变量冲突无法用 JSON schema 表达时必须拆表"？
3. **[需 PM 确认]** 是否将 P1-1 至 P1-7 的补充澄清作为 P3-025 的后续修订任务（不另立新任务），由原执行 Agent 或 PM 指定 Agent 完成？
4. **[需 PM 确认]** `lifeos_control` 是否应拆分为 `lifeos_mutate`（创建/追加）和 `lifeos_destruct`（撤销/断开/删除）以支持差异化 capability 授权？若拆分，将影响 Tauri capability 配置和 P3-024 M-01/M-04 验证项。

## 最终建议

1. **建议结论：Pass with Conditions**。P3-025 在核心安全不变量层面未发现 P0 级设计漏洞，可作为后续 migration 设计和最小 Tauri 壳任务的候选输入。
2. **P1-1 至 P1-7 必须在 migration 编写前澄清**。建议作为 P3-025 的后续修订（不另立新任务），修订后无需再次独立评审，但 PM 须确认修订内容覆盖全部 P1 条件。
3. **`semantic_object` 聚合可继续**，但必须记录拆分条件并在实现中监控触发。
4. **P3-025 不作为 R-0040 关闭输入**。R-0040 关闭仍需真实 Tauri/IPC 验证（P3-024 M-01～M-26）+ 进程杀死耐久 + 独立复评 + 用户确认。
5. **P3-025 不作为 Schema/API 冻结合同**。冻结前须完成 P1 补充、migration/约束验证、真实 IPC 旁路验证和 P3-024 M-01～M-26 实测。
6. **本评审完成后不自行启动后续任务**。是否进入 migration 设计或最小 Tauri 壳搭建由 PM 决定。
7. **声明**：本评审为只读独立反例评审，未修改 P3-025 主交付物、工程代码、Stitch、项目账本或冻结资产；未写 SQL migration、未创建 IPC handler、未安装/配置/运行真实 Tauri；未关闭 R-0040、未冻结 Schema/API、未进入下一阶段。
