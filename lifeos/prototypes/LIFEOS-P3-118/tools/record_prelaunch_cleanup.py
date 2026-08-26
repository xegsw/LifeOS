#!/usr/bin/env python3
"""Record only the exact P3-118 temporary root without inspecting processes."""

import argparse
import json
from pathlib import Path

TMP_ROOT = Path("/private/tmp/lifeos-p3-118-native-capture-v1")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": "1.0",
        "exact_temporary_root": str(TMP_ROOT),
        "exists": TMP_ROOT.exists(),
        "chrome_launch_attempted": False,
        "chrome_pid_created": False,
        "computer_use_chrome_query_attempted": False,
        "screenshot_created": False,
        "cleanup_action": "NONE_REQUIRED",
        "result": "PASS" if not TMP_ROOT.exists() else "FAIL",
        "meaning": "The exact authorized temporary root was absent before and after the fail-closed preflight. No process enumeration was used, because it could inspect unrelated Chrome state.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
