# PM-P3-104-CE-01｜Dangling final DB symlink is accepted and replaced

## Frozen mapping

- Severity: P1.
- L1: L1-1 数据主权、L1-4 失败关闭、L1-7 Evidence 诚实、L1-10 可复核性。
- L2: ABF-I-05、ABF-I-07、ABF-I-11；ABF-M-008、ABF-M-012。
- Candidate: `src/runtime.rs` SHA-256 `b67d210cf80238549d1e049ab09d0c01717534337d7b1e856684e4091cf44056`。
- Frozen lock: `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1`。

## Fixed non-sensitive fixture

- Root: `/private/tmp/lifeos-p3-104-pm-dangling-20pdjCDD`。
- Initial final DB object: dangling symlink `capture.sqlite -> /private/tmp/lifeos-p3-104-pm-dangling-20pdjCDD/missing.sqlite`。
- Sentinel: fixed text `P3-104-PM-DANGLING-SENTINEL`。
- No retained pilot, personal data, network, cloud or external target was used.

## Actual action and observation

1. PM built the candidate offline with the Frozen lock and launched the actual unsigned Tauri `.app` with the above `capture.sqlite` path.
2. Startup succeeded and the actual page displayed the empty backend state instead of rejecting the final symlink object.
3. PM activated the actual `明确确认本地保存` control.
4. The actual app displayed `已保存：SQLite 原子发布完成后 backend 返回成功。` and one user-original record.
5. After the action, `capture.sqlite` was a regular single-link SQLite file, `quick_check=ok`, captures=1, audit=1. The dangling symlink directory entry had been replaced.
6. The symlink target remained missing and the sentinel hash remained `2764869beb165aafdc854afdef660fe730542470af3d1f3e5540c572fd511d73`.

## Root cause

`validate_database_path()` gates final-object inspection with `if path.exists()`. Rust `Path::exists()` is false for a dangling symlink, so `symlink_metadata()` and the explicit link/type rejection are skipped. The later atomic rename replaces the dangling symlink entry and reports success.

## Required same-ABF remediation

- Inspect final DB and relevant sidecar objects with `symlink_metadata()`／error-aware `lstat` semantics that distinguish `NotFound` from an existing dangling link or other inaccessible object.
- Reject every final DB link type, including dangling links, before app startup or capture mutation.
- Add a real runtime regression proving dangling final DB symlink rejection, sentinel/target/DB state unchanged, no candidate/sidecar residue and no success UI.
- Review the same `exists()` pattern for `-journal`／`-wal`／`-shm` objects and add the corresponding dangling-object regressions where applicable.

This remains the same user result, directory, data, IPC, dependency and ABF boundary. It is eligible for P3-104 Rework 1/2; no new task or ABF change is required.
