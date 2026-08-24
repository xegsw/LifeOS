# LIFEOS-P3-104 PM Rework 1/2 Replay Summary

## Boundary

- Frozen basis: `ABF-P3-104-v1`, unchanged hash `2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b`.
- Candidate: Rework 1/2 submission under the original P3-104 authorization.
- Data: fixed non-sensitive fixtures only; retained pilot and real personal content were not accessed.
- Network: replay used locked offline Cargo/Tauri execution.

## Hash and Evidence verification

- Rework Manifest: 16/16 entries verified before PM Review update.
- Frozen historical inputs: 14/14 matched.
- Initial Engineering Manifest: unchanged at `861d0be5bc40d1ebac41cc8b5a695d154d3bf073407b5fc6e3e85e42532a3f46`.
- Initial PM Evidence Manifest: unchanged at `dbce89510ea161181b9e997579ff92da0019bb93a2e9857ae415ba5484faf9c6`.
- Cargo.lock: unchanged, 438 packages and zero inventory failures.

## Fresh isolated replay

PM copied the candidate without its build target to `/private/tmp/lifeos-p3-104-pm-rework-M6fV9M`, supplied only the Frozen read-only hash inputs required by the submitted verifier, and ran:

- Rework checks: 19/19 PASS.
- Existing static checks: 44/44 PASS.
- Rust runtime unit tests: 7/7 PASS.
- Locked offline debug build: PASS.
- Submitted locked offline actual `.app` bundle/replay: PASS.
- Normal actual-app start/stop/reopen/stop: 4/4 PASS.
- Submitted actual-app dangling-final rejection and cleanup: PASS, residual 0.
- Dynamic Evidence verifier: 17/17 PASS.
- Lock inventory: 438/438 PASS.

PM independently launched the isolated actual binary against four direct task-local roots containing dangling symlinks at `capture.sqlite`, `-journal`, `-wal`, and `-shm`. All four exited fail-closed with the expected type/sidecar rejection; each link and missing target state was preserved, the sentinel remained unchanged, and candidate residue was zero.

## Honest diagnostics

The first `offline_verify.sh` call stopped because the PM-created minimal copy did not yet include the 14 Frozen historical files that `static_checks.py` hashes. PM copied those exact read-only inputs and reran without changing the candidate. The first external counterexample used a second-level `/private/tmp` directory and correctly failed earlier at the task-local path schema gate; PM removed it and reran with four direct `/private/tmp/lifeos-p3-104-*` roots.

## Governance note

The user-observed difference from the original frozen Stitch screens is real. It does not block this ABF because P3-104 froze the P3-091 semantic UI baseline, not high-fidelity Stitch reproduction. It is recorded as a separate new-task candidate and must not be retroactively added to this Rework acceptance basis.

## Result

`Accepted / PM Pass / Awaiting User Adoption`; P0=0, P1=0, P2=0, Unknown=0, Not Implemented=0. Assets remain Not Frozen; R-0040/R-0052 remain Open and R-0051 remains unchanged; no Stage 4 admission.
