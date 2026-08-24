#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"
if command -v cargo >/dev/null 2>&1; then cargo_bin=$(command -v cargo); else cargo_bin=/Users/xxe/.cargo/bin/cargo; fi
python3 tests/verify_preflight.py
CARGO_NET_OFFLINE=true "$cargo_bin" test --locked
CARGO_NET_OFFLINE=true "$cargo_bin" build --locked
python3 tests/verify_dynamic_closure.py
