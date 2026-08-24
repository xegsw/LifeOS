# LIFEOS-P3-104 official toolchain bootstrap record

## Authorized boundary

- Task-card delivery received: `2026-08-23T12:28:01+0800`.
- Frozen ABF explicitly authorizes the one-time official Rust/Tauri bootstrap and requires the network to stop after dependency closure.
- Network was used only for official `rustup.rs`, `static.rust-lang.org`, and crates.io supply. No retained pilot or personal data path was accessed.

## Toolchain

- rustup: `1.29.0 (28d1352db 2026-03-05)`.
- rustc: `1.98.0 (88d9e12ae178fab0fb5cc050a94da85685d449ea)`, host `aarch64-apple-darwin`, LLVM `22.1.8`.
- cargo: `1.98.0 (797e8a9bca276c1c9f9f738d2a20f484fa4eea9d)`.
- tauri-cli: `2.11.4`.
- `rustup-init.sh`: 29,250 bytes, saved `2026-08-23T12:32:41+0800`, SHA-256 `6c30b75a75b28a96fd913a037c8581b580080b6ee9b8169a3c0feb1af7fe8caf`.
- `cargo-tauri`: 33,955,200 bytes, installed `2026-08-23T14:33:46+0800`, SHA-256 `da2bd22945b356fa4d8e4d5b7eaab0b2e26df81b63d1a17a63b90d2f61c37ca7`.

## Dependency closure

- Direct Rust dependencies are exact-pinned in `Cargo.toml`.
- `Cargo.lock` was frozen at `2026-08-23T14:42:13+0800` with SHA-256 `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1`.
- Lock inventory: 438 packages, zero unresolved entries.
- Lock-generation log SHA-256: `2bca1a242a775aabec147258ce48d83b174d572e39599c0c7186b543c6d8308c`.
- Locked fetch log SHA-256: `6223be76c79507379ff1ae058589aabce4f7637f5784f642d3c603f754da50d2`.
- Tauri CLI install log SHA-256: `290900b90a3125c270547c3073c79cb07223e1a71407053a6ae97039ec4574e6`.
- `rusqlite` uses the exact-pinned `bundled` SQLite feature; this avoids a runtime dependency on an uncontrolled system SQLite build.

## Honest bootstrap incidents

- A concurrent rustup retry collided with the first still-running install and reported a cargo component-cache rename failure. The final toolchain was repaired only by removing and re-adding the same official `cargo` component for Rust 1.98.0; the final versions above were independently verified.
- The official locked tauri-cli dependency set includes the yanked transitive `spin 0.9.8`; `--locked` was intentionally retained and no dependency substitution was made.
- Several recoverable crates.io HTTP/2 stream errors occurred and remain in the logs.
- The final `cargo fetch --locked` stopped producing output after downloading the dependency set and was interrupted with exit 130 at `2026-08-23T15:20:55+0800`. Completeness was not inferred from that exit: a clean `CARGO_NET_OFFLINE=true cargo test --locked` and `cargo tauri build ... -- --locked` subsequently resolved and compiled all 438 locked packages with no network.

## Offline boundary after closure

- All compile, test, runner, debug build, and actual-app execution commands after dependency closure used `CARGO_NET_OFFLINE=true` and the frozen lock.
- The real UI candidate was packaged only as a local unsigned debug `.app` using a one-command config override; repository config retains `bundle.active=false`, so no production bundle or release claim is made.
