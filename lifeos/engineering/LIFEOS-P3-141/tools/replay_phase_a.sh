#!/bin/sh
set -eu

task_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
candidate="$task_root/candidate"
temp_root="/private/tmp/lifeos-p3-141-controlled-pilot-v1"
workspace_root="$(CDPATH= cd -- "$task_root/../../.." && pwd)"
input_root="${LIFEOS_P3_141_INPUT_ROOT:-$workspace_root}"

if [ "${1:-}" = "--input-root" ]; then
    if [ -z "${2:-}" ] || [ "${3:-}" != "" ]; then
        printf '%s\n' 'usage: replay_phase_a.sh [--input-root /absolute/path]' >&2
        exit 64
    fi
    input_root="$2"
fi
case "$input_root" in
    /*) ;;
    *) printf '%s\n' 'input root must be absolute' >&2; exit 64 ;;
esac
mkdir -p "$temp_root/runtime" "$temp_root/cargo-target"

python3 -B "$task_root/tools/verify_phase_a.py" --input-root "$input_root"
cd "$candidate"
LIFEOS_RUNTIME_ROOT="$temp_root/runtime" \
LIFEOS_INPUT_MODE=synthetic \
CARGO_NET_OFFLINE=true \
CARGO_TARGET_DIR="$temp_root/cargo-target" \
/Users/xxe/.cargo/bin/cargo test --locked --offline -- --test-threads=1
