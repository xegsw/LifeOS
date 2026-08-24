# LIFEOS-P3-103 Independent Test Design

Status: frozen before candidate-source inspection  
Basis: task card, ABF-P3-103-v1, P3-102 task/ABF/deliverable/PM Review, and the two submitted manifests only.  
Prohibited design inputs: P3-102 runner implementation and P3-097 candidate source.

## Independence and privacy contract

- The independent runner is newly written for P3-103 and must not import, execute, copy, or inspect P3-102 `runner.py`.
- Real retained content is limited to one immutable/query-only read of the single capture text. The text exists only in a minimal local scope for an in-memory SHA-256 comparison with the authorized P3-102 attestation, then is discarded. No text, idempotency key, expected hash, actual hash, DB hash, page body, SQL dump, DB/page copy, or derived fragment may enter output, logs, Evidence, commands, or chat.
- The real page is never opened, read, parsed, hashed, copied, or screenshotted.
- All dynamic lifecycle and boundary tests use fresh fixed non-sensitive fixtures under `/private/tmp/lifeos-p3-103-*`. They never use real retained input or key and never call `clear`.
- Every parent ABF row and leaf test has unique test, fixture, and execution IDs, explicit before/after observations, an actual assertion, a log/result reference, and PASS/FAIL. Missing rows, duplicate IDs, prohibited fields, or unverifiable results cause non-zero exit.

## Fixed non-sensitive fixture specification

- Text A: a constant string explicitly marked as a P3-103 non-sensitive test fixture.
- Text B: a distinct constant string explicitly marked as a P3-103 non-sensitive conflict fixture.
- Key A: a task-local synthetic idempotency identifier unrelated to the retained real key.
- Root: a fresh directory created by `tempfile.mkdtemp(prefix="lifeos-p3-103-", dir="/private/tmp")` after confirming it did not pre-exist.
- Allowed live fixture assets: one `capture.sqlite`, one `today.html`, and runner-owned sentinel files used only within the fresh root.
- All fixture roots are precisely removed after structured Evidence is safely written. No SQLite, HTML, pyc, cache, temporary DB, shadow, journal, WAL, SHM, or sentinel remains.

## Frozen test matrix

| ABF row | Test ID | Fixture ID | Required independent action and assertion |
|---|---|---|---|
| M-001 | P3-103-T-001 | P3-103-F-001 | Verify task-card delivery, new-session independence statement, receive time, prior user authorization, ABF ID/status/hash, and no ambiguity. |
| M-002 | P3-103-T-002 | P3-103-F-002 | Recompute the ten fixed-input hashes, all 17 Engineering Manifest entries, and all 5 PM Manifest entries before and after; require complete match and no mutation. |
| M-003 | P3-103-T-003 | P3-103-F-003 | `lstat` `/`, `/Users`, `/Users/xxe`, `/Users/xxe/Documents`, the exact retained directory, DB, and page; list only the exact directory filenames; require no symlink ancestor, directory 0700, regular DB/page 0600, nlink 1, and exactly two allowed files. |
| M-004 | P3-103-T-004 | P3-103-F-004 | Open only the exact DB using SQLite URI `mode=ro&immutable=1`, set and verify `query_only=ON`, select only the single capture text (never key), compare its in-memory digest to the authorized attestation, discard it, close immediately, and emit only record count and `match`. Require zero sidecars before/after. |
| M-005 | P3-103-T-005 | P3-103-F-005 | With the same immutable/query-only constraints, query only schema names/definitions needed for canonical validation and non-content source/status/count/time/audit facts. Require one capture, expected audit lifecycle/order/time, `local_capture`, canonical constraints, and no selection/output/hash of text or key. |
| M-006 | P3-103-T-006 | P3-103-F-006 | Validate the submitted user visual-confirmation Evidence chain and retained page metadata without opening or hashing the page. |
| M-007 | P3-103-T-007 | P3-103-F-007 | Re-run exact retained metadata, filename, sidecar, and non-content structure observations after queries; require all allowed observations unchanged. Never hash the DB or page. |
| M-008 | P3-103-T-008 | P3-103-F-008 | In a fresh fixture, independently invoke candidate CLI for first saved, same-key/same-text repeat, same-key/different-text conflict, process-restart today, process-restart render, and injected failure. Require accurate statuses, counts, audit semantics, page behavior, failure atomicity, and zero sidecars/shadows. |
| M-009 | P3-103-T-009 | P3-103-F-009 | Independently attack non-canonical paths, ancestor/final symlinks, DB/page hardlinks, FIFO/directory special targets, and external output. Require pre-change rejection and unchanged sentinels/DB/page for every leaf. |
| M-010 | P3-103-T-010 | P3-103-F-010 | Feed the Evidence validator deliberately missing-row, duplicate-ID, prohibited-field, and unverifiable-result documents. Require rejection and non-zero status for each. |
| M-011 | P3-103-T-011 | P3-103-F-011 | Static and dynamic observation: candidate surface used only for capture/today/render; `clear` invocation count zero; no Tauri/IPC/Vault/export/network/cloud/sync/multi-device/L3/external-user capability. |
| M-012 | P3-103-T-012 | P3-103-F-012 | Recompute all protected hashes, run privacy/prohibited-artifact scan, verify exact temp cleanup and unchanged retained assets, and report R-0052 Open, R-0040 Open/Conditional, R-0051 limited closed, assets Not Frozen, Stage 3 unchanged. |

## Required boundary leaves

M-009 must contain separately executed leaves for relative path, dot/dotdot normalization, ancestor symlink, final DB symlink, final page symlink, DB hardlink, page hardlink, FIFO target, directory target, and caller-selected external output. Each leaf receives its own unique test/fixture/execution ID and before/after assertion.

## Required lifecycle leaves

M-008 must contain separately executed leaves for first save, idempotent repeat, conflicting repeat, fresh-process today, fresh-process render, and injected failure. The render body may be inspected only for the fixed non-sensitive fixture and must not be copied into Evidence; structured Evidence records only semantic booleans/counts.

## Evidence validation and exit formula

The runner exits zero only if I-01 through I-12 and M-001 through M-012 plus every leaf are actually PASS; P0/P1/P2/Unknown/Not Implemented are all zero; protected hashes match before/after; retained observations are unchanged; privacy scan hits zero; and temporary residue is zero. No N/A is accepted.

This file becomes immutable test-design evidence after its SHA-256 is recorded. Later candidate-source inspection may clarify invocation mechanics but must not add, remove, or weaken assertions.
