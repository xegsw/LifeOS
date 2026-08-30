#!/usr/bin/env python3
"""Persist an isolated, read-only candidate regression and Phase-C gate check."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
CANDIDATE = Path(sys.argv[1]).resolve()
TEMP = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1").resolve()
EVIDENCE = REVIEW / "evidence"


def invoke(command: list[str], env: dict[str, str]) -> dict[str, object]:
    completed = subprocess.run(command, text=True, capture_output=True, env=env, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
    }


def main() -> int:
    if not CANDIDATE.is_dir():
        raise SystemExit("candidate directory missing")
    TEMP.mkdir(mode=0o700, parents=True, exist_ok=True)
    runtime = TEMP / "independent-regression-runtime"
    runtime.mkdir(mode=0o700, exist_ok=True)
    common = os.environ.copy()
    common.update(
        {
            "LIFEOS_RUNTIME_ROOT": str(runtime),
            "LIFEOS_INPUT_MODE": "synthetic",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TEMP / "independent-regression-target"),
        }
    )
    test = invoke(
        [
            "/Users/xxe/.cargo/bin/cargo", "test", "--manifest-path", str(CANDIDATE / "Cargo.toml"),
            "--locked", "--offline", "--", "--test-threads=1",
        ],
        common,
    )
    match = re.search(r"test result: ok\. (\d+) passed; 0 failed", str(test["stdout_tail"]))
    test_payload = {
        "schema": "lifeos-p3-141-independent-regression-v1",
        "candidate_read_only": str(CANDIDATE),
        "synthetic_runtime_root": str(runtime),
        "network_mode": "cargo_offline",
        "result": test,
        "test_count": int(match.group(1)) if match else None,
        "pass": test["returncode"] == 0 and match is not None and int(match.group(1)) == 42,
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "independent_candidate_regression.json").write_text(
        json.dumps(test_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    phase_env = common.copy()
    phase_runtime = TEMP / "phase-c-gate-unresolved"
    phase_env["LIFEOS_RUNTIME_ROOT"] = str(phase_runtime)
    phase_env["LIFEOS_INPUT_MODE"] = "real_self_use"
    phase_env.pop("LIFEOS_P3_141_PHASE_B_RECEIPT", None)
    phase_env["CARGO_TARGET_DIR"] = str(TEMP / "phase-c-gate-target")
    gate = invoke(
        [
            "/Users/xxe/.cargo/bin/cargo", "build", "--manifest-path", str(CANDIDATE / "Cargo.toml"),
            "--locked", "--offline",
        ],
        phase_env,
    )
    expected = "phase_b_independent_pass_required before runtime-root inspection"
    gate_payload = {
        "schema": "lifeos-p3-141-phase-c-pre-root-gate-v1",
        "candidate_read_only": str(CANDIDATE),
        "mode": "real_self_use",
        "receipt_present": False,
        "unresolved_synthetic_path": str(phase_runtime),
        "result": gate,
        "expected_error": expected,
        "pass": gate["returncode"] != 0 and expected in (str(gate["stdout_tail"]) + str(gate["stderr_tail"])),
    }
    (EVIDENCE / "phase_c_pre_root_gate.json").write_text(
        json.dumps(gate_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if test_payload["pass"] and gate_payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
