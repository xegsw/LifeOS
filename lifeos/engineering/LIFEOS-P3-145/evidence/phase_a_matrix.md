# P3-145 Phase A matrix

| AC | Phase A status | Evidence |
|---|---|---|
| AC-01 | PASS — 20 IPC order, provider boundary, UI and native three-viewport paths retained | `static_contract_report.json`, `phase_a_automation.json`, `actual_tauri_evidence.json` |
| AC-02 | PASS — engineering-only synthetic profile and declared zero-contact boundary | `phase_a_boundary_declaration.md`, `checkpoint.json` |
| AC-03 | PASS for synthetic root mode/typed persistence; real-root non-content comparison is deferred to Phase C | `actual_tauri_evidence.json`, `cleanup.json` |
| AC-04 | PASS — Health type, one confirmed Durable Memory, limits and rejection paths covered | Rust targeted test and `actual_tauri_evidence.json` |
| AC-05 | PASS — typed Understanding remains separate from Memory/State | Rust targeted test, `actual_tauri_evidence.json` |
| AC-06 | PASS — correction/revocation invalidates affected derivations; stale disclosure rejects | Rust targeted test |
| AC-07 | PASS — empty or one Person Focus and non-quota presentation covered | Rust targeted test, Today screenshots |
| AC-08 | PASS — Person preview displayed Work, Health, and Durable Memory refs only | `actual_tauri_evidence.json` |
| AC-09 | PASS — preview displayed scope, item type, DeepSeek, model, location, and budget | `actual_tauri_person_preview.png`, `actual_tauri_evidence.json` |
| AC-10 | PASS — preview-before-confirmation and replay/restart failure-closed paths covered | Rust targeted test |
| AC-11 | PASS for synthetic mode — maximum counter and exact DeepSeek adapter boundary covered; real requests are deferred | Rust targeted test, `static_contract_report.json` |
| AC-12 | PASS — synthetic result saved as typed Understanding with refs and lifecycle state | `actual_tauri_evidence.json` |
| AC-13 | PASS — feedback confirmation changed the reason shown by Person Today | `actual_tauri_today_feedback.png`, `actual_tauri_evidence.json` |
| AC-14 | PASS — single-use feedback and affected-only invalidation covered | Rust targeted test |
| AC-15 | PASS — medical-risk synthetic input rejects before write/network | Rust targeted test, `static_contract_report.json` |
| AC-16 | PASS — AEAD/Keychain lifecycle, missing/tamper failure and synthetic cleanup covered | Rust test, `cleanup.json` |
| AC-17 | PASS — only fixed synthetic canaries used; no real text or credential in retained evidence | `phase_a_boundary_declaration.md`, `actual_tauri_evidence.json` |
| AC-18 | PASS — fresh direct PID restart preserved typed state, feedback, and Person Today | `actual_tauri_restart_today.png`, `actual_tauri_evidence.json` |
| AC-19 | Deferred — mandatory fresh isolated Phase B independent review has not started | `checkpoint.json` |
| AC-20 | PASS — marker negative matrix and exact engine-root cleanup completed | `phase_a_automation.json`, `cleanup.json`, `checkpoint.json` |

Phase A conclusion: applicable engineering rows PASS. This does not constitute Phase B independent-review PASS, Phase C real-loop PASS, PM acceptance, risk closure, product freeze, or Stage transition.
