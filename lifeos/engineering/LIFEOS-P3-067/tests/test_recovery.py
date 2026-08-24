#!/usr/bin/env python3
import json, os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from recovery import BOUNDARIES, RecoveryPlan, SyntheticRecovery

cases = []
def check(name, assertion):
    assert assertion, name
    cases.append(name)

with tempfile.TemporaryDirectory(dir=ROOT / "runtime") as temp:
    db = str(Path(temp) / "synthetic.sqlite")
    drill = SyntheticRecovery(db)
    failed = drill.capture("fault-1", "synthetic-source", "non-sensitive", fault="before_commit")
    check("precommit_fault_is_visible_never_saved", failed["status"] == "failed" and not failed["saved"] and not drill.snapshot()["records"])
    invalid = drill.capture("", "synthetic-source", "non-sensitive")
    check("invalid_input_is_visible_never_saved", invalid["status"] == "failed" and not invalid["saved"])
    saved = drill.capture("record-1", "synthetic-source", "non-sensitive synthetic text")
    check("saved_only_after_commit", saved["status"] == "saved" and saved["saved"])
    drill.close()
    reopened = SyntheticRecovery(db)
    plan = RecoveryPlan("synthetic-source", "record-1", 1, "saved")
    check("restart_reopens_committed_record", reopened.preview(plan)["status"] == "ready")
    check("explicit_confirm_required", reopened.recover(plan, "NO")["reason"] == "explicit_confirmation_required")
    reopened.close()
    reopened = SyntheticRecovery(db)
    after_not_confirmed_restart = reopened.snapshot()
    check("not_confirmed_audit_persists_across_restart", [a["event"] for a in after_not_confirmed_restart["audit"]] == ["capture_pending", "recovery_not_confirmed"])
    first = reopened.recover(plan, "CONFIRM")
    again = reopened.recover(plan, "CONFIRM")
    check("confirmed_recovery_is_idempotent", first["status"] == "recovered" and not first["idempotent"] and again["idempotent"])
    check("unknown_plan_has_visible_failure", reopened.preview(object())["reason"] == "invalid_or_unknown_plan")
    check("source_mismatch_blocks", reopened.preview(RecoveryPlan("other", "record-1", 1, "saved"))["reason"] == "source_mismatch")
    check("version_mismatch_blocks", reopened.preview(RecoveryPlan("synthetic-source", "record-1", 9, "saved"))["reason"] == "version_mismatch")
    reopened.revoke("record-1", "tombstoned")
    check("tombstone_blocks_recovery", reopened.recover(plan, "CONFIRM")["reason"] == "revoked_or_tombstoned")
    reopened.close()
    reopened = SyntheticRecovery(db)
    after_blocked_restart = reopened.snapshot()
    check("blocked_audit_persists_across_restart", [a["event"] for a in after_blocked_restart["audit"]][-2:] == ["record_revoked", "recovery_blocked"])
    saved2 = reopened.capture("record-2", "synthetic-source", "second synthetic text")
    reopened.revoke("record-2", "revoked")
    check("revocation_blocks_recovery", saved2["status"] == "saved" and reopened.preview(RecoveryPlan("synthetic-source", "record-2", 1, "saved"))["reason"] == "revoked_or_tombstoned")
    snapshot = reopened.snapshot()
    check("audit_and_external_boundaries_observable", len(snapshot["audit"]) >= 7 and snapshot["boundaries"] == BOUNDARIES and all(json.loads(a["detail_json"])["boundaries"] == BOUNDARIES for a in snapshot["audit"]))
    reopened.close()

audit_snapshots = {
    "after_not_confirmed_restart": after_not_confirmed_restart,
    "after_blocked_restart": after_blocked_restart,
}
(ROOT / "evidence" / "cross_restart_audit_snapshots.json").write_text(json.dumps(audit_snapshots, indent=2, sort_keys=True) + "\n")
result = {"task":"LIFEOS-P3-067", "pass":len(cases), "fail":0, "p0":0, "p1":0, "p2":0, "unknown":0, "not_implemented":0, "cases":cases, "audit_snapshots":"cross_restart_audit_snapshots.json", "scope":"synthetic SQLite only; no network/Tauri/IPC/Vault/real paths/export/cloud/sync/multi-device/L3/external user"}
(ROOT / "evidence" / "test_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
