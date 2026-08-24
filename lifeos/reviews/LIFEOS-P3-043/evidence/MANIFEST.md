# LIFEOS-P3-043 Evidence MANIFEST

## 任务信息

- 任务 ID：LIFEOS-P3-043
- 任务名称：Active Authorization 父表安全包络整改隔离独立工程复评
- 评审 Agent：WorkBuddy（隔离新建会话）
- 评审日期：2026-08-20
- 评审结论：Pass with Conditions

## Evidence 文件清单

| 文件 | SHA-256 | 说明 |
|------|---------|------|
| candidate_schema.sql | `ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b` | 候选 SQL 快照（与 P3-042 source_hashes.json 一致） |
| counter_example_attacks.py | `400c6fcb63d3ecac76f75a54a3017a12c379055dbeec2ebcc597d9fe1c30e40a` | 独立反例攻击脚本（46 攻击 / 9 组） |
| counter_example_results.json | `a5d283fbb14e65605d83c20f5aebfee91a4cb1007893ae8ac85e4ae3a6b46d7b` | 攻击结果 JSON（46 攻击 / 34 PASS / 12 BYPASS） |
| counter_example_results.txt | `b6aceeb1b92f7924ace7161dc6478755f3ecc5eafcb6fc2f1842ba4d8bcde5b6` | 攻击结果文本输出 |

## 隔离复跑结果

| 回归套件 | PASS | FAIL | 退出码 | Evidence 保留 |
|----------|------|------|--------|---------------|
| P3-031 | 44 | 0 | 0 | N/A |
| P3-040 | 128 | 0 | 0 | P3_039_EVIDENCE_PRESERVED=True |
| P3-042 | 52 | 0 | 0 | P3_031_EXIT=0, P3_040_ISOLATED_EXIT=0, P3_041_EVIDENCE_PRESERVED=True |

## 反例攻击统计

| 指标 | 数量 |
|------|------|
| 总攻击数 | 46 |
| PASS | 34 |
| BYPASS | 12 |
| P1 旁路 | 1 |
| P2 旁路 | 10 |
| P3 观察 | 1 |

## P1 旁路（新发现）

| ID | 攻击名称 | 根因 |
|----|---------|------|
| BYPASS-P1-01 | insert_or_replace_granted_fk_on | INSERT OR REPLACE 的 DELETE+INSERT 路径绕过 BEFORE UPDATE trigger |

## P2 旁路

| ID | 组 | 攻击名称 |
|----|-----|---------|
| BYPASS-P2-01 | ENV-STATE | envelope_change_while_revoked |
| BYPASS-P2-02 | ENV-STATE | envelope_change_while_expired |
| BYPASS-P2-03 | SQL | fk_off_replace_rebuild_then_activate |
| BYPASS-P2-04 | R0048 | prewrite_revoked_at_active |
| BYPASS-P2-05 | R0048 | prewrite_then_legal_retirement |
| BYPASS-P2-06 | R0048 | preset_evidence_forged_retirement |
| BYPASS-P2-07 | R0048 | rewrite_created_at_active |
| BYPASS-P2-08 | R0048 | generation_bump_active |
| BYPASS-P2-09 | R0048 | staged_generation_climb_retire |
| BYPASS-P2-10 | R0048 | retirement_with_forged_revoked_at |

## P3 观察

| ID | 攻击名称 | 说明 |
|----|---------|------|
| OBS-P3-01 | envelope_change_while_granted | granted 状态（pre-activation）包络可变，by design |

## P3-041 evidence 保留验证

| 文件 | unchanged | hash_match |
|------|-----------|------------|
| MANIFEST.md | True | True |
| counter_example_attacks.py | True | True |
| counter_example_results.json | True | True |
| counter_example_results.txt | True | True |
| candidate_schema.sql | True | True |

## 运行环境

- Python: 3.13.12（managed）
- SQLite: Python sqlite3 模块（内存数据库）
- FK: PRAGMA foreign_keys=ON（默认）
- Schema: candidate_schema.sql（与 P3-042 source hash 一致）
