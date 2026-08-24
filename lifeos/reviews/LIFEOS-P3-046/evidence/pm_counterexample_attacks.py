#!/usr/bin/env python3
"""PM counterexamples for LIFEOS-P3-046 candidate SQLite contracts."""

import json
import sqlite3
from pathlib import Path


LIFEOS = Path(__file__).resolve().parents[3]
SCHEMA = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
OUTPUT = Path(__file__).resolve().parent / "counterexample_results.json"
NOW = 1786550400000


def fresh():
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(
        "INSERT INTO project VALUES ('p1','Synthetic','test','active',1,?,?,?)",
        (NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "auth1", "logical1", "actor:user", "local", "test", "device",
            "proposed", 1, 1, NOW, "indefinite", None, None, "policy@1",
            None, NOW, NOW,
        ),
    )
    conn.execute(
        "INSERT INTO authorization_scope VALUES "
        "('scope1','auth1','allow','p1',NULL,NULL)"
    )
    conn.execute(
        "INSERT INTO authorization_action VALUES ('action1','auth1','read')"
    )
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("auth1", "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    return conn


def retire(conn, request_hash="request:valid"):
    conn.execute(
        """INSERT INTO authorization_lifecycle_command(
             id,idempotency_key,authorization_id,expected_generation,target_status,
             scoped_actor_claim,canonical_request_hash,requested_at_ms
           ) VALUES ('cmd1','idem1','auth1',1,'revoked','claim:direct',?,?)""",
        (request_hash, NOW),
    )


def finding(fid, severity, title, expected, actual, passed, detail):
    return {
        "id": fid,
        "severity": severity,
        "title": title,
        "expected": expected,
        "actual": actual,
        "status": "PASS" if passed else "BYPASS",
        "detail": detail,
    }


def main():
    results = []

    conn = fresh()
    retire(conn, "x")
    submission_count = conn.execute("SELECT count(*) FROM submission").fetchone()[0]
    results.append(finding(
        "PM-CE-01", "P2", "canonical hash and Submission binding",
        "Malformed/unbound request hash is rejected or bound to a matching Submission",
        "Lifecycle command accepted canonical_request_hash='x' with zero Submission rows",
        False, {"submission_count": submission_count},
    ))
    conn.close()

    conn = fresh()
    retire(conn)
    job_id = conn.execute("SELECT id FROM outbox_job").fetchone()[0]
    db_now = conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]
    future = db_now + 86400000
    conn.execute("UPDATE outbox_job SET available_at_ms=? WHERE id=?", (future, job_id))
    claimed = conn.execute(
        """UPDATE outbox_job
           SET status='leased', attempts=attempts+1, lease_owner='worker:a',
               lease_generation=lease_generation+1, lease_expires_at_ms=?,
               last_error_code=NULL
           WHERE id=? AND status='pending'""",
        (db_now + 60000, job_id),
    ).rowcount
    results.append(finding(
        "PM-CE-02", "P1", "Outbox availability and claim CAS",
        "A future-scheduled job cannot be claimed; claim binds old lease generation",
        "Future-scheduled pending job was leased",
        claimed == 0, {"rows_changed": claimed, "available_at_ms": future, "db_now_ms": db_now},
    ))
    conn.close()

    conn = fresh()
    retire(conn)
    job_id = conn.execute("SELECT id FROM outbox_job").fetchone()[0]
    db_now = conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]
    conn.execute(
        """UPDATE outbox_job
           SET status='leased', attempts=attempts+1, lease_owner='worker:current',
               lease_generation=lease_generation+1, lease_expires_at_ms=?
           WHERE id=?""",
        (db_now + 60000, job_id),
    )
    completed = conn.execute(
        """UPDATE outbox_job
           SET status='completed', lease_owner=NULL, lease_expires_at_ms=NULL
           WHERE id=?""",
        (job_id,),
    ).rowcount
    results.append(finding(
        "PM-CE-03", "P1", "Outbox completion ownership CAS",
        "Completion requires caller-supplied current lease owner and generation CAS",
        "Update without owner/generation predicate completed the currently leased job",
        completed == 0, {"rows_changed": completed},
    ))
    conn.close()

    conn = fresh()
    retire(conn)
    conn.execute(
        "INSERT INTO audit_entry VALUES "
        "('cleanup-a','authorization.cleanup','claim','auth1',1,'redacted_by_user',?,"
        "'authorization-cleanup:auth1:2')",
        (NOW,),
    )
    conn.execute(
        "INSERT INTO tombstone VALUES "
        "('authorization','auth1',2,'cleanup:auth1','user_cleanup',?,'accepted',?)",
        (NOW, NOW),
    )
    conn.execute(
        "UPDATE tombstone SET cleanup_status='active_blocked' "
        "WHERE subject_type='authorization' AND subject_id='auth1'"
    )
    conn.execute(
        "UPDATE tombstone SET cleanup_status='cleanup_pending' "
        "WHERE subject_type='authorization' AND subject_id='auth1'"
    )
    mutated = conn.execute(
        """UPDATE tombstone
           SET subject_id='ghost', command_id='forged', reason_code='other', blocked_at_ms=0
           WHERE subject_type='authorization' AND subject_id='auth1'"""
    ).rowcount
    row = conn.execute(
        "SELECT subject_id,command_id,reason_code,blocked_at_ms FROM tombstone"
    ).fetchone()
    results.append(finding(
        "PM-CE-04", "P2", "Authorization tombstone control-envelope immutability",
        "Subject identity, command, reason, blocked time and generation remain immutable",
        "cleanup_pending tombstone control fields and subject identity were rewritten",
        mutated == 0, {"rows_changed": mutated, "row": list(row)},
    ))
    conn.close()

    conn = fresh()
    db_now = conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER)*1000").fetchone()[0]
    conn.execute(
        "INSERT INTO outbox_job VALUES "
        "('generic','generic_job','artifact','artifact1',1,NULL,'pending',0,?,NULL,0,NULL,'generic:1',NULL)",
        (db_now,),
    )
    conn.execute(
        """UPDATE outbox_job SET status='leased',attempts=1,lease_owner='worker',
           lease_generation=1,lease_expires_at_ms=? WHERE id='generic'""",
        (db_now + 60000,),
    )
    conn.execute(
        """UPDATE outbox_job SET status='dead_letter',lease_owner=NULL,
           lease_expires_at_ms=NULL,last_error_code='E' WHERE id='generic'"""
    )
    rejected = False
    error = None
    try:
        conn.execute("DELETE FROM outbox_job WHERE id='generic'")
    except sqlite3.DatabaseError as exc:
        rejected = True
        error = str(exc)
    results.append(finding(
        "PM-CE-05", "P2", "Generic terminal Outbox cleanup regression",
        "Terminal non-authoritative jobs have a defined audited/retained cleanup route",
        "All non-authorization terminal jobs are unconditionally undeletable",
        not rejected, {"error": error},
    ))
    conn.close()

    payload = {
        "task_id": "LIFEOS-P3-046",
        "scope": "synthetic in-memory SQLite PM counterexamples",
        "summary": {
            "pass": sum(x["status"] == "PASS" for x in results),
            "bypass": sum(x["status"] == "BYPASS" for x in results),
            "p1_bypass": sum(x["status"] == "BYPASS" and x["severity"] == "P1" for x in results),
            "p2_bypass": sum(x["status"] == "BYPASS" and x["severity"] == "P2" for x in results),
        },
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 1 if payload["summary"]["bypass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
