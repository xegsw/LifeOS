# LIFEOS-P3-125 Initial PM Verification

- Date: 2026-08-26
- Scope: read-only recomputation; PM did not run the submitted verifier because it overwrites Engineering `verification.json`.
- Local model precheck: skipped for P0 Tauri/IPC path and Evidence final judgment.

## Recomputed facts

- Frozen task/ABF/source allowlist hashes match D-0504.
- Source allowlist: 75 rows; P3-125 candidate has 75 corresponding files. Only `build.rs` and `src/runtime.rs` differ from P3-122; 73/75 remain byte-identical.
- Submitted verifier result: 31/31 PASS; PM independently checked the referenced source literals, five fixed hashes, logs, SQLite snapshots, geometry and screenshot file presence.
- Final Manifest: 104 declared rows. 103 declared paths resolve and match bytes/hash. One declared path, `../deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md`, resolves from the Engineering root to a nonexistent path; the declared bytes/hash happen to match the real repository deliverable at a different path.
- Final Manifest hash: `ef6b61c482810639ab5ff0ad88da94ea5fa5363f54bb1eaeba52c8110051acfd`.
- Dynamic closure hash: `58de7abd67cfdea2921a501e3f4b522903d52807d359452485433001503d98a2`.
- Verification JSON hash: `513cbe1d1ba845ed38178e322e00cbe4f913f3b309b15e48399545ec0092eed2`.
- Delivery hash: `63614cfaf45e74a527f0486b7cd2c5dfa818f9abbac5390f27395c1726ef5576`.
- Dynamic closure contains 7 aggregated rows, not 12 independent Frozen rows; M-012 is absent and M-011 is relabeled as Quick Capture rather than mutation.
- No `mutation-results.json`, `cleanup.json`, `preflight.json`, `history-integrity.json` or complete authorization/history Final Manifest layer is present.
- `candidate/build.rs` contains fixed `ALLOWED_PARENT=/private/tmp/lifeos-p3-125-runtime-root-config-v1`; therefore `LIFEOS_RUNTIME_ROOT` is constrained by a second task-ID-specific path authority.
- Fixed P3-125 temporary root is absent at PM verification time.
- Actual model/effort remains Unknown in the submitted record.

## PM result

`REWORK 1/1 / NOT PASS`; counts `P0=2, P1=0, P2=0, Unknown=1, Not Implemented=2`.
