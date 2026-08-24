# LIFEOS-P3-027｜Schema / API 条件整改包

## 1. 结论摘要与非冻结声明

1. **[事实]** P3-026 未发现 P0，但要求在 migration、最小 Tauri 壳或真实 IPC 验证前澄清 P1-1～P1-7；P3-025 当前仍为 `Accepted but Not Frozen`。
2. **[建议]** 本补丁已逐项给出可测试的授权算法、Feedback 依赖折叠规则、严格 DTO、诊断 token、四类语义对象 schema、SQLite 互斥约束和 ContentIdentity 条件约束。是否关闭 7 项条件仍由 PM 验收决定。
3. **[建议｜需 PM 确认]** 将候选 `lifeos_control` 拆为 `lifeos_mutate` 与 `lifeos_destruct`，使创建/追加与撤销/断开/删除拥有不同 capability；因此候选 invoke 面由三类变为四类，需要轻量独立复核并同步调整 P3-024 M-01/M-04，不能由本会话单独定案。
4. **[建议]** `semantic_object` 继续作为 V1 实现候选，不改变 Assertion、Decision、Action、Event 的冻结领域语义；达到明确触发器时必须拆表。
5. **[非冻结声明]** 本文与 P3-025 合并阅读，仅为候选补充合同；不修改 P3-025，不冻结 Schema/API，不写 SQL migration，不改代码，不安装/配置/运行 Tauri，不启用真实能力，不关闭 R-0040，不进入下一阶段。

## 2. P1 条件整改总表

| 条件 | 处理结果（待 PM 验收） | 后续落点 |
|---|---|---|
| P1-1 Authorization scope | deny 全层级阻断；多 allow 规范化合并；无“更具体 allow 覆盖 deny” | DB fixture + 属性测试 |
| P1-2 Feedback retract | 显式依赖、自动失效效果、无隐式 retract 事件 | 状态折叠器 + 乱序测试 |
| P1-3 IPC DTO | 建议拆 mutate/destruct；Rust/TS 严格联合、拒绝额外字段 | 双端合同与 capability 负测 |
| P1-4 `details_token` | 默认不发；短时、一次性、会话/请求绑定、仅安全摘要 | 内存诊断存储与泄露测试 |
| P1-5 `semantic_object` | 四类型最小 schema、不可变 schema version、强制拆表触发器 | JSON Schema 与迁移设计 |
| P1-6 DerivationInput | DB 级“恰一非空”+ type/column 一致性 | SQLite CHECK + partial unique index |
| P1-7 ContentIdentity | 按 identity_kind 约束 actor/derivation 可空性 | SQLite CHECK/触发器 |

## 3. P1-1｜Authorization scope 形式化解析

### 3.1 作用域与优先规则

- 请求先由后端解析权威闭包 `R={exact artifact/version, its current source(s), explicit project context}`；候选 Project link 不进入闭包，Renderer 声称的归属不可信。
- Project、Source、Artifact 不是覆盖优先级，而是匹配集合：Artifact 最窄，Source 覆盖其当前合法子项，Project 只覆盖该明确上下文内且仍被 Source/Artifact 约束允许的对象。
- **任一当前有效、六维与 action 匹配、且 scope 命中 R 的 deny 都全局阻断。** Project deny 可阻断其上下文内请求，Source/Artifact allow 不能覆盖；Source/Artifact deny 同样阻断 Project allow。不存在“更具体 allow 胜出”。
- deny 未命中时才评估 allow。多条 allow 不自动冲突：先移除被 supersede 的旧版本，再把同一 grantor、processor、purpose、location、action 的匹配 allow 规范化为一个有效决定，约束取交集/最严格值。grantor/主体不一致、包络互斥、版本关系不明或交集不可判定时返回内部 `AMBIGUOUS` 并对外 fail closed。

### 3.2 可测试伪代码

```text
resolve(request):
  R = authoritative_resource_closure(request.refs, request.project_context)
  if R unknown or exact version/generation/tombstone check fails: DENY
  C = current authorizations matching subject, action, purpose,
      location, processor, time and policy version
  if any matching scope row in C has effect=deny and intersects R: DENY
  A = non-superseded allow grants whose scope contains the requested resource
  if A empty: DENY
  groups = group A by (grantor, processor, purpose, location, action)
  if groups.count != 1: DENY_AMBIGUOUS
  envelope = strict_intersection(groups[0].policy_and_scope_constraints)
  if envelope unknown/empty or request not contained: DENY_AMBIGUOUS
  return ALLOW(effective_authorization_ids, envelope_hash)
```

对外读取不存在、无权或 ambiguous 仍统一 `E_NOT_FOUND_OR_DENIED`；`E_AUTH_AMBIGUOUS` 仅进入受限诊断摘要，不向普通 Renderer 暗示对象存在。入队、执行、发布均重算，不复用跨 Project/processor 的决定缓存。

## 4. P1-2｜Feedback retract 与级联

新增候选关系 `feedback_dependency(feedback_id, basis_feedback_id, dependency_kind)`；`complete/defer` 必须绑定使 Action 当时有效确认的具体 Feedback，复合“编辑后确认”拆成 correction 与对修正版 confirm 两条事件。规则如下：

1. retract 永远追加新 Feedback，指向一条当前有效、较早且同一用户可撤回的 Feedback；不 UPDATE/DELETE 历史。
2. **不按时间或“同一 target”猜依赖。** retract F 后，F 的状态效果失效，并递归使显式依赖 F 的效果变为 `inactive_due_to_basis_retracted`；这是状态折叠器自动计算，不自动伪造更多 retract 事件。
3. `correct` 默认是用户独立修正，不依赖旧 confirm，故 retract confirm 不撤销 correction；若某 correction 明确基于 F，必须写 dependency 才级联。
4. `complete/defer` 的基础 confirm 被撤回后，反馈记录与现实结果证据仍留历史，但其当前工作流效果失效，Action 转为 `review_required` 或由其余有效反馈重算；不能宣称现实行为被逆转。
5. 已确认 Link 的 confirm 被撤回且无其他有效 confirm 时回到 `unconfirmed/candidate`；来源身份不变。Derivation 的确认被撤回时回到 `available_unconfirmed/feedback_retracted`，不会仅因此变成 invalid；evidence/auth/tombstone 仍可独立令其 stale/invalid。
6. 重复 retract 幂等返回原结果；乱序、环形 dependency、跨 target 依赖或指向已失效 basis 均 fail closed。

## 5. P1-3｜IPC DTO 与 capability 拆分

### 5.1 建议映射（需 PM 确认）

| invoke | 允许 action | capability 性质 |
|---|---|---|
| `lifeos_read` | read/search/capability_status/health_check | 只读、最小诊断 |
| `lifeos_export_candidate` | export candidate/evaluate restore candidates | 只生成内存候选、禁止路径写入 |
| `lifeos_mutate` | capture/create suggestion/record or retract feedback/create link | 权威创建或追加，不含删除/断源/撤权 |
| `lifeos_destruct` | revoke authorization/disconnect source/delete artifact | 高影响控制；独立 capability、preview token、expected generation、幂等键均必需 |

拆分比保留单一 `lifeos_control` 更符合最小权限，也让 Renderer 页面只能获得当前流程必要 capability。若 PM 决定仍保留三类 invoke，则 `lifeos_control` 必须整体按 destruct 权限管理，这会扩大普通创建流程的授权成本，因此不推荐。

### 5.2 严格联合合同

- Rust 使用封闭 enum，每个 variant 拥有独立 struct 并启用 `deny_unknown_fields`；TypeScript 使用同一合同生成的 discriminated union，并以 strict schema 校验。
- 先校验顶层 `contract_version` 与 `action`，再只用该 variant 的参数反序列化；禁止 `Map<String,Value>`、字段展平和 handler 内按字段猜 action。
- 未知 action/contract version → `E_UNKNOWN_COMMAND`；已知 action 的缺字段、错类型、额外字段、跨 variant 字段 → `E_INVALID_ARGUMENT`；均为零业务副作用、零 outbox、零详细解析错误回传。
- exhaustive match 缺少 variant 时构建失败；DTO 变更必须触发 capability snapshot 与 P3-024 M-01/M-04/M-20 复测。

## 6. P1-4｜`details_token` 生命周期与脱敏

- 默认省略；仅在标准错误码不足以指导本地故障处理时签发 256-bit 随机不透明 token。
- 仅绑定当前 app session、request_id、调用主体和错误码；TTL 最长 5 分钟、单次兑换，过期/重放/跨会话统一返回不可用。
- 只保存在后端内存，不进 SQLite、AuditEntry、日志、遥测或导出；进程退出立即失效。Renderer 只能通过同一会话的受限诊断动作兑换。
- 可检索内容仅为 `{public_code, operation_class, retryable, component_category, coarse_time_bucket, correlation_id}` 的安全摘要。
- 永久禁止路径/文件名、SQL/堆栈/原始错误、对象或版本 ID、Project 名、URL、正文/hash、内部状态枚举、授权匹配数量、数据库计数和密钥。底层诊断若确需原始信息，只能进入另立的开发期本地安全流程，不由 token 旁路暴露。

## 7. P1-5｜`semantic_object` 类型 schema 与拆表门

公共 envelope 固定：`payload_schema="<type>@<major>.<minor>"`、`schema_version`、`object_type`；JSON Schema 均 `additionalProperties:false`。Project、来源身份、业务/证据状态、Derivation 与 Feedback 仍在规范表中，不复制进 payload 充当权威。

| 类型 | payload 必填 | 可选但限本类型 |
|---|---|---|
| Assertion | `statement` | `valid_from, valid_until, qualification` |
| Decision | `decision_text` | `question, options_considered, rationale, validity_window`；提出身份由公共 `origin_identity` 表达，`confirmed` 必须由 Feedback 得出 |
| Action | `action_text` | `due_at, defer_until, commitment_to, result_ref`；意图身份由公共 `origin_identity` 表达，due date 不是普遍必填 |
| Event | `event_type, description, occurrence` | `occurrence` 为 `at / interval / unknown` 的严格联合；不得用 captured_at 冒充发生时间 |

版本规则：major 表示破坏性字段/不变量变化，minor 只允许向后兼容且不得放宽身份或确认规则；读取未知 major 必须 fail closed。既有 `semantic_object_version` 不原地改 JSON；确定性转换产生新版本、记录 `migrated_from_version` 与 migrator version/hash，再原子切换 current pointer。转换失败保留旧版并标 `migration_required`，不得生成貌似有效的默认值。

**强制拆表触发器**：任一类型的持久化顶层专属字段（含 optional，不含公共 envelope；嵌套对象不得用于规避计数）超过 5 个，或类型间状态/唯一性/FK/时间/确认不变量发生冲突且无法由 JSON Schema + 公共列无歧义表达时，必须在下一 migration 前拆成类型表；不得靠更多自由 JSON、应用层 if 或 nullable 公共列规避。按当前清单各类型均不超过 5 个，聚合可暂时继续。

## 8. P1-6｜DerivationInput DB 级约束

以下是设计表达，不是 migration 文件。应用层校验必须重复，但不能替代 DB 约束：

```sql
CHECK (
  (artifact_version_id IS NOT NULL) +
  (semantic_object_id IS NOT NULL) +
  (feedback_id IS NOT NULL) +
  (source_id IS NOT NULL) = 1
),
CHECK (
  (input_type='artifact_version' AND artifact_version_id IS NOT NULL) OR
  (input_type='semantic_object' AND semantic_object_id IS NOT NULL) OR
  (input_type='feedback' AND feedback_id IS NOT NULL) OR
  (input_type='source' AND source_id IS NOT NULL)
)
```

使用独立随机 `id` 作主键，并为四种引用建立 `WHERE <fk> IS NOT NULL` 的 partial unique index，分别保证同一 Derivation 不重复消费同一输入；不能以含多个 nullable FK 的复合主键代替。migration 设计须补 FK、输入类型枚举、generation 字段适用性及至少一条输入的提交时校验/延迟触发器。

## 9. P1-7｜ContentIdentity 条件约束

| identity_kind | `origin_actor_ref` | `derivation_id` | 规则 |
|---|---|---|---|
| user_original / user_edited | 可空（已知用户可用作用域化引用） | 必须空 | 不因经 AI 编辑建议而改写用户原文身份 |
| external_original / external_reference | 必填 | 必须空 | actor 指外部作者/发布主体；未知作者使用作用域化 `external:unknown`，不能用 NULL 吞掉来源 |
| quoted_excerpt | 必填 | 可空 | AI 选取时可同时记 Derivation；引用的外部主体仍不可丢 |
| ai_generated / ai_inference / ai_suggestion | 必须空 | 必填 | 模型/工作流/外部输入由 Derivation 包络承担，禁止把 AI 文本冒充外部作者原文 |

上述条件必须用 DB CHECK/触发器强制；`origin_actor_ref` 只保存不可枚举的作用域化 actor 引用，不保存路径、URL 或自由文本。ContentIdentity 约束不改变 AI 输出经用户确认后仍保留 AI 来源身份的上位规则。

## 10. P2 清洁项（Should）

1. **Idempotency namespace**：键格式候选为 `<command>@<contract-major>:<client-instance-random>:<request-random>`；数据库唯一性按 `(command, contract_major, idempotency_key)`，另存 canonical request hash。同键同 hash 返回原结果，同键不同 hash 返回 `E_IDEMPOTENCY_CONFLICT`；不得含用户/对象/路径信息。
2. **FTS 数量泄露**：search 不返回 raw hit count、过滤前数量、估算总数或空洞页；只返回可见 hits 与基于可见结果生成、绑定 query/project/auth/index generation 的不透明 cursor。内部定长批次扫描且每项回连权威。
3. **Health detail**：仅允许 `minimal|standard`。minimal 返回 overall status 与 contract version；standard 增加组件级 `ok/degraded/unavailable`、粗粒度 freshness/queue bucket。禁止精确对象数、路径、SQL、ID、插件清单或自由错误；其他值 `E_INVALID_ARGUMENT`。
4. **SemanticObjectVersion 清理**：正常修订不可 UPDATE/DELETE；内容删除先写支配 tombstone、实现 active_blocked、失效依赖，再由受控清理删除/密钥销毁 payload。仅在独立合法依据下保留不可还原的版本号/状态说明；restore 不得从旧包补回 payload。
5. **Capture 去重**：idempotency 只去重同一请求，不按 content_hash 合并用户意图。不同 idempotency 即使正文相同也可形成新 Artifact；显式 append-version 必须携带 artifact_id、expected current version/generation。相同内容的新版本合法，hash 仅用于完整性与提示，不是唯一约束。

## 11. 对 P3-025 的补充合同与分层

本文件第 3～10 节作为 P3-025 的补充合同；发生文字歧义时，在 P1/P2 指定问题范围内采用本文更严格规则，真正的上位语义冲突交 PM，不反向修改冻结领域模型或 AI 权限边界。

- **Must（进入 migration 设计前）**：P1-1、P1-2、P1-4～P1-7；严格 DTO union。若 PM采纳四 invoke，mutate/destruct 分权及相应矩阵更新同为 Must。
- **Should**：五项 P2 清洁口径进入 migration/API 合同测试，不阻塞本文文档验收，但不得在实现时遗失。
- **Later**：真实 capability 配置、SQL migration 文件、Tauri handler、真实路径/导出/restore、耐久和跨平台实测；必须另立任务。

## 12. 后续 migration 判断、角色与关卡

### 12.1 是否允许后续 migration 设计

**[建议｜需 PM 确认] 条件允许进入“SQL migration 设计任务”，不等于允许直接编写或执行 migration。** 前提是 PM 验收 P1-1～P1-7 已在设计层完整响应，并决定四 invoke 拆分。由于本文建议改变候选 Tauri capability 结构，进入最小 Tauri 壳/handler 前必须轻量独立复核；PM 可决定该复核与纯 Schema migration 设计并行还是前置。任何实际 migration 写入仍需新任务明确授权。

### 12.2 角色检查点

- **技术架构 / 数据模型：Pass with Conditions（整改设计层）**。7 项均有算法、状态规则或 DB/DTO 表达；未新增领域实体，新增的 dependency 为 Feedback 关系/实现支撑，不改变核心对象集合。
- **AI 信任与安全：Pass with Conditions**。deny 不可被更具体 allow 覆盖；撤回效果可解释；AI/外部/用户身份不混用；destruct capability 独立候选需复核。
- **QA / Evidence：Pass with Conditions**。每项可转成正反例；尚无 migration、Rust/TS DTO 或真实 IPC 证据。
- **体验设计：Pass（状态合同层）**。撤回后的 unconfirmed/review_required、诊断脱敏和搜索数量口径可诚实展示，未冻结 UI 文案。
- **Gate 2：Pass with Conditions**，待 PM 验收与 migration 约束验证。
- **Gate 3：Pass with Conditions**，待 capability 拆分轻量复核及真实 IPC 负测。
- **Gate 4：Pass with Conditions**，待 SQLite/Rust/TS 合同实现和 P3-024 矩阵实测。以上均非冻结、启用或阶段准入结论。

## 13. 需要 PM / 用户确认与后续建议

### 需 PM 确认

1. 是否认定 P1-1～P1-7 已在设计层完成整改，并允许 P3-025 + 本补丁继续作为 migration 设计输入。
2. 是否采纳四 invoke，将 `lifeos_control` 拆为 `lifeos_mutate` / `lifeos_destruct`，并安排轻量独立复核与 P3-024 M-01/M-04 更新。
3. 是否确认 `semantic_object` 暂时聚合，并采用“专属字段超过 5 个，或类型不变量冲突无法表达”即强制拆表的触发器。

### 后续任务建议（不自行启动）

- PM 验收后，可创建只产出 migration 设计/合同测试的任务；仍不得直接执行 migration。
- 对四 invoke 和 P1 整改做轻量独立复核；之后才可另立最小 Tauri 壳任务。

## 14. 范围与变更声明

本任务仅创建本独立整改文档和本地预检报告。未修改 P3-025、工程代码、Stitch、项目账本或冻结资产；未写/执行 SQL migration，未创建 handler，未安装/配置/运行 Tauri；未处理真实数据/Vault/文件，未启用文件导出、云/第三方模型、向量、同步、多设备、L3 或外部用户；未关闭 R-0040，未冻结 Schema/API/Tauri 配置/导出格式/SLA/工程基线，未进入下一阶段，未启动后续任务。
