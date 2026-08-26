#!/usr/bin/env python3
"""Run the frozen P3-121 Rust test suite with task-local build paths."""
from __future__ import annotations

import json
import os
import subprocess
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
OUT = ROOT / "evidence" / "runtime"
CARGO = "/Users/xxe/.cargo/bin/cargo"


def main() -> int:
    env = os.environ.copy()
    env.update({
        "CARGO_TARGET_DIR": str(ROOT / "build" / "cargo-target"),
        "TMPDIR": str(ROOT / "build" / "tmp"),
    })
    completed = subprocess.run([CARGO, "test", "--locked", "--offline"], cwd=CANDIDATE, env=env, text=True, capture_output=True, check=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cargo-test-locked-offline.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    named = [
        "first_repeat_second_refresh_and_reopen_are_consistent",
        "runtime_path_is_exact_and_other_paths_are_rejected",
        "invalid_or_unpaired_input_is_rejected_before_storage",
        "injected_failure_preserves_database_and_sentinel",
        "runtime_status_closes_direct_capabilities_and_keeps_three_ipc",
    ]
    payload = {
        "task": "LIFEOS-P3-121",
        "command": [CARGO, "test", "--locked", "--offline"],
        "cwd": str(CANDIDATE),
        "cargo_target_dir": env["CARGO_TARGET_DIR"],
        "tmpdir": env["TMPDIR"],
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0 and "test result: ok. 9 passed" in completed.stdout,
        "required_named_tests_seen": {name: (name in completed.stdout) for name in named},
        "warning_preserved": "DARWIN_USER_TEMP_DIR" in completed.stderr,
    }
    bundle = ROOT / "build" / "cargo-target" / "release" / "bundle" / "macos" / "LifeOS P3-121 Person-centered Runtime.app"
    executable = bundle / "Contents" / "MacOS" / "lifeos-p3-121"
    payload["actual_app_bundle"] = {
        "path": str(bundle),
        "exists": bundle.is_dir(),
        "executable_exists": executable.is_file(),
        "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest() if executable.is_file() else None,
    }
    (OUT / "cargo-test-locked-offline.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("P3-121-RUST-TEST: " + ("PASS" if payload["passed"] and all(payload["required_named_tests_seen"].values()) else "FAIL"))
    success = payload["passed"] and all(payload["required_named_tests_seen"].values()) and payload["actual_app_bundle"]["executable_exists"]
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
