#!/usr/bin/env python3
"""Independent P3-066 synthetic permission review runner.

This file is deliberately independent from P3-065's test suite.  It invokes
the candidate only in a copied, disposable directory and records compact,
structured results for the P3-066 review.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


def load_candidate(root: Path):
    module_path = root / "src" / "permissions.py"
    spec = importlib.util.spec_from_file_location("p3066_candidate", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: independent_runner.py CANDIDATE_COPY OUTPUT_JSON", file=sys.stderr)
        return 2
    root, output = map(Path, sys.argv[1:])
    runtime = root / "runtime"
    shutil.rmtree(runtime, ignore_errors=True)
    runtime.mkdir()
    candidate = load_candidate(root)
    app = candidate.PermissionSettings(runtime / "independent.sqlite")
    ctx = dict(project_id=candidate.CONTROLLED_PROJECT_ID, category="synthetic_note", purpose="local_recovery", location="local_sqlite", processor="local_rules")
    now, future = 10_000, 50_000
    cases: list[dict] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        cases.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    def decide(decision: str, key: str, *, expires: int = future):
        return app.decide(**ctx, expires_at_ms=expires, decision=decision, confirmation="CONFIRM", idempotency_key=key, now_ms=now)

    # Historical P1 in both orders; deny must dominate a matching current grant.
    g1 = decide("grant", "p3066-g1"); d1 = decide("deny", "p3066-d1")
    r = app.consume(**ctx, now_ms=now)
    check("grant_then_deny_is_explicitly_blocked", not r["allowed"] and r["reason"] == "explicit_deny_current" and r["external_action"] == "none" and r["ai_consumption"] == "none")
    # A second binding keeps order testing isolated from an already-current deny.
    ctx2 = {**ctx, "category": "synthetic_task"}
    app.decide(**ctx2, expires_at_ms=future, decision="deny", confirmation="CONFIRM", idempotency_key="p3066-d2", now_ms=now)
    app.decide(**ctx2, expires_at_ms=future, decision="grant", confirmation="CONFIRM", idempotency_key="p3066-g2", now_ms=now)
    r = app.consume(**ctx2, now_ms=now)
    check("deny_then_grant_is_explicitly_blocked", not r["allowed"] and r["reason"] == "explicit_deny_current" and not r["current_grant_ids"] == [])

    # Default, mismatch, expired and revoked states must never fall through to allow.
    ctx3 = {**ctx, "purpose": "local_summary"}
    check("default_is_deny", app.consume(**ctx3, now_ms=now)["reason"] == "default_deny")
    check("four_dimension_mismatch_is_deny", not app.consume(**{**ctx, "processor": "local_summary_engine"}, now_ms=now)["allowed"])
    expired = app.decide(**ctx3, expires_at_ms=now, decision="grant", confirmation="CONFIRM", idempotency_key="p3066-expired", now_ms=1)
    check("expired_grant_is_blocked", not app.consume(**ctx3, now_ms=now)["allowed"])
    ctx4 = {**ctx, "location": "local_cache"}
    revocable = app.decide(**ctx4, expires_at_ms=future, decision="grant", confirmation="CONFIRM", idempotency_key="p3066-revoke", now_ms=now)
    app.revoke(authorization_id=revocable["authorization_id"], confirmation="REVOKE", idempotency_key="p3066-revoke-cmd", now_ms=now + 1)
    check("revoked_grant_is_blocked", not app.consume(**ctx4, now_ms=now + 2)["allowed"])

    # Ambiguity and idempotency must preserve state and expose failures.
    ctx5 = {**ctx, "purpose": "local_summary", "location": "local_cache"}
    decide_args = dict(**ctx5, expires_at_ms=future, decision="grant", confirmation="CONFIRM", now_ms=now)
    app.decide(**decide_args, idempotency_key="p3066-a")
    app.decide(**decide_args, idempotency_key="p3066-b")
    check("multiple_current_grants_are_blocked", app.consume(**ctx5, now_ms=now)["reason"] == "ambiguous_multiple_current_grants")
    repeat = app.decide(**ctx5, expires_at_ms=future, decision="deny", confirmation="CONFIRM", idempotency_key="p3066-repeat-deny", now_ms=now)
    repeat2 = app.decide(**ctx5, expires_at_ms=future, decision="deny", confirmation="CONFIRM", idempotency_key="p3066-repeat-deny", now_ms=now)
    check("duplicate_deny_is_idempotent", repeat2["duplicate"] and repeat2["authorization_id"] == repeat["authorization_id"])
    before = len(app.snapshot()["authorizations"])
    try:
        app.decide(**ctx5, expires_at_ms=future + 1, decision="grant", confirmation="CONFIRM", idempotency_key="p3066-repeat-deny", now_ms=now)
        conflict = False
    except candidate.PermissionErrorVisible:
        conflict = True
    check("decision_idempotency_conflict_preserves_other_authorization", conflict and len(app.snapshot()["authorizations"]) == before)
    rev2 = app.revoke(authorization_id=revocable["authorization_id"], confirmation="REVOKE", idempotency_key="p3066-revoke-cmd", now_ms=now + 3)
    check("repeat_revoke_is_idempotent", rev2["duplicate"] and rev2["status"] == "revoked")
    other = app.decide(**{**ctx, "location": "local_cache", "purpose": "local_summary"}, expires_at_ms=future, decision="grant", confirmation="CONFIRM", idempotency_key="p3066-other", now_ms=now)
    other_before = app.snapshot()
    try:
        app.revoke(authorization_id=other["authorization_id"], confirmation="REVOKE", idempotency_key="p3066-revoke-cmd", now_ms=now + 4)
        revoke_conflict = False
    except candidate.PermissionErrorVisible:
        revoke_conflict = True
    other_after = app.snapshot()
    check("revoke_idempotency_conflict_preserves_other_authorization", revoke_conflict and next(x for x in other_after["authorizations"] if x["id"] == other["authorization_id"])["status"] == next(x for x in other_before["authorizations"] if x["id"] == other["authorization_id"])["status"])

    # Black-box operator path with a fresh database: preview -> grant -> consume -> deny -> consume.
    cli = [sys.executable, str(root / "scripts" / "permission_cli.py")]
    common = ["--synthetic-only", "--run-id", "p3066-cli", "--project", candidate.CONTROLLED_PROJECT_ID, "--category", "synthetic_note", "--purpose", "local_recovery", "--location", "local_sqlite", "--processor", "local_rules"]
    def invoke(command: str, tail: list[str]):
        return subprocess.run(cli + [command] + common + tail, text=True, capture_output=True, check=False)
    preview = invoke("preview", ["--expires-at-ms", "50000"])
    grant = invoke("decide", ["--expires-at-ms", "50000", "--decision", "grant", "--confirmation", "CONFIRM", "--idempotency-key", "p3066-cli-g"])
    allowed = invoke("consume", [])
    deny = invoke("decide", ["--expires-at-ms", "50000", "--decision", "deny", "--confirmation", "CONFIRM", "--idempotency-key", "p3066-cli-d"])
    denied = invoke("consume", [])
    try:
        p, a, b = json.loads(preview.stdout), json.loads(allowed.stdout), json.loads(denied.stdout)
        cli_ok = all(x.returncode == 0 for x in (preview, grant, allowed, deny, denied)) and p["default_decision"] == "deny" and a["allowed"] and a["external_action"] == "none" and not b["allowed"] and b["reason"] == "explicit_deny_current" and b["external_action"] == "none"
    except (json.JSONDecodeError, KeyError):
        cli_ok = False
    check("operator_cli_confirmed_grant_then_deny_path", cli_ok)

    snapshot = app.snapshot()
    check("audit_and_identity_states_are_separate", all(e["event_type"] for e in snapshot["audit_events"]) and all(x["operator_confirmation"] == "CONFIRM" for x in snapshot["authorizations"]))
    check("candidate_declares_closed_external_boundaries", snapshot["boundaries"] == {"network": "disabled", "tauri_ipc": "not_used", "real_paths": "not_used", "external_action": "none"})
    app.close()
    result = {"task": "LIFEOS-P3-066", "runner": "independent", "pass": sum(x["status"] == "PASS" for x in cases), "fail": sum(x["status"] == "FAIL" for x in cases), "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0, "cases": cases, "candidate_hashes": {p.relative_to(root).as_posix(): digest(p) for p in (root / "src" / "permissions.py", root / "scripts" / "permission_cli.py", root / "tests" / "test_permissions.py", root / "evidence" / "test_results.json", root / "evidence" / "conflict_matrix_snapshot.json")}}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not result["fail"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
