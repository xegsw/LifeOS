#!/bin/zsh
set -eu

closure_root="${0:A:h}"
task_tmp=/private/tmp/lifeos-p3-141-provider-restoration-closure-v1
if [[ -e "$task_tmp" ]]; then
  print -u2 "refusing replay: exact temporary root already exists"
  exit 64
fi
mkdir -p "$task_tmp/runtime" "$task_tmp/cargo-target"
print -n 'lifeos-p3-141-provider-restoration-closure-v1' > "$task_tmp/.lifeos-p3-141-provider-restoration.marker"
export CARGO_NET_OFFLINE=true
export LIFEOS_RUNTIME_ROOT="$task_tmp/runtime"
export LIFEOS_INPUT_MODE=synthetic
export LIFEOS_P3_141_BUILD_MODE=synthetic_review
export CARGO_TARGET_DIR="$task_tmp/cargo-target"
cd "$closure_root/candidate"
/Users/xxe/.cargo/bin/cargo test --bin lifeos-p3-141
print 'Synthetic regression complete. actual-Tauri and final evidence require a fresh, separately documented direct-PID run; do not reuse retained evidence.'
