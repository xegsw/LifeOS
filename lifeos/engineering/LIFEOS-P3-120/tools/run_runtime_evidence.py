#!/usr/bin/env python3
"""Run the structured synthetic Runtime lifecycle and failure replay."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
TEST_NAME = "evidence_trace_covers_status_lifecycle_and_atomic_failure"


def result(identifier: str, passed: bool, actual: object, evidence: list[str]) -> dict[str, object]:
    return {"id": identifier, "result": "PASS" if passed else "FAIL", "actual": actual, "evidence": evidence}


def main() -> int:
    if not CARGO.is_file():
        print(f"missing Cargo binary: {CARGO}", file=sys.stderr)
        return 1
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TEMP_ROOT / "cargo-target"),
            "TMPDIR": str(TEMP_ROOT / "tmp"),
        }
    )
    (TEMP_ROOT / "tmp").mkdir(parents=True, exist_ok=True)
    command = [str(CARGO), "test", "--locked", "--offline", TEST_NAME, "--", "--nocapture"]
    completed = subprocess.run(command, cwd=CANDIDATE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    log = EVIDENCE / "runtime-test.log"
    log.write_text(completed.stdout, encoding="utf-8")
    match = re.search(r"P3-120-RUNTIME-TRACE (\{.+\})", completed.stdout)
    trace = json.loads(match.group(1)) if match else None
    lifecycle = trace.get("lifecycle", {}) if trace else {}
    failure = trace.get("atomic_failure", {}) if trace else {}
    status = trace.get("runtime_status", {}) if trace else {}
    expected_texts = ["P3-120 synthetic capture one", "P3-120 synthetic capture two"]
    checks = [
        result("P120-M005", bool(completed.returncode == 0 and status == {"status": "restricted_offline", "offline": True, "ai_enabled": False, "ipc_allowlist": ["capture_record", "get_today", "runtime_status"], "renderer_direct_capabilities": [], "unknown_ipc": "deny"}), status, ["runtime-test.log"]),
        result("P120-M006", bool(lifecycle.get("initial_status") == "empty" and lifecycle.get("first_status") == "saved" and lifecycle.get("first_record_id") == lifecycle.get("repeat_record_id")), {key: lifecycle.get(key) for key in ["initial_status", "first_status", "first_record_id"]}, ["runtime-test.log"]),
        result("P120-M007", bool(lifecycle.get("repeat_status") == "idempotent_repeat" and lifecycle.get("first_record_id") == lifecycle.get("repeat_record_id")), {key: lifecycle.get(key) for key in ["repeat_status", "first_record_id", "repeat_record_id"]}, ["runtime-test.log"]),
        result("P120-M008", bool(lifecycle.get("second_status") == "saved" and lifecycle.get("refresh_contents") == expected_texts), {key: lifecycle.get(key) for key in ["second_status", "refresh_contents"]}, ["runtime-test.log"]),
        result("P120-M009", bool(lifecycle.get("refresh_status") == "loaded" and lifecycle.get("refresh_contents") == expected_texts and lifecycle.get("before_refresh_sha256")), {key: lifecycle.get(key) for key in ["refresh_status", "refresh_contents", "before_refresh_sha256"]}, ["runtime-test.log"]),
        result("P120-M010", bool(lifecycle.get("reopen_status") == "loaded" and lifecycle.get("reopen_contents") == expected_texts), {key: lifecycle.get(key) for key in ["reopen_status", "reopen_contents"]}, ["runtime-test.log"]),
        result("P120-M012", bool(failure.get("code") == "injected_atomic_failure" and failure.get("before_db_sha256") == failure.get("after_db_sha256") and failure.get("before_sentinel_sha256") == failure.get("after_sentinel_sha256") and failure.get("records_after_failure") == 1), failure, ["runtime-test.log"]),
    ]
    passed = completed.returncode == 0 and trace is not None and all(check["result"] == "PASS" for check in checks)
    payload = {
        "schema": "lifeos-p3-120/runtime-results-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "command": command,
        "exit_code": completed.returncode,
        "trace": trace,
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }
    (EVIDENCE / "runtime-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "checks": len(checks), "exit_code": completed.returncode}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
