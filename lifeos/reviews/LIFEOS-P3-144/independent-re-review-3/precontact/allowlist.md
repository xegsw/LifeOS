# LIFEOS-P3-144 independent re-review-3 — precontact allowlist

## Review-owned writable paths

- `lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/`
- `lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/precontact/`
- `lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/work/`
- `/private/tmp/lifeos-p3-144-independent-review-v1`

## Review-owned work subpaths

- `work/cargo-target/` — the only Cargo target output directory.
- `work/home/`, `work/tmp/`, and any review cache directory under `work/` — HOME/TMP/cache containment.
- `work/tests/`, `work/fixtures/`, `work/logs/`, `work/screenshots/`, `work/verification/`, and `work/markers/` — independently authored sources and generated artifacts.

## Read-only paths after seal verification

- The exact fixed task card and `ABF-P3-144-v1`.
- `lifeos/engineering/LIFEOS-P3-144/` and `lifeos/deliverables/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md` only as candidate/engineering inputs, never writable.
- `lifeos/engineering/LIFEOS-P3-143/candidate/` and the formal P3-143 Task, ABF, PM Review, final Independent Review, Evidence, and Manifest only as historical read-only inputs.
- P3-138 formal inputs, D-0595–D-0614 decisions, the Frozen Architecture V1.0, and the model-settings baseline, all read-only.
- Git metadata only for commit and blob identity checks; no history rewriting, branch switching, or index modification.

## Tool and network limits

- Cargo/Rust/Tauri and local macOS native accessibility/screenshot tooling are allowed only with review-owned output/cache containment.
- Any synthetic HTTP harness must remain local and must not open a real network connection.
- No real Provider authority, credential store secret, real user text, Pilot, external website, proxy, redirect, or unrelated workspace path is in scope.
