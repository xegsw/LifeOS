#!/usr/bin/env python3
"""P3-046 synthetic SQLite lifecycle/evidence/terminal-history regression.

Only in-memory and task-local file databases are created. No real DB, Vault,
file capability, Tauri/IPC, network, cloud model, sync, or external user exists.
"""

import hashlib
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
PROJECT = TASK.parents[1]
CANDIDATE = PROJECT / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
P31_TESTS = PROJECT / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py"
P31_SHELL = PROJECT / "engineering/LIFEOS-P3-031/scripts/run_validation.sh"
SNAPSHOT = TASK / "input/001_candidate_schema.sql"
EVIDENCE = TASK / "evidence"
WORK = TASK / "work"
NOW = 1786550400000
RESULTS = []
SNAPSHOTS = []
TRACES = []
INTEGRITY = []
DATABASES = []

P3_044_EXPECTED = {
    "evidence/MANIFEST.md": "8e057568701f49de990301e66f4bea351fecc4819c67c4f1f0eb49447da43b26",
    "scripts/run_validation.py": "1e297a9eaf031776b33ee978656e9aa62e477d1b05875a6c1aa9627b532774c3",
    "evidence/test_results.json": "857c86c8212a09f35f5fdd129acda82ca4b532269158c0c4b5c9e08a8dbe439f",
    "evidence/test_run.log": "b0e4f76ce3af1cd447e1dfac53823fb73894f6959dd14f1afe8bdf949adc6848",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db_now(conn):
    return conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]


def cfg_id(backend, fk, rec):
    return "%s-fk_%s-rec_%s" % (backend, "on" if fk else "off", "on" if rec else "off")


CONFIGS = [(b, fk, rec) for b in ("memory", "file") for fk in (True, False) for rec in (True, False)]


def fresh(backend, fk, rec, name):
    if backend == "memory":
        path = ":memory:"
    else:
        target = WORK / (name.replace("/", "_").replace(":", "_") + ".db")
        target.unlink(missing_ok=True)
        path = str(target)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if rec else "OFF"))
    if bool(conn.execute("PRAGMA foreign_keys").fetchone()[0]) != fk:
        raise AssertionError("foreign_keys PRAGMA mismatch")
    if bool(conn.execute("PRAGMA recursive_triggers").fetchone()[0]) != rec:
        raise AssertionError("recursive_triggers PRAGMA mismatch")
    DATABASES.append(path)
    return conn


def insert_parent(conn, aid="auth1", logical="logical1", version=1, supersedes=None,
                  status="proposed", processor="local", policy="policy@1"):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, logical, "actor:user", processor, "test", "device", status, version, 1,
         NOW, "indefinite", None, None, policy, supersedes, NOW, NOW),
    )


def configure(conn, aid="auth1"):
    conn.execute("INSERT INTO authorization_scope VALUES (?,?, 'allow','p1',NULL,NULL)", (aid + ":scope", aid))
    conn.execute("INSERT INTO authorization_action VALUES (?,?, 'read')", (aid + ":action", aid))
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))


def setup_active(conn, aid="auth1", logical="logical1", version=1, supersedes=None,
                 processor="local", policy="policy@1"):
    if conn.execute("SELECT 1 FROM project WHERE id='p1'").fetchone() is None:
        conn.execute("INSERT INTO project VALUES ('p1','Synthetic','test','active',1,?,?,?)", (NOW, NOW, NOW))
    insert_parent(conn, aid, logical, version, supersedes, processor=processor, policy=policy)
    configure(conn, aid)
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (aid,))


def command(conn, status, aid="auth1", expected=1, actor=None, cid=None, idem=None, req_hash=None):
    actor = actor or ("system:local" if status == "expired" else "actor:claim")
    token = "%s:%s:%s" % (aid, expected + 1, status)
    conn.execute(
        """INSERT INTO authorization_lifecycle_command(
             id,idempotency_key,authorization_id,expected_generation,target_status,
             scoped_actor_claim,canonical_request_hash,requested_at_ms
           ) VALUES (?,?,?,?,?,?,?,?)""",
        (cid or ("cmd:" + token), idem or ("idem:" + token), aid, expected, status,
         actor, req_hash or ("request:" + token), NOW),
    )


def expect_error(fn, contains=None):
    try:
        fn()
    except sqlite3.DatabaseError as exc:
        if contains and contains not in str(exc):
            raise AssertionError("unexpected SQLite error %r, expected %r" % (str(exc), contains))
        return str(exc)
    raise AssertionError("operation unexpectedly succeeded")


def rows(conn, sql, args=()):
    return [list(row) for row in conn.execute(sql, args)]


def state(conn):
    return {
        "authorization": rows(conn, "SELECT * FROM authorization ORDER BY id"),
        "scope": rows(conn, "SELECT * FROM authorization_scope ORDER BY id"),
        "action": rows(conn, "SELECT * FROM authorization_action ORDER BY id"),
        "policy": rows(conn, "SELECT * FROM authorization_policy ORDER BY authorization_id"),
        "command": rows(conn, "SELECT * FROM authorization_lifecycle_command ORDER BY id"),
        "audit": rows(conn, "SELECT * FROM audit_entry ORDER BY id"),
        "outbox": rows(conn, "SELECT * FROM outbox_job ORDER BY id"),
        "submission": rows(conn, "SELECT * FROM submission ORDER BY namespace,idempotency_key"),
        "tombstone": rows(conn, "SELECT * FROM tombstone ORDER BY subject_type,subject_id"),
    }


def health(conn, case, fk):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = rows(conn, "PRAGMA foreign_key_check")
    passed = integrity == "ok" and quick == "ok" and not foreign
    INTEGRITY.append({"case": case, "foreign_keys_enabled": fk, "integrity_check": integrity,
                      "quick_check": quick, "foreign_key_check": foreign, "passed": passed})
    return passed


def record(ac, severity, config, passed, detail, group="AC", extra=None):
    item = {"id": ac, "severity": severity, "group": group, "config": config,
            "status": "PASS" if passed else "FAIL", "detail": detail}
    if extra:
        item.update(extra)
    RESULTS.append(item)


def run_standard(ac, severity, scenario):
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec)
        case = "%s/%s" % (ac, config)
        conn = fresh(backend, fk, rec, case)
        passed, detail = False, ""
        try:
            detail = scenario(conn, case) or "contract held"
            passed = True
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk):
            passed, detail = False, "file integrity/FK check failed"
        conn.close()
        record(ac, severity, config, passed, detail)


def ac01(conn, case):
    setup_active(conn)
    corr = "authorization-state:auth1:2:revoked"
    conn.execute("INSERT INTO audit_entry VALUES ('pre','authorization.revoke','actor:claim','auth1',1,'ok',?,?)", (NOW, corr))
    before = state(conn)
    expect_error(lambda: command(conn, "revoked"), "audit_entry_reinsert_forbidden")
    after = state(conn)
    assert before == after
    SNAPSHOTS.append({"case": case, "kind": "prewritten_audit_atomic_rollback", "before": before, "after": after})


def ac02(conn, case):
    conn.execute("INSERT INTO audit_entry VALUES ('a','legal.append','actor:claim','subject',NULL,'ok',?,'corr:a')", (NOW,))
    before = state(conn)["audit"]
    expect_error(lambda: conn.execute("UPDATE audit_entry SET result_code='evil' WHERE id='a'"), "append_only")
    expect_error(lambda: conn.execute("DELETE FROM audit_entry WHERE id='a'"), "append_only")
    expect_error(lambda: conn.execute("INSERT OR REPLACE INTO audit_entry VALUES ('a','evil','x','x',NULL,'x',?,'corr:a')", (NOW,)), "reinsert")
    assert state(conn)["audit"] == before


def ac03(conn, case):
    setup_active(conn)
    conn.execute("INSERT INTO audit_entry VALUES ('wrong','authorization.revoke','actor:claim','auth1',99,'ok',?,'wrong')", (NOW,))
    conn.execute("INSERT INTO outbox_job VALUES ('wrong','authorization_state_change','authorization','auth1',9,'revoked','pending',0,?,NULL,0,NULL,'wrong',NULL)", (NOW,))
    before = state(conn)
    expect_error(lambda: conn.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'", (NOW, NOW)), "lifecycle_command")
    assert state(conn) == before


def ac04(conn, case):
    setup_active(conn); command(conn, "revoked")
    before = state(conn)
    expect_error(lambda: command(conn, "revoked", cid="replay"))
    assert state(conn) == before


def ac05(conn, case):
    setup_active(conn); command(conn, "revoked")
    job = conn.execute("SELECT * FROM outbox_job").fetchone(); before = state(conn)["outbox"]
    for sql in ("UPDATE outbox_job SET payload_ref='active' WHERE id=?",
                "UPDATE outbox_job SET subject_id='other' WHERE id=?",
                "UPDATE outbox_job SET idempotency_key='other' WHERE id=?"):
        expect_error(lambda sql=sql: conn.execute(sql, (job["id"],)), "payload_immutable")
    expect_error(lambda: conn.execute("INSERT OR REPLACE INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(job)), "reinsert")
    assert state(conn)["outbox"] == before


def claim(conn, job_id, worker="worker:a"):
    now = db_now(conn)
    assert conn.execute(
        "UPDATE outbox_job SET status='leased',attempts=attempts+1,lease_owner=?,lease_generation=lease_generation+1,lease_expires_at_ms=? WHERE id=? AND status='pending'",
        (worker, now + 60000, job_id),
    ).rowcount == 1


def ac06(conn, case):
    setup_active(conn); command(conn, "revoked")
    job = conn.execute("SELECT * FROM outbox_job").fetchone(); claim(conn, job["id"])
    lease = conn.execute("SELECT lease_generation FROM outbox_job WHERE id=?", (job["id"],)).fetchone()[0]
    stale = conn.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id=? AND lease_generation=?", (job["id"], lease - 1)).rowcount
    done = conn.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id=? AND lease_owner='worker:a' AND lease_generation=?", (job["id"], lease)).rowcount
    assert stale == 0 and done == 1
    TRACES.append({"case": case, "machine": "outbox", "trace": ["pending", "leased", "completed"]})


def ac07(conn, case):
    setup_active(conn); now = db_now(conn)
    conn.execute("INSERT INTO outbox_job VALUES ('stale','publish','authorization','auth1',2,NULL,'pending',0,?,NULL,0,NULL,'idem:stale',NULL)", (now,))
    claim(conn, "stale")
    assert conn.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='stale' AND lease_generation=0").rowcount == 0
    expect_error(lambda: conn.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='stale'"), "runtime_transition_invalid")
    assert conn.execute("SELECT status FROM outbox_job WHERE id='stale'").fetchone()[0] == "leased"


def ac08(conn, case):
    setup_active(conn); command(conn, "expired")
    job = conn.execute("SELECT * FROM outbox_job").fetchone()
    payload = tuple(job[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key"))
    claim(conn, job["id"]); now = db_now(conn)
    conn.execute("UPDATE outbox_job SET status='pending',available_at_ms=?,lease_owner=NULL,lease_expires_at_ms=NULL,last_error_code='E_RETRY' WHERE id=?", (now + 1000, job["id"]))
    row = conn.execute("SELECT * FROM outbox_job WHERE id=?", (job["id"],)).fetchone()
    assert row["attempts"] == 1 and row["status"] == "pending"
    assert tuple(row[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key")) == payload
    TRACES.append({"case": case, "machine": "outbox", "trace": ["pending", "leased", "pending(retry)"]})


def ac09(conn, case):
    setup_active(conn); before = state(conn)
    expect_error(lambda: conn.execute("UPDATE authorization SET generation=2 WHERE id='auth1'"), "lifecycle_command")
    expect_error(lambda: conn.execute("UPDATE authorization SET generation=9 WHERE id='auth1'"), "lifecycle_command")
    assert state(conn) == before


def ac10(conn, case):
    setup_active(conn); before = state(conn)
    expect_error(lambda: conn.execute("UPDATE authorization SET created_at_ms=created_at_ms-1 WHERE id='auth1'"), "created_at_immutable")
    expect_error(lambda: conn.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 1,)), "revoked_time")
    assert state(conn) == before


def ac11(conn, case):
    setup_active(conn)
    expect_error(lambda: conn.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'", (NOW - 1, NOW - 2)), "lifecycle_command")
    command(conn, "revoked")
    parent = conn.execute("SELECT * FROM authorization WHERE id='auth1'").fetchone()
    audit = conn.execute("SELECT * FROM audit_entry").fetchone()
    assert parent["updated_at_ms"] == parent["revoked_at_ms"] == audit["occurred_at_ms"]


def ac12(conn, case):
    setup_active(conn); command(conn, "revoked"); before = state(conn)
    row = tuple(conn.execute("SELECT * FROM authorization WHERE id='auth1'").fetchone())
    expect_error(lambda: conn.execute("UPDATE authorization SET processor='evil' WHERE id='auth1'"), "terminal_authorization_immutable")
    expect_error(lambda: conn.execute("DELETE FROM authorization WHERE id='auth1'"), "terminal_authorization_delete")
    expect_error(lambda: conn.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row), "terminal_authorization_replace")
    assert state(conn) == before


def ac13(conn, case):
    setup_active(conn); command(conn, "expired"); before = state(conn)
    expect_error(lambda: conn.execute("INSERT INTO authorization_scope VALUES ('extra','auth1','deny','p1',NULL,NULL)"), "terminal_authorization_scope_insert")
    expect_error(lambda: conn.execute("UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'"), "terminal_authorization_scope_update")
    expect_error(lambda: conn.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")
    expect_error(lambda: conn.execute("UPDATE authorization_action SET action='export_candidate' WHERE authorization_id='auth1'"), "terminal_authorization_action_update")
    expect_error(lambda: conn.execute("DELETE FROM authorization_policy WHERE authorization_id='auth1'"), "requires_cleanup")
    assert state(conn) == before


def ac15(conn, case):
    setup_active(conn, "old", "versioned"); command(conn, "superseded", "old")
    old = tuple(conn.execute("SELECT * FROM authorization WHERE id='old'").fetchone())
    setup_active(conn, "new", "versioned", 2, "old", "approved-v2", "policy@2")
    assert tuple(conn.execute("SELECT * FROM authorization WHERE id='old'").fetchone()) == old
    assert tuple(conn.execute("SELECT status,version_no,generation FROM authorization WHERE id='new'").fetchone()) == ("active", 2, 1)


def cleanup_gate(conn, aid="auth1"):
    row = conn.execute("SELECT version_no,generation FROM authorization WHERE id=?", (aid,)).fetchone()
    corr = "authorization-cleanup:%s:%s" % (aid, row["generation"])
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 ("audit:" + corr, "authorization.cleanup", "actor:claim", aid,
                  row["version_no"], "redacted_by_user", NOW, corr))
    conn.execute("INSERT INTO tombstone VALUES ('authorization',?,?,?,'user_cleanup',?,'accepted',?)",
                 (aid, row["generation"], "cleanup:" + aid, NOW, NOW))
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='authorization' AND subject_id=?", (aid,))
    conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id=?", (aid,))


def ac17(conn, case):
    setup_active(conn)
    expect_error(lambda: conn.execute("INSERT INTO tombstone VALUES ('authorization','auth1',1,'active','cleanup',?,'accepted',?)", (NOW, NOW)), "requires_terminal_generation")
    command(conn, "revoked")
    expect_error(lambda: conn.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")
    expect_error(lambda: conn.execute("INSERT INTO tombstone VALUES ('authorization','auth1',1,'wrong','cleanup',?,'accepted',?)", (NOW, NOW)), "requires_terminal_generation")
    conn.execute("INSERT INTO tombstone VALUES ('authorization','auth1',2,'no-audit','cleanup',?,'accepted',?)", (NOW, NOW))
    expect_error(lambda: conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='authorization' AND subject_id='auth1'"), "cleanup_audit_required")


def ac18(conn, case):
    setup_active(conn); command(conn, "revoked"); cleanup_gate(conn)
    before = state(conn)
    for table in ("authorization_scope", "authorization_action", "authorization_policy"):
        conn.execute("DELETE FROM %s WHERE authorization_id='auth1'" % table)
    conn.execute("UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id='auth1'")
    after = state(conn)
    assert after["authorization"] == before["authorization"] and len(after["audit"]) == 2
    assert not after["scope"] and not after["action"] and not after["policy"]
    expect_error(lambda: conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id='auth1'"), "transition_invalid")
    rebuild = ("auth1", "logical1", "evil", "cloud", "prod", "remote", "granted", 1, 1,
               NOW, "indefinite", None, None, "evil", None, NOW, NOW)
    expect_error(lambda: conn.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rebuild), "terminal_authorization_replace")
    tomb_gen = conn.execute("SELECT generation FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'").fetchone()[0]
    assert tomb_gen >= 1  # old package generation 1 is dominated and cannot revive.
    SNAPSHOTS.append({"case": case, "kind": "controlled_cleanup", "before": before, "after": after})


def run_retirement_matrix():
    severity = "P1"
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec)
        for terminal in ("revoked", "expired", "superseded"):
            for tx in ("autocommit", "explicit_commit", "explicit_rollback"):
                case = "AC-14/%s/%s/%s" % (terminal, config, tx)
                conn = fresh(backend, fk, rec, case); passed = False; detail = ""
                try:
                    setup_active(conn); before = state(conn)
                    if tx != "autocommit":
                        conn.execute("BEGIN IMMEDIATE")
                    command(conn, terminal, actor=("system:local" if terminal == "expired" else "claim:unverified"))
                    inside = state(conn)
                    if tx == "explicit_rollback":
                        conn.rollback(); after = state(conn)
                        assert after == before
                    else:
                        if tx == "explicit_commit": conn.commit()
                        after = state(conn)
                        parent = conn.execute("SELECT status,generation,updated_at_ms,revoked_at_ms FROM authorization WHERE id='auth1'").fetchone()
                        cmd = conn.execute("SELECT * FROM authorization_lifecycle_command").fetchone()
                        audit = conn.execute("SELECT * FROM audit_entry WHERE correlation_id=?", (cmd["correlation_id"],)).fetchone()
                        outbox = conn.execute("SELECT * FROM outbox_job WHERE idempotency_key=?", (cmd["correlation_id"],)).fetchone()
                        assert tuple(parent[:2]) == (terminal, 2) and audit and outbox
                        assert parent["updated_at_ms"] == audit["occurred_at_ms"]
                        assert audit["scoped_actor_ref"] == cmd["scoped_actor_claim"]
                    SNAPSHOTS.append({"case": case, "kind": "retirement_atomicity", "before": before,
                                      "inside": inside, "after": after})
                    passed, detail = True, "DB-time retirement/evidence atomic; actor remains an unverified claim"
                except Exception as exc:
                    try: conn.rollback()
                    except sqlite3.DatabaseError: pass
                    detail = "%s: %s" % (type(exc).__name__, exc)
                if backend == "file" and not health(conn, case, fk):
                    passed, detail = False, "file integrity/FK check failed"
                conn.close()
                record("AC-14", severity, config, passed, detail, extra={"terminal": terminal, "transaction": tx})


def run_fault_matrix():
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec)
        for fault in ("audit", "outbox"):
            case = "AC-16/%s/%s" % (fault, config)
            conn = fresh(backend, fk, rec, case); passed = False; detail = ""
            try:
                setup_active(conn); corr = "authorization-state:auth1:2:revoked"
                if fault == "audit":
                    conn.execute("INSERT INTO audit_entry VALUES ('pre','authorization.revoke','claim','auth1',1,'ok',?,?)", (NOW, corr))
                else:
                    conn.execute("INSERT INTO outbox_job VALUES ('pre','authorization_state_change','authorization','auth1',2,'revoked','pending',0,?,NULL,0,NULL,?,NULL)", (NOW, corr))
                before = state(conn); conn.execute("BEGIN IMMEDIATE")
                conn.execute("INSERT INTO submission VALUES ('destruct@1','retire','request','revoke_authorization','auth1',NULL,?)", (NOW,))
                expect_error(lambda: command(conn, "revoked"))
                conn.rollback(); after = state(conn)
                assert before == after and not after["command"] and not after["submission"]
                SNAPSHOTS.append({"case": case, "kind": fault + "_fault_rollback", "before": before, "after": after})
                passed, detail = True, "fault rolled back parent/command/submission/generated evidence"
            except Exception as exc:
                try: conn.rollback()
                except sqlite3.DatabaseError: pass
                detail = "%s: %s" % (type(exc).__name__, exc)
            if backend == "file" and not health(conn, case, fk):
                passed, detail = False, "file integrity/FK check failed"
            conn.close(); record("AC-16", "P1", config, passed, detail, extra={"fault": fault})


def run_command_edges():
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec); case = "COMMAND-EDGES/" + config
        conn = fresh(backend, fk, rec, case); passed = False; detail = ""
        try:
            setup_active(conn); before = state(conn)
            expect_error(lambda: command(conn, "revoked", expected=9), "precondition")
            expect_error(lambda: conn.execute(
                """INSERT INTO authorization_lifecycle_command(
                  id,idempotency_key,authorization_id,expected_generation,target_status,
                  scoped_actor_claim,canonical_request_hash,requested_at_ms,processed_at_ms
                ) VALUES ('bad-time','bad-time','auth1',1,'revoked','claim','hash',?,?)""",
                (NOW, NOW)), "db_time")
            expect_error(lambda: command(conn, "expired", actor="claim:not-system", cid="bad-actor", idem="bad-actor"), "local_system_claim")
            assert state(conn) == before
            command(conn, "revoked", actor="claim:direct-sql")
            expect_error(lambda: conn.execute("UPDATE authorization_lifecycle_command SET scoped_actor_claim='authenticated'"), "append_only")
            expect_error(lambda: conn.execute("DELETE FROM authorization_lifecycle_command"), "append_only")
            passed, detail = True, "direct SQL claim can request deny-terminal transition but is not authenticated or an expansion path"
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk): passed, detail = False, "file integrity/FK check failed"
        conn.close(); record("COMMAND-EDGES", "P1", config, passed, detail, group="ADDITIONAL")


def run_outbox_edges():
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec); case = "OUTBOX-STATE/" + config
        conn = fresh(backend, fk, rec, case); passed = False; detail = ""
        try:
            setup_active(conn); command(conn, "revoked")
            job = conn.execute("SELECT * FROM outbox_job").fetchone(); jid = job["id"]
            expect_error(lambda: conn.execute("UPDATE outbox_job SET status='completed' WHERE id=?", (jid,)), "runtime_transition_invalid")
            expect_error(lambda: conn.execute("DELETE FROM outbox_job WHERE id=?", (jid,)), "terminal_audit")
            claim(conn, jid); now = db_now(conn)
            conn.execute("UPDATE outbox_job SET lease_expires_at_ms=lease_expires_at_ms+1000 WHERE id=?", (jid,))
            conn.execute("UPDATE outbox_job SET status='dead_letter',lease_owner=NULL,lease_expires_at_ms=NULL,last_error_code='E_DEAD' WHERE id=?", (jid,))
            expect_error(lambda: conn.execute("UPDATE outbox_job SET status='pending' WHERE id=?", (jid,)), "runtime_transition_invalid")
            conn.execute("DELETE FROM outbox_job WHERE id=?", (jid,))
            assert conn.execute("SELECT count(*) FROM audit_entry").fetchone()[0] == 1
            TRACES.append({"case": case, "machine": "outbox", "trace": ["pending", "leased", "leased(renew)", "dead_letter", "cleaned"], "at": now})
            passed, detail = True, "legal/illegal transitions, renewal, terminal lock and audited queue cleanup passed"
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk): passed, detail = False, "file integrity/FK check failed"
        conn.close(); record("OUTBOX-STATE", "P1", config, passed, detail, group="ADDITIONAL")


def run_cleanup_retry():
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec); case = "CLEANUP-RETRY/" + config
        conn = fresh(backend, fk, rec, case); passed = False; detail = ""
        try:
            setup_active(conn); command(conn, "revoked"); cleanup_gate(conn)
            conn.execute("UPDATE tombstone SET cleanup_status='cleanup_failed' WHERE subject_type='authorization' AND subject_id='auth1'")
            expect_error(lambda: conn.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")
            conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id='auth1'")
            for table in ("authorization_scope","authorization_action","authorization_policy"):
                conn.execute("DELETE FROM %s WHERE authorization_id='auth1'" % table)
            conn.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_type='authorization' AND subject_id='auth1'")
            TRACES.append({"case": case, "machine": "cleanup", "trace": ["accepted", "active_blocked", "cleanup_pending", "cleanup_failed", "cleanup_pending", "cleaned"]})
            passed, detail = True, "cleanup failure remained blocked and retry completed one-way"
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk): passed, detail = False, "file integrity/FK check failed"
        conn.close(); record("CLEANUP-RETRY", "P2", config, passed, detail, group="ADDITIONAL")


def run_p3044_regression():
    for backend, fk, rec in CONFIGS:
        config = cfg_id(backend, fk, rec); case = "P3-044-CURRENT/" + config
        conn = fresh(backend, fk, rec, case); passed = False; detail = ""
        try:
            setup_active(conn); before = state(conn)
            evil = ("auth1","logical1","evil","cloud","prod","remote","granted",1,1,NOW,"indefinite",None,None,"evil",None,NOW,NOW)
            expect_error(lambda: conn.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", evil), "active_authorization_replace")
            expect_error(lambda: conn.execute("DELETE FROM authorization WHERE id='auth1'"), "active_authorization_delete")
            expect_error(lambda: conn.execute("UPDATE authorization SET processor='cloud' WHERE id='auth1'"), "security_envelope")
            expect_error(lambda: conn.execute("UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'"), "scope_update")
            assert state(conn) == before
            passed, detail = True, "active parent/child/REPLACE/DELETE defenses preserved"
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk): passed, detail = False, "file integrity/FK check failed"
        conn.close(); record("P3-044-CURRENT", "P1", config, passed, detail, group="REGRESSION")


STANDARD = [
    ("AC-01", "P2", ac01), ("AC-02", "P2", ac02), ("AC-03", "P2", ac03),
    ("AC-04", "P2", ac04), ("AC-05", "P2", ac05), ("AC-06", "P1", ac06),
    ("AC-07", "P1", ac07), ("AC-08", "P2", ac08), ("AC-09", "P2", ac09),
    ("AC-10", "P2", ac10), ("AC-11", "P2", ac11), ("AC-12", "P2", ac12),
    ("AC-13", "P2", ac13), ("AC-15", "P1", ac15), ("AC-17", "P2", ac17),
    ("AC-18", "P2", ac18),
]


def summary():
    states = ("PASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")
    out = {}
    for level in ("P0", "P1", "P2"):
        selected = [r for r in RESULTS if r["severity"] == level]
        out[level] = {s: sum(r["status"] == s for r in selected) for s in states}
    out["total"] = {s: sum(r["status"] == s for r in RESULTS) for s in states}
    return out


def p3044_state():
    base = PROJECT / "engineering/LIFEOS-P3-044"
    return {name: {"expected_sha256": expected, "actual_sha256": digest(base / name),
                   "matches_expected": digest(base / name) == expected}
            for name, expected in P3_044_EXPECTED.items()}


def run_p31():
    result = subprocess.run(["sh", str(P31_SHELL)], cwd=PROJECT.parent,
                            text=True, capture_output=True)
    (EVIDENCE / "regressions/p3_031_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    shutil.copyfile(PROJECT / "engineering/LIFEOS-P3-031/evidence/test_results.json",
                    EVIDENCE / "regressions/p3_031_test_results.json")
    return result.returncode


def write_evidence(p31_exit, preservation):
    stats = summary()
    ac_map = {}
    for ac in ("AC-%02d" % i for i in range(1, 19)):
        items = [r for r in RESULTS if r["id"] == ac]
        ac_map[ac] = {"instances": len(items), "pass": sum(r["status"] == "PASS" for r in items),
                      "fail": sum(r["status"] == "FAIL" for r in items),
                      "not_implemented": sum(r["status"] == "NOT_IMPLEMENTED" for r in items),
                      "unknown": sum(r["status"] == "UNKNOWN" for r in items)}
    (EVIDENCE / "test_results.json").write_text(json.dumps({
        "task_id": "LIFEOS-P3-046", "route": "gpt-5.6-sol+xhigh",
        "scope": "synthetic SQLite only", "summary": stats,
        "p3_031_exit": p31_exit, "ac_coverage": ac_map, "results": RESULTS,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "atomic_snapshots.json").write_text(json.dumps(SNAPSHOTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "state_machine_traces.json").write_text(json.dumps(TRACES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(json.dumps({
        "all_passed": all(x["passed"] for x in INTEGRITY), "results": INTEGRITY,
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "environment.json").write_text(json.dumps({
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "platform": platform.platform(), "machine": platform.machine(),
        "network_used": False, "real_db_vault_file_tauri_ipc_used": False,
        "real_migration_executed": False, "database_paths": DATABASES,
        "pragma_matrix": {"foreign_keys": ["ON", "OFF"], "recursive_triggers": ["ON", "OFF"]},
        "data_classification": "synthetic only",
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/p3_044_preservation.json").write_text(json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps({
        "candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
        "p3_031_tests": digest(P31_TESTS), "p3_031_shell": digest(P31_SHELL),
        "p3_046_runner": digest(Path(__file__)),
    }, indent=2) + "\n", encoding="utf-8")
    return stats, ac_map


def main():
    for path in (SNAPSHOT.parent, EVIDENCE / "checks", EVIDENCE / "input", EVIDENCE / "regressions", WORK):
        path.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    before = p3044_state()
    if not all(x["matches_expected"] for x in before.values()):
        print("P3-044 preservation baseline mismatch", file=sys.stderr); return 2
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    p31_exit = run_p31()
    for ac, severity, scenario in STANDARD:
        run_standard(ac, severity, scenario)
    run_retirement_matrix()
    run_fault_matrix()
    run_command_edges()
    run_outbox_edges()
    run_cleanup_retry()
    run_p3044_regression()
    after = p3044_state()
    preservation = {name: {"expected_sha256": P3_044_EXPECTED[name],
                           "before_sha256": before[name]["actual_sha256"],
                           "after_sha256": after[name]["actual_sha256"],
                           "unchanged": before[name]["actual_sha256"] == after[name]["actual_sha256"]
                                        and after[name]["matches_expected"]}
                    for name in P3_044_EXPECTED}
    stats, ac_map = write_evidence(p31_exit, preservation)
    for row in RESULTS:
        print("%-12s %-16s %-28s %s" % (row["group"], row["id"], row["config"], row["status"]))
    print("SUMMARY " + json.dumps(stats, sort_keys=True))
    print("AC_COVERAGE " + json.dumps(ac_map, sort_keys=True))
    print("P3_031_EXIT", p31_exit)
    print("P3_044_PRESERVED", all(x["unchanged"] for x in preservation.values()))
    bad = p31_exit != 0 or any(r["status"] != "PASS" for r in RESULTS)
    bad = bad or not all(x["passed"] for x in INTEGRITY)
    bad = bad or not all(x["unchanged"] for x in preservation.values())
    bad = bad or any(v["instances"] == 0 or v["fail"] or v["not_implemented"] or v["unknown"] for v in ac_map.values())
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
