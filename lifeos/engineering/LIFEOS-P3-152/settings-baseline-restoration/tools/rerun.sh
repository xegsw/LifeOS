#!/bin/bash
set -euo pipefail
D="$(cd "$(dirname "$0")/.." && pwd)"
TASK_ROOT=/private/tmp/lifeos-p3-152-health-conversation-v1
export TMPDIR="$TASK_ROOT/tmp" CARGO_TARGET_DIR="$TASK_ROOT/real-target" LIFEOS_P3_152_MODE=synthetic
umask 077
python3 "$D/tools/verify_package.py"
OUT="$TASK_ROOT/settings-restoration-rerun-$(date +%Y%m%dT%H%M%S)-$$"
mkdir "$OUT"
/Users/xxe/.cargo/bin/cargo test --locked --offline --features synthetic-driver --bin lifeos-p3-152 --manifest-path "$D/candidate/Cargo.toml" > "$OUT/host.log" 2>&1
/Users/xxe/.cargo/bin/cargo build --locked --offline --features synthetic-driver --bin synthetic-driver --manifest-path "$D/candidate/Cargo.toml" > "$OUT/driver.log" 2>&1
NODE=/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
"$NODE" "$D/tools/integration_tests.mjs" > "$OUT/integration.json"
"$NODE" "$D/tools/combined_tests.mjs" > "$OUT/combined.json"
"$NODE" --test "$D/tools/settings_tests.mjs" "$D/tools/health_view_tests.mjs" "$D/tools/sources_ui_tests.mjs" > "$OUT/ui.log" 2>&1
printf '%s\n' "$OUT"
