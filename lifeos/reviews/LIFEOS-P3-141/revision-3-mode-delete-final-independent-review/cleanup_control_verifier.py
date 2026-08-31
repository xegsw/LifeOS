#!/usr/bin/env python3
"""Detect a review-cleanup marker-validation bypass before execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    text = Path(args.script).read_text(encoding="utf-8")
    required = {
        "literal-root": 'LITERAL_ROOT = "/private/tmp/lifeos-p3-141-revision-3-independent-review-mode-delete-v1"',
        "lstat": "os.lstat(marker)",
        "non-symlink": "stat.S_ISLNK(marker_stat.st_mode)",
        "0600": "stat.S_IMODE(marker_stat.st_mode) != 0o600",
        "exact-content": "if marker_bytes != MARKER_BYTES:",
        "literal-absence": "not os.path.lexists(root)",
    }
    checks = [{"id": key, "status": "PASS" if needle in text else "FAIL"} for key, needle in required.items()]
    payload = {"schema": "lifeos.p3-141.review-cleanup-control-verifier.v1", "checks": checks, "pass": all(row["status"] == "PASS" for row in checks)}
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
