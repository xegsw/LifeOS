# P3-141 Provider Restoration Closure — Independent ABF2 Matrix

| ABF2 ID | Review-owned evidence | Result | Reason |
|---|---|---|---|
| M-001 | `evidence/static_lineage_after_p0.json` | NOT IMPLEMENTED | Static five-profile, five-Adapter, mode mapping and labels match P3-140, but the required review-owned dynamic loopback did not start after P0. |
| M-002 | `evidence/static_lineage_after_p0.json` | NOT IMPLEMENTED | Static count is exactly 20 IPC; the required independent non-Provider regression did not start after P0. |
| M-003 | `evidence/p0_revision2_phase_gate.json` | NOT IMPLEMENTED | The save/test/enable/first-send state-machine test did not start after P0. |
| M-004 | `evidence/p0_revision2_phase_gate.json` | NOT IMPLEMENTED | No review-owned Custom loopback or protocol mutation ran after P0. |
| M-005 | `evidence/p0_revision2_phase_gate.json` | NOT IMPLEMENTED | No desktop/compact/narrow actual-Tauri launch, PID, AX, WebView or screenshot was started after P0. |
| M-006 | `evidence/prohibited_target_attestation.json` | PASS (scope attestation only) | No prohibited target or real/external surface was accessed. This does not compensate for the P0. |
| M-007 | `evidence/static_lineage_after_p0.json` | PASS (read-only lineage only) | Revision-2 fixed inputs 7/7, P3-140 Manifest candidate 79/79, candidate engineering Manifest 79/79, and attempt-8 v1 receipt history were independently recomputed and retained as superseded history. |
| M-008 | `evidence/p0_revision2_phase_gate.json` | P0 FAIL | Candidate Phase-C build gate binds receipts to withdrawn `ABF-P3-141-v1` / v1 hash, not frozen `ABF-P3-141-v2`; a Revision-2 independent Pass cannot satisfy the candidate’s authorization gate. |
| M-009 | `evidence/cleanup_receipt.json` | NOT IMPLEMENTED | P0 occurred before the authorized temporary root was created; no marker-gated cleanup evidence exists. |

Final state: **REWORK**. Counts: P0=1, P1=0, P2=0, Unknown=0, Not Implemented=6. Per the P0 fail-closed rule, no positive dynamic evidence was collected after the P0.
