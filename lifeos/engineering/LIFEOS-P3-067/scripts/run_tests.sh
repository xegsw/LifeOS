#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p runtime evidence
python3 tests/test_recovery.py > evidence/test_run.log
# A PID-derived task-local label makes every invocation a clean CLI chain without
# accepting an arbitrary database path or reusing an already-restored record.
chain_run_id="operator-chain-$$"
export LIFEOS_CHAIN_RUN_ID="$chain_run_id"
python3 - <<'PY'
import os
import sys
sys.path.insert(0, 'src')
from recovery import SyntheticRecovery
run_id = os.environ['LIFEOS_CHAIN_RUN_ID']
d = SyntheticRecovery('runtime/' + run_id + '.sqlite')
result = d.capture('operator-1', 'synthetic-cli', 'operator-provided non-sensitive synthetic content')
assert result['status'] == 'saved' and result['saved'] is True
d.close()
PY
LIFEOS_SYNTHETIC_ONLY=1 python3 scripts/recovery_cli.py --run-id "$chain_run_id" --record-id operator-1 --source synthetic-cli --version 1 > evidence/operator_chain_ready_preview.json
LIFEOS_SYNTHETIC_ONLY=1 python3 scripts/recovery_cli.py --run-id "$chain_run_id" --record-id operator-1 --source synthetic-cli --version 1 --confirm CONFIRM > evidence/operator_chain_first_confirm.json
LIFEOS_SYNTHETIC_ONLY=1 python3 scripts/recovery_cli.py --run-id "$chain_run_id" --record-id operator-1 --source synthetic-cli --version 1 --confirm CONFIRM > evidence/operator_chain_idempotent.json
python3 scripts/verify_cli_chain.py | tee -a evidence/test_run.log
python3 scripts/make_manifest.py
