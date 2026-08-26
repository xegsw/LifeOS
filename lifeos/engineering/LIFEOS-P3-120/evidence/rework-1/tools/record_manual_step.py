#!/usr/bin/env python3
"""Record one user-manual packaged-app step with DB, stdout, and auxiliary window evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
DB_PATH = TEMP_ROOT / "capture.sqlite"
SESSION = REWORK / "session.json"
APP_LOG = REWORK / "actual-app.log"
SCREENSHOTS = REWORK / "screenshots"
LOGS = REWORK / "logs"
STEPS = REWORK / "steps"

ORDER = [
    "today-empty", "me", "contexts", "context-detail", "memory", "memory-detail", "global-ai", "ai-workspace", "settings",
    "capture-one", "repeat-one", "capture-two", "refresh", "closed", "reopen-today",
]
EXPECTED = {
    "today-empty": {"captures": 0, "audit": 0, "running": True, "screenshot": True, "minimum_log": ["runtime_start status=restricted_offline", "ipc_result command=runtime_status status=restricted_offline"]},
    "me": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "contexts": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "context-detail": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "memory": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "memory-detail": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "global-ai": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "ai-workspace": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "settings": {"captures": 0, "audit": 0, "running": True, "screenshot": True},
    "capture-one": {"captures": 1, "audit": 1, "running": True, "screenshot": True, "minimum_log": ["ipc_result command=capture_record status=saved record_count=1 audit_event_count=1 repeated=false", "ipc_result command=get_today status=loaded record_count=1 audit_event_count=1"]},
    "repeat-one": {"captures": 1, "audit": 2, "running": True, "screenshot": True, "minimum_log": ["ipc_result command=capture_record status=idempotent_repeat record_count=1 audit_event_count=2 repeated=true", "ipc_result command=get_today status=loaded record_count=1 audit_event_count=2"]},
    "capture-two": {"captures": 2, "audit": 3, "running": True, "screenshot": True, "minimum_log": ["ipc_result command=capture_record status=saved record_count=2 audit_event_count=3 repeated=false", "ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"]},
    "refresh": {"captures": 2, "audit": 3, "running": True, "screenshot": True, "minimum_log": ["ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"]},
    "closed": {"captures": 2, "audit": 3, "running": False, "screenshot": False},
    "reopen-today": {"captures": 2, "audit": 3, "running": True, "screenshot": True, "minimum_log": ["runtime_start status=restricted_offline", "ipc_result command=runtime_status status=restricted_offline", "ipc_result command=get_today status=loaded record_count=2 audit_event_count=3"]},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def snapshot_db() -> dict[str, object]:
    if not DB_PATH.exists() and not DB_PATH.is_symlink():
        return {"exists": False, "captures": [], "audit": [], "sha256": None}
    metadata = DB_PATH.lstat()
    if DB_PATH.is_symlink() or not DB_PATH.is_file():
        return {"exists": True, "type": "invalid", "sha256": None, "captures": [], "audit": []}
    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        captures = [dict(zip(["id", "content", "created_at_ms", "source", "idem_key"], row)) for row in connection.execute("SELECT id, content, created_at_ms, source, idem_key FROM captures ORDER BY created_at_ms, id")]
        audit = [dict(zip(["id", "event", "capture_id", "created_at_ms", "detail"], row)) for row in connection.execute("SELECT id, event, capture_id, created_at_ms, detail FROM audit ORDER BY id")]
    finally:
        connection.close()
    return {"exists": True, "type": "regular", "bytes": metadata.st_size, "sha256": sha256(DB_PATH), "quick_check": quick_check, "user_version": version, "captures": captures, "audit": audit}


def previous_step(step: str) -> str | None:
    index = ORDER.index(step)
    return ORDER[index - 1] if index else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=ORDER)
    parser.add_argument("--attestation", required=True, help="User's concise confirmation of the manual visible action just completed.")
    parser.add_argument("--capture-delay-seconds", type=int, default=0, choices=range(0, 16), metavar="0..15", help="Visible waiting period for the user to bring the already-open target app to the foreground before screenshot capture.")
    arguments = parser.parse_args()
    step = arguments.step
    prior = previous_step(step)
    if prior and not (STEPS / f"{prior}.json").is_file():
        print(f"prior step missing: {prior}", file=sys.stderr)
        return 1
    if (STEPS / f"{step}.json").exists():
        print(f"step already recorded: {step}", file=sys.stderr)
        return 1
    if not SESSION.is_file() or not APP_LOG.is_file():
        print("manual session or app log is missing", file=sys.stderr)
        return 1
    session = json.loads(SESSION.read_text(encoding="utf-8"))
    expected = EXPECTED[step]
    app_running = running(int(session["current_pid"]))
    if app_running != expected["running"]:
        print(f"unexpected process state for {step}: {app_running}", file=sys.stderr)
        return 1
    db = snapshot_db()
    capture_count = len(db.get("captures", []))
    audit_count = len(db.get("audit", []))
    if capture_count != expected["captures"] or audit_count != expected["audit"]:
        print(json.dumps({"error": "unexpected_db_state", "step": step, "captures": capture_count, "audit": audit_count}), file=sys.stderr)
        return 1
    LOGS.mkdir(parents=True, exist_ok=True)
    STEPS.mkdir(parents=True, exist_ok=True)
    log_snapshot = LOGS / f"{step}.app.log"
    log_snapshot.write_bytes(APP_LOG.read_bytes())
    log_text = log_snapshot.read_text(encoding="utf-8")
    missing_log = [value for value in expected.get("minimum_log", []) if value not in log_text]
    screenshot = None
    if expected["screenshot"]:
        SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        screenshot = SCREENSHOTS / f"{step}.png"
        if arguments.capture_delay_seconds:
            time.sleep(arguments.capture_delay_seconds)
        command = ["/usr/sbin/screencapture", "-x", "-R", "225,32,1250,900", str(screenshot)]
        captured = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if captured.returncode != 0 or not screenshot.is_file():
            print(json.dumps({"error": "screenshot_failed", "stdout": captured.stdout, "stderr": captured.stderr}), file=sys.stderr)
            return 1
    payload = {
        "schema": "lifeos-p3-120/rework-1-manual-step-v1",
        "step": step,
        "structured_result_id": f"R1-{step}",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "operator": "actual-app-start" if step == "today-empty" else "user-manual",
        "attestation": arguments.attestation,
        "capture_delay_seconds": arguments.capture_delay_seconds,
        "automation_excluded": ["Computer Use", "AppleScript", "AX", "CDP", "HTTP", "WebDriver", "browser control"],
        "app": {"pid": session["current_pid"], "running": app_running, "launch_count": len(session["launches"])},
        "db": db,
        "log_snapshot": {"path": log_snapshot.relative_to(REWORK).as_posix(), "sha256": sha256(log_snapshot), "missing_expected_lines": missing_log},
        "screenshot": None if screenshot is None else {"path": screenshot.relative_to(REWORK).as_posix(), "sha256": sha256(screenshot), "bytes": screenshot.stat().st_size},
        "result": "PASS" if not missing_log else "FAIL",
    }
    output = STEPS / f"{step}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "step": step, "db_captures": capture_count, "db_audit": audit_count, "screenshot": screenshot is not None}))
    return 0 if payload["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
