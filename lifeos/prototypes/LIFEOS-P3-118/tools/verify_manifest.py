#!/usr/bin/env python3
"""Verify every payload hash listed in the P3-118 non-self manifest."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| (\d+) \|$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for line in args.manifest.read_text(encoding="utf-8").splitlines():
        matched = ROW.match(line)
        if matched:
            relative, expected, expected_size = matched.groups()
            path = ROOT / relative
            rows.append({
                "path": relative,
                "exists": path.is_file(),
                "sha256_matches": path.is_file() and digest(path) == expected,
                "size_matches": path.is_file() and path.stat().st_size == int(expected_size),
            })
    checks = {
        "manifest_is_nonself": "| `MANIFEST.md` |" not in args.manifest.read_text(encoding="utf-8"),
        "payload_count_positive": len(rows) > 0,
        "all_listed_payloads_match": all(all(value for key, value in row.items() if key != "path") for row in rows),
    }
    result = {"schema_version": "1.0", "checks": checks, "payload_count": len(rows), "result": "PASS" if all(checks.values()) else "FAIL"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
