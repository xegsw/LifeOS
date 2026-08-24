#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$ROOT/evidence" "$ROOT/runtime"
if python3 "$ROOT/tests/test_mvp.py" >"$ROOT/evidence/test_run.log" 2>&1; then
  cat "$ROOT/evidence/test_run.log"
  exit 0
else
  status=$?
  cat "$ROOT/evidence/test_run.log"
  exit "$status"
fi
