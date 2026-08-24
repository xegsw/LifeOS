#!/usr/bin/env python3
"""P3-044 active Authorization replacement/rebuild remediation regression.

Only synthetic in-memory and task-local file SQLite databases are used. Older
P3 suites are replayed from temporary project trees against the current P3-031
candidate SQL; their original directories and evidence remain read-only.
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
REPLACE_ERROR = "active_authorization_replace_forbidden"
DELETE_ERROR = "active_authorization_delete_forbidden"
RESULTS = []
INTEGRITY = []
DATABASES = []

P3_043_EXPECTED = {
    "../../LIFEOS-P3-043_pm_review.md": "1d35de5209064ae0688d5c63c55d92afddc07079317eb4beab09de82756dbd39",
    "../independent_review.md": "4018d8c6115d393dd739b046a7256f5c81d659292318deda7a1ad34958e8fc61",
    "MANIFEST.md": "116f5b1d45b81e3673708b5590a97c166721f2c6f034ec4d9a39212170a72279",
    "candidate_schema.sql": "ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b",
    "counter_example_attacks.py": "400c6fcb63d3ecac76f75a54a3017a12c379055dbeec2ebcc597d9fe1c30e40a",
    "counter_example_results.json": "a5d283fbb14e65605d83c20f5aebfee91a4cb1007893ae8ac85e4ae3a6b46d7b",
    "counter_example_results.txt": "b6aceeb1b92f7924ace7161dc6478755f3ecc5eafcb6fc2f1842ba4d8bcde5b6",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def p3_043_path(name):
    base = PROJECT / "reviews/LIFEOS-P3-043/evidence"
    return (base / name).resolve()


def p3_043_state():
    state = {}
    for name, expected in P3_043_EXPECTED.items():
        actual = digest(p3_043_path(name))
        state[name] = {"expected_sha256": expected, "actual_sha256": actual,
                       "matches_expected": actual == expected}
    return state


def setup_base(conn):
    conn.execute("INSERT INTO project VALUES ('p1','P','T','active',1,?,?,?)", (NOW, NOW, NOW))


def parent_values(aid="auth1", logical="logical1", status="proposed", version=1,
                  generation=1, processor="local", purpose="test", location="device",
                  expires_mode="indefinite", expires_at=None, policy_version="policy-v1",
                  supersedes=None):
    return (aid, logical, "actor", processor, purpose, location, status, version, generation,
            NOW, expires_mode, expires_at, None, policy_version, supersedes, NOW, NOW)


def insert_parent(conn, **kwargs):
    conn.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 parent_values(**kwargs))


def configure(conn, aid="auth1"):
    conn.execute("INSERT INTO authorization_scope VALUES (?,?, 'allow','p1',NULL,NULL)", (aid + "-scope", aid))
    conn.execute("INSERT INTO authorization_action VALUES (?,?, 'read')", (aid + "-action", aid))
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))


def setup_active(conn):
    setup_base(conn)
    insert_parent(conn)
    configure(conn)
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    conn.execute("INSERT INTO audit_entry VALUES ('activation','authorization.activate','actor','auth1',1,'ok',?,'activate:auth1')", (NOW,))
    conn.commit()


def retirement_evidence(conn, status, aid="auth1", generation=2):
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire",
              "superseded": "authorization.supersede"}[status]
    correlation = "authorization-state:%s:%d:%s" % (aid, generation, status)
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 ("audit-%s-%d" % (status, generation), action, "actor", aid, 1, "ok", NOW, correlation))
    conn.execute("INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 ("job-%s-%d" % (status, generation), "authorization_state_change", "authorization",
                  aid, generation, status, "pending", 0, NOW, None, 0, None, correlation, None))


def config_id(backend, fk_on, recursive):
    return "%s-fk_%s-rec_%s" % (backend, "on" if fk_on else "off", "on" if recursive else "off")


CONFIGS = [(backend, fk, rec) for backend in ("memory", "file")
           for fk in (True, False) for rec in (True, False)]


def fresh(backend, fk_on, recursive, case_name):
    if backend == "memory":
        path = ":memory:"
    else:
        path_obj = WORK / (case_name.replace("/", "_") + ".db")
        path_obj.unlink(missing_ok=True)
        path = str(path_obj)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    conn.commit()
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk_on else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if recursive else "OFF"))
    actual_fk = bool(conn.execute("PRAGMA foreign_keys").fetchone()[0])
    actual_recursive = bool(conn.execute("PRAGMA recursive_triggers").fetchone()[0])
    if actual_fk != fk_on or actual_recursive != recursive:
        raise RuntimeError("requested PRAGMA combination was not applied")
    DATABASES.append(path)
    return conn


def state(conn):
    parents = [tuple(row) for row in conn.execute(
        "SELECT id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,"
        "valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,supersedes_id,"
        "created_at_ms,updated_at_ms FROM authorization ORDER BY id")]
    children = {
        table: [tuple(row) for row in conn.execute("SELECT * FROM %s ORDER BY 1" % table)]
        for table in ("authorization_scope", "authorization_action", "authorization_policy")
    }
    return {"parents": parents, "children": children,
            "audit": [tuple(row) for row in conn.execute("SELECT * FROM audit_entry ORDER BY id")],
            "outbox": [tuple(row) for row in conn.execute("SELECT * FROM outbox_job ORDER BY id")]}


def health(conn, case_id, fk_on):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
    passed = integrity == "ok" and quick == "ok" and not foreign
    INTEGRITY.append({"case": case_id, "foreign_keys_enabled": fk_on,
                      "integrity_check": integrity, "quick_check": quick,
                      "foreign_key_check": foreign, "passed": passed})
    return passed


def run_rejected(name, operation, expected_error, transactions=("autocommit",), severity="P1"):
    for backend, fk_on, recursive in CONFIGS:
        for transaction in transactions:
            cid = "%s/%s/%s" % (name, config_id(backend, fk_on, recursive), transaction)
            conn = fresh(backend, fk_on, recursive, cid)
            setup_active(conn)
            before = state(conn)
            status, detail, sqlite_error = "FAIL", "operation unexpectedly succeeded", None
            try:
                if transaction != "autocommit":
                    conn.execute("BEGIN IMMEDIATE")
                operation(conn)
                if transaction == "explicit_rollback":
                    conn.rollback()
                else:
                    conn.commit()
            except sqlite3.DatabaseError as exc:
                sqlite_error = str(exc)
                conn.rollback()
                if expected_error in sqlite_error:
                    status, detail = "PASS", "rejected with stable contract error"
                else:
                    detail = "unexpected SQLite error"
            after = state(conn)
            atomic = before == after
            if not atomic:
                status, detail = "FAIL", "failed write did not preserve parent/children/generation/evidence atomically"
            if backend == "file" and not health(conn, cid, fk_on):
                status, detail = "FAIL", "file database integrity/FK check failed"
            conn.close()
            RESULTS.append({"group": "REBUILD", "name": name, "backend": backend,
                            "foreign_keys": "ON" if fk_on else "OFF",
                            "recursive_triggers": "ON" if recursive else "OFF",
                            "transaction": transaction, "severity": severity, "status": status,
                            "atomic_state_preserved": atomic, "detail": detail,
                            "sqlite_error": sqlite_error})


def run_legal(name, operation, verify, severity="P2"):
    for backend, fk_on, recursive in CONFIGS:
        cid = "%s/%s" % (name, config_id(backend, fk_on, recursive))
        conn = fresh(backend, fk_on, recursive, cid)
        status, detail, sqlite_error = "FAIL", "legal operation failed", None
        try:
            setup_active(conn)
            conn.execute("BEGIN IMMEDIATE")
            operation(conn)
            conn.commit()
            verify(conn)
            status, detail = "PASS", "legal path succeeded"
        except (sqlite3.DatabaseError, AssertionError) as exc:
            conn.rollback()
            sqlite_error = str(exc) if isinstance(exc, sqlite3.DatabaseError) else None
            detail = str(exc)
        if backend == "file" and not health(conn, cid, fk_on):
            status, detail = "FAIL", "file database integrity/FK check failed"
        conn.close()
        RESULTS.append({"group": "LEGAL", "name": name, "backend": backend,
                        "foreign_keys": "ON" if fk_on else "OFF",
                        "recursive_triggers": "ON" if recursive else "OFF",
                        "transaction": "explicit_commit", "severity": severity, "status": status,
                        "detail": detail, "sqlite_error": sqlite_error})


def replacement_sql(prefix="INSERT OR REPLACE INTO", **kwargs):
    return prefix + " authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", parent_values(**kwargs)


def run_conflict_matrix():
    # Exact P3-043 P1 under the full backend/PRAGMA/transaction cartesian product.
    sql, row = replacement_sql(processor="evil-replace", purpose="production", location="remote",
                               status="granted", expires_mode="at", expires_at=NOW + 50000,
                               policy_version="policy-evil")
    run_rejected("insert_or_replace_granted_fk_on", lambda c: c.execute(sql, row), REPLACE_ERROR,
                 transactions=("autocommit", "explicit_commit", "explicit_rollback"))
    run_rejected("fk_off_replace_rebuild_then_activate", lambda c: (
        c.execute(sql, row), c.execute("UPDATE authorization SET status='active' WHERE id='auth1'")),
        REPLACE_ERROR, severity="P2")

    cases = []
    for status in ("proposed", "granted", "active", "revoked"):
        sql, row = replacement_sql(status=status, processor="evil-%s" % status,
                                   policy_version="policy-evil", expires_mode="at", expires_at=NOW + 50000)
        cases.append(("replace_same_id_to_" + status, lambda c, s=sql, r=row: c.execute(s, r), REPLACE_ERROR))
    sql, row = replacement_sql(prefix="REPLACE INTO", aid="replacement-id", logical="logical1",
                               status="granted", processor="evil-version-key")
    cases.append(("replace_version_key_different_id", lambda c, s=sql, r=row: c.execute(s, r), REPLACE_ERROR))
    sql, row = replacement_sql(status="granted", processor="evil-both")
    cases.append(("replace_both_identity_keys", lambda c, s=sql, r=row: c.execute(s, r), REPLACE_ERROR))
    sql, row = replacement_sql(status="granted", processor="evil-id", logical="other-logical")
    cases.append(("replace_id_only_conflict", lambda c, s=sql, r=row: c.execute(s, r), REPLACE_ERROR))

    insert = "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    row_id = parent_values(status="granted", processor="evil-upsert")
    cases.append(("upsert_id_do_update", lambda c, r=row_id: c.execute(
        insert + " ON CONFLICT(id) DO UPDATE SET status=excluded.status,processor=excluded.processor,"
        "policy_version=excluded.policy_version", r), REPLACE_ERROR))
    row_version = parent_values(aid="replacement-id", status="granted", processor="evil-upsert-version")
    cases.append(("upsert_version_key_do_update", lambda c, r=row_version: c.execute(
        insert + " ON CONFLICT(logical_key,version_no) DO UPDATE SET processor=excluded.processor", r), REPLACE_ERROR))
    cases.append(("upsert_id_do_nothing", lambda c, r=row_id: c.execute(
        insert + " ON CONFLICT(id) DO NOTHING", r), REPLACE_ERROR))
    cases.append(("ordinary_duplicate_insert", lambda c, r=row_id: c.execute(insert, r), REPLACE_ERROR))
    cases.append(("direct_delete_active", lambda c: c.execute(
        "DELETE FROM authorization WHERE id='auth1'"), DELETE_ERROR))

    def delete_insert(c):
        c.execute("DELETE FROM authorization WHERE id='auth1'")
        c.execute(insert, parent_values(status="granted", processor="evil-delete-insert"))

    for name, operation, error in cases:
        run_rejected(name, operation, error)
    run_rejected("delete_then_insert_rebuild", delete_insert, DELETE_ERROR,
                 transactions=("autocommit", "explicit_commit", "explicit_rollback"))

    # Same transaction: prewritten fake evidence must roll back with rejected REPLACE.
    def evidence_then_replace(c):
        c.execute("INSERT INTO audit_entry VALUES ('fake','authorization.revoke','actor','auth1',1,'ok',?,'fake')", (NOW,))
        c.execute(sql, row)
    run_rejected("evidence_then_replace_transaction", evidence_then_replace, REPLACE_ERROR,
                 transactions=("explicit_commit", "explicit_rollback"))


def run_legal_matrix():
    def create_granted(c):
        insert_parent(c, aid="auth2", logical="logical2", status="granted", processor="configured")
        configure(c, "auth2")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    run_legal("new_granted_configure_activate", create_granted,
              lambda c: (_ for _ in ()).throw(AssertionError("new authorization inactive"))
              if c.execute("SELECT status FROM authorization WHERE id='auth2'").fetchone()[0] != "active" else None)

    def create_proposed(c):
        insert_parent(c, aid="auth2", logical="logical2")
        configure(c, "auth2")
        c.execute("UPDATE authorization SET processor='configured-v2' WHERE id='auth2'")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    run_legal("new_proposed_configure_activate", create_proposed,
              lambda c: (_ for _ in ()).throw(AssertionError("proposed path failed"))
              if tuple(c.execute("SELECT status,processor FROM authorization WHERE id='auth2'").fetchone())
              != ("active", "configured-v2") else None)

    def retire_successor(c):
        retirement_evidence(c, "superseded")
        c.execute("UPDATE authorization SET status='superseded',generation=2 WHERE id='auth1'")
        insert_parent(c, aid="auth2", logical="logical1", version=2, supersedes="auth1",
                      processor="approved-v2", policy_version="policy-v2")
        configure(c, "auth2")
        c.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    run_legal("retire_then_successor_same_transaction", retire_successor,
              lambda c: (_ for _ in ()).throw(AssertionError("successor lifecycle failed"))
              if [tuple(r) for r in c.execute("SELECT id,status,generation FROM authorization ORDER BY id")]
              != [("auth1", "superseded", 2), ("auth2", "active", 1)] else None)

    def no_op_maintenance(c):
        c.execute("UPDATE authorization SET processor=processor,policy_version=policy_version WHERE id='auth1'")
        c.execute("UPDATE authorization SET updated_at_ms=updated_at_ms+1 WHERE id='auth1'")
    run_legal("active_noop_and_updated_at", no_op_maintenance,
              lambda c: (_ for _ in ()).throw(AssertionError("maintenance path changed envelope"))
              if tuple(c.execute("SELECT status,processor,policy_version FROM authorization WHERE id='auth1'").fetchone())
              != ("active", "local", "policy-v1") else None)


def add_observation(name, severity, operation, expected_status, setup=setup_active):
    for backend in ("memory", "file"):
        cid = "observation/%s/%s" % (name, backend)
        conn = fresh(backend, True, False, cid)
        status, detail, sqlite_error = "UNKNOWN", "observation not reproduced", None
        try:
            setup(conn)
            operation(conn)
            conn.commit()
            status, detail = expected_status, "P3-043 non-range behavior retained"
        except sqlite3.DatabaseError as exc:
            conn.rollback(); sqlite_error = str(exc); detail = "observation changed: " + str(exc)
        if backend == "file" and not health(conn, cid, True):
            status, detail = "FAIL", "file database integrity/FK check failed"
        conn.close()
        RESULTS.append({"group": "P3-043-NONRANGE", "name": name, "backend": backend,
                        "foreign_keys": "ON", "recursive_triggers": "OFF",
                        "transaction": "autocommit", "severity": severity, "status": status,
                        "detail": detail, "sqlite_error": sqlite_error})


def run_nonrange_observations():
    def terminal(status):
        def setup(conn):
            setup_active(conn); retirement_evidence(conn, status)
            conn.execute("UPDATE authorization SET status=?,generation=2 WHERE id='auth1'", (status,)); conn.commit()
        return setup
    add_observation("envelope_change_while_revoked", "P2",
                    lambda c: c.execute("UPDATE authorization SET processor='history-rewrite' WHERE id='auth1'"),
                    "KNOWN_LIMITATION", terminal("revoked"))
    add_observation("envelope_change_while_expired", "P2",
                    lambda c: c.execute("UPDATE authorization SET purpose='history-rewrite' WHERE id='auth1'"),
                    "KNOWN_LIMITATION", terminal("expired"))
    add_observation("prewrite_revoked_at_active", "P2",
                    lambda c: c.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 1,)),
                    "KNOWN_LIMITATION")

    def prewrite_retire(c):
        c.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 1,))
        retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'")
    add_observation("prewrite_then_legal_retirement", "P2", prewrite_retire, "KNOWN_LIMITATION")
    def preset_retire(c):
        retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'")
    add_observation("preset_evidence_forged_retirement", "P2", preset_retire, "KNOWN_LIMITATION")
    add_observation("rewrite_created_at_active", "P2",
                    lambda c: c.execute("UPDATE authorization SET created_at_ms=created_at_ms-1 WHERE id='auth1'"),
                    "KNOWN_LIMITATION")
    add_observation("generation_bump_active", "P2",
                    lambda c: c.execute("UPDATE authorization SET generation=5 WHERE id='auth1'"),
                    "KNOWN_LIMITATION")
    def staged(c):
        c.execute("UPDATE authorization SET generation=2 WHERE id='auth1'")
        retirement_evidence(c, "revoked", generation=3)
        c.execute("UPDATE authorization SET status='revoked',generation=3 WHERE id='auth1'")
    add_observation("staged_generation_climb_retire", "P2", staged, "KNOWN_LIMITATION")
    def forged_time(c):
        retirement_evidence(c, "revoked")
        c.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=? WHERE id='auth1'", (NOW - 999,))
    add_observation("retirement_with_forged_revoked_at", "P2", forged_time, "KNOWN_LIMITATION")

    def granted_setup(c):
        setup_base(c); insert_parent(c, status="granted"); c.commit()
    add_observation("envelope_change_while_granted", "P3",
                    lambda c: c.execute("UPDATE authorization SET processor='configured' WHERE id='auth1'"),
                    "OBSERVATION", granted_setup)


def copy_p3_039(root):
    target = root / "reviews/LIFEOS-P3-039/evidence"
    target.mkdir(parents=True, exist_ok=True)
    source = PROJECT / "reviews/LIFEOS-P3-039/evidence"
    for name in ("MANIFEST.md", "counter_example_attacks.py", "counter_example_results.json",
                 "counter_example_results.txt", "candidate_schema.sql"):
        shutil.copyfile(source / name, target / name)


def run_p3_031():
    result = subprocess.run(["sh", str(PROJECT / "engineering/LIFEOS-P3-031/scripts/run_validation.sh")],
                            cwd=PROJECT.parent, text=True, capture_output=True)
    (EVIDENCE / "regressions/p3_031_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-031/evidence/test_results.json",
                    EVIDENCE / "regressions/p3_031_test_results.json")
    return result.returncode


def run_p3_040_current():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-044-p40-") as temp:
        root = Path(temp) / "lifeos"
        task = root / "engineering/LIFEOS-P3-040"
        for path in (task / "scripts", task / "input", task / "evidence/checks",
                     task / "evidence/input", task / "work",
                     root / "engineering/LIFEOS-P3-031/migrations"):
            path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-040/scripts/run_validation.py",
                        task / "scripts/run_validation.py")
        shutil.copyfile(CANDIDATE, root / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql")
        copy_p3_039(root)
        result = subprocess.run([sys.executable, str(task / "scripts/run_validation.py")],
                                cwd=Path(temp), text=True, capture_output=True)
        (EVIDENCE / "regressions/p3_040_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        for source, target in (("test_results.json", "p3_040_test_results.json"),
                               ("environment.json", "p3_040_environment.json"),
                               ("checks/integrity_and_fk.json", "p3_040_integrity_and_fk.json"),
                               ("input/source_hashes.json", "p3_040_source_hashes.json")):
            shutil.copyfile(task / "evidence" / source, EVIDENCE / "regressions" / target)
        return result.returncode


def run_p3_042_current():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-044-p42-") as temp:
        root = Path(temp) / "lifeos"
        task = root / "engineering/LIFEOS-P3-042"
        p31 = root / "engineering/LIFEOS-P3-031"
        p40 = root / "engineering/LIFEOS-P3-040"
        for path in (task / "scripts", task / "input", task / "evidence/checks",
                     task / "evidence/input", task / "evidence/regressions", task / "work",
                     p31 / "migrations", p31 / "tests", p31 / "scripts", p31 / "evidence",
                     p40 / "scripts"):
            path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-042/scripts/run_validation.py", task / "scripts/run_validation.py")
        shutil.copyfile(CANDIDATE, p31 / "migrations/001_candidate_schema.sql")
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py", p31 / "tests/run_contract_tests.py")
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-031/scripts/run_validation.sh", p31 / "scripts/run_validation.sh")
        shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-040/scripts/run_validation.py", p40 / "scripts/run_validation.py")
        copy_p3_039(root)
        source41 = PROJECT / "reviews/LIFEOS-P3-041/evidence"
        target41 = root / "reviews/LIFEOS-P3-041/evidence"
        target41.mkdir(parents=True, exist_ok=True)
        for name in ("MANIFEST.md", "counter_example_attacks.py", "counter_example_results.json",
                     "counter_example_results.txt", "candidate_schema.sql"):
            shutil.copyfile(source41 / name, target41 / name)
        result = subprocess.run([sys.executable, str(task / "scripts/run_validation.py")],
                                cwd=Path(temp), text=True, capture_output=True)
        (EVIDENCE / "regressions/p3_042_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        for source, target in (("test_results.json", "p3_042_test_results.json"),
                               ("environment.json", "p3_042_environment.json"),
                               ("checks/integrity_and_fk.json", "p3_042_integrity_and_fk.json"),
                               ("input/source_hashes.json", "p3_042_source_hashes.json")):
            shutil.copyfile(task / "evidence" / source, EVIDENCE / "regressions" / target)
        return result.returncode


def summary():
    states = ("PASS", "FAIL", "KNOWN_LIMITATION", "OBSERVATION", "NOT_IMPLEMENTED", "UNKNOWN")
    output = {}
    for severity in ("P0", "P1", "P2", "P3"):
        rows = [r for r in RESULTS if r["severity"] == severity]
        output[severity] = {state: sum(r["status"] == state for r in rows) for state in states}
    output["total"] = {state: sum(r["status"] == state for r in RESULTS) for state in states}
    return output


def write_evidence(exits, preservation):
    stats = summary()
    (EVIDENCE / "test_results.json").write_text(json.dumps({
        "task_id": "LIFEOS-P3-044", "route": "gpt-5.6-sol+xhigh",
        "scope": "synthetic SQLite only", "summary": stats,
        "regression_exit_codes": exits, "results": RESULTS,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(json.dumps({
        "all_passed": all(row["passed"] for row in INTEGRITY), "results": INTEGRITY,
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "environment.json").write_text(json.dumps({
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "platform": platform.platform(), "machine": platform.machine(),
        "network_used": False, "real_db_vault_file_tauri_ipc_used": False,
        "real_migration_executed": False, "database_paths": DATABASES,
        "pragma_matrix": {"foreign_keys": ["ON", "OFF"],
                          "recursive_triggers": ["ON", "OFF"]},
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/p3_043_preservation.json").write_text(
        json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps({
        "candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
        "p3_031_contract_tests": digest(PROJECT / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py"),
        "p3_031_shell": digest(PROJECT / "engineering/LIFEOS-P3-031/scripts/run_validation.sh"),
        "p3_040_runner": digest(PROJECT / "engineering/LIFEOS-P3-040/scripts/run_validation.py"),
        "p3_042_runner": digest(PROJECT / "engineering/LIFEOS-P3-042/scripts/run_validation.py"),
        "p3_044_runner": digest(Path(__file__)),
    }, indent=2) + "\n", encoding="utf-8")
    return stats


def main():
    for path in (SNAPSHOT.parent, EVIDENCE / "checks", EVIDENCE / "input",
                 EVIDENCE / "regressions", WORK):
        path.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    before = p3_043_state()
    if not all(row["matches_expected"] for row in before.values()):
        print("P3-043 preservation baseline mismatch", file=sys.stderr)
        return 2
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    exits = {"p3_031": run_p3_031(), "p3_040_current": run_p3_040_current(),
             "p3_042_current": run_p3_042_current()}
    run_conflict_matrix()
    run_legal_matrix()
    run_nonrange_observations()
    after = p3_043_state()
    preservation = {name: {"expected_sha256": P3_043_EXPECTED[name],
                           "before_sha256": before[name]["actual_sha256"],
                           "after_sha256": after[name]["actual_sha256"],
                           "unchanged": before[name]["actual_sha256"] == after[name]["actual_sha256"] and
                                        after[name]["matches_expected"]}
                    for name in P3_043_EXPECTED}
    stats = write_evidence(exits, preservation)
    for result in RESULTS:
        print("%-28s %-48s %-6s %-3s %-3s %-17s %s" %
              (result["group"], result["name"], result["backend"],
               result["foreign_keys"], result["recursive_triggers"],
               result["transaction"], result["status"]))
    print("SUMMARY " + json.dumps(stats, sort_keys=True))
    print("REGRESSION_EXITS " + json.dumps(exits, sort_keys=True))
    print("P3_043_PRESERVED", all(row["unchanged"] for row in preservation.values()))
    bad = any(code != 0 for code in exits.values())
    bad = bad or not all(row["passed"] for row in INTEGRITY)
    bad = bad or not all(row["unchanged"] for row in preservation.values())
    bad = bad or any(r["severity"] in ("P0", "P1") and r["status"] != "PASS" for r in RESULTS)
    bad = bad or any(r["status"] in ("FAIL", "NOT_IMPLEMENTED", "UNKNOWN") for r in RESULTS)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
