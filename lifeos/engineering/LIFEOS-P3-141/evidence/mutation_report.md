# P3-141 Phase A mutation report

- Baseline candidate: 79 files, tree SHA-256 `6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e`.
- Current candidate: 79 files, tree SHA-256 `b3c681d5aca74f5f8d8cc0c3114a26f080b2c61091a43e3f3799c7163a656227`.
- Allowed changed paths are exactly `Cargo.lock`, `Cargo.toml`, `build.rs`, `src/runtime.rs`, `tauri.conf.json`, and `ui/runtime-adapter.js`.
- Negative mutations covered by the final successful test run: unsupported Provider profile, unsafe endpoint, stale enablement, malformed/oversize/timeout/disconnect Provider replies, revoked authorization after dispatch, invalid DTO/IPC/database/path inputs, feedback and budget failure closure.
- The Provider transition mutation is explicit: after one successful synthetic loopback send, switching from Ollama to LM Studio returns `provider_locked_after_first_send`; reloading keeps the lock and does not enable or resend.
- No mutation test uses a real root, real text, Health values, credentials, or network target.
