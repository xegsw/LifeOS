#!/usr/bin/env python3
"""Delete only the Attempt-4 controlled root after exact marker validation."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1")
MARKER = ROOT / ".attempt-4-marker.json"
REPORT = Path(__file__).resolve().parents[1] / "evidence/matrices/cleanup_and_retention.json"
EXPECTED = {
    "task_id": "LIFEOS-P3-141",
    "attempt": 4,
    "purpose": "controlled-pilot-v1",
    "created_by": "independent-review",
}


def main() -> None:
    if not ROOT.is_dir() or ROOT.is_symlink():
        raise SystemExit("refusing cleanup: exact controlled root is not a direct directory")
    if MARKER.is_symlink() or not MARKER.is_file():
        raise SystemExit("refusing cleanup: exact marker is absent or unsafe")
    if json.loads(MARKER.read_text(encoding="utf-8")) != EXPECTED:
        raise SystemExit("refusing cleanup: marker content mismatch")
    shutil.rmtree(ROOT)
    report = {
        "task_id": "LIFEOS-P3-141",
        "attempt": 4,
        "target": str(ROOT),
        "marker_validated": True,
        "operation": "shutil.rmtree on exact marker-gated target only",
        "root_exists_after": ROOT.exists(),
        "retained": "review-root evidence only; no temporary databases, binaries, copies or screenshots retained under the temporary root",
    }
    if report["root_exists_after"]:
        raise SystemExit("cleanup failed: controlled root remains")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
