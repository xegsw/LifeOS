#!/usr/bin/env python3
"""PM counterexample for LIFEOS-P3-047 tombstone identity rebind."""

import json
import sqlite3
import tempfile
from pathlib import Path


LIFEOS = Path(__file__).resolve().parents[3]
SCHEMA = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
OUTPUT = Path(__file__).resolve().parent / "counterexample_results.json"
NOW = 1786550400000
CONFIGS = [
    (backend, foreign_keys, recursive_triggers)
    for backend in ("memory", "file")
    for foreign_keys in (True, False)
    for recursive_triggers in (True, False)
]


def request_hash(value):
    import hashlib

    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def fresh(path, foreign_keys, recursive_triggers):
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if foreign_keys else "OFF"))
    conn.execute(
        "PRAGMA recursive_triggers=%s" % ("ON" if recursive_triggers else "OFF")
    )
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
    canonical = request_hash("authorization-lifecycle:auth1:2:revoked")
    conn.execute(
        "INSERT INTO submission VALUES "
        "('destruct@1','idem:auth1:2:revoked',?,'revoke_authorization','auth1',NULL,?)",
        (canonical, NOW),
    )
    conn.execute(
        """INSERT INTO authorization_lifecycle_command(
             id,idempotency_key,authorization_id,expected_generation,target_status,
             scoped_actor_claim,canonical_request_hash,requested_at_ms
           ) VALUES ('cmd:auth1:2:revoked','idem:auth1:2:revoked','auth1',1,
                     'revoked','actor:user',?,?)""",
        (canonical, NOW),
    )
    return conn


def run_case(backend, foreign_keys, recursive_triggers, temp_dir):
    label = "%s-fk_%s-rec_%s" % (
        backend,
        "on" if foreign_keys else "off",
        "on" if recursive_triggers else "off",
    )
    path = ":memory:" if backend == "memory" else str(Path(temp_dir) / (label + ".db"))
    conn = fresh(path, foreign_keys, recursive_triggers)
    conn.execute(
        """INSERT INTO tombstone(
             subject_type,subject_id,generation,command_id,reason_code,
             blocked_at_ms,cleanup_status,updated_at_ms
           ) VALUES ('artifact','placeholder',1,'seed-command','seed-reason',?,
                     'accepted',?)""",
        (NOW, NOW),
    )
    before = list(conn.execute("SELECT * FROM tombstone").fetchone())
    rejected = False
    error = None
    try:
        conn.execute(
            """UPDATE tombstone
               SET subject_type='authorization', subject_id='auth1', generation=2,
                   command_id='forged-cleanup', reason_code='user_cleanup',
                   blocked_at_ms=?
               WHERE subject_type='artifact' AND subject_id='placeholder'""",
            (NOW,),
        )
    except sqlite3.DatabaseError as exc:
        rejected = True
        error = str(exc)
    after_row = conn.execute("SELECT * FROM tombstone").fetchone()
    after = list(after_row) if after_row is not None else None
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    foreign = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
    conn.close()
    return {
        "id": "PM-CE-06",
        "severity": "P2",
        "config": label,
        "expected": "A tombstone identity and control envelope are immutable from INSERT",
        "actual": (
            "Generic tombstone was rebound into an Authorization tombstone"
            if not rejected
            else "Rebind was rejected"
        ),
        "status": "PASS" if rejected else "BYPASS",
        "error": error,
        "before": before,
        "after": after,
        "integrity_check": integrity,
        "foreign_key_check": foreign,
    }


def main():
    with tempfile.TemporaryDirectory(prefix="lifeos-p3047-pm-") as temp_dir:
        results = [run_case(*config, temp_dir) for config in CONFIGS]
    payload = {
        "task_id": "LIFEOS-P3-047",
        "scope": "synthetic SQLite PM counterexample; no real data or capability",
        "summary": {
            "pass": sum(row["status"] == "PASS" for row in results),
            "bypass": sum(row["status"] == "BYPASS" for row in results),
            "p2_bypass": sum(
                row["status"] == "BYPASS" and row["severity"] == "P2"
                for row in results
            ),
        },
        "results": results,
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload["summary"], sort_keys=True))
    return 1 if payload["summary"]["bypass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
