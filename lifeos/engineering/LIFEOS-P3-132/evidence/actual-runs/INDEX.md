# P3-132 actual Tauri run index

All runs used the locally built `LifeOS P3-132 Global AI Today Lite.app`, product identifier `local.lifeos.p3-132`, the visible `Offline synthetic adapter` label, and a fresh `LIFEOS_RUNTIME_ROOT` under the task-only temporary root. Each retained JSON is a read-only row-level SQLite/audit snapshot made before cleanup.

| Case | Fresh runtime root | UI observation retained | SQLite/audit snapshot | Result |
| --- | --- | --- | --- | --- |
| confirm | `run-evidence-confirm` | `screenshots/confirm-final.jpeg` | `confirm.json` | understanding feedback `confirm`; one synthetic noticed; zero Actions |
| edit_confirm | `run-evidence-edit-confirm` | `screenshots/edit-confirm-final.jpeg` | `edit-confirm.json` | edited text kept as user feedback; zero Actions |
| reject | `run-evidence-reject` | `screenshots/reject-final.jpeg` | `reject.json` | disclosure/no reliable noticed; zero Actions |
| correct | `run-evidence-correct` | `screenshots/correct-final.jpeg` | `correct.json` | corrected notice with `user_corrected`; zero Actions |
| ignore | `run-evidence-ignore-no-auto` | `screenshots/ignore-no-auto-final.jpeg` | `ignore-no-auto-action.json` | disclosure/no reliable noticed; zero Actions |
| explicit action | `run-evidence-ignore` | `screenshots/explicit-action-focus-final.jpeg` | `ignore-and-explicit-action.json` | only the old candidate accept path creates one open Action and one Today Focus |
| request-local removal | `run-evidence-ignore` | `screenshots/request-local-removal-final.jpeg` | same snapshot; no persisted mutation after the action | Context removal returns the fixed no-reliable disclosure while existing Focus remains |
| reopen | `run-actual-ignore` | `screenshots/reopen-focus.jpeg` | `ignore-and-explicit-action.json` is the final equivalent lifecycle state | persisted open Action is shown as the single Today Focus after app quit/reopen |
| bundle-bound confirm | `run-bound-confirm` | structured fresh UI checks in the execution log | `bound-confirm.json` + `bundle-identities/confirm/` | retained binary and Info.plist bind a recomputable current bundle to an actual confirm run |
| Closure CL-01 | `closure-cl01-insufficient` | `screenshots/closure-cl01-insufficient-reopen-verified.jpeg` | `closure-cl01-before-second-reopen.json` + `closure-cl01-after-second-reopen.json` + `closure-ui-observations.json` | insufficient Capture keeps its own text and `Project link: none · evidence insufficient`; the SQLite SHA-256 is stable across actual quit/reopen |
| Closure CL-02 start | `closure-cl02-multi` | `screenshots/closure-cl02-multi-start.jpeg` | `closure-cl02-fixture.json` + `closure-cl02-multi-start.json` | reverse-inserted 3 open confirmed Actions render in `confirmed_at / action_id` order; `tie-a` wins the equal-time tie-break |
| Closure CL-02 refresh | `closure-cl02-multi` | `screenshots/closure-cl02-multi-refresh.jpeg` | `closure-cl02-multi-refresh.json` | actual Refresh preserves the Focus, the displayed order and SQLite/audit SHA-256 |
| Closure CL-02 reopen | `closure-cl02-multi` | `screenshots/closure-cl02-multi-reopen.jpeg` | `closure-cl02-multi-reopen.json` | actual quit/reopen preserves the same Focus, displayed order and SQLite/audit SHA-256 |

The first five rows are independent feedback runs. Their evidence states are obtained from the same final candidate source tree recorded in `source-lineage.json`; no source change occurred during those five final UI runs. The retained raw bundle binary is for the final bound-confirm control. See `verification.json` for machine checks; it does not infer outcomes from this Markdown file.

The Closure rows retain a separate raw binary and Info.plist for each fresh run root. They do not revise or erase the two historical P2 disclosures from the first engineering submission.
