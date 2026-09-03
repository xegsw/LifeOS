# LIFEOS-P3-145 Phase B Independent Review — Test Design

## Identity and independence

- Review session: fresh isolated Phase B independent review.
- Candidate under review: Git commit `579914d06923db65db8c3b421b2da663a1950354`, declared engineering branch `codex/l3-p3-145-engineering-phase-a`.
- This reviewer did not implement the candidate. Candidate source, engineering Evidence, engineering deliverables, and candidate-provided tests are not positive proof and will remain read-only.
- This design, its companion allowlist, and the prohibited-boundary declaration are authored before first candidate or engineering contact. Any failure of that order is a review P0 and ends the attempt.

## Scope and controls

- Review only Phase B. It may use a newly created synthetic SQLite database, fixed non-sensitive canaries, a task-local bundle, and direct native Tauri execution.
- No real personal root, real database, real text, credential, Provider, HTTPS connection, or network request will be accessed in this phase.
- Review-owned test code must be authored and retained under this review root. It must not import, invoke, copy, or treat candidate test runners as positive proof.
- The candidate is first bound to the exact commit and a read-only source snapshot. Before/after source hashes must show it unchanged.

## Review-owned verification design

| Area | Tests and mutations | Required independent evidence |
|---|---|---|
| Lineage and isolation | Verify Frozen inputs, fixed commit, source snapshot, exactly 20 IPC, and command audit. Mutate the IPC list and source/binary binding expectation. | Input/commit/hash records and fail-closed mutation result. |
| Data identity/lifecycle | Use synthetic Work, non-medical Health Current State, and one confirmed Durable Memory. Reject empty, over-200, unknown, unconfirmed, expired, revoked, and corrected inputs before unintended writes. | Review-owned SQLite before/after metadata; no real content. |
| Resolver and Today | Exercise relevant cross-domain selection, exclusion-by-reason, minimum disclosure budget, a non-required-domain case, conflict, and evidence-insufficient empty state. Mutate selected refs and priority evidence. | Structured selected/excluded refs, reason records, at-most-one/empty Today assertions. |
| Disclosure and request | Check per-request disclosure preview, removal, cancel, stale confirmation, changed collection, and empty collection. | UI/DTO records plus network counter remains zero for deny cases. |
| Network and credential | Use a synthetic adapter/harness only. Attack authority, redirect, proxy, timeout/retry/fallback and request quota; exercise missing/tampered/deleted synthetic credential. | Target ledger and secret-free failure receipts. No external connection. |
| Understanding and feedback | Verify typed AI Understanding/Suggestion never becomes user fact; run all five feedback forms, duplicate consumption, correction/revocation and unrelated-slice stability across restart. | Dependency before/after and restart result records. |
| Health safety | Use a fixed synthetic high-risk canary and assert conservative network-before-stop with no partial write. | Zero-network and unchanged DB records. |
| Native UI | At 700x760, 1160x768, and 1280x1024: fresh direct-launch PID, exact title-bound AXWindow, AXWebView/AXArea, target-only screenshot and geometry. Include Today, disclosure, answer, feedback, close and fresh-PID restart. | PID/title/AX chain and target-only artifacts per viewport. |
| Cleanup and finalization | Test wrong/missing/symlink marker denial, then marker-gated exact temporary-root cleanup. Create non-self-referential FINAL_MANIFEST and independently verify every included hash. | Cleanup receipt, verifier result, and excluded-manifest self hash rule. |

## Result rule

Each applicable AC-01 through AC-20 and ABF-M-001 through ABF-M-020 receives an explicit Pass, Fail, Unknown, Not Implemented, or N/A only where the Frozen contract permits N/A. A Phase B Pass requires all applicable rows Pass and P0=P1=Unknown=Not Implemented=0. It may only permit PM to decide whether to enter Phase C; it does not itself begin real use, alter risks, freeze assets, or advance Stage.

## Stop and recovery rule

Stop immediately on a Frozen-input mismatch, precontact-order failure, prohibited-boundary contact, readonly-candidate modification, or other P0. For locked screen, unavailable AX/screenshot service, or temporarily unavailable runner with no prohibited contact, record a review-owned checkpoint as `Paused — Resumable` and resume only from the affected phase after binding inputs again.
