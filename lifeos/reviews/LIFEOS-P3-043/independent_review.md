# LIFEOS-P3-043 独立评审

## 评审信息

- 对应任务 ID：LIFEOS-P3-043
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
- 独立评审角色：WorkBuddy（隔离新建会话）
- 协审视角：权限边界反例攻击 / 证据链 / R-0048 组合
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-043/independent_review.md`
- 评审结论：**Pass with Conditions**
- 更新时间：2026-08-20

## 评审摘要

1. **三套回归隔离复跑全部通过**：P3-031 44 PASS / 0 FAIL、P3-040 128 PASS / 0 FAIL、P3-042 52 PASS / 26 P2 Known Limitation / 0 FAIL，退出码均为 0；P3-039 evidence 和 P3-041 evidence 保留标记均为 True。

2. **Hash 与 evidence 完整性确认**：candidate_schema.sql 的 SHA-256 与 P3-042 source_hashes.json 完全一致；P3-041 全部 5 个 evidence 文件 unchanged=True；隔离副本复跑前后原始文件未变。

3. **P3-041 的 7 个 P1 真实关闭**：八字段（grantor_ref / processor / purpose / location / valid_from_ms / expires_mode / expires_at_ms / policy_version）在 `status='active'` 时的直接 UPDATE 全部被 `authorization_security_envelope_immutable` trigger 阻断，稳定错误码为 `active_authorization_security_envelope_immutable`。NULL↔值翻转、at↔indefinite 配对、复合八字段、多行 UPDATE、no-op UPDATE 均正确处理。

4. **新发现 1 个 P1 旁路**：`INSERT OR REPLACE INTO authorization` 使用 `status='granted'` 在 FK ON + 全部 trigger 生效下，可通过 DELETE+INSERT 路径绕过 BEFORE UPDATE trigger，将 active 授权的安全包络完全替换（processor/policy_version 等全换），随后可重新 `UPDATE SET status='active'` 激活——0 audit、0 outbox、子表行存活。此旁路根因是 `authorization_security_envelope_immutable` 仅为 BEFORE UPDATE trigger，不覆盖 INSERT OR REPLACE 的 DELETE+INSERT 路径。

5. **R-0048 组合攻击确认 10 个 P2 旁路**：revoked_at_ms / created_at_ms / generation 在 active 时可自由改写；预置 audit/outbox 可满足退休 fence；staged generation climb 可配合预设证据完成退休。PM 要求的组合攻击未发现从 P2 升级为 P1 的路径——这些旁路需要直接 DB 写入权限（writer-level），不构成对应用层授权消费门的直接绕过。

6. **Terminal 状态包络可变（P2）**：`authorization_security_envelope_immutable` trigger 的 WHEN 条件仅检查 `OLD.status='active'`，不覆盖 revoked/expired/superseded 状态。terminal 授权记录的安全包络字段可被事后修改，影响历史授权语义完整性。

7. **合法路径全部通过**：合法 retirement（gen+1 + audit + outbox）、合法 granted 状态包络修改、合法新版本 supersede + activate、trigger 顺序 / recursive_triggers / PRAGMA 变体均正确处理。

## 已通过内容

### 回归复跑

| 回归套件 | 结果 | 退出码 | Evidence 保留 |
|----------|------|--------|---------------|
| P3-031 | 44 PASS / 0 FAIL | 0 | N/A |
| P3-040 | 128 PASS / 0 FAIL | 0 | P3_039_EVIDENCE_PRESERVED=True |
| P3-042 | 52 PASS / 26 P2 Known Limitation / 0 FAIL | 0 | P3_031_EXIT=0, P3_040_ISOLATED_EXIT=0, P3_041_EVIDENCE_PRESERVED=True |

### Hash 核对

| 文件 | P3-042 source_hashes.json | P3-043 实测 | 匹配 |
|------|--------------------------|-------------|------|
| candidate_schema.sql | `ceedad2ba...5a6b` | `ceedad2ba...5a6b` | ✅ |
| P3-031 contract_tests | `b8ee1db6...4d78` | 通过 P3-042 runner 间接验证 | ✅ |
| P3-042 runner | 通过 source_hashes.json | 隔离复跑结果一致 | ✅ |

### P3-041 evidence 保留

| 文件 | unchanged | hash_match |
|------|-----------|------------|
| MANIFEST.md | True | True |
| counter_example_attacks.py | True | True |
| counter_example_results.json | True | True |
| counter_example_results.txt | True | True |
| candidate_schema.sql | True | True |

### 反例攻击结果（46 攻击 / 34 PASS / 12 BYPASS）

**P1 旁路（1 个，新发现）**

| ID | 组 | 攻击名称 | 细节 |
|----|-----|---------|------|
| BYPASS-P1-01 | SQL | insert_or_replace_granted_fk_on | `INSERT OR REPLACE INTO authorization VALUES (...)` 使用 `status='granted'` 在 FK ON + 全部 trigger 生效下，通过 DELETE+INSERT 路径绕过 `authorization_security_envelope_immutable`（BEFORE UPDATE only），将 active 授权的 processor 从 'local' 改为 'evil-replace'、policy_version 从 'policy-v1' 改为 'policy-evil'；随后可 `UPDATE SET status='active'` 重新激活，0 audit / 0 outbox / 子表行存活。 |

**P2 旁路（10 个）**

| ID | 组 | 攻击名称 | 细节 |
|----|-----|---------|------|
| BYPASS-P2-01 | ENV-STATE | envelope_change_while_revoked | revoked 状态授权的包络字段（processor）可被修改，trigger 仅保护 `status='active'` |
| BYPASS-P2-02 | ENV-STATE | envelope_change_while_expired | expired 状态授权的包络字段（purpose）可被修改 |
| BYPASS-P2-03 | SQL | fk_off_replace_rebuild_then_activate | PRAGMA foreign_keys=OFF + INSERT OR REPLACE(granted) + activate 可重建 active 授权并完全改写包络（writer-level action） |
| BYPASS-P2-04 | R0048 | prewrite_revoked_at_active | active 时可预写 revoked_at_ms（任意时间戳） |
| BYPASS-P2-05 | R0048 | prewrite_then_legal_retirement | 预写的 forged revoked_at_ms 在合法退休后仍然保留 |
| BYPASS-P2-06 | R0048 | preset_evidence_forged_retirement | 直接表写入可预置 audit/outbox 满足退休 fence |
| BYPASS-P2-07 | R0048 | rewrite_created_at_active | active 时 created_at_ms 可被改写 |
| BYPASS-P2-08 | R0048 | generation_bump_active | active 时 generation 可自由升高（trigger 只防降） |
| BYPASS-P2-09 | R0048 | staged_generation_climb_retire | 分步升高 generation + 预设证据可完成退休 |
| BYPASS-P2-10 | R0048 | retirement_with_forged_revoked_at | 退休语句可携带任意 revoked_at_ms |

**P3 观察（1 个，by design）**

| ID | 组 | 攻击名称 | 细节 |
|----|-----|---------|------|
| OBS-P3-01 | ENV-STATE | envelope_change_while_granted | granted 状态（pre-activation）包络可变，by design |

### 已关闭的 P1（P3-041 的 7 个全部真实关闭）

| P3-041 P1 | P3-043 验证 | 结果 |
|-----------|-------------|------|
| update_grantor_ref_active | ENV-01 | PASS (blocked) |
| update_processor_active | ENV-02 | PASS (blocked) |
| update_purpose_active | ENV-03 | PASS (blocked) |
| update_location_active | ENV-04 | PASS (blocked) |
| update_valid_from_active | ENV-05 | PASS (blocked) |
| update_expires_mode_active | ENV-06 | PASS (blocked) |
| update_policy_version_active | ENV-07 | PASS (blocked) |

## 关键问题

### 1. INSERT OR REPLACE 旁路（P1-NEW-01）

**根因**：`authorization_security_envelope_immutable` 是 `BEFORE UPDATE ON authorization` trigger，仅在 UPDATE 操作时触发。`INSERT OR REPLACE` 在 SQLite 内部执行 DELETE + INSERT 序列，不触发 BEFORE UPDATE trigger，因此绕过安全包络保护。

**攻击路径**：
```sql
-- 授权 auth1 当前 status='active', processor='local', policy_version='policy-v1'
INSERT OR REPLACE INTO authorization VALUES
  ('auth1','logical1','actor','evil-replace','evil','remote',
   'granted',1,1,1786550400000,'indefinite',NULL,NULL,'policy-evil',NULL,1786550400000,1786550400000);
-- 结果：auth1 现在是 status='granted', processor='evil-replace', policy_version='policy-evil'
-- 子表行（scope/action/policy）因 FK deferred check 存活
UPDATE authorization SET status='active' WHERE id='auth1';
-- auth1 重新变为 active，但包络已完全替换
-- 0 audit_entry, 0 outbox_job
```

**影响**：攻击者可在不触发 audit/outbox 的情况下，将一个 active 的本地测试授权替换为远程生产授权（processor='remote'），然后重新激活。这构成授权扩权和信任边界破坏。

**建议修复**：增加 `BEFORE INSERT ON authorization` trigger，在 INSERT 时检查是否已存在同 id 的 active 记录；或增加 `BEFORE DELETE ON authorization` trigger，在 DELETE 时检查 OLD.status 是否为 'active'（子表 FK 已有保护，但 INSERT OR REPLACE 的 FK 检查是 deferred 的）。

### 2. Terminal 状态包络可变（P2，R-0049 相邻）

`authorization_security_envelope_immutable` trigger 的 WHEN 条件为 `OLD.status = 'active'`，不覆盖 revoked/expired/superseded 状态。Terminal 授权记录的安全包络字段可被事后修改，影响历史授权语义完整性。此问题与 R-0049（terminal 子表可变）同属历史记录不可变性问题族。

### 3. R-0048 组合路径未升级

PM 要求验证 `created_at_ms`/`revoked_at_ms` 与 generation、预置 evidence、退休状态组合后是否从 P2 升级为 P1。经 7 个组合攻击测试，确认这些旁路均需要直接 DB 写入权限（writer-level action），不构成对应用层授权消费门的直接绕过。维持 P2 定级。

## 必须整改项

### 冻结前必须修复

1. **P1-NEW-01：INSERT OR REPLACE 旁路** — 需要新增 trigger 覆盖 INSERT OR REPLACE 的 DELETE+INSERT 路径。建议方案：
   - 方案 A：增加 `BEFORE INSERT ON authorization` trigger，当 INSERT 且存在同 id 的 OLD.status='active' 记录时 RAISE(ABORT)
   - 方案 B：增加 `BEFORE DELETE ON authorization` trigger，当 OLD.status='active' 且存在子表行时 RAISE(ABORT)（需注意不影响合法 DELETE 路径）
   - 方案 C：在应用层禁止 INSERT OR REPLACE，只允许显式 INSERT + UPDATE + 状态转换

2. **Terminal 状态包络保护** — 扩展 trigger WHEN 条件为 `OLD.status IN ('active', 'revoked', 'expired', 'superseded')`，或新增 terminal 状态专用不可变 trigger。

### 冻结前必须明确处置

3. **R-0048 证据链 P2 族** — Schema 冻结前必须明确 DB 层与应用层对 audit/outbox append-only、generation 防升、时间元数据不可变的责任分工和验证任务。

## 条件通过项

| 条件 | 适用范围 | 失效条件 |
|------|---------|----------|
| P1-NEW-01 修复并经独立复评确认 | INSERT OR REPLACE 路径 | 复评发现旁路仍存在 |
| Terminal 状态包络保护明确处置 | revoked/expired/superseded 授权记录 | Schema 冻结前未明确 |
| R-0048/R-0049 P2 族明确 DB/应用层责任 | audit/outbox/generation/时间元数据 | Schema 冻结前未明确 |

## 关卡检查

- **Gate 1 产品一致性评审**：N/A（本任务不涉及产品定位或 V1 范围变化）
- **Gate 2 数据与来源评审**：Pass with Conditions — 三套回归和 hash 完整性通过；R-0048 证据链 P2 族和 terminal 包络可变仍开放
- **Gate 3 AI 权限与信任评审**：Pass with Conditions — 八字段 P1 真实关闭；INSERT OR REPLACE P1 旁路必须修复后才能讨论 R-0044/R-0047 关闭
- **Gate 4 技术可行性评审**：Pass — trigger 顺序、recursive_triggers、PRAGMA 变体、FK ON/OFF 均正确处理；INSERT OR REPLACE 是 SQLite 语义已知行为
- **Gate 5 用户价值验证评审**：N/A（本任务不涉及用户体验验证）

## 风险

| 风险 | 当前状态 | 本评审建议 |
|------|---------|-----------|
| R-0040 | Open / Conditional | 保持 |
| R-0043 | Reopened / Closure Candidate | 保持 |
| R-0044 | Reopened / Remediation Candidate | 保持 Reopened；P1-NEW-01 修复前不得关闭 |
| R-0045 | Closed | 保持 Closed |
| R-0046 | Open / Closure Candidate | 保持 |
| R-0047 | Open / Remediation Candidate | 保持 Open；八字段 P1 已确认关闭，但 INSERT OR REPLACE P1 旁路需修复后才能进入关闭候选 |
| R-0048 | P2 Open / Known Limitation | 保持 P2；组合攻击确认未升级为 P1 |
| R-0049 | P2 Open / Known Limitation | 保持 P2；建议扩展纳入 terminal 状态父表包络可变 |

**建议新增风险**：
- **R-0050（建议）**：`INSERT OR REPLACE` / `DELETE + INSERT` 可绕过 BEFORE UPDATE trigger 替换 active 授权的安全包络。P1。Open。

## 需要 PM 决策

1. **是否启动 P3-044**：修复 INSERT OR REPLACE 旁路（P1-NEW-01），增加 BEFORE INSERT 或 BEFORE DELETE trigger 覆盖 DELETE+INSERT 路径。
2. **是否登记 R-0050**：INSERT OR REPLACE 安全包络旁路风险。
3. **R-0044/R-0047 是否保持 Reopened**：建议保持，直到 P1-NEW-01 修复并经独立复评确认。
4. **R-0048 组合路径定级确认**：本评审确认维持 P2，PM 是否同意。
5. **Terminal 状态包络保护**：是否在 P3-044 中一并处理，或单独任务。
6. **Schema 冻结门槛**：P1-NEW-01 修复 + Terminal 保护明确处置 + R-0048/R-0049 责任明确，三者均满足前不得冻结。

## 最终建议

**Pass with Conditions**。

P3-042 的八字段安全包络不可变 trigger 正确关闭了 P3-041 的 7 个 P1 旁路，三套回归和 hash 完整性全部通过。但独立反例攻击发现 1 个新 P1 旁路（INSERT OR REPLACE 绕过 BEFORE UPDATE trigger），必须在 Schema 冻结前修复并经独立复评确认。

R-0048 组合攻击确认 10 个 P2 旁路均维持 P2 定级，未升级为 P1——这些旁路需要直接 DB 写入权限，不构成对应用层授权消费门的直接绕过。但 PM 要求的"Schema 冻结前必须明确 DB 与应用层责任分工"条件仍然有效。

**不允许**在 P1-NEW-01 修复前冻结 Schema/API、关闭 R-0044/R-0047、或进入下一阶段。
