#!/usr/bin/env python3
"""Single-root refusal probes and marker-gated cleanup for re-review-4."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902")
MARKER = ROOT / ".lifeos-p3-143-owner.json"
SENTINEL = ROOT / "review-owned-sentinel.txt"
EXPECTED = {
    "schema": "lifeos.p3-143.independent-review-root.v1",
    "task": "LIFEOS-P3-143",
    "owner": "lifeos-p3-143-independent-review",
    "runId": "finalgui-20260902",
}


def mode(path: Path) -> int:
    return stat.S_IMODE(os.lstat(path).st_mode)


def validate() -> str:
    root_meta = os.lstat(ROOT)
    if not stat.S_ISDIR(root_meta.st_mode) or stat.S_ISLNK(root_meta.st_mode) or mode(ROOT) != 0o700:
        raise RuntimeError("root_type_or_mode_rejected")
    marker_meta = os.lstat(MARKER)
    if not stat.S_ISREG(marker_meta.st_mode) or stat.S_ISLNK(marker_meta.st_mode) or mode(MARKER) != 0o600:
        raise RuntimeError("marker_type_or_mode_rejected")
    if json.loads(MARKER.read_text(encoding="utf-8")) != EXPECTED:
        raise RuntimeError("marker_payload_rejected")
    for parent, dirs, files in os.walk(ROOT, followlinks=False):
        for name in dirs + files:
            if stat.S_ISLNK(os.lstat(Path(parent) / name).st_mode):
                raise RuntimeError("nested_symlink_rejected")
    return "valid"


def refusal_probes() -> dict[str, str]:
    original = MARKER.read_bytes()
    result: dict[str, str] = {}
    MARKER.unlink()
    try:
        validate()
    except (RuntimeError, FileNotFoundError) as error:
        result["missing_marker"] = type(error).__name__
    MARKER.write_bytes(original)
    os.chmod(MARKER, 0o600)
    MARKER.write_text('{"schema":"wrong"}\n', encoding="utf-8")
    os.chmod(MARKER, 0o600)
    try:
        validate()
    except RuntimeError as error:
        result["wrong_marker"] = str(error)
    MARKER.write_bytes(original)
    os.chmod(MARKER, 0o600)
    MARKER.unlink()
    os.symlink(SENTINEL.name, MARKER)
    try:
        validate()
    except RuntimeError as error:
        result["symlink_marker"] = str(error)
    MARKER.unlink()
    MARKER.write_bytes(original)
    os.chmod(MARKER, 0o600)
    if set(result) != {"missing_marker", "wrong_marker", "symlink_marker"}:
        raise RuntimeError("refusal_probe_incomplete")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    if not ROOT.exists() or ROOT.is_symlink():
        raise SystemExit("sole_literal_root_required_and_absent")
    checks = refusal_probes()
    validate()
    document = {
        "schema": "lifeos.p3-143.independent-rereview4.cleanup.v1",
        "literal_root": str(ROOT),
        "profile": "independent-review",
        "run_id": "finalgui-20260902",
        "writers_stopped": True,
        "refusal_probes": checks,
        "cleanup": "not_requested",
    }
    if args.cleanup:
        shutil.rmtree(ROOT)
        if ROOT.exists() or ROOT.is_symlink():
            raise SystemExit("post_cleanup_absence_failed")
        document["cleanup"] = "CLEANED_AND_ABSENT"
    Path(args.output).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, ensure_ascii=False))


if __name__ == "__main__":
    main()
