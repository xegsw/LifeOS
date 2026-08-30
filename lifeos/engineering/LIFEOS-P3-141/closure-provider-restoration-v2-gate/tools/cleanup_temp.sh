#!/bin/zsh
set -eu

task_tmp=/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1
closure_root="${0:A:h:h}"
receipt="$closure_root/evidence/cleanup_receipt.json"
marker="$task_tmp/.lifeos-p3-141-provider-restoration-v2-gate.marker"

if [[ "$task_tmp" != "/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1" ]]; then
  print -u2 "unexpected cleanup target"
  exit 64
fi
if [[ ! -f "$marker" || "$(tr -d '\r\n' < "$marker")" != "lifeos-p3-141-provider-restoration-v2-gate-v1:synthetic-only" ]]; then
  print -u2 "required marker absent or mismatched"
  exit 65
fi
if [[ -e "$receipt" ]]; then
  print -u2 "cleanup receipt already exists"
  exit 66
fi
rm -rf "$task_tmp"
if [[ -e "$task_tmp" ]]; then
  print -u2 "exact cleanup did not remove target"
  exit 67
fi
print '{"schema":"lifeos.p3-141.provider-restoration-v2-gate.cleanup.v1","status":"REMOVED_EXACT_TASK_ROOT","temporary_root":"/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1","marker_required":true,"root_exists_after":false,"prohibited_target_access":false}' > "$receipt"
