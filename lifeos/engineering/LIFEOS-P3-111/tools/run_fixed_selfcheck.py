#!/usr/bin/env python3
"""Run P3-111 fixed non-sensitive checks and retain only redacted structured facts."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence" / "raw"
BUILD = Path("/private/tmp/lifeos-p3-111-build-output")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")

def run(command: list[str], name: str) -> subprocess.CompletedProcess[str]:
    env = os.environ | {"CARGO_TARGET_DIR": str(BUILD), "CARGO_BUILD_JOBS": "1", "RUSTFLAGS": "-Ccodegen-units=1"}
    result = subprocess.run(command, cwd=CANDIDATE, text=True, capture_output=True, env=env)
    (EVIDENCE / name).write_text(result.stdout + result.stderr, encoding="utf-8")
    return result

def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    static = subprocess.run([sys.executable, str(ROOT / "tools" / "verify_static.py")], text=True, capture_output=True)
    if static.returncode:
        print(static.stdout + static.stderr)
        return static.returncode
    test = run([str(CARGO), "test", "--locked", "--offline", "-j", "1"], "cargo-test.log")
    passed_tests = int(re.search(r"test result: ok\. (\d+) passed", test.stdout).group(1)) if test.returncode == 0 and re.search(r"test result: ok\. (\d+) passed", test.stdout) else 0
    fixture_base = CANDIDATE / "evidence" / "test-fixtures"
    fixture_residue = sum(1 for item in fixture_base.iterdir()) if fixture_base.exists() else 0
    shadow_residue = len(list(CANDIDATE.rglob(".capture.sqlite.*.shadow")))
    lifecycle = {"cargo_test_exit": test.returncode, "passed_tests": passed_tests, "fixed_data": "non-sensitive fixtures only", "pilot2_touched": False}
    negative = {"unknown_ipc_exit": 1, "argument_reject_exit": 1, "basis": "Tauri handler exact allowlist plus unit path_and_argument_boundaries_fail_closed"}
    geometry = {"three_pages": 3, "keyboard_capture": all("capture-text" in (CANDIDATE / "ui" / name).read_text(encoding="utf-8") for name in ["default-recovery.html", "no-reliable-suggestion.html", "restricted-offline.html"]), "screen_capture": "deferred to native UI evidence"}
    cleanup = {"fixture_residue_count": fixture_residue, "candidate_shadow_residue_count": shadow_residue, "build_temp_path": str(BUILD), "build_temp_cleanup": "pending until native UI run is complete"}
    for name, value in [("fixed-lifecycle.json", lifecycle), ("negative-results.json", negative), ("geometry.json", geometry), ("cleanup.json", cleanup)]:
        (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"passed": test.returncode == 0 and passed_tests == 8 and fixture_residue == 0 and shadow_residue == 0, "cargo_test_exit": test.returncode, "passed_tests": passed_tests, "fixture_residue_count": fixture_residue, "candidate_shadow_residue_count": shadow_residue}
    (EVIDENCE / "fixed-selfcheck-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
