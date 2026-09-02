# P3-144 Phase B Independent Re-review 1 — Review-owned Test Design

## Status and independence

- Reviewer session: fresh isolated Phase B re-review; not the engineering executor.
- Candidate identity to bind after this seal: Git commit `4115f2958d8fa08fa30fccc90217bdc404769363`.
- This design was authored before any contact with the candidate, engineering materials, prior independent review, deliverables, or their manifests.
- Phase boundary: synthetic/offline only. No real provider, credential, content, network, or Pilot-7 filesystem interaction is permitted.

## Frozen review objectives

The review will independently prove or fail-close each Phase B ABF line M-001 through M-024. M-025 through M-030 are Phase C/user-only and will be recorded as `N/A — not entered`; M-031 is checked only if an environment interruption occurs; M-032 is the final non-self-referential lineage check.

## Review-owned controls and artifacts

- Create one fresh synthetic SQLite database under the fixed review root only.
- Create review-owned Rust/black-box tests and mutation harnesses; do not import, execute, or treat candidate verifier/tests/screenshots as the only positive proof.
- Establish before/after candidate and history Git/blob or SHA-256 snapshots after sealed read-only contact; fail the review on any unexpected change.
- Bind each actual-Tauri evidence set to its direct launch-returned PID, exact target AXWindow title, and target-only AXWebArea/WebView. Capture the three required viewports afresh.
- Keep command results, state receipts, screenshots, AX logs, counter ledgers, database summaries, and test sources free of real content and secrets.

## Matrix

| Review ID | ABF lines | Independent operation and expected proof |
|---|---|---|
| R-01 | M-001/M-023 | Bind fixed inputs, commit, source, UI/profile boundary and exactly 20 IPC; recompute lineage without altering history. |
| R-02 | M-002/I-01 | Audit own allowlist/prohibition controls; demonstrate no Pilot-7 command or filesystem contact. |
| R-03 | M-003/M-004 | Fresh synthetic Work and non-medical Health Current State lifecycle plus restart; verify semantic separation. |
| R-04 | M-005 | For both domains: 1–3 accepted, fourth, 201-char, blank, unknown field, and wrong type rejected before writes; DB snapshots unchanged on negatives. |
| R-05 | M-006–M-009 | Relevance/domain/scope/authorization/validity/recency filtering plus count/character/token-budget paths; selected refs and excluded reasons contain no body text. |
| R-06 | M-010–M-012 | Actual disclosure preview, remove, cancel, explicit confirmation, changed-set stale confirmation, replay, and fresh restart; all non-confirm paths have zero-send counters. |
| R-07 | M-013/M-014 | DeepSeek-only route, no fallback/background/retry/parallel/proxy/redirect/cross-authority behavior, and bad authority mutations; non-DeepSeek counters stay zero. |
| R-08 | M-015 | Synthetic encrypted credential lifecycle, fresh restart, missing key, missing ciphertext, and tamper mutations fail before network and disclose no secrets. |
| R-09 | M-016–M-018 | Synthetic AI output is Derivation/Understanding/Suggestion with provider/model/evidence refs; verify confirm, edit, reject, ignore, correct and restart; correction/revocation invalidates affected projections without rewriting history. |
| R-10 | M-019 | Diagnosis/treatment/medication/emergency fixtures reject or return only the frozen non-medical safety response; no medical fact is persisted. |
| R-11 | M-020–M-022 | Fresh direct-PID actual-Tauri desktop, compact, and narrow runs; exact AXWindow then AXWebArea/WebView and target-only screenshots/geometry per viewport. |
| R-12 | M-024/M-032/I-14 | Run review-owned mutation suite; verify prior review/engineering remain read-only, exact marker-gated cleanup, and a manifest that excludes itself and is independently recomputed. |

## Mutation set

At minimum mutate/attack: fourth Work and Health records; character overflow; blank/unknown/wrong-domain input; irrelevant/cross-domain/expired/corrected/revoked/unconfirmed context; budget overflow; cancel/all-removed/stale/replayed confirmation; disabled/missing/tampered credentials; non-DeepSeek profile, fallback, background, redirect, proxy and bad authority; medical request; each of five feedback actions; correction/revocation projection dependency; wrong/missing/symlink cleanup marker; and manifest payload/hash corruption.

## Stop conditions

- Any access, stat, probe, hash, creation, read, write, enumeration, or cleanup of Pilot-7 or its DB; real provider/network; real credential/content; or other provider is an irrecoverable P0 invalidation.
- Any required test only supported by a candidate verifier is `Not Implemented`, not a pass.
- Missing fixed input, candidate identity mismatch, candidate/history write, or a non-target PID/window/WebView is a fail-closed review stop.
- Lock-screen, unavailable AX/screenshot service, or temporary local runtime blockage writes `checkpoint.json` and is `Paused — Resumable`; no unrelated matrix rows are repeated.
