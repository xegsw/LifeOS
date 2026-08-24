#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture_dir=${1:?existing exact fixture directory required}
python3 "$project_dir/scripts/validate_fixture_path.py" "$fixture_dir" >/dev/null
case "$(basename "$fixture_dir")" in lifeos-p3-104-p3-106-app-*|lifeos-p3-104-p3-106-replay-*|lifeos-p3-104-p3-106-a11y-*|lifeos-p3-104-p3-106-visual-*) ;; *) exit 64 ;; esac
test -d "$fixture_dir" && test ! -L "$fixture_dir" || { echo "fixture missing or linked" >&2; exit 65; }
LIFEOS_P3_104_DB_PATH="$fixture_dir/capture.sqlite" exec "$project_dir/target/debug/lifeos-p3-104"
