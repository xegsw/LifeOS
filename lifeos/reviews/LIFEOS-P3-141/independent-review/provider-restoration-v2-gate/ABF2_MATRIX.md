# ABF-P3-141-v2 Matrix — fail-closed

| ABF row | Result | Evidence / reason |
|---|---|---|
| ABF2-M-001 | Not Implemented | Stopped before valid precontact seal; no candidate lineage evaluation may be positive evidence. |
| ABF2-M-002 | Not Implemented | Stopped before IPC/non-Provider regression. |
| ABF2-M-003 | Not Implemented | Stopped before review-owned state-machine cases. |
| ABF2-M-004 | Not Implemented | Stopped before loopback protocol cases. |
| ABF2-M-005 | Not Implemented | Stopped before actual-Tauri capture. |
| ABF2-M-006 | Not Implemented | `evidence/prohibited_target_attestation.json` says prohibited targets were not accessed, but the required full review did not run. |
| ABF2-M-007 | Not Implemented | No valid review-owned history/new-candidate lineage closure. |
| ABF2-M-008 | **P0 Fail** | `evidence/precontact_violation.json`: candidate contact preceded self-written, hashed precontact artifacts. |
| ABF2-M-009 | Not Implemented | No authorized temporary root was created after the P0; marker-gated cleanup did not run. |

This is not a partial pass: the P0 invalidates this review as a source of positive acceptance evidence.
