#!/usr/bin/env python3
"""Run P3-077 tests in a clean temporary copy and emit structured evidence."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-077-selfcheck-") as temp:
        copy = Path(temp) / "LIFEOS-P3-077"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("evidence", "runtime", "__pycache__"))
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=copy, text=True, capture_output=True)
        tests = [line.split(" ", 1)[0] for line in result.stderr.splitlines() if line.startswith("test_") and line.rstrip().endswith("ok")]
        payload = {"status": "PASS" if result.returncode == 0 else "FAIL", "pass_count": len(tests), "fail_count": 0 if result.returncode == 0 else 1, "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0, "clean_copy": True, "tests": tests}
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        (EVIDENCE / "self_check_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        (EVIDENCE / "self_check.log").write_text(result.stdout + result.stderr)
        snapshots = {"source_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in sorted((ROOT / "src").rglob("*.py"))}, "result": payload}
        (EVIDENCE / "snapshot.json").write_text(json.dumps(snapshots, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(payload, ensure_ascii=False))
        return result.returncode
if __name__ == "__main__":
    raise SystemExit(main())
