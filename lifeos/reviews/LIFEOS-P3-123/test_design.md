# LIFEOS-P3-123 Independent Test Design

## Freeze-before-read record

- Task: `LIFEOS-P3-123`.
- Frozen ABF: `ABF-P3-123-v1`, SHA-256 `7b5f67152c9c50187999d11900d2efc44efe79d2b87e2e33173be0a13dc2302b`.
- Scope: fresh, offline, actual-Tauri review of the read-only P3-122 candidate.
- Write allowlist: `lifeos/reviews/LIFEOS-P3-123/`, the task delivery and local-precheck paths, and `/private/tmp/lifeos-p3-123-independent-review-v1` only.
- Independence rule: no import, copy, call, or execution of `lifeos/engineering/LIFEOS-P3-122/tools/build_evidence.py` or any P3-122 runner/test. Historical result files are inputs to verify, not an oracle.

## Independent test approach

1. Recompute the ABF, authorization, candidate allowlist/tree and all frozen P3-122 PM/Engineering inputs before any candidate copy.
2. Create a P3-123-owned runner that reads raw inputs, writes only task-local results, and produces one record per ABF-M-001 through ABF-M-014 with action, test ID, evidence path, SHA-256 and status.
3. Use a fresh task-local copy of the allowlisted candidate and an empty synthetic SQLite database. Resolve Rust/Cargo paths explicitly, keep `CARGO_TARGET_DIR`, `TMPDIR`, and module caches below the exact temporary root, and enforce offline execution.
4. Perform an actual Tauri build/test and, only if it launches safely, capture each of the six page/state journeys at 1280x1024, 1160x768 and 700x760 with independent native/WebView/DOM geometry. A screenshot cannot substitute for native geometry.
5. Exercise only `capture_record`, `get_today`, and `runtime_status` through first, repeat, refresh and close/reopen paths. Check DB, audit and UI before/after; negative paths must leave database, sentinel and success UI unchanged.
6. Independently scan the candidate/review roots for forbidden capabilities and conduct a nine-class mutation suite after an unchanged pristine control. The verifier must recompute hashes and semantic predicates from raw files.
7. Hash protected P3-122 assets before and after, perform only exact temporary-root cleanup, and report Pass, Rework, or Blocked strictly under the Frozen ABF without mutating PM records, risks, freezes or stage.

## Decision rules

- Any authorization/hash drift, historical modification, P3-122-runner dependency, external write, visual/source mismatch, failed lifecycle/negative path, missing row evidence, or failed mutation is Rework unless an ABF-defined external tool/actual-app condition prevents safe execution.
- Unproved native geometry, runtime state, lineage, history integrity or cleanup remains Unknown; it is never inferred from screenshots, configuration or a successful summary.
- A Blocked conclusion is reserved for an authorized offline toolchain or actual-Tauri condition that cannot start within the frozen boundary and cannot be safely substituted.
