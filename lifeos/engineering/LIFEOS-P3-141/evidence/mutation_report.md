# P3-141 Phase A mutation report

- Baseline candidate: 79 files, tree SHA-256 `6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e`.
- Current candidate: 79 files, tree SHA-256 `e2f6a9f85ba5dbd462519d84fce015aed8eda63f2e6b773493c9336ed1d0eff7`.
- Changed paths are exactly `Cargo.lock`, `Cargo.toml`, `build.rs`, `src/runtime.rs`, `tauri.conf.json`, `ui/runtime-adapter.js`, and `ui/index.html`. The final title-only change ensures the native browser document title presents the P3-141 candidate identity at every viewport while retaining P3-140 Today semantics in the page body.
- Negative mutations covered by the final successful test run: unsupported Provider profile, unsafe endpoint, stale enablement, malformed/oversize/timeout/disconnect Provider replies, revoked authorization after dispatch, invalid DTO/IPC/database/path inputs, feedback and budget failure closure.
- The Provider transition mutation is explicit: after one successful synthetic loopback send, switching from Ollama to LM Studio returns `provider_locked_after_first_send`; reloading keeps the lock and does not enable or resend.
- No mutation test uses a real root, real text, Health values, credentials, or network target.
