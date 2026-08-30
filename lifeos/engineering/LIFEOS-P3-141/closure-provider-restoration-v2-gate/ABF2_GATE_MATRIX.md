# ABF-P3-141-v2 Gate Repair — Engineering Matrix

This matrix covers only the P0 repair. It does not convert the failed independent review into a Pass or authorize Phase C.

| ABF2 | Engineering state | Evidence | Conclusion |
|---|---|---|---|
| M-001 | PASS | `evidence/cargo_test.log`, `evidence/source_lineage.json` | Provider restoration candidate remains five-profile and now has an explicit Revision-2 gate. |
| M-002 | PASS | `evidence/source_gate_diff.md`, `evidence/non_provider_regression.json` | Only gate/test paths changed from commit `48a26320`; Provider/UI/20 IPC/domain semantics are regression-covered. |
| M-003 | PASS | `evidence/cargo_test.log` | Existing save→test→enable, first-send lock and no-fallback tests remain green. |
| M-004 | PASS | `evidence/cargo_test.log` | Existing Custom OpenAI-compatible loopback positive/negative protocol tests remain green. |
| M-005 | PENDING_NEW_INDEPENDENT_REVIEW | task contract, `evidence/history_lineage.json` | This narrow gate repair intentionally does not reuse or recreate actual-Tauri; the fresh independent review must collect its own direct-PID evidence. |
| M-006 | PASS | `precontact_seal.json`, `evidence/prohibited_target_attestation.json`, `evidence/cleanup_receipt.json` | Only the declared new synthetic temp root is used and then precisely removed. |
| M-007 | PASS | `evidence/history_lineage.json`, `evidence/failure_review_reference.json` | The first independent Rework/P0 remains read-only and is not used as positive evidence. |
| M-008 | PASS_FOR_ENGINEERING_REPAIR | `receipt_v2_contract.md`, `evidence/v2_gate_dynamic_matrix.json`, `evidence/phase_c_pre_root_negative.json`, `evidence/phase_c_dirty_candidate_negative.json` | Phase-C build gate is v2-only and verifies Revision-2 task/inventory/ABF, clean candidate commit/tree and a new independent v2 Manifest. |
| M-009 | PASS | `tools/cleanup_temp.sh`, `evidence/cleanup_receipt.json` | Marker-gated exact temporary root removal completed; receipt records `REMOVED_EXACT_TASK_ROOT` and `root_exists_after=false`. |

Engineering repair counts before cleanup: P0=0, P1=0, P2=0, Unknown=0, Not Implemented=0. The mandatory new independent review and its actual-Tauri work are future governance actions, not an engineering claim.
