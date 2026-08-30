#!/bin/sh
set -eu

task_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
candidate="$task_root/candidate"
temp_root="/private/tmp/lifeos-p3-141-controlled-pilot-v1"
mkdir -p "$temp_root/runtime" "$temp_root/cargo-target"

python3 -B "$task_root/tools/verify_phase_a.py"
cd "$candidate"
LIFEOS_RUNTIME_ROOT="$temp_root/runtime" \
LIFEOS_INPUT_MODE=synthetic \
CARGO_NET_OFFLINE=true \
CARGO_TARGET_DIR="$temp_root/cargo-target" \
/Users/xxe/.cargo/bin/cargo test --locked --offline -- --test-threads=1
