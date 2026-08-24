#!/usr/bin/env python3
"""Prove that the evidence verifier fails closed when raw evidence is altered.

The only test copies live beneath the exact task-local temporary root. It never
touches project history or removes existing paths.
"""
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMP_ROOT = pathlib.Path("/private/tmp/lifeos-p3-115-prototype-v1")
RESULT = ROOT / "evidence" / "results" / "mutation_results.json"


def run(base):
    return subprocess.run(
        [sys.executable, str(ROOT / "tests" / "verify_evidence.py"), "--base", str(base), "--allow-pre-finalization"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def clone(name):
    target = TEMP_ROOT / name
    if target.exists():
        raise RuntimeError(f"refusing to reuse mutation path: {target}")
    shutil.copytree(ROOT / "evidence", target)
    return target


def require_failed(label, completed):
    if completed.returncode == 0:
        raise RuntimeError(f"mutation unexpectedly passed: {label}")
    return {"id": label, "status": "PASS", "exit_code": completed.returncode, "output": completed.stdout.strip()}


def main():
    control = run(ROOT / "evidence")
    if control.returncode != 0:
        raise RuntimeError(f"control verifier failed: {control.stdout}")
    matrix = clone("mutation-matrix")
    matrix_path = matrix / "results" / "matrix_results.json"
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    payload["matrix"][0]["status"] = "FAIL"
    matrix_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    closure = clone("mutation-closure")
    closure_doc = json.loads((closure / "dynamic_closure.json").read_text(encoding="utf-8"))
    target = closure / closure_doc["rows"][0]["evidence_path"]
    target.write_bytes(target.read_bytes() + b"\nTAMPERED\n")
    report = {
        "status": "PASS",
        "control": {"exit_code": control.returncode, "output": control.stdout.strip()},
        "mutations": [
            require_failed("matrix-status-tamper", run(matrix)),
            require_failed("raw-evidence-hash-tamper", run(closure)),
        ],
        "temporary_root": str(TEMP_ROOT),
    }
    RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
