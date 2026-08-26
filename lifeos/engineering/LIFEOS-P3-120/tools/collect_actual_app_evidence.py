#!/usr/bin/env python3
"""Preserve actual app launch/reopen evidence without any GUI automation."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
SOURCE_LOGS = {
    "actual-app-launch.log": TEMP_ROOT / "app-launch.stdout.log",
    "actual-app-reopen.log": TEMP_ROOT / "app-reopen.stdout.log",
    "actual-app-process.trace": TEMP_ROOT / "actual-app-process.trace",
}
SCREENSHOT = EVIDENCE / "support-images/actual-app-today.png"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with IHDR")
    return struct.unpack(">II", data[16:24])


def check(identifier: str, passed: bool, actual: object) -> dict[str, object]:
    return {"id": identifier, "result": "PASS" if passed else "FAIL", "actual": actual}


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    copied: dict[str, dict[str, object]] = {}
    for target_name, source in SOURCE_LOGS.items():
        target = EVIDENCE / target_name
        if source.is_file():
            shutil.copyfile(source, target)
            copied[target_name] = {"source": str(source), "sha256": sha256(target), "bytes": target.stat().st_size}
        else:
            copied[target_name] = {"source": str(source), "missing": True}
    launch = (EVIDENCE / "actual-app-launch.log").read_text(encoding="utf-8") if (EVIDENCE / "actual-app-launch.log").is_file() else ""
    reopen = (EVIDENCE / "actual-app-reopen.log").read_text(encoding="utf-8") if (EVIDENCE / "actual-app-reopen.log").is_file() else ""
    process_trace = (EVIDENCE / "actual-app-process.trace").read_text(encoding="utf-8") if (EVIDENCE / "actual-app-process.trace").is_file() else ""
    width, height = png_dimensions(SCREENSHOT) if SCREENSHOT.is_file() else (0, 0)
    checks = [
        check("P120-M004", "app-launch pid=" in process_trace and "app-reopen pid=" in process_trace and "runtime_start status=restricted_offline db_scope=synthetic_task_local" in launch and "runtime_start status=restricted_offline db_scope=synthetic_task_local" in reopen and width > 0 and height > 0, {"process_trace": process_trace.splitlines(), "screenshot": {"path": "support-images/actual-app-today.png", "width": width, "height": height, "sha256": sha256(SCREENSHOT) if SCREENSHOT.is_file() else None}},),
        check("P120-M005-actual-app", "ipc_result command=runtime_status status=restricted_offline" in launch and "ipc_result command=runtime_status status=restricted_offline" in reopen, {"launch": launch.splitlines(), "reopen": reopen.splitlines()}),
    ]
    passed = all(entry["result"] == "PASS" for entry in checks)
    payload = {
        "schema": "lifeos-p3-120/actual-app-results-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "method": "direct macOS app process launch and controlled termination; no GUI injection, AppleScript, AX, CDP, WebDriver, browser control, or screenshot-as-function-proof.",
        "copied_logs": copied,
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }
    (EVIDENCE / "actual-app-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "checks": len(checks)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
