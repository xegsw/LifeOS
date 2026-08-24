#!/bin/sh
set -eu

TASK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LOG_PATH="$TASK_DIR/evidence/test_run.log"

mkdir -p "$TASK_DIR/evidence"

if python3 "$TASK_DIR/scripts/run_validation.py" >"$LOG_PATH" 2>&1; then
  STATUS=0
else
  STATUS=$?
fi

cat "$LOG_PATH"
exit "$STATUS"
