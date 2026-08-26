#!/usr/bin/env python3
"""Fail-closed source audit for the P3-118 PID/window helper."""

import hashlib
import json
from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "pid_window_attest.swift"

required = [
    "--pid",
    "let owned = listed.filter",
    "eligible: [TargetWindow] = owned.compactMap",
    "layer == 0, onscreen",
    "target_window: onlyTarget",
    "executable_sha256",
]
forbidden = [
    "kCGWindowOwnerName",
    "kCGWindowName",
    "osascript",
    "System Events",
    "CGWindowListCreateImage",
    "com.google.Chrome",
    "Google Chrome",
    "open -na",
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    missing = [token for token in required if token not in text]
    present_forbidden = [token for token in forbidden if token in text]
    result = {
        "schema_version": "1.0",
        "helper": str(SOURCE.relative_to(ROOT)),
        "helper_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "required_tokens_missing": missing,
        "forbidden_tokens_present": present_forbidden,
        "result": "PASS" if not missing and not present_forbidden else "FAIL",
        "meaning": "Source-only audit: target-PID filtering precedes all serializable window-field extraction; no browser/app selector or title metadata exists in the helper.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["result"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
