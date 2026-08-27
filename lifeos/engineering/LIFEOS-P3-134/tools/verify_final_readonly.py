#!/usr/bin/env python3
"""Default read-only verifier for final-closure Manifest and AC-01..AC-16."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

TASK_ROOT = Path("/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-134")
FINAL_ROOT = TASK_ROOT / "evidence/final-closure"
MANIFEST = FINAL_ROOT / "FINAL_MANIFEST.json"
MATRIX = FINAL_ROOT / "matrix/ac-matrix.json"
REQUIRED = (
    "evidence/final-closure/fixed-inputs.json",
    "evidence/final-closure/source-lineage.json",
    "evidence/final-closure/matrix/ac03-dom-class-landmark-matrix.json",
    "evidence/final-closure/matrix/ac04-actual-tauri-three-viewport.json",
    "evidence/final-closure/matrix/ac05-visual-comparison.json",
    "evidence/final-closure/matrix/ac10-today-focus-and-stale-evidence.json",
    "evidence/final-closure/matrix/ac14-prewrite-failure-matrix.json",
    "evidence/final-closure/matrix/ac-matrix.json",
    "evidence/final-closure/cleanup.json",
)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    data = json.loads(MANIFEST.read_text())
    assets = data.get("assets", [])
    errors = []
    listed = set()
    for item in assets:
        relative = item.get("path", "")
        path = TASK_ROOT / relative
        listed.add(relative)
        try:
            mode = os.lstat(path).st_mode
            if not stat.S_ISREG(mode):
                errors.append({"path": relative, "error": "not_regular"})
                continue
            if path.stat().st_size != item.get("bytes"):
                errors.append({"path": relative, "error": "bytes"})
            if sha(path) != item.get("sha256"):
                errors.append({"path": relative, "error": "sha256"})
        except FileNotFoundError:
            errors.append({"path": relative, "error": "missing"})
    actual = {str(p.relative_to(TASK_ROOT)) for p in TASK_ROOT.rglob("*") if p.is_file()}
    scope = {p for p in actual if p.startswith(("candidate/", "tools/", "evidence/final-closure/")) and p != "evidence/final-closure/FINAL_MANIFEST.json"}
    missing_from_manifest = sorted(scope - listed)
    extras = sorted(listed - scope)
    if "evidence/final-closure/FINAL_MANIFEST.json" in listed:
        errors.append({"path": "evidence/final-closure/FINAL_MANIFEST.json", "error": "self_reference"})
    required_missing = [path for path in REQUIRED if not (TASK_ROOT / path).is_file()]
    matrix_error = None
    try:
        matrix = json.loads(MATRIX.read_text())
        results = matrix.get("results", {})
        counts = matrix.get("counts", {})
        expected_ids = {f"AC-{index:02d}" for index in range(1, 17)}
        if set(results) != expected_ids or not all(results.values()):
            matrix_error = "ac_not_all_pass"
        elif any(counts.get(key) != 0 for key in ("P0", "P1", "Unknown", "Not Implemented")):
            matrix_error = "blocking_count_nonzero"
        elif not matrix.get("overall_pass"):
            matrix_error = "overall_not_pass"
    except Exception as exc:
        matrix_error = f"matrix_unreadable:{type(exc).__name__}"
    result = {"task": "LIFEOS-P3-134", "readonly": True, "manifest": str(MANIFEST), "asset_count": len(assets), "errors": errors, "missing_from_manifest": missing_from_manifest, "extras": extras, "required_missing": required_missing, "matrix_error": matrix_error, "passed": not errors and not missing_from_manifest and not extras and not required_missing and matrix_error is None}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
