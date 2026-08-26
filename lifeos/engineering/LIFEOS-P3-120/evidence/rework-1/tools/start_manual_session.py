#!/usr/bin/env python3
"""Build and start the packaged P3-120 app for user-manual Evidence capture."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
P3_ROOT = SCRIPT.parents[3]
CANDIDATE = P3_ROOT / "candidate"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
SESSION = REWORK / "session.json"
APP_LOG = REWORK / "actual-app.log"
BUNDLE = TEMP_ROOT / "cargo-target/release/bundle/macos/LifeOS P3-120 Synthetic Runtime MVP.app"
APP_BINARY = BUNDLE / "Contents/MacOS/lifeos-p3-120"


def main() -> int:
    if TEMP_ROOT.exists() or TEMP_ROOT.is_symlink():
        print("temporary root must be absent before a clean rework session", file=sys.stderr)
        return 1
    if not CARGO.is_file():
        print("pinned Cargo executable unavailable", file=sys.stderr)
        return 1
    REWORK.mkdir(parents=True, exist_ok=True)
    (TEMP_ROOT / "tmp").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"CARGO_NET_OFFLINE": "true", "CARGO_TARGET_DIR": str(TEMP_ROOT / "cargo-target"), "TMPDIR": str(TEMP_ROOT / "tmp")})
    build_command = [str(CARGO), "tauri", "build", "--bundles", "app", "--config", "tauri.conf.json", "--", "--locked", "--offline"]
    build = subprocess.run(build_command, cwd=CANDIDATE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    (REWORK / "build-bundle.log").write_text(build.stdout, encoding="utf-8")
    if build.returncode != 0 or not APP_BINARY.is_file():
        print(json.dumps({"result": "FAIL", "build_exit": build.returncode, "app_binary": str(APP_BINARY)}))
        return 1
    with APP_LOG.open("w", encoding="utf-8") as log:
        process = subprocess.Popen([str(APP_BINARY)], cwd=CANDIDATE, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(4)
    if process.poll() is not None:
        print(json.dumps({"result": "FAIL", "reason": "app_exited_before_manual_session", "exit_code": process.returncode}))
        return 1
    payload = {
        "schema": "lifeos-p3-120/rework-1-manual-session-v1",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "manual_only": True,
        "prohibited_automation": ["P3-119 helper", "Computer Use", "AppleScript", "AX", "CDP", "HTTP", "WebDriver", "browser control"],
        "app_binary": str(APP_BINARY),
        "runtime_root": str(TEMP_ROOT),
        "db_path": str(TEMP_ROOT / "capture.sqlite"),
        "log_path": "actual-app.log",
        "current_pid": process.pid,
        "launches": [{"id": "launch-1", "pid": process.pid, "started_at_utc": datetime.now(UTC).isoformat()}],
        "phase": "running-initial",
    }
    SESSION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "pid": process.pid, "app_binary": str(APP_BINARY)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
