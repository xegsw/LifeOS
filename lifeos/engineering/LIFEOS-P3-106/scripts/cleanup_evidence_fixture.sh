#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture_dir=${1:?exact fixture directory required}
python3 "$project_dir/scripts/validate_fixture_path.py" "$fixture_dir" >/dev/null
if test -L "$fixture_dir"; then
  rm -- "$fixture_dir"
elif test -d "$fixture_dir"; then
  rm -R -- "$fixture_dir"
else
  echo "exact fixture path missing or unsupported" >&2
  exit 65
fi
