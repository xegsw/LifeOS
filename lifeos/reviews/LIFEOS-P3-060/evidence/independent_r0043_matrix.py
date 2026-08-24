#!/usr/bin/env python3
"""P3-060 standalone synthetic SQLite R-0043 adjacency matrix.

This file intentionally imports no P3-039/P3-058 material and uses no historical
attack scenario/result table. It applies the current candidate SQL to new databases.
"""
import argparse
import json
import sqlite3
import tempfile
from pathlib import Path

LIFEOS = Path(__file__).resolve().parents[3]
SQL = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"

def execute_rejected(conn, sql, params=()):
    try:
        conn.execute(sql, params)
    except sqlite3.DatabaseError as exc:
        return {"rejected": True, "error": str(exc)}
    return {"rejected": False, "error": None}

def row(conn, subject_type="artifact", subject_id="a1"):
    return conn.execute(
        "SELECT subject_type,subject_id,generation,command_id,reason_code,blocked_at_ms,cleanup_status,updated_at_ms "
        "FROM tombstone WHERE subject_type=? AND subject_id=?", (subject_type, subject_id)
    ).fetchone()

def run_case(storage, fk, recursive):
    db_file = None
    if storage == "file":
        handle = tempfile.NamedTemporaryFile(prefix="lifeos-p3-060-", suffix=".db", delete=False)
        db_file = handle.name
        handle.close()
        conn = sqlite3.connect(db_file)
    else:
        conn = sqlite3.connect(":memory:")
    conn.execute(f"PRAGMA foreign_keys={'ON' if fk else 'OFF'}")
    conn.execute(f"PRAGMA recursive_triggers={'ON' if recursive else 'OFF'}")
    conn.executescript(SQL.read_text(encoding="utf-8"))
    now = 1786550400000
    outcomes = []

    # Tombstone generation downgrade; state must remain intact after rejection.
    conn.execute("INSERT INTO tombstone VALUES ('artifact','a1',5,'cmd-5','cleanup',?,'accepted',?)", (now, now))
    before = row(conn)
    denial = execute_rejected(conn, "UPDATE tombstone SET generation=4 WHERE subject_type='artifact' AND subject_id='a1'")
    outcomes.append({"id": "generation_downgrade", "pass": denial["rejected"] and row(conn) == before, "detail": denial})

    # DELETE/reinsert: deletion must fail; original identity then blocks reinsert.
    denial = execute_rejected(conn, "DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='a1'")
    reinsert = execute_rejected(conn, "INSERT INTO tombstone VALUES ('artifact','a1',6,'cmd-6','cleanup',?,'accepted',?)", (now + 1, now + 1))
    outcomes.append({"id": "delete_reinsert", "pass": denial["rejected"] and reinsert["rejected"] and row(conn) == before, "detail": {"delete": denial, "reinsert": reinsert}})

    # A normal tombstone cannot be rebound into the Authorization namespace, even
    # if the attempted row also forges generation, command, reason and timestamps.
    denial = execute_rejected(conn, "UPDATE tombstone SET subject_type='authorization',subject_id='auth-forged',generation=99,command_id='forged',reason_code='forged',blocked_at_ms=0,updated_at_ms=0 WHERE subject_type='artifact' AND subject_id='a1'")
    outcomes.append({"id": "ordinary_to_authorization_rebind_with_forged_envelope", "pass": denial["rejected"] and row(conn) == before, "detail": denial})

    # A direct forged Authorization Tombstone has no matching terminal parent.
    denial = execute_rejected(conn, "INSERT INTO tombstone VALUES ('authorization','auth-forged',99,'forged','forged',0,'accepted',0)")
    outcomes.append({"id": "forged_authorization_insert", "pass": denial["rejected"], "detail": denial})

    # The candidate deliberately keeps a legal monotonic generic Tombstone path.
    conn.execute("UPDATE tombstone SET generation=6,command_id='cmd-6',reason_code='retry',blocked_at_ms=?,updated_at_ms=? WHERE subject_type='artifact' AND subject_id='a1'", (now + 2, now + 2))
    successor = row(conn)
    outcomes.append({"id": "legal_monotonic_successor", "pass": successor[2] == 6 and successor[3:6] == ('cmd-6','retry',now + 2), "detail": {"row": successor}})

    # A failed write inside a savepoint must be reversible and must not poison a
    # subsequent legal update in the enclosing transaction.
    conn.commit()
    conn.execute("BEGIN")
    conn.execute("SAVEPOINT p3_060_guard")
    denial = execute_rejected(conn, "UPDATE tombstone SET generation=1 WHERE subject_type='artifact' AND subject_id='a1'")
    conn.execute("ROLLBACK TO p3_060_guard")
    conn.execute("RELEASE p3_060_guard")
    conn.execute("UPDATE tombstone SET generation=7,command_id='cmd-7',reason_code='savepoint',blocked_at_ms=?,updated_at_ms=? WHERE subject_type='artifact' AND subject_id='a1'", (now + 3, now + 3))
    conn.commit()
    outcomes.append({"id": "savepoint_rollback_then_legal_write", "pass": denial["rejected"] and row(conn)[2] == 7, "detail": denial})
    conn.close()
    return {"storage": storage, "foreign_keys": fk, "recursive_triggers": recursive, "cases": outcomes, "pass": all(x["pass"] for x in outcomes), "db_file": db_file}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-json", type=Path, required=True)
    args = parser.parse_args()
    matrix = [run_case(storage, fk, recursive) for storage in ("memory", "file") for fk in (False, True) for recursive in (False, True)]
    flat = [item for cell in matrix for item in cell["cases"]]
    payload = {"task_id": "LIFEOS-P3-060", "scope": "standalone synthetic SQLite R-0043 adjacency matrix", "candidate_sql": str(SQL), "matrix": matrix, "summary": {"PASS": sum(x["pass"] for x in flat), "FAIL": sum(not x["pass"] for x in flat), "Unknown": 0, "Not Implemented": 0, "total": len(flat)}}
    args.results_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if payload["summary"]["FAIL"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
