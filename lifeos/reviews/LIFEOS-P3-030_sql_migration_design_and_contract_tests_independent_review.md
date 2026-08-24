# LIFEOS-P3-030｜SQL migration 设计 / 合同测试独立评审

## 评审信息

- 对应任务 ID：LIFEOS-P3-029
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
- 独立评审角色：数据 / 领域模型负责人、AI 信任与安全负责人
- 协审视角：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-030_sql_migration_design_and_contract_tests_independent_review.md`
- 评审结论：**Pass with Conditions**
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-029_LIFEOS-P3-029_sql_migration_design_and_contract_tests_local_precheck.md`
- 本地预检状态：Skipped / Local Model Unavailable（502 Bad Gateway），符合允许跳过场景
- 更新时间：2026-08-13

## 评审摘要

1. **[事实]** P3-029 准确承接了 P3-025 §2-4 的表分层、P3-027 §3-10 的 P1 条件整改和 P3-028 的 3 个 P2 清洁项处理口径。未发现把候选设计误写为已实现、已冻结或风险已关闭的情况。
2. **[事实]** P3-028 的三项 P2 清洁项已在 P3-029 中充分处理：retract-of-retract 线性链语义已显式声明（§3.5）；`feedback_dependency` 跨 target 强制已指定为 BEFORE INSERT trigger（§3.5）；`strict_intersection` 已形式化定义（§3.6）。
3. **[事实]** 未发现 P0 级设计漏洞。ContentIdentity 条件 CHECK、DerivationInput 恰一引用 + type 一致性 CHECK + partial unique index、Feedback 线性 retract 链、Authorization deny 优先 + strict intersection、Tombstone/Outbox/FTS 分责等核心设计均可接受。
4. **[事实]** 发现 2 项 P1 级设计澄清需求：Tombstone generation 单调性缺少 DB 级 trigger 强制（§4 Must 清单遗漏）；Authorization activation completeness 有 trigger 设计但缺少 §7 合同测试清单中的对应测试项。
5. **[事实]** 发现 3 项 P2 清洁项：DerivationInput `input_type` 缺少显式 enum CHECK、并发 tombstone upgrade 测试未显式列出、Tombstone status 转换约束未指定强制层级。
6. **[推断]** `semantic_object` 聚合可继续。Decision=5、Action=5 已触及上限，"新增任一持久化顶层专属字段即拆表"的硬门可执行；嵌套对象不得规避计数的规则已覆盖。
7. **[建议]** 四 invoke / DTO 合同测试草案覆盖正测与关键反例，足以支撑后续 P3-024 M-01/M-04/M-20 矩阵调整。CHECK / trigger / partial index / transaction guard 分责合理。
8. **[建议｜需 PM 确认]** P3-029 在 2 项 P1 条件补齐后可作为候选 SQL migration 编写输入。最小 Tauri shell / handler 仍被阻塞。

## 已通过内容

### 承接关系

1. **表分层与创建顺序**：§2.1 的 00-90 分层准确继承 P3-025 §3.1-3.3 的权威/控制/派生/索引分责，并补充了 P3-027 §9-10 的 ContentIdentity 和 tombstone 调整。✓
2. **ContentIdentity 条件约束**：§3.2 的 CHECK 与 P3-027 §9 完全一致，四组 identity_kind 约束正确区分用户原文、外部来源、引用摘录和 AI 派生。trigger 补充阻止 user identity 携带 AI Derivation 和 AI identity 指向非 active Derivation。✓
3. **DerivationInput 恰一引用**：§3.4 的两条 CHECK（恰一非空 + type-column 一致性）与 P3-027 §8 一致；独立随机 id 主键 + 四个 partial unique index 设计正确。✓
4. **Feedback retract 与 dependency**：§3.5 在 P3-027 §4 基础上补强了 retract-of-retract 线性链语义（partial unique on retracts_feedback_id）、偶/奇层效果规则、跨 target dependency BEFORE INSERT trigger。✓
5. **Authorization strict_intersection**：§3.6 形式化定义了 deny 全局阻断、多 allow 严格交集、时间/集合/保留/频率维度计算、canonical hash 缓存键。与 P3-027 §3 一致且更精确。✓
6. **Tombstone / Outbox / FTS 分责**：§3.7 准确继承 P3-025 §3.2-3.3 的 generation fencing、lease CAS、FTS 回连权威和 post-filter 设计。✓
7. **四 invoke / DTO 合同**：§5 准确采纳 P3-027 §5 的四 invoke 拆分（read/export_candidate/mutate/destruct），每 invoke 有正测与必测反例。✓
8. **P3-024 M-01/M-04/M-20 补丁**：§6 提供了从三窄命令到四窄命令的候选更新合同，P0 断言覆盖越级 invoke、mutate 路由 destruct、参数篡改等场景。标注为候选设计补丁，不修改原文件。✓
9. **非实现 / 非冻结声明**：§1 和 §10 明确声明未创建 `.sql` 文件、未执行 migration、未连接数据库、未改代码、未运行 Tauri、未冻结 Schema/API、未关闭 R-0040。✓

### P3-028 P2 清洁项处理

| P2 项 | P3-028 要求 | P3-029 处理 | 判定 |
|---|---|---|---|
| P2-1 retract-of-retract | migration 设计时明确是否允许及状态效果 | §3.5 显式允许，线性链 + partial unique + 偶/奇层效果规则 | 关闭 ✓ |
| P2-2 跨 target dependency 强制 | 指定 DB CHECK / trigger / 事务级校验 | §3.5 明确 BEFORE INSERT trigger 查询两端强制 target tuple 完全相同 | 关闭 ✓ |
| P2-3 strict_intersection 形式化 | 形式化定义术语 | §3.6 完整定义集合/时间/保留/频率维度计算规则 | 关闭 ✓ |

## DB 约束反例攻击

### A1: ContentIdentity 身份混淆

**攻击**：插入 identity_kind='external_original' 但 derivation_id 非空（AI 伪装外部来源）。

**验证**：CHECK 第 2 分支要求 `external_original` 时 `derivation_id IS NULL` → 拒绝。✓

**攻击**：插入 identity_kind='ai_generated' 但 origin_actor_ref 非空（AI 文本冒充外部作者）。

**验证**：CHECK 第 4 分支要求 `ai_generated` 时 `origin_actor_ref IS NULL` → 拒绝。✓

**攻击**：插入未知 identity_kind='foo'。

**验证**：四个 OR 分支均不匹配 → CHECK 为 false → 拒绝。✓

**攻击**：quoted_excerpt 同时携带 derivation_id 和 origin_actor_ref。

**验证**：CHECK 第 3 分支仅要求 `origin_actor_ref IS NOT NULL`，不限制 derivation_id。P3-027 §9 明确允许"AI 选取时可同时记 Derivation"。✓ 有意行为。

### A2: DerivationInput 恰一引用绕过

**攻击**：插入两行 FK 非空（artifact_version_id + semantic_object_id）。

**验证**：CHECK 1 `(1)+(1)=2 ≠ 1` → 拒绝。✓

**攻击**：input_type='artifact_version' 但 artifact_version_id 为 NULL，semantic_object_id 非空。

**验证**：CHECK 2 第 1 分支 `input_type='artifact_version' AND artifact_version_id IS NOT NULL` = false；第 2 分支 `input_type='semantic_object'` = false → 全 false → 拒绝。✓

**攻击**：同一 Derivation 对同一 artifact_version_id 重复消费。

**验证**：partial unique index `UNIQUE(derivation_id, artifact_version_id) WHERE artifact_version_id IS NOT NULL` → 拒绝重复。✓

**攻击**：同一 Derivation 有两条不同 artifact_version_id 输入（合理多输入场景）。

**验证**：partial unique index 允许 (D, V1) 和 (D, V2) 共存。P3-025 "输入集非空、完整且用于 ID/重检；多输入约束取交集/最严格值" → 有意行为。✓

### A3: Feedback retract 链分叉与乱序

**攻击**：F2 retract F1 后，插入 F2b 也 retract F1（分叉）。

**验证**：partial unique index on `retracts_feedback_id` → F1 已被 F2 指向，F2b 插入 → 唯一冲突拒绝。✓

**攻击**：F3 retract F2，F2 的 event_seq 大于 F3（逆序）。

**验证**：BEFORE INSERT trigger 检查"目标 event_seq 更小" → F2.event_seq < F3.event_seq 违反 → 拒绝。✓

**攻击**：F2 retract F1，但 F2 和 F1 不同 actor。

**验证**：BEFORE INSERT trigger 检查"同 actor" → 拒绝。✓

**攻击**：F2 retract F1，F3 retract F2（retract-of-retract），验证奇偶效果。

**验证**：F3 有效 → F2 无效 → F1 有效（恢复）。偶数层（2）恢复原效果。✓ 线性链语义正确。

**攻击**：F4 retract F3，验证奇数层取消。

**验证**：F4 有效 → F3 无效 → F2 有效 → F1 无效（取消）。奇数层（3）取消原效果。✓

### A4: feedback_dependency 跨 target

**攻击**：F2 (target=Action A) 依赖 F1 (target=Artifact V)，跨 target。

**验证**：BEFORE INSERT trigger 查询两端，强制 target tuple (target_type, target_id, target_version) 完全相同 → 拒绝。✓

**攻击**：F2 依赖 F1，但 F1.event_seq > F2.event_seq（后向序列）。

**验证**：trigger 检查 basis.event_seq 更小 → 拒绝。✓ 依赖图因严格递增 event_seq 无环。

**攻击**：F2 self-dependency（F2 依赖自身）。

**验证**：§3.5 明确"禁止 self" → 拒绝。✓

**攻击**：basis F1 被有效 retract 后，依赖效果。

**验证**：状态折叠器自动计算为 `inactive_due_to_basis_retracted`，不新增伪 retract。✓ 但注意：这是应用层计算，不是 DB 级强制。trigger 只保证结构完整性，有效状态在读取时计算。设计合理。

### A5: Authorization deny 优先与 strict_intersection

**攻击**：Project deny + Source allow（P3-026 标记的危险场景）。

**验证**：deny 全局阻断，具体 allow 不覆盖 deny → DENY。✓

**攻击**：两组不同 grantor 的 allow（多 G）。

**验证**：`groups.count != 1` → DENY_AMBIGUOUS。✓

**攻击**：policy version 不可验证。

**验证**：§3.6 明确"policy version 不可验证 → DENY"。✓

**攻击**：缓存投毒（旧缓存返回过期授权）。

**验证**：缓存键包含全部 Authorization IDs/generations + policy version + 资源闭包 hash；入队/执行/发布均重算。✓

**攻击**：expires_at 为 NULL（无限期）。

**验证**：§3.6 明确"NULL 不表示'任意'；无限期必须由显式 mode 表达"。✓

### A6: Tombstone 竞态与复活

**攻击**：旧 generation 请求在 tombstone 后消费。

**验证**：tombstone.generation >= request.generation → 拒绝。expected_generation CAS → 0 行更新。✓

**攻击**：Outbox 旧 lease 完成发布。

**验证**：lease CAS + subject generation 双重匹配 → CAS 失败。✓

**攻击**：FTS 含已删/撤权候选。

**验证**：FTS 回连权威 post-filter；不返回 raw hit count。search_index_state 双 generation 检查。✓

**攻击**：旧导出包在 tombstone 后评估恢复。

**验证**：restore evaluation 以当前 tombstone 为准；blocked/excluded，零写入。✓

**攻击**：直接 DB 写入降低 tombstone.generation（绕过应用层）。

**验证**：§3.7 声明"generation 只增"，但 §4 Trigger Must 清单未包含 tombstone generation 单调性 trigger。**→ 见 P1-1。**

## semantic_object 聚合 / 拆表门复核

### 字段计数验证

| 类型 | 专属字段 | 计数 | 状态 |
|---|---|---|---|
| Assertion | statement, valid_from, valid_until, qualification | 4 | 安全 |
| Decision | decision_text, question, options_considered, rationale, validity_window | 5 | **触及上限** |
| Action | action_text, due_at, defer_until, commitment_to, result_ref | 5 | **触及上限** |
| Event | event_type, description, occurrence | 3 | 安全 |

与 P3-027 §7 和 P3-028 复核结果一致。✓

### 拆表硬门

- "Decision/Action 新增任一持久化顶层专属字段即超过 5，候选 SQL 编写必须暂停并提出拆表" — 可执行。✓
- "嵌套对象不得规避计数" — DB CHECK 执行 top-level key 白名单 + `additionalProperties:false`；完整 JSON Schema 在应用层重复验证。✓
- "类型间状态/唯一性/FK/时间/确认不变量发生冲突且无法由 JSON Schema + 公共列无歧义表达时必须拆表" — 可判定。✓

### 嵌套规避风险

**攻击**：在 Decision 的 `rationale` 字段中嵌套存储新专属字段（如 `priority`）以规避计数。

**验证**：DB CHECK 执行 top-level key 白名单，`priority` 不在白名单 → 拒绝。但 DB CHECK 不递归检查嵌套对象内部。嵌套字段计数依赖应用层 JSON Schema 执行。直接 DB 写入可绕过。

**判定**：直接 DB 写入绕过嵌套计数检查是低风险场景（migration/调试工具），且 top-level key 白名单已防止新增顶层字段。聚合可继续，嵌套计数在应用层强制。P2 级别记录，不阻塞。

## Migration 可实现性复核

### 创建顺序与循环激活

§2.1 的 00-90 创建顺序正确处理了 FK 依赖：先 schema_migration_meta → 权威内容 → 语义对象 → 授权 → 派生 → 反馈 → 控制账本 → FTS → 索引/触发器 → 验证。✓

Artifact/Version 循环采用"两步激活"：先 draft Artifact (current_version NULL) → 插入 v1 + ContentIdentity → guarded UPDATE 设置 current pointer。任一步失败整事务回滚。✓

Derivation 循环同样先创建 draft，完整 inputs + identity + output 互相可达后才激活。✓

### 单版本事务与回滚

"校验前置 schema checksum → BEGIN IMMEDIATE → 创建表/索引/触发器 → 写 migration meta → foreign_key_check 与必要断言 → COMMIT。失败必须整体 ROLLBACK" ✓

FTS 初始重建通过事务提交的 outbox 后异步完成，不令权威 schema 提交失败。✓

回退策略："不得把 destructive down migration 当默认回滚；回退应使用 SQLite-aware 备份和前一可验证版本" — 合理但具体流程"仍待实现任务验证"。P2 记录。

### CHECK / trigger / partial index / transaction guard 分责

| 层级 | 强制内容 | 是否可由 SQLite 实现 | 判定 |
|---|---|---|---|
| CHECK | 枚举/generation；ContentIdentity 条件；DerivationInput exact-one+type；scope exact-one；Feedback kind/引用 | ✓ SQLite 支持条件 CHECK | 合理 ✓ |
| Unique/partial index | 聚合版本号；Source stable key；Derivation typed input；retract direct child；Feedback idempotency；Outbox idempotency | ✓ SQLite ≥3.8.0 支持 partial index | 合理 ✓ |
| Trigger | 不可变性；current pointer ownership；Derivation activation completeness；retract/dependency same-target/sequence；Authorization activation completeness；受控 payload 清理 | ✓ SQLite 支持 BEFORE INSERT/UPDATE trigger | **缺少 tombstone generation 单调性 trigger（见 P1-1）** |
| Transaction guard | authoritative closure；strict intersection；generation/tombstone；跨表状态折叠；active_blocked 全路径证明；AI output 循环激活；outbox 同事务登记 | ✓ 应用层事务 guard | 合理 ✓ |
| 应用层重复校验 | 完整 JSON Schema；Rust/TS DTO；canonical request hash；资源/速率上限；用户可理解 preview | ✓ 必须应用层 | 合理 ✓ |

**判定**：分责合理。trigger 层有 1 项遗漏（P1-1），其余均可落地。应用层重复校验不可替代 DB 约束，P3-029 已明确。✓

## 四 invoke / DTO 合同测试复核

### 正测覆盖

| Invoke | 正测 variant | 覆盖 |
|---|---|---|
| `lifeos_read` | read/search/health/capability | ✓ |
| `lifeos_export_candidate` | 内存 export candidate、只读 restore evaluation | ✓ |
| `lifeos_mutate` | capture/suggestion/feedback/retract/link | ✓ |
| `lifeos_destruct` | revoke/disconnect/delete + 三项必填全匹配 | ✓ |

### 反例覆盖

| 反例 | 覆盖 invoke | 判定 |
|---|---|---|
| 未知 action | read | ✓ E_UNKNOWN_COMMAND |
| destructive action in read | read | ✓ 拒绝 |
| 额外/跨 variant 字段 | read | ✓ E_INVALID_ARGUMENT |
| 错误 contract version | read | ✓ E_UNKNOWN_COMMAND |
| raw path / write / overwrite | export_candidate | ✓ 拒绝，零文件写 |
| mutate 字段混入 | export_candidate | ✓ 拒绝 |
| 被删包复活 | export_candidate | ✓ 拒绝 |
| delete/revoke/disconnect action in mutate | mutate | ✓ E_UNKNOWN_COMMAND |
| 同幂等键不同 hash | mutate | ✓ 冲突拒绝 |
| 伪造 identity/project/auth | mutate | ✓ 拒绝 |
| destruct 缺/错 preview、generation、idempotency | destruct | ✓ P0 拒绝 |
| 跨 variant 字段 | destruct | ✓ 拒绝 |
| 旧 generation | destruct | ✓ 拒绝 |
| 无 capability | destruct | ✓ 拒绝 |

### mutate 路由 destruct 检查

**攻击**：`lifeos_mutate` 携带 `delete_artifact` action。

**验证**：§5 明确 "delete/revoke/disconnect action → 拒绝；无 destruct capability"。mutate DTO 不包含 destructive action 枚举 → E_UNKNOWN_COMMAND。✓

### read 携带 destructive action 检查

**攻击**：`lifeos_read` 携带 `delete_artifact` action。

**验证**：read DTO variant 不包含 destructive action → E_UNKNOWN_COMMAND。✓

### export_candidate 产生真实写入检查

**攻击**：`lifeos_export_candidate` 携带 write/overwrite 参数。

**验证**：§5 明确 "零文件写、零 outbox"。export_candidate DTO 不包含写入参数 → E_INVALID_ARGUMENT。✓

### 错误详情泄露检查

**验证**：§5 明确 "零详细解析错误回传"。错误只含允许列表 `{code, safe_message, retryable, details_token?}`。`details_token` 受 P3-027 §6 约束（TTL ≤5 分钟、单次、内存-only、安全摘要限定 6 字段）。✓

### exhaustive match 检查

**验证**：§5 明确 "exhaustive match 缺 variant 构建失败"。Rust 封闭 enum + `deny_unknown_fields`；TS discriminated union + strict schema。✓

## P3-024 M-01 / M-04 / M-20 影响复核

| 矩阵项 | P3-029 候选新合同 | P0 断言 | 判定 |
|---|---|---|---|
| M-01 | capability 只含四窄 invoke；按页面/流程最小授予 | 任意通用文件/DB/shell/network 或越级 invoke 可达即 P0 | 清晰 ✓ |
| M-04 | handler 只注册 read/export_candidate/mutate/destruct；未知默认拒绝 | 任意未注册 handler 可调用，或 mutate 路由 destruct即 P0 | 清晰 ✓ |
| M-20 | 四 DTO 各自正测 + 未知/额外/跨 variant/错误 contract；destruct 三项强制字段；服务端重建 Project/auth/version/generation | 任一参数篡改被接受即 P0 | 清晰 ✓ |

**判断**：补丁清楚地将"三窄命令"更新为"四窄命令"，P0 断言覆盖关键旁路。标注为"候选设计补丁，不修改原文件，不代表已验证"。✓

但需注意：这是设计层补丁，不是 P3-024 原文件的实际修改。P3-024 M-01/M-04/M-20 的实际更新需要另立任务。

## 新发现问题

### P0

无。

### P1

| # | 发现 | 位置 | 风险 | 建议 |
|---|---|---|---|---|
| P1-1 | **Tombstone generation 单调性缺少 DB 级 trigger 强制。** §3.7 声明"generation 只增"，但 §4 Trigger Must 清单未包含 "tombstone generation monotonicity" trigger。当前 trigger 清单含"受控 payload 清理"但不覆盖 tombstone generation。若直接 DB 写入（migration/调试工具）降低 tombstone.generation，结合匹配的 subject.generation 请求，可绕过 tombstone 消费门，导致已删内容被消费。 | P3-029 §3.7, §4 | 删除/撤回绕过、恢复复活 | 在 §4 Trigger Must 清单补充 "tombstone generation monotonicity (BEFORE UPDATE: reject generation decrease)"；在 §7 P0 测试补充 "DB-P0-15: UPDATE tombstone SET generation = lower → trigger rejects, tombstone unchanged" |
| P1-2 | **Authorization activation completeness 缺少 §7 合同测试。** §3.6 设计了 activation trigger（proposed→active 前至少一条 scope、一条 action、一条完整 policy；旧版本显式 superseded），§4 列出了 "Authorization activation completeness" trigger，但 §7 P0/P1 测试清单无对应测试项。DB-P0-08 测试运行时 strict_intersection 评估，不覆盖 activation guard。 | P3-029 §3.6, §4, §7 | 不完整授权变为 active，影响审计和缓存 | 在 §7 P1 测试补充 "CT-P1-07: activate Authorization with 0 scopes → trigger rejects; 0 actions → rejects; incomplete policy → rejects; unsuperseded old version → rejects" |

### P2

| # | 发现 | 位置 | 建议 |
|---|---|---|---|
| P2-1 | DerivationInput `input_type` 缺少显式 enum CHECK。CHECK 2 功能上等价（未知 input_type 无法满足任一分支），但独立 `CHECK(input_type IN ('artifact_version','semantic_object','feedback','source'))` 更清晰可维护。 | §3.4 | 候选 SQL 编写时补充显式 enum CHECK |
| P2-2 | 并发 tombstone upgrade（同一 subject 第二次删除请求）测试未显式列出。PK 防止重复 tombstone，但 upgrade 路径（UPDATE tombstone generation）的 generation 单调性检查未有显式测试。 | §3.7, §7 | 补充测试："concurrent tombstone upgrade with stale generation → reject" |
| P2-3 | Tombstone status 转换约束未指定强制层级。"cleanup pending/failed/vendor_limited 不得解除阻断"是规则，但未说明由 CHECK、trigger 还是应用层强制。 | §3.7 | 候选 SQL 编写时指定 status 转换矩阵和强制层级 |

## 必须整改项

无 P0 级必须整改项。

以下 P1 项建议在候选 SQL migration 编写任务中补齐：

1. **P1-1**：§4 Trigger Must 清单补充 "tombstone generation monotonicity" trigger；§7 补充 DB-P0 测试项。
2. **P1-2**：§7 补充 Authorization activation completeness 的 P1 合同测试项。

## 条件通过项

| 条件 | 适用范围 | 失效条件 |
|---|---|---|
| P1-1 tombstone generation trigger 补齐 | 候选 SQL migration 编写任务 | 若编写 SQL 时未添加此 trigger |
| P1-2 activation completeness 测试补齐 | 候选 SQL migration 编写 + 合同测试实现任务 | 若实现时未覆盖此测试 |
| P3-024 M-01/M-04/M-20 补丁需另立任务实际更新 | 最小 Tauri shell / handler 任务准入 | 若 Tauri 壳任务启动前补丁未完成 |
| Decision/Action 字段数复查 | 候选 SQL migration 编写任务 | 若编写时新增第 6 个专属字段 |
| 回退策略具体流程待实现验证 | 候选 SQL migration 编写 + DB 实测任务 | 若实现时未验证回退可行性 |

## 关卡检查

### Gate 2：数据与来源评审 — Pass with Conditions

- 用户原文 / AI 生成 / AI 推断建议 / 外部引用 / 用户确认事实的区分清晰：ContentIdentity 八类条件 CHECK + trigger + `origin_actor_ref` 按身份必填 ✓
- DerivationInput 恰一引用 + type 一致性 + partial unique 防重复消费 ✓
- Feedback 追加式 + 线性 retract 链 + 跨 target dependency trigger + 严格递归无环 ✓
- Tombstone generation fencing + 清理失败不解阻断 ✓
- **条件**：P1-1 tombstone generation trigger 补齐后 Gate 2 完全通过

### Gate 3：AI 权限与信任评审 — Pass with Conditions

- deny 全局阻断不可被具体 allow 覆盖 ✓
- strict_intersection 形式化定义完整 ✓
- 四 invoke 拆分，destruct capability 独立隔离 ✓
- `details_token` 不泄露路径/SQL/对象 ID/授权匹配数量 ✓
- ContentIdentity 防止 AI 冒充外部来源 ✓
- **条件**：P1-2 activation completeness 测试补齐后 Gate 3 完全通过

### Gate 4：技术可行性评审 — Pass with Conditions

- migration 创建顺序、循环激活、两步激活可实现 ✓
- CHECK / trigger / partial index / transaction guard 分责合理 ✓
- 合同测试清单可转为自动测试 ✓
- 单版本事务 + 整体 ROLLBACK 可落地 ✓
- FTS/outbox 解耦不拖垮权威写入 ✓
- **条件**：回退策略具体流程仍待实现验证；P1-1 trigger 补齐

## 风险

| 风险 ID | 描述 | 级别 | 状态 |
|---|---|---|---|
| R-P3-030-01 | Tombstone generation 单调性若未由 trigger 强制，直接 DB 写入可降低 generation 并绕过消费门 | P1 | Open，候选 SQL 编写时补齐 trigger |
| R-P3-030-02 | Authorization activation guard 若无测试覆盖，实现可能遗漏 | P1 | Open，候选合同测试实现时补齐 |
| R-P3-030-03 | Decision/Action 专属字段已触及 5 上限，migration 设计时可能新增字段触发拆表 | P2 | Open，候选 SQL 编写时复查 |
| R-P3-030-04 | 回退策略具体流程未验证 | P2 | Open，DB 实测时验证 |
| R-0040 | Tauri / IPC 安全风险 | 既有 | 保持 Open / Conditional |

## 需要 PM 决策

1. **[需 PM 确认]** 是否认定 P3-029 的 2 项 P1 条件可在候选 SQL migration 编写任务中补齐（而非要求 P3-029 返工）？
2. **[需 PM 确认]** 是否允许在 P3-030 通过后另立"候选 SQL migration 编写 + 合成空库合同测试实现"任务？该任务须明确授权创建 `.sql` 文件和运行合成空库测试。
3. **[需 PM 确认]** 最小 Tauri shell / handler 任务的启动条件是否为：(a) P3-030 评审通过；(b) P3-024 M-01/M-04/M-20 补丁另立任务完成；(c) 候选 SQL migration 编写 + 合同测试实现完成？
4. **[需 PM 确认]** P2-1 至 P2-3 是否纳入候选 SQL migration 编写任务的检查清单？
5. **[需 PM 确认]** 是否确认 P3-029 不改变核心领域模型、AI 权限边界或技术架构 V0.1 冻结合同？

## 最终建议

1. **评审结论：Pass with Conditions。** P3-029 在设计层充分承接了 P3-025 / P3-027 / P3-028 的关键约束，P3-028 的 3 个 P2 清洁项已全部处理。未发现 P0 级设计漏洞。2 项 P1 条件可在后续候选 SQL 编写任务中补齐，不要求 P3-029 返工。

2. **允许启动"候选 SQL migration 编写 + 合成空库合同测试实现"任务**，前提是 PM 确认采纳本评审结论。该任务须：(a) 明确授权创建 `.sql` 文件和运行合成空库测试；(b) 补齐 P1-1 tombstone generation trigger 和 P1-2 activation completeness 测试；(c) 复查 Decision/Action 字段数；(d) 将 §7 P0 测试先落成或同步落成。

3. **最小 Tauri shell / handler 仍被阻塞。** 启动条件为：(a) P3-030 评审通过；(b) P3-024 M-01/M-04/M-20 补丁另立任务完成；(c) 候选 SQL migration 编写 + 合同测试实现完成。真实 Tauri 安装/运行仍未获授权。

4. **P3-029 不冻结 Schema / API。** 冻结前须完成 migration/约束验证、真实 IPC/debug-release/目标平台矩阵、耐久验证、独立复评和用户确认。

5. **P3-029 不作为 R-0040 关闭输入。** R-0040 关闭仍需真实 Tauri/IPC 验证 + 进程杀死耐久 + 独立复评 + 用户确认。

6. **声明**：本评审为只读独立反例评审，未修改 P3-029 / P3-025 / P3-027 / P3-028 或任何工程文件、Stitch、项目账本或冻结资产；未写 SQL migration、未创建 `.sql` 文件、未执行 migration、未创建 IPC handler、未安装/配置/运行真实 Tauri；未关闭 R-0040、未冻结 Schema/API、未进入下一阶段、未启动后续任务。
