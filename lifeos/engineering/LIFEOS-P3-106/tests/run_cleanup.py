#!/usr/bin/env python3
"""Ledger-driven exact cleanup for this P3-106 execution only."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CLEANER = ROOT / "scripts/cleanup_evidence_fixture.sh"
PATHS = [
    "/private/tmp/lifeos-p3-104-p3-106-app-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-dangling-final-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-dangling-journal-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-dangling-wal-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-dangling-shm-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-path-main-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-path-target-20260823",
    "/private/tmp/lifeos-p3-104-p3-106-tamper-main-20260823",
]
LEGACY = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")


def metadata(path: Path) -> dict[str, object]:
    try:
        value = path.lstat()
        return {
            "exists": True,
            "type": stat.filemode(value.st_mode)[0],
            "size": value.st_size,
            "mtime_ns": value.st_mtime_ns,
            "ctime_ns": value.st_ctime_ns,
        }
    except FileNotFoundError:
        return {"exists": False}


def main() -> int:
    before_legacy = metadata(LEGACY)
    before = [{"path": value, "metadata": metadata(Path(value))} for value in PATHS]
    rows = []
    for value in PATHS:
        path = Path(value)
        if metadata(path)["exists"]:
            completed = subprocess.run(
                [str(CLEANER), value],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            rows.append({
                "path": value,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            })
        else:
            rows.append({"path": value, "status": "PASS", "returncode": 0, "detail": "already absent"})
    after = [{"path": value, "metadata": metadata(Path(value))} for value in PATHS]
    after_legacy = metadata(LEGACY)
    residuals = [row["path"] for row in after if row["metadata"]["exists"]]
    payload = {
        "task": "LIFEOS-P3-106",
        "selection": "literal in-source exact ledger; no glob, prefix, find, or environment expansion",
        "before": before,
        "operations": rows,
        "after": after,
        "residuals": residuals,
        "legacy": {
            "path": str(LEGACY),
            "before": before_legacy,
            "after": after_legacy,
            "unchanged": before_legacy == after_legacy,
        },
        "status": "PASS" if not residuals and before_legacy == after_legacy and all(row["status"] == "PASS" for row in rows) else "FAIL",
    }
    (EVIDENCE / "cleanup_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "residuals": residuals, "legacy_unchanged": payload["legacy"]["unchanged"]}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
