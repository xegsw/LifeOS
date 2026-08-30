#!/bin/zsh
set -eu

closure_root="${0:A:h}"
task_tmp=/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1
if [[ -e "$task_tmp" ]]; then
  print -u2 "refusing replay: exact temporary root already exists"
  exit 64
fi
mkdir -p "$task_tmp/runtime" "$task_tmp/cargo-target" "$task_tmp/gate-tests"
print -n 'lifeos-p3-141-provider-restoration-v2-gate-v1:synthetic-only' > "$task_tmp/.lifeos-p3-141-provider-restoration-v2-gate.marker"
cd "$closure_root/candidate"
env -u LIFEOS_P3_141_PHASE_B_RECEIPT -u LIFEOS_P3_141_PHASE_B_RECEIPT_PATH -u LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH CARGO_NET_OFFLINE=true LIFEOS_RUNTIME_ROOT="$task_tmp/runtime" LIFEOS_INPUT_MODE=synthetic LIFEOS_P3_141_BUILD_MODE=synthetic_review LIFEOS_P3_141_V2_GATE_TEST_ROOT="$task_tmp/gate-tests" CARGO_TARGET_DIR="$task_tmp/cargo-target" /Users/xxe/.cargo/bin/cargo test
print 'Synthetic v2 gate replay passed. Use zsh tools/cleanup_temp.sh after collecting a new task-local receipt; never reuse this closure as independent-review evidence.'
