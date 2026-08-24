#!/usr/bin/env python3
"""LIFEOS-P3-040 controlled synthetic SQLite regression.

Runs the 29 P3-039 attacks plus stronger mutation/lifecycle cases against both
in-memory and fixed, task-local file databases. No real DB/Vault/Tauri/IPC or
network capability is used.
"""

import hashlib
import json
import platform
import shutil
import sqlite3
import sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
PROJECT = TASK.parents[1]
CANDIDATE = PROJECT / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
SNAPSHOT = TASK / "input/001_candidate_schema.sql"
EVIDENCE = TASK / "evidence"
WORK = TASK / "work"
P3_039 = PROJECT / "reviews/LIFEOS-P3-039/evidence"
NOW = 1786550400000
RESULTS = []
ACCESSED = []
INTEGRITY = []

P3_039_EXPECTED = {
    "MANIFEST.md": "a5603682e1b60af5947200f5b7c9954fb3825857cda74a37ac686b4365f8c7f7",
    "counter_example_attacks.py": "16e493390a1eeb86cf076959ab2576e593c74f6fc5c98e7c647642c50179ce9d",
    "counter_example_results.json": "0630a27be39692a5e1b962feefacaec84bc8941a754069d0c51f25e04cdd6545",
    "counter_example_results.txt": "0b95ea393a39655a81c0a34cb4281ff49a2858de1326906a1e74f479ed9c69fa",
    "candidate_schema.sql": "008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parent(conn, aid, logical, version=1, supersedes=None):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, logical, "actor", "local", "test", "device", "proposed", version, 1,
         NOW, "indefinite", None, None, "policy-v1", supersedes, NOW, NOW),
    )


def policy(conn, aid):
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )


def setup_auth(conn):
    conn.execute("INSERT INTO project VALUES ('p1','P','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO project VALUES ('p2','P2','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES ('s1','synthetic','K','L','available','allowed',1,?,?)", (NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES ('a1','s1',NULL,'note','active',1,?,?)", (NOW, NOW))
    parent(conn, "auth1", "logical1")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-deny','auth1','deny',NULL,'s1',NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    conn.execute("INSERT INTO audit_entry VALUES ('audit-activate','authorization.activate','actor','auth1',1,'ok',?,'corr-a')", (NOW,))
    conn.commit()


def setup_tombstone(conn):
    conn.execute("INSERT INTO tombstone VALUES ('artifact','a1',5,'cmd','T',?,'accepted',?)", (NOW, NOW))
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a1'")
    conn.commit()


def retirement_evidence(conn, status, include_audit=True, include_outbox=True):
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire", "superseded": "authorization.supersede"}[status]
    correlation = "authorization-state:auth1:2:" + status
    if include_audit:
        conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                     ("audit-" + status, action, "actor", "auth1", 1, "ok", NOW, correlation))
    if include_outbox:
        conn.execute("INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     ("job-" + status, "authorization_state_change", "authorization", "auth1", 2,
                      status, "pending", 0, NOW, None, 0, None, correlation, None))


def fresh(mode, case_id):
    if mode == "memory":
        path = ":memory:"
    else:
        path = str(WORK / (case_id.replace("/", "_").replace(" ", "_") + ".db"))
        Path(path).unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    ACCESSED.append(path)
    return conn


def case(group, name, severity, setup, operation, rejected=True, error=None, verify=None):
    for mode in ("memory", "file"):
        case_id = "%s/%s/%s" % (group, name, mode)
        conn = fresh(mode, case_id)
        passed = False
        detail = ""
        sqlite_error = None
        try:
            setup(conn)
            operation(conn)
            if rejected:
                detail = "operation unexpectedly succeeded"
            else:
                if verify:
                    verify(conn)
                passed = True
                detail = "legal operation succeeded"
        except sqlite3.DatabaseError as exc:
            sqlite_error = str(exc)
            if rejected and (error is None or error in sqlite_error):
                conn.rollback()
                if verify:
                    verify(conn)
                passed = True
                detail = "attack rejected"
            else:
                detail = "unexpected SQLite error"
        except AssertionError as exc:
            detail = str(exc)
        finally:
            if mode == "file":
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
                quick = conn.execute("PRAGMA quick_check").fetchone()[0]
                foreign_keys = [tuple(row) for row in conn.execute("PRAGMA foreign_key_check").fetchall()]
                healthy = integrity == "ok" and quick == "ok" and not foreign_keys
                INTEGRITY.append({"case": case_id, "integrity_check": integrity,
                                  "quick_check": quick, "foreign_key_check": foreign_keys,
                                  "passed": healthy})
                if not healthy:
                    passed = False
                    detail = "file database integrity/FK check failed"
            conn.close()
        RESULTS.append({"group": group, "name": name, "mode": mode, "severity": severity,
                        "status": "PASS" if passed else "FAIL", "detail": detail,
                        "sqlite_error": sqlite_error})


def noop(conn):
    pass


def assert_tombstone(conn, generation=5, status="active_blocked"):
    row = conn.execute("SELECT generation,cleanup_status FROM tombstone WHERE subject_id='a1'").fetchone()
    assert row is not None and tuple(row) == (generation, status), "Tombstone changed"


def assert_auth_active(conn):
    row = conn.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()
    assert row is not None and tuple(row) == ("active", 1), "active parent changed"


def p3_039_cases():
    # P2-2: six original delete/replace/reinsert attacks.
    case("P2-2", "ordinary_delete", "P1", setup_tombstone,
         lambda c: c.execute("DELETE FROM tombstone WHERE subject_id='a1'"), True, "tombstone_delete_forbidden", assert_tombstone)
    for suffix, generation in (("lower_gen", 4), ("same_gen", 5), ("higher_gen", 6)):
        case("P2-2", "insert_or_replace_" + suffix, "P1", setup_tombstone,
             lambda c, generation=generation: c.execute(
                 "INSERT OR REPLACE INTO tombstone VALUES ('artifact','a1',?,'replace','T',?,'accepted',?)",
                 (generation, NOW, NOW)), True, "tombstone_reinsert_forbidden", assert_tombstone)

    def delete_insert(c):
        c.execute("BEGIN IMMEDIATE")
        c.execute("DELETE FROM tombstone WHERE subject_id='a1'")
        c.execute("INSERT INTO tombstone VALUES ('artifact','a1',4,'new','T',?,'accepted',?)", (NOW, NOW))
        c.commit()
    case("P2-2", "delete_insert_commit", "P1", setup_tombstone, delete_insert, True, "tombstone_delete_forbidden", assert_tombstone)
    case("P2-2", "delete_insert_rollback", "P1", setup_tombstone, delete_insert, True, "tombstone_delete_forbidden", assert_tombstone)

    # P2-3: eight original initial-state/transition/generation cases.
    for status in ("active_blocked", "cleaned", "cleanup_failed", "vendor_limited"):
        case("P2-3", "direct_insert_" + status, "P1", noop,
             lambda c, status=status: c.execute(
                 "INSERT INTO tombstone VALUES ('artifact',?,1,'cmd','T',?,?,?)",
                 ("a-" + status, NOW, status, NOW)), True, "tombstone_must_start_accepted")
    case("P2-3", "accepted_start", "P1", noop,
         lambda c: c.execute("INSERT INTO tombstone VALUES ('artifact','legal',1,'cmd','T',?,'accepted',?)", (NOW, NOW)), False)

    def legal_tomb(c):
        c.execute("INSERT INTO tombstone VALUES ('artifact','a1',1,'cmd','T',?,'accepted',?)", (NOW, NOW))
        for status in ("active_blocked", "cleanup_pending", "cleaned"):
            c.execute("UPDATE tombstone SET cleanup_status=? WHERE subject_id='a1'", (status,))
    case("P2-3", "legal_transitions", "P1", noop, legal_tomb, False)
    case("P2-3", "illegal_skip_transition", "P1", noop,
         lambda c: (c.execute("INSERT INTO tombstone VALUES ('artifact','a1',1,'cmd','T',?,'accepted',?)", (NOW, NOW)),
                    c.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_id='a1'")),
         True, "tombstone_status_transition_invalid")
    case("P2-3", "generation_decrease", "P1", setup_tombstone,
         lambda c: c.execute("UPDATE tombstone SET generation=3 WHERE subject_id='a1'"),
         True, "tombstone_generation_must_not_decrease", assert_tombstone)

    # P2-4: four original active DELETE/inactive cleanup cases.
    for child, statement, error in (
        ("scope", "DELETE FROM authorization_scope WHERE id='scope-allow'", "scope_delete"),
        ("action", "DELETE FROM authorization_action WHERE id='action-read'", "action_delete"),
        ("policy", "DELETE FROM authorization_policy WHERE authorization_id='auth1'", "policy_delete"),
    ):
        case("P2-4", "active_%s_delete" % child, "P1", setup_auth,
             lambda c, statement=statement: c.execute(statement), True,
             "active_authorization_%s_forbidden" % error, assert_auth_active)

    def inactive_cleanup(c):
        setup_auth(c); retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'")
    case("P2-4", "inactive_scope_delete_allowed", "P2", inactive_cleanup,
         lambda c: c.execute("DELETE FROM authorization_scope WHERE id='scope-allow'"), False)

    # The eleven P3-039 ADJ attacks, with their original names.
    adjacent = (
        ("insert_new_scope_active", "INSERT INTO authorization_scope VALUES ('scope-extra','auth1','allow',NULL,NULL,'a1')", "scope_insert"),
        ("insert_new_action_active", "INSERT INTO authorization_action VALUES ('action-export','auth1','export_candidate')", "action_insert"),
        ("update_scope_effect_active", "UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow'", "scope_update"),
        ("update_scope_target_active", "UPDATE authorization_scope SET project_id='p2' WHERE id='scope-allow'", "scope_update"),
        ("update_policy_training_active", "UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth1'", "policy_update"),
        ("update_policy_sensitivity_active", "UPDATE authorization_policy SET sensitivity_rank=5 WHERE authorization_id='auth1'", "policy_update"),
        ("update_policy_external_send_active", "UPDATE authorization_policy SET external_send_allowed=1 WHERE authorization_id='auth1'", "policy_update"),
        ("update_action_value_active", "UPDATE authorization_action SET action='export_candidate' WHERE id='action-read'", "action_update"),
        ("insert_or_replace_scope_effect", "INSERT OR REPLACE INTO authorization_scope VALUES ('scope-allow','auth1','deny','p1',NULL,NULL)", "scope_insert"),
        ("insert_or_replace_policy", "INSERT OR REPLACE INTO authorization_policy VALUES ('auth1','none',NULL,5,1,1,'[\"evil\"]','[\"*\"]','[]','[]',999,999)", "policy_insert"),
    )
    for name, statement, suffix in adjacent:
        case("ADJ", name, "P1", setup_auth, lambda c, statement=statement: c.execute(statement),
             True, "active_authorization_%s_forbidden" % suffix, assert_auth_active)

    def setup_rebind(c):
        setup_auth(c); parent(c, "auth2", "logical2")
    case("ADJ", "scope_rebind_active", "P1", setup_rebind,
         lambda c: c.execute("UPDATE authorization_scope SET authorization_id='auth2' WHERE id='scope-allow'"),
         True, "active_authorization_scope_update_forbidden", assert_auth_active)


def extended_cases():
    child_cases = (
        ("scope_insert_deny", "INSERT INTO authorization_scope VALUES ('new-deny','auth1','deny','p1',NULL,NULL)", "scope_insert"),
        ("scope_update_source", "UPDATE authorization_scope SET project_id=NULL,source_id='s1' WHERE id='scope-allow'", "scope_update"),
        ("scope_update_artifact", "UPDATE authorization_scope SET project_id=NULL,artifact_id='a1' WHERE id='scope-allow'", "scope_update"),
        ("action_replace", "INSERT OR REPLACE INTO authorization_action VALUES ('action-read','auth1','export_candidate')", "action_insert"),
        ("policy_direct_insert", "INSERT INTO authorization_policy VALUES ('auth1','none',NULL,5,1,1,'[]','[]','[]','[]',99,99)", "policy_insert"),
    )
    for name, statement, suffix in child_cases:
        case("EXT-CHILD", name, "P1", setup_auth, lambda c, statement=statement: c.execute(statement),
             True, "active_authorization_%s_forbidden" % suffix, assert_auth_active)

    policy_fields = (
        ("retention", "retention_mode='until',retention_deadline_ms=%d" % (NOW + 1000)),
        ("recipients", "recipients_json='[\"r\"]'"), ("regions", "regions_json='[\"z\"]'"),
        ("disclosure", "disclosure_json='[\"d\"]'"), ("license", "source_license_json='[\"l\"]'"),
        ("quantity", "quantity_ceiling=99"), ("frequency", "frequency_ceiling=99"),
    )
    for name, assignment in policy_fields:
        case("EXT-POLICY", "update_" + name, "P1", setup_auth,
             lambda c, assignment=assignment: c.execute("UPDATE authorization_policy SET %s WHERE authorization_id='auth1'" % assignment),
             True, "active_authorization_policy_update_forbidden", assert_auth_active)

    # OLD inactive -> NEW active and active -> active for every child table.
    for table, keycol, insert_sql, key, error in (
        ("authorization_scope", "id", "INSERT INTO authorization_scope VALUES ('i-s','inactive','allow','p1',NULL,NULL)", "i-s", "scope_update"),
        ("authorization_action", "id", "INSERT INTO authorization_action VALUES ('i-a','inactive','export_candidate')", "i-a", "action_update"),
        ("authorization_policy", "authorization_id", None, "inactive", "policy_update"),
    ):
        def inactive_to_active(c, insert_sql=insert_sql, table=table):
            setup_auth(c); parent(c, "inactive", "logical-i")
            policy(c, "inactive") if table == "authorization_policy" else c.execute(insert_sql)
        case("EXT-REBIND", table + "_inactive_to_active", "P1", inactive_to_active,
             lambda c, table=table, keycol=keycol, key=key: c.execute(
                 "UPDATE %s SET authorization_id='auth1' WHERE %s=?" % (table, keycol), (key,)),
             True, "active_authorization_%s_forbidden" % error, assert_auth_active)

        def active_to_inactive(c):
            setup_auth(c); parent(c, "inactive", "logical-i")
        active_key = {"authorization_scope": "scope-allow", "authorization_action": "action-read", "authorization_policy": "auth1"}[table]
        case("EXT-REBIND", table + "_active_to_inactive", "P1", active_to_inactive,
             lambda c, table=table, keycol=keycol, active_key=active_key: c.execute(
                 "UPDATE %s SET authorization_id='inactive' WHERE %s=?" % (table, keycol), (active_key,)),
             True, "active_authorization_%s_forbidden" % error, assert_auth_active)

        def active_to_active(c):
            setup_auth(c); parent(c, "auth2", "logical2")
            c.execute("INSERT INTO authorization_scope VALUES ('a2-s','auth2','allow','p1',NULL,NULL)")
            c.execute("INSERT INTO authorization_action VALUES ('a2-a','auth2','read')"); policy(c, "auth2")
            c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        source_key = {"authorization_scope": "scope-allow", "authorization_action": "action-read", "authorization_policy": "auth1"}[table]
        case("EXT-REBIND", table + "_active_to_active", "P1", active_to_active,
             lambda c, table=table, keycol=keycol, source_key=source_key: c.execute(
                 "UPDATE %s SET authorization_id='auth2' WHERE %s=?" % (table, keycol), (source_key,)),
             True, "active_authorization_%s_forbidden" % error, assert_auth_active)

    for status in ("proposed", "granted"):
        case("EXT-STATE", "active_to_" + status, "P1", setup_auth,
             lambda c, status=status: c.execute("UPDATE authorization SET status=? WHERE id='auth1'", (status,)),
             True, "authorization_status_transition_invalid", assert_auth_active)

    case("EXT-STATE", "retire_without_generation", "P1", setup_auth,
         lambda c: c.execute("UPDATE authorization SET status='revoked' WHERE id='auth1'"),
         True, "authorization_retirement_generation_invalid", assert_auth_active)
    case("EXT-STATE", "retire_without_audit", "P1", setup_auth,
         lambda c: c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
         True, "authorization_retirement_audit_required", assert_auth_active)

    def audit_only(c):
        setup_auth(c); retirement_evidence(c, "revoked", include_outbox=False)
    case("EXT-STATE", "retire_without_outbox", "P1", audit_only,
         lambda c: c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"),
         True, "authorization_retirement_outbox_required", assert_auth_active)

    for terminal in ("revoked", "expired", "superseded"):
        def retired(c, terminal=terminal):
            setup_auth(c); retirement_evidence(c, terminal)
            c.execute("UPDATE authorization SET status=?,generation=2 WHERE id='auth1'", (terminal,)); c.commit()
        case("EXT-STATE", terminal + "_mutate_then_reactivate", "P1", retired,
             lambda c: (c.execute("UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow'"),
                        c.execute("UPDATE authorization_action SET action='export_candidate' WHERE id='action-read'"),
                        c.execute("UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth1'"),
                        c.execute("UPDATE authorization SET status='active' WHERE id='auth1'")),
             True, "authorization_status_transition_invalid")

        def cleanup(c, terminal=terminal):
            retired(c, terminal)
        case("EXT-LEGAL", terminal + "_child_cleanup", "P1", cleanup,
             lambda c: (c.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"),
                        c.execute("DELETE FROM authorization_action WHERE authorization_id='auth1'"),
                        c.execute("DELETE FROM authorization_policy WHERE authorization_id='auth1'")), False)

    case("EXT-STATE", "version_identity_update", "P1", setup_auth,
         lambda c: c.execute("UPDATE authorization SET version_no=2 WHERE id='auth1'"),
         True, "authorization_version_identity_immutable", assert_auth_active)

    def versioned(c):
        setup_auth(c); retirement_evidence(c, "superseded")
        c.execute("UPDATE authorization SET status='superseded',generation=2 WHERE id='auth1'")
    def activate_v2(c):
        parent(c, "auth2", "logical1", 2, "auth1")
        c.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        c.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')"); policy(c, "auth2")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    case("EXT-LEGAL", "new_version_supersede_activate", "P1", versioned, activate_v2, False,
         verify=lambda c: (_ for _ in ()).throw(AssertionError("new version inactive"))
         if c.execute("SELECT status FROM authorization WHERE id='auth2'").fetchone()[0] != "active" else None)

    def bad_v2(c):
        setup_auth(c); retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'")
        parent(c, "auth2", "logical1", 2, None)
        c.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        c.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')"); policy(c, "auth2")
    case("EXT-STATE", "new_version_without_supersedes", "P1", bad_v2,
         lambda c: c.execute("UPDATE authorization SET status='active' WHERE id='auth2'"),
         True, "authorization_new_version_requires_supersedes")


def write_evidence():
    summary = {}
    for severity in ("P0", "P1", "P2"):
        rows = [r for r in RESULTS if r["severity"] == severity]
        summary[severity] = {state: sum(r["status"] == state for r in rows)
                             for state in ("PASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")}
    summary["total"] = {state: sum(r["status"] == state for r in RESULTS)
                        for state in ("PASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")}
    payload = {"task_id": "LIFEOS-P3-040", "scope": "synthetic in-memory and controlled file SQLite only",
               "summary": summary, "results": RESULTS}
    (EVIDENCE / "test_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preservation = {}
    for name, expected in P3_039_EXPECTED.items():
        actual = digest(P3_039 / name)
        preservation[name] = {"expected_sha256": expected, "actual_sha256": actual, "unchanged": actual == expected}
    (EVIDENCE / "input/p3_039_evidence_preservation.json").write_text(
        json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    env = {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
           "platform": platform.platform(), "machine": platform.machine(), "network_used": False,
           "real_db_vault_tauri_ipc_used": False, "accessed_databases": ACCESSED}
    (EVIDENCE / "environment.json").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(
        json.dumps({"all_passed": all(row["passed"] for row in INTEGRITY), "results": INTEGRITY}, indent=2) + "\n",
        encoding="utf-8")
    hashes = {"candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
              "runner": digest(Path(__file__))}
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    return summary, all(v["unchanged"] for v in preservation.values())


def main():
    EVIDENCE.joinpath("input").mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    p3_039_cases()
    extended_cases()
    summary, preserved = write_evidence()
    for result in RESULTS:
        print("%-12s %-42s %-6s %-2s %s" %
              (result["group"], result["name"], result["mode"], result["severity"], result["status"]))
    print("SUMMARY " + json.dumps(summary, sort_keys=True))
    print("P3_039_EVIDENCE_PRESERVED " + str(preserved))
    bad = any(r["severity"] in ("P0", "P1") and r["status"] != "PASS" for r in RESULTS)
    bad = bad or any(r["status"] in ("NOT_IMPLEMENTED", "UNKNOWN") for r in RESULTS) or not preserved
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
