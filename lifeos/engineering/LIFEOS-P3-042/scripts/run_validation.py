#!/usr/bin/env python3
"""P3-042 synthetic SQLite remediation and regression harness.

Uses only in-memory SQLite and task-local disposable SQLite files. P3-040 is
replayed in a temporary project tree so its original evidence remains intact.
"""

import hashlib
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
PROJECT = TASK.parents[1]
CANDIDATE = PROJECT / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
SNAPSHOT = TASK / "input/001_candidate_schema.sql"
EVIDENCE = TASK / "evidence"
WORK = TASK / "work"
NOW = 1786550400000
STABLE_ERROR = "active_authorization_security_envelope_immutable"
RESULTS = []
INTEGRITY = []
ACCESSED = []

P3_041_FILES = {
    "MANIFEST.md": "3323903061e68e393dfe8512f0b49ddcd9fb947b65a7aef69deeee4692069623",
    "counter_example_attacks.py": "7e887e6db5f74ce7fbd69d7d77071141d3bc42cc83e54f4cb4590277d948b46c",
    "counter_example_results.json": "78c5b2aa45a3b7abe57078807528e914fc023db56deb58cc07f885c8f16f6619",
    "counter_example_results.txt": "3220a83c8731ffa5c761382a31e39bddd1d24d3668e201b45bdd67f314b89211",
    "candidate_schema.sql": "50d25371865b6a153267042c68290bbb00baca12a9b43d2821bd8c3a2a93cf7c",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup_base(conn):
    conn.execute("INSERT INTO project VALUES ('p1','P','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO project VALUES ('p2','P2','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES ('s1','synthetic','K','L','available','allowed',1,?,?)", (NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES ('a1','s1',NULL,'note','active',1,?,?)", (NOW, NOW))


def parent(conn, aid="auth1", logical="logical1", version=1, supersedes=None,
           status="proposed", grantor="actor", processor="local", purpose="test",
           location="device", valid_from=NOW, expires_mode="at",
           expires_at=NOW + 100000, policy_version="policy-v1"):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, logical, grantor, processor, purpose, location, status, version, 1,
         valid_from, expires_mode, expires_at, None, policy_version, supersedes, NOW, NOW),
    )


def policy(conn, aid="auth1"):
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )


def configure(conn, aid="auth1"):
    conn.execute("INSERT INTO authorization_scope VALUES (?,?, 'allow','p1',NULL,NULL)", (aid + "-scope", aid))
    conn.execute("INSERT INTO authorization_action VALUES (?,?, 'read')", (aid + "-action", aid))
    policy(conn, aid)


def setup_active(conn, aid="auth1", logical="logical1", **fields):
    setup_base(conn)
    parent(conn, aid=aid, logical=logical, **fields)
    configure(conn, aid)
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (aid,))
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 (aid + "-activate", "authorization.activate", "actor", aid, 1, "ok", NOW, aid + "-corr"))
    conn.commit()


def retirement_evidence(conn, status, aid="auth1", generation=2):
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire",
              "superseded": "authorization.supersede"}[status]
    correlation = "authorization-state:%s:%d:%s" % (aid, generation, status)
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 ("audit-" + status, action, "actor", aid, 1, "ok", NOW, correlation))
    conn.execute("INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 ("job-" + status, "authorization_state_change", "authorization", aid,
                  generation, status, "pending", 0, NOW, None, 0, None, correlation, None))


def fresh(mode, case_id):
    if mode == "memory":
        db_path = ":memory:"
    else:
        db_file = WORK / (case_id.replace("/", "_") + ".db")
        db_file.unlink(missing_ok=True)
        db_path = str(db_file)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    ACCESSED.append(db_path)
    return conn


def check_file(conn, case_id):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
    passed = integrity == "ok" and quick == "ok" and not foreign
    INTEGRITY.append({"case": case_id, "integrity_check": integrity,
                      "quick_check": quick, "foreign_key_check": foreign, "passed": passed})
    return passed


def rejected_case(name, operation, setup=setup_active, severity="P1", error=STABLE_ERROR,
                  verify=None, group="ENVELOPE"):
    for mode in ("memory", "file"):
        case_id = "%s/%s/%s" % (group, name, mode)
        conn = fresh(mode, case_id)
        status, detail, sqlite_error = "FAIL", "operation unexpectedly succeeded", None
        try:
            setup(conn)
            before = conn.total_changes
            operation(conn)
            conn.commit()
            if verify:
                verify(conn, False)
            detail += "; changes=%d" % (conn.total_changes - before)
        except sqlite3.DatabaseError as exc:
            sqlite_error = str(exc)
            conn.rollback()
            if error in sqlite_error:
                status, detail = "PASS", "operation rejected with stable contract error"
                if verify:
                    verify(conn, True)
            else:
                detail = "unexpected SQLite error"
        except AssertionError as exc:
            detail = str(exc)
        if mode == "file" and not check_file(conn, case_id):
            status, detail = "FAIL", "file database integrity/FK check failed"
        conn.close()
        RESULTS.append({"group": group, "name": name, "mode": mode, "severity": severity,
                        "status": status, "detail": detail, "sqlite_error": sqlite_error})


def legal_case(name, operation, setup=setup_active, verify=None, severity="P2", group="LEGAL"):
    for mode in ("memory", "file"):
        case_id = "%s/%s/%s" % (group, name, mode)
        conn = fresh(mode, case_id)
        status, detail, sqlite_error = "FAIL", "legal operation failed", None
        try:
            setup(conn)
            operation(conn)
            conn.commit()
            if verify:
                verify(conn)
            status, detail = "PASS", "legal operation succeeded"
        except (sqlite3.DatabaseError, AssertionError) as exc:
            sqlite_error = str(exc) if isinstance(exc, sqlite3.DatabaseError) else None
            detail = str(exc)
        if mode == "file" and not check_file(conn, case_id):
            status, detail = "FAIL", "file database integrity/FK check failed"
        conn.close()
        RESULTS.append({"group": group, "name": name, "mode": mode, "severity": severity,
                        "status": status, "detail": detail, "sqlite_error": sqlite_error})


def limitation_case(name, operation, setup=setup_active, verify=None, group="KNOWN-R0048-R0049"):
    for mode in ("memory", "file"):
        case_id = "%s/%s/%s" % (group, name, mode)
        conn = fresh(mode, case_id)
        status, detail, sqlite_error = "UNKNOWN", "observation did not execute", None
        try:
            setup(conn)
            operation(conn)
            conn.commit()
            if verify:
                verify(conn)
            status, detail = "KNOWN_LIMITATION", "known non-range behavior reproduced"
        except (sqlite3.DatabaseError, AssertionError) as exc:
            sqlite_error = str(exc) if isinstance(exc, sqlite3.DatabaseError) else None
            detail = "known-limitation reproduction changed: " + str(exc)
        if mode == "file" and not check_file(conn, case_id):
            status, detail = "FAIL", "file database integrity/FK check failed"
        conn.close()
        RESULTS.append({"group": group, "name": name, "mode": mode, "severity": "P2",
                        "status": status, "detail": detail, "sqlite_error": sqlite_error})


def run_envelope_cases():
    assignments = {
        "update_processor_active": "processor='external-cloud'",
        "update_purpose_active": "purpose='production'",
        "update_location_active": "location='remote'",
        "update_grantor_active": "grantor_ref='evil-actor'",
        "update_expiry_to_indefinite_active": "expires_mode='indefinite',expires_at_ms=NULL",
        "update_policy_version_active": "policy_version='policy-v2'",
        "compound_field_update_active": "processor='external-cloud',purpose='production'",
        "update_valid_from_active": "valid_from_ms=valid_from_ms+1",
        "update_expires_at_active": "expires_at_ms=expires_at_ms+1",
        "expires_indefinite_to_at_active": "expires_mode='at',expires_at_ms=%d" % (NOW + 200000),
        "expires_null_to_value_active": "expires_at_ms=%d" % (NOW + 200000),
    }
    for name, assignment in assignments.items():
        if name == "expires_indefinite_to_at_active":
            setup = lambda c: setup_active(c, expires_mode="indefinite", expires_at=None)
        elif name == "expires_null_to_value_active":
            setup = lambda c: setup_active(c, expires_mode="indefinite", expires_at=None)
        else:
            setup = setup_active
        rejected_case(name, lambda c, a=assignment: c.execute(
            "UPDATE authorization SET %s WHERE id='auth1'" % a), setup=setup)

    def compound_retire(c):
        retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2,processor='changed' WHERE id='auth1'")
    rejected_case("compound_retirement_and_envelope_update", compound_retire)

    def setup_two(c):
        setup_active(c)
        parent(c, aid="auth2", logical="logical2")
        configure(c, "auth2")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        c.commit()
    def verify_two(c, rejected):
        rows = [row[0] for row in c.execute("SELECT processor FROM authorization WHERE id IN ('auth1','auth2') ORDER BY id")]
        assert rows == ["local", "local"], "multi-row UPDATE was not atomic"
    rejected_case("multirow_active_parent_update_atomic", lambda c: c.execute(
        "UPDATE authorization SET processor='external-cloud' WHERE status='active'"), setup=setup_two, verify=verify_two)


def run_legal_cases():
    legal_case("noop_security_envelope", lambda c: c.execute(
        "UPDATE authorization SET grantor_ref=grantor_ref,processor=processor,purpose=purpose,"
        "location=location,valid_from_ms=valid_from_ms,expires_mode=expires_mode,"
        "expires_at_ms=expires_at_ms,policy_version=policy_version WHERE id='auth1'"))
    legal_case("updated_at_only", lambda c: c.execute(
        "UPDATE authorization SET updated_at_ms=updated_at_ms+1 WHERE id='auth1'"))

    def setup_draft(c, status):
        setup_base(c); parent(c, status=status); configure(c); c.commit()
    for initial in ("proposed", "granted"):
        legal_case(initial + "_configure_then_activate", lambda c: c.execute(
            "UPDATE authorization SET processor='local-v2',purpose='approved',status='active' WHERE id='auth1'"),
            setup=lambda c, s=initial: setup_draft(c, s))

    for terminal in ("revoked", "expired", "superseded"):
        def retire(c, terminal=terminal):
            retirement_evidence(c, terminal)
            c.execute("UPDATE authorization SET status=?,generation=2 WHERE id='auth1'", (terminal,))
        legal_case("retire_" + terminal + "_without_envelope_change", retire)

    def successor(c):
        retirement_evidence(c, "superseded")
        c.execute("UPDATE authorization SET status='superseded',generation=2 WHERE id='auth1'")
        parent(c, aid="auth2", logical="logical1", version=2, supersedes="auth1",
               processor="local-v2", purpose="new-purpose", location="new-device",
               policy_version="policy-v2")
        configure(c, "auth2")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    legal_case("successor_version_changed_envelope", successor)


def run_adjacent_protected_cases():
    rejected_case("update_id_active", lambda c: c.execute(
        "UPDATE authorization SET id='auth-renamed' WHERE id='auth1'"), severity="P2",
        error="FOREIGN KEY constraint failed", group="ADJACENT-PROTECTED")
    for field, value in (("logical_key", "'logical-changed'"), ("version_no", "2"),
                         ("supersedes_id", "'auth1'")):
        rejected_case("update_%s_active" % field, lambda c, f=field, v=value: c.execute(
            "UPDATE authorization SET %s=%s WHERE id='auth1'" % (f, v)), severity="P2",
            error="authorization_version_identity_immutable", group="ADJACENT-PROTECTED")
    rejected_case("active_to_proposed", lambda c: c.execute(
        "UPDATE authorization SET status='proposed' WHERE id='auth1'"), severity="P2",
        error="authorization_status_transition_invalid", group="ADJACENT-PROTECTED")


def run_known_limitations():
    # R-0048: audit/outbox evidence rows and independent generation bump remain outside P3-042.
    limitation_case("preposition_fake_retirement", lambda c: retirement_evidence(c, "revoked"))
    limitation_case("delete_audit_after_retirement", lambda c: (
        retirement_evidence(c, "revoked"),
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
        c.execute("DELETE FROM audit_entry WHERE id='audit-revoked'")))
    limitation_case("delete_outbox_after_retirement", lambda c: (
        retirement_evidence(c, "revoked"),
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
        c.execute("DELETE FROM outbox_job WHERE job_type='authorization_state_change'")))
    limitation_case("update_outbox_status_after_retirement", lambda c: (
        retirement_evidence(c, "revoked"),
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
        c.execute("UPDATE outbox_job SET status='completed' WHERE job_type='authorization_state_change'")))
    limitation_case("update_audit_action_after_retirement", lambda c: (
        retirement_evidence(c, "revoked"),
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
        c.execute("UPDATE audit_entry SET action_code='authorization.expire' WHERE id='audit-revoked'")))
    limitation_case("increase_generation_active", lambda c: c.execute(
        "UPDATE authorization SET generation=generation+1 WHERE id='auth1'"))
    limitation_case("bump_then_retire_with_prepositioned_evidence", lambda c: (
        retirement_evidence(c, "revoked", generation=3),
        c.execute("UPDATE authorization SET generation=2 WHERE id='auth1'"),
        c.execute("UPDATE authorization SET status='revoked',generation=3 WHERE id='auth1'")))

    def terminal(c):
        setup_active(c); retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"); c.commit()
    for name, statement in (
        ("update_scope_effect_revoked", "UPDATE authorization_scope SET effect='deny' WHERE id='auth1-scope'"),
        ("insert_scope_revoked", "INSERT INTO authorization_scope VALUES ('new','auth1','allow','p2',NULL,NULL)"),
        ("update_action_value_revoked", "UPDATE authorization_action SET action='export_candidate' WHERE id='auth1-action'"),
        ("update_policy_training_revoked", "UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth1'"),
    ):
        limitation_case(name, lambda c, s=statement: c.execute(s), setup=terminal)

    # Adjacent metadata/lifecycle fields are recorded, not remediated, pending PM classification.
    limitation_case("update_created_at_active", lambda c: c.execute(
        "UPDATE authorization SET created_at_ms=created_at_ms+1 WHERE id='auth1'"), group="ADJACENT-OBSERVATION")
    limitation_case("update_revoked_at_active", lambda c: c.execute(
        "UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW,)), group="ADJACENT-OBSERVATION")


def p3_041_state():
    root = PROJECT / "reviews/LIFEOS-P3-041/evidence"
    return {name: {"expected_sha256": expected, "actual_sha256": digest(root / name),
                   "unchanged": digest(root / name) == expected}
            for name, expected in P3_041_FILES.items()}


def run_p3_031():
    command = ["sh", str(PROJECT / "engineering/LIFEOS-P3-031/scripts/run_validation.sh")]
    result = subprocess.run(command, cwd=PROJECT.parent, text=True, capture_output=True)
    (EVIDENCE / "regressions/p3_031_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-031/evidence/test_results.json",
                    EVIDENCE / "regressions/p3_031_test_results.json")
    return result.returncode


def run_p3_040_isolated():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-042-") as temp:
        root = Path(temp) / "lifeos"
        p3040 = root / "engineering/LIFEOS-P3-040"
        p3031 = root / "engineering/LIFEOS-P3-031/migrations"
        p3039 = root / "reviews/LIFEOS-P3-039/evidence"
        for path in (p3040 / "scripts", p3040 / "input", p3040 / "evidence/checks",
                     p3040 / "evidence/input", p3040 / "work", p3031, p3039):
            path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-040/scripts/run_validation.py",
                        p3040 / "scripts/run_validation.py")
        shutil.copyfile(CANDIDATE, p3031 / "001_candidate_schema.sql")
        for name in ("MANIFEST.md", "counter_example_attacks.py", "counter_example_results.json",
                     "counter_example_results.txt", "candidate_schema.sql"):
            shutil.copyfile(PROJECT / "reviews/LIFEOS-P3-039/evidence" / name, p3039 / name)
        result = subprocess.run([sys.executable, str(p3040 / "scripts/run_validation.py")],
                                cwd=Path(temp), text=True, capture_output=True)
        (EVIDENCE / "regressions/p3_040_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        for source, target in (
            ("test_results.json", "p3_040_test_results.json"),
            ("environment.json", "p3_040_environment.json"),
            ("checks/integrity_and_fk.json", "p3_040_integrity_and_fk.json"),
            ("input/source_hashes.json", "p3_040_source_hashes.json"),
            ("input/p3_039_evidence_preservation.json", "p3_040_p3_039_preservation.json"),
        ):
            shutil.copyfile(p3040 / "evidence" / source, EVIDENCE / "regressions" / target)
        return result.returncode


def write_evidence(p3031_exit, p3040_exit, preservation):
    states = ("PASS", "FAIL", "KNOWN_LIMITATION", "NOT_IMPLEMENTED", "UNKNOWN")
    summary = {}
    for severity in ("P0", "P1", "P2"):
        rows = [r for r in RESULTS if r["severity"] == severity]
        summary[severity] = {state: sum(r["status"] == state for r in rows) for state in states}
    summary["total"] = {state: sum(r["status"] == state for r in RESULTS) for state in states}
    payload = {"task_id": "LIFEOS-P3-042", "route": "gpt-5.6-sol+xhigh",
               "scope": "synthetic in-memory and task-local file SQLite only",
               "summary": summary, "results": RESULTS,
               "regressions": {"p3_031_exit": p3031_exit, "p3_040_isolated_exit": p3040_exit}}
    (EVIDENCE / "test_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(
        json.dumps({"all_passed": all(r["passed"] for r in INTEGRITY), "results": INTEGRITY}, indent=2) + "\n",
        encoding="utf-8")
    (EVIDENCE / "environment.json").write_text(json.dumps({
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "platform": platform.platform(), "machine": platform.machine(),
        "network_used": False, "real_db_vault_tauri_ipc_used": False,
        "executed_real_migration": False, "accessed_databases": ACCESSED,
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/p3_041_evidence_preservation.json").write_text(
        json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    hashes = {"candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
              "runner": digest(Path(__file__)),
              "p3_031_contract_tests": digest(PROJECT / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py"),
              "p3_040_original_runner": digest(PROJECT / "engineering/LIFEOS-P3-040/scripts/run_validation.py")}
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    for path in (EVIDENCE / "checks", EVIDENCE / "input", EVIDENCE / "regressions", WORK, SNAPSHOT.parent):
        path.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    before = p3_041_state()
    if not all(row["unchanged"] for row in before.values()):
        print("P3-041 baseline hash mismatch before test", file=sys.stderr)
        return 2
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    p3031_exit = run_p3_031()
    p3040_exit = run_p3_040_isolated()
    run_envelope_cases()
    run_legal_cases()
    run_adjacent_protected_cases()
    run_known_limitations()
    after = p3_041_state()
    preservation = {name: {"before": before[name]["actual_sha256"],
                           "after": after[name]["actual_sha256"],
                           "expected_sha256": P3_041_FILES[name],
                           "unchanged": before[name]["unchanged"] and after[name]["unchanged"] and
                                        before[name]["actual_sha256"] == after[name]["actual_sha256"]}
                    for name in P3_041_FILES}
    summary = write_evidence(p3031_exit, p3040_exit, preservation)
    for result in RESULTS:
        print("%-24s %-46s %-6s %-2s %s" %
              (result["group"], result["name"], result["mode"], result["severity"], result["status"]))
    print("SUMMARY " + json.dumps(summary, sort_keys=True))
    print("P3_031_EXIT", p3031_exit)
    print("P3_040_ISOLATED_EXIT", p3040_exit)
    print("P3_041_EVIDENCE_PRESERVED", all(row["unchanged"] for row in preservation.values()))
    bad = p3031_exit != 0 or p3040_exit != 0 or not all(row["passed"] for row in INTEGRITY)
    bad = bad or not all(row["unchanged"] for row in preservation.values())
    bad = bad or any(r["severity"] in ("P0", "P1") and r["status"] != "PASS" for r in RESULTS)
    bad = bad or any(r["status"] in ("FAIL", "NOT_IMPLEMENTED", "UNKNOWN") for r in RESULTS)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
