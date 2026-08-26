#!/usr/bin/env python3
"""In-memory mutation proof: each evidence integrity failure must fail closed."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "results" / "mutation_results.json"


def run_verifier() -> int:
    return subprocess.run([sys.executable, str(ROOT / "tests" / "verify_evidence.py")], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    paths = {
        "closure": EVIDENCE / "dynamic_closure.json",
        "actions": EVIDENCE / "raw" / "dynamic_actions.json",
        "matrix": EVIDENCE / "results" / "matrix_results.json",
        "preflight": EVIDENCE / "results" / "chrome_preflight.json",
    }
    original = {key: path.read_text(encoding="utf-8") for key, path in paths.items()}
    baseline = run_verifier()
    cases = []
    mutations = [
        ("missing_closure_row", "closure", lambda value: value["rows"].pop()),
        ("matrix_status", "matrix", lambda value: value["rows"][0].update({"status": "PASS" if value["rows"][0]["status"] != "PASS" else "FAIL"})),
        ("raw_log_hash", "closure", lambda value: value["rows"][0].update({"raw_log_sha256": "0" * 64})),
        ("unknown_action_link", "closure", lambda value: value["rows"][0].update({"action_id": "D-UNKNOWN"})),
        ("unsafe_evidence_path", "closure", lambda value: value["rows"][0].update({"screenshot": "../outside.png"})),
        ("preflight_status", "preflight", lambda value: value.update({"status": "FAIL"})),
    ]
    try:
        for name, target, mutate in mutations:
            data = json.loads(original[target])
            mutate(data)
            write(paths[target], data)
            code = run_verifier()
            cases.append({"mutation": name, "expected_exit": 1, "actual_exit": code, "status": "PASS" if code != 0 else "FAIL"})
            paths[target].write_text(original[target], encoding="utf-8")
        restored = run_verifier()
        payload = {"runner": "tests/run_mutations.py", "baseline_exit": baseline, "restored_exit": restored, "cases": cases, "overall": "PASS" if baseline == 0 and restored == 0 and all(item["status"] == "PASS" for item in cases) else "FAIL"}
    finally:
        for key, path in paths.items():
            path.write_text(original[key], encoding="utf-8")
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
