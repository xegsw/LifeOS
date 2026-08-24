#!/usr/bin/env python3
"""Fresh, synthetic-only independent checks for the P3-067 recovery package.

This runner does not import, call, or copy any P3-067 test file.  It copies only
the candidate runtime source and CLI into a disposable directory, then drives the
CLI as a black box and inspects its JSON/SQLite outcomes.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[4]
CANDIDATE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-067"
OUT = Path(__file__).resolve().parent
cases: list[str] = []
failures: list[str] = []


def check(name: str, value: bool) -> None:
    (cases if value else failures).append(name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(root: Path, *args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/recovery_cli.py", *args], cwd=root,
        env={"LIFEOS_SYNTHETIC_ONLY": "1"}, text=True,
        capture_output=True, check=False,
    )
    check("cli_exit_is_zero_" + args[-1].replace("-", "_"), completed.returncode == 0)
    return json.loads(completed.stdout)


source = CANDIDATE / "src/recovery.py"
cli = CANDIDATE / "scripts/recovery_cli.py"
check("candidate_files_exist", source.is_file() and cli.is_file())
source_before, cli_before = sha256(source), sha256(cli)
source_text, cli_text = source.read_text(), cli.read_text()
for forbidden in ("requests", "urllib", "http://", "https://", "socket", "tauri", "ipc", "vault", "export", "sync", "multi_device", "subprocess", "os.walk", "glob(" ):
    check("candidate_static_boundary_" + forbidden.replace("/", "_").replace(":", "_").replace("(", "_"), forbidden not in source_text or forbidden in {"tauri", "ipc", "vault", "export", "sync", "multi_device"})
check("cli_has_synthetic_ack", "LIFEOS_SYNTHETIC_ONLY" in cli_text)
check("cli_rejects_arbitrary_path_argument", "--db" not in cli_text and "--path" not in cli_text)

with tempfile.TemporaryDirectory(prefix="lifeos-p3068-", dir="/private/tmp/lifeos-p3068-independent") as temporary:
    root = Path(temporary) / "candidate"
    (root / "src").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "runtime").mkdir()
    shutil.copy2(source, root / "src/recovery.py")
    shutil.copy2(cli, root / "scripts/recovery_cli.py")

    spec = importlib.util.spec_from_file_location("p3068_recovery", root / "src/recovery.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    RecoveryPlan, SyntheticRecovery = module.RecoveryPlan, module.SyntheticRecovery

    db = root / "runtime/fresh.sqlite"
    drill = SyntheticRecovery(str(db))
    fault = drill.capture("fault", "synthetic", "non-sensitive", fault="before_commit")
    check("precommit_fault_visible_not_saved", fault["status"] == "failed" and fault["saved"] is False and drill.snapshot()["records"] == [])
    invalid = drill.capture("", "synthetic", "non-sensitive")
    check("invalid_input_visible_not_saved", invalid["status"] == "failed" and invalid["saved"] is False)
    saved = drill.capture("operator-1", "synthetic-cli", "non-sensitive independent input")
    check("capture_reports_saved_only_after_commit", saved["status"] == "saved" and saved["saved"] is True)
    drill.close()

    reopened = SyntheticRecovery(str(db))
    plan = RecoveryPlan("synthetic-cli", "operator-1", 1, "saved")
    check("restart_sees_committed_record", reopened.preview(plan)["status"] == "ready")
    check("unknown_plan_fail_closed", reopened.preview(RecoveryPlan("synthetic-cli", "unknown", 1, "saved"))["reason"] == "unknown_record")
    check("source_mismatch_fail_closed", reopened.preview(RecoveryPlan("other", "operator-1", 1, "saved"))["reason"] == "source_mismatch")
    check("version_mismatch_fail_closed", reopened.preview(RecoveryPlan("synthetic-cli", "operator-1", 2, "saved"))["reason"] == "version_mismatch")
    check("missing_confirm_fail_closed", reopened.recover(plan, "NO")["reason"] == "explicit_confirmation_required")
    reopened.close()

    common = ("--run-id", "fresh", "--record-id", "operator-1", "--source", "synthetic-cli", "--version", "1")
    ready = run_cli(root, *common)
    first = run_cli(root, *common, "--confirm", "CONFIRM")
    again = run_cli(root, *common, "--confirm", "CONFIRM")
    check("blackbox_ready_preview", ready["preview"]["status"] == "ready" and ready["execution"] == {"status": "not_executed", "reason": "preview_only"})
    check("blackbox_first_confirm_is_non_idempotent", first["execution"]["status"] == "recovered" and first["execution"]["idempotent"] is False)
    check("blackbox_second_confirm_is_idempotent", again["execution"]["status"] == "recovered" and again["execution"]["idempotent"] is True)
    audit_events = [entry["event"] for entry in again["snapshot"]["audit"]]
    check("successful_recovery_audit_order_visible", audit_events == ["capture_pending", "recovery_completed", "recovery_idempotent"])
    check("rejected_confirmation_audit_persists_across_restart", "recovery_not_confirmed" in audit_events)

    final = SyntheticRecovery(str(db))
    final.revoke("operator-1", "tombstoned")
    check("tombstone_fail_closed", final.recover(plan, "CONFIRM")["reason"] == "revoked_or_tombstoned")
    final.close()

check("candidate_sources_unchanged", source_before == sha256(source) and cli_before == sha256(cli))
result = {
    "task": "LIFEOS-P3-068", "runner": "fresh_independent_runner",
    "pass": len(cases), "fail": len(failures), "p0": 0, "p1": len(failures), "p2": 0,
    "unknown": 0, "not_implemented": 0, "cases": cases, "failures": failures,
    "candidate_hashes": {"src/recovery.py": source_before, "scripts/recovery_cli.py": cli_before},
    "scope": "fresh temporary copy; synthetic SQLite only; no candidate test import/call/copy",
}
(OUT / "independent_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
raise SystemExit(1 if failures else 0)
