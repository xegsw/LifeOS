#!/bin/zsh
set -eu

task_tmp=/private/tmp/lifeos-p3-141-provider-restoration-closure-v1
closure_root="${0:A:h:h}"
receipt="$closure_root/evidence/cleanup_receipt.json"
marker="$task_tmp/.lifeos-p3-141-provider-restoration.marker"

if [[ "$task_tmp" != "/private/tmp/lifeos-p3-141-provider-restoration-closure-v1" ]]; then
  print -u2 "unexpected cleanup target"
  exit 64
fi
if [[ ! -f "$marker" ]]; then
  print -u2 "required marker absent"
  exit 65
fi
if [[ "$(tr -d '\r\n' < "$marker")" != "lifeos-p3-141-provider-restoration-closure-v1:synthetic-only" ]]; then
  print -u2 "required marker mismatched"
  exit 66
fi
for direct_pid in 78153 78339 78414; do
  if kill -0 "$direct_pid" 2>/dev/null; then
    print -u2 "recorded direct PID is still live: $direct_pid"
    exit 67
  fi
done
rm -rf "$task_tmp"
if [[ -e "$task_tmp" ]]; then
  print -u2 "exact cleanup did not remove target"
  exit 68
fi
if [[ -e "$receipt" ]]; then
  print -u2 "cleanup receipt already exists"
  exit 69
fi
print '{"schema":"lifeos.p3-141.provider-restoration.cleanup.v1","status":"REMOVED_EXACT_TASK_ROOT","temporary_root":"/private/tmp/lifeos-p3-141-provider-restoration-closure-v1","marker_required":true,"recorded_direct_pids":[78153,78339,78414],"root_exists_after":false,"prohibited_target_access":false}' > "$receipt"
