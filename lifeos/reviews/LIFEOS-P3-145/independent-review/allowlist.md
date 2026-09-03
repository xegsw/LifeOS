# LIFEOS-P3-145 Phase B Independent Review — Allowlist

This allowlist was written before candidate contact.

## Writable review-controlled locations

- `lifeos/reviews/LIFEOS-P3-145/independent-review/` only.
- `/private/tmp/lifeos-p3-145-independent-review-v1` only, after it is created as a 0700 review-owned temporary root with a regular 0600 marker.

## Read-only inputs before and after sealing

- Frozen task card, ABF, acceptance freeze manifest, applicable governance/role/stage/architecture inputs, and the prescribed independent-review template.
- The exact Git commit `579914d06923db65db8c3b421b2da663a1950354` and only its `lifeos/engineering/LIFEOS-P3-145/` candidate tree, inspected through a detached, read-only snapshot after commit identity binding.
- The exact P3-144 historical inputs named by the Frozen manifest and task card, read-only, only after their recorded hashes are checked.
- Candidate branch name `codex/l3-p3-145-engineering-phase-a` may be used only to compare its resolved commit with the fixed commit; it is never a substitute for the fixed commit.

## Allowed executables and evidence types

- Git read-only object inspection; SHA-256 hashing; review-owned Rust/Tauri build and test execution; SQLite against only the review-created synthetic DB; native Accessibility inspection and target-window screenshots; review-owned mutation scripts; marker-gated cleanup script.
- Fixed non-sensitive synthetic canaries and metadata-only receipts. All review-created sources, logs, screenshots, test results, hashes, command audit, checkpoint, and final manifest must stay in the review root or the permitted temporary root.

Anything not enumerated here is denied. Candidate-provided verifier/test output may be recorded as background only and is never positive independent evidence.
