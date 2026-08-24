# LIFEOS-P3-104 Rework 1/2 Engineering Report

## Authorization and boundary

- User delivered `lifeos/reviews/LIFEOS-P3-104_pm_review.md` back to the original P3-104 engineering session on 2026-08-23.
- The Review explicitly authorizes same-task Rework 1/2 under unchanged `ABF-P3-104-v1`; no new task, ABF, data, IPC, dependency, risk, freeze, or stage boundary is introduced.
- Initial Engineering Evidence and PM Evidence are read-only. All new Evidence is isolated in this `rework/attempt-1/` directory.

## PM-P3-104-CE-01 remediation

- Replaced final-object `Path::exists()` gates with error-aware `symlink_metadata()` semantics.
- Only `ErrorKind::NotFound` is treated as absence. An existing dangling link returns metadata and is rejected as `database_type_rejected`.
- Parent creation also distinguishes true NotFound from an existing non-directory/link object.
- `capture.sqlite-journal`, `capture.sqlite-wal`, and `capture.sqlite-shm` now reject every directory object, including dangling symlinks.
- Added `dangling_database_and_sidecar_links_fail_closed`, covering final DB plus all three sidecar variants, capture and today denial, link/target/sentinel/DB preservation, and zero candidate residue.
- Actual unsigned debug `.app` replay with a dangling final DB exited before a window/success UI appeared, emitted `database_type_rejected`, preserved the link and missing target, preserved the sentinel, and left zero shadow/sidecar residue.

## PM-P3-104-EV-01 remediation

- Added executable `scripts/offline_actual_app_replay.sh`.
- The runner performs a task-local `cargo clean`, exact `cargo tauri build --debug --bundles app --no-sign --config ... -- --locked`, binary/lock hashing, normal app launch/stop/reopen, dangling-final actual-app rejection, and exact cleanup.
- It uses `CARGO_NET_OFFLINE=true`; no dependency, lock, domain, or system component changed.
- The authoritative successful replay is `offline_actual_app_replay_pass.log`; the earlier successful draft replay is retained as non-authoritative history.

## Results

- Existing static suite: 44/44 PASS.
- Rework-specific static suite: 19/19 PASS.
- Rust unit tests: 7/7 PASS.
- Clean offline actual `.app` bundle: PASS.
- Normal first start/stop/reopen/stop: 4/4 PASS.
- Actual dangling-final startup rejection: PASS; process 0, success UI not rendered.
- Cargo.lock and Frozen ABF: unchanged.
- Initial Engineering Manifest and initial PM Evidence: unchanged.
- `/private/tmp/lifeos-p3-104-rework-replay-*` residual: 0.
- Final counts: P0=0, P1=0, P2=0, Unknown=0, Not Implemented=0.

## Honest diagnostic

`cargo fmt --check` was attempted but the Frozen minimal Rust 1.98.0 toolchain does not include `rustfmt`. No network or component expansion was attempted. This is not an ABF-required check and does not replace compilation/testing; the compiler, seven unit tests, static suites, clean bundle, and actual-app replay all passed.

## Remaining governance

This is an execution-side remediation result only. It is not PM Accepted, not Frozen, not an independent review, and not Stage 4 admission. The same task must return to PM for formal re-review; only a PM Pass followed by user adoption may permit a fresh isolated independent review.
