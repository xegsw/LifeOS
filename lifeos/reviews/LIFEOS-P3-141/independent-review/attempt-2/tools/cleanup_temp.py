#!/usr/bin/env python3
"""Precisely remove only the literal task-local temporary root."""
from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
LITERAL = "/private/tmp/lifeos-p3-141-controlled-pilot-v1"
TEMP = Path(LITERAL)
OUTPUT = REVIEW / "evidence" / "cleanup_receipt.json"


def main() -> int:
    if str(TEMP) != LITERAL or TEMP.parent != Path("/private/tmp"):
        raise SystemExit("literal temporary-root guard failed")
    receipt: dict[str, object] = {
        "schema": "lifeos-p3-141-attempt-2-exact-cleanup-v1",
        "literal_target": LITERAL,
        "candidate_or_review_source_touched": False,
    }
    try:
        info = os.lstat(TEMP)
    except FileNotFoundError:
        receipt["before"] = {"exists": False}
    else:
        receipt["before"] = {
            "exists": True,
            "mode": stat.S_IFMT(info.st_mode),
            "is_symlink": stat.S_ISLNK(info.st_mode),
            "is_directory": stat.S_ISDIR(info.st_mode),
        }
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            receipt["removed"] = False
            OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 1
        shutil.rmtree(TEMP)
        receipt["removed"] = True
    receipt["after"] = {"exists": os.path.lexists(TEMP)}
    receipt["pass"] = receipt["after"] == {"exists": False}
    OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if receipt["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
