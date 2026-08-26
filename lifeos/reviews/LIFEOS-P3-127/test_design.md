# LIFEOS-P3-127 Independent Test Design

## Independence commitment

This plan is authored in the P3-127 review root before any P3-126 historical runner, test result, candidate source, delivery, Review, or Engineering Evidence is read. The review will not import, copy, execute, or subprocess any P3-126 runner. All P3-127 scripts will be authored in this root and recorded in the final Manifest.

## Fixed review boundary

- Read-only candidate: `lifeos/engineering/LIFEOS-P3-126/candidate/`.
- Writable review root: `lifeos/reviews/LIFEOS-P3-127/`.
- Exact disposable root: `/private/tmp/lifeos-p3-127-independent-review-v1`.
- Runtime authority under test: build-time `LIFEOS_RUNTIME_ROOT` only.
- Permitted IPC: `capture_record`, `get_today`, `runtime_status` only.
- No old P3-122 Runtime-root access of any kind; no network, Pilot, real data, new IPC, capability, Schema/API, export, clear, permission, recovery, cloud, or model operation.

## Independent test matrix

| ABF row | P3-127 test | Independent method and evidence |
|---|---|---|
| M-001 | P127-M001 | Hash Frozen inputs; parse 75 physical allowlist rows; record user platform confirmation and two initial roots absent. |
| M-002 | P127-M002 | Inspect only P3-127 scripts for P3-126 runner imports, copies, or subprocess references. |
| M-003 | P127-M003 | Parse Frozen allowlist; independently SHA-256 and byte-count exactly its 75 candidate files. |
| M-004 | P127-M004 | Copy only listed candidate files to the exact disposable root; run locked offline test/build/bundle with root-local Cargo/TMP paths and capture logs. |
| M-005 | P127-M005 | Run the bundled App independently under two fresh authorized Runtime roots; record native/UI, process, IPC and derived-path evidence. |
| M-006 | P127-M006 | Exercise status, first capture, repeat, refresh and close/reopen; bind each to UI/screenshot, IPC result, DB/audit and process/log evidence. |
| M-007 | P127-M007 | Independently test invalid, file, symlink and DB failure paths; assert failure precedes DB/sentinel/history mutation. |
| M-008 | P127-M008 | Statically and dynamically inventory permitted IPC/capability surface; prove no old-root access from logs and source. |
| M-009 | P127-M009 | Recompute Frozen hashes for all named P3-126 protected assets after execution. |
| M-010 | P127-M010 | First run an unchanged pristine control; then apply each Frozen disposable mutation and require a fail-closed verifier result. |
| M-011 | P127-M011 | Close App, remove only the exact disposable root by explicit path, and verify it absent while review Evidence remains. |
| M-012 | P127-M012 | Recompute a non-self-referential Manifest and reconcile every ABF row to raw logs/results/hashes before writing the Review. |

## Stop conditions

Stop Blocked before or during execution if an authorization boundary, Frozen input hash/semantics, offline restriction, old-root zero-touch constraint, protected history hash, native identity, or required actual-app Evidence cannot be met without expanding this Task Contract. Never infer native geometry or dynamic state from static source, configuration, thumbnails, or aggregate test totals.
