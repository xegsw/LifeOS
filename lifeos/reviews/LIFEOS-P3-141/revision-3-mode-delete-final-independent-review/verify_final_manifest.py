#!/usr/bin/env python3
"""Recompute and verify FINAL_MANIFEST.json without modifying it."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW_DIR = Path(__file__).resolve().parent
MANIFEST = REVIEW_DIR / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    expected = {entry["path"]: entry for entry in payload["entries"]}
    actual: dict[str, dict[str, object]] = {}
    for path in sorted(REVIEW_DIR.rglob("*")):
        if path == MANIFEST:
            continue
        relative = path.relative_to(REVIEW_DIR).as_posix()
        if path.is_symlink():
            failures.append({"path": relative, "reason": "symlink"})
        elif path.is_file():
            actual[relative] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    for relative in sorted(set(expected) | set(actual)):
        if relative not in expected:
            failures.append({"path": relative, "reason": "unexpected"})
        elif relative not in actual:
            failures.append({"path": relative, "reason": "missing"})
        elif expected[relative]["bytes"] != actual[relative]["bytes"] or expected[relative]["sha256"] != actual[relative]["sha256"]:
            failures.append({"path": relative, "reason": "digest_or_size_mismatch"})
    result = {
        "schema": "lifeos.p3-141.revision-3.mode-delete.final-manifest-verifier.v1",
        "pass": not failures,
        "expected_entry_count": payload["entry_count"],
        "actual_entry_count": len(actual),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
