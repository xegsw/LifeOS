#!/usr/bin/env python3
"""Remove only the exact P3-120 disposable temporary root and prove its absence."""

from __future__ import annotations

import json
import os
import shutil
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")


def main() -> int:
    if str(TEMP_ROOT) != "/private/tmp/lifeos-p3-120-runtime-mvp-v1":
        print("unexpected cleanup target", file=sys.stderr)
        return 1
    existed_before = TEMP_ROOT.exists() or TEMP_ROOT.is_symlink()
    pre_cleanup_file_count = None
    if existed_before:
        metadata = os.lstat(TEMP_ROOT)
        if not TEMP_ROOT.is_dir() or TEMP_ROOT.is_symlink() or not stat.S_ISDIR(metadata.st_mode):
            print("cleanup target is not a real directory", file=sys.stderr)
            return 1
        pre_cleanup_file_count = sum(1 for path in TEMP_ROOT.rglob("*") if path.is_file() or path.is_symlink())
        shutil.rmtree(TEMP_ROOT)
    absent_after = not TEMP_ROOT.exists() and not TEMP_ROOT.is_symlink()
    payload = {
        "schema": "lifeos-p3-120/cleanup-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "exact_target": str(TEMP_ROOT),
        "target_existed_before": existed_before,
        "pre_cleanup_file_count": pre_cleanup_file_count,
        "target_absent_after": absent_after,
        "result": "PASS" if absent_after else "FAIL",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "cleanup.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "target_absent_after": absent_after}))
    return 0 if absent_after else 1


if __name__ == "__main__":
    sys.exit(main())
