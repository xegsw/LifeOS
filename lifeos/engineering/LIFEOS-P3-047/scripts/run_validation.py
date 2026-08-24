#!/usr/bin/env python3
"""P3-047 synthetic SQLite remediation and regression runner.

Only new in-memory and task-local file databases are used. P3-046 and PM
counterexample assets are hash-checked read-only baselines.
"""

import hashlib
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
LIFEOS = TASK.parents[1]
ROOT = LIFEOS.parent
CANDIDATE = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
P31_SHELL = LIFEOS / "engineering/LIFEOS-P3-031/scripts/run_validation.sh"
P31_TESTS = LIFEOS / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py"
SNAPSHOT = TASK / "input/001_candidate_schema.sql"
EVIDENCE = TASK / "evidence"
WORK = TASK / "work"
NOW = 1786550400000
RESULTS, SNAPSHOTS, TRACES, INTEGRITY, DATABASES = [], [], [], [], []

READ_ONLY = {
    "lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md": "94dac087ee1dfacbdf9b448b7fef08a90109ee7282a89293739342b9dbb800b9",
    "lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md": "9ef071fa5c74c2283125b48f0cc8c91c07f3f667849c2eac1cc14f0654a463fb",
    "lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.py": "106a959cb9dedd49d8b2866e80aef3f4ee7010bf26800d7b3da9d83a4d851e4a",
    "lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.sh": "268c4c0a6a04017222cc1d1838fd9c1c3baa0d930f66087ef4767eaf142bd028",
    "lifeos/engineering/LIFEOS-P3-046/evidence/test_results.json": "6e918b089196077bbca7e6ac0ee24b122ab2c9fb4eeb2ab358d514a622b332bb",
    "lifeos/engineering/LIFEOS-P3-046/evidence/test_run.log": "152ef9022c18ed3bfd0c566bb50f4e9564a3f461e2fff737038666914427dce9",
    "lifeos/engineering/LIFEOS-P3-046/evidence/atomic_snapshots.json": "6acd7d65c92752b61b96174d04a28c3320314cff260bf6d280e0267c6bca38dd",
    "lifeos/engineering/LIFEOS-P3-046/evidence/state_machine_traces.json": "9484580f4ff676081fb128cc935709510baa02244333fc45ce72f7d95e2fa56f",
    "lifeos/engineering/LIFEOS-P3-046/evidence/environment.json": "98e16eae0c263606cb92e71916b70b62b5a69437e4b46371967cf8842817f805",
    "lifeos/engineering/LIFEOS-P3-046/evidence/checks/integrity_and_fk.json": "ffb7557407eb113d269e5042f1758ddf6f95457260f8d13420932d825279ef3c",
    "lifeos/engineering/LIFEOS-P3-046/evidence/input/p3_044_preservation.json": "349b7befca98472416503d4b38da9e790a4b365efddf739a8a08b1fc63080593",
    "lifeos/engineering/LIFEOS-P3-046/evidence/input/source_hashes.json": "19e1c9a58d77dd85e6120b99278975a23d6d865d38336b4c89fb9254c4eecd1b",
    "lifeos/engineering/LIFEOS-P3-046/evidence/regressions/p3_031_test_results.json": "7fb8bbc1f688267efc84c17674f2f527f6c2c6fe54f0a81e393c20340b0319a5",
    "lifeos/engineering/LIFEOS-P3-046/evidence/regressions/p3_031_test_run.log": "fe20e2f76225199e647c892f78c6fe365a0b2ebb77ff433190083b6c447b5600",
    "lifeos/reviews/LIFEOS-P3-046_pm_review.md": "0ce9b79aa212065f53b9f8a7cffe10e7a1587b6e37b5ab5acb7305b2260a04b5",
    "lifeos/reviews/LIFEOS-P3-046/evidence/MANIFEST.md": "b5f3c954f932f068cd192ba74a792e2a0c55f47fb93132e98bf94d9909286aaf",
    "lifeos/reviews/LIFEOS-P3-046/evidence/pm_counterexample_attacks.py": "725dc0b2a4e36e9eac9949c9dbc9cb969493a67c303f5684ad268d63d8edb777",
    "lifeos/reviews/LIFEOS-P3-046/evidence/counterexample_results.json": "541fe7980e7ab7d4ce6c38188aeacac477813760ff0810ada0cfee40ff16e560",
}

CONFIGS = [(b, fk, rec) for b in ("memory", "file") for fk in (True, False) for rec in (True, False)]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db_now(conn):
    return conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]


def request_hash(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def cfg_name(backend, fk, rec):
    return "%s-fk_%s-rec_%s" % (backend, "on" if fk else "off", "on" if rec else "off")


def fresh(backend, fk, rec, case):
    if backend == "memory":
        path = ":memory:"
    else:
        target = WORK / (case.replace("/", "_").replace(":", "_") + ".db")
        target.unlink(missing_ok=True)
        path = str(target)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if rec else "OFF"))
    assert bool(conn.execute("PRAGMA foreign_keys").fetchone()[0]) == fk
    assert bool(conn.execute("PRAGMA recursive_triggers").fetchone()[0]) == rec
    DATABASES.append(path)
    return conn


def project(conn):
    if not conn.execute("SELECT 1 FROM project WHERE id='p1'").fetchone():
        conn.execute("INSERT INTO project VALUES ('p1','Synthetic','test','active',1,?,?,?)", (NOW, NOW, NOW))


def active(conn, aid="auth1", logical="logical1", version=1, supersedes=None,
           processor="local", policy="policy@1"):
    project(conn)
    conn.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (aid, logical, "actor:user", processor, "test", "device", "proposed",
                  version, 1, NOW, "indefinite", None, None, policy, supersedes, NOW, NOW))
    conn.execute("INSERT INTO authorization_scope VALUES (?,?, 'allow','p1',NULL,NULL)", (aid + ":scope", aid))
    conn.execute("INSERT INTO authorization_action VALUES (?,?, 'read')", (aid + ":action", aid))
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                 (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (aid,))


def retire(conn, status, aid="auth1", expected=1, cid=None, idem=None,
           actor=None, canonical=None):
    token = "%s:%s:%s" % (aid, expected + 1, status)
    idem = idem or ("idem:" + token)
    canonical = canonical or request_hash("authorization-lifecycle:" + token)
    actor = actor or ("system:local" if status == "expired" else "actor:user")
    command = {"revoked": "revoke_authorization", "expired": "expire_authorization",
               "superseded": "supersede_authorization"}[status]
    conn.execute("SAVEPOINT lifecycle")
    try:
        conn.execute("INSERT INTO submission VALUES ('destruct@1',?,?,?,?,NULL,?)",
                     (idem, canonical, command, aid, NOW))
        conn.execute("""INSERT INTO authorization_lifecycle_command(
          id,idempotency_key,authorization_id,expected_generation,target_status,
          scoped_actor_claim,canonical_request_hash,requested_at_ms
        ) VALUES (?,?,?,?,?,?,?,?)""",
                     (cid or ("cmd:" + token), idem, aid, expected, status, actor, canonical, NOW))
        conn.execute("RELEASE lifecycle")
    except sqlite3.DatabaseError:
        conn.execute("ROLLBACK TO lifecycle")
        conn.execute("RELEASE lifecycle")
        raise


def runtime(conn, jid, operation, worker=None, expiry=None, available=None,
            error=None, overrides=None, command_id=None):
    row = conn.execute("SELECT * FROM outbox_job WHERE id=?", (jid,)).fetchone()
    assert row is not None
    expected = {
        "status": row["status"], "available": row["available_at_ms"],
        "owner": row["lease_owner"], "generation": row["lease_generation"],
        "expiry": row["lease_expires_at_ms"],
    }
    if overrides:
        expected.update(overrides)
    seq = conn.execute("SELECT count(*) FROM outbox_runtime_command WHERE job_id=?", (jid,)).fetchone()[0] + 1
    conn.execute("""INSERT INTO outbox_runtime_command(
      id,job_id,operation,expected_status,expected_available_at_ms,
      expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,
      requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,
      error_code,requested_at_ms
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (command_id or "runtime:%s:%s:%s" % (jid, operation, seq), jid, operation,
                  expected["status"], expected["available"], expected["owner"],
                  expected["generation"], expected["expiry"], worker, expiry,
                  available, error, NOW))


def claim(conn, jid, owner="worker:a", delta=60000):
    now = db_now(conn)
    runtime(conn, jid, "claim", worker=owner, expiry=now + delta)


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


def table_rows(conn, table, order="1"):
    return [list(x) for x in conn.execute("SELECT * FROM %s ORDER BY %s" % (table, order))]


def state(conn):
    return {name: table_rows(conn, table) for name, table in (
        ("authorization", "authorization"), ("scope", "authorization_scope"),
        ("action", "authorization_action"), ("policy", "authorization_policy"),
        ("submission", "submission"), ("lifecycle", "authorization_lifecycle_command"),
        ("audit", "audit_entry"), ("outbox", "outbox_job"),
        ("runtime", "outbox_runtime_command"), ("tombstone", "tombstone"),
    )}


def expect_error(fn, contains=None):
    try:
        fn()
    except sqlite3.DatabaseError as exc:
        if contains and contains not in str(exc):
            raise AssertionError("unexpected %r; expected %r" % (str(exc), contains))
        return str(exc)
    raise AssertionError("operation unexpectedly succeeded")


def record(group, ident, severity, config, passed, detail, **extra):
    row = {"group": group, "id": ident, "severity": severity, "config": config,
           "status": "PASS" if passed else "FAIL", "detail": detail}
    row.update(extra); RESULTS.append(row)


def health(conn, case, fk):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [list(x) for x in conn.execute("PRAGMA foreign_key_check")]
    passed = integrity == quick == "ok" and not foreign
    INTEGRITY.append({"case": case, "foreign_keys_enabled": fk,
                      "integrity_check": integrity, "quick_check": quick,
                      "foreign_key_check": foreign, "passed": passed})
    return passed


def run_standard(group, ident, severity, scenario):
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec); case = "%s/%s/%s" % (group, ident, config)
        conn = fresh(backend, fk, rec, case); passed = False
        try:
            detail = scenario(conn, case) or "contract held"; passed = True
        except Exception as exc:
            detail = "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk):
            passed, detail = False, "file integrity/FK check failed"
        conn.close(); record(group, ident, severity, config, passed, detail)


def ac01(c, case):
    active(c); corr = "authorization-state:auth1:2:revoked"
    c.execute("INSERT INTO audit_entry VALUES ('pre','authorization.revoke','claim','auth1',1,'ok',?,?)", (NOW, corr))
    before = state(c); expect_error(lambda: retire(c, "revoked"), "audit_entry_reinsert")
    assert state(c) == before; SNAPSHOTS.append({"case": case, "kind": "prewrite_rollback", "before": before, "after": state(c)})


def ac02(c, case):
    c.execute("INSERT INTO audit_entry VALUES ('a','test','claim','s',NULL,'ok',?,'corr')", (NOW,))
    before = table_rows(c, "audit_entry")
    expect_error(lambda: c.execute("UPDATE audit_entry SET result_code='x'"), "append_only")
    expect_error(lambda: c.execute("DELETE FROM audit_entry"), "append_only")
    expect_error(lambda: c.execute("INSERT OR REPLACE INTO audit_entry VALUES ('a','x','x','x',NULL,'x',?,'corr')", (NOW,)), "reinsert")
    assert table_rows(c, "audit_entry") == before


def ac03(c, case):
    active(c); before = state(c)
    expect_error(lambda: c.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'", (NOW, NOW)), "lifecycle_command")
    assert state(c) == before


def ac04(c, case):
    active(c); retire(c, "revoked"); before = state(c)
    expect_error(lambda: retire(c, "revoked", cid="replay"))
    assert state(c) == before


def ac05(c, case):
    active(c); retire(c, "revoked"); job = c.execute("SELECT * FROM outbox_job").fetchone(); before = tuple(job)
    expect_error(lambda: c.execute("UPDATE outbox_job SET subject_id='other' WHERE id=?", (job["id"],)), "payload_immutable")
    expect_error(lambda: c.execute("UPDATE outbox_job SET payload_ref='active' WHERE id=?", (job["id"],)), "payload_immutable")
    expect_error(lambda: c.execute("INSERT OR REPLACE INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", before), "reinsert")


def ac06(c, case):
    active(c); retire(c, "revoked"); jid = c.execute("SELECT id FROM outbox_job").fetchone()[0]
    claim(c, jid); runtime(c, jid, "complete")
    assert c.execute("SELECT status FROM outbox_job WHERE id=?", (jid,)).fetchone()[0] == "completed"
    TRACES.append({"case": case, "machine": "outbox", "trace": ["pending", "leased", "completed"]})


def ac07(c, case):
    active(c); now = db_now(c)
    c.execute("INSERT INTO outbox_job VALUES ('stale','publish','authorization','auth1',2,NULL,'pending',0,?,NULL,0,NULL,'stale',NULL)", (now,))
    claim(c, "stale")
    expect_error(lambda: runtime(c, "stale", "complete"), "invalid")
    assert c.execute("SELECT status FROM outbox_job WHERE id='stale'").fetchone()[0] == "leased"


def ac08(c, case):
    active(c); retire(c, "expired"); job = c.execute("SELECT * FROM outbox_job").fetchone(); jid = job["id"]
    payload = tuple(job[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key"))
    claim(c, jid); runtime(c, jid, "retry", available=db_now(c) + 1000, error="E_RETRY")
    row = c.execute("SELECT * FROM outbox_job WHERE id=?", (jid,)).fetchone()
    assert row["status"] == "pending" and row["attempts"] == 1
    assert tuple(row[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key")) == payload


def ac09(c, case):
    active(c); expect_error(lambda: c.execute("UPDATE authorization SET generation=2 WHERE id='auth1'"), "lifecycle_command")


def ac10(c, case):
    active(c); expect_error(lambda: c.execute("UPDATE authorization SET created_at_ms=created_at_ms-1 WHERE id='auth1'"), "created_at")
    expect_error(lambda: c.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW,)), "revoked_time")


def ac11(c, case):
    active(c); expect_error(lambda: c.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'", (NOW - 1, NOW - 2)), "lifecycle_command")
    retire(c, "revoked"); parent = c.execute("SELECT * FROM authorization").fetchone(); audit = c.execute("SELECT * FROM audit_entry").fetchone()
    assert parent["updated_at_ms"] == parent["revoked_at_ms"] == audit["occurred_at_ms"]


def ac12(c, case):
    active(c); retire(c, "revoked"); before = tuple(c.execute("SELECT * FROM authorization").fetchone())
    expect_error(lambda: c.execute("UPDATE authorization SET processor='evil'"), "terminal_authorization_immutable")
    expect_error(lambda: c.execute("DELETE FROM authorization"), "terminal_authorization_delete")
    expect_error(lambda: c.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", before), "terminal_authorization_replace")


def ac13(c, case):
    active(c); retire(c, "expired")
    expect_error(lambda: c.execute("INSERT INTO authorization_scope VALUES ('x','auth1','deny','p1',NULL,NULL)"), "terminal_authorization_scope_insert")
    expect_error(lambda: c.execute("UPDATE authorization_action SET action='export_candidate'"), "terminal_authorization_action_update")
    expect_error(lambda: c.execute("DELETE FROM authorization_policy"), "requires_cleanup")


def ac15(c, case):
    active(c, "old", "versioned"); retire(c, "superseded", "old"); before = tuple(c.execute("SELECT * FROM authorization WHERE id='old'").fetchone())
    active(c, "new", "versioned", 2, "old", "approved", "policy@2")
    assert tuple(c.execute("SELECT * FROM authorization WHERE id='old'").fetchone()) == before


def ac17(c, case):
    active(c); expect_error(lambda: c.execute("INSERT INTO tombstone VALUES ('authorization','auth1',1,'x','cleanup',?,'accepted',?)", (NOW, NOW)), "terminal_generation")
    retire(c, "revoked"); expect_error(lambda: c.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")


def ac18(c, case):
    active(c); retire(c, "revoked"); cleanup_gate(c); before = state(c)
    for table in ("authorization_scope", "authorization_action", "authorization_policy"):
        c.execute("DELETE FROM %s WHERE authorization_id='auth1'" % table)
    c.execute("UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization'")
    assert c.execute("SELECT count(*) FROM audit_entry").fetchone()[0] == 2
    SNAPSHOTS.append({"case": case, "kind": "controlled_cleanup", "before": before, "after": state(c)})


STANDARD_AC = [("AC-%02d" % n, "P1" if n in (6, 7, 15) else "P2", fn) for n, fn in (
    (1, ac01), (2, ac02), (3, ac03), (4, ac04), (5, ac05), (6, ac06),
    (7, ac07), (8, ac08), (9, ac09), (10, ac10), (11, ac11), (12, ac12),
    (13, ac13), (15, ac15), (17, ac17), (18, ac18))]


def run_ac14():
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for terminal in ("revoked", "expired", "superseded"):
            for tx in ("autocommit", "commit", "rollback"):
                case = "AC/AC-14/%s/%s/%s" % (terminal, config, tx); c = fresh(backend, fk, rec, case)
                passed = False
                try:
                    active(c); before = state(c)
                    if tx != "autocommit": c.execute("BEGIN IMMEDIATE")
                    retire(c, terminal)
                    inside = state(c)
                    if tx == "rollback":
                        c.rollback(); after = state(c); assert after == before
                    else:
                        if tx == "commit": c.commit()
                        after = state(c); parent = c.execute("SELECT status,generation FROM authorization").fetchone()
                        assert tuple(parent) == (terminal, 2) and len(after["audit"]) == len(after["outbox"]) == 1
                    SNAPSHOTS.append({"case": case, "kind": "retirement_atomicity", "before": before, "inside": inside, "after": after})
                    passed, detail = True, "bound Submission + retirement evidence atomic"
                except Exception as exc:
                    try: c.rollback()
                    except sqlite3.DatabaseError: pass
                    detail = "%s: %s" % (type(exc).__name__, exc)
                if backend == "file" and not health(c, case, fk): passed, detail = False, "integrity failed"
                c.close(); record("AC", "AC-14", "P1", config, passed, detail, terminal=terminal, transaction=tx)


def run_ac16():
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for fault in ("audit", "outbox"):
            case = "AC/AC-16/%s/%s" % (fault, config); c = fresh(backend, fk, rec, case); passed = False
            try:
                active(c); corr = "authorization-state:auth1:2:revoked"
                if fault == "audit":
                    c.execute("INSERT INTO audit_entry VALUES ('pre','authorization.revoke','claim','auth1',1,'ok',?,?)", (NOW, corr))
                else:
                    c.execute("INSERT INTO outbox_job VALUES ('pre','authorization_state_change','authorization','auth1',2,'revoked','pending',0,?,NULL,0,NULL,?,NULL)", (NOW, corr))
                before = state(c); expect_error(lambda: retire(c, "revoked")); after = state(c); assert after == before
                SNAPSHOTS.append({"case": case, "kind": fault + "_rollback", "before": before, "after": after})
                passed, detail = True, "fault rolled back Submission/command/evidence"
            except Exception as exc: detail = "%s: %s" % (type(exc).__name__, exc)
            if backend == "file" and not health(c, case, fk): passed, detail = False, "integrity failed"
            c.close(); record("AC", "AC-16", "P1", config, passed, detail, fault=fault)


def ce01(c, case):
    active(c); valid = request_hash("valid")
    sql = """INSERT INTO authorization_lifecycle_command(
      id,idempotency_key,authorization_id,expected_generation,target_status,
      scoped_actor_claim,canonical_request_hash,requested_at_ms) VALUES (?,?,?,?,?,?,?,?)"""
    expect_error(lambda: c.execute(sql, ("bad", "bad", "auth1", 1, "revoked", "actor:user", "x", NOW)))
    expect_error(lambda: c.execute(sql, ("missing", "missing", "auth1", 1, "revoked", "actor:user", valid, NOW)), "submission_binding")
    c.execute("INSERT INTO submission VALUES ('destruct@1','mismatch',?,'revoke_authorization','other',NULL,?)", (valid, NOW))
    expect_error(lambda: c.execute(sql, ("subject", "mismatch", "auth1", 1, "revoked", "actor:user", valid, NOW)), "submission_binding")
    before = state(c); c.execute("BEGIN IMMEDIATE"); retire(c, "revoked", idem="rollback")
    inside = state(c); c.rollback(); assert state(c) == before
    retire(c, "revoked"); submission = tuple(c.execute("SELECT * FROM submission WHERE idempotency_key LIKE 'idem:%'").fetchone())
    expect_error(lambda: c.execute("UPDATE submission SET result_subject_id='evil' WHERE idempotency_key LIKE 'idem:%'"), "append_only")
    expect_error(lambda: c.execute("DELETE FROM submission WHERE idempotency_key LIKE 'idem:%'"), "append_only")
    SNAPSHOTS.append({"case": case, "kind": "submission_command_atomicity", "before": before, "inside": inside, "after_rollback": before, "bound_submission": list(submission)})


def ce02(c, case):
    now = db_now(c); future = now + 86400000
    c.execute("INSERT INTO outbox_job VALUES ('future','generic','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'future',NULL)", (future,))
    expect_error(lambda: runtime(c, "future", "claim", worker="w", expiry=now + 60000), "invalid")
    expect_error(lambda: c.execute("UPDATE outbox_job SET status='leased',attempts=1,lease_owner='w',lease_generation=1,lease_expires_at_ms=? WHERE id='future'", (now + 60000,)), "runtime_command_required")
    c.execute("INSERT INTO outbox_job VALUES ('boundary','generic','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'boundary',NULL)", (now,))
    claim(c, "boundary", "winner")
    expect_error(lambda: runtime(c, "boundary", "claim", worker="loser", expiry=now + 60000,
                                 overrides={"status": "pending", "owner": None, "generation": 0, "expiry": None}), "cas_mismatch")
    assert c.execute("SELECT lease_owner FROM outbox_job WHERE id='boundary'").fetchone()[0] == "winner"
    TRACES.append({"case": case, "machine": "claim", "trace": ["future denied", "boundary accepted", "stale competitor denied"]})


def ce03(c, case):
    active(c); retire(c, "revoked"); jid = c.execute("SELECT id FROM outbox_job").fetchone()[0]; claim(c, jid, "owner")
    expect_error(lambda: c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id=?", (jid,)), "runtime_command_required")
    expect_error(lambda: runtime(c, jid, "complete", overrides={"owner": "wrong"}), "cas_mismatch")
    expect_error(lambda: runtime(c, jid, "complete", overrides={"generation": 0}), "cas_mismatch")
    runtime(c, jid, "renew", worker="owner", expiry=c.execute("SELECT lease_expires_at_ms FROM outbox_job WHERE id=?", (jid,)).fetchone()[0] + 1000)
    runtime(c, jid, "complete"); assert c.execute("SELECT status FROM outbox_job WHERE id=?", (jid,)).fetchone()[0] == "completed"
    TRACES.append({"case": case, "machine": "worker_cas", "trace": ["claim", "wrong owner/gen denied", "renew", "complete"]})


def mutate_tombstone(c, aid):
    attacks = ("subject_type='artifact'", "subject_id='ghost'", "generation=generation+1",
               "command_id='forged'", "reason_code='forged'", "blocked_at_ms=0")
    for assignment in attacks:
        expect_error(lambda assignment=assignment: c.execute(
            "UPDATE tombstone SET %s WHERE subject_type='authorization' AND subject_id=?" % assignment, (aid,)), "control_envelope")
    expect_error(lambda: c.execute("UPDATE tombstone SET updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (aid,)), "time_requires_status_change")


def ce04(c, case):
    targets = ("accepted", "active_blocked", "cleanup_pending", "cleanup_failed", "vendor_limited", "cleaned")
    snapshots = []
    for index, target in enumerate(targets):
        aid = "auth%s" % index; active(c, aid, "logical%s" % index); retire(c, "revoked", aid)
        row = c.execute("SELECT version_no,generation FROM authorization WHERE id=?", (aid,)).fetchone(); corr = "authorization-cleanup:%s:%s" % (aid, row["generation"])
        c.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)", ("audit:" + corr, "authorization.cleanup", "claim", aid, row["version_no"], "redacted_by_user", NOW, corr))
        c.execute("INSERT INTO tombstone VALUES ('authorization',?,?,?,'user_cleanup',?,'accepted',?)", (aid, row["generation"], "cleanup:" + aid, NOW, NOW))
        if target != "accepted": c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id=?", (aid,))
        if target not in ("accepted", "active_blocked"): c.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_id=?", (aid,))
        if target in ("cleanup_failed", "vendor_limited"):
            c.execute("UPDATE tombstone SET cleanup_status=? WHERE subject_id=?", (target, aid))
        if target == "cleaned":
            for table in ("authorization_scope", "authorization_action", "authorization_policy"):
                c.execute("DELETE FROM %s WHERE authorization_id=?" % table, (aid,))
            c.execute("UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 WHERE subject_id=?", (aid,))
        before = tuple(c.execute("SELECT * FROM tombstone WHERE subject_id=?", (aid,)).fetchone()); mutate_tombstone(c, aid)
        assert tuple(c.execute("SELECT * FROM tombstone WHERE subject_id=?", (aid,)).fetchone()) == before
        snapshots.append({"status": target, "row": list(before)})
    SNAPSHOTS.append({"case": case, "kind": "tombstone_envelope_all_states", "states": snapshots})


def run_retention():
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for mode in ("unconfigured", "before", "at", "generic"):
            case = "PM-CE/PM-CE-05/%s/%s" % (mode, config); c = fresh(backend, fk, rec, case); passed = False
            try:
                now = db_now(c)
                if mode == "generic":
                    c.execute("INSERT INTO outbox_job VALUES ('g','generic','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'g',NULL)", (now,))
                    claim(c, "g"); runtime(c, "g", "dead_letter", error="E"); c.execute("DELETE FROM outbox_job WHERE id='g'")
                else:
                    if mode == "before": c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',60000)")
                    if mode == "at": c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
                    active(c); retire(c, "revoked"); jid = c.execute("SELECT id FROM outbox_job").fetchone()[0]
                    claim(c, jid); runtime(c, jid, "complete")
                    if mode in ("unconfigured", "before"):
                        expect_error(lambda: c.execute("DELETE FROM outbox_job WHERE id=?", (jid,)), "retention_not_satisfied")
                    else:
                        c.execute("DELETE FROM outbox_job WHERE id=?", (jid,))
                        assert c.execute("SELECT count(*) FROM authorization").fetchone()[0] == 1
                        assert c.execute("SELECT count(*) FROM audit_entry").fetchone()[0] == 1
                passed, detail = True, "retention %s contract held" % mode
                TRACES.append({"case": case, "machine": "retention", "trace": [mode, "PASS"]})
            except Exception as exc: detail = "%s: %s" % (type(exc).__name__, exc)
            if backend == "file" and not health(c, case, fk): passed, detail = False, "integrity failed"
            c.close(); record("PM-CE", "PM-CE-05", "P2", config, passed, detail, retention_case=mode)

    # One real DB-clock tick proves strictly-after eligibility without eight sleeps.
    c = fresh("memory", True, True, "PM-CE/PM-CE-05/after")
    try:
        c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
        active(c); retire(c, "revoked"); jid = c.execute("SELECT id FROM outbox_job").fetchone()[0]
        claim(c, jid); runtime(c, jid, "complete"); terminal_at = c.execute("SELECT max(processed_at_ms) FROM outbox_runtime_command WHERE job_id=?", (jid,)).fetchone()[0]
        deadline = time.time() + 2
        while db_now(c) <= terminal_at and time.time() < deadline: time.sleep(0.01)
        assert db_now(c) > terminal_at; c.execute("DELETE FROM outbox_job WHERE id=?", (jid,))
        record("PM-CE", "PM-CE-05", "P2", "memory-fk_on-rec_on", True, "strictly-after retention accepted", retention_case="after")
    except Exception as exc:
        record("PM-CE", "PM-CE-05", "P2", "memory-fk_on-rec_on", False, "%s: %s" % (type(exc).__name__, exc), retention_case="after")
    c.close()


def run_expired_lease():
    pending = []
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec); case = "PM-CE/PM-CE-03/expired/%s" % config
        c = fresh(backend, fk, rec, case); active(c); retire(c, "revoked"); jid = c.execute("SELECT id FROM outbox_job").fetchone()[0]
        claim(c, jid, "owner", 1); expiry = c.execute("SELECT lease_expires_at_ms FROM outbox_job WHERE id=?", (jid,)).fetchone()[0]
        pending.append((backend, fk, config, case, c, jid, expiry))
    deadline = time.time() + 2
    while pending and db_now(pending[0][4]) <= max(x[6] for x in pending) and time.time() < deadline: time.sleep(0.01)
    for backend, fk, config, case, c, jid, expiry in pending:
        try:
            expect_error(lambda c=c, jid=jid: runtime(c, jid, "complete"), "invalid")
            passed, detail = True, "expired lease completion rejected"
        except Exception as exc: passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(c, case, fk): passed, detail = False, "integrity failed"
        c.close(); record("PM-CE", "PM-CE-03", "P1", config, passed, detail, lease_case="expired")


def p3044(c, case):
    active(c); before = state(c)
    evil = ("auth1","logical1","evil","cloud","prod","remote","granted",1,1,NOW,"indefinite",None,None,"evil",None,NOW,NOW)
    expect_error(lambda: c.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", evil), "active_authorization_replace")
    expect_error(lambda: c.execute("DELETE FROM authorization WHERE id='auth1'"), "active_authorization_delete")
    expect_error(lambda: c.execute("UPDATE authorization SET processor='cloud'"), "security_envelope")
    expect_error(lambda: c.execute("UPDATE authorization_scope SET effect='deny'"), "scope_update")
    assert state(c) == before


def read_only_state():
    return {name: {"expected_sha256": expected, "actual_sha256": digest(ROOT / name),
                   "matches_expected": digest(ROOT / name) == expected}
            for name, expected in READ_ONLY.items()}


def run_p31():
    result = subprocess.run(["sh", str(P31_SHELL)], cwd=ROOT, text=True, capture_output=True)
    (EVIDENCE / "regressions/p3_031_test_run.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    shutil.copyfile(LIFEOS / "engineering/LIFEOS-P3-031/evidence/test_results.json",
                    EVIDENCE / "regressions/p3_031_test_results.json")
    return result.returncode


def summary():
    states = ("PASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")
    out = {}
    for level in ("P0", "P1", "P2"):
        chosen = [x for x in RESULTS if x["severity"] == level]
        out[level] = {s: sum(x["status"] == s for x in chosen) for s in states}
    out["total"] = {s: sum(x["status"] == s for x in RESULTS) for s in states}
    return out


def write_evidence(p31_exit, preservation):
    stats = summary()
    coverage = {}
    for ident in ["AC-%02d" % x for x in range(1, 19)] + ["PM-CE-%02d" % x for x in range(1, 6)]:
        rows = [x for x in RESULTS if x["id"] == ident]
        coverage[ident] = {"instances": len(rows), "pass": sum(x["status"] == "PASS" for x in rows),
                           "fail": sum(x["status"] == "FAIL" for x in rows),
                           "not_implemented": sum(x["status"] == "NOT_IMPLEMENTED" for x in rows),
                           "unknown": sum(x["status"] == "UNKNOWN" for x in rows)}
    (EVIDENCE / "test_results.json").write_text(json.dumps({
        "task_id": "LIFEOS-P3-047", "route": "gpt-5.6-sol+xhigh",
        "scope": "synthetic SQLite only", "summary": stats, "p3_031_exit": p31_exit,
        "coverage": coverage, "results": RESULTS,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "atomic_snapshots.json").write_text(json.dumps(SNAPSHOTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "state_machine_traces.json").write_text(json.dumps(TRACES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(json.dumps({"all_passed": all(x["passed"] for x in INTEGRITY), "results": INTEGRITY}, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "environment.json").write_text(json.dumps({
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "platform": platform.platform(), "machine": platform.machine(),
        "network_used": False, "real_db_vault_file_tauri_ipc_used": False,
        "real_migration_executed": False, "data_classification": "synthetic only",
        "pragma_matrix": {"foreign_keys": ["ON", "OFF"], "recursive_triggers": ["ON", "OFF"]},
        "database_paths": DATABASES,
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/read_only_preservation.json").write_text(json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps({
        "candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
        "p3_031_tests": digest(P31_TESTS), "p3_031_shell": digest(P31_SHELL),
        "p3_047_runner": digest(Path(__file__)),
    }, indent=2) + "\n", encoding="utf-8")
    return stats, coverage


def main():
    for path in (SNAPSHOT.parent, EVIDENCE / "checks", EVIDENCE / "input", EVIDENCE / "regressions", WORK):
        path.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"): old.unlink()
    before = read_only_state()
    if not all(x["matches_expected"] for x in before.values()):
        print("read-only baseline mismatch", file=sys.stderr); return 2
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    p31_exit = run_p31()
    for ident, severity, scenario in STANDARD_AC: run_standard("AC", ident, severity, scenario)
    run_ac14(); run_ac16()
    run_standard("PM-CE", "PM-CE-01", "P2", ce01)
    run_standard("PM-CE", "PM-CE-02", "P1", ce02)
    run_standard("PM-CE", "PM-CE-03", "P1", ce03)
    run_expired_lease()
    run_standard("PM-CE", "PM-CE-04", "P2", ce04)
    run_retention()
    run_standard("REGRESSION", "P3-044-CURRENT", "P1", p3044)
    after = read_only_state()
    preservation = {name: {"expected_sha256": READ_ONLY[name],
                           "before_sha256": before[name]["actual_sha256"],
                           "after_sha256": after[name]["actual_sha256"],
                           "unchanged": before[name]["actual_sha256"] == after[name]["actual_sha256"]
                                        and after[name]["matches_expected"]}
                    for name in READ_ONLY}
    stats, coverage = write_evidence(p31_exit, preservation)
    for row in RESULTS: print("%-12s %-16s %-28s %s" % (row["group"], row["id"], row["config"], row["status"]))
    print("SUMMARY " + json.dumps(stats, sort_keys=True))
    print("COVERAGE " + json.dumps(coverage, sort_keys=True))
    print("P3_031_EXIT", p31_exit)
    print("READ_ONLY_PRESERVED", all(x["unchanged"] for x in preservation.values()))
    bad = p31_exit != 0 or any(x["status"] != "PASS" for x in RESULTS)
    bad = bad or not all(x["passed"] for x in INTEGRITY)
    bad = bad or not all(x["unchanged"] for x in preservation.values())
    bad = bad or any(v["instances"] == 0 or v["fail"] or v["not_implemented"] or v["unknown"] for v in coverage.values())
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
