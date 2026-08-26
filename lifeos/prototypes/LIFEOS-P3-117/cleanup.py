#!/usr/bin/env python3
"""Record pending cleanup or exactly remove only the P3-117 temporary root."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/tmp/lifeos-p3-117-native-capture-v1")
OUTPUT = TASK_ROOT / "evidence/cleanup.json"


def write(payload: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    if TEMP_ROOT != Path("/private/tmp/lifeos-p3-117-native-capture-v1"):
        raise RuntimeError("temporary root constant changed; refusing cleanup")
    before = {
        "root_exists": TEMP_ROOT.exists(),
        "candidate_exists": (TEMP_ROOT / "candidate").exists(),
        "profile_exists": (TEMP_ROOT / "chrome-profile").exists(),
    }
    if not args.final:
        write({
            "task": "LIFEOS-P3-117",
            "status": "pending",
            "temporary_root": str(TEMP_ROOT),
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "before": before,
            "statement": "No deletion has occurred; final verification must not treat this as cleanup complete.",
        })
        print(json.dumps({"result": "PASS", "status": "pending"}, ensure_ascii=False))
        return 0
    if not before["root_exists"]:
        raise RuntimeError("temporary root is already absent; cannot prove this runner performed exact cleanup")
    shutil.rmtree(TEMP_ROOT)
    after = {
        "root_exists": TEMP_ROOT.exists(),
        "candidate_exists": (TEMP_ROOT / "candidate").exists(),
        "profile_exists": (TEMP_ROOT / "chrome-profile").exists(),
    }
    if any(after.values()):
        raise RuntimeError("exact cleanup failed")
    write({
        "task": "LIFEOS-P3-117",
        "status": "complete",
        "temporary_root": str(TEMP_ROOT),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "after": after,
        "statement": "Only the Frozen exact P3-117 temporary root was deleted.",
    })
    print(json.dumps({"result": "PASS", "status": "complete"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
