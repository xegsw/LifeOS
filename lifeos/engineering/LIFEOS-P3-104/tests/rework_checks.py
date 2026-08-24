#!/usr/bin/env python3
"""Static fail-closed checks for P3-104 Rework 1/2."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
OUTPUT = Path(os.environ.get(
    "LIFEOS_P3_104_REWORK_RESULTS",
    "/private/tmp/lifeos-p3-104-rework-static-results.json",
))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


runtime = (ROOT / "src/runtime.rs").read_text()
runner = (ROOT / "scripts/offline_actual_app_replay.sh").read_text()
checks: list[tuple[str, bool, str]] = []


def check(check_id: str, condition: bool, detail: str) -> None:
    checks.append((check_id, bool(condition), detail))


check("RW-STATIC-01", "fn optional_metadata" in runtime, "error-aware lstat helper exists")
check("RW-STATIC-02", "fs::symlink_metadata(path)" in runtime, "final objects use symlink_metadata")
check("RW-STATIC-03", "ErrorKind::NotFound" in runtime, "only true NotFound is treated as absent")
check("RW-STATIC-04", "validate_database_object(path)?" in runtime, "final DB type is always validated")
check("RW-STATIC-05", "optional_metadata(&sidecar)?.is_some()" in runtime, "all sidecar directory objects are rejected")
check("RW-STATIC-06", "dangling_database_and_sidecar_links_fail_closed" in runtime, "dangling DB and sidecar regression exists")
for suffix in ("-journal", "-wal", "-shm"):
    check(f"RW-STATIC-SIDECAR-{suffix[1:].upper()}", f'"{suffix}"' in runtime, f"{suffix} variant covered")
check("RW-RUNNER-01", "CARGO_NET_OFFLINE=true" in runner, "actual-app replay is offline")
check("RW-RUNNER-02", "tauri build" in runner and "--bundles app" in runner and "-- --locked" in runner, "exact locked app bundle command exists")
check("RW-RUNNER-CLEAN", '"$CARGO_HOME/bin/cargo" clean' in runner, "task-local clean rebuild is explicit")
check("RW-RUNNER-03", "normal_reopen=PASS" in runner and "stop_app" in runner, "launch, stop, reopen lifecycle exists")
check("RW-RUNNER-04", "dangling_final_symlink_rejected=PASS" in runner, "actual-app dangling rejection is verified")
check("RW-RUNNER-NO-UI", "dangling_success_ui=not_rendered" in runner, "dangling startup cannot render success UI")
check("RW-RUNNER-05", "cleanup_residual=0" in runner, "exact cleanup gate exists")
check("RW-LOCK-01", digest(ROOT / "Cargo.lock") == "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1", "Frozen Cargo.lock unchanged")
check("RW-ABF-01", digest(PROJECT / "lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration_acceptance_basis_freeze.md") == "2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b", "Frozen ABF unchanged")
check("RW-OLD-EVIDENCE-01", digest(ROOT / "evidence/MANIFEST.md") == "861d0be5bc40d1ebac41cc8b5a695d154d3bf073407b5fc6e3e85e42532a3f46", "initial Engineering Manifest unchanged")

failed = [item for item in checks if not item[1]]
payload = {
    "task": "LIFEOS-P3-104",
    "attempt": "rework-1",
    "passed": len(checks) - len(failed),
    "failed": len(failed),
    "p0": 0,
    "p1": len(failed),
    "p2": 0,
    "unknown": 0,
    "not_implemented": 0,
    "results": [
        {"id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail}
        for check_id, passed, detail in checks
    ],
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(1 if failed else 0)
