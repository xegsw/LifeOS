# P3-041 Evidence MANIFEST

## 评审信息

- 任务 ID: LIFEOS-P3-041
- 评审类型: 隔离独立工程复评
- 评审角色: WorkBuddy (Independent Reviewer)
- 评审日期: 2026-08-13
- 候选 SQL 来源: `engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` (P3-040 整改后版本)

## Evidence 文件清单

| 文件 | SHA-256 |
|------|---------|
| `counter_example_attacks.py` | `7e887e6db5f74ce7fbd69d7d77071141d3bc42cc83e54f4cb4590277d948b46c` |
| `counter_example_results.json` | `78c5b2aa45a3b7abe57078807528e914fc023db56deb58cc07f885c8f16f6619` |
| `counter_example_results.txt` | `3220a83c8731ffa5c761382a31e39bddd1d24d3668e201b45bdd67f314b89211` |
| `candidate_schema.sql` | `50d25371865b6a153267042c68290bbb00baca12a9b43d2821bd8c3a2a93cf7c` |

## 候选 SQL hash 验证

| 来源 | Hash | 匹配 |
|------|------|------|
| P3-040 `source_hashes.json` → `candidate_source` | `50d25371...3cf7c` | YES |
| P3-040 `source_hashes.json` → `candidate_snapshot` | `50d25371...3cf7c` | YES |
| P3-041 `candidate_schema.sql` (本目录) | `50d25371...3cf7c` | YES |

## 反例攻击结果摘要

- 总攻击数: 38
- 通过 (fail-closed 或 legal verified): 19
- 失败 (bypass found): 19
- P1 bypass: 7
- P2 bypass: 12

### P1 Bypass 明细 (7)

| 攻击组 | 攻击名 | 细节 |
|--------|--------|------|
| PARENT | update_processor_active | processor local→external-cloud, gen 不变, 无 audit |
| PARENT | update_purpose_active | purpose test→production, gen 不变, 无 audit |
| PARENT | update_location_active | location device→remote, gen 不变, 无 audit |
| PARENT | update_grantor_active | grantor_ref 变更, gen 不变, 无 audit |
| PARENT | update_expiry_to_indefinite_active | expires_mode at→indefinite, gen 不变, 无 audit |
| PARENT | update_policy_version_active | policy_version 变更, gen 不变, 无 audit |
| PARENT | compound_field_update_active | processor+purpose+location 同时变更, gen 不变, 无 audit |

### P2 Bypass 明细 (12)

| 攻击组 | 攻击名 | 细节 |
|--------|--------|------|
| PARENT | update_valid_from_active | valid_from_ms 变更 (minor field) |
| AUDIT | preposition_fake_retirement | 预置 audit/outbox 允许假退休 (已知限制) |
| AUDIT | delete_audit_after_retirement | audit_entry 可删除 (证据链缺口) |
| AUDIT | delete_outbox_after_retirement | outbox_job 可删除 (证据链缺口) |
| AUDIT | update_outbox_status_after_retirement | outbox status 可修改 |
| AUDIT | update_audit_action_after_retirement | audit action_code 可修改 |
| GEN | increase_generation_active | generation 1→5 无状态变更 |
| GEN | bump_then_retire_with_prepositioned_evidence | generation bump + 预置证据退休 |
| TERM | update_scope_effect_revoked | revoked 后 scope effect 可改 |
| TERM | insert_scope_revoked | revoked 后可 INSERT 新 scope |
| TERM | update_action_value_revoked | revoked 后 action value 可改 |
| TERM | update_policy_training_revoked | revoked 后 policy 可改 |

### PASS 明细 (19)

| 攻击组 | 攻击名 | 结果 |
|--------|--------|------|
| UPSERT (4/4) | scope/action/policy ON CONFLICT DO UPDATE/NOTHING | 全部被 BEFORE INSERT trigger 阻断 |
| MULTI (2/2) | multi-row scope effect UPDATE / rebind | 全部被 BEFORE UPDATE trigger 阻断 |
| VER (5/5) | supersede revoked / skip version / wrong logical_key / version gap / concurrent active | 全部被 authorization_activation_complete trigger 阻断 |
| TRIG (4/4) | compound status+gen / recursive trigger / FK off insert / FK off bypass | 合法路径通过 + 非法路径阻断 |
| LEGAL (4/4) | proposed→granted→active / proposed→active / supersede+new version / terminal cleanup | 全部合法路径通过 |

## 回归复跑结果

| 回归 | 结果 | Hash 验证 |
|------|------|-----------|
| P3-031 | 42 PASS / 0 FAIL | 3 个稳定源文件 hash 全部匹配 MANIFEST |
| P3-040 | 128 PASS / 0 FAIL | 3 个 evidence 文件 hash 全部匹配 MANIFEST |

## P3-039 Evidence 保留验证

| 文件 | expected_match | actual_match | unchanged |
|------|---------------|---------------|-----------|
| MANIFEST.md | True | True | True |
| counter_example_attacks.py | True | True | True |
| counter_example_results.json | True | True | True |
| counter_example_results.txt | True | True | True |
| candidate_schema.sql | True | True | True |

P3-039 全部 5 个 evidence 文件保留完整，无篡改。
