#!/usr/bin/env python3
"""Remove only the exact P3-120 task-local temporary root after final manual close."""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
EXPECTED = "/private/tmp/lifeos-p3-120-runtime-mvp-v1"
OUTPUT = REWORK / "cleanup.json"


def pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main() -> int:
    session_path = REWORK / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8")) if session_path.is_file() else {}
    pid = session.get("current_pid")
    errors: list[str] = []
    if str(TEMP_ROOT) != EXPECTED or TEMP_ROOT.is_symlink():
        errors.append("temporary root is not the exact allowed non-symlink path")
    if not isinstance(pid, int) or pid_running(pid):
        errors.append("reopened app is still running; user must close it before cleanup")
    if TEMP_ROOT.exists() and not errors:
        shutil.rmtree(TEMP_ROOT)
    removed = not TEMP_ROOT.exists() and not TEMP_ROOT.is_symlink()
    if not removed and not errors:
        errors.append("temporary root remains after cleanup")
    payload = {
        "schema": "lifeos-p3-120/rework-1-cleanup-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": EXPECTED,
        "operator": "exact-path cleanup after user manual close",
        "app_pid": pid,
        "removed": removed,
        "errors": errors,
        "result": "PASS" if not errors and removed else "NOT PASS",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "removed": removed, "error_count": len(errors)}))
    return 0 if payload["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
