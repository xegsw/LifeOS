#!/usr/bin/env python3
"""Narrow actual-app launcher/snapshot helper for P3-110's authorized fixtures."""
from __future__ import annotations

import hashlib
import json
import os
import plistlib
import signal
import sqlite3
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
WORK = Path("/private/tmp/lifeos-p3-110-review-work-v1")
BINARY = WORK / "target/debug/lifeos-p3-104"
WRAPPER = WORK / "P3-110-LifeOS.app"
ALLOWED = {
    f"lifeos-p3-104-p3-110-review-{name}-v1"
    for name in ["nominal", "reopen", "failure", "dangling-final", "dangling-journal", "dangling-wal", "dangling-shm", "path", "link", "hardlink", "tamper", "a11y", "narrow"]
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def emit(name: str, value: object) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixture(name: str) -> Path:
    if name not in ALLOWED:
        raise SystemExit(f"fixture is not ABF-authorized: {name}")
    return Path("/private/tmp") / name


def snapshot(name: str, label: str) -> int:
    root = fixture(name)
    db = root / "capture.sqlite"
    value: dict[str, object] = {"fixture": str(root), "label": label, "captured_at_utc": now(), "root_exists": os.path.lexists(root), "db_exists": os.path.lexists(db)}
    sentinel = root / "sentinel.txt"
    value["sentinel_sha256"] = hashlib.sha256(sentinel.read_bytes()).hexdigest() if sentinel.is_file() else None
    if db.is_file() and not db.is_symlink():
        try:
            uri = f"file:{db}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            value["quick_check"] = conn.execute("PRAGMA quick_check").fetchone()[0]
            value["record_count"] = conn.execute("SELECT count(*) FROM captures").fetchone()[0]
            value["audit_count"] = conn.execute("SELECT count(*) FROM audit").fetchone()[0]
            conn.close()
        except sqlite3.Error as error:
            value["sqlite_error"] = str(error)
    emit(f"snapshot-{label}.json", value)
    return 0


def create_sentinel(name: str) -> int:
    root = fixture(name)
    root.mkdir(exist_ok=True)
    path = root / "sentinel.txt"
    if path.exists():
        raise SystemExit("sentinel already exists")
    path.write_text("P3-110 NOMINAL SENTINEL\n", encoding="utf-8")
    emit("nominal-sentinel.json", {"fixture": str(root), "sentinel": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "created_at_utc": now()})
    return 0


def wrap() -> int:
    if not BINARY.is_file():
        raise SystemExit("debug binary missing")
    executable = WRAPPER / "Contents/MacOS/lifeos-p3-104"
    plist = WRAPPER / "Contents/Info.plist"
    executable.parent.mkdir(parents=True, exist_ok=True)
    if executable.exists() or plist.exists():
        raise SystemExit("wrapper path already exists")
    shutil.copy2(BINARY, executable)
    with plist.open("wb") as handle:
        plistlib.dump({
            "CFBundleDevelopmentRegion": "en",
            "CFBundleDisplayName": "LifeOS P3-110 Review",
            "CFBundleExecutable": "lifeos-p3-104",
            "CFBundleIdentifier": "local.lifeos.p3-110.review",
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleName": "LifeOS P3-110 Review",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "1",
        }, handle)
    source_hash = hashlib.sha256(BINARY.read_bytes()).hexdigest()
    wrapper_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
    emit("actual-app-wrapper.json", {"wrapper": str(WRAPPER), "source_binary": str(BINARY), "source_sha256": source_hash, "wrapper_binary_sha256": wrapper_hash, "binary_unchanged": source_hash == wrapper_hash})
    return 0


def start(name: str, log_name: str) -> int:
    root = fixture(name)
    if not BINARY.is_file():
        raise SystemExit("debug binary missing")
    env = os.environ.copy()
    env["LIFEOS_P3_104_DB_PATH"] = str(root / "capture.sqlite")
    log = EVIDENCE / log_name
    handle = log.open("w", encoding="utf-8")
    handle.write(f"started_at_utc={now()}\nfixture={root}\n")
    executable = WRAPPER / "Contents/MacOS/lifeos-p3-104" if (WRAPPER / "Contents/MacOS/lifeos-p3-104").is_file() else BINARY
    process = subprocess.Popen([str(executable)], cwd=WORK, env=env, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
    emit("actual-app-process.json", {"pid": process.pid, "fixture": str(root), "log": str(log.relative_to(ROOT)), "started_at_utc": now(), "binary": str(BINARY), "launched_executable": str(executable), "wrapper": str(WRAPPER) if executable != BINARY else None})
    # Let an immediate path validation rejection settle before Computer Use inspects the app.
    time.sleep(1)
    return process.poll() or 0


def stop() -> int:
    record = json.loads((EVIDENCE / "actual-app-process.json").read_text(encoding="utf-8"))
    pid = int(record["pid"])
    try:
        os.killpg(pid, signal.SIGTERM)
        stopped = True
    except ProcessLookupError:
        stopped = False
    emit("actual-app-stop.json", {"pid": pid, "stop_requested_at_utc": now(), "signal": "SIGTERM", "process_group_found": stopped})
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: app_control.py start <fixture> <log>|snapshot <fixture> <label>|sentinel <fixture>|stop")
    action = sys.argv[1]
    if action == "start" and len(sys.argv) == 4:
        raise SystemExit(start(sys.argv[2], sys.argv[3]))
    if action == "snapshot" and len(sys.argv) == 4:
        raise SystemExit(snapshot(sys.argv[2], sys.argv[3]))
    if action == "sentinel" and len(sys.argv) == 3:
        raise SystemExit(create_sentinel(sys.argv[2]))
    if action == "wrap" and len(sys.argv) == 2:
        raise SystemExit(wrap())
    if action == "stop" and len(sys.argv) == 2:
        raise SystemExit(stop())
    raise SystemExit("invalid arguments")
