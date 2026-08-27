# LIFEOS-P3-134 Closure-2 Acceptance Matrix

This closure preserves Closure-1 as read-only history. It adds a fresh, offline actual-Tauri capability preflight and a fresh synthetic Runtime test run. It is deliberately fail-closed: unavailable native or WebView geometry is not substituted with a screenshot, static scan, browser mock, or prose.

| AC | Closure-2 status | Basis |
|---|---|---|
| AC-01 | PASS (retained) | Fixed inputs were freshly re-hashed 13/13 before the probe; `static/source-integrity.json` records the result. |
| AC-02 | PASS (retained) | `static/source-integrity.json` records six byte-identical visual-contract files and a 75-regular-file candidate. |
| AC-03 | NOT IMPLEMENTED | No permitted actual-app surface yields the required reference/candidate DOM, class, landmark and key-node geometry matrix. |
| AC-04 | NOT PASS | A fresh 700x760 actual bundle was opened and captured, but the permitted capture surface has no native content bounds or WebView/DOM geometry. The 1280x1024 and 1160x768 full action runs therefore cannot be honestly completed. |
| AC-05 | NOT IMPLEMENTED | No same-fixture fresh reference/candidate baseline with allowed masked pixel/perceptual comparison was produced. |
| AC-06 | PASS (retained) | Closure-1 PM validation remains read-only-valid; this closure does not claim a new full action matrix. |
| AC-07 | PASS (retained) | Source-integrity scan remains free of UI direct-capability indicators. |
| AC-08 | PASS (retained) | Fresh offline synthetic `cargo test --locked --offline`: 5/5 pass; source-integrity records exactly 11 IPC. |
| AC-09 | PASS (retained) | Fresh runtime test suite includes the capture rejection/lifecycle coverage; no regression was observed. |
| AC-10 | NOT IMPLEMENTED | No fresh complete zero/one/multiple/tie/stale actual UI-to-IPC-to-DB-to-audit-to-restart matrix. |
| AC-11 | PASS (retained) | Closure-1 PM validation remains read-only-valid. |
| AC-12 | PASS (retained) | Closure-1 PM validation remains read-only-valid. |
| AC-13 | PASS (retained) | Closure-1 PM validation remains read-only-valid; this closure makes no replacement claim. |
| AC-14 | NOT IMPLEMENTED | No complete fresh independent-fixture write-before-failure/sentinel/DB invariant matrix. |
| AC-15 | PASS (retained) | Closure-1 PM validation remains read-only-valid. |
| AC-16 | PASS | The exact task temporary root was removed after the task-local App process exited; `cleanup.json` records the exact target and absent postcondition. Closure-2 has its own non-self-referential manifest and read-only verifier. |

**Package result: NOT PASS.** The continued deficiencies are AC-03, AC-04, AC-05, AC-10 and AC-14. No PM Pass candidate is submitted.
