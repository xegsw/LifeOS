# LIFEOS-P3-141 Phase B Independent Review — attempt-6 Test Design

## Identity, authority and stop rule

- Review type: fresh, isolated, read-only Phase B synthetic/offline independent review.
- Candidate commit: `e4eeb73395151955c0b833965979be1806406ce5` (must be verified only after this design, the write allowlist and precontact seal are hashed).
- Candidate is read-only.  The reviewer will never repair it, write into its engineering root, reuse attempt-1 through attempt-5 material, or touch Phase C Pilot assets.
- Review write root: `lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-6/` only.
- Sole temporary root: `/private/tmp/lifeos-p3-141-controlled-pilot-v1` only.
- Prohibited: all existing Pilots and real DB/path/text/Health/credentials/Provider/network targets.  In particular, Pilot-6 must not be tested, enumerated, statted, hashed, copied, created or cleaned during Phase B.
- Stop-positive-evidence rule: any P0 (including a prohibited-path access, content/credential exposure, candidate mutation, unbound PID/window/WebView, a failed frozen input, or the specified attempt-4 counterexample) stops the positive conclusion immediately.  Preserve only failure evidence and clean the single temporary root.

## Frozen inputs and precontact gate

1. Recompute all 12 fixed inputs from the PM fixed-input inventory: byte size and SHA-256, including the P3-139/P3-140 Final Manifests.
2. Confirm the P3-141 task and ABF hashes; failure stops before candidate contact.
3. Before candidate contact, author this design, `write_allowlist.md`, and `precontact_seal.json` in the review root.  Hash all three and retain the hashes in a separate precontact receipt.
4. Only after the sealed receipt may the reviewer inventory the candidate and permitted prior attempt history.  Historical attempts are read-only comparison material and never a source of code, fixtures, screenshots, PID/window records or conclusions.

## Independent test assets

- Write an attempt-6-owned Rust test module and runner under `tools/`; do not import, execute, copy or count engineering-owned tests as independent positive evidence.
- Create only synthetic fixtures and SQLite files under the single temporary root.  Use synthetic identifiers and non-sensitive categorical text; no real Work, Health, Memory, prompt, response or credential values.
- Record non-content SQLite object counts, audit/receipt/request IDs, sentinels and dispatch counters before/after each negative case.
- Build a review-owned bundle from the unchanged candidate.  Record source-tree hash, executable hash, bundle hash, direct-launch PID, exact title, AXWindow and AXWebView/WebArea identity for every actual-Tauri run.

## Test matrix

### A. Lineage, scope and topology

- Verify the 12/12 fixed inputs; P3-139 tree is 77 files / `63e2bc…acc9e`; P3-140 tree is 79 files / `6d5659…9940`; candidate is exactly 79 files and matches commit/tree lineage.
- Recompute candidate source-tree before and after all review activity; a change is P0.
- Verify the candidate Final Manifest with an attempt-6-owned non-self-referential verifier and recompute all listed hashes.
- Statical/dynamic topology: exactly 20 IPC; no 21st IPC; only four Provider kinds `OpenAI`, `Anthropic`, `Ollama`, `LM Studio`; zero Custom, second-provider, fallback, background send/check or network dispatch in Phase B.

### B. Fresh synthetic SQLite lifecycle and negative controls

1. Root/DB gate: absent canonical synthetic root accepts; existing root/DB, leaf/ancestor symlink, regular-file collision, non-directory root, non-regular DB and root mismatch all reject before DB/receipt/snapshot/audit/Memory/State writes.  Sentinels remain unchanged.
2. Provider state machine: save → test → explicit enable → explicit first send.  Assert first-send lock; reject a second Provider, Custom, automatic fallback, background probe/send and send-before-enable.  Dispatch remains zero for rejected paths.
3. Resolver: test reject, exact, over-by-one, CrossDomain and multi-L1/L2 cases.  Budget/authorization/minimal-disclosure rejection is `context_budget_rejected` before request/receipt/snapshot/audit/Memory/State writes, with no deletion-to-fit behavior.
4. Quotas: Work at most one per synthetic day and fourteen total; all over-limit, same-day and forged-date cases close before writes.
5. Health DTO: only one controlled source; require exactly sleep range, fatigue/energy 1–5, soreness/pain boolean, recent-load low/medium/high and available-time range.  Reject multi-source, missing field, invalid enum/range and free text before every durable write.
6. Identity: durable Memory requires explicit confirmation and never exceeds three; Current State and AI Understanding remain separately typed/lifecycled.
7. Feedback: correct/reject makes the old result stale, recomputation changes the next result, and ignored feedback does not become confirmation.
8. Health request-local removal: the removed request has no Health disclosure or output; Memory/State remain unchanged and a later request does not silently inherit the removal.
9. Health safety: structured high-risk signal reaches conservative stop/no training-load recommendation without diagnosis/treatment text.
10. Restart: direct relaunch does not re-send, repeat derivation/write, revive stale data or reuse a request ID; non-content counts and state remain consistent.

### C. Required attempt-4 P0 counterexamples

1. For desktop/compact/narrow, direct-launch a fresh PID for each viewport.  After viewport `set_size`, collect a stable receipt sample (not the first pre-set-size sample) and require its dimensions to equal the same-run direct PID's exact-title AXWindow dimensions.  A reused first-tier receipt or an unbound/mismatched AX record is P0.
2. In actual Tauri, submit the single unique controlled-source legal five-field Health DTO through Today → `update_current_state` → SQLite → Today/feedback.  For multi-source, missing-field, invalid-value and free-text controls, prove rejection before each potential write and unchanged sentinels.

### D. Actual-Tauri visual/interaction evidence

- Use only a review-owned direct launcher per viewport; no ambient/global application search as an identity substitute.
- For desktop, compact and narrow: bind source → binary → bundle → direct PID → exact title → AXWindow → AXWebView/WebArea.  Capture new redacted/synthetic screenshots and inspect them visually for usable Health/Today/feedback states.
- Do not reuse earlier attempts' PIDs, windows, screenshots, fixtures, DBs or statements.  If required capture capability is unavailable, mark the corresponding line Blocked/Unknown; do not infer PASS from P3-140.

### E. Matrix and completion

- Evaluate ABF-M-001 through ABF-M-020 one by one.  M-008/M-009/M-017 are explicitly `PENDING_PHASE_C`, not Phase-B failures and not PASS claims.
- Phase B can only conclude `Pass` when every applicable Phase-B line passes, no P0/P1/Unknown/Not Implemented remains, required new actual-Tauri evidence is bound, and temporary-root cleanup is exact.  It is never a Phase C result, PM acceptance, freeze, risk closure or Stage 4 determination.
- On completion, remove exactly `/private/tmp/lifeos-p3-141-controlled-pilot-v1` after verifying its marker; do not probe or modify any other path.
