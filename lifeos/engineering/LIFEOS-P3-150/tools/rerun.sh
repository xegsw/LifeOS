#!/bin/zsh
set -eu
TASK_DIR="${0:A:h:h}"
ROOT=/private/tmp/lifeos-p3-150-health-view-v1
/usr/bin/python3 - "$ROOT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);assert json.loads((p/'.owner.json').read_text())['task']=='P3-150'
assert p.stat().st_mode&0o777==0o700
PY
LIFEOS_P3_150_MODE=synthetic CARGO_TARGET_DIR="$ROOT/target-synthetic" TMPDIR="$ROOT/tmp" /Users/xxe/.cargo/bin/cargo test --locked --offline --manifest-path "$TASK_DIR/candidate/Cargo.toml"
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node "$TASK_DIR/tools/ui_tests.mjs"
/usr/bin/python3 "$TASK_DIR/tools/verify_history.py"
