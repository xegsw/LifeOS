#!/usr/bin/env python3
"""Fresh P3-057 independent synthetic SQLite review runner.

This runner is intentionally self-contained.  It neither imports nor invokes
P3-044 code and was written after the sealed P3-057 attack plan.  It accepts
only a schema path, creates new synthetic databases, and writes results only
to the output path supplied by this review.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


NOW = 1786550400000
ACTIVE = "active_authorization_replace_forbidden"


class CheckFailure(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expect_abort(conn, statement, expected, params=()):
    try:
        conn.execute(statement, params)
    except sqlite3.DatabaseError as exc:
        detail = str(exc)
        require(expected in detail, "expected %r, got %r" % (expected, detail))
        return detail
    raise CheckFailure("statement unexpectedly succeeded: %s" % statement)


def parent_values(auth_id="auth1", logical_key="logical1", version_no=1,
                  status="proposed", supersedes_id=None, expires_mode="indefinite",
                  expires_at_ms=None):
    return (
        auth_id, logical_key, "actor:user", "local", "review", "device", status,
        version_no, 1, NOW, expires_mode, expires_at_ms, None, "policy@1",
        supersedes_id, NOW, NOW,
    )


def insert_parent(conn, **kwargs):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        parent_values(**kwargs),
    )


def add_project(conn, project_id="p1"):
    conn.execute(
        "INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        (project_id, "Synthetic project", "P3-057", "active", 1, NOW, NOW, NOW),
    )


def add_policy(conn, auth_id):
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (auth_id, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )


def add_children(conn, auth_id):
    conn.execute(
        "INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        (auth_id + ":scope", auth_id, "allow", "p1", None, None),
    )
    conn.execute(
        "INSERT INTO authorization_action VALUES (?,?,?)",
        (auth_id + ":action", auth_id, "read"),
    )
    add_policy(conn, auth_id)


def add_active(conn, auth_id="auth1", logical_key="logical1", version_no=1,
               supersedes_id=None, expires_mode="indefinite", expires_at_ms=None):
    insert_parent(
        conn,
        auth_id=auth_id,
        logical_key=logical_key,
        version_no=version_no,
        supersedes_id=supersedes_id,
        expires_mode=expires_mode,
        expires_at_ms=expires_at_ms,
    )
    add_children(conn, auth_id)
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (auth_id,))


def snapshot(conn):
    tables = ("authorization_scope", "authorization_action", "authorization_policy")
    return {
        "parents": [
            tuple(row) for row in conn.execute(
                "SELECT id,logical_key,status,version_no,generation,grantor_ref,processor,"
                "purpose,location,valid_from_ms,expires_mode,expires_at_ms,policy_version,"
                "supersedes_id,created_at_ms,updated_at_ms FROM authorization ORDER BY id"
            )
        ],
        "children": {
            table: [tuple(row) for row in conn.execute("SELECT * FROM %s ORDER BY 1" % table)]
            for table in tables
        },
        "audit": [tuple(row) for row in conn.execute("SELECT * FROM audit_entry ORDER BY id")],
        "outbox": [tuple(row) for row in conn.execute("SELECT * FROM outbox_job ORDER BY id")],
    }


def open_case(schema, directory, config, label):
    if config["storage"] == "memory":
        target = ":memory:"
        file_path = None
    else:
        file_path = directory / (label + ".sqlite")
        target = str(file_path)
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(schema.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%d" % int(config["foreign_keys"]))
    conn.execute("PRAGMA recursive_triggers=%d" % int(config["recursive_triggers"]))
    require(conn.execute("PRAGMA foreign_keys").fetchone()[0] == int(config["foreign_keys"]),
            "foreign_keys pragma was not applied")
    require(conn.execute("PRAGMA recursive_triggers").fetchone()[0] == int(config["recursive_triggers"]),
            "recursive_triggers pragma was not applied")
    add_project(conn)
    return conn, file_path


def finish_case(conn, file_path):
    conn.commit()
    conn.close()
    if file_path is None:
        return {"storage_check": "not_applicable"}
    reopened = sqlite3.connect(str(file_path))
    integrity = [row[0] for row in reopened.execute("PRAGMA integrity_check")]
    quick = [row[0] for row in reopened.execute("PRAGMA quick_check")]
    fk = [tuple(row) for row in reopened.execute("PRAGMA foreign_key_check")]
    reopened.close()
    require(integrity == ["ok"], "integrity_check failed: %r" % integrity)
    require(quick == ["ok"], "quick_check failed: %r" % quick)
    require(not fk, "foreign_key_check returned rows: %r" % fk)
    return {"integrity_check": integrity, "quick_check": quick, "foreign_key_check": fk}


def active_baseline(conn, **kwargs):
    add_active(conn, **kwargs)
    conn.commit()


def assert_rejected_unchanged(conn, statement, error, params=()):
    before = snapshot(conn)
    detail = expect_abort(conn, statement, error, params)
    conn.rollback()
    require(snapshot(conn) == before, "rejected write altered the safety snapshot")
    return detail


def conflict_row(auth_id="auth1", logical_key="logical1", status="granted"):
    return parent_values(
        auth_id=auth_id,
        logical_key=logical_key,
        status=status,
        expires_mode="at",
        expires_at_ms=NOW + 60000,
    )[:-4] + ("policy@attacker", None, NOW, NOW)


def attack_replace_same_id(conn):
    active_baseline(conn)
    assert_rejected_unchanged(
        conn, "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ACTIVE, conflict_row(),
    )


def attack_replace_version_key(conn):
    active_baseline(conn)
    assert_rejected_unchanged(
        conn, "REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ACTIVE, conflict_row(auth_id="substitute", logical_key="logical1"),
    )


def attack_replace_both_keys(conn):
    active_baseline(conn)
    assert_rejected_unchanged(
        conn, "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ACTIVE, conflict_row(status="active"),
    )


def attack_upsert_id(conn):
    active_baseline(conn)
    statement = (
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET processor=excluded.processor,"
        "policy_version=excluded.policy_version,status=excluded.status"
    )
    assert_rejected_unchanged(conn, statement, ACTIVE, conflict_row())


def attack_upsert_version(conn):
    active_baseline(conn)
    statement = (
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(logical_key,version_no) DO UPDATE SET purpose=excluded.purpose,"
        "location=excluded.location,status=excluded.status"
    )
    assert_rejected_unchanged(
        conn, statement, ACTIVE, conflict_row(auth_id="other-id", logical_key="logical1")
    )


def attack_upsert_do_nothing(conn):
    active_baseline(conn)
    statement = (
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(id) DO NOTHING"
    )
    assert_rejected_unchanged(conn, statement, ACTIVE, conflict_row())


def attack_plain_duplicate(conn):
    active_baseline(conn)
    assert_rejected_unchanged(
        conn, "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ACTIVE, conflict_row(),
    )


def attack_delete_rebuild(conn):
    active_baseline(conn)
    before = snapshot(conn)
    expect_abort(conn, "DELETE FROM authorization WHERE id='auth1'", "active_authorization_delete_forbidden")
    conn.rollback()
    require(snapshot(conn) == before, "delete phase altered active authorization")
    require(conn.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()[0] == "active",
            "rebuild insertion became reachable")


def attack_parent_envelope(conn, assignment, expires_fixture=False):
    if expires_fixture:
        active_baseline(conn, expires_mode="at", expires_at_ms=NOW + 60000)
    else:
        active_baseline(conn)
    assert_rejected_unchanged(
        conn, "UPDATE authorization SET %s WHERE id='auth1'" % assignment,
        "active_authorization_security_envelope_immutable",
    )


def attack_parent_multi_row(conn):
    add_active(conn, "auth1", "logical1")
    add_active(conn, "auth2", "logical2")
    conn.commit()
    assert_rejected_unchanged(
        conn, "UPDATE authorization SET processor='bulk-rewrite' WHERE status='active'",
        "active_authorization_security_envelope_immutable",
    )


def child_inactive_parent(conn, child_table):
    add_active(conn)
    insert_parent(conn, auth_id="inactive", logical_key="inactive-logical")
    if child_table == "authorization_scope":
        conn.execute("INSERT INTO authorization_scope VALUES ('inactive:scope','inactive','allow','p1',NULL,NULL)")
    elif child_table == "authorization_action":
        conn.execute("INSERT INTO authorization_action VALUES ('inactive:action','inactive','read')")
    else:
        add_policy(conn, "inactive")
    conn.commit()


def attack_child_insert(conn, table):
    active_baseline(conn)
    statements = {
        "authorization_scope": "INSERT INTO authorization_scope VALUES ('new:scope','auth1','deny','p1',NULL,NULL)",
        "authorization_action": "INSERT INTO authorization_action VALUES ('new:action','auth1','export_candidate')",
        "authorization_policy": "INSERT INTO authorization_policy VALUES ('auth1','none',NULL,4,1,1,'[]','[]','[]','[]',9,9)",
    }
    assert_rejected_unchanged(conn, statements[table], "active_%s_insert_forbidden" % table)


def attack_child_update(conn, table):
    active_baseline(conn)
    statements = {
        "authorization_scope": "UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'",
        "authorization_action": "UPDATE authorization_action SET action='export_candidate' WHERE authorization_id='auth1'",
        "authorization_policy": "UPDATE authorization_policy SET external_send_allowed=1 WHERE authorization_id='auth1'",
    }
    assert_rejected_unchanged(conn, statements[table], "active_%s_update_forbidden" % table)


def attack_child_delete(conn, table):
    active_baseline(conn)
    assert_rejected_unchanged(
        conn, "DELETE FROM %s WHERE authorization_id='auth1'" % table,
        "active_%s_delete_forbidden" % table,
    )


def attack_child_replace(conn, table):
    active_baseline(conn)
    statements = {
        "authorization_scope": "INSERT OR REPLACE INTO authorization_scope VALUES ('auth1:scope','auth1','deny','p1',NULL,NULL)",
        "authorization_action": "INSERT OR REPLACE INTO authorization_action VALUES ('auth1:action','auth1','export_candidate')",
        "authorization_policy": "INSERT OR REPLACE INTO authorization_policy VALUES ('auth1','none',NULL,4,1,1,'[]','[]','[]','[]',9,9)",
    }
    assert_rejected_unchanged(conn, statements[table], "active_%s_insert_forbidden" % table)


def attack_child_rebind_from_active(conn, table):
    child_inactive_parent(conn, table)
    keys = {
        "authorization_scope": ("id", "auth1:scope"),
        "authorization_action": ("id", "auth1:action"),
        "authorization_policy": ("authorization_id", "auth1"),
    }
    column, value = keys[table]
    assert_rejected_unchanged(
        conn, "UPDATE %s SET authorization_id='inactive' WHERE %s=?" % (table, column),
        "active_%s_update_forbidden" % table, (value,),
    )


def attack_child_rebind_into_active(conn, table):
    child_inactive_parent(conn, table)
    keys = {
        "authorization_scope": ("id", "inactive:scope"),
        "authorization_action": ("id", "inactive:action"),
        "authorization_policy": ("authorization_id", "inactive"),
    }
    column, value = keys[table]
    assert_rejected_unchanged(
        conn, "UPDATE %s SET authorization_id='auth1' WHERE %s=?" % (table, column),
        "active_%s_update_forbidden" % table, (value,),
    )


def attack_child_multi_row(conn):
    add_active(conn, "auth1", "logical1")
    add_active(conn, "auth2", "logical2")
    conn.commit()
    assert_rejected_unchanged(
        conn, "UPDATE authorization_scope SET effect='deny' WHERE authorization_id IN ('auth1','auth2')",
        "active_authorization_scope_update_forbidden",
    )
    assert_rejected_unchanged(
        conn,
        "INSERT INTO authorization_action(id,authorization_id,action) "
        "SELECT 'bulk:' || id,id,'export_candidate' FROM authorization WHERE status='active'",
        "active_authorization_action_insert_forbidden",
    )


def transaction_rollback(conn):
    active_baseline(conn)
    before = snapshot(conn)
    conn.execute("BEGIN")
    conn.execute(
        "INSERT INTO audit_entry VALUES ('audit:transient','test','actor:user','auth1',1,'ok',?,'transient')",
        (NOW,),
    )
    expect_abort(conn, "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 ACTIVE, conflict_row())
    conn.rollback()
    require(snapshot(conn) == before, "transaction rollback left evidence or parent mutation")


def savepoint_recovery(conn):
    active_baseline(conn)
    before = snapshot(conn)
    conn.execute("BEGIN")
    conn.execute("SAVEPOINT parent_child_guard")
    expect_abort(conn, "DELETE FROM authorization_scope WHERE authorization_id='auth1'",
                 "active_authorization_scope_delete_forbidden")
    conn.execute("ROLLBACK TO parent_child_guard")
    conn.execute("RELEASE parent_child_guard")
    require(snapshot(conn) == before, "savepoint rollback left active mutation")
    insert_parent(conn, auth_id="post-savepoint", logical_key="post-savepoint")
    conn.commit()
    require(conn.execute("SELECT status FROM authorization WHERE id='post-savepoint'").fetchone()[0] == "proposed",
            "connection unusable after savepoint recovery")


def retire_superseded(conn, auth_id):
    row = conn.execute("SELECT generation FROM authorization WHERE id=?", (auth_id,)).fetchone()
    require(row is not None and row[0] == 1, "unexpected successor fixture generation")
    token = "%s:2:superseded" % auth_id
    idem = "idem:" + token
    request_hash = "sha256:" + hashlib.sha256(
        ("authorization-lifecycle:" + token).encode("utf-8")
    ).hexdigest()
    conn.execute(
        "INSERT INTO submission VALUES ('destruct@1',?,?,?,?,NULL,?)",
        (idem, request_hash, "supersede_authorization", auth_id, NOW),
    )
    conn.execute(
        "INSERT INTO authorization_lifecycle_command("
        "id,idempotency_key,authorization_id,expected_generation,target_status,"
        "scoped_actor_claim,canonical_request_hash,requested_at_ms) VALUES (?,?,?,?,?,?,?,?)",
        ("cmd:" + token, idem, auth_id, 1, "superseded", "actor:user", request_hash, NOW),
    )


def legal_paths(conn):
    # A newly created proposed record can be configured, granted, then activated.
    insert_parent(conn, auth_id="candidate", logical_key="candidate")
    add_children(conn, "candidate")
    conn.execute("UPDATE authorization SET status='granted' WHERE id='candidate'")
    conn.execute("UPDATE authorization SET status='active' WHERE id='candidate'")
    require(conn.execute("SELECT status FROM authorization WHERE id='candidate'").fetchone()[0] == "active",
            "legal proposed/granted/active path regressed")

    # A distinct active version can retire through its bound lifecycle command;
    # its proper successor has a new id, version, and supersedes link.
    add_active(conn, "old", "versioned")
    retire_superseded(conn, "old")
    require(conn.execute("SELECT status,generation FROM authorization WHERE id='old'").fetchone() == ("superseded", 2),
            "legal terminal transition regressed")
    add_active(conn, "successor", "versioned", version_no=2, supersedes_id="old")
    require(conn.execute("SELECT status,version_no,supersedes_id FROM authorization WHERE id='successor'").fetchone()
            == ("active", 2, "old"), "legal successor activation regressed")


def hash_checks(root, schema):
    expected = {
        # P3-043 original failed-review evidence.
        "lifeos/reviews/LIFEOS-P3-043/evidence/candidate_schema.sql": "ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b",
        "lifeos/reviews/LIFEOS-P3-043/evidence/counter_example_attacks.py": "400c6fcb63d3ecac76f75a54a3017a12c379055dbeec2ebcc597d9fe1c30e40a",
        "lifeos/reviews/LIFEOS-P3-043/evidence/counter_example_results.json": "a5d283fbb14e65605d83c20f5aebfee91a4cb1007893ae8ac85e4ae3a6b46d7b",
        "lifeos/reviews/LIFEOS-P3-043/evidence/counter_example_results.txt": "b6aceeb1b92f7924ace7161dc6478755f3ecc5eafcb6fc2f1842ba4d8bcde5b6",
        # P3-044 preserved snapshot and remediation evidence.
        "lifeos/engineering/LIFEOS-P3-044/input/001_candidate_schema.sql": "0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376",
        "lifeos/engineering/LIFEOS-P3-044/scripts/run_validation.py": "1e297a9eaf031776b33ee978656e9aa62e477d1b05875a6c1aa9627b532774c3",
        "lifeos/engineering/LIFEOS-P3-044/evidence/test_results.json": "857c86c8212a09f35f5fdd129acda82ca4b532269158c0c4b5c9e08a8dbe439f",
        "lifeos/engineering/LIFEOS-P3-044/evidence/test_run.log": "b0e4f76ce3af1cd447e1dfac53823fb73894f6959dd14f1afe8bdf949adc6848",
        "lifeos/engineering/LIFEOS-P3-044/evidence/environment.json": "4e851b2cb375b6049fdcda2dc301207b43f9eb6926ded83d5c1f4ddc4eca2e45",
        "lifeos/engineering/LIFEOS-P3-044/evidence/checks/integrity_and_fk.json": "46c7cb980ee3e47e7594726ef0196d45cadcdb50231a1461d814394da954fdb5",
        "lifeos/engineering/LIFEOS-P3-044/evidence/input/source_hashes.json": "cbaf6545c616892b14798255c3b818b382e566b2ae7c88d1a16ecd53ca2b5138",
        "lifeos/engineering/LIFEOS-P3-044/evidence/input/p3_043_preservation.json": "5a57b71e4d182beb2671ad141822fddea998b74d9be95f90bf4f8212e32ccaa0",
    }
    outcomes = []
    for relative, wanted in expected.items():
        actual = sha256(root / relative)
        outcomes.append({"path": relative, "expected": wanted, "actual": actual, "match": actual == wanted})
    current_hash = sha256(schema)
    return {
        "historical_assets": outcomes,
        "all_historical_hashes_match": all(item["match"] for item in outcomes),
        "current_candidate_sha256": current_hash,
        "p3_044_snapshot_sha256": expected["lifeos/engineering/LIFEOS-P3-044/input/001_candidate_schema.sql"],
        "current_differs_from_p3_044_snapshot": current_hash != expected["lifeos/engineering/LIFEOS-P3-044/input/001_candidate_schema.sql"],
        "current_matches_r0048_closed_boundary": current_hash == "bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1",
        "p3_044_pm_review_observed_sha256": sha256(root / "lifeos/reviews/LIFEOS-P3-044_pm_review.md"),
    }


def execute_case(schema, work, config, case_id, severity, func):
    label = "%s-%s-fk%d-rec%d" % (
        case_id, config["storage"], config["foreign_keys"], config["recursive_triggers"],
    )
    conn = None
    file_path = None
    result = {"id": case_id, "severity": severity, **config}
    try:
        conn, file_path = open_case(schema, work, config, label)
        func(conn)
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAIL"
        result["detail"] = "%s: %s" % (type(exc).__name__, exc)
    finally:
        if conn is not None:
            try:
                result["storage_checks"] = finish_case(conn, file_path)
            except Exception as exc:
                result["status"] = "FAIL"
                result["detail"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    schema = args.schema.resolve()
    require(schema.is_file(), "schema path does not exist")
    input_before_sha256 = sha256(schema)
    configs = [
        {"storage": storage, "foreign_keys": foreign_keys, "recursive_triggers": recursive}
        for storage in ("memory", "file")
        for foreign_keys in (False, True)
        for recursive in (False, True)
    ]
    parent_fields = [
        ("grantor_ref", "grantor_ref='actor:other'", False),
        ("processor", "processor='remote'", False),
        ("purpose", "purpose='broadened'", False),
        ("location", "location='external'", False),
        ("valid_from_ms", "valid_from_ms=0", False),
        ("expires_mode", "expires_mode='at',expires_at_ms=%d" % (NOW + 90000), False),
        ("expires_at_ms", "expires_at_ms=%d" % (NOW + 120000), True),
        ("policy_version", "policy_version='policy@attacker'", False),
    ]
    tests = [
        ("replace_same_id", "P1", attack_replace_same_id),
        ("replace_version_identity", "P1", attack_replace_version_key),
        ("replace_both_identity", "P1", attack_replace_both_keys),
        ("upsert_id_do_update", "P1", attack_upsert_id),
        ("upsert_version_do_update", "P1", attack_upsert_version),
        ("upsert_do_nothing", "P1", attack_upsert_do_nothing),
        ("plain_duplicate_insert", "P1", attack_plain_duplicate),
        ("delete_then_rebuild", "P1", attack_delete_rebuild),
        ("parent_multi_row_update", "P1", attack_parent_multi_row),
        ("children_multi_row", "P1", attack_child_multi_row),
        ("transaction_rollback", "P1", transaction_rollback),
        ("savepoint_recovery", "P1", savepoint_recovery),
        ("legal_lifecycle_successor", "P1", legal_paths),
    ]
    for field, assignment, expiry_fixture in parent_fields:
        tests.append(("parent_envelope_" + field, "P1",
                      lambda conn, a=assignment, e=expiry_fixture: attack_parent_envelope(conn, a, e)))
    for table in ("authorization_scope", "authorization_action", "authorization_policy"):
        tests.extend([
            ("%s_insert" % table, "P1", lambda conn, t=table: attack_child_insert(conn, t)),
            ("%s_update" % table, "P1", lambda conn, t=table: attack_child_update(conn, t)),
            ("%s_delete" % table, "P1", lambda conn, t=table: attack_child_delete(conn, t)),
            ("%s_replace" % table, "P1", lambda conn, t=table: attack_child_replace(conn, t)),
            ("%s_rebind_from_active" % table, "P1", lambda conn, t=table: attack_child_rebind_from_active(conn, t)),
            ("%s_rebind_into_active" % table, "P1", lambda conn, t=table: attack_child_rebind_into_active(conn, t)),
        ])
    results = []
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-057-") as temporary:
        work = Path(temporary)
        for case_id, severity, func in tests:
            for config in configs:
                results.append(execute_case(schema, work, config, case_id, severity, func))
    hashes = hash_checks(root, schema)
    hashes["input_before_sha256"] = input_before_sha256
    hashes["input_after_sha256"] = hashes["current_candidate_sha256"]
    hashes["input_unchanged_during_p3_057_runner"] = (
        input_before_sha256 == hashes["current_candidate_sha256"]
    )
    hash_status = "PASS" if hashes["all_historical_hashes_match"] else "FAIL"
    results.append({
        "id": "historical_evidence_hash_preservation", "severity": "P2", "status": hash_status,
        "detail": "all historical source/evidence hashes match" if hash_status == "PASS" else "historical evidence hash mismatch",
    })
    results.append({
        "id": "current_r0048_hash_boundary_observation", "severity": "P2",
        "status": "PASS" if hashes["current_matches_r0048_closed_boundary"] else "FAIL",
        "detail": "current candidate matches recorded closed-boundary hash" if hashes["current_matches_r0048_closed_boundary"]
        else "current candidate differs from the R-0048 recorded closed-boundary hash",
    })
    summary = {
        severity: {state: sum(1 for result in results if result["severity"] == severity and result["status"] == state)
                   for state in ("PASS", "FAIL")}
        for severity in ("P0", "P1", "P2")
    }
    summary["not_implemented"] = 0
    summary["unknown"] = 0
    summary["total"] = {state: sum(1 for result in results if result["status"] == state) for state in ("PASS", "FAIL")}
    payload = {
        "task_id": "LIFEOS-P3-057",
        "scope": "fresh isolated synthetic SQLite only",
        "independence": {
            "imports_p3_044": False,
            "calls_p3_044": False,
            "copies_p3_044_attack_functions_or_scenario_table": False,
            "runner_sha256": sha256(Path(__file__)),
        },
        "runtime": {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version},
        "schema": str(schema),
        "hash_checks": hashes,
        "summary": summary,
        "results": results,
    }
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "current_candidate": hashes["current_candidate_sha256"]}, ensure_ascii=False, sort_keys=True))
    return 0 if summary["total"]["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
