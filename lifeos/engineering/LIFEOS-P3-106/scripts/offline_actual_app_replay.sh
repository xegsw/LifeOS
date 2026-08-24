#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"
if command -v cargo >/dev/null 2>&1; then cargo_bin=$(command -v cargo); else cargo_bin=/Users/xxe/.cargo/bin/cargo; fi
CARGO_NET_OFFLINE=true "$cargo_bin" test --locked
CARGO_NET_OFFLINE=true "$cargo_bin" build --locked
CARGO_NET_OFFLINE=true "$cargo_bin" tauri build --debug --bundles app --no-sign --config '{"bundle":{"active":true,"targets":["app"]}}' -- --locked
echo "Offline locked test/build/bundle complete. Actual app interaction is recorded separately in evidence/dynamic_closure.json."
