#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from permissions import CONTROLLED_PROJECT_ID, PermissionErrorVisible, PermissionSettings

def settings(**overrides):
    value = dict(project_id=CONTROLLED_PROJECT_ID, category="synthetic_note", purpose="local_recovery", location="local_sqlite", processor="local_rules")
    value.update(overrides); return value
def expect_error(fn):
    try: fn()
    except PermissionErrorVisible: return
    raise AssertionError("expected visible refusal")
def main():
    cases=[]
    (ROOT / "runtime").mkdir(parents=True, exist_ok=True)
    (ROOT / "evidence").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "runtime") as temp:
        app=PermissionSettings(Path(temp)/"permissions.sqlite")
        try:
            assert app.consume(**settings(), now_ms=10)["allowed"] is False; cases.append("default_deny")
            expect_error(lambda: app.decide(**settings(category=""), expires_at_ms=100, decision="grant", confirmation="CONFIRM", idempotency_key="bad", now_ms=10)); cases.append("empty_input_rejected")
            expect_error(lambda: app.decide(**settings(), expires_at_ms=100, decision="grant", confirmation="yes", idempotency_key="bad-confirm", now_ms=10)); cases.append("explicit_confirmation_required")
            allow=app.decide(**settings(), expires_at_ms=100, decision="grant", confirmation="CONFIRM", idempotency_key="grant-1", now_ms=10)
            assert allow["status"]=="granted" and app.consume(**settings(), now_ms=11)["allowed"]; cases.append("granted_allows_local_synthetic_consumption")
            assert app.decide(**settings(), expires_at_ms=100, decision="grant", confirmation="CONFIRM", idempotency_key="grant-1", now_ms=12)["duplicate"]; cases.append("grant_idempotent")
            expect_error(lambda: app.decide(**settings(), expires_at_ms=100, decision="deny", confirmation="CONFIRM", idempotency_key="grant-1", now_ms=12)); cases.append("idempotency_conflict_visible")
            assert app.revoke(authorization_id=allow["authorization_id"], confirmation="REVOKE", idempotency_key="revoke-1", now_ms=20)["status"]=="revoked"
            assert not app.consume(**settings(), now_ms=21)["allowed"]; cases.append("revoke_fail_closed")
            assert app.revoke(authorization_id=allow["authorization_id"], confirmation="REVOKE", idempotency_key="revoke-1", now_ms=22)["duplicate"]; cases.append("revoke_idempotent")
            denied=app.decide(**settings(category="synthetic_task"), expires_at_ms=100, decision="deny", confirmation="CONFIRM", idempotency_key="deny-1", now_ms=30)
            assert denied["status"]=="denied" and not app.consume(**settings(category="synthetic_task"), now_ms=31)["allowed"]; cases.append("explicit_deny_blocks")
            exp=app.decide(**settings(purpose="local_summary"), expires_at_ms=40, decision="grant", confirmation="CONFIRM", idempotency_key="expire-1", now_ms=30)
            assert not app.consume(**settings(purpose="local_summary"), now_ms=40)["allowed"]; cases.append("expiry_fail_closed")
            assert not app.consume(**settings(purpose="local_recovery"), now_ms=30)["allowed"]
            assert not app.consume(**settings(category="synthetic_task"), now_ms=30)["allowed"]
            assert not app.consume(**settings(purpose="local_summary", location="local_cache"), now_ms=30)["allowed"]
            assert not app.consume(**settings(purpose="local_summary", processor="local_summary_engine"), now_ms=30)["allowed"]
            cases.append("purpose_location_processor_binding_mismatch_blocks")
            expect_error(lambda: app.revoke(authorization_id=exp["authorization_id"], confirmation="no", idempotency_key="x", now_ms=50)); cases.append("invalid_revoke_refused")
            snapshot=app.snapshot()
            checks=[e for e in snapshot["audit_events"] if e["event_type"] == "consumption.check"]
            assert len(checks) >= 7 and all("external_action" in e["detail_json"] and "ai_consumption" in e["detail_json"] for e in checks)
            assert snapshot["boundaries"] == {"network":"disabled", "tauri_ipc":"not_used", "real_paths":"not_used", "external_action":"none"}
            cases.append("audit_and_versions_observable")
            (ROOT / "evidence" / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        finally: app.close()
    def matrix_app(name):
        return PermissionSettings(ROOT / "runtime" / (name + ".sqlite"))
    def decide(app, key, decision, now, **overrides):
        return app.decide(**settings(**overrides), expires_at_ms=100, decision=decision, confirmation="CONFIRM", idempotency_key=key, now_ms=now)
    matrix_evidence=[]
    for name in ("matrix-grant-deny", "matrix-deny-grant", "matrix-grant-revoke", "matrix-expiry", "matrix-ambiguous-grants", "matrix-repeat-grant", "matrix-repeat-deny", "matrix-revoke-replay", "matrix-revoke-conflict"):
        (ROOT / "runtime" / (name + ".sqlite")).unlink(missing_ok=True)
    app=matrix_app("matrix-grant-deny")
    try:
        decide(app, "gd-grant", "grant", 10); decide(app, "gd-deny", "deny", 11)
        observed=app.consume(**settings(), now_ms=12); snap=app.snapshot()
        assert observed["allowed"] is False and observed["reason"] == "explicit_deny_current" and len(observed["current_grant_ids"]) == len(observed["current_deny_ids"]) == 1
        assert len(snap["authorizations"]) == 2 and all(row["version"] == 1 for row in snap["authorizations"])
        matrix_evidence.append({"case":"grant_then_deny", "return":observed, "snapshot":snap})
        cases.append("matrix_grant_then_deny_deny_priority")
    finally: app.close()
    app=matrix_app("matrix-deny-grant")
    try:
        decide(app, "dg-deny", "deny", 10); decide(app, "dg-grant", "grant", 11)
        observed=app.consume(**settings(), now_ms=12); snap=app.snapshot()
        assert not observed["allowed"] and observed["reason"] == "explicit_deny_current" and len(snap["audit_events"]) == 3
        matrix_evidence.append({"case":"deny_then_grant", "return":observed, "snapshot":snap})
        cases.append("matrix_deny_then_grant_deny_priority")
    finally: app.close()
    app=matrix_app("matrix-grant-revoke")
    try:
        granted=decide(app, "gr-grant", "grant", 10); revoked=app.revoke(authorization_id=granted["authorization_id"], confirmation="REVOKE", idempotency_key="gr-revoke", now_ms=11)
        observed=app.consume(**settings(), now_ms=12); snap=app.snapshot()
        assert revoked["status"] == "revoked" and not observed["allowed"] and snap["authorizations"][0]["version"] == 2 and len(snap["revocation_commands"]) == 1
        matrix_evidence.append({"case":"grant_then_revoke", "return":observed, "revoke":revoked, "snapshot":snap})
        cases.append("matrix_grant_then_revoke_fail_closed")
    finally: app.close()
    app=matrix_app("matrix-expiry")
    try:
        app.decide(**settings(), expires_at_ms=20, decision="grant", confirmation="CONFIRM", idempotency_key="expiry-grant", now_ms=10)
        observed=app.consume(**settings(), now_ms=20)
        assert not observed["allowed"] and observed["reason"] == "authorization_not_current_or_not_matching"
        matrix_evidence.append({"case":"grant_then_expiry", "return":observed, "snapshot":app.snapshot()})
        cases.append("matrix_grant_then_expiry_fail_closed")
    finally: app.close()
    app=matrix_app("matrix-ambiguous-grants")
    try:
        decide(app, "ag-grant-a", "grant", 10); decide(app, "ag-grant-b", "grant", 11)
        observed=app.consume(**settings(), now_ms=12); snap=app.snapshot()
        assert not observed["allowed"] and observed["reason"] == "ambiguous_multiple_current_grants" and len(observed["current_grant_ids"]) == 2 and not observed["current_deny_ids"]
        matrix_evidence.append({"case":"multiple_current_grants_ambiguous", "return":observed, "snapshot":snap})
        cases.append("matrix_multiple_current_grants_fail_closed")
    finally: app.close()
    app=matrix_app("matrix-repeat-grant")
    try:
        first=decide(app, "repeat-grant", "grant", 10); second=decide(app, "repeat-grant", "grant", 11); snap=app.snapshot()
        assert not first["duplicate"] and second["duplicate"] and len(snap["authorizations"]) == 1 and len(snap["audit_events"]) == 1
        matrix_evidence.append({"case":"duplicate_grant", "first":first, "second":second, "snapshot":snap})
        cases.append("matrix_duplicate_grant_idempotent")
    finally: app.close()
    app=matrix_app("matrix-repeat-deny")
    try:
        first=decide(app, "repeat-deny", "deny", 10); second=decide(app, "repeat-deny", "deny", 11); observed=app.consume(**settings(), now_ms=12); snap=app.snapshot()
        assert not first["duplicate"] and second["duplicate"] and not observed["allowed"] and len(snap["authorizations"]) == 1
        matrix_evidence.append({"case":"duplicate_deny", "first":first, "second":second, "return":observed, "snapshot":snap})
        cases.append("matrix_duplicate_deny_idempotent")
    finally: app.close()
    app=matrix_app("matrix-revoke-replay")
    try:
        granted=decide(app, "rr-grant", "grant", 10); first=app.revoke(authorization_id=granted["authorization_id"], confirmation="REVOKE", idempotency_key="rr-revoke", now_ms=11); second=app.revoke(authorization_id=granted["authorization_id"], confirmation="REVOKE", idempotency_key="rr-revoke", now_ms=12); snap=app.snapshot()
        assert not first["duplicate"] and second["duplicate"] and len(snap["revocation_commands"]) == 1 and len(snap["audit_events"]) == 2
        matrix_evidence.append({"case":"revoke_idempotent", "first":first, "second":second, "snapshot":snap})
        cases.append("matrix_revoke_idempotent")
    finally: app.close()
    app=matrix_app("matrix-revoke-conflict")
    try:
        first=decide(app, "rc-grant-a", "grant", 10); second=decide(app, "rc-grant-b", "grant", 10, category="synthetic_task")
        app.revoke(authorization_id=first["authorization_id"], confirmation="REVOKE", idempotency_key="rc-key", now_ms=11)
        expect_error(lambda: app.revoke(authorization_id=second["authorization_id"], confirmation="REVOKE", idempotency_key="rc-key", now_ms=12))
        snap=app.snapshot(); assert len(snap["revocation_commands"]) == 1 and any(row["id"] == second["authorization_id"] and row["status"] == "granted" for row in snap["authorizations"])
        matrix_evidence.append({"case":"revoke_idempotency_key_conflict", "snapshot":snap})
        cases.append("matrix_revoke_idempotency_key_conflict_visible")
    finally: app.close()
    cli_db = ROOT / "runtime" / "cli-e2e.sqlite"
    cli_db.unlink(missing_ok=True)
    base=[sys.executable, str(ROOT / "scripts" / "permission_cli.py")]
    arguments=["--synthetic-only", "--run-id", "cli-e2e", "--category", "synthetic_note", "--purpose", "local_recovery", "--location", "local_sqlite", "--processor", "local_rules"]
    preview=subprocess.run(base+["preview", *arguments, "--expires-at-ms", "5000"], capture_output=True, text=True)
    grant=subprocess.run(base+["decide", *arguments, "--expires-at-ms", "5000", "--decision", "grant", "--confirmation", "CONFIRM", "--idempotency-key", "cli-e2e-grant"], capture_output=True, text=True)
    consume=subprocess.run(base+["consume", *arguments], capture_output=True, text=True)
    deny=subprocess.run(base+["decide", *arguments, "--expires-at-ms", "5000", "--decision", "deny", "--confirmation", "CONFIRM", "--idempotency-key", "cli-e2e-deny", "--now-ms", "1001"], capture_output=True, text=True)
    blocked=subprocess.run(base+["consume", *arguments, "--now-ms", "1002"], capture_output=True, text=True)
    assert preview.returncode == grant.returncode == consume.returncode == deny.returncode == blocked.returncode == 0
    assert json.loads(preview.stdout)["default_decision"] == "deny" and json.loads(grant.stdout)["status"] == "granted" and json.loads(consume.stdout)["allowed"] is True
    assert json.loads(deny.stdout)["status"] == "denied" and json.loads(blocked.stdout)["allowed"] is False and json.loads(blocked.stdout)["reason"] == "explicit_deny_current"
    cases.append("operator_cli_preview_grant_deny_consume")
    (ROOT / "evidence" / "conflict_matrix_snapshot.json").write_text(json.dumps(matrix_evidence, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    result={"task":"LIFEOS-P3-065","pass":len(cases),"fail":0,"p0":0,"p1":0,"p2":0,"unknown":0,"not_implemented":0,"cases":cases,"scope":"synthetic SQLite only; no network/Tauri/IPC/real paths/Vault/external action"}
    (ROOT / "evidence" / "test_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
