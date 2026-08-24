#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$ROOT/tests/test_permissions.py" | tee "$ROOT/evidence/test_run.log"
