# LifeOS 独立评审报告 — P3-041

## 评审信息

- 对应任务 ID: LIFEOS-P3-041
- 对应交付物路径: `lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`
- 独立评审角色: WorkBuddy (Independent Reviewer)
- 协审视角: 反例攻击 / 证据链完整性 / 版本链不变量
- 评审关卡: 隔离独立工程复评
- 独立评审路径: `lifeos/reviews/LIFEOS-P3-041/`
- 评审结论: **Pass with Conditions**
- 更新时间: 2026-08-13

## 评审摘要

1. **P3-031 回归隔离复跑通过**：42 PASS / 0 FAIL，三个稳定源文件 hash 全部匹配 MANIFEST，退出码 0。
2. **P3-040 回归隔离复跑通过**：128 PASS / 0 FAIL，三个 evidence 文件 hash 全部匹配 MANIFEST，P3-039 evidence 保留验证 True，退出码 0。
3. **P3-039 的 11 个 P1 真实关闭**：子表 INSERT/UPDATE/DELETE/REPLACE/改绑旁路在 active 状态下全部被 BEFORE INSERT + BEFORE UPDATE trigger 阻断，ON CONFLICT (UPSERT) 路径同样被阻断，多行 UPDATE 被阻断。
4. **版本链不变量全部通过**：supersede revoked (非 superseded) 被阻断、skip version 被阻断、wrong logical_key 被阻断、version gap 被阻断、concurrent active 被阻断——5/5 PASS。
5. **合法路径全部通过**：proposed→granted→active、proposed→active、supersede+new version activation、terminal child cleanup——4/4 PASS。
6. **新发现 7 个 P1 bypass（核心发现）**：父授权表自身的安全字段（processor, purpose, location, grantor_ref, expires_mode, policy_version）在 active 状态下可被 UPDATE 静默修改，无需 generation 变更或 audit 追加。P3-040 的整改仅覆盖子表变异，未覆盖父表字段不可变性。
7. **新发现 12 个 P2 bypass**：audit_entry/outbox_job 可被 DELETE/UPDATE（证据链缺口）、generation 可在 active 时自由升高、terminal 状态后子表仍可变异。这些是证据完整性和历史不可变性问题。
8. **候选 SQL hash 验证一致**：P3-041 使用的 candidate_schema.sql hash 与 P3-040 source_hashes.json 完全匹配（`50d25371...3cf7c`）。

## 已通过内容

### P3-039 的 11 个 P1 真实关闭

P3-039 发现的 11 个 P1 bypass 全部在 ADJ 组（active 状态下子表 INSERT/UPDATE/REPLACE/改绑）。P3-040 通过添加以下 trigger 实现了修复：

- `authorization_scope_no_insert_while_active` (BEFORE INSERT)
- `authorization_scope_no_update_while_active` (BEFORE UPDATE, 检查 OLD 和 NEW 父状态)
- `authorization_scope_no_delete_while_active` (BEFORE DELETE)
- 同模式 action 三个 trigger
- 同模式 policy 三个 trigger

本次评审通过以下攻击组验证了修复的有效性：

- **UPSERT (4/4 PASS)**：ON CONFLICT DO UPDATE 和 ON CONFLICT DO NOTHING 均被 BEFORE INSERT trigger 阻断，返回 `active_authorization_*_insert_forbidden`。
- **MULTI (2/2 PASS)**：多行 scope effect UPDATE 被阻断，多行 rebind 被阻断，返回 `active_authorization_scope_update_forbidden`。
- **TRIG (4/4 PASS)**：compound status+generation UPDATE 合法通过，recursive_triggers=ON 时 scope UPDATE 被阻断，FK off 时 orphan child INSERT 被阻断。

### 版本链不变量

5 个版本链攻击全部被 `authorization_activation_complete` trigger 阻断，返回 `authorization_old_version_not_superseded`：

- V-1: v2 supersede revoked (非 superseded) → 阻断
- V-2: v3 supersede v1 skip v2 → 阻断
- V-3: v2 wrong logical_key supersedes → 阻断
- V-4: v3 supersedes v1 wrong version gap → 阻断
- V-5: concurrent active v1+v2 → 阻断

### 合法路径

4 个合法路径全部通过：

- proposed→granted→active
- proposed→active (直接激活)
- supersede + new version activation
- terminal child cleanup after revocation

### 回归一致性

- P3-031: 42 PASS / 0 FAIL — 隔离复跑与原始结果一致
- P3-040: 128 PASS / 0 FAIL — 隔离复跑与原始结果一致
- P3-039 evidence: 5/5 文件保留完整，hash 全部匹配

## 关键问题

### P1-NEW-01: 父授权表安全字段 active 状态下可被静默修改 (7 个 P1)

**问题描述**：P3-040 的 trigger 矩阵仅保护子表（authorization_scope, authorization_action, authorization_policy）在父授权 active 状态下不被 INSERT/UPDATE/DELETE。但父授权表 `authorization` 自身的安全相关字段——`processor`, `purpose`, `location`, `grantor_ref`, `expires_mode`, `policy_version`——在 `status='active'` 时可被直接 UPDATE，不触发任何阻断、不要求 generation 变更、不追加 audit_entry。

**攻击向量**：
```sql
-- 攻击者可在 active 时执行：
UPDATE authorization SET processor='external-cloud' WHERE id='auth1' AND status='active';
-- 结果：processor 变更，generation 不变 (仍为 1)，无新 audit_entry
```

**影响**：
- `processor` 从 `local` 改为 `external-cloud`：绕过本地处理器约束
- `purpose` 从 `test` 改为 `production`：测试授权变为生产授权
- `location` 从 `device` 改为 `remote`：设备本地变为远程
- `grantor_ref` 变更：伪造授权来源
- `expires_mode` 从 `at` 改为 `indefinite`：有限期变为无限期
- `policy_version` 变更：绕过策略版本绑定
- 复合攻击：同时修改 processor + purpose + location，单次 UPDATE 即可完成全部篡改

**根因**：authorization 表上缺少 "active 状态下安全字段不可变" trigger。现有 trigger 只覆盖：
- `authorization_status_transition`：仅管控 status 列的状态机
- `authorization_active_retirement_contract`：仅管控 status 从 active→revoked/expired/superseded 的退出
- `authorization_generation_monotonic`：仅防止 generation 下降
- `authorization_version_identity_immutable`：仅保护 logical_key/version_no/supersedes

**整改建议**：新增 `authorization_security_field_immutable_while_active` trigger (BEFORE UPDATE)，当 `OLD.status='active'` 且 `NEW.status='active'`（状态未变）时，检查安全字段是否被修改：
- processor, purpose, location, grantor_ref, expires_mode, expires_at_ms, policy_version, valid_from_ms
- 若任一安全字段被修改，抛出 `active_authorization_field_immutable` 错误

### P2-NEW-01: audit_entry/outbox_job 可被 DELETE/UPDATE (5 个 P2)

**问题描述**：audit_entry 和 outbox_job 表在退休操作完成后可被 DELETE 或 UPDATE，构成证据链缺口。当前 trigger 仅在 `authorization_active_retirement_contract` 中检查 audit/outbox 是否存在（retirement 时），但不对 retirement 后的 DELETE/UPDATE 提供保护。

**影响**：
- 攻击者可在退休后删除 audit_entry，抹除退休证据
- 攻击者可修改 outbox_job status，伪造执行状态
- 攻击者可修改 audit_entry action_code，伪造操作类型

**严重性**：P2（证据完整性，非直接授权旁路）。这是已知的设计限制——audit/outbox 的不可变性需要更高层的应用逻辑或 SQLite 的 immutable table 机制来保障。

### P2-NEW-02: generation 可在 active 时自由升高 (2 个 P2)

**问题描述**：`authorization_generation_monotonic` trigger 仅防止 generation 下降（NEW.generation < OLD.generation），但不防止在 active 状态下自由升高 generation。攻击者可将 generation 从 1 直接改为 5，然后利用预置证据完成退休。

**影响**：结合预置证据，可绕过 generation+1 的递增约束。

**严重性**：P2（需要与预置证据组合才构成实际威胁）。

### P2-NEW-03: terminal 状态后子表仍可变异 (4 个 P2)

**问题描述**：P3-040 的子表 trigger 仅检查父授权是否 `active`。当父授权状态为 `revoked` 或 `expired` 时，子表（scope, action, policy）仍可被 INSERT/UPDATE/DELETE，导致历史授权语义可被篡改。

**影响**：已退休的授权记录可被事后修改其范围和权限，破坏历史不可变性。

**严重性**：P2（历史完整性，不影响当前 active 授权的运行时安全）。

## 必须整改项

### 冻结前必须修复

1. **[P1] 父授权表安全字段不可变 trigger**：新增 BEFORE UPDATE trigger，防止 active 状态下 processor/purpose/location/grantor_ref/expires_mode/expires_at_ms/policy_version 被修改。这是 7 个 P1 bypass 的根因，必须在 Schema 冻结前修复。

### 条件通过项

以下 P2 问题可在后续迭代中修复，不阻塞当前阶段：

2. **[P2] audit_entry/outbox_job 不可变性**：考虑应用层不可变追加或 SQLite WAL 模式下的追加约束。已知限制，需在 V1 应用层补偿。
3. **[P2] generation 升高约束**：考虑在 active 状态下同时禁止 generation 升高（当前仅防降）。
4. **[P2] terminal 状态子表保护**：将子表 trigger 的检查条件从 `status='active'` 扩展为 `status IN ('active', 'revoked', 'expired', 'superseded')`，即 terminal 状态下也不允许子表变异。

## 条件通过项

- **条件 1**：P3-040 回归的两套结果（42 PASS + 128 PASS）在隔离复跑中可复现 — **已满足**
- **条件 2**：P3-039 的 11 个 P1 真实关闭 — **已满足**
- **条件 3**：候选 SQL hash 与 P3-040 一致 — **已满足**
- **条件 4（未满足）**：父授权表安全字段 active 状态下不可变 — **需 P3-042 整改**
- **条件 5（未满足）**：audit_entry/outbox_job 不可变性 — **已知限制，可在 V1 应用层补偿**

**失效条件**：若 P3-042 未修复 P1-NEW-01（父授权字段不可变 trigger），则 R-0040 不得关闭，Schema 不得冻结。

## 关卡检查

- Gate 1 产品一致性评审：N/A（本任务为工程复评，不涉及产品定义）
- Gate 2 数据与来源评审：**通过** — P3-031 和 P3-040 回归隔离复跑一致，hash 全部匹配
- Gate 3 AI 权限与信任评审：**条件通过** — P3-039 的 11 个 P1 真实关闭，但新发现 7 个 P1（父表字段不可变性）
- Gate 4 技术可行性评审：**通过** — 候选 SQL trigger 机制可工作，合法路径通过，非法路径阻断
- Gate 5 用户价值验证评审：N/A（本任务为工程复评）

## 风险

1. **R-0047 (建议新增)**：父授权表安全字段 active 状态下可被静默修改。7 个 P1 bypass。状态：Open。需 P3-042 整改。
2. **R-0048 (建议新增)**：audit_entry/outbox_job 可被 DELETE/UPDATE，证据链缺口。5 个 P2。状态：Open (Known Limitation)。可在 V1 应用层补偿。
3. **R-0049 (建议新增)**：terminal 状态后子表仍可变异，历史完整性问题。4 个 P2。状态：Open。可在后续迭代修复。
4. **R-0040**：保持 Open/Conditional。P3-039 的 11 个 P1 已关闭，但 P1-NEW-01 新增 7 个 P1，关闭条件未完全满足。
5. **R-0043**：保持 Reopened/Closure Candidate。Tombstone 面 P1 全部关闭，但 Auth 面（父表字段）新增 P1，暂不可关闭。

## 需要 PM 决策

1. **是否启动 P3-042**：新增父授权表安全字段不可变 trigger 整改任务。这是冻结前的硬条件。
2. **R-0047/R-0048/R-0049 是否登记**：三个新风险是否正式写入 RISK_LOG.md。
3. **R-0040 状态保持**：确认 R-0040 维持 Open/Conditional，不因 P3-039 P1 关闭而关闭。
4. **P2 整改优先级**：audit/outbox 不可变性和 terminal 子表保护是否纳入 P3-042 范围，还是单独任务。
5. **Schema 冻结门槛**：确认 Schema 冻结前必须完成 P1-NEW-01 整改（父表字段 trigger），P2 可条件通过。

## 最终建议

**结论：Pass with Conditions**

P3-040 的整改在子表变异防护方面是有效的——P3-039 的 11 个 P1 真实关闭，UPSERT/MULTI/版本链/合法路径全部通过。但本次独立复评发现了 P3-040 未覆盖的攻击面：父授权表自身的安全字段在 active 状态下缺乏不可变保护，构成 7 个新的 P1 bypass。

**建议路径**：
1. 启动 P3-042：新增 `authorization_security_field_immutable_while_active` trigger (BEFORE UPDATE)
2. P3-042 完成后进行 P3-043 隔离复评（验证 7 个 P1 关闭 + P3-040 回归不退化）
3. P3-043 通过后关闭 R-0040 和 R-0043
4. P2 问题（audit/outbox 不可变性、terminal 子表保护）可在 Schema 冻结后由 V1 应用层补偿或后续迭代修复

**不允许在 P1-NEW-01 修复前冻结 Schema。**
