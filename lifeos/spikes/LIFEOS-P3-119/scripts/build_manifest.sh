#!/bin/bash
set -euo pipefail

spike_dir="$(cd "$(dirname "$0")/.." && /bin/pwd -P)"
workspace_dir="$(cd "$spike_dir/../../.." && /bin/pwd -P)"
rg_bin="$(command -v rg)"
manifest="$spike_dir/MANIFEST.md"

hash_file() {
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}

{
  printf '%s\n' '# LIFEOS-P3-119 Evidence Manifest'
  printf '%s\n' ''
  printf '%s\n' 'Non-self; every payload is relative to the workspace root and includes SHA-256 plus bytes.'
  printf '%s\n' ''
  "$rg_bin" --files "$spike_dir" -g '!MANIFEST.md' | /usr/bin/sort | while IFS= read -r path; do
    relative_path="${path#$workspace_dir/}"
    printf '%s  %s  %s\n' "$(hash_file "$path")" "$(/usr/bin/stat -f %z "$path")" "$relative_path"
  done
} > "$manifest"
