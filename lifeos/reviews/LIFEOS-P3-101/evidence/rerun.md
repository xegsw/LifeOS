# LIFEOS-P3-101 read-only rerun

From the workspace root:

```sh
shasum -a 256 lifeos/tasks/LIFEOS-P3-101_stage3_self_use_mvp_candidate_integration_and_pre_enablement_gap_assessment_acceptance_basis_freeze.md
rg -n '当前可执行下一步|当前任务指针|D-0414|D-0415' lifeos/CURRENT_STATUS.md
rg -n '^\| LIFEOS-P3-10(0|1)\b' lifeos/TASK_REGISTRY.md
rg -n '^\| R-(0040|0051)\b' lifeos/RISK_LOG.md
rg -n '^\| D-041(4|5)\b' lifeos/DECISION_LOG.md
rg -n '允许的下一步|当前阶段' lifeos/FREEZE_STATUS.md
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/session_start.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/ledger_reconciliation.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/candidate_capability_map.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/stage_gate_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/risk_boundary_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/pre_enablement_gap_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/next_direction_decision.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/input_integrity.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-101/evidence/temporary_residue.json >/dev/null
```

Expected result: ABF hash matches the task card; all JSON parses; the current-next-step conflict is reproduced; the only selected direction is `Blocked`.
