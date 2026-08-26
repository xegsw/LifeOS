#!/usr/bin/env python3
"""Start the same packaged app against the existing P3-120 synthetic DB after manual close."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
SESSION = REWORK / "session.json"
APP_LOG = REWORK / "actual-app.log"


def running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main() -> int:
    if not SESSION.is_file():
        print("missing initial manual session", file=sys.stderr)
        return 1
    session = json.loads(SESSION.read_text(encoding="utf-8"))
    prior_pid = int(session["current_pid"])
    if running(prior_pid):
        print("prior app process is still running; user must close it before reopen", file=sys.stderr)
        return 1
    binary = Path(session["app_binary"])
    if not binary.is_file():
        print("packaged app binary missing", file=sys.stderr)
        return 1
    with APP_LOG.open("a", encoding="utf-8") as log:
        process = subprocess.Popen([str(binary)], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(4)
    if process.poll() is not None:
        print(json.dumps({"result": "FAIL", "reason": "app_exited_after_reopen", "exit_code": process.returncode}))
        return 1
    session["current_pid"] = process.pid
    session["phase"] = "running-reopen"
    session["launches"].append({"id": "launch-2", "pid": process.pid, "started_at_utc": datetime.now(timezone.utc).isoformat()})
    SESSION.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "pid": process.pid}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
