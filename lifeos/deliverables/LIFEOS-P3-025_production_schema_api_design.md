# LIFEOS-P3-025｜生产 Schema / API 设计草案

## 1. 结论摘要

1. **[事实]** 冻结上位合同要求：用户原文不可被 AI 原地覆盖；Source 与 Artifact 分离；AI/算法输出必须可追到 Derivation 及完整输入集；Feedback 追加留痕；消费前重检 Project、Source、精确版本、双级 generation、tombstone、evidence、lease、purpose、location、processor；FTS、导出投影和恢复候选均不得成为权威或复活旧数据。
2. **[建议｜生产候选]** 采用单机 SQLite 权威库，按“权威内容—控制账本—派生/索引—任务”分责。`ArtifactVersion` 保存不可变正文；当前指针、授权、反馈与 tombstone 决定可消费性；FTS 只保存可重建投影并回连权威表。
3. **[建议｜生产候选]** IPC 采用窄命令、统一响应包络、服务端重建可信上下文、默认拒绝。Renderer 提交的 ID、版本、generation、purpose 等全部视为不可信断言，不能提交 raw SQL、任意路径或“已授权”布尔值。
4. **[推断]** 下述设计足以作为“最小 Tauri 壳”的实现输入，但尚未通过真实 Tauri、跨进程竞态、崩溃耐久、路径攻击或正式恢复验证。
5. **[非冻结声明]** 本文不冻结 Schema、API、表名、枚举、Tauri capability、导出格式或 SLA；不运行 Tauri、不启用真实能力、不关闭 R-0040、不进入下一阶段。

## 2. 设计边界与共同约定

- **Must 范围**：单用户、单设备、本地优先、合成数据；SQLite + FTS-first；云/第三方、向量、同步、多设备、真实 Vault、文件导出、L3、外部用户默认关闭。
- 主键使用不可枚举的 128-bit 随机 ID（数据库中 `TEXT`）；时间统一为 UTC epoch milliseconds `INTEGER`；布尔值为 `INTEGER CHECK (value IN (0,1))`。
- 所有可变权威实体至少含 `id, generation CHECK(generation>=1), status, created_at, updated_at`。版本实体另含聚合内单调 `version_no>=1`；正文哈希为 `sha256:<hex>`。
- `generation` 是消费 fencing token，不等同内容版本：权限/删除/来源可用性或当前版本变化导致旧消费上下文失效时递增；版本正文永不更新。tombstone 的 generation 大于等于请求快照即拒绝。
- 枚举均用 `CHECK` 或引用表；`PRAGMA foreign_keys=ON`；写事务用 `BEGIN IMMEDIATE`；关键写入与必要 outbox 同事务提交。数据库错误文本不得原样穿过 IPC。
- 每个 IPC 请求含 `request_id`；写命令另含 `idempotency_key` 和适用的 `expected_version_id/expected_generation`。响应固定为 `{request_id, ok, data?, error?}`，错误只含允许列表 `code, safe_message, retryable, details_token?`。

## 3. 生产候选 Schema 总览

### 3.1 权威内容与语义对象

| 表 / 实体 | Must 字段（除共同字段外） | 关键约束与定位 |
|---|---|---|
| `project` | `name, purpose, status, last_focused_at` | Project 是恢复上下文，不是权限根；状态限 draft/active/paused/completed/archived/cancelled。|
| `source` | `kind, stable_key, display_locator, access_status, license_status, generation` | `UNIQUE(kind,stable_key)`；定位显示值与实际路径 token 分离；断开不等于删 Artifact。|
| `artifact` | `primary_source_id NULL FK, current_version_id, kind, status, generation` | 不把 Project 单列外键当唯一归属；当前版本必须属于本 Artifact（延迟 FK/触发器或事务校验）。|
| `artifact_version` | `artifact_id FK, version_no, source_id NULL FK, content_blob, content_hash, content_time, captured_at` | `UNIQUE(artifact_id,version_no)`，hash 建普通索引（允许用户再次写入相同内容形成新版本）；UPDATE 触发器禁止改正文；DELETE 仅在支配性 tombstone 已 `active_blocked` 后由受控清理事务放行，或采用可验证的密钥销毁。|
| `content_identity` | `artifact_version_id PK/FK, identity_kind, author_kind, origin_actor_ref NULL, derivation_id NULL FK` | 一版本恰一身份；identity 限 user_original/user_edited/external_original/external_reference/quoted_excerpt/ai_generated/ai_inference/ai_suggestion；AI 类必须有 Derivation，用户原文不得有 AI derivation。|
| `artifact_project_link` | `artifact_id FK, project_id FK, link_identity, confirmation_status, generation` | `UNIQUE(artifact_id,project_id,link_identity)`；候选归属不授予权限，不得把零/多 Project 压成单一归属。|
| `semantic_object` | `object_type, project_id NULL FK, current_version_no, origin_identity, business_status, evidence_status, derivation_id NULL FK` | V1 以受控聚合承载 Assertion/Decision/Action/Event；类型专属字段可后续拆表。来源身份、用户认可、业务状态、证据状态、派生状态保持正交。|
| `semantic_object_version` | `object_id FK, version_no, payload_json, content_hash, created_by_kind` | `UNIQUE(object_id,version_no)`；修订追加版本，不覆盖历史。JSON 必须有版本化 schema 校验，不允许任意未验证 payload。|

### 3.2 控制、派生、关系与任务

| 表 / 实体 | Must 字段（除共同字段外） | 关键约束与定位 |
|---|---|---|
| `authorization` | `grantor_ref, processor, purpose, location, status, version_no, generation, valid_from, expires_at NULL, revoked_at NULL, policy_version, retention_until NULL` | 状态 proposed/granted/active/expired/revoked/superseded；`expires_at>valid_from`；同一判定必须命中唯一当前 allow，未知/多条冲突均拒绝。|
| `authorization_scope` | `authorization_id FK, effect, project_id/source_id/artifact_id NULL` | 每行恰有一个 scope 目标；deny 优先；Project scope 不覆盖 Source/Artifact 排除。|
| `authorization_action` | `authorization_id FK, action` | 动作限 read/parse/index/derive/export_candidate/restore_evaluate/create_candidate/internal_write 等白名单；确认 Feedback 不扩权。|
| `derivation` | `project_id NULL FK, kind, output_artifact_version_id NULL FK, status, purpose, location, processor, workflow_version, model_version NULL, authorization_id FK, authorization_generation, constraint_hash, rebuildable, generated_at, stale_reason NULL, supersedes_id NULL FK` | AI/算法输出必须有记录；`evidence_version_id` 若保留仅作显示指针，不能替代完整输入集。|
| `derivation_input` | `derivation_id FK, input_type, artifact_version_id NULL FK, semantic_object_id NULL FK, feedback_id NULL FK, source_id NULL FK, artifact_generation NULL, source_generation NULL, input_content_hash` | 一个输入列恰非空；主键为 `(derivation_id,input_type,input-id)`；输入集非空、完整且用于 ID/重检；多输入约束取交集/最严格值。|
| `derivation_constraint` | `derivation_id PK/FK, allowed_projects_json, allowed_purposes_json, allowed_locations_json, allowed_processors_json, sensitivity, disclosure, retention_until NULL, training_allowed, source_license_rule` | JSON 为规范化排序集合并计算 `constraint_hash`；不能合并则拒绝或用合法子集产生新 Derivation。|
| `feedback` | `target_type, target_id, target_version, kind, user_text NULL, retracts_feedback_id NULL FK, idempotency_key, applied_at` | 只追加，不 UPDATE；kind 限 confirm/reject/correct/ignore/complete/defer/retract；retract 必须指向较早有效 Feedback；`UNIQUE(idempotency_key)`；当前认可由事件折叠得到。|
| `important_link` | `project_id NULL FK, from_type/from_id/from_version, to_type/to_id/to_version, relation_type, link_identity, confirmation_status, generation, derivation_id NULL FK` | 端点不可相同；AI link 必须有 Derivation；用户确认 link 必须有有效 Feedback；Project 仅为展示上下文。|
| `link_evidence` | `link_id FK, artifact_version_id FK, source_id FK, artifact_generation, source_generation, evidence_role` | `UNIQUE(link_id,artifact_version_id,evidence_role)`；至少一条当前有效证据才能进入重要关系消费路径。|
| `tombstone` | `subject_type, subject_id, generation, command_id, reason_code, blocked_at, cleanup_status` | `PRIMARY KEY(subject_type,subject_id)`；只含不可还原最小信息；generation 只增；状态 accepted/active_blocked/cleanup_pending/cleanup_failed/vendor_limited/cleaned/no_cleanup_required。|
| `audit_entry` | `action_code, scoped_actor_ref, scoped_subject_ref, authorization_version NULL, result_code, occurred_at, correlation_id` | 追加式；禁止正文、路径、Project 名、URL、可猜 hash、请求体、自由错误、向量或模型输入输出。|
| `outbox_job` | `job_type, subject_type, subject_id, subject_generation, payload_ref, status, attempts, available_at, lease_owner NULL, lease_generation, lease_expires_at NULL, idempotency_key, last_error_code NULL` | `UNIQUE(idempotency_key)`；队列非权威；领取/完成用 `lease_generation` CAS；执行前重新过消费门；死信不解除活跃阻断。|
| `submission` | `idempotency_key PK, command, result_subject_id, result_version_id NULL, committed_at` | 捕获/控制/反馈写幂等回执；同 key 不同 payload hash 返回冲突。|

### 3.3 FTS / SearchIndex 与索引

- `artifact_fts` 为 FTS5 虚表：`artifact_version_id UNINDEXED, artifact_id UNINDEXED, body`；只索引当前可消费版本。`search_index_state(artifact_version_id PK, artifact_generation, source_generation, indexed_hash, status, updated_at)` 记录投影代际，不保存额外权威语义。
- 搜索流程必须先取 FTS 候选 ID，再联结 Artifact/Version/Source/Authorization/Tombstone 做当前重检；不得把 FTS 命中直接返回。重建采用新 shadow index 后切换或分批代际，长维护不得阻塞捕获。
- 最小索引：`artifact(current_version_id,status)`、`artifact_version(artifact_id,version_no DESC)`、`artifact_project_link(project_id,confirmation_status)`、`authorization(processor,purpose,location,status,expires_at)`、各 scope 目标索引、`derivation(project_id,status,generated_at)`、`derivation_input` 各输入 FK、`feedback(target_type,target_id,target_version,applied_at)`、`important_link(project_id,status)`、`tombstone(subject_type,subject_id,generation)`、`outbox_job(status,available_at,lease_expires_at)`。

## 4. generation / version / 消费门规则

统一门函数 `authorize_and_resolve(command, refs, intent, now)` 必须在入队前、执行前，以及外发/保存输出/索引/发布等关键点调用：

`ALLOW = ids_resolve ∧ exact_versions ∧ generations_match ∧ no_dominating_tombstone ∧ source_usable ∧ evidence_current ∧ lease_current_if_job ∧ unique_authorization_match ∧ purpose/location/processor_match ∧ policy_envelope_pass`

任一项为 false 或未知均拒绝。写操作在事务内最后一次重检并使用 `expected_generation`；0 行更新视为竞态失败。Source/Artifact generation 变化会将其依赖 Derivation、Link evidence、FTS state 与未执行 job 标 stale/cancelled；重建产生新 Derivation/投影，不修改旧身份。删除/撤回先在同一权威事务写 tombstone/授权状态、递增 generation、登记阻断/清理 jobs；只有所有活跃读取、搜索、建议、队列、导出/恢复入口已拒绝后才可报告 `active_blocked`。

## 5. Tauri IPC / 本地 API 命令草案

所有返回均用共同包络；下表是领域命令，不等于直接增加同数量的 Tauri invoke。为继承 P3-024 的“三窄命令”候选，可将其映射为版本化、可穷举的 `lifeos_read`、`lifeos_export_candidate`、`lifeos_control` 三个 invoke DTO 联合；联合内未知 `action` 仍返回 `E_UNKNOWN_COMMAND`，不能变成任意 dispatcher。最终映射需独立评审。下表的“写”指权威/控制状态写，审计最小追加另列。参数中的 `expected_*` 只用于发现竞态，服务端仍须自行查询权威值。

| 命令 | 输入 → 输出 | 重检 / fail closed | 写与派生影响 |
|---|---|---|---|
| `capture_original` | `{idempotency_key, source_token?, project_ids[], title?, original_text}` → `{artifact_id,version_id,content_hash,saved_at,deduplicated}` | 输入大小/身份、source token、Project 存在但不扩权；提交失败不得返回 saved | **写** Source/Artifact/Version/Identity/Project link/Submission；同事务登记 FTS outbox；AI 不改原文。|
| `read_artifact` | `{artifact_id, version_id?, project_context_id, purpose}` → 内容身份、版本、来源最小视图 | Project/source/version/generation/tombstone/purpose/location/processor/auth；不存在与无权统一 `E_NOT_FOUND_OR_DENIED` | 权威不写；高风险读取可追加最小 audit；不触发 FTS。|
| `search` | `{query, project_id, purpose, cursor?, limit}` → `{hits[],next_cursor,index_freshness}` | 每个 FTS 候选逐项回连全部消费门；空合法，不泄露被拒对象存在性 | 不写权威；可写最小 audit；FTS 过期返回合法子集/缺口。|
| `create_suggestion_candidate` | `{project_id,evidence_refs[],purpose,idempotency_key}` → Derivation 候选、完整 evidence、缺口 | 完整输入集、版本/双 generation/evidence/auth/purpose/location/processor；证据不足返回 no_candidate | **写** Derivation/Input/Constraint，必要时输出 ArtifactVersion；登记派生/FTS outbox；永远未确认。|
| `record_feedback` | `{idempotency_key,target_ref,kind,user_text?,expected_target_version}` → `{feedback_id,effective_state}` | 目标/版本/Project/evidence/tombstone/auth；complete/defer 只允许已确认 Action；correct 不改原文 | **追加写** Feedback；重算投影；correct/reject 可登记依赖 stale/rebuild/FTS job。|
| `retract_feedback` | `{idempotency_key,feedback_id}` → 新 retract Feedback 与重算状态 | 原反馈归当前用户、未被有效撤回、目标/版本/generation；不得反推内容已删 | **追加写** Feedback(retract)，不覆盖原记录；登记依赖重算；不改变内容授权。|
| `create_important_link` | `{idempotency_key,project_id?,from_ref,to_ref,relation_type,evidence_refs[],identity,confirmation_ref?}` → link | 两端和全部证据的 Project/source/version/双 generation/tombstone/auth/constraint；候选 Project 不扩权 | **写** Link/Evidence；AI 候选需 Derivation，确认需有效 Feedback；必要时索引 outbox。|
| `revoke_authorization` | `{idempotency_key,authorization_id,expected_generation,scope_preview_token}` → 控制状态 | 授权版本/范围/actor/目的/位置/processor；scope preview 防止陈旧确认 | **写** revoked + generation + 最小控制/audit 记录（不是内容 tombstone）；同事务登记活跃阻断、派生/FTS/缓存清理 jobs。|
| `disconnect_source` | `{idempotency_key,source_id,expected_generation,retention_choice,preview_token}` → 断开与清理状态 | Source/actor/retention 许可/当前 generation；不得暗示已删已存内容 | **写** Source disconnected + generation；登记停止监听及合法保留/清理 jobs。|
| `delete_artifact` | `{idempotency_key,artifact_id,expected_generation,preview_token}` → `{accepted,active_blocked,cleanup_status}` | 对象/版本/actor/保留边界；事务内再次查 tombstone；外部原件边界明确 | **写** tombstone + generation + auth deny；同事务登记全部活跃阻断与物理清理 jobs；不得同步物理删后才记墓碑。|
| `export_memory_package_candidate` | `{project_id,selection_refs[],purpose}` → 内存/受控测试包投影与 exclusions | 每项重检 auth/source/version/generation/tombstone/evidence/constraint；不接收任意路径 | 不写文件；只读生成候选投影，可追加 audit；不导出可重建 FTS/向量/缓存或被删正文。|
| `evaluate_restore_candidates` | `{package_bytes_or_token,project_id}` → 每项 restorable/stale/blocked/excluded + reason codes | 先验证包版本/hash，再以当前 tombstone、撤回、授权、版本、generation、身份为准；包中状态不可信 | **严格只读**；不得写 Artifact/FTS/outbox，不执行 restore。|
| `capability_status` | `{}` → 每项 enabled/disabled/reason/contract_version | 状态由后端编译/签名配置读取，不信 Renderer；未知能力不枚举内部细节 | 不写；真实 Vault/Tauri 文件导出/云/向量/同步/L3 等保持 disabled。|
| `health_check` | `{detail_level}` → DB/FTS/outbox 的安全摘要 | 不返回路径、SQL、版本正文、密钥、对象数量小样本或自由错误 | 不写权威；只允许聚合健康信息。|

## 6. 错误码与风险映射

风险级别表示“若系统未拒绝/错误处理会造成的后果”，不是向用户展示的告警等级。

| 风险 | 允许列表错误码 | 处理合同 |
|---|---|---|
| **P0** | `E_UNKNOWN_COMMAND`, `E_NOT_FOUND_OR_DENIED`, `E_AUTH_DENIED`, `E_AUTH_AMBIGUOUS`, `E_PURPOSE_MISMATCH`, `E_LOCATION_MISMATCH`, `E_PROCESSOR_MISMATCH`, `E_VERSION_STALE`, `E_GENERATION_STALE`, `E_TOMBSTONED`, `E_EVIDENCE_INVALID`, `E_LEASE_STALE`, `E_IDENTITY_INVALID`, `E_CONFIRMATION_REQUIRED`, `E_CAPABILITY_DISABLED`, `E_SCOPE_VIOLATION`, `E_RESTORE_REVIVAL_BLOCKED` | 必须零副作用（控制命令的耐久阻断除外）、不泄露对象存在性、不可自动重试为更宽权限；任何旁路成功即 P0。|
| **P1** | `E_DURABILITY_FAILED`, `E_SOURCE_UNAVAILABLE`, `E_INDEX_UNAVAILABLE`, `E_OUTBOX_FAILED`, `E_CLEANUP_PENDING`, `E_CLEANUP_FAILED`, `E_VENDOR_LIMITED`, `E_PACKAGE_INCOMPATIBLE` | 关闭/降级对应能力；权威保存与派生失败分离；显示合法子集和诚实状态，不把失败说成完成。|
| **P2** | `E_INVALID_ARGUMENT`, `E_PAYLOAD_TOO_LARGE`, `E_RATE_LIMITED`, `E_UNSUPPORTED_FILTER`, `E_HEALTH_DETAIL_REDACTED` | 安全校验失败；可修正文案/参数后重试；若接受该输入可造成越权，则测试严重性升级 P0。|

## 7. Export / Restore package projection（候选）

候选包只含版本化 `manifest`、Project 最小投影、合法 Artifact/Version/ContentIdentity、Source 最小来源说明、有效/历史状态清楚的语义对象与 Feedback、可允许的 Link/Derivation 元数据、Authorization 最小边界说明、tombstone/撤回水位及逐项 hash。不得包含内部路径、映射密钥、日志细节、FTS/向量/缓存、不可导出的外部正文或可还原的已删派生。

恢复评估先验证包结构和 hash，再比较当前权威状态；采用“当前环境与包内更严格且更新的 tombstone/撤回优先”。结果只是候选清单，不写库；真正 restore/import 需另立命令、冲突策略、预览和用户确认，本任务不设计启用。

## 8. 与 P3-024 M-01 至 M-26 映射

| 矩阵 | 本草案提供的输入 | 尚待实际验证 |
|---|---|---|
| M-01～03 | IPC 命令白名单、未知命令错误、contract version/变更复测要求 | capability JSON 与变更门实际配置。|
| M-04～06 | 仅注册上述窄命令；capability_status 不启用 updater/sidecar | invoke/plugin 注册面及默认权限。|
| M-07～11 | 响应最小化、禁止 Renderer 可信授权；无 eval/debug 合同由壳承担 | CSP、WebView、debug/release 双包。|
| M-12～16 | 业务命令不接受 raw path；Source/导出使用后端 token | macOS/Windows/Linux 路径、symlink、模拟 Vault 零写。|
| M-17～19 | scope token、文件导出默认关闭、候选包不写文件 | 真实 scope 与授权目录/覆盖攻击。|
| M-20 | 参数 DTO、枚举/大小限制、expected version/generation、服务端重建上下文 | 真实序列化篡改与 handler 校验。|
| M-21～23 | 统一消费门、Project 不扩权、双 generation/tombstone/lease、不复活投影 | 跨进程竞态、真实导出/恢复及 ID 复用攻击。|
| M-24～26 | capability_status 后端真值；八类能力默认 disabled；接口无真实密钥/路径 | 配置、UI、IPC、运行时负测与环境扫描。|

## 9. Must / Should / Later

- **Must**：不可变 ArtifactVersion；ContentIdentity；完整 DerivationInput；追加式 Feedback；六维授权 + policy envelope；统一消费门；双 generation/tombstone；幂等写；outbox lease fencing；FTS 回连权威；只读恢复评估；窄 IPC 和允许列表错误。
- **Should**：`semantic_object` 按负载稳定后拆分 Assertion/Decision/Action/Event 表；索引 shadow rebuild；清理状态与最小 audit；包 schema/version/hash；输入大小、分页和资源上限。
- **Later**：正式文件导出/restore 写入、真实 Vault、跨平台路径 token、向量、同步、多设备、云/第三方模型、L3。Later 不是隐式授权。

## 10. 冻结前硬条件与实现前注意事项

1. 由独立评审会话反例检查 Schema/API，重点攻击多 Project、多 Source、授权冲突、Feedback 乱序/重复、tombstone 优先、lease 竞态、包复活和审计反识别。
2. PM 决定 `semantic_object` 聚合实现是否足以承接已冻结的 Assertion/Decision/Action/Event 语义；若改动核心实体边界，必须升级为“需 PM 确认”，本文不能决定。
3. 用 migration 草案验证 SQLite FK/触发器、循环依赖、正文删除策略、WAL/backup；用 property/故障注入验证事务、generation CAS、outbox 幂等、长 FTS rebuild 与进程杀死。
4. 最小 Tauri 壳只能在另立授权任务后搭建；handler 必须共享后端服务层，不能在 IPC 层复制或简化消费门。命令名、DTO、error code 应生成 Rust/TypeScript 双端合同并做拒绝未知字段测试。
5. 正式冻结前须完成 P3-024 M-01～26 的真实 debug/release 及目标平台验证，P0=0，并由 PM 验收；R-0040 关闭还需独立复评和用户确认。
6. **本任务完成后仍不允许实际安装、配置或运行 Tauri**：任务卡未授权工程或工具链变更，且 Schema/API 尚未独立评审，真实 capability/IPC、耐久和目标平台条件均未验证。

## 11. 角色检查点与关卡自审

- **技术架构 / 数据模型主责：条件通过（设计层）**。H1-H9/T-ARCH 已映射；Must/Should/Later、权威/派生/任务分责、索引与约束明确。尚无 migration、性能、崩溃或真实 IPC 证据。
- **AI 信任与安全协审：条件通过（合同层）**。五类以上内容身份、完整输入、六维授权、对象级反馈、四命令、活跃阻断和不复活保留；没有启用 L3/外发/真实能力。
- **QA / Evidence 协审：条件通过（可测设计层）**。错误码映射 P0/P1/P2，M-01～26 有追踪；实际测试/evidence 仍待后续任务。
- **体验设计协审：条件通过（状态语义层）**。保存、无候选、权限不足、stale、证据失效、清理中/失败可被 UI 诚实表达；具体 UI/文案未冻结。
- **Gate 2：Pass with Conditions（候选 Schema 设计层）**；条件为独立反例评审及 migration/约束验证。
- **Gate 3：Pass with Conditions（API 信任合同层）**；条件为真实 IPC 旁路、撤回竞态和默认关闭负测。
- **Gate 4：Pass with Conditions（实现输入层）**；条件为最小壳、SQLite 耐久/备份、M-01～26 实测。以上均不是冻结或能力启用结论。

## 12. 需 PM / 用户确认与后续建议

### 需 PM 确认

1. 是否接受本草案进入独立反例评审，作为后续 migration 设计与最小 Tauri 壳任务的候选输入，而非冻结资产。
2. 是否接受 V1 先用版本化 `semantic_object` 聚合承载 Assertion/Decision/Action/Event；若要求现在拆成四组生产表，将影响实现复杂度，但不得改变既有领域语义。
3. 是否接受正式 restore 写命令、文件导出路径、清理 SLA 与目标平台继续留在后续任务。

### 后续任务建议（不自行启动）

1. WorkBuddy 独立反例评审本草案，输出 Gate 2/3/4 条件与 P0 攻击清单。
2. PM 验收后另立 SQLite migration/合同测试任务；仍只用合成数据。
3. 上述通过后再另立最小 Tauri 壳任务，随后迁移 P3-024 M-01～26；真实能力仍须独立启用门。

## 13. 范围与变更声明

本任务仅创建本文档。未修改工程、Stitch、项目账本或冻结资产；未写 SQL migration、未创建 IPC handler、未安装/配置/运行 Tauri；未连接真实 Vault、真实文件或外部服务；未启用真实导出、云/第三方模型、向量、同步、多设备、L3 或外部用户；未关闭 R-0040，未冻结 Schema/API/Tauri 配置/导出格式/SLA/工程基线，未进入下一阶段。
