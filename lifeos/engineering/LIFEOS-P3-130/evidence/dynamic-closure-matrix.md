# LIFEOS-P3-130 Dynamic Closure Matrix

| AC | Engineering precheck | Machine-checkable Evidence |
|---|---|---|
| AC-01 | PASS | `static-verification.json`: corrected task hash, allowlist hash, 75/75 source lineage, and changed candidate files are enumerated. |
| AC-02 | PASS | `static-verification.json` inventories exactly five commands; `unit-tests.log` covers strict DTOs, root boundary, lifecycle and fail-closed behavior. |
| AC-03 | PASS | `actual-app-action-trace.json` run-a empty/candidate/repeat states; `run-a-candidate-db.json` stores immutable fixed raw text, Source and Artifact; audit becomes saved then repeat. |
| AC-04 | PASS | run-a visible state changes `empty → candidate` only after the capture action; `run-a-candidate-db.json` shows typed link status `candidate`. |
| AC-05 | PASS | run-a `candidate → confirmed` plus append-only Feedback in `run-a-confirmed-db.json`; independent run-b `candidate → rejected` in `run-b-rejected-db.json`; conflict/idempotency negative tests are in `unit-tests.log`. |
| AC-06 | PASS | `actual-app-action-trace.json` preserves run-a confirmed UI before and after actual application close/reopen; `run-a-reopened-db.json` correlates same capture, link, Feedback and audit. |
| AC-07 | PASS | `run-a-confirmed-db.json` contains Source, Artifact/version, typed link, Feedback and audit; UI trace states that Memory is reference-only; no Memory table or copied raw content exists in `static-verification.json`. |
| AC-08 | PASS | trace records `selection_included true → false → true after reopen`; `run-a-selection-before-db.json` and `run-a-selection-after-db.json` have the same SHA-256, so the UI-only removal did not persist. |
| AC-09 | PASS | `unit-tests.log` includes source availability, generation, tombstone, authorization and evidence-gap mutations, each rejected before confirmation write. |
| AC-10 | PASS | `unit-tests.log` covers unknown DTO fields, invalid Context, absent capture, duplicate-key conflict and injected pre-commit failure with durable-hash assertions. |
| AC-11 | PASS | `static-verification.json` verifies the exact command set, renderer invoke set, no legacy fixture adapter loaded, and preserved inherited shell hooks. |
| AC-12 | PASS | `actual-app-action-trace.json`, actual screenshots, native geometry JSONL, and SQLite snapshots together correlate UI, IPC result text, durable state, audit, and restart. |
| AC-13 | PASS (engineering cleanup) | `pre-cleanup-inventory.json`, `cleanup.json`, and `FINAL_MANIFEST.json` record the exact task temporary root, its absence after cleanup, source history check, and a non-self-referential inventory. |

## Actual-app geometry semantics

- `native-geometry-1280x1024.jsonl` proves actual native logical content `1280×1024` at scale `2.0`. Its host screenshot is `960×768`, so it is retained only as a host-visible capture, not asserted as a full logical-pixel image.
- `native-geometry-1160x768.jsonl` proves native logical content `1160×768` at scale `2.0`; its host screenshot is `1160×768`.
- `native-geometry-700x760.jsonl` proves native logical content `700×760` at scale `2.0`; its host screenshot is `700×760`.

Engineering result: all contract rows have local Evidence. This is **Candidate Ready / Awaiting independent review and PM acceptance**, not a self-declared PM Pass, freeze, risk closure, or Stage transition.
