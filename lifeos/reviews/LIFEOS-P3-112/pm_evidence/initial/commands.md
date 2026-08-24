# LIFEOS-P3-112 PM Initial Review Commands

- Scope: PM-only counterexample and submitted Evidence recomputation.
- Candidate source: fixed P3-111 candidate copied to `/private/tmp/lifeos-p3-112-pm-initial-v1/candidate`.
- Toolchain: pre-existing `/Users/xxe/.cargo/bin/cargo` and `/Users/xxe/.cargo/bin/rustc`; no installation and no network.
- Isolation: `CARGO_NET_OFFLINE=true`, `CARGO_TARGET_DIR=/private/tmp/lifeos-p3-112-pm-initial-v1/target`, `TMPDIR=/private/tmp/lifeos-p3-112-pm-initial-v1/tmp`.
- Test: `/Users/xxe/.cargo/bin/cargo test --locked --offline -j 1` from the candidate copy.
- Build: `/Users/xxe/.cargo/bin/cargo build --locked --offline -j 1` from the candidate copy.
- Cleanup: exact removal of `/private/tmp/lifeos-p3-112-pm-initial-v1`; no wildcard or historical-path deletion.

The first PM harness invocation was accidentally started from the workspace root and returned Cargo exit 101 (`Cargo.toml` not found). It performed no candidate test or build. The corrected invocation used the candidate copy as its working directory and is the result reported below.
