#!/usr/bin/env python3
"""Record (without treating as positive evidence) the candidate replay portability result."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
CANDIDATE_TASK = Path(sys.argv[1]).resolve()
OUTPUT = REVIEW / "evidence" / "engineering_replay_path_diagnostic.json"


def main() -> int:
    replay = CANDIDATE_TASK / "tools" / "replay_phase_a.sh"
    completed = subprocess.run(["/bin/sh", str(replay)], text=True, capture_output=True, check=False)
    payload = {
        "schema": "lifeos-p3-141-engineering-replay-diagnostic-v1",
        "candidate_replay_read_only": str(replay),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
        "expected_isolated_portability_failure": completed.returncode != 0 and "fixed_input_inventory.json" in (completed.stdout + completed.stderr),
        "not_used_as_positive_evidence": True,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["expected_isolated_portability_failure"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
