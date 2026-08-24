#!/usr/bin/env python3
"""Fresh, synthetic-only independent audit for LIFEOS-P3-069.

This runner copies only the candidate implementation and CLI into a fresh
temporary directory.  It neither imports, calls, nor copies P3-067 tests.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
P67 = REPO / "lifeos/engineering/LIFEOS-P3-067"
P68 = REPO / "lifeos/reviews/LIFEOS-P3-068/evidence"
OUT = Path(__file__).with_name("independent_results.json")
TMP_PARENT = Path("/private/tmp/lifeos-p3069-independent")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect(results: list[dict], name: str, condition: bool, detail: str) -> None:
    results.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def cli(candidate: Path, run_id: str, record_id: str, source: str, version: int, confirm: str = "") -> dict:
    command = [sys.executable, str(candidate / "scripts/recovery_cli.py"), "--run-id", run_id,
               "--record-id", record_id, "--source", source, "--version", str(version)]
    if confirm:
        command.extend(["--confirm", confirm])
    environment = dict(os.environ, LIFEOS_SYNTHETIC_ONLY="1")
    completed = subprocess.run(command, cwd=candidate, env=environment, check=False,
                               text=True, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def load_candidate(candidate: Path):
    spec = importlib.util.spec_from_file_location("p3069_recovery", candidate / "src/recovery.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_manifest(results: list[dict]) -> dict:
    manifest = (P67 / "evidence/MANIFEST.md").read_text()
    rows = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", manifest)
    valid = bool(rows) and all(sha256(P67 / "evidence" / name) == digest for name, digest in rows)
    expect(results, "p3_067_current_evidence_hashes", valid, f"checked={len(rows)}")

    old_manifest = (P68 / "MANIFEST.md").read_text()
    old_runner = re.search(r"`independent_runner.py` \| `([0-9a-f]{64})`", old_manifest)
    old_results = re.search(r"`independent_results.json` \| `([0-9a-f]{64})`", old_manifest)
    preserved = bool(old_runner and old_results and sha256(P68 / "independent_runner.py") == old_runner.group(1)
                     and sha256(P68 / "independent_results.json") == old_results.group(1))
    expect(results, "p3_068_historical_evidence_preserved", preserved, "historical runner/results hashes unchanged")
    historic_source = re.search(r"src/recovery.py` \| `([0-9a-f]{64})`", old_manifest)
    current_source = sha256(P67 / "src/recovery.py")
    expected_changed = bool(historic_source and current_source != historic_source.group(1))
    expect(results, "p3_068_historic_hash_not_reused_as_current", expected_changed,
           "current candidate differs from P3-068 pre-rework source hash")
    return {"p3_067_manifest_entries": len(rows), "current_source_sha256": current_source,
            "p3_068_historic_source_sha256": historic_source.group(1) if historic_source else None}


def main() -> int:
    results: list[dict] = []
    TMP_PARENT.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix="candidate-", dir=TMP_PARENT))
    (candidate / "src").mkdir(); (candidate / "scripts").mkdir(); (candidate / "runtime").mkdir()
    shutil.copy2(P67 / "src/recovery.py", candidate / "src/recovery.py")
    shutil.copy2(P67 / "scripts/recovery_cli.py", candidate / "scripts/recovery_cli.py")
    module = load_candidate(candidate)
    Recovery, Plan = module.SyntheticRecovery, module.RecoveryPlan

    try:
        # Capture durability and failure truthfulness in a clean runtime.
        db = candidate / "runtime/capture.sqlite"
        drill = Recovery(str(db))
        fault = drill.capture("fault", "synthetic", "text", fault="before_commit")
        invalid = drill.capture("", "synthetic", "text")
        saved = drill.capture("saved", "synthetic", "text")
        drill.close()
        reopened = Recovery(str(db)); snapshot = reopened.snapshot(); reopened.close()
        expect(results, "capture_fault_never_claims_saved", fault["saved"] is False and fault["status"] == "failed", str(fault))
        expect(results, "capture_invalid_never_claims_saved", invalid["saved"] is False and invalid["status"] == "failed", str(invalid))
        expect(results, "saved_only_after_committed_reopen", saved["saved"] is True and [r["id"] for r in snapshot["records"]] == ["saved"], str(saved))

        # Black-box operator chain: a separate pre-commit operation makes the CLI preview ready.
        chain_db = candidate / "runtime/chain.sqlite"
        setup = Recovery(str(chain_db)); setup.capture("operator", "synthetic-cli", "non-sensitive text"); setup.close()
        ready = cli(candidate, "chain", "operator", "synthetic-cli", 1)
        first = cli(candidate, "chain", "operator", "synthetic-cli", 1, "CONFIRM")
        again = cli(candidate, "chain", "operator", "synthetic-cli", 1, "CONFIRM")
        expect(results, "cli_ready_preview_before_confirmation", ready["preview"]["status"] == "ready" and ready["execution"]["status"] == "not_executed", "ready preview")
        expect(results, "cli_first_confirm_is_non_idempotent", first["execution"].get("idempotent") is False and first["execution"]["status"] == "recovered", "first recovery")
        expect(results, "cli_second_confirm_is_idempotent", again["execution"].get("idempotent") is True and again["execution"]["status"] == "recovered", "second receipt")
        expect(results, "cli_audit_order", [x["event"] for x in again["snapshot"]["audit"]] == ["capture_pending", "recovery_completed", "recovery_idempotent"], "audit sequence")

        # Reproduce P3-068's prior P1 as a current cross-restart durability attack.
        audit_db = candidate / "runtime/audit.sqlite"
        audit = Recovery(str(audit_db)); audit.capture("audit", "synthetic", "text")
        not_confirmed = audit.recover(Plan("synthetic", "audit", 1, "saved"), "NO"); audit.close()
        audit = Recovery(str(audit_db)); after_reject = audit.snapshot(); audit.revoke("audit", "tombstoned"); audit.close()
        audit = Recovery(str(audit_db)); blocked = audit.recover(Plan("synthetic", "audit", 2, "tombstoned"), "CONFIRM"); audit.close()
        audit = Recovery(str(audit_db)); after_block = audit.snapshot(); audit.close()
        reject_events = [x["event"] for x in after_reject["audit"]]
        block_events = [x["event"] for x in after_block["audit"]]
        expect(results, "not_confirmed_audit_durable_across_restart", not_confirmed["reason"] == "explicit_confirmation_required" and reject_events == ["capture_pending", "recovery_not_confirmed"], str(reject_events))
        expect(results, "blocked_audit_durable_and_ordered_across_restart", blocked["reason"] == "revoked_or_tombstoned" and block_events == ["capture_pending", "recovery_not_confirmed", "record_revoked", "recovery_blocked"], str(block_events))

        # Four independent fail-closed variants; none may recover the record.
        failures = []
        for record_id in ("source", "version", "revoked", "tombstone"):
            d = Recovery(str(candidate / f"runtime/{record_id}.sqlite")); d.capture(record_id, "synthetic", "text")
            if record_id == "source": plan = Plan("other", record_id, 1, "saved")
            elif record_id == "version": plan = Plan("synthetic", record_id, 2, "saved")
            elif record_id == "revoked": d.revoke(record_id, "revoked"); plan = Plan("synthetic", record_id, 2, "revoked")
            else: d.revoke(record_id, "tombstoned"); plan = Plan("synthetic", record_id, 2, "tombstoned")
            result = d.recover(plan, "CONFIRM"); snap = d.snapshot(); d.close()
            failures.append((record_id, result["status"], result["reason"], snap["records"][0]["restored"]))
        expect(results, "source_version_revocation_tombstone_fail_closed", all(status == "blocked" and restored == 0 for _, status, _, restored in failures), str(failures))

        source_text = (candidate / "src/recovery.py").read_text()
        cli_text = (candidate / "scripts/recovery_cli.py").read_text()
        forbidden = [term for term in ("requests", "urllib", "http.client", "socket", "os.walk", "rglob(", "glob(") if term in source_text + cli_text]
        boundaries = module.BOUNDARIES
        expect(results, "external_capabilities_staticly_closed", not forbidden and boundaries == {
            "network": "disabled", "tauri_ipc": "not_used", "vault": "not_used", "real_paths": "not_used", "export": "not_used", "cloud": "not_used", "sync": "not_used", "multi_device": "not_used", "l3": "not_used", "external_user": "not_used", "external_action": "none"}, str(forbidden))
        expect(results, "cli_accepts_no_database_path", "db-path" not in cli_text and "--path" not in cli_text, "task-local run-id only")
        evidence = verify_manifest(results)
    except Exception as error:
        results.append({"name": "runner_exception", "status": "FAIL", "detail": repr(error)})

    passed = sum(case["status"] == "PASS" for case in results)
    failed = len(results) - passed
    document = {"task": "LIFEOS-P3-069", "scope": "fresh temporary copy; synthetic SQLite only", "pass": passed, "fail": failed,
                "p0": 0, "p1": 0 if failed == 0 else 1, "p2": 0, "unknown": 0, "not_implemented": 0,
                "candidate_copy": str(candidate), "cases": results, "evidence": evidence if "evidence" in locals() else {}}
    OUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": passed, "fail": failed, "results": str(OUT)}, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
