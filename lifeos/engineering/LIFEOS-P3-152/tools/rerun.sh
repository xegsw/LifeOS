#!/bin/bash
set -euo pipefail
ENGINE="$(cd "$(dirname "$0")/.." && pwd)"
TASK_ROOT=/private/tmp/lifeos-p3-152-health-conversation-v1
NODE=/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
export LIFEOS_P3_152_MODE=synthetic CARGO_TARGET_DIR="$TASK_ROOT/target" TMPDIR="$TASK_ROOT/tmp"
umask 077
python3 "$ENGINE/tools/check_root.py"
python3 "$ENGINE/tools/verify_inputs.py"
python3 "$ENGINE/tools/verify_package.py"
OUT="$TASK_ROOT/rerun-$(date +%Y%m%dT%H%M%S)-$$"
mkdir "$OUT"
/Users/xxe/.cargo/bin/cargo test --locked --offline --bin lifeos-p3-152 --manifest-path "$ENGINE/candidate/Cargo.toml" > "$OUT/rust.log" 2>&1
/Users/xxe/.cargo/bin/cargo build --locked --offline --features synthetic-driver --bin synthetic-driver --manifest-path "$ENGINE/candidate/Cargo.toml" > "$OUT/driver.log" 2>&1
"$NODE" "$ENGINE/tools/integration_tests.mjs" > "$OUT/integration.json"
/Users/xxe/.cargo/bin/cargo build --locked --offline --bin lifeos-p3-152 --manifest-path "$ENGINE/candidate/Cargo.toml" > "$OUT/app.log" 2>&1
printf '%s\n' "$OUT"
