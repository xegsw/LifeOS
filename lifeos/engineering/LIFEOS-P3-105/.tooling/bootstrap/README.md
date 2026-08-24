# Frozen bootstrap area

Only the Rust installer fetched from `https://sh.rustup.rs`, its SHA-256, the
redirect record, and bootstrap logs may be stored here. After `Cargo.lock` is
frozen, all build, test, runner, and app evidence must run with
`CARGO_NET_OFFLINE=true` and `--locked` where supported.

