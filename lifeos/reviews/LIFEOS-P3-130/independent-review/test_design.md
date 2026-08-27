# P3-130 Independent Review Test Design

Status: Frozen before candidate runners, tests, or Engineering dynamic results are read.

## Scope and independence

- Review only `LIFEOS-P3-130` under the corrected Task Contract hash `f39f1ca8460389fa637f8e1e175f43ef67742697efbb5ea1e8081ed8aacd10ec`.
- Read candidate, Engineering Evidence, delivery and PM materials only; never import, copy, call, or modify Engineering tools, tests, runners, Evidence, candidate, delivery, PM review, task card, or ledgers.
- Write only this review directory and use only `/private/tmp/lifeos-p3-130-context-recovery-v1` for task-local build, runtime, synthetic SQLite, raw evidence and cleanup.
- Use fixed synthetic identifiers and text from the Task Contract. Do not access Pilot, real data, historical runtime roots, network, model, Agent, Vault, filesystem inputs, or a sixth IPC.

## Entry gates

1. Recompute and compare the corrected Task Contract hash, 75-line physical source allowlist hash/row structure, Frozen Architecture V1.0 hash, P3-128 contract-input hashes, and Engineering FINAL_MANIFEST hash.
2. Verify candidate lineage is exactly 75 allowlisted files, with no missing/extra files and retained inputs unchanged.
3. Inspect the candidate directly for exactly five commands, strict DTO boundaries, no renderer/resolver SQL/filesystem/network/model/Agent path, root fail-closed behavior, and no prohibited capability.
4. Establish this review root and exact temp root as the only writable locations. Before mutations, create an unchanged pristine control and record protected hashes.

## Independent verification matrix

| Acceptance rows | Independent actions and raw evidence |
|---|---|
| AC-01, AC-13 | Recompute hashes and 75/75 lineage; inventory protected sources, candidate and review evidence; verify a non-self-referential review Manifest and exact temp-root absence after cleanup. |
| AC-02, AC-11 | Build/run offline in task-local cache; enumerate actual Tauri command surface and capability; exercise strict existing DTOs and root-invalid startup; scan paths forbidden to UI/resolver. |
| AC-03, AC-04 | New empty SQLite DB; actual Tauri `capture_record` with fixed text/key; repeat same key; record UI, IPC, DB tables and audit before candidate/after candidate. |
| AC-05 | Actual Tauri confirm; repeat confirm; fresh-run reject; test decision/idempotency conflict and mismatched capture. Record append-only Feedback and typed Link facts. |
| AC-06, AC-07 | Close the actual app and relaunch against the same task-local DB; obtain Today, context and Memory provenance through the permitted commands and correlate to DB/audit/UI. |
| AC-08 | Record Inspector selection, temporary removal and close/reopen. Prove durable DB/audit hash unchanged across selection removal and UI reopening. |
| AC-09, AC-10 | Use only disposable copies/new synthetic DBs to independently make source/version/generation/tombstone/authorization/evidence invalid plus unknown/illegal context/capture/duplicate conflict. Each must fail closed before DB/audit changes. |
| AC-12 | Preserve per-action raw logs and structured rows tying the same actual Tauri run to UI state, IPC request/response, SQLite/audit state and close/reopen. Capture three logical native content sizes: 1280x1024, 1160x768, 700x760; distinguish host visibility from logical geometry. |

## Adversarial checks

- Unchanged pristine negative control must pass before changes.
- Each mutation independently alters a disposable input and must be rejected for the expected condition, with before/after DB and audit hashes.
- Verify no mutation returns reliable advice or persists new facts.
- Verify no action runs after a failing setup gate; never reinterpret screenshots, static scans, or Engineering self-checks as dynamic proof.

## Completion rule

The review can conclude Pass only if AC-01 through AC-13 have fresh review evidence and no new P0, P1, Unknown or Not Implemented. The Engineering-side out-of-bound `/private/tmp/p3-130-manifest-parse.json` remains a preserved historical P1 and is neither deleted, excused, nor used as positive evidence. PM alone decides whether this clean independent evidence closes the outstanding Closure Cycle.
