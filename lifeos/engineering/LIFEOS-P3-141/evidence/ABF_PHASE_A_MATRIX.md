# LIFEOS-P3-141 Phase A ABF matrix

Status vocabulary: `PASS_SYNTHETIC_ONLY` is evidence that the row's synthetic-contract portion passed. It is not an ABF final Pass, independent-review Pass, real-pilot Pass, PM acceptance, risk closure, Freeze, or Stage conclusion. `PENDING_PHASE_B` and `PENDING_PHASE_C` are intentionally not passed in this engineering package.

| Row | Phase A status | Evidence / successful test | Boundary statement |
|---|---|---|---|
| ABF-M-001 | PASS_SYNTHETIC_ONLY | `source_lineage.json`, `tools/verify_phase_a.py` | 12/12 fixed hashes and P3-140 79-file tree match; prohibited target untouched. |
| ABF-M-002 | PASS_SYNTHETIC_ONLY | `pilot_root_boundary.json`, closure boundary tests | Only the authorized temporary synthetic root was used. |
| ABF-M-003 | PASS_SYNTHETIC_ONLY | `phase_gate.json`, build-time gate | No receipt means `phase_b_independent_pass_required` before runtime-root inspection. |
| ABF-M-004 | PASS_SYNTHETIC_ONLY | `provider_activation.json`, Provider fixture tests | Explicit save → test → enable → synthetic send; four profiles only. |
| ABF-M-005 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, loopback request tests | Exactly one synthetic loopback dispatch uses only the selected Capture ref. |
| ABF-M-006 | PASS_SYNTHETIC_ONLY | `content_exclusion.json` | Scanner zero-hit; only synthetic fixtures were present. |
| ABF-M-007 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Memory/State tests | Original, Memory, State and Understanding remain distinct; no automatic Memory upgrade. |
| ABF-M-008 | PENDING_PHASE_C | — | Seven actual user dates cannot be fabricated in Phase A. |
| ABF-M-009 | PENDING_PHASE_C | — | Real paired daily-fact outcome requires controlled real-use evidence. |
| ABF-M-010 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, `synthetic_behavior.json` | Request-local disclosures, budgets and refs are tested without text leakage. |
| ABF-M-011 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Today feedback tests | Correction/rejection invalidates the relevant result slice in synthetic paths. |
| ABF-M-012 | PASS_SYNTHETIC_ONLY | `actual_tauri_viewports.json`, Today tests | Actual synthetic UI invoked request-local Health removal; no persistent inheritance. |
| ABF-M-013 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Today safety tests | High-risk signal produces a conservative non-diagnostic stop. |
| ABF-M-014 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, closure and Provider negative tests | Authorization, stale, budget, DB and Provider failures stop before their protected write/dispatch. |
| ABF-M-015 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, lifecycle test | Restart reloads lock but does not enable or dispatch; repeated request id reuses result. |
| ABF-M-016 | PASS_SYNTHETIC_ONLY | `actual_tauri_viewports.json` | Three known launch PIDs each bind exactly one AXWindow and one AXWebArea. |
| ABF-M-017 | PENDING_PHASE_C | — | User-only non-content real-use receipt is outside Phase A. |
| ABF-M-018 | PENDING_PHASE_B | — | A fresh independent-review session is mandatory and has not started. |
| ABF-M-019 | PASS_SYNTHETIC_ONLY | `cleanup_and_retention.json`, `tools/cleanup_temp.sh` | Exact temporary root is absent; prohibited real targets were not accessed or cleaned. |
| ABF-M-020 | PASS_SYNTHETIC_ONLY | `FINAL_MANIFEST.json` | Non-self-referential Manifest is finalized and lists the Phase B/C pending rows. |

Phase A engineering gate: all Phase-A-applicable rows above are ready for independent re-review subject to final cleanup and Manifest verification. Rows reserved for Phase B/C remain pending by contract.
