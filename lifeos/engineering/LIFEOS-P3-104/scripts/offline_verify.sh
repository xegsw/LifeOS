#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export RUSTUP_HOME=/Users/xxe/.rustup
export CARGO_HOME=/Users/xxe/.cargo
export CARGO_TARGET_DIR="$PROJECT_ROOT/.tooling/target"
export CARGO_NET_OFFLINE=true
export CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

cd "$PROJECT_ROOT"
python3 tests/static_checks.py
"$CARGO_HOME/bin/cargo" test --locked
"$CARGO_HOME/bin/cargo" tauri build --debug --no-bundle -- --locked
