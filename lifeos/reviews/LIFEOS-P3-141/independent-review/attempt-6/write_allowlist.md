# LIFEOS-P3-141 attempt-6 Write Allowlist

## Allowed writes

- `/Users/xxe/.codex/worktrees/b443/No.2/lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-6/**`
- `/private/tmp/lifeos-p3-141-controlled-pilot-v1/**` only after a task-local marker is created and only for fresh synthetic fixtures, synthetic SQLite, review-owned build products and ephemeral actual-Tauri artifacts.

## Allowed final artifacts

- `test_design.md`, `write_allowlist.md`, `precontact_seal.json`, `precontact_hashes.sha256`
- `independent_review.md`, `FINAL_MANIFEST.json`, `rerun.md`, `review_result_matrix.json`
- review-owned `tools/`, `evidence/matrices/`, `evidence/raw/`, `evidence/logs/`, `evidence/screenshots/`, `evidence/mutations/`, and cleanup receipt files under this attempt root.

## Forbidden writes and operations

- All candidate roots, including `lifeos/engineering/LIFEOS-P3-141/**`, are read-only.
- All PM ledgers, tasks, risk/freeze/stage records, deliverables and prior reviews are read-only.
- Do not write outside the two listed roots; do not create, enumerate, stat, hash, copy, access or clean Pilot-6, an existing Pilot, a real DB/path/text/Health item, a real Provider endpoint, credential store or network target.
- Do not reuse or overwrite attempt-1 to attempt-5 assets.  Do not clean any root except the one exact temporary root under its marker gate.
