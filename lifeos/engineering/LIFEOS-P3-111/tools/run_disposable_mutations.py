#!/usr/bin/env python3
"""Make six real disposable evidence mutations and require the same verifier to fail."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "mutations"
VERIFIER = ROOT / "tools" / "semantic_verifier.py"

def mutate(copy_root: Path, name: str) -> None:
    if name == "missing_file": (copy_root / "raw/geometry.json").unlink()
    elif name == "hash_changed": (copy_root / "raw/static-results.json").write_bytes((copy_root / "raw/static-results.json").read_bytes() + b" ")
    elif name == "cleanup_residue":
        path = copy_root / "raw/cleanup.json"; value = json.loads(path.read_text()); value["fixture_residue_count"] = 1; path.write_text(json.dumps(value) + "\n")
    elif name == "negative_exit_zero":
        path = copy_root / "raw/negative-results.json"; value = json.loads(path.read_text()); value["unknown_ipc_exit"] = 0; path.write_text(json.dumps(value) + "\n")
    elif name == "db_count_wrong":
        path = copy_root / "raw/fixed-lifecycle.json"; value = json.loads(path.read_text()); value["passed_tests"] = 6; path.write_text(json.dumps(value) + "\n")
    elif name == "geometry_wrong":
        path = copy_root / "raw/geometry.json"; value = json.loads(path.read_text()); value["three_pages"] = 2; path.write_text(json.dumps(value) + "\n")
    else: raise ValueError(name)

def main() -> int:
    names = ["missing_file", "hash_changed", "cleanup_residue", "negative_exit_zero", "db_count_wrong", "geometry_wrong"]
    disposable = EVIDENCE / "disposable"
    shutil.rmtree(disposable, ignore_errors=True)
    results = []
    try:
        for name in names:
            target = disposable / name
            shutil.copytree(EVIDENCE, target, ignore=shutil.ignore_patterns("disposable"))
            mutate(target, name)
            process = subprocess.run([sys.executable, str(VERIFIER), str(target)], text=True, capture_output=True)
            output = OUT / f"{name}.json"
            output.write_text(process.stdout, encoding="utf-8")
            results.append({"mutation": name, "actual_copy": str(target.relative_to(EVIDENCE)), "exit_code": process.returncode, "detected": process.returncode != 0, "output": str(output.relative_to(EVIDENCE))})
    finally:
        shutil.rmtree(disposable, ignore_errors=True)
    payload = {"runner": "same semantic verifier on six actual disposable copies", "all_detected": all(item["detected"] for item in results), "results": results, "disposable_residue": disposable.exists()}
    (EVIDENCE / "mutation-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["all_detected"] and not payload["disposable_residue"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
