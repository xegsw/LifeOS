#!/usr/bin/env python3
"""Fail-closed verifier for P3-115 dynamic raw evidence and closure rows."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
MATRIX_IDS = [f"ABF-M-{n:03d}" for n in range(1, 17)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def abort(reason):
    print(json.dumps({"status": "FAIL", "reason": reason}, ensure_ascii=False))
    raise SystemExit(1)

def validate(base, allow_pre_finalization=False):
    results_path = base / "results" / "matrix_results.json"
    closure_path = base / "dynamic_closure.json"
    fixed_path = base / "fixed_inputs.json"
    for path in [results_path, closure_path, fixed_path]:
        if not path.is_file():
            abort(f"missing raw evidence: {path.relative_to(base)}")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    result_ids = {row.get("id") for row in results.get("matrix", []) if row.get("status") == "PASS"}
    provisional_ids = {"ABF-M-015", "ABF-M-016"} if allow_pre_finalization else set()
    missing_matrix = [item for item in MATRIX_IDS if item not in result_ids and item not in provisional_ids]
    if missing_matrix:
        abort(f"matrix PASS rows missing: {missing_matrix}")
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    rows = closure.get("rows")
    if not isinstance(rows, list) or not rows:
        abort("dynamic closure has no rows")
    for row in rows:
        if row.get("matrix_id") in provisional_ids:
            continue
        if row.get("status") != "PASS":
            abort(f"closure row not PASS: {row.get('id')}")
        path = base / row.get("evidence_path", "")
        if not path.is_file():
            abort(f"closure Evidence missing: {row.get('id')}")
        if sha(path) != row.get("sha256"):
            abort(f"closure Evidence hash mismatch: {row.get('id')}")
        if not row.get("operation") or not row.get("result_id"):
            abort(f"closure metadata incomplete: {row.get('id')}")
        screenshot = row.get("screenshot_path")
        if row.get("dynamic"):
            if not screenshot:
                abort(f"dynamic closure screenshot missing: {row.get('id')}")
            screenshot_path = base / screenshot
            if not screenshot_path.is_file() or sha(screenshot_path) != row.get("screenshot_sha256"):
                abort(f"dynamic closure screenshot hash mismatch: {row.get('id')}")
    fixed = json.loads(fixed_path.read_text(encoding="utf-8"))
    for item in fixed.get("inputs", []):
        path = ROOT.parents[2] / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            abort(f"fixed input changed: {item['path']}")
    manifest = base / "MANIFEST.md"
    if not manifest.is_file():
        abort("non-self manifest missing")
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"\| `(.+)` \| (\d+) \| `([0-9a-f]{64})` \|", line)
        if match:
            entries[match.group(1)] = (int(match.group(2)), match.group(3))
    if "evidence/MANIFEST.md" in entries:
        abort("manifest must be non-self")
    expected = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.resolve() != manifest.resolve() and "__pycache__" not in path.parts:
            expected.append(path)
    for path in expected:
        rel = str(path.relative_to(ROOT))
        actual = entries.get(rel)
        if actual != (path.stat().st_size, sha(path)):
            abort(f"manifest mismatch: {rel}")
    return {"status": "PASS", "matrix_rows": len(MATRIX_IDS), "closure_rows": len(rows), "manifest_entries": len(entries)}

parser = argparse.ArgumentParser()
parser.add_argument("--base", default=str(EVIDENCE))
parser.add_argument("--allow-pre-finalization", action="store_true", help="only for the mutation check before cleanup")
args = parser.parse_args()
print(json.dumps(validate(pathlib.Path(args.base), args.allow_pre_finalization), ensure_ascii=False))
