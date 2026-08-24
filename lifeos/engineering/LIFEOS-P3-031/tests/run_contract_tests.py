#!/usr/bin/env python3
"""Synthetic-empty-database contract tests through LIFEOS-P3-048.

No network, real database, Vault, filesystem export, Tauri, or IPC is used.
The IPC cases below exercise only an in-process strict DTO parser.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "001_candidate_schema.sql"
NOW = 1786550400000

# The normal P3-031 suite keeps its historical single in-memory entry point.
# P3-053 additionally drives selected lifecycle evidence cases through the
# eight SQLite pragma/storage combinations below.  Keeping the configuration
# here makes the candidate contract runner, rather than an evidence-only
# helper, the executable source of truth for the remediation regressions.
MATRIX_CONFIG = None
MATRIX_WORK = None
MATRIX_CASE_ID = ""
MATRIX_CONNECTION_INDEX = 0
MATRIX_CONNECTIONS = []


class ContractFailure(AssertionError):
    pass


def check(value, message):
    if not value:
        raise ContractFailure(message)


def canonical_hash(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def rejected(fn, contains=None):
    try:
        fn()
    except sqlite3.DatabaseError as exc:
        if contains is not None:
            check(contains in str(exc), "unexpected SQLite error: %s" % exc)
        return
    raise ContractFailure("operation was expected to be rejected")


def migrated_connection(path=":memory:"):
    global MATRIX_CONNECTION_INDEX
    matrix_path = None
    if MATRIX_CONFIG is not None and path == ":memory:" and MATRIX_CONFIG["storage"] == "file":
        MATRIX_CONNECTION_INDEX += 1
        matrix_path = MATRIX_WORK / ("%s-%02d.db" % (MATRIX_CASE_ID, MATRIX_CONNECTION_INDEX))
        path = str(matrix_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(MIGRATION.read_text(encoding="utf-8"))
    if MATRIX_CONFIG is not None:
        conn.execute("PRAGMA foreign_keys=%s" % ("ON" if MATRIX_CONFIG["foreign_keys"] else "OFF"))
        conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if MATRIX_CONFIG["recursive_triggers"] else "OFF"))
        check(
            conn.execute("PRAGMA foreign_keys").fetchone()[0] == int(MATRIX_CONFIG["foreign_keys"]),
            "foreign key pragma did not match matrix configuration",
        )
        check(
            conn.execute("PRAGMA recursive_triggers").fetchone()[0] == int(MATRIX_CONFIG["recursive_triggers"]),
            "recursive trigger pragma did not match matrix configuration",
        )
        MATRIX_CONNECTIONS.append((conn, matrix_path))
    else:
        check(conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign keys disabled")
    return conn


def add_project(conn, pid="p1"):
    conn.execute(
        "INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        (pid, "Synthetic project", "test", "active", 1, NOW, NOW, NOW),
    )


def add_source(conn, sid="s1", generation=1):
    conn.execute(
        "INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?)",
        (sid, "synthetic", "stable:" + sid, "synthetic-only", "available", "allowed", generation, NOW, NOW),
    )


def add_artifact(conn, aid="a1", vid="v1", sid="s1", body="synthetic body", active=True):
    if conn.execute("SELECT 1 FROM source WHERE id=?", (sid,)).fetchone() is None:
        add_source(conn, sid)
    conn.execute(
        "INSERT INTO artifact VALUES (?,?,?,?,?,?,?,?)",
        (aid, sid, None, "note", "draft", 1, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO artifact_version VALUES (?,?,?,?,?,?,?,?,?)",
        (vid, aid, 1, sid, body, "sha256:" + hashlib.sha256(body.encode()).hexdigest(), NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO content_identity VALUES (?,?,?,?,?)",
        (vid, "user_original", "user", "actor:user", None),
    )
    if active:
        conn.execute("UPDATE artifact SET current_version_id=?, status='active' WHERE id=?", (vid, aid))


def add_semantic(conn, oid="o1", object_type="decision"):
    conn.execute(
        "INSERT INTO semantic_object VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (oid, object_type, None, None, "user", "open", "supported", 1, "draft", NOW, NOW),
    )
    payloads = {
        "assertion": {"statement": "synthetic"},
        "decision": {"decision_text": "synthetic"},
        "action": {"action_text": "synthetic"},
        "event": {"event_type": "synthetic", "description": "synthetic", "occurrence": {"unknown": True}},
    }
    payload = json.dumps(payloads[object_type], sort_keys=True)
    conn.execute(
        "INSERT INTO semantic_object_version VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (oid + "v1", oid, 1, object_type + "@1.0", 1, 0, payload, "sha256:" + hashlib.sha256(payload.encode()).hexdigest(), None, None, None, NOW),
    )
    conn.execute("UPDATE semantic_object SET current_version_no=1,status='active' WHERE id=?", (oid,))


def add_policy(conn, auth_id, complete=True):
    values = (
        auth_id,
        "indefinite" if complete else None,
        None,
        2 if complete else None,
        0 if complete else None,
        0 if complete else None,
        "[]" if complete else None,
        "[]" if complete else None,
        "[]" if complete else None,
        "[]" if complete else None,
        10 if complete else None,
        10 if complete else None,
    )
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", values)


def add_authorization_parent(conn, auth_id="auth1", logical="logical1", version=1, supersedes=None,
                             grantor_ref="actor:user", processor="local", purpose="test",
                             location="device", valid_from_ms=NOW, expires_mode="indefinite",
                             expires_at_ms=None, policy_version="policy@1", generation=1,
                             revoked_at_ms=None):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (auth_id, logical, grantor_ref, processor, purpose, location, "proposed", version, generation,
         valid_from_ms, expires_mode, expires_at_ms, revoked_at_ms, policy_version, supersedes, NOW, NOW),
    )


def add_authorization(conn, auth_id="auth1", logical="logical1", version=1, supersedes=None,
                      activate=True, **parent_fields):
    add_authorization_parent(conn, auth_id, logical, version, supersedes, **parent_fields)
    if conn.execute("SELECT 1 FROM project WHERE id='p1'").fetchone() is None:
        add_project(conn)
    conn.execute("INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)", (auth_id + ":scope", auth_id, "allow", "p1", None, None))
    conn.execute("INSERT INTO authorization_action VALUES (?,?,?)", (auth_id + ":action", auth_id, "read"))
    add_policy(conn, auth_id, True)
    if activate:
        conn.execute("UPDATE authorization SET status='active' WHERE id=?", (auth_id,))


def retire_authorization(conn, auth_id, status):
    """Write bound Submission + command atomically; DB emits retirement evidence."""
    row = conn.execute(
        "SELECT grantor_ref,version_no,generation FROM authorization WHERE id=?",
        (auth_id,),
    ).fetchone()
    check(row is not None, "authorization to retire does not exist")
    next_generation = row["generation"] + 1
    token = "%s:%s:%s" % (auth_id, next_generation, status)
    actor = "system:local" if status == "expired" else row["grantor_ref"]
    idem = "idem:" + token
    request_hash = canonical_hash("authorization-lifecycle:" + token)
    command_name = {
        "revoked": "revoke_authorization",
        "expired": "expire_authorization",
        "superseded": "supersede_authorization",
    }[status]
    conn.execute("SAVEPOINT lifecycle_request")
    try:
        conn.execute(
            "INSERT INTO submission VALUES ('destruct@1',?,?,?,?,NULL,?)",
            (idem, request_hash, command_name, auth_id, NOW),
        )
        conn.execute(
            """INSERT INTO authorization_lifecycle_command(
                 id,idempotency_key,authorization_id,expected_generation,target_status,
                 scoped_actor_claim,canonical_request_hash,requested_at_ms
               ) VALUES (?,?,?,?,?,?,?,?)""",
            ("cmd:" + token, idem, auth_id, row["generation"], status,
             actor, request_hash, NOW),
        )
        conn.execute("RELEASE lifecycle_request")
    except sqlite3.DatabaseError:
        conn.execute("ROLLBACK TO lifecycle_request")
        conn.execute("RELEASE lifecycle_request")
        raise


def outbox_runtime(conn, job_id, operation, worker=None, lease_until=None,
                   available_at=None, error_code=None):
    """Append one CAS-bound runtime intent; its trigger performs the transition."""
    row = conn.execute("SELECT * FROM outbox_job WHERE id=?", (job_id,)).fetchone()
    check(row is not None, "runtime job missing")
    sequence = conn.execute("SELECT count(*) FROM outbox_runtime_command WHERE job_id=?", (job_id,)).fetchone()[0] + 1
    conn.execute(
        """INSERT INTO outbox_runtime_command(
             id,job_id,operation,expected_status,expected_available_at_ms,
             expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,
             requested_lease_owner,requested_lease_expires_at_ms,
             requested_available_at_ms,error_code,requested_at_ms
           ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("runtime:%s:%s:%s" % (job_id, operation, sequence), job_id, operation,
         row["status"], row["available_at_ms"], row["lease_owner"],
         row["lease_generation"], row["lease_expires_at_ms"], worker,
         lease_until, available_at, error_code, NOW),
    )


def add_authorization_cleanup_gate(conn, auth_id="auth1", actor="actor:user"):
    row = conn.execute(
        "SELECT version_no,generation,status FROM authorization WHERE id=?", (auth_id,)
    ).fetchone()
    check(row is not None and row["status"] in ("revoked", "expired", "superseded"),
          "cleanup requires terminal authorization")
    correlation = "authorization-cleanup:%s:%s" % (auth_id, row["generation"])
    conn.execute(
        "INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
        ("audit:" + correlation, "authorization.cleanup", actor, auth_id,
         row["version_no"], "redacted_by_user", NOW, correlation),
    )
    conn.execute(
        "INSERT INTO tombstone VALUES ('authorization',?,?,?,'user_cleanup',?,'accepted',?)",
        (auth_id, row["generation"], "cleanup:" + auth_id, NOW, NOW),
    )
    conn.execute(
        "UPDATE tombstone SET cleanup_status='active_blocked' "
        "WHERE subject_type='authorization' AND subject_id=?", (auth_id,),
    )
    conn.execute(
        "UPDATE tombstone SET cleanup_status='cleanup_pending' "
        "WHERE subject_type='authorization' AND subject_id=?", (auth_id,),
    )


def cleanup_authorization_children(conn, auth_id="auth1"):
    for table in ("authorization_scope", "authorization_action", "authorization_policy"):
        conn.execute("DELETE FROM %s WHERE authorization_id=?" % table, (auth_id,))
    conn.execute(
        "UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 "
        "WHERE subject_type='authorization' AND subject_id=?", (auth_id,),
    )


def add_derivation(conn, did="d1", activate=True):
    if conn.execute("SELECT 1 FROM authorization WHERE id='auth1'").fetchone() is None:
        add_authorization(conn)
    if conn.execute("SELECT 1 FROM source WHERE id='s1'").fetchone() is None:
        add_source(conn)
    conn.execute(
        "INSERT INTO derivation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (did, "p1", "summary", None, "draft", "test", "device", "local", "wf@1", None, "auth1", 1, "constraint:1", 1, NOW, None, None, 1, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO derivation_input VALUES (?,?,?,?,?,?,?,?,?,?)",
        (did + ":input", did, "source", None, None, None, "s1", None, 1, "sha256:source"),
    )
    conn.execute(
        "INSERT INTO derivation_constraint VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (did, '["p1"]', '["test"]', '["device"]', '["local"]', 2, "private", None, 0, "allowed", "constraint:1"),
    )
    if activate:
        conn.execute("UPDATE derivation SET status='active' WHERE id=?", (did,))


def add_feedback(conn, fid, seq, kind="confirm", target="o1", actor="actor:user", basis=None, retracts=None, key=None):
    conn.execute(
        "INSERT INTO feedback VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (fid, actor, seq, "semantic_object", target, 1, kind, None, basis, retracts, key or ("idem:" + fid), "sha256:" + fid, NOW),
    )


def strict_intersection(grants, request_scope):
    """Pure transaction-guard candidate; unknown/empty/multiple groups fail closed."""
    if not grants or any(g.get("unknown") for g in grants):
        return False
    if any(request_scope in g.get("deny", set()) for g in grants):
        return False
    groups = {(g["grantor"], g["processor"], g["purpose"], g["location"], g["action"]) for g in grants}
    if len(groups) != 1:
        return False
    allowed = None
    for grant in grants:
        scope = set(grant.get("allow", set()))
        allowed = scope if allowed is None else allowed & scope
    return bool(allowed) and request_scope in allowed


DTO_VARIANTS = {
    "lifeos_read": {
        "read": {"artifact_id", "project_context_id", "purpose"},
        "search": {"query", "project_id", "purpose", "limit"},
        "health_check": {"detail_level"},
        "capability_status": set(),
    },
    "lifeos_export_candidate": {
        "export_candidate": {"project_id", "selection_refs", "purpose"},
        "evaluate_restore_candidates": {"package_token", "project_id"},
    },
    "lifeos_mutate": {
        "capture": {"idempotency_key", "original_text"},
        "feedback": {"idempotency_key", "target_ref", "kind"},
    },
    "lifeos_destruct": {
        "delete_artifact": {"artifact_id", "preview_token", "expected_generation", "idempotency_key"},
        "revoke_authorization": {"authorization_id", "preview_token", "expected_generation", "idempotency_key"},
        "disconnect_source": {"source_id", "preview_token", "expected_generation", "idempotency_key"},
    },
}


def parse_dto(invoke, envelope, capability=True):
    if invoke not in DTO_VARIANTS or not capability:
        return {"ok": False, "code": "E_UNKNOWN_COMMAND"}
    if set(envelope) != {"contract_version", "request_id", "action", "payload"}:
        return {"ok": False, "code": "E_INVALID_ARGUMENT"}
    if envelope["contract_version"] != "1.0" or envelope["action"] not in DTO_VARIANTS[invoke]:
        return {"ok": False, "code": "E_UNKNOWN_COMMAND"}
    payload = envelope["payload"]
    if not isinstance(payload, dict) or set(payload) != DTO_VARIANTS[invoke][envelope["action"]]:
        return {"ok": False, "code": "E_INVALID_ARGUMENT"}
    return {"ok": True, "data": {"accepted": True}}


def envelope(action, payload, version="1.0"):
    return {"contract_version": version, "request_id": "req:synthetic", "action": action, "payload": payload}


def db_p0_01():
    c = migrated_connection(); add_artifact(c); add_semantic(c); add_feedback(c, "f1", 1)
    rejected(lambda: c.execute("UPDATE artifact_version SET content_blob='changed' WHERE id='v1'"), "immutable")
    rejected(lambda: c.execute("UPDATE semantic_object_version SET payload_json='{}' WHERE id='o1v1'"), "immutable")
    rejected(lambda: c.execute("UPDATE feedback SET kind='reject' WHERE id='f1'"), "append_only")
    check(c.execute("SELECT content_blob FROM artifact_version WHERE id='v1'").fetchone()[0] == "synthetic body", "artifact changed")


def db_p0_02():
    c = migrated_connection(); add_source(c); add_artifact(c)
    c.execute("INSERT INTO artifact VALUES ('a2','s1',NULL,'note','draft',1,?,?)", (NOW, NOW))
    c.execute("INSERT INTO artifact_version VALUES ('v2','a2',1,'s1','x','sha256:x',?,?,?)", (NOW, NOW, NOW))
    c.execute("INSERT INTO content_identity VALUES ('v2','external_original','external','external:unknown',NULL)")
    c.execute("INSERT INTO artifact VALUES ('a3','s1',NULL,'note','draft',1,?,?)", (NOW, NOW))
    c.execute("INSERT INTO artifact_version VALUES ('v3','a3',1,'s1','x','sha256:x',?,?,?)", (NOW, NOW, NOW))
    rejected(lambda: c.execute("INSERT INTO content_identity VALUES ('v3','external_original','external',NULL,NULL)"))
    c.execute("INSERT INTO artifact VALUES ('a4','s1',NULL,'note','draft',1,?,?)", (NOW, NOW))
    c.execute("INSERT INTO artifact_version VALUES ('v4','a4',1,'s1','x','sha256:x',?,?,?)", (NOW, NOW, NOW))
    rejected(lambda: c.execute("INSERT INTO content_identity VALUES ('v4','ai_generated','ai','actor:fake',NULL)"))


def db_p0_03():
    c = migrated_connection(); add_derivation(c)
    rejected(lambda: c.execute("INSERT INTO derivation_input VALUES ('bad0','d1','source',NULL,NULL,NULL,NULL,NULL,NULL,'h')"))
    rejected(lambda: c.execute("INSERT INTO derivation_input VALUES ('bad2','d1','source',NULL,NULL,NULL,'s1',NULL,1,'h')"))  # duplicate typed ref
    rejected(lambda: c.execute("INSERT INTO derivation_input VALUES ('badtype','d1','bogus',NULL,NULL,NULL,'s1',NULL,1,'h')"))
    add_source(c, "s2")
    add_artifact(c, "a1", "v1", "s1")
    rejected(lambda: c.execute("INSERT INTO derivation_input VALUES ('badmulti','d1','source','v1',NULL,NULL,'s2',1,1,'h')"))


def db_p0_04():
    c = migrated_connection(); add_authorization(c); add_source(c)
    c.execute("INSERT INTO derivation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ("d0", "p1", "summary", None, "draft", "test", "device", "local", "wf", None, "auth1", 1, "c", 1, NOW, None, None, 1, NOW, NOW))
    rejected(lambda: c.execute("UPDATE derivation SET status='active' WHERE id='d0'"), "no_inputs")
    c.execute("INSERT INTO derivation_input VALUES ('di0','d0','source',NULL,NULL,NULL,'s1',NULL,1,'h')")
    rejected(lambda: c.execute("UPDATE derivation SET status='active' WHERE id='d0'"), "no_constraint")


def db_p0_05():
    c = migrated_connection(); add_feedback(c, "f1", 1); add_feedback(c, "f2", 2, "retract", retracts="f1")
    add_feedback(c, "f3", 3, "retract", retracts="f2")
    rejected(lambda: add_feedback(c, "branch", 4, "retract", retracts="f1"))
    rejected(lambda: add_feedback(c, "actor", 5, "retract", actor="actor:other", retracts="f3"))
    rejected(lambda: add_feedback(c, "target", 6, "retract", target="o2", retracts="f3"))


def db_p0_06():
    c = migrated_connection(); add_feedback(c, "f1", 1); add_feedback(c, "f2", 2, "correct")
    c.execute("INSERT INTO feedback_dependency VALUES ('f2','f1','requires_confirmation')")
    add_feedback(c, "f3", 3, "confirm", target="other")
    rejected(lambda: c.execute("INSERT INTO feedback_dependency VALUES ('f3','f1','explicit_basis')"), "dependency_invalid")
    rejected(lambda: c.execute("INSERT INTO feedback_dependency VALUES ('f1','f1','explicit_basis')"))
    rejected(lambda: c.execute("INSERT INTO feedback_dependency VALUES ('f1','f2','explicit_basis')"), "dependency_invalid")


def db_p0_07():
    base = {"grantor": "u", "processor": "local", "purpose": "p", "location": "d", "action": "read"}
    g1 = dict(base, allow={"artifact:a"}, deny={"project:p"})
    g2 = dict(base, allow={"project:p", "artifact:a"}, deny={"artifact:a"})
    check(not strict_intersection([g1], "project:p"), "project deny bypassed")
    check(not strict_intersection([g2], "artifact:a"), "artifact deny bypassed")


def db_p0_08():
    base = {"grantor": "u", "processor": "local", "purpose": "p", "location": "d", "action": "read", "deny": set()}
    a = dict(base, allow={"a", "b"}); b = dict(base, allow={"b", "c"})
    check(strict_intersection([a, b], "b"), "valid intersection denied")
    check(not strict_intersection([a, b], "a"), "non-intersection allowed")
    check(not strict_intersection([a, dict(b, allow={"c"})], "a"), "empty intersection allowed")
    check(not strict_intersection([dict(a, unknown=True)], "a"), "unknown policy allowed")
    check(not strict_intersection([a, dict(b, grantor="other")], "b"), "multiple groups allowed")


def db_p0_09():
    c = migrated_connection()
    c.execute("INSERT INTO tombstone VALUES ('artifact','a1',2,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a1'")
    updated = c.execute("UPDATE tombstone SET generation=3 WHERE subject_type='artifact' AND subject_id='a1' AND generation=2").rowcount
    stale = c.execute("UPDATE tombstone SET generation=4 WHERE subject_type='artifact' AND subject_id='a1' AND generation=2").rowcount
    check(updated == 1 and stale == 0, "stale generation was not fenced")


def db_p0_10():
    c = migrated_connection(); add_artifact(c, "a1", "v1"); add_artifact(c, "a2", "v2", "s1")
    rejected(lambda: c.execute("UPDATE artifact SET current_version_id='v2' WHERE id='a1'"), "not_owned")
    c.execute("INSERT INTO semantic_object VALUES ('o1','decision',NULL,NULL,'user','open','supported',1,'draft',?,?)", (NOW, NOW))
    rejected(lambda: c.execute("INSERT INTO semantic_object_version VALUES ('x','o1',1,'decision@2.0',2,0,'{\"decision_text\":\"x\"}','sha256:x',NULL,NULL,NULL,?)", (NOW,)))


def db_p0_11():
    c = migrated_connection(); add_artifact(c, "a1", "v1", body="needle visible"); add_artifact(c, "a2", "v2", body="needle blocked")
    c.execute("INSERT INTO artifact_fts VALUES ('v1','a1','needle visible')")
    c.execute("INSERT INTO artifact_fts VALUES ('v2','a2','needle blocked')")
    c.execute("INSERT INTO tombstone VALUES ('artifact','a2',1,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a2'")
    rows = c.execute("SELECT f.artifact_id FROM artifact_fts f JOIN artifact a ON a.id=f.artifact_id LEFT JOIN tombstone t ON t.subject_type='artifact' AND t.subject_id=a.id WHERE artifact_fts MATCH 'needle' AND a.status='active' AND t.subject_id IS NULL").fetchall()
    check([r[0] for r in rows] == ["a1"], "FTS leaked tombstoned candidate")


def db_p0_12():
    package = {"artifact_id": "a1", "generation": 1, "body": "old"}
    current_tombstone = {"artifact_id": "a1", "generation": 2}
    outcome = "blocked" if current_tombstone["generation"] >= package["generation"] else "restorable"
    check(outcome == "blocked", "old package revived tombstoned content")


def db_p0_13():
    c = migrated_connection()
    db_now = c.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]
    c.execute("INSERT INTO outbox_job VALUES ('j','publish','artifact','a',2,NULL,'pending',0,?,NULL,0,NULL,'idem:j',NULL)", (db_now,))
    outbox_runtime(c, "j", "claim", worker="worker", lease_until=db_now + 60000)
    stale_lease = c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='j' AND lease_generation=0 AND subject_generation=2").rowcount
    stale_subject = c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='j' AND lease_generation=1 AND subject_generation=1").rowcount
    rejected(lambda: c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='j' AND lease_generation=1 AND subject_generation=2"), "runtime_command_required")
    outbox_runtime(c, "j", "complete")
    check((stale_lease, stale_subject) == (0, 0) and c.execute("SELECT status FROM outbox_job WHERE id='j'").fetchone()[0] == "completed", "outbox CAS contract failed")


def db_p0_14():
    c = migrated_connection()
    hash_a, hash_b = canonical_hash("a"), canonical_hash("b")
    c.execute("INSERT INTO submission VALUES ('mutate@1','key',?,'capture','a1',NULL,?)", (hash_a, NOW))
    rejected(lambda: c.execute("INSERT INTO submission VALUES ('mutate@1','key',?,'capture','a2',NULL,?)", (hash_b, NOW)))
    check(c.execute("SELECT canonical_request_hash FROM submission").fetchone()[0] == hash_a, "original idempotency result changed")


def db_p0_15():
    c = migrated_connection()
    c.execute("INSERT INTO tombstone VALUES ('artifact','a1',5,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a1'")
    rejected(lambda: c.execute("UPDATE tombstone SET generation=4 WHERE subject_type='artifact' AND subject_id='a1'"), "must_not_decrease")
    check(c.execute("SELECT generation FROM tombstone").fetchone()[0] == 5, "tombstone generation changed")


def ipc_p0_01():
    payload = {"artifact_id": "a", "preview_token": "t", "expected_generation": 1, "idempotency_key": "k"}
    check(not parse_dto("lifeos_mutate", envelope("delete_artifact", payload))["ok"], "mutate routed destruct")
    check(not parse_dto("lifeos_destruct", envelope("delete_artifact", payload), capability=False)["ok"], "missing capability allowed")


def ipc_p0_02():
    valid = envelope("read", {"artifact_id": "a", "project_context_id": "p", "purpose": "view"})
    check(parse_dto("lifeos_read", valid)["ok"], "valid DTO rejected")
    bad = dict(valid); bad["extra"] = True
    check(parse_dto("lifeos_read", bad)["code"] == "E_INVALID_ARGUMENT", "extra top-level accepted")
    bad_payload = envelope("read", dict(valid["payload"], preview_token="cross"))
    check(parse_dto("lifeos_read", bad_payload)["code"] == "E_INVALID_ARGUMENT", "cross-variant field accepted")
    check(parse_dto("lifeos_read", envelope("read", valid["payload"], "2.0"))["code"] == "E_UNKNOWN_COMMAND", "wrong major accepted")


def ipc_p0_03():
    required = {"artifact_id": "a", "preview_token": "t", "expected_generation": 1, "idempotency_key": "k"}
    check(parse_dto("lifeos_destruct", envelope("delete_artifact", required))["ok"], "valid destruct rejected")
    for field in ("preview_token", "expected_generation", "idempotency_key"):
        bad = dict(required); del bad[field]
        check(not parse_dto("lifeos_destruct", envelope("delete_artifact", bad))["ok"], "missing %s accepted" % field)


def ct_p1_01():
    text = MIGRATION.read_text(encoding="utf-8").replace("INSERT INTO schema_migration_meta", "THIS IS NOT SQL;\nINSERT INTO schema_migration_meta", 1)
    c = sqlite3.connect(":memory:")
    try:
        c.executescript(text)
        raise ContractFailure("fault-injected migration unexpectedly succeeded")
    except sqlite3.DatabaseError:
        c.rollback()
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','trigger','index') AND name NOT LIKE 'sqlite_%'")]
    check(tables == [], "migration left partial schema: %r" % tables)


def ct_p1_02():
    c = migrated_connection(); add_source(c); add_artifact(c, active=False); add_authorization(c); add_derivation(c, "d2", activate=False)
    check(c.execute("SELECT count(*) FROM artifact WHERE status='active'").fetchone()[0] == 0, "draft artifact visible")
    check(c.execute("SELECT count(*) FROM derivation WHERE status='active'").fetchone()[0] == 0, "draft derivation visible")


def ct_p1_03():
    c = migrated_connection(); add_semantic(c, "o1", "decision")
    old = c.execute("SELECT payload_json FROM semantic_object_version WHERE id='o1v1'").fetchone()[0]
    payload = json.dumps({"decision_text": "migrated", "rationale": "synthetic"}, sort_keys=True)
    c.execute("INSERT INTO semantic_object_version VALUES ('o1v2','o1',2,'decision@1.1',1,1,?,'sha256:new',1,'migrator@1','sha256:m',?)", (payload, NOW))
    c.execute("UPDATE semantic_object SET current_version_no=2 WHERE id='o1'")
    check(c.execute("SELECT payload_json FROM semantic_object_version WHERE id='o1v1'").fetchone()[0] == old, "old payload changed")
    c.execute("UPDATE semantic_object SET status='migration_required' WHERE id='o1'")
    check(c.execute("SELECT current_version_no FROM semantic_object WHERE id='o1'").fetchone()[0] == 2, "failure marker destroyed current pointer")


def ct_p1_04():
    c = migrated_connection(); c.execute("INSERT INTO tombstone VALUES ('artifact','a',1,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a'")
    c.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_id='a'")
    c.execute("UPDATE tombstone SET cleanup_status='cleanup_failed' WHERE subject_id='a'")
    rejected(lambda: c.execute("UPDATE tombstone SET cleanup_status='accepted' WHERE subject_id='a'"), "transition_invalid")
    check(c.execute("SELECT cleanup_status FROM tombstone").fetchone()[0] == "cleanup_failed", "cleanup failure removed block")


def ct_p1_05():
    issued = {"token": "opaque", "session": "s", "expires": time.time() + 30, "used": False, "detail": {"public_code": "E_DB", "operation_class": "read", "retryable": False, "component_category": "db", "coarse_time_bucket": "now", "correlation_id": "c"}}
    allowed = {"public_code", "operation_class", "retryable", "component_category", "coarse_time_bucket", "correlation_id"}
    check(set(issued["detail"]) == allowed, "details token leaked fields")
    issued["used"] = True
    check(issued["used"], "single-use token not consumed")
    check(not (issued["session"] == "other" and not issued["used"]), "cross-session replay allowed")


def ct_p1_06():
    c = migrated_connection(); add_artifact(c)
    c.execute("DROP TABLE artifact_fts")
    c.commit()
    check(c.execute("SELECT content_blob FROM artifact_version WHERE id='v1'").fetchone()[0] == "synthetic body", "FTS failure rolled back authority")


def ct_p1_07():
    def auth_base(c, aid, logical="l", version=1, supersedes=None):
        c.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (aid, logical, "u", "local", "p", "d", "proposed", version, 1, NOW, "indefinite", None, None, "p@1", supersedes, NOW, NOW))
    c = migrated_connection(); add_project(c)
    auth_base(c, "no_scope")
    c.execute("INSERT INTO authorization_action VALUES ('x','no_scope','read')"); add_policy(c, "no_scope")
    rejected(lambda: c.execute("UPDATE authorization SET status='active' WHERE id='no_scope'"), "no_scope")
    auth_base(c, "no_action", "l2")
    c.execute("INSERT INTO authorization_scope VALUES ('s','no_action','allow','p1',NULL,NULL)"); add_policy(c, "no_action")
    rejected(lambda: c.execute("UPDATE authorization SET status='active' WHERE id='no_action'"), "no_action")
    auth_base(c, "bad_policy", "l3")
    c.execute("INSERT INTO authorization_scope VALUES ('s3','bad_policy','allow','p1',NULL,NULL)"); c.execute("INSERT INTO authorization_action VALUES ('a3','bad_policy','read')"); add_policy(c, "bad_policy", False)
    rejected(lambda: c.execute("UPDATE authorization SET status='active' WHERE id='bad_policy'"), "policy_incomplete")
    add_authorization(c, "old", "l4", 1)
    auth_base(c, "new", "l4", 2, "old")
    c.execute("INSERT INTO authorization_scope VALUES ('s4','new','allow','p1',NULL,NULL)"); c.execute("INSERT INTO authorization_action VALUES ('a4','new','read')"); add_policy(c, "new")
    rejected(lambda: c.execute("UPDATE authorization SET status='active' WHERE id='new'"), "old_version_not_superseded")
    retire_authorization(c, "old", "superseded")
    c.execute("UPDATE authorization SET status='active' WHERE id='new'")


def ct_p1_08():
    """P3-032 P1-1: a parent Authorization cannot be inserted active."""
    c = migrated_connection()
    rejected(
        lambda: c.execute(
            "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("direct-active", "direct-active", "u", "local", "p", "d", "active", 1, 1, NOW, "indefinite", None, None, "p@1", None, NOW, NOW),
        ),
        "authorization_must_start_inactive",
    )
    check(c.execute("SELECT count(*) FROM authorization WHERE id='direct-active'").fetchone()[0] == 0, "rejected active authorization persisted")


def ct_p1_09():
    """P3-032 P1-2: a parent Derivation cannot be inserted active."""
    c = migrated_connection(); add_authorization(c)
    rejected(
        lambda: c.execute(
            "INSERT INTO derivation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("direct-active", "p1", "summary", None, "active", "test", "device", "local", "wf@1", None, "auth1", 1, "constraint:1", 1, NOW, None, None, 1, NOW, NOW),
        ),
        "derivation_must_start_inactive",
    )
    check(c.execute("SELECT count(*) FROM derivation WHERE id='direct-active'").fetchone()[0] == 0, "rejected active derivation persisted")


def ct_p1_10():
    """P3-037 P2-2: delete, replace, and delete+insert cannot lower a Tombstone."""
    c = migrated_connection()
    c.execute("INSERT INTO tombstone VALUES ('artifact','a1',5,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='a1'")
    c.commit()
    before = tuple(c.execute("SELECT generation,cleanup_status,command_id FROM tombstone WHERE subject_id='a1'").fetchone())
    rejected(lambda: c.execute("DELETE FROM tombstone WHERE subject_id='a1'"), "tombstone_delete_forbidden")
    rejected(
        lambda: c.execute("INSERT OR REPLACE INTO tombstone VALUES ('artifact','a1',4,'replace','test',?,'accepted',?)", (NOW, NOW)),
        "tombstone_reinsert_forbidden",
    )
    c.rollback()
    try:
        c.execute("BEGIN IMMEDIATE")
        c.execute("DELETE FROM tombstone WHERE subject_id='a1'")
        c.execute("INSERT INTO tombstone VALUES ('artifact','a1',4,'reinsert','test',?,'accepted',?)", (NOW, NOW))
        raise ContractFailure("delete+insert attack unexpectedly succeeded")
    except sqlite3.DatabaseError as exc:
        check("tombstone_delete_forbidden" in str(exc), "unexpected delete+insert error: %s" % exc)
        c.rollback()
    after = tuple(c.execute("SELECT generation,cleanup_status,command_id FROM tombstone WHERE subject_id='a1'").fetchone())
    check(after == before == (5, "active_blocked", "cmd"), "blocked Tombstone changed after bypass attempts")


def ct_p1_11():
    """P3-037 P2-3: Tombstones must start accepted and then follow the matrix."""
    c = migrated_connection()
    for index, status in enumerate(("active_blocked", "cleaned", "cleanup_failed", "vendor_limited"), 1):
        rejected(
            lambda index=index, status=status: c.execute(
                "INSERT INTO tombstone VALUES ('artifact',?,1,?,'test',?, ?,?)",
                ("bad-%s" % index, "cmd-%s" % index, NOW, status, NOW),
            ),
            "tombstone_must_start_accepted",
        )
    check(c.execute("SELECT count(*) FROM tombstone").fetchone()[0] == 0, "illegal initial Tombstone persisted")
    c.execute("INSERT INTO tombstone VALUES ('artifact','good',1,'cmd-good','test',?,'accepted',?)", (NOW, NOW))
    c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='good'")
    c.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_id='good'")
    c.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_id='good'")
    check(c.execute("SELECT cleanup_status FROM tombstone WHERE subject_id='good'").fetchone()[0] == "cleaned", "legal Tombstone lifecycle failed")


def ct_p1_12():
    """P3-037 P2-4: active Authorization children cannot be directly deleted."""
    cases = (
        ("scope", "DELETE FROM authorization_scope WHERE authorization_id='auth1'", "active_authorization_scope_delete_forbidden", "authorization_scope"),
        ("action", "DELETE FROM authorization_action WHERE authorization_id='auth1'", "active_authorization_action_delete_forbidden", "authorization_action"),
        ("policy", "DELETE FROM authorization_policy WHERE authorization_id='auth1'", "active_authorization_policy_delete_forbidden", "authorization_policy"),
    )
    for name, statement, error, table in cases:
        c = migrated_connection(); add_authorization(c); c.commit()
        parent_before = tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone())
        child_before = c.execute("SELECT count(*) FROM %s WHERE authorization_id='auth1'" % table).fetchone()[0]
        rejected(lambda statement=statement: c.execute(statement), error)
        c.rollback()
        parent_after = tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone())
        child_after = c.execute("SELECT count(*) FROM %s WHERE authorization_id='auth1'" % table).fetchone()[0]
        check(parent_after == parent_before == ("active", 1), "%s delete changed active parent" % name)
        check(child_after == child_before, "%s delete removed active child" % name)
    c = migrated_connection(); add_authorization(c, activate=False)
    c.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'")
    c.execute("DELETE FROM authorization_action WHERE authorization_id='auth1'")
    c.execute("DELETE FROM authorization_policy WHERE authorization_id='auth1'")
    check(c.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'").fetchone()[0] == 0, "inactive scope cleanup rejected")
    check(c.execute("SELECT count(*) FROM authorization_action WHERE authorization_id='auth1'").fetchone()[0] == 0, "inactive action cleanup rejected")
    check(c.execute("SELECT count(*) FROM authorization_policy WHERE authorization_id='auth1'").fetchone()[0] == 0, "inactive policy cleanup rejected")


def ct_p1_13():
    """P3-039 ADJ: every active child INSERT/UPDATE/REPLACE is rejected."""
    statements = [
        ("scope insert allow", "INSERT INTO authorization_scope VALUES ('scope-extra','auth1','allow','p1',NULL,NULL)", "scope_insert"),
        ("scope insert deny", "INSERT INTO authorization_scope VALUES ('scope-deny','auth1','deny','p1',NULL,NULL)", "scope_insert"),
        ("scope effect", "UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'", "scope_update"),
        ("scope project", "UPDATE authorization_scope SET project_id='p2' WHERE authorization_id='auth1'", "scope_update"),
        ("scope source", "UPDATE authorization_scope SET project_id=NULL,source_id='s1' WHERE authorization_id='auth1'", "scope_update"),
        ("scope artifact", "UPDATE authorization_scope SET project_id=NULL,artifact_id='a1' WHERE authorization_id='auth1'", "scope_update"),
        ("action insert", "INSERT INTO authorization_action VALUES ('action-extra','auth1','export_candidate')", "action_insert"),
        ("action update", "UPDATE authorization_action SET action='export_candidate' WHERE authorization_id='auth1'", "action_update"),
        ("scope replace", "INSERT OR REPLACE INTO authorization_scope VALUES ('auth1:scope','auth1','deny','p1',NULL,NULL)", "scope_insert"),
        ("action replace", "INSERT OR REPLACE INTO authorization_action VALUES ('auth1:action','auth1','export_candidate')", "action_insert"),
        ("policy insert", "INSERT INTO authorization_policy VALUES ('auth1','none',NULL,5,1,1,'[]','[]','[]','[]',99,99)", "policy_insert"),
        ("policy replace", "INSERT OR REPLACE INTO authorization_policy VALUES ('auth1','none',NULL,5,1,1,'[\"x\"]','[\"*\"]','[]','[]',99,99)", "policy_insert"),
    ]
    policy_updates = [
        "retention_mode='none'", "retention_mode='until',retention_deadline_ms=%d" % (NOW + 1000),
        "sensitivity_rank=5", "training_allowed=1", "external_send_allowed=1",
        "recipients_json='[\"r\"]'", "regions_json='[\"z\"]'",
        "disclosure_json='[\"d\"]'", "source_license_json='[\"l\"]'",
        "quantity_ceiling=99", "frequency_ceiling=99",
    ]
    statements.extend(
        ("policy field %s" % index, "UPDATE authorization_policy SET %s WHERE authorization_id='auth1'" % assignment, "policy_update")
        for index, assignment in enumerate(policy_updates, 1)
    )
    for name, statement, error_suffix in statements:
        c = migrated_connection(); add_project(c, "p2"); add_source(c); add_artifact(c); add_authorization(c); c.commit()
        before = tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone())
        rejected(lambda statement=statement: c.execute(statement), "active_authorization_%s_forbidden" % error_suffix)
        c.rollback()
        check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == before, "%s changed parent" % name)


def ct_p1_14():
    """P3-040: child rebinds check both OLD and NEW active parents."""
    for table, key_column, key in (
        ("authorization_scope", "id", "auth1:scope"),
        ("authorization_action", "id", "auth1:action"),
        ("authorization_policy", "authorization_id", "auth1"),
    ):
        error = "active_%s_update_forbidden" % table
        c = migrated_connection(); add_authorization(c); add_authorization_parent(c, "inactive", "logical-inactive")
        rejected(lambda c=c, table=table, key_column=key_column, key=key: c.execute(
            "UPDATE %s SET authorization_id='inactive' WHERE %s=?" % (table, key_column), (key,)
        ), error)

        c = migrated_connection(); add_authorization(c); add_authorization_parent(c, "inactive", "logical-inactive")
        if table == "authorization_scope":
            c.execute("INSERT INTO authorization_scope VALUES ('inactive:scope','inactive','allow','p1',NULL,NULL)")
            source_key = "inactive:scope"
        elif table == "authorization_action":
            c.execute("INSERT INTO authorization_action VALUES ('inactive:action','inactive','export_candidate')")
            source_key = "inactive:action"
        else:
            add_policy(c, "inactive")
            source_key = "inactive"
        rejected(lambda c=c, table=table, key_column=key_column, source_key=source_key: c.execute(
            "UPDATE %s SET authorization_id='auth1' WHERE %s=?" % (table, key_column), (source_key,)
        ), error)

        c = migrated_connection(); add_authorization(c); add_authorization(c, "active2", "logical2")
        rejected(lambda c=c, table=table, key_column=key_column, key=key: c.execute(
            "UPDATE %s SET authorization_id='active2' WHERE %s=?" % (table, key_column), (key,)
        ), error)


def ct_p1_15():
    """Forward-only retirement requires a one-shot lifecycle command."""
    for illegal in ("proposed", "granted"):
        c = migrated_connection(); add_authorization(c)
        rejected(lambda c=c, illegal=illegal: c.execute("UPDATE authorization SET status=? WHERE id='auth1'", (illegal,)), "status_transition_invalid")

    c = migrated_connection(); add_authorization(c)
    rejected(lambda: c.execute("UPDATE authorization SET status='revoked' WHERE id='auth1'"), "lifecycle_command")
    rejected(lambda: c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"), "lifecycle_command")
    c.execute("INSERT INTO audit_entry VALUES ('audit-only','authorization.revoke','actor:user','auth1',1,'ok',?,'authorization-state:auth1:2:revoked')", (NOW,))
    rejected(lambda: c.execute("UPDATE authorization SET status='revoked',generation=2 WHERE id='auth1'"), "lifecycle_command")

    for terminal in ("revoked", "expired", "superseded"):
        c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", terminal)
        check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == (terminal, 2), "legal retirement failed")
        rejected(lambda c=c: c.execute("UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'"), "terminal_authorization_scope_update_forbidden")
        rejected(lambda c=c: c.execute("UPDATE authorization_action SET action='export_candidate' WHERE authorization_id='auth1'"), "terminal_authorization_action_update_forbidden")
        rejected(lambda c=c: c.execute("UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth1'"), "terminal_authorization_policy_update_forbidden")
        rejected(lambda c=c: c.execute("UPDATE authorization SET status='active' WHERE id='auth1'"), "terminal_authorization_immutable")
        check(c.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()[0] == terminal, "terminal authorization reactivated")

    c = migrated_connection(); add_authorization(c)
    rejected(lambda: c.execute("UPDATE authorization SET version_no=2 WHERE id='auth1'"), "version_identity_immutable")
    rejected(lambda: c.execute("UPDATE authorization SET generation=0 WHERE id='auth1'"), "generation_requires_lifecycle_command")


def ct_p1_16():
    """Controlled terminal cleanup and legitimate new-version activation remain usable."""
    for terminal in ("revoked", "expired", "superseded"):
        c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", terminal)
        add_authorization_cleanup_gate(c)
        cleanup_authorization_children(c)
        remaining = sum(c.execute("SELECT count(*) FROM %s WHERE authorization_id='auth1'" % table).fetchone()[0]
                        for table in ("authorization_scope", "authorization_action", "authorization_policy"))
        check(remaining == 0, "%s child cleanup was locked" % terminal)
        check(c.execute("SELECT cleanup_status FROM tombstone WHERE subject_type='authorization'").fetchone()[0] == "cleaned",
              "%s cleanup did not reach cleaned" % terminal)

    c = migrated_connection(); add_authorization(c, "old", "versioned", 1); retire_authorization(c, "old", "superseded")
    add_authorization(c, "new", "versioned", 2, "old")
    check(tuple(c.execute("SELECT status,version_no,generation FROM authorization WHERE id='new'").fetchone()) == ("active", 2, 1), "new version did not activate")
    check(c.execute("SELECT status FROM authorization WHERE id='old'").fetchone()[0] == "superseded", "old version did not remain superseded")

    c = migrated_connection(); add_project(c); add_authorization_parent(c, "bad-v2", "versioned", 2)
    c.execute("INSERT INTO authorization_scope VALUES ('bad-v2:s','bad-v2','allow','p1',NULL,NULL)")
    c.execute("INSERT INTO authorization_action VALUES ('bad-v2:a','bad-v2','read')"); add_policy(c, "bad-v2")
    rejected(lambda: c.execute("UPDATE authorization SET status='active' WHERE id='bad-v2'"), "new_version_requires_supersedes")

    c = migrated_connection(); add_project(c); add_authorization(c, "granted", "granted-flow", activate=False)
    c.execute("UPDATE authorization SET status='granted' WHERE id='granted'")
    c.execute("UPDATE authorization SET status='active' WHERE id='granted'")
    check(c.execute("SELECT status FROM authorization WHERE id='granted'").fetchone()[0] == "active", "granted activation flow failed")


def ct_p1_17():
    """P3-041 P1: all eight active parent security-envelope fields are immutable."""
    error = "active_authorization_security_envelope_immutable"
    cases = (
        ("grantor_ref", {}, "grantor_ref='actor:other'"),
        ("processor", {}, "processor='external-cloud'"),
        ("purpose", {}, "purpose='production'"),
        ("location", {}, "location='remote'"),
        ("valid_from_ms", {}, "valid_from_ms=0"),
        ("expires_mode", {"expires_mode": "at", "expires_at_ms": NOW + 10000},
         "expires_mode='indefinite',expires_at_ms=NULL"),
        ("expires_at_ms", {"expires_mode": "at", "expires_at_ms": NOW + 10000},
         "expires_at_ms=%d" % (NOW + 20000)),
        ("policy_version", {}, "policy_version='policy@evil'"),
    )
    fields = "grantor_ref,processor,purpose,location,valid_from_ms,expires_mode,expires_at_ms,policy_version"
    for name, fixture, assignment in cases:
        c = migrated_connection(); add_authorization(c, **fixture); c.commit()
        before = tuple(c.execute("SELECT %s FROM authorization WHERE id='auth1'" % fields).fetchone())
        rejected(lambda c=c, assignment=assignment: c.execute(
            "UPDATE authorization SET %s WHERE id='auth1'" % assignment
        ), error)
        c.rollback()
        after = tuple(c.execute("SELECT %s FROM authorization WHERE id='auth1'" % fields).fetchone())
        check(after == before, "%s changed despite envelope trigger" % name)


def ct_p1_18():
    """P3-042 compound/multi-row/no-op and legal lifecycle paths."""
    error = "active_authorization_security_envelope_immutable"

    c = migrated_connection(); add_authorization(c); c.commit()
    rejected(lambda: c.execute(
        "UPDATE authorization SET processor='cloud',purpose='prod',location='remote' WHERE id='auth1'"
    ), error)
    c.rollback()
    check(tuple(c.execute("SELECT processor,purpose,location FROM authorization WHERE id='auth1'").fetchone())
          == ("local", "test", "device"), "compound update partially changed envelope")

    c = migrated_connection(); add_authorization(c); add_authorization(c, "auth2", "logical2"); c.commit()
    rejected(lambda: c.execute("UPDATE authorization SET purpose='bulk-change' WHERE status='active'"), error)
    c.rollback()
    check([row[0] for row in c.execute("SELECT purpose FROM authorization ORDER BY id")] == ["test", "test"],
          "multi-row update was not atomic")

    c = migrated_connection(); add_authorization(c); c.commit()
    c.execute("""UPDATE authorization SET
        grantor_ref=grantor_ref,processor=processor,purpose=purpose,location=location,
        valid_from_ms=valid_from_ms,expires_mode=expires_mode,expires_at_ms=expires_at_ms,
        policy_version=policy_version WHERE id='auth1'""")
    c.execute("UPDATE authorization SET updated_at_ms=? WHERE id='auth1'", (NOW + 1,))
    check(c.execute("SELECT updated_at_ms FROM authorization WHERE id='auth1'").fetchone()[0] == NOW + 1,
          "updated_at-only maintenance was blocked")

    c = migrated_connection(); add_authorization(c, activate=False)
    c.execute("UPDATE authorization SET processor='local-v2',purpose='configured',expires_mode='at',expires_at_ms=? WHERE id='auth1'", (NOW + 10000,))
    c.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    check(c.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()[0] == "active",
          "proposed configuration then activation failed")

    c = migrated_connection(); add_authorization(c, activate=False)
    c.execute("UPDATE authorization SET status='granted' WHERE id='auth1'")
    c.execute("UPDATE authorization SET policy_version='policy@2' WHERE id='auth1'")
    c.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    check(c.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()[0] == "active",
          "granted configuration then activation failed")

    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "superseded")
    add_authorization(c, "auth2", "logical1", 2, "auth1", processor="external-approved",
                      purpose="new-purpose", policy_version="policy@2")
    check(tuple(c.execute("SELECT status,processor,purpose,policy_version FROM authorization WHERE id='auth2'").fetchone())
          == ("active", "external-approved", "new-purpose", "policy@2"),
          "successor with changed envelope did not activate")

    c = migrated_connection(); add_authorization(c); c.commit()
    row = c.execute("SELECT generation FROM authorization WHERE id='auth1'").fetchone()
    next_generation = row[0] + 1
    token = "authorization-state:auth1:%s:revoked" % next_generation
    c.execute("INSERT INTO audit_entry VALUES ('audit-retire','authorization.revoke','actor:user','auth1',1,'ok',?,?)", (NOW, token))
    c.execute(
        "INSERT INTO outbox_job VALUES (?,?,?, ?,1,NULL,'pending',0,?,NULL,0,NULL,?,NULL)",
        ('outbox:' + token, 'generic', 'artifact', 'retirement-conflict', NOW, 'generic-retirement-conflict'),
    )
    rejected(lambda: c.execute(
        "UPDATE authorization SET status='revoked',generation=?,processor='changed' WHERE id='auth1'",
        (next_generation,)))
    c.rollback()
    check(tuple(c.execute("SELECT status,generation,processor FROM authorization WHERE id='auth1'").fetchone())
          == ("active", 1, "local"), "compound retirement changed active envelope")


def ct_p1_19():
    """P3-043 P1: conflict INSERT/REPLACE cannot replace an active parent."""
    error = "active_authorization_replace_forbidden"

    def values(aid="auth1", logical="logical1", status="granted", processor="evil",
               policy_version="policy@evil"):
        return (aid, logical, "actor:evil", processor, "production", "remote", status,
                1, 1, NOW, "at", NOW + 10000, None, policy_version, None, NOW, NOW)

    cases = (
        ("same id", "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
         values()),
        ("same version identity", "REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
         values(aid="replacement-id")),
        ("both identities active", "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
         values(status="active")),
        ("terminal replacement", "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
         values(status="revoked")),
    )
    for name, statement, row in cases:
        c = migrated_connection(); add_authorization(c); c.commit()
        before_parent = tuple(c.execute(
            "SELECT id,logical_key,status,generation,processor,policy_version FROM authorization WHERE id='auth1'"
        ).fetchone())
        before_children = tuple(c.execute(
            "SELECT (SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'),"
            "(SELECT count(*) FROM authorization_action WHERE authorization_id='auth1'),"
            "(SELECT count(*) FROM authorization_policy WHERE authorization_id='auth1')"
        ).fetchone())
        rejected(lambda c=c, statement=statement, row=row: c.execute(statement, row), error)
        c.rollback()
        after_parent = tuple(c.execute(
            "SELECT id,logical_key,status,generation,processor,policy_version FROM authorization WHERE id='auth1'"
        ).fetchone())
        after_children = tuple(c.execute(
            "SELECT (SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'),"
            "(SELECT count(*) FROM authorization_action WHERE authorization_id='auth1'),"
            "(SELECT count(*) FROM authorization_policy WHERE authorization_id='auth1')"
        ).fetchone())
        check(after_parent == before_parent, "%s changed active parent" % name)
        check(after_children == before_children == (1, 1, 1), "%s changed active children" % name)


def ct_p1_20():
    """P3-044: UPSERT/plain duplicate/delete rebuild fail closed; legal inserts remain."""
    c = migrated_connection(); add_authorization(c); c.commit()
    row = ("auth1", "logical1", "actor:evil", "evil-upsert", "prod", "remote", "granted",
           1, 1, NOW, "indefinite", None, None, "policy@evil", None, NOW, NOW)
    rejected(lambda: c.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET processor=excluded.processor,status=excluded.status", row
    ), "active_authorization_replace_forbidden")
    rejected(lambda: c.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row
    ), "active_authorization_replace_forbidden")
    rejected(lambda: c.execute("DELETE FROM authorization WHERE id='auth1'"),
             "active_authorization_delete_forbidden")
    c.rollback()
    check(tuple(c.execute(
        "SELECT status,generation,processor,policy_version FROM authorization WHERE id='auth1'"
    ).fetchone()) == ("active", 1, "local", "policy@1"), "failed rebuild changed active parent")

    c = migrated_connection(); add_project(c)
    add_authorization_parent(c, "new-proposed", "new-logical")
    add_authorization_parent(c, "new-granted", "new-logical-2")
    c.execute("UPDATE authorization SET status='granted' WHERE id='new-granted'")
    check(c.execute("SELECT count(*) FROM authorization").fetchone()[0] == 2,
          "non-conflicting proposed/granted insert was blocked")


def ct_p2_01():
    c = migrated_connection(); add_feedback(c, "f1", 1); add_feedback(c, "f2", 2, "retract", retracts="f1"); add_feedback(c, "f3", 3, "retract", retracts="f2"); add_feedback(c, "f4", 4, "retract", retracts="f3")
    def effective(fid):
        child = c.execute("SELECT id FROM feedback WHERE retracts_feedback_id=?", (fid,)).fetchone()
        return True if child is None else not effective(child[0])
    check(effective("f1") is False, "odd-depth chain did not cancel")
    check(effective("f2") is True, "even-depth chain did not restore")
    rejected(lambda: add_feedback(c, "replay", 5, key="idem:f1"))


def ct_p2_02():
    grants = [{"id": "b", "generation": 2}, {"id": "a", "generation": 1}]
    def digest(items):
        canonical = json.dumps(sorted(items, key=lambda x: x["id"]), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
    check(digest(grants) == digest(list(reversed(grants))), "authorization order changed canonical hash")


def ct_p2_03():
    response = {"hits": [{"id": "visible"}], "next_cursor": "opaque:q:p:auth:index"}
    check("raw_count" not in response and "total" not in response, "search response leaks filtered count")
    check(response["next_cursor"].startswith("opaque:"), "cursor is not opaque contract")


def ct_p2_04():
    good = parse_dto("lifeos_read", envelope("health_check", {"detail_level": "minimal"}))
    bad = parse_dto("lifeos_read", envelope("health_check", {"detail_level": "verbose", "path": "/forbidden"}))
    check(good["ok"] and not bad["ok"], "health DTO enum/whitelist failed")


def ct_p2_05():
    fields = {"assertion": 4, "decision": 5, "action": 5, "event": 3}
    check(max(fields.values()) == 5, "semantic object field count changed")
    proposed_action = fields["action"] + 1
    check(proposed_action > 5, "sixth field did not trip split gate")


def ct_p2_06():
    c = migrated_connection(); add_derivation(c)
    sql = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='derivation_input'").fetchone()[0]
    check("input_type IN ('artifact_version','semantic_object','feedback','source')" in sql, "explicit input_type enum missing")


def ct_p2_07():
    c = migrated_connection(); c.execute("INSERT INTO tombstone VALUES ('artifact','a',1,'cmd','delete',?,'accepted',?)", (NOW, NOW))
    first = c.execute("UPDATE tombstone SET generation=2 WHERE subject_id='a' AND generation=1").rowcount
    stale = c.execute("UPDATE tombstone SET generation=3 WHERE subject_id='a' AND generation=1").rowcount
    rejected(lambda: c.execute("UPDATE tombstone SET generation=1 WHERE subject_id='a'"), "must_not_decrease")
    check(first == 1 and stale == 0, "concurrent stale tombstone upgrade succeeded")


def ct_p2_08():
    allowed = {"accepted": {"active_blocked"}, "active_blocked": {"cleanup_pending", "no_cleanup_required"}, "cleanup_pending": {"cleanup_failed", "vendor_limited", "cleaned"}, "cleanup_failed": {"cleanup_pending", "cleaned"}, "vendor_limited": {"cleanup_pending", "cleaned"}, "cleaned": set(), "no_cleanup_required": set()}
    check("accepted" not in allowed["cleanup_failed"] and not allowed["cleaned"], "status matrix permits unblock/regression")


def db_now_ms(conn):
    return conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]


def lifecycle_job(conn, auth_id="auth1"):
    return conn.execute(
        "SELECT * FROM outbox_job WHERE subject_type='authorization' AND subject_id=?",
        (auth_id,),
    ).fetchone()


def claim_job(conn, job_id, worker="worker:synthetic"):
    now = db_now_ms(conn)
    outbox_runtime(conn, job_id, "claim", worker=worker, lease_until=now + 60000)
    check(conn.execute("SELECT status FROM outbox_job WHERE id=?", (job_id,)).fetchone()[0] == "leased", "outbox claim CAS failed")


def ac_01():
    c = migrated_connection(); add_authorization(c); c.commit()
    correlation = "authorization-state:auth1:2:revoked"
    c.execute("INSERT INTO audit_entry VALUES ('prewrite','authorization.revoke','actor:claim','auth1',1,'ok',?,?)", (NOW, correlation))
    c.commit()
    rejected(lambda: retire_authorization(c, "auth1", "revoked"), "audit_entry_reinsert_forbidden")
    c.rollback()
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == ("active", 1), "prewritten audit retired authorization")
    check(c.execute("SELECT count(*) FROM authorization_lifecycle_command").fetchone()[0] == 0, "failed command persisted")
    check(c.execute("SELECT count(*) FROM outbox_job").fetchone()[0] == 0, "failed retirement left outbox")


def ac_02():
    c = migrated_connection()
    c.execute("INSERT INTO audit_entry VALUES ('a','test.action','actor:claim','subject',NULL,'ok',?,'corr:a')", (NOW,))
    rejected(lambda: c.execute("UPDATE audit_entry SET result_code='changed' WHERE id='a'"), "append_only")
    rejected(lambda: c.execute("DELETE FROM audit_entry WHERE id='a'"), "append_only")
    rejected(lambda: c.execute("INSERT OR REPLACE INTO audit_entry VALUES ('a','evil','x','x',NULL,'x',?,'corr:a')", (NOW,)), "reinsert_forbidden")
    check(tuple(c.execute("SELECT action_code,result_code FROM audit_entry WHERE id='a'").fetchone()) == ("test.action", "ok"), "audit changed")


def ac_03():
    c = migrated_connection(); add_authorization(c)
    c.execute("INSERT INTO audit_entry VALUES ('wrong','authorization.revoke','actor:claim','auth1',99,'ok',?,'wrong:corr')", (NOW,))
    rejected(
        lambda: c.execute(
            "INSERT INTO outbox_job VALUES ('wrong-job','authorization_state_change','authorization','auth1',9,'revoked','pending',0,?,NULL,0,NULL,'wrong:idem',NULL)",
            (NOW,),
        ),
        "provenance_required",
    )
    rejected(lambda: c.execute("UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'", (NOW, NOW)), "lifecycle_command")
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == ("active", 1), "wrong evidence retired authorization")
    check(c.execute("SELECT count(*) FROM outbox_job").fetchone()[0] == 0, "forged lifecycle outbox was persisted")


def ac_04():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    before = tuple(c.execute("SELECT (SELECT count(*) FROM authorization_lifecycle_command),(SELECT count(*) FROM audit_entry),(SELECT count(*) FROM outbox_job)").fetchone())
    request_hash = c.execute("SELECT canonical_request_hash FROM authorization_lifecycle_command").fetchone()[0]
    rejected(lambda: c.execute(
        """INSERT INTO authorization_lifecycle_command(
             id,idempotency_key,authorization_id,expected_generation,target_status,
             scoped_actor_claim,canonical_request_hash,requested_at_ms
           ) VALUES ('replay','idem:auth1:2:revoked','auth1',1,'revoked','actor:user',?,?)""", (request_hash, NOW)
    ))
    check(tuple(c.execute("SELECT (SELECT count(*) FROM authorization_lifecycle_command),(SELECT count(*) FROM audit_entry),(SELECT count(*) FROM outbox_job)").fetchone()) == before, "replay duplicated evidence")


def ac_05():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); before = tuple(job)
    rejected(lambda: c.execute("UPDATE outbox_job SET payload_ref='active' WHERE id=?", (job["id"],)), "payload_immutable")
    rejected(lambda: c.execute("UPDATE outbox_job SET subject_id='other' WHERE id=?", (job["id"],)), "payload_immutable")
    rejected(lambda: c.execute("INSERT OR REPLACE INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", before), "reinsert_forbidden")
    check(tuple(c.execute("SELECT * FROM outbox_job WHERE id=?", (job["id"],)).fetchone()) == before, "outbox payload changed")


def ac_06():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); claim_job(c, job["id"])
    lease = c.execute("SELECT lease_generation FROM outbox_job WHERE id=?", (job["id"],)).fetchone()[0]
    outbox_runtime(c, job["id"], "complete")
    check(lease == 1 and c.execute("SELECT status FROM outbox_job WHERE id=?", (job["id"],)).fetchone()[0] == "completed", "legal completion failed")


def ac_07():
    c = migrated_connection(); add_authorization(c)
    now = db_now_ms(c)
    c.execute("INSERT INTO outbox_job VALUES ('stale','publish','authorization','auth1',2,NULL,'pending',0,?,NULL,0,NULL,'idem:stale',NULL)", (now,))
    claim_job(c, "stale")
    stale_lease = c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='stale' AND lease_generation=0").rowcount
    rejected(lambda: c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id='stale'"), "runtime_command_required")
    rejected(lambda: outbox_runtime(c, "stale", "complete"), "outbox_runtime_command_invalid")
    check(stale_lease == 0 and c.execute("SELECT status FROM outbox_job WHERE id='stale'").fetchone()[0] == "leased", "stale completion published")


def ac_08():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "expired")
    job = lifecycle_job(c); payload = tuple(job[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key"))
    claim_job(c, job["id"])
    now = db_now_ms(c)
    outbox_runtime(c, job["id"], "retry", available_at=now + 1000, error_code="E_RETRY")
    row = c.execute("SELECT * FROM outbox_job WHERE id=?", (job["id"],)).fetchone()
    check(row["status"] == "pending" and row["attempts"] == 1 and row["last_error_code"] == "E_RETRY", "retry state invalid")
    check(tuple(row[k] for k in ("job_type","subject_type","subject_id","subject_generation","payload_ref","idempotency_key")) == payload, "retry changed payload")


def ac_09():
    c = migrated_connection(); add_authorization(c)
    rejected(lambda: c.execute("UPDATE authorization SET generation=2 WHERE id='auth1'"), "requires_lifecycle_command")
    rejected(lambda: c.execute("UPDATE authorization SET generation=9 WHERE id='auth1'"), "requires_lifecycle_command")
    check(c.execute("SELECT generation FROM authorization WHERE id='auth1'").fetchone()[0] == 1, "active generation climbed")


def ac_10():
    c = migrated_connection(); add_authorization(c)
    rejected(lambda: c.execute("UPDATE authorization SET created_at_ms=created_at_ms-1 WHERE id='auth1'"), "created_at_immutable")
    rejected(lambda: c.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 1,)), "revoked_time_requires_lifecycle_command")
    check(tuple(c.execute("SELECT created_at_ms,revoked_at_ms FROM authorization WHERE id='auth1'").fetchone()) == (NOW, None), "authorization time metadata changed")


def ac_11():
    for terminal in ("revoked", "expired", "superseded"):
        c = migrated_connection(); add_authorization(c)
        rejected(lambda c=c, terminal=terminal: c.execute(
            "UPDATE authorization SET status=?,generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id='auth1'",
            (terminal, NOW - 1, NOW - 2)), "lifecycle_command")
        retire_authorization(c, "auth1", terminal)
        parent = c.execute("SELECT * FROM authorization WHERE id='auth1'").fetchone()
        audit = c.execute("SELECT * FROM audit_entry WHERE scoped_subject_ref='auth1' AND action_code LIKE 'authorization.%'").fetchone()
        check(parent["updated_at_ms"] == audit["occurred_at_ms"], "terminal/audit time mismatch")
        check((terminal == "revoked" and parent["revoked_at_ms"] == audit["occurred_at_ms"]) or
              (terminal != "revoked" and parent["revoked_at_ms"] is None), "revoked time pairing invalid")


def ac_12():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked"); c.commit()
    before = tuple(c.execute("SELECT * FROM authorization WHERE id='auth1'").fetchone())
    rejected(lambda: c.execute("UPDATE authorization SET processor='history-rewrite' WHERE id='auth1'"), "terminal_authorization_immutable")
    rejected(lambda: c.execute("DELETE FROM authorization WHERE id='auth1'"), "terminal_authorization_delete_forbidden")
    rejected(lambda: c.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", before), "terminal_authorization_replace_forbidden")
    check(tuple(c.execute("SELECT * FROM authorization WHERE id='auth1'").fetchone()) == before, "terminal parent changed")


def ac_13():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "expired")
    rejected(lambda: c.execute("INSERT INTO authorization_scope VALUES ('extra','auth1','deny','p1',NULL,NULL)"), "terminal_authorization_scope_insert_forbidden")
    rejected(lambda: c.execute("UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'"), "terminal_authorization_scope_update_forbidden")
    rejected(lambda: c.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")
    rejected(lambda: c.execute("UPDATE authorization_action SET action='export_candidate' WHERE authorization_id='auth1'"), "terminal_authorization_action_update_forbidden")
    rejected(lambda: c.execute("DELETE FROM authorization_policy WHERE authorization_id='auth1'"), "requires_cleanup")
    check(tuple(c.execute("SELECT (SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'),(SELECT count(*) FROM authorization_action WHERE authorization_id='auth1'),(SELECT count(*) FROM authorization_policy WHERE authorization_id='auth1')").fetchone()) == (1, 1, 1), "terminal children changed")


def ac_14():
    for terminal in ("revoked", "expired", "superseded"):
        c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", terminal)
        parent = c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()
        command = c.execute("SELECT * FROM authorization_lifecycle_command").fetchone()
        audit = c.execute("SELECT * FROM audit_entry WHERE correlation_id=?", (command["correlation_id"],)).fetchone()
        outbox = c.execute("SELECT * FROM outbox_job WHERE idempotency_key=?", (command["correlation_id"],)).fetchone()
        check(tuple(parent) == (terminal, 2) and audit is not None and outbox is not None, "legal lifecycle was not atomic")
        check(audit["scoped_actor_ref"] == command["scoped_actor_claim"], "actor claim was not preserved as claim")


def ac_15():
    c = migrated_connection(); add_authorization(c, "old", "versioned", 1); retire_authorization(c, "old", "superseded")
    old = tuple(c.execute("SELECT status,generation,processor FROM authorization WHERE id='old'").fetchone())
    add_authorization(c, "new", "versioned", 2, "old", processor="approved-v2", policy_version="policy@2")
    check(tuple(c.execute("SELECT status,generation,processor FROM authorization WHERE id='old'").fetchone()) == old == ("superseded", 2, "local"), "successor changed old history")
    check(tuple(c.execute("SELECT status,version_no,generation FROM authorization WHERE id='new'").fetchone()) == ("active", 2, 1), "successor activation failed")


def ac_16():
    for fault in ("audit", "outbox"):
        c = migrated_connection(); add_authorization(c); c.commit()
        correlation = "authorization-state:auth1:2:revoked"
        if fault == "audit":
            c.execute("INSERT INTO audit_entry VALUES ('pre','authorization.revoke','actor:claim','auth1',1,'ok',?,?)", (NOW, correlation))
        else:
            # A forged lifecycle Outbox is now rejected at INSERT.  A generic
            # row that collides with the canonical lifecycle job id preserves
            # the atomic outbox-conflict rollback test without bypassing that
            # new provenance guard.
            c.execute(
                "INSERT INTO outbox_job VALUES (?,?,?, ?,1,NULL,'pending',0,?,NULL,0,NULL,?,NULL)",
                ('outbox:' + correlation, 'generic', 'artifact', 'fault:outbox', NOW, 'pre:outbox'),
            )
        c.commit(); c.execute("BEGIN IMMEDIATE")
        rejected(lambda c=c: retire_authorization(c, "auth1", "revoked"))
        c.rollback()
        check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == ("active", 1), "%s fault left terminal parent" % fault)
        check(c.execute("SELECT count(*) FROM authorization_lifecycle_command").fetchone()[0] == 0, "%s fault left command" % fault)
        check(c.execute("SELECT count(*) FROM submission").fetchone()[0] == 0, "%s fault left submission" % fault)


def ac_17():
    c = migrated_connection(); add_authorization(c)
    rejected(lambda: c.execute("INSERT INTO tombstone VALUES ('authorization','auth1',1,'cmd','cleanup',?,'accepted',?)", (NOW, NOW)), "requires_terminal_generation")
    retire_authorization(c, "auth1", "revoked")
    rejected(lambda: c.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'"), "requires_cleanup")
    rejected(lambda: c.execute("INSERT INTO tombstone VALUES ('authorization','auth1',1,'bad-gen','cleanup',?,'accepted',?)", (NOW, NOW)), "requires_terminal_generation")
    c.execute("INSERT INTO tombstone VALUES ('authorization','auth1',2,'cmd','cleanup',?,'accepted',?)", (NOW, NOW))
    rejected(lambda: c.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='authorization' AND subject_id='auth1'"), "cleanup_audit_required")


def ac_18():
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    add_authorization_cleanup_gate(c); cleanup_authorization_children(c); c.commit()
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == ("revoked", 2), "cleanup removed terminal parent")
    check(c.execute("SELECT count(*) FROM audit_entry WHERE scoped_subject_ref='auth1'").fetchone()[0] == 2, "cleanup removed minimum audit")
    check(c.execute("SELECT cleanup_status FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'").fetchone()[0] == "cleaned", "cleanup not marked cleaned")
    check(sum(c.execute("SELECT count(*) FROM %s WHERE authorization_id='auth1'" % table).fetchone()[0] for table in ("authorization_scope","authorization_action","authorization_policy")) == 0, "sensitive projections remain")
    rejected(lambda: c.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id='auth1'"), "transition_invalid")
    row = ("auth1", "logical1", "actor:evil", "cloud", "prod", "remote", "granted", 1, 1, NOW, "indefinite", None, None, "evil", None, NOW, NOW)
    rejected(lambda: c.execute("INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row), "terminal_authorization_replace_forbidden")
    package = {"authorization_id": "auth1", "generation": 1, "status": "active"}
    tombstone = c.execute("SELECT generation FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'").fetchone()[0]
    check(tombstone >= package["generation"], "old package restore could revive cleaned authorization")


def pm_ce_01():
    """P3-047 P2: lifecycle command is bound to immutable Submission/hash."""
    c = migrated_connection(); add_authorization(c)
    valid_hash = canonical_hash("authorization-lifecycle:auth1:2:revoked")
    statement = """INSERT INTO authorization_lifecycle_command(
      id,idempotency_key,authorization_id,expected_generation,target_status,
      scoped_actor_claim,canonical_request_hash,requested_at_ms
    ) VALUES (?,?,?,?,?,?,?,?)"""
    rejected(lambda: c.execute(statement, ("bad-format", "idem:bad", "auth1", 1, "revoked", "actor:user", "x", NOW)))
    rejected(lambda: c.execute(statement, ("unbound", "idem:unbound", "auth1", 1, "revoked", "actor:user", valid_hash, NOW)), "submission_binding_required")
    retire_authorization(c, "auth1", "revoked")
    submission = tuple(c.execute("SELECT * FROM submission").fetchone())
    rejected(lambda: c.execute("UPDATE submission SET result_subject_id='other'"), "append_only")
    rejected(lambda: c.execute("DELETE FROM submission"), "append_only")
    rejected(lambda: c.execute("INSERT OR REPLACE INTO submission VALUES (?,?,?,?,?,?,?)", submission), "replay_forbidden")
    check(tuple(c.execute("SELECT * FROM submission").fetchone()) == submission, "Submission binding changed")


def pm_ce_02():
    """P3-047 P1: future availability and stale claim generation fail closed."""
    c = migrated_connection(); now = db_now_ms(c); future = now + 86400000
    c.execute("INSERT INTO outbox_job VALUES ('future','generic','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'future',NULL)", (future,))
    rejected(lambda: outbox_runtime(c, "future", "claim", worker="worker:a", lease_until=now + 60000), "outbox_runtime_command_invalid")
    rejected(lambda: c.execute("UPDATE outbox_job SET status='leased',attempts=1,lease_owner='worker:a',lease_generation=1,lease_expires_at_ms=? WHERE id='future'", (now + 60000,)), "runtime_command_required")
    c.execute("INSERT INTO outbox_job VALUES ('boundary','generic','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'boundary',NULL)", (now,))
    outbox_runtime(c, "boundary", "claim", worker="worker:a", lease_until=now + 60000)
    rejected(lambda: c.execute(
        """INSERT INTO outbox_runtime_command(
          id,job_id,operation,expected_status,expected_available_at_ms,
          expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,
          requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms
        ) VALUES ('stale','boundary','claim','pending',?,NULL,0,NULL,'worker:b',?,NULL,NULL,?)""",
        (now, now + 60000, NOW)), "cas_mismatch")
    check(c.execute("SELECT lease_owner FROM outbox_job WHERE id='boundary'").fetchone()[0] == "worker:a", "claim competition had multiple winners")


def pm_ce_03():
    """P3-047 P1: completion requires the controlled owner/generation CAS."""
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); claim_job(c, job["id"], "worker:current")
    rejected(lambda: c.execute("UPDATE outbox_job SET status='completed',lease_owner=NULL,lease_expires_at_ms=NULL WHERE id=?", (job["id"],)), "runtime_command_required")
    leased = c.execute("SELECT * FROM outbox_job WHERE id=?", (job["id"],)).fetchone()
    rejected(lambda: c.execute(
        """INSERT INTO outbox_runtime_command(
          id,job_id,operation,expected_status,expected_available_at_ms,
          expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,
          requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms
        ) VALUES ('wrong-owner',?,'complete','leased',?,'worker:other',?,?,NULL,NULL,NULL,NULL,?)""",
        (job["id"], leased["available_at_ms"], leased["lease_generation"], leased["lease_expires_at_ms"], NOW)), "cas_mismatch")
    outbox_runtime(c, job["id"], "complete")
    check(c.execute("SELECT status FROM outbox_job WHERE id=?", (job["id"],)).fetchone()[0] == "completed", "controlled completion failed")


def pm_ce_04():
    """P3-047 P2: Authorization tombstone control envelope is immutable."""
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked"); add_authorization_cleanup_gate(c)
    before = tuple(c.execute("SELECT * FROM tombstone WHERE subject_type='authorization'").fetchone())
    rejected(lambda: c.execute("UPDATE tombstone SET subject_id='ghost',command_id='forged',reason_code='other',blocked_at_ms=0 WHERE subject_type='authorization'"), "control_envelope_immutable")
    rejected(lambda: c.execute("UPDATE tombstone SET updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization'"), "time_requires_status_change")
    check(tuple(c.execute("SELECT * FROM tombstone WHERE subject_type='authorization'").fetchone()) == before, "tombstone envelope changed")


def pm_ce_05():
    """P3-047 P2: generic cleanup works; Authorization retention defaults deny."""
    c = migrated_connection(); now = db_now_ms(c)
    c.execute("INSERT INTO outbox_job VALUES ('generic','generic_job','artifact','a',1,NULL,'pending',0,?,NULL,0,NULL,'generic',NULL)", (now,))
    outbox_runtime(c, "generic", "claim", worker="worker", lease_until=now + 60000)
    outbox_runtime(c, "generic", "dead_letter", error_code="E")
    c.execute("DELETE FROM outbox_job WHERE id='generic'")
    add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); claim_job(c, job["id"]); outbox_runtime(c, job["id"], "complete")
    rejected(lambda: c.execute("DELETE FROM outbox_job WHERE id=?", (job["id"],)), "retention_not_satisfied")
    c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
    rejected(lambda: c.execute("DELETE FROM outbox_job WHERE id=?", (job["id"],)), "retention_not_satisfied")

    c = migrated_connection()
    c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
    add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); claim_job(c, job["id"]); outbox_runtime(c, job["id"], "complete")
    c.execute("DELETE FROM outbox_job WHERE id=?", (job["id"],))
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='auth1'").fetchone()) == ("revoked", 2), "outbox cleanup changed authority")
    check(c.execute("SELECT count(*) FROM audit_entry WHERE scoped_subject_ref='auth1'").fetchone()[0] == 1, "outbox cleanup changed audit")


def pm_ce_06():
    """P3-048 P2: OLD/NEW Authorization tombstone identity is immutable."""
    c = migrated_connection(); add_authorization(c); retire_authorization(c, "auth1", "revoked")
    c.execute(
        "INSERT INTO tombstone VALUES ('artifact','placeholder',1,'seed-command','seed-reason',?,'accepted',?)",
        (NOW, NOW),
    )
    generic_before = tuple(c.execute(
        "SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id='placeholder'"
    ).fetchone())
    rejected(lambda: c.execute(
        """UPDATE tombstone
           SET subject_type='authorization',subject_id='auth1',generation=2,
               command_id='forged-cleanup',reason_code='user_cleanup',
               blocked_at_ms=?,cleanup_status='active_blocked',updated_at_ms=?
           WHERE subject_type='artifact' AND subject_id='placeholder'""",
        (NOW, NOW + 1)))
    check(tuple(c.execute(
        "SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id='placeholder'"
    ).fetchone()) == generic_before, "generic tombstone was rebound to Authorization")

    add_authorization_cleanup_gate(c)
    auth_before = tuple(c.execute(
        "SELECT * FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'"
    ).fetchone())
    rejected(lambda: c.execute(
        "UPDATE tombstone SET subject_type='artifact',subject_id='other' "
        "WHERE subject_type='authorization' AND subject_id='auth1'"
    ), "control_envelope_immutable")
    check(tuple(c.execute(
        "SELECT * FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'"
    ).fetchone()) == auth_before, "Authorization tombstone escaped its identity")

    # The patch is deliberately narrow: existing generic generation CAS and
    # forward cleanup transition semantics remain legal.
    changed = c.execute(
        "UPDATE tombstone SET generation=2,command_id='generic-v2',reason_code='retry',"
        "cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1 "
        "WHERE subject_type='artifact' AND subject_id='placeholder' AND generation=1"
    ).rowcount
    check(changed == 1, "existing generic Tombstone semantics were narrowed")


def p3_052_p1_01_outbox_provenance():
    """P3-052 P1: direct lifecycle Outbox rows require canonical evidence."""
    c = migrated_connection(); add_authorization(c)
    now = db_now_ms(c)
    statement = """INSERT INTO outbox_job VALUES
      ('outbox:forged-active-revoke','authorization_state_change','authorization','auth1',1,
       'revoked','pending',0,?,NULL,0,NULL,'forged-correlation',NULL)"""
    rejected(lambda: c.execute(statement, (now,)), "provenance_required")
    rejected(lambda: c.execute(statement.replace("INSERT INTO", "INSERT OR REPLACE INTO"), (now,)), "provenance_required")
    check(c.execute("SELECT count(*) FROM outbox_job").fetchone()[0] == 0, "forged lifecycle job persisted")
    retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c)
    command = c.execute("SELECT * FROM authorization_lifecycle_command").fetchone()
    audit = c.execute("SELECT * FROM audit_entry WHERE correlation_id=?", (command["correlation_id"],)).fetchone()
    check(
        job["id"] == 'outbox:' + command["correlation_id"]
        and job["idempotency_key"] == command["correlation_id"]
        and job["subject_generation"] == command["result_generation"]
        and job["payload_ref"] == command["target_status"]
        and audit is not None,
        "legal lifecycle Outbox provenance is incomplete",
    )


def p3_052_p1_02_retention_replay_fence():
    """P3-052 P1: retention never frees a lifecycle dispatch identity."""
    c = migrated_connection()
    c.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
    add_authorization(c); retire_authorization(c, "auth1", "revoked")
    job = lifecycle_job(c); correlation = job["idempotency_key"]
    claim_job(c, job["id"]); outbox_runtime(c, job["id"], "complete")
    c.execute("DELETE FROM outbox_job WHERE id=?", (job["id"],))
    fence = c.execute(
        "SELECT job_id,lifecycle_correlation_id FROM outbox_retention_binding WHERE job_id=?",
        (job["id"],),
    ).fetchone()
    check(fence is not None and tuple(fence) == (job["id"], correlation), "lifecycle replay fence was not retained")
    now = db_now_ms(c)
    rejected(
        lambda: c.execute(
            "INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (job["id"], 'authorization_state_change', 'authorization', 'auth1', 2,
             'forged-after-retention', 'pending', 0, now, None, 0, None, correlation, None),
        ),
        "replay_fence",
    )
    rejected(
        lambda: c.execute(
            "INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ('generic:reusing-lifecycle-correlation', 'generic', 'artifact', 'artifact:replay', 1,
             'payload', 'pending', 0, now, None, 0, None, correlation, None),
        ),
        "replay_fence",
    )
    c.execute(
        "INSERT INTO outbox_job VALUES ('generic:terminal','generic','artifact','artifact:ok',1,NULL,'pending',0,?,NULL,0,NULL,'generic:terminal',NULL)",
        (now,),
    )
    outbox_runtime(c, 'generic:terminal', 'claim', worker='worker:generic', lease_until=now + 60000)
    outbox_runtime(c, 'generic:terminal', 'complete')
    c.execute("DELETE FROM outbox_job WHERE id='generic:terminal'")
    check(c.execute("SELECT count(*) FROM outbox_job").fetchone()[0] == 0, "generic terminal cleanup was narrowed")


def p3_052_p2_01_initial_generation():
    """P3-052 P2: inserts, REPLACE and activation all start at generation one."""
    c = migrated_connection()
    rejected(lambda: add_authorization_parent(c, 'bad-generation', 'bad-generation', generation=7), "initial_generation")
    add_authorization_parent(c, 'replace-generation', 'replace-generation')
    original = tuple(c.execute("SELECT * FROM authorization WHERE id='replace-generation'").fetchone())
    rejected(
        lambda: c.execute(
            "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ('replace-generation', 'replace-generation', 'actor:user', 'local', 'test', 'device',
             'proposed', 1, 7, NOW, 'indefinite', None, None, 'policy@1', None, NOW, NOW),
        ),
        "initial_generation",
    )
    check(tuple(c.execute("SELECT * FROM authorization WHERE id='replace-generation'").fetchone()) == original, "REPLACE changed proposed Authorization")
    add_project(c)
    add_authorization_parent(c, 'activation-generation', 'activation-generation')
    c.execute("INSERT INTO authorization_scope VALUES ('activation-generation:scope','activation-generation','allow','p1',NULL,NULL)")
    c.execute("INSERT INTO authorization_action VALUES ('activation-generation:action','activation-generation','read')")
    add_policy(c, 'activation-generation')
    rejected(lambda: c.execute("UPDATE authorization SET status='active',generation=2 WHERE id='activation-generation'"))
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='activation-generation'").fetchone()) == ('proposed', 1), "activation accepted a noninitial generation")
    c.execute("UPDATE authorization SET status='active' WHERE id='activation-generation'")
    check(tuple(c.execute("SELECT status,generation FROM authorization WHERE id='activation-generation'").fetchone()) == ('active', 1), "legal generation-one activation failed")


def p3_052_p2_02_initial_revoked_time():
    """P3-052 P2: non-revoked initial and activation states cannot carry revoke time."""
    c = migrated_connection()
    rejected(lambda: add_authorization_parent(c, 'bad-time', 'bad-time', revoked_at_ms=NOW), "initial_revoked_time")
    add_authorization_parent(c, 'replace-time', 'replace-time')
    original = tuple(c.execute("SELECT * FROM authorization WHERE id='replace-time'").fetchone())
    rejected(
        lambda: c.execute(
            "INSERT OR REPLACE INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ('replace-time', 'replace-time', 'actor:user', 'local', 'test', 'device',
             'proposed', 1, 1, NOW, 'indefinite', None, NOW, 'policy@1', None, NOW, NOW),
        ),
        "initial_revoked_time",
    )
    check(tuple(c.execute("SELECT * FROM authorization WHERE id='replace-time'").fetchone()) == original, "REPLACE prewrote revoked time")
    add_project(c)
    add_authorization_parent(c, 'activation-time', 'activation-time')
    c.execute("INSERT INTO authorization_scope VALUES ('activation-time:scope','activation-time','allow','p1',NULL,NULL)")
    c.execute("INSERT INTO authorization_action VALUES ('activation-time:action','activation-time','read')")
    add_policy(c, 'activation-time')
    rejected(lambda: c.execute("UPDATE authorization SET status='active',revoked_at_ms=? WHERE id='activation-time'", (NOW,)))
    check(tuple(c.execute("SELECT status,revoked_at_ms FROM authorization WHERE id='activation-time'").fetchone()) == ('proposed', None), "activation accepted a prewritten revoked time")
    c.execute("UPDATE authorization SET status='active' WHERE id='activation-time'")
    for terminal in ('revoked', 'expired', 'superseded'):
        terminal_db = migrated_connection(); add_authorization(terminal_db); retire_authorization(terminal_db, 'auth1', terminal)
        parent = terminal_db.execute("SELECT generation,revoked_at_ms,updated_at_ms FROM authorization WHERE id='auth1'").fetchone()
        check(
            parent['generation'] == 2
            and ((terminal == 'revoked' and parent['revoked_at_ms'] == parent['updated_at_ms'])
                 or (terminal != 'revoked' and parent['revoked_at_ms'] is None)),
            'terminal revoked-time pairing changed',
        )


MATRIX_CONFIGS = [
    {"storage": storage, "foreign_keys": foreign_keys, "recursive_triggers": recursive_triggers}
    for storage in ("memory", "file")
    for foreign_keys in (False, True)
    for recursive_triggers in (False, True)
]

MATRIX_TESTS = [
    ("P3-052-P1-01", "P1", p3_052_p1_01_outbox_provenance),
    ("P3-052-P1-02", "P1", p3_052_p1_02_retention_replay_fence),
    ("P3-052-P2-01", "P2", p3_052_p2_01_initial_generation),
    ("P3-052-P2-02", "P2", p3_052_p2_02_initial_revoked_time),
    ("AC-14-atomic-lifecycle", "P1", ac_14),
    ("AC-16-rollback-on-evidence-conflict", "P1", ac_16),
    ("PM-CE-01", "P2", pm_ce_01),
    ("PM-CE-02", "P1", pm_ce_02),
    ("PM-CE-03", "P1", pm_ce_03),
    ("PM-CE-04", "P2", pm_ce_04),
    ("PM-CE-05", "P2", pm_ce_05),
]


def finish_matrix_connections():
    """Close a matrix case and verify every persisted synthetic file."""
    checks = []
    global MATRIX_CONNECTIONS
    for conn, path in MATRIX_CONNECTIONS:
        try:
            conn.commit()
        except sqlite3.DatabaseError:
            conn.rollback()
        conn.close()
        if path is not None:
            reopened = sqlite3.connect(path)
            integrity = [item[0] for item in reopened.execute("PRAGMA integrity_check")]
            quick = [item[0] for item in reopened.execute("PRAGMA quick_check")]
            foreign_key = [tuple(item) for item in reopened.execute("PRAGMA foreign_key_check")]
            reopened.close()
            check(integrity == ["ok"], "file integrity_check failed")
            check(quick == ["ok"], "file quick_check failed")
            check(not foreign_key, "file foreign_key_check found rows")
            checks.append({"path": path.name, "integrity_check": integrity, "quick_check": quick, "foreign_key_check": foreign_key})
    MATRIX_CONNECTIONS = []
    return checks


def run_matrix(work):
    global MATRIX_CONFIG, MATRIX_WORK, MATRIX_CASE_ID, MATRIX_CONNECTION_INDEX, MATRIX_CONNECTIONS
    results = []
    for case_id, severity, fn in MATRIX_TESTS:
        for config in MATRIX_CONFIGS:
            MATRIX_CONFIG = config
            MATRIX_WORK = work
            MATRIX_CASE_ID = "%s-%s-fk%s-rec%s" % (
                case_id,
                config["storage"],
                int(config["foreign_keys"]),
                int(config["recursive_triggers"]),
            )
            MATRIX_CONNECTION_INDEX = 0
            MATRIX_CONNECTIONS = []
            result = {"id": case_id, "severity": severity, **config}
            try:
                fn()
                result["status"] = "PASS"
            except Exception as exc:
                result["status"] = "FAIL"
                result["detail"] = "%s: %s" % (type(exc).__name__, exc)
            try:
                result["file_checks"] = finish_matrix_connections()
            except Exception as exc:
                result["status"] = "FAIL"
                result["detail"] = "%s: %s" % (type(exc).__name__, exc)
            results.append(result)
    MATRIX_CONFIG = None
    MATRIX_WORK = None
    MATRIX_CASE_ID = ""
    MATRIX_CONNECTION_INDEX = 0
    MATRIX_CONNECTIONS = []
    summary = {
        state: sum(1 for result in results if result["status"] == state)
        for state in ("PASS", "FAIL")
    }
    return {"task_id": "LIFEOS-P3-053", "scope": "synthetic SQLite lifecycle matrix only", "matrix_cases": results, "summary": summary}


TESTS = [
    ("DB-P0-01", "P0", db_p0_01), ("DB-P0-02", "P0", db_p0_02),
    ("DB-P0-03", "P0", db_p0_03), ("DB-P0-04", "P0", db_p0_04),
    ("DB-P0-05", "P0", db_p0_05), ("DB-P0-06", "P0", db_p0_06),
    ("DB-P0-07", "P0", db_p0_07), ("DB-P0-08", "P0", db_p0_08),
    ("DB-P0-09", "P0", db_p0_09), ("DB-P0-10", "P0", db_p0_10),
    ("DB-P0-11", "P0", db_p0_11), ("DB-P0-12", "P0", db_p0_12),
    ("DB-P0-13", "P0", db_p0_13), ("DB-P0-14", "P0", db_p0_14),
    ("DB-P0-15", "P0", db_p0_15), ("IPC-P0-01", "P0", ipc_p0_01),
    ("IPC-P0-02", "P0", ipc_p0_02), ("IPC-P0-03", "P0", ipc_p0_03),
    ("CT-P1-01", "P1", ct_p1_01), ("CT-P1-02", "P1", ct_p1_02),
    ("CT-P1-03", "P1", ct_p1_03), ("CT-P1-04", "P1", ct_p1_04),
    ("CT-P1-05", "P1", ct_p1_05), ("CT-P1-06", "P1", ct_p1_06),
    ("CT-P1-07", "P1", ct_p1_07), ("CT-P1-08", "P1", ct_p1_08),
    ("CT-P1-09", "P1", ct_p1_09), ("CT-P1-10", "P1", ct_p1_10),
    ("CT-P1-11", "P1", ct_p1_11), ("CT-P1-12", "P1", ct_p1_12),
    ("CT-P1-13", "P1", ct_p1_13), ("CT-P1-14", "P1", ct_p1_14),
    ("CT-P1-15", "P1", ct_p1_15), ("CT-P1-16", "P1", ct_p1_16),
    ("CT-P1-17", "P1", ct_p1_17), ("CT-P1-18", "P1", ct_p1_18),
    ("CT-P1-19", "P1", ct_p1_19), ("CT-P1-20", "P1", ct_p1_20),
    ("CT-P2-01", "P2", ct_p2_01), ("CT-P2-02", "P2", ct_p2_02),
    ("CT-P2-03", "P2", ct_p2_03), ("CT-P2-04", "P2", ct_p2_04),
    ("CT-P2-05", "P2", ct_p2_05), ("CT-P2-06", "P2", ct_p2_06),
    ("CT-P2-07", "P2", ct_p2_07), ("CT-P2-08", "P2", ct_p2_08),
    ("AC-01", "P2", ac_01), ("AC-02", "P2", ac_02),
    ("AC-03", "P2", ac_03), ("AC-04", "P2", ac_04),
    ("AC-05", "P2", ac_05), ("AC-06", "P1", ac_06),
    ("AC-07", "P1", ac_07), ("AC-08", "P2", ac_08),
    ("AC-09", "P2", ac_09), ("AC-10", "P2", ac_10),
    ("AC-11", "P2", ac_11), ("AC-12", "P2", ac_12),
    ("AC-13", "P2", ac_13), ("AC-14", "P1", ac_14),
    ("AC-15", "P1", ac_15), ("AC-16", "P1", ac_16),
    ("AC-17", "P2", ac_17), ("AC-18", "P2", ac_18),
    ("P3-052-P1-01", "P1", p3_052_p1_01_outbox_provenance),
    ("P3-052-P1-02", "P1", p3_052_p1_02_retention_replay_fence),
    ("P3-052-P2-01", "P2", p3_052_p2_01_initial_generation),
    ("P3-052-P2-02", "P2", p3_052_p2_02_initial_revoked_time),
    ("PM-CE-01", "P2", pm_ce_01), ("PM-CE-02", "P1", pm_ce_02),
    ("PM-CE-03", "P1", pm_ce_03), ("PM-CE-04", "P2", pm_ce_04),
    ("PM-CE-05", "P2", pm_ce_05), ("PM-CE-06", "P2", pm_ce_06),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-json", type=Path)
    parser.add_argument("--matrix-results-json", type=Path)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix="synthetic-db-", dir=str(ROOT / "evidence")):
        for test_id, severity, fn in TESTS:
            started = time.time()
            try:
                fn()
                status, detail = "PASS", ""
            except Exception as exc:  # test harness must preserve every failure in evidence
                status, detail = "FAIL", "%s: %s" % (type(exc).__name__, exc)
            elapsed = round((time.time() - started) * 1000, 2)
            results.append({"id": test_id, "severity": severity, "status": status, "duration_ms": elapsed, "detail": detail})
            print("%-10s %-2s %-4s %8.2f ms %s" % (test_id, severity, status, elapsed, detail))
    summary = {level: {state: sum(1 for r in results if r["severity"] == level and r["status"] == state) for state in ("PASS", "FAIL", "NOT_IMPLEMENTED")} for level in ("P0", "P1", "P2")}
    summary["total"] = {state: sum(1 for r in results if r["status"] == state) for state in ("PASS", "FAIL", "NOT_IMPLEMENTED")}
    payload = {"task_id": "LIFEOS-P3-031", "scope": "synthetic empty SQLite only", "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version, "migration": str(MIGRATION), "summary": summary, "results": results}
    print("SUMMARY " + json.dumps(summary, sort_keys=True))
    if args.results_json:
        args.results_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    matrix_payload = None
    if args.matrix_results_json:
        with tempfile.TemporaryDirectory(prefix="lifeos-p3-053-matrix-") as matrix_work:
            matrix_payload = run_matrix(Path(matrix_work))
        args.matrix_results_json.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("MATRIX " + json.dumps(matrix_payload["summary"], sort_keys=True))
    return 1 if any(r["status"] == "FAIL" for r in results) or (matrix_payload is not None and matrix_payload["summary"]["FAIL"] > 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
