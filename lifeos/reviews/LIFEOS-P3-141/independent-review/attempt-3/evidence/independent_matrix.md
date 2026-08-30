# P3-141 Phase B Attempt 3 — independent matrix

`PASS` means this limited Phase-B review has reproducible evidence for that check. `FAIL` is a demonstrated candidate contract violation. `UNKNOWN` or `BLOCKED` is not a pass and cannot be filled by source-owned tests.

| # | Independent check | Result | Evidence / reason |
|---:|---|---|---|
| 1 | 12 fixed inputs hash and byte-size | PASS | `independent_verification.json` (12/12) |
| 2 | P3-139 lineage, 77 files | PASS | `candidate_integrity.json` |
| 3 | P3-140 lineage, 79 files | PASS | `candidate_integrity.json` |
| 4 | candidate tree before test | PASS | 79 / `6a45…87e1` |
| 5 | candidate tree after test | PASS | 79 / `6a45…87e1` |
| 6 | exact 20 IPC names | PASS | verifier check `ipc:exact_20` |
| 7 | closed four Provider profiles | PASS | verifier check `provider:closed_four` |
| 8 | no Custom Provider vocabulary | PASS | verifier check `provider:no_custom` |
| 9 | first-send Provider lock seam | PASS | verifier check `provider:first_send_lock` |
| 10 | receipt check precedes runtime-root resolution | PASS | verifier check `gate:receipt_precedes_root` |
| 11 | missing receipt fails before root probing | PASS (static) | candidate `build.rs` ordering; no real root contacted |
| 12 | receipt-enabled synthetic root startup | BLOCKED | actual-Tauri binary did not link |
| 13 | root ownership/schema marker seam | PASS (static) | verifier check `root:ownership_marker` |
| 14 | SQLite sidecar rejection seam | PASS (static) | verifier check `root:sidecar_rejection` |
| 15 | pre-existing empty root is rejected pre-write | UNKNOWN | no independent dynamic invocation after P0 gate failure |
| 16 | ordinary file root is rejected pre-write | UNKNOWN | same |
| 17 | leaf symlink is rejected pre-write | UNKNOWN | same |
| 18 | ancestor symlink is rejected pre-write | UNKNOWN | same |
| 19 | unowned existing DB is rejected pre-write | UNKNOWN | same |
| 20 | unknown file in root is rejected pre-write | UNKNOWN | same |
| 21 | canonical-path violation is rejected pre-write | UNKNOWN | same |
| 22 | owned restart avoids duplicate send/write | UNKNOWN | same |
| 23 | Work total allowance is 14 across the Pilot | FAIL / P0 | real-mode limit is 3, not 14 |
| 24 | Work daily quota is at most one | FAIL / P0 | no date/day partition or daily counter exists |
| 25 | Health uses the five required bounded fields | FAIL / P0 | no typed sleep/energy/soreness/training-load/available-time model |
| 26 | Health stays structured and non-medical | UNKNOWN | required structured input is absent |
| 27 | Durable Memory requires confirmation seam | PASS (static) | P3-139 lifecycle code retained |
| 28 | confirmed Durable Memory maximum is three | FAIL / P0 | no cap; resolver permits up to 12 L1 rows |
| 29 | Context Resolver minimum budget failure is closed | PASS (static) | verifier check `resolver:budget_failure_closed` |
| 30 | Context Resolver exact budget path | UNKNOWN | no independent runtime case after P0 gate failure |
| 31 | Context Resolver over-budget failure | UNKNOWN | same |
| 32 | CrossDomain authorization / Health removal seam | PASS (static) | verifier check `health:request_local_removal` |
| 33 | Today Intelligence contract seam | PASS (static) | candidate `today_intelligence.rs` present; not a P3-141 runtime proof |
| 34 | feedback stale-path seam | PASS (static) | verifier check `feedback:stale_path` |
| 35 | feedback changes later result | UNKNOWN | no independent runtime case after P0 gate failure |
| 36 | provider dispatch lacks fallback/parallel route | PASS (static) | closed profile and one locked state seam |
| 37 | real-flow IDs use the current P3-141 contract | FAIL / P0 | P3-133 prefixes and request keys remain |
| 38 | receipt-gate mutation is detected | PASS | `semantic_mutations.json` |
| 39 | root-ownership mutation is detected | PASS | `semantic_mutations.json` |
| 40 | Provider-lock mutation is detected | PASS | `semantic_mutations.json` |
| 41 | Health-boundary mutation is detected | PASS | `semantic_mutations.json` |
| 42 | feedback/budget mutation is detected | PASS | `semantic_mutations.json` |
| 43 | candidate auxiliary synthetic suite | PASS (auxiliary only) | `candidate_auxiliary_cargo_test.log`: 43 passed; not an independent substitute |
| 44 | actual-Tauri desktop 1280×1024 PID→AXWindow→AXWebView | BLOCKED / UNKNOWN | `actual_tauri_blocked.md` |
| 45 | actual-Tauri compact 700×760 PID→AXWindow→AXWebView | BLOCKED / UNKNOWN | `actual_tauri_blocked.md` |
| 46 | actual-Tauri narrow 560×640 PID→AXWindow→AXWebView | BLOCKED / UNKNOWN | `actual_tauri_blocked.md` |
| 47 | Phase C 7–14 day real use | Pending / Not Implemented | expressly out of Phase B and not started |
| 48 | Phase D non-content receipt review | Pending / Not Implemented | depends on an eligible Phase C |
| 49 | Phase E PM final review | Pending / Not Implemented | PM-only after previous gates |

Result: 22 PASS (including clearly labelled static/auxiliary seams), 5 demonstrated P0 FAIL, 11 UNKNOWN, 3 BLOCKED/UNKNOWN, and 3 Pending / Not Implemented. This does not meet the task’s pass formula.
