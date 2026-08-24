# LIFEOS-P3-029｜SQL migration 设计 / 合同测试草案

## 1. 结论摘要与非实现声明

1. **[事实]** P3-028 已确认 P3-026 的 7 个 P1 条件在设计层关闭，四 invoke 可作为候选输入；本任务需承接 3 个 P2 清洁项。
2. **[建议]** 已形成足够清晰的 migration 设计输入：表的创建顺序、DB CHECK/trigger/partial index、跨表事务 guard、FTS/outbox 分责和 P0/P1/P2 合同测试均有候选合同。
3. **[建议]** `semantic_object` 继续聚合。Assertion=4、Decision=5、Action=5、Event=3 个专属顶层字段；Decision/Action 触及但未超过上限，任何新增专属字段或无法表达的不变量冲突都必须先拆表。
4. **[建议]** 明确允许 retract-of-retract，使用线性撤回链恢复被撤回效果；`feedback_dependency` 跨 target 由 DB trigger 强制；`strict_intersection` 定义为资源、时间、集合和限制包络的最严格交集，未知或空交集即拒绝。
5. **[建议｜需 PM 确认]** P3-029 经独立评审通过后，可进入“候选 SQL migration 编写任务”；不应由本任务直接编写。最小 Tauri shell/handler 仍被 migration/DTO 合同评审和 P3-024 四 invoke 矩阵补丁阻塞。
6. **[非实现 / 非冻结声明]** 本文仅含候选 DDL与测试伪代码；未创建 `.sql` 文件、未写或执行 migration、未连接数据库、未改代码、未运行 Tauri、未启用真实能力、未冻结 Schema/API、未关闭 R-0040、未进入下一阶段。

## 2. Migration 设计总览

### 2.1 分层与建议创建顺序

| 顺序 | 分层 / 候选对象 | 主要来源 | 权威性 |
|---|---|---|---|
| 00 | `schema_migration_meta`、显式 enum/check 词表 | P3-025 §2 | migration 控制元数据，非业务权威 |
| 10 | `project`, `source`, `artifact`, `artifact_version`, `content_identity`, `artifact_project_link` | P3-025 §3.1；P3-027 §9 | 原文、来源、版本、身份权威 |
| 20 | `semantic_object`, `semantic_object_version` | P3-025 §3.1；P3-027 §7 | 语义对象与不可变版本权威 |
| 30 | `authorization`, `authorization_scope`, `authorization_action`, `authorization_policy` | P3-025 §3.2；P3-027 §3 | 授权与强制政策权威 |
| 40 | `derivation`, `derivation_input`, `derivation_constraint` | P3-025 §3.2；P3-027 §8 | AI/算法来源与限制权威 |
| 50 | `feedback`, `feedback_dependency`, `important_link`, `link_evidence` | P3-025 §3.2；P3-027 §4 | 用户反馈、关系和证据权威 |
| 60 | `tombstone`, `audit_entry`, `submission`, `outbox_job` | P3-025 §3.2/4；P3-027 §10 | 控制账本权威；outbox 非权威 |
| 70 | `search_index_state`, `artifact_fts` | P3-025 §3.3 | 可删除、可重建投影 |
| 80 | secondary/partial indexes、immutability/activation/cleanup triggers | P3-027/P3-028 | DB 防线 |
| 90 | `foreign_key_check`、schema checksum、合同测试与失败回滚验收 | P3-025 §10；P3-028 | 验证证据，非能力启用 |

未来 migration 应按单一版本事务执行：校验前置 schema checksum → `BEGIN IMMEDIATE` → 创建表/索引/触发器 → 写 migration meta → `foreign_key_check` 与必要断言 → COMMIT。失败必须整体 ROLLBACK；FTS 初始重建通过事务提交的 outbox 后异步完成，不能令权威 schema 提交失败。不得把 destructive down migration 当默认回滚；回退应使用 SQLite-aware 备份和前一可验证版本，具体流程仍待实现任务验证。

### 2.2 共同字段与状态原则

- 随机不可枚举 `TEXT` 主键；UTC epoch milliseconds；`generation>=1`；枚举用 CHECK；`foreign_keys=ON`。
- 版本表 `UNIQUE(parent_id,version_no)`、正文/payload 不 UPDATE；当前指针只允许指向本聚合版本。
- `status` 不能替代 Tombstone、Feedback、Authorization 或 AuditEntry；缓存状态必须能由权威记录重算。
- 复杂跨行不变量不假装由 CHECK 解决：同一事务内用 trigger + application transaction guard；任何 guard 未知、0 行更新或竞态均 fail closed。

## 3. 表、约束、索引与强制层级

### 3.1 权威内容、来源与版本

| 对象 | Must DB 约束 / 索引 | 必须配合的事务 guard |
|---|---|---|
| Project | status CHECK；`generation>=1` | 归档不等于删除；Project link 不授予权限 |
| Source | `UNIQUE(kind,stable_key)`；access/license status CHECK；generation index | disconnect 同事务递增 generation、登记阻断/清理 outbox |
| Artifact | primary source FK；current version 可空仅限 draft；status/generation CHECK | 激活前确认 current version 属于自身；删除先写 tombstone |
| ArtifactVersion | parent FK；`UNIQUE(artifact_id,version_no)`；hash 普通索引；UPDATE 禁止 | 相同 hash 允许新版本；受控 DELETE 需支配 tombstone 已 active_blocked |
| ContentIdentity | 一版本一行；identity CHECK；条件约束见 §3.2 | AI 身份的 Derivation 必须已完整激活，不能只存在空壳 |
| ArtifactProjectLink | `UNIQUE(artifact_id,project_id,link_identity)`；confirmation CHECK | candidate 不进入授权闭包 |

Artifact/Version 循环采用“两步激活”：先插入 draft Artifact（current_version NULL），再插入 v1 与 ContentIdentity，最后以 guarded UPDATE 设置 current pointer/status active；任一步失败整事务回滚。AI 输出涉及 Derivation 循环时同样先创建 draft 记录，只有完整 inputs、identity 和 output 互相可达后才能激活。

### 3.2 ContentIdentity 条件 CHECK

候选 DB 表达如下（仅设计片段）：

```sql
CHECK (
  (identity_kind IN ('user_original','user_edited')
    AND derivation_id IS NULL)
  OR (identity_kind IN ('external_original','external_reference')
    AND origin_actor_ref IS NOT NULL AND derivation_id IS NULL)
  OR (identity_kind='quoted_excerpt'
    AND origin_actor_ref IS NOT NULL)
  OR (identity_kind IN ('ai_generated','ai_inference','ai_suggestion')
    AND origin_actor_ref IS NULL AND derivation_id IS NOT NULL)
)
```

`origin_actor_ref` 仅为作用域化不可枚举引用；`external:unknown` 是显式受控值而不是 NULL。另设 trigger 阻止 user identity 携带 AI Derivation、阻止 AI identity 指向非 active/输入为空的 Derivation。

### 3.3 SemanticObject 与版本

- `semantic_object(object_type, current_version_no NULL, origin_identity, business_status, evidence_status, generation, status)`；四个状态维度不得合并。
- `semantic_object_version(object_id,version_no,payload_schema,schema_major,schema_minor,payload_json,content_hash,migrated_from_version_no,migrator_version,migrator_hash,created_at)`；`UNIQUE(object_id,version_no)`。
- DB CHECK 至少执行 `json_valid`、object_type/schema major 白名单、关键字段类型和 `additionalProperties:false` 的 top-level key 白名单；完整 JSON Schema 在应用事务入口重复验证。未知 major、非法 key 或类型错配不得激活 current pointer。
- migration 转换生成新版本，不原地改 payload；失败保留旧版并设置 `migration_required`，旧版不得被当作已升级数据。
- 正常修订禁止 DELETE；物理清理必须先有支配 tombstone、active_blocked 和依赖失效，restore 不得从旧包补回 payload。

当前字段复查：Assertion 4；Decision 5；Action 5；Event 3。公共 `origin_identity/business_status/evidence_status/project/feedback` 不重复塞入 payload。**聚合继续有效；Decision/Action 新增任一持久化顶层专属字段即超过 5，候选 SQL 编写必须暂停并提出拆表。** 嵌套对象不得规避计数。

### 3.4 DerivationInput 恰一引用

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

随机 `id` 为 PK；四个 `UNIQUE(derivation_id,<typed_fk>) WHERE <typed_fk> IS NOT NULL` partial indexes 防重复。应用校验不能替代 CHECK。SQLite 无通用 deferred assertion，故 Derivation 先为 draft；UPDATE 为 active 的 BEFORE trigger 必须确认至少一条 input、每条精确 version/generation/hash 可解析且 constraint 已存在。

### 3.5 Feedback、retract 与 dependency（P3-028 P2-1/P2-2）

Feedback 增加单调 `event_seq UNIQUE`、`basis_feedback_id NULL`、`retracts_feedback_id NULL`。DB CHECK：只有 retract 可填 `retracts_feedback_id`；complete/defer 必须填指向 confirm 的 basis；其他 kind 不得伪装。Feedback 只 INSERT，UPDATE/DELETE trigger 一律阻断。

**retract-of-retract 允许**，但强制形成线性链：同一 Feedback 最多被一个后续 retract 直接指向（partial unique index on `retracts_feedback_id`）；新 retract 必须与目标同 actor、同 `target_type/id/version`，且目标 `event_seq` 更小。链尾有效；父事件仅在其直接 retract 子事件无效时有效，因此偶数层撤回恢复原事件效果，奇数层撤回取消原效果。重复请求由 idempotency 返回原结果，不分叉新链，不删除任何历史。

`feedback_dependency` 使用 `PRIMARY KEY(feedback_id,basis_feedback_id)`、两端 FK、禁止 self。**跨 target 不能由 CHECK 跨行判断，必须由 BEFORE INSERT trigger 查询两端并强制 target tuple 完全相同、basis.event_seq 更小；`requires_confirmation` 还要求 basis.kind=confirm。** 应用事务再做相同检查与折叠，但不能取代 trigger。依赖图因严格递增 event_seq 无环；basis 被有效 retract 后，依赖效果自动变 `inactive_due_to_basis_retracted`，不新增伪 retract。

### 3.6 Authorization 与 `strict_intersection`（P3-028 P2-3）

持久化支撑：Authorization 主表保存 grantor/processor/purpose/location/status/version/generation/时效/policy_version；Scope 行用 exact-one target CHECK + effect；Action 行白名单；一对一 `authorization_policy` 明确 retention mode/deadline、sensitivity rank、training/external-send boolean、recipient/region/disclosure/source-license 集合版本和数量/频率上限。NULL 不表示“任意”；无限期必须由显式 mode 表达，未知字段即不可判定。

对同一唯一分组 `G=(grantor,processor,purpose,location,action)` 的当前 grants：

```text
D = union(all matched deny scopes)
S_i = union(allow scopes of grant i)
S_effective = intersection(S_i for all i in G) minus D
T_effective = [max(valid_from_i), min(expires_at_i or explicit infinity))
set dimension = mathematical intersection of explicit allow sets
retention deadline / quantity / frequency ceiling = minimum
required sensitivity protection = maximum rank
training_allowed / external_send_allowed = logical AND (false wins)
```

请求资源不在 `S_effective`、时间区间空、集合交集空、存在多于一个 G、任一值未知/无法比较、policy version 不可验证，结果均为 DENY/内部 AMBIGUOUS；外部仍使用 `E_NOT_FOUND_OR_DENIED`。规范化结果计算 canonical hash，缓存键必须包含全部 Authorization IDs/generations、policy version、资源闭包 hash；缓存非权威且在入队/执行/发布重算。任何层级匹配 deny 在交集前全局阻断，具体 allow 永不覆盖 deny。

Activation trigger/事务 guard 要求 Authorization 从 proposed→active 前至少一条 scope、一条 action、一条完整 policy；旧版本必须显式 superseded，禁止两个未知关系的 active grant 被静默合并。索引至少覆盖 scope 的三类 target+effect、Authorization 六维+status+expiry、action。

### 3.7 Tombstone、Outbox、Audit 与 FTS

- Tombstone `(subject_type,subject_id)` 唯一、generation 单调；`active_blocked` 只在读取/搜索/建议/队列/导出/恢复消费门全部拒绝后由事务 guard 设置。cleanup pending/failed/vendor_limited 不得解除阻断。
- 删除事务顺序：写/升级 tombstone → 递增目标 generation/status → 撤销相应授权 → stale 依赖 → 同事务登记幂等清理 jobs/audit → 提交；物理清理异步。
- Outbox `UNIQUE(idempotency_key)`；lease CAS 使用 `lease_generation`，完成时再次匹配 subject generation 与 lease；队列永不成为权威。
- Audit 仅允许列表字段；禁止正文、路径、URL、自由错误、可猜 hash、请求体和模型内容。
- FTS 不用 trigger 与权威写强耦合；outbox 投影。search 只返回重检后的 hits 和授权可见 cursor，不返回 raw/过滤前 hit count。`search_index_state` 记录双 generation/hash/status，旧代际不消费。

## 4. 索引、触发器与事务 Guard：Must 清单

| 类别 | Must |
|---|---|
| CHECK | 枚举/generation；ContentIdentity 条件；DerivationInput exact-one+type；scope exact-one；Feedback kind/引用字段；JSON/schema 基础合法性 |
| Unique/partial index | 聚合版本号；Source stable key；Derivation typed input；retract direct child；Feedback idempotency；Outbox idempotency；Link evidence；Submission namespace+key |
| Trigger | Artifact/Semantic/Feedback immutability；current pointer ownership；Derivation activation completeness；feedback retract/dependency same-target/sequence；受控 payload 清理；Authorization activation completeness |
| Transaction guard | authoritative closure、strict intersection、generation/tombstone、跨表状态折叠、active_blocked 全路径证明、AI output 循环激活、outbox 同事务登记 |
| 应用层重复校验 | 完整 JSON Schema、Rust/TS DTO、canonical request hash、资源/速率上限、用户可理解 preview |

## 5. 四 invoke / DTO 合同测试草案

共同包络为严格 `{contract_version,request_id,action,payload}`，各层拒绝未知字段；Renderer 字段均是不可信断言，后端重建上下文。

| Invoke | 正测 | 必测反例 / 期望 |
|---|---|---|
| `lifeos_read` | read/search/health/capability 的合法 variant | 未知 action、destruct action、额外/跨 variant 字段、错误 contract → `E_UNKNOWN_COMMAND`/`E_INVALID_ARGUMENT`，零副作用 |
| `lifeos_export_candidate` | 内存 export candidate、只读 restore evaluation | raw path、write/overwrite、mutate 字段、被删包复活 → 拒绝；零文件写、零 outbox |
| `lifeos_mutate` | capture/suggestion/feedback/retract/link 严格 DTO | delete/revoke/disconnect action、同幂等键不同 hash、伪造 identity/project/auth → 拒绝；无 destruct capability |
| `lifeos_destruct` | revoke/disconnect/delete 且 preview token、expected generation、idempotency key 全匹配 | 任一必填缺失/过期/错对象、跨 variant 字段、旧 generation、无 capability → P0 拒绝；零部分副作用 |

双端合同要求：Rust 封闭 enum+每 variant `deny_unknown_fields`；TypeScript 由同一版本源生成 strict discriminated union；exhaustive match 缺 variant 构建失败。每个 variant 至少一正测及缺字段、错类型、额外字段、未知 action、错误 major、字段篡改六类反例。

## 6. P3-024 M-01 / M-04 / M-20 设计补丁建议

| 项 | 候选新合同 | P0 断言 |
|---|---|---|
| M-01 | capability 声明只允许四窄 invoke；按页面/流程最小授予，普通 capture 页面不得获得 destruct | 任意通用文件/DB/shell/network 或越级 invoke 可达即 P0 |
| M-04 | invoke handler 只注册 read/export_candidate/mutate/destruct；未知 invoke 默认拒绝 | 任意未注册 handler 可调用，或 mutate 可路由 destruct，即 P0 |
| M-20 | 四 DTO 各自正测；未知/额外/跨 variant/错误 contract；destruct 三项强制字段；服务端重建 Project/auth/version/generation | 任一参数篡改被接受、解析失败产生副作用或泄露细节即 P0 |

这是 P3-024 的候选设计补丁，不修改其原文件，不代表 capability JSON、handler、debug/release 或目标平台已验证。

## 7. P0 / P1 / P2 合同测试清单

### 7.1 P0（正式写 migration 前必须先定义，后续实现零失败）

| ID | 目标 / 输入 | 期望结果 | 覆盖风险 | 对应约束 |
|---|---|---|---|---|
| DB-P0-01 | UPDATE ArtifactVersion/SemanticObjectVersion/Feedback | DB 拒绝、原记录/hash 不变 | 原文/历史被静默覆盖 | immutable trigger、append-only |
| DB-P0-02 | ContentIdentity 各合法/非法 actor+derivation 组合 | 合法通过；混用全拒绝 | 身份/来源混淆 | 条件 CHECK、AI identity trigger |
| DB-P0-03 | DerivationInput 0、2、错 type、重复 typed ref | CHECK/unique 拒绝 | 输入断链或伪证据 | exact-one/type CHECK、typed partial unique |
| DB-P0-04 | 激活 0 input 或无 constraint Derivation | activation 拒绝 | 空壳 AI 输出 | activation trigger、事务 guard |
| DB-P0-05 | retract chain、分叉、乱序、跨 actor/target | 线性合法；其余 trigger 拒绝 | 用户权威状态漂移 | retract partial unique、same-target/actor、event_seq |
| DB-P0-06 | dependency 跨 target/self/后向序列 | trigger 拒绝 | 撤回级联越界 | dependency PK/FK、BEFORE INSERT trigger |
| DB-P0-07 | project deny+source allow、source deny+project allow | 均 DENY | deny 被具体 allow 绕过 | deny union 全局阻断 |
| DB-P0-08 | 多 allow 交集、空集、未知 policy、多 G | 仅唯一可判定非空交集 ALLOW | 授权歧义 | `strict_intersection`、unknown/empty/multi-G deny |
| DB-P0-09 | 旧 version/generation 与新 tombstone 并发 | 0 行更新/消费拒绝 | 删除竞态复活 | expected generation、tombstone gate、CAS |
| DB-P0-10 | current pointer 指向他者版本/未知 schema major | trigger 拒绝、保持旧 pointer | 跨对象污染或未知结构误读 | pointer ownership trigger、schema major 白名单 |
| DB-P0-11 | FTS 含已删/撤权候选 | 回连过滤且不泄露 raw count | 索引绕权或存在性泄露 | authoritative post-filter、opaque count/cursor |
| DB-P0-12 | 旧导出包在当前 tombstone 后评估 | blocked/excluded，零写入 | 恢复复活已删内容 | restore evaluation、tombstone supremacy |
| DB-P0-13 | Outbox 旧 lease/旧 subject generation 完成 | CAS 失败，不发布 | 队列越权发布 | lease/subject generation CAS |
| DB-P0-14 | 同 idempotency key 不同 canonical hash | 冲突拒绝、原结果不变 | 重放替换原请求 | idempotency unique、canonical request hash |
| IPC-P0-01 | 四 invoke 跨 capability/action 调用 | 未授权/未知命令，零副作用 | capability 越权 | 四窄 capability、handler allowlist |
| IPC-P0-02 | 未知/额外/跨 variant/错误 contract | 严格拒绝，无解析详情 | 任意 dispatcher 接受畸形输入 | strict DTO、deny unknown fields、版本 gate |
| IPC-P0-03 | destruct 缺/错 preview、generation、idempotency | 拒绝、无部分事务/outbox | 重大操作未经确认 | destruct 三项必填、原子事务 |

### 7.2 P1

| ID | 目标 / 输入 | 期望结果 | 覆盖风险 | 对应约束 |
|---|---|---|---|---|
| CT-P1-01 | migration 任一中间断言失败 | 整体 rollback，schema meta/checksum 不前进 | 半完成 schema 无法识别或回退 | 单版本事务、checksum、失败回滚 |
| CT-P1-02 | draft Artifact/Derivation/SemanticObject 未完成激活 | 所有消费入口不可见 | 空壳记录被读取或发布 | 两步激活、activation trigger、status gate |
| CT-P1-03 | JSON schema minor/major 转换成功与失败 | 新版本原子切换或标记 `migration_required`，旧 payload 不变 | 静默改写、未知版本误读 | 不可变版本、current pointer guard、schema 白名单 |
| CT-P1-04 | cleanup 为 pending/failed/vendor_limited | `active_blocked` 继续成立，状态诚实 | 清理失败导致删除对象复活 | Tombstone 消费门、cleanup 与阻断解耦 |
| CT-P1-05 | `details_token` 过期/重放/跨会话，且 payload 含禁止字段 | 不可兑换、零敏感字段输出 | 错误详情泄密或跨会话重放 | token 会话绑定/TTL/单次使用、Audit 字段白名单 |
| CT-P1-06 | FTS 索引或 outbox 投影故障 | 权威捕获事务仍可提交，freshness 明确 degraded | 派生故障拖垮原始记录 | 权威写与投影解耦、outbox 幂等、状态诚实 |

### 7.3 P2

| ID | 目标 / 输入 | 期望结果 | 覆盖风险 | 对应约束 |
|---|---|---|---|---|
| CT-P2-01 | retract-of-retract 偶/奇深度链及同幂等键重放 | 奇数层取消、偶数层恢复；重放回执一致且不新增分支 | 撤回语义漂移或历史分叉 | 线性 retract 链、partial unique、event_seq、idempotency |
| CT-P2-02 | 相同 Authorization 集合以不同输入顺序求交 | canonical intersection 与 hash 完全一致 | 缓存键不稳定或顺序影响授权 | `strict_intersection`、canonical sort/hash、全维度 cache key |
| CT-P2-03 | search 分页含撤权/删除候选和大量过滤项 | 无 raw count/过滤空洞泄露；cursor 绑定 query/project/auth/index generation | 存在性侧信道和旧游标越权 | post-filter、opaque cursor、generation binding |
| CT-P2-04 | `health_check` 使用 minimal/standard、未知 level | 合法 level 返回去敏状态；未知值拒绝；不含精确计数、路径、ID、SQL | 诊断接口泄密 | DTO enum、输出字段白名单、最小披露 |
| CT-P2-05 | Decision/Action 当前 5 字段及新增第 6 字段 | 当前检查通过；新增字段令设计检查失败并要求拆表 | 聚合无限膨胀、类型约束失真 | 顶层专属字段上限、嵌套不得规避、拆表硬门 |

**本任务发现的问题状态：P0=0、P1=0；P3-028 三项 P2 已全部形成设计处理与测试入口。** 该结论只针对文档覆盖，不代表测试已实现或运行。

## 8. 后续准入判断、角色与关卡

### 8.1 后续任务判断

- **候选 SQL migration 编写：Conditional Yes。** 必须先由独立评审确认本设计无遗漏，再由 PM/用户另立明确允许创建 `.sql` 的任务；实际编写仍只可使用合成空库/夹具，且需把 §7 P0 测试先落成或同步落成。
- **最小 Tauri shell/handler：仍阻塞。** 至少等待：P3-029 独立评审、四 invoke M-01/M-04/M-20 补丁被后续任务采纳、DTO 合同实现与 capability 任务明确授权；真实 Tauri 安装/运行仍未获本任务授权。
- **Schema/API 冻结与 R-0040：均不允许。** 仍需 migration/约束验证、真实 IPC/debug-release/目标平台矩阵、耐久验证、独立复评和用户确认。

### 8.2 角色检查点

- **数据 / 领域模型负责人：Pass with Conditions（设计层）**。核心对象、版本、来源、身份、反馈和删除语义有持久化落点；`semantic_object` 未触发拆表，但已在上限边界。
- **技术架构负责人：Pass with Conditions**。创建顺序、循环激活、DB/transaction 分责、回滚与 FTS/outbox 隔离可实现；尚无可执行 migration 或耐久证据。
- **AI 信任与安全：Pass with Conditions**。deny/strict intersection、撤回链、ContentIdentity、四 invoke 与 tombstone 均 fail closed；真实 IPC 未验证。
- **QA / Evidence：Pass with Conditions**。17 条 P0 与 P1/P2 清单可转为自动测试；本轮未运行任何测试。
- **体验设计：Pass（状态合同层）**。review_required、migration_required、active_blocked/degraded 等状态可诚实反馈；未冻结 UI。

### 8.3 Gate 结论

- Gate 2：**Pass with Conditions（migration 设计层）**；待独立评审和 DB 合同实测。
- Gate 3：**Pass with Conditions（信任合同层）**；待四 invoke/撤回/授权真实实现负测。
- Gate 4：**Pass with Conditions（技术设计层）**；待候选 SQL、回滚、性能、耐久及 P3-024 实测。

## 9. 需要 PM / 用户确认与后续建议

### 需 PM / 用户确认

1. 是否接受 `semantic_object` 继续聚合，并把 Decision/Action 的“任何新增专属顶层字段即拆表复查”作为候选 SQL 编写硬门。
2. 是否接受 retract-of-retract 的线性链/奇偶效果、跨 target dependency trigger 和本文 `strict_intersection` 定义。
3. 是否安排 P3-029 的轻量独立评审；评审通过前不启动候选 SQL 编写。
4. 评审通过后，是否另立“候选 SQL migration 编写 + 合同测试实现”任务；该确认不授权真实数据库或 Tauri。

### 后续任务建议（不自行启动）

- 先进行 P3-029 轻量独立评审，重点攻击 trigger 绕过、retract 链、strict intersection、循环激活、拆表门和四 invoke 测试完整性。
- 仅在评审及 PM 确认后，创建候选 SQL migration/合成空库合同测试任务。

## 10. 范围与变更声明

本任务只创建本 Markdown 交付物与本地预检报告。未创建 `.sql` 文件，未写或执行 SQL migration，未连接任何数据库，未修改 `lifeos/engineering/`、P3-025/P3-027/P3-028、Stitch、项目账本或冻结资产；未创建 handler，未安装/配置/运行 Tauri；未处理真实数据/Vault/文件，未启用真实导出、云/第三方模型、向量、同步、多设备、L3 或外部用户；未关闭 R-0040，未冻结 Schema/API/Tauri 配置/导出格式/SLA/工程基线，未进入下一阶段，未启动后续任务。
