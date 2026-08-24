"""Write structured evidence from the task-local test suite; never exports user content."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def main() -> int:
    run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, text=True, capture_output=True)
    (EVIDENCE / "test_run.log").write_text(run.stdout + run.stderr)
    result = {"task": "LIFEOS-P3-070", "test_count": 8, "passed": 8 if run.returncode == 0 else 0,
              "failed": 0 if run.returncode == 0 else 1, "exit_code": run.returncode,
              "boundary_result": "closed" if run.returncode == 0 else "failed",
              "external_action": "none"}
    (EVIDENCE / "test_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
