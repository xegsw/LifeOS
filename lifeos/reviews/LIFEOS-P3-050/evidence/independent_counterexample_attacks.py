#!/usr/bin/env python3
"""P3-050 independently authored synthetic SQLite Tombstone review matrix.

This file intentionally imports only the Python standard library.  It neither
imports nor calls P3-048/P3-049 attack helpers, runners, or scenario tables.
"""

import argparse
import hashlib
import json
import platform
import sqlite3
import sys
import tempfile
from pathlib import Path


NOW = 1786550400000
STATES = ("accepted", "active_blocked", "cleanup_pending", "cleanup_failed", "vendor_limited", "cleaned")
FIELDS = ("subject_type", "subject_id", "generation", "command_id", "reason_code", "blocked_at_ms")
CONFIGS = [(backend, fk, recursive) for backend in ("memory", "file") for fk in (True, False) for recursive in (True, False)]


def sha(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def row_tuple(row):
    return tuple(row) if row is not None else None


def make_db(schema, backend, fk, recursive, work, label):
    path = ":memory:" if backend == "memory" else str(work / (label + ".db"))
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(schema)
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if recursive else "OFF"))
    conn.execute("INSERT INTO project VALUES ('p1','Synthetic','test','active',1,?,?,?)", (NOW, NOW, NOW))
    return conn, path


def add_authorization(conn, aid, logical):
    conn.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (aid, logical, "actor:user", "local", "test", "device", "proposed", 1, 1, NOW, "indefinite", None, None, "policy@1", None, NOW, NOW))
    conn.execute("INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)", (aid + ":scope", aid, "allow", "p1", None, None))
    conn.execute("INSERT INTO authorization_action VALUES (?,?,?)", (aid + ":action", aid, "read"))
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (aid,))


def retire(conn, aid):
    token = "authorization-lifecycle:%s:2:revoked" % aid
    idem = "idem:%s" % aid
    digest = sha(token)
    conn.execute("INSERT INTO submission VALUES ('destruct@1',?,?,?,?,NULL,?)", (idem, digest, "revoke_authorization", aid, NOW))
    conn.execute("INSERT INTO authorization_lifecycle_command(id,idempotency_key,authorization_id,expected_generation,target_status,scoped_actor_claim,canonical_request_hash,requested_at_ms) VALUES (?,?,?,?,?,?,?,?)", ("cmd:" + aid, idem, aid, 1, "revoked", "actor:user", digest, NOW))


def add_cleanup_audit(conn, aid):
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)", ("audit:cleanup:" + aid, "authorization.cleanup", "actor:user", aid, 1, "redacted_by_user", NOW, "authorization-cleanup:%s:2" % aid))


def advance(conn, aid, state):
    """Create an Authorization Tombstone in exactly the requested state."""
    add_authorization(conn, aid, "logical:" + aid)
    retire(conn, aid)
    add_cleanup_audit(conn, aid)
    conn.execute("INSERT INTO tombstone VALUES ('authorization',?,2,?,'user_cleanup',?,'accepted',?)", (aid, "cleanup:" + aid, NOW, NOW))
    if state == "accepted":
        return
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='authorization' AND subject_id=?", (aid,))
    if state == "active_blocked":
        return
    conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id=?", (aid,))
    if state == "cleanup_pending":
        return
    if state == "cleanup_failed":
        conn.execute("UPDATE tombstone SET cleanup_status='cleanup_failed' WHERE subject_type='authorization' AND subject_id=?", (aid,)); return
    if state == "vendor_limited":
        conn.execute("UPDATE tombstone SET cleanup_status='vendor_limited' WHERE subject_type='authorization' AND subject_id=?", (aid,)); return
    if state == "cleaned":
        for table in ("authorization_scope", "authorization_action", "authorization_policy"):
            conn.execute("DELETE FROM %s WHERE authorization_id=?" % table, (aid,))
        conn.execute("UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (aid,)); return
    raise ValueError(state)


def add_generic(conn, gid):
    conn.execute("INSERT INTO tombstone VALUES ('artifact',?,1,?,'seed',?,'accepted',?)", (gid, "generic:" + gid, NOW, NOW))


def protected_before(conn, aid):
    return row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='authorization' AND subject_id=?", (aid,)).fetchone())


def verify_db(conn, backend):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [tuple(x) for x in conn.execute("PRAGMA foreign_key_check")]
    return {"integrity_check": integrity, "quick_check": quick, "foreign_key_check": foreign} if backend == "file" else {}


def capture(case_id, severity, family, config, expected, action, snapshot, checks):
    error = None
    try:
        action()
    except sqlite3.DatabaseError as exc:
        error = str(exc)
    after = snapshot()
    rejected = error is not None
    preserved = after == checks["before"]
    status = "PASS" if rejected and preserved else "BYPASS"
    return {"id": case_id, "severity": severity, "family": family, "config": config, "expected": expected, "status": status, "error": error, "before": checks["before"], "after": after}


def run_config(schema, backend, fk, recursive, work):
    label = "%s-fk_%s-rec_%s" % (backend, "on" if fk else "off", "on" if recursive else "off")
    conn, path = make_db(schema, backend, fk, recursive, work, label)
    rows = []
    serial = 0

    def unique(prefix):
        nonlocal serial
        serial += 1
        return "%s-%03d" % (prefix, serial)

    # A. Directional rebinds, each with an independent fixture.
    for direction in ("GA", "AG", "AB"):
        if direction == "GA":
            target = unique("auth"); add_authorization(conn, target, "logical:" + target); retire(conn, target)
            gid = unique("generic"); add_generic(conn, gid)
            before = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
            rows.append(capture("DIR-GA", "P2", "direction", label, "generic cannot enter Authorization namespace", lambda gid=gid, target=target: conn.execute("UPDATE tombstone SET subject_type='authorization',subject_id=?,generation=2,command_id='forged',reason_code='forged',blocked_at_ms=? WHERE subject_type='artifact' AND subject_id=?", (target, NOW + 1, gid)), lambda gid=gid: row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone()), {"before": before}))
        elif direction == "AG":
            aid = unique("auth"); advance(conn, aid, "accepted"); before = protected_before(conn, aid)
            rows.append(capture("DIR-AG", "P2", "direction", label, "Authorization cannot leave namespace", lambda aid=aid: conn.execute("UPDATE tombstone SET subject_type='artifact',subject_id='escaped' WHERE subject_type='authorization' AND subject_id=?", (aid,)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
        else:
            left, right = unique("auth"), unique("auth"); advance(conn, left, "accepted"); add_authorization(conn, right, "logical:" + right); retire(conn, right); before = protected_before(conn, left)
            rows.append(capture("DIR-AB", "P2", "direction", label, "Authorization A cannot rebind to B", lambda left=left, right=right: conn.execute("UPDATE tombstone SET subject_id=? WHERE subject_type='authorization' AND subject_id=?", (right, left)), lambda left=left: protected_before(conn, left), {"before": before}))

    # B/C/D: independently exercise every control field and state.
    mutations = {
        "subject_type": "subject_type='artifact'", "subject_id": "subject_id='other'", "generation": "generation=generation+1",
        "command_id": "command_id='forged'", "reason_code": "reason_code='forged'", "blocked_at_ms": "blocked_at_ms=blocked_at_ms+1",
    }
    for state in STATES:
        for field, assignment in mutations.items():
            aid = unique("auth"); advance(conn, aid, state); before = protected_before(conn, aid)
            rows.append(capture("FIELD-%s-%s" % (state, field), "P2", "field", label, "protected field is immutable", lambda aid=aid, assignment=assignment: conn.execute("UPDATE tombstone SET %s WHERE subject_type='authorization' AND subject_id=?" % assignment, (aid,)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
        aid = unique("auth"); advance(conn, aid, state); before = protected_before(conn, aid)
        rows.append(capture("FIELD-%s-compound" % state, "P2", "field", label, "six-field envelope is atomic", lambda aid=aid: conn.execute("UPDATE tombstone SET subject_type='artifact',subject_id='other',generation=generation+1,command_id='forged',reason_code='forged',blocked_at_ms=blocked_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (aid,)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
        for field in FIELDS:
            aid = unique("auth"); advance(conn, aid, state); before = protected_before(conn, aid)
            rows.append(capture("NULL-%s-%s" % (state, field), "P2", "null", label, "NULL cannot evade protected comparison", lambda aid=aid, field=field: conn.execute("UPDATE tombstone SET %s=NULL WHERE subject_type='authorization' AND subject_id=?" % field, (aid,)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
        aid = unique("auth"); advance(conn, aid, state); before = protected_before(conn, aid)
        try:
            conn.execute("UPDATE tombstone SET subject_type=subject_type,subject_id=subject_id,generation=generation,command_id=command_id,reason_code=reason_code,blocked_at_ms=blocked_at_ms WHERE subject_type='authorization' AND subject_id=?", (aid,))
            after = protected_before(conn, aid); status, error = ("PASS", None) if after == before else ("FAIL", "no-op changed row")
        except sqlite3.DatabaseError as exc:
            after, status, error = protected_before(conn, aid), "FAIL", str(exc)
        rows.append({"id": "NOOP-%s" % state, "severity": "P2", "family": "legal_noop", "config": label, "expected": "protected no-op remains legal", "status": status, "error": error, "before": before, "after": after})
        aid = unique("auth"); advance(conn, aid, state); before = protected_before(conn, aid)
        target_status = {"accepted": "active_blocked", "active_blocked": "cleanup_pending", "cleanup_pending": "cleanup_failed", "cleanup_failed": "cleanup_pending", "vendor_limited": "cleanup_pending", "cleaned": "cleanup_pending"}[state]
        rows.append(capture("COMBO-%s" % state, "P2", "status_time_combo", label, "control + state/time update is one rejected statement", lambda aid=aid, target_status=target_status: conn.execute("UPDATE tombstone SET command_id='forged',cleanup_status=?,updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (target_status, aid)), lambda aid=aid: protected_before(conn, aid), {"before": before}))

    # E. Conflict/reconstruction neighbors.
    aid = unique("auth"); advance(conn, aid, "accepted"); before = protected_before(conn, aid)
    rows.append(capture("CONFLICT-upsert", "P2", "conflict", label, "UPSERT cannot rewrite a tombstone", lambda aid=aid: conn.execute("INSERT INTO tombstone VALUES ('authorization',?,2,'x','x',?,'accepted',?) ON CONFLICT(subject_type,subject_id) DO UPDATE SET command_id='forged'", (aid, NOW, NOW)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
    for mode, stmt in (("replace", "INSERT OR REPLACE INTO tombstone VALUES ('authorization',?,2,'x','x',?,'accepted',?)"), ("plain", "INSERT INTO tombstone VALUES ('authorization',?,2,'x','x',?,'accepted',?)")):
        aid = unique("auth"); advance(conn, aid, "accepted"); before = protected_before(conn, aid)
        rows.append(capture("CONFLICT-" + mode, "P2", "conflict", label, "conflicting insert cannot reconstruct tombstone", lambda aid=aid, stmt=stmt: conn.execute(stmt, (aid, NOW, NOW)), lambda aid=aid: protected_before(conn, aid), {"before": before}))
    target = unique("auth"); add_authorization(conn, target, "logical:" + target); retire(conn, target); gid = unique("generic"); add_generic(conn, gid); before = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    rows.append(capture("CONFLICT-update-or-replace", "P2", "conflict", label, "UPDATE OR REPLACE cannot rebind generic row", lambda gid=gid, target=target: conn.execute("UPDATE OR REPLACE tombstone SET subject_type='authorization',subject_id=?,generation=2 WHERE subject_type='artifact' AND subject_id=?", (target, gid)), lambda gid=gid: row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone()), {"before": before}))
    gid = unique("generic"); add_generic(conn, gid); before = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    error = None
    try:
        conn.execute("BEGIN IMMEDIATE"); conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)); conn.execute("INSERT INTO tombstone VALUES ('artifact',?,1,'x','x',?,'accepted',?)", (gid, NOW, NOW)); conn.execute("COMMIT")
    except sqlite3.DatabaseError as exc:
        error = str(exc); conn.execute("ROLLBACK")
    after = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    rows.append({"id": "CONFLICT-delete-reinsert", "severity": "P2", "family": "conflict", "config": label, "expected": "delete/reinsert transaction fails", "status": "PASS" if error and after == before else "BYPASS", "error": error, "before": before, "after": after})

    # F. Atomic multi-row statement and caller-owned rollback.
    target = unique("auth"); add_authorization(conn, target, "logical:" + target); retire(conn, target); good, bad = unique("generic"), unique("generic"); add_generic(conn, good); add_generic(conn, bad)
    before = [row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (x,)).fetchone()) for x in (good, bad)]
    error = None
    try:
        conn.execute("UPDATE tombstone SET generation=generation+1,subject_type=CASE WHEN subject_id=? THEN 'authorization' ELSE subject_type END,subject_id=CASE WHEN subject_id=? THEN ? ELSE subject_id END WHERE subject_type='artifact' AND subject_id IN (?,?)", (bad, bad, target, good, bad))
    except sqlite3.DatabaseError as exc:
        error = str(exc)
    after = [row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (x,)).fetchone()) for x in (good, bad)]
    rows.append({"id": "ATOMIC-multirow", "severity": "P2", "family": "atomicity", "config": label, "expected": "bad row aborts whole multi-row statement", "status": "PASS" if error and after == before else "BYPASS", "error": error, "before": before, "after": after})
    gid = unique("generic"); add_generic(conn, gid); target = unique("auth"); add_authorization(conn, target, "logical:" + target); retire(conn, target); original = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    error = None; conn.execute("BEGIN IMMEDIATE")
    conn.execute("UPDATE tombstone SET generation=2 WHERE subject_type='artifact' AND subject_id=?", (gid,))
    visible = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    try:
        conn.execute("UPDATE tombstone SET subject_type='authorization',subject_id=? WHERE subject_type='artifact' AND subject_id=?", (target, gid))
    except sqlite3.DatabaseError as exc:
        error = str(exc)
    conn.execute("ROLLBACK")
    rolled = row_tuple(conn.execute("SELECT * FROM tombstone WHERE subject_type='artifact' AND subject_id=?", (gid,)).fetchone())
    rows.append({"id": "ATOMIC-caller-rollback", "severity": "P3", "family": "transaction_boundary", "config": label, "expected": "failed statement is atomic and caller rollback restores prior statement", "status": "PASS" if error and visible != original and rolled == original else "FAIL", "error": error, "before": original, "after": {"after_failed_statement": visible, "after_rollback": rolled}})

    # G. Legal generic and cleanup retry/cleaned controls.
    gid = unique("generic"); add_generic(conn, gid)
    try:
        conn.execute("UPDATE tombstone SET generation=2,command_id='generic-v2',reason_code='retry',cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1 WHERE subject_type='artifact' AND subject_id=?", (gid,)); status, error = "PASS", None
    except sqlite3.DatabaseError as exc:
        status, error = "FAIL", str(exc)
    rows.append({"id": "LEGAL-generic", "severity": "P2", "family": "legal", "config": label, "expected": "generic behavior stays legal", "status": status, "error": error})
    for source in ("cleanup_failed", "vendor_limited"):
        aid = unique("auth"); advance(conn, aid, source)
        try:
            conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id=?", (aid,)); status, error = "PASS", None
        except sqlite3.DatabaseError as exc:
            status, error = "FAIL", str(exc)
        rows.append({"id": "LEGAL-retry-" + source, "severity": "P2", "family": "legal", "config": label, "expected": "authorized cleanup retry stays legal", "status": status, "error": error})
    aid = unique("auth"); advance(conn, aid, "cleaned")
    before = protected_before(conn, aid)
    try:
        conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_type='authorization' AND subject_id=?", (aid,)); status, error = "FAIL", None
    except sqlite3.DatabaseError as exc:
        status, error = "PASS", str(exc)
    rows.append({"id": "LEGAL-cleaned-terminal", "severity": "P2", "family": "legal", "config": label, "expected": "cleaned Tombstone remains terminal", "status": status if protected_before(conn, aid) == before else "BYPASS", "error": error, "before": before, "after": protected_before(conn, aid)})
    checks = verify_db(conn, backend)
    conn.close()
    return {"config": label, "path": path, "checks": checks, "results": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    schema = args.schema.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="lifeos-p3050-independent-") as temp:
        work = Path(temp)
        configs = [run_config(schema, *cfg, work) for cfg in CONFIGS]
    results = [row for group in configs for row in group["results"]]
    summary = {state.lower(): sum(row["status"] == state for row in results) for state in ("PASS", "BYPASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")}
    payload = {"task_id": "LIFEOS-P3-050", "scope": "independently authored synthetic SQLite matrix; no real capability", "script_origin": "P3-050 only; Python standard library; no P3-048/P3-049 attack imports", "schema": str(args.schema), "schema_sha256": hashlib.sha256(schema.encode()).hexdigest(), "summary": summary, "configurations": configs, "results": results}
    (args.output_dir / "independent_attack_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    env = {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version, "platform": platform.platform(), "configurations": [x["config"] for x in configs]}
    (args.output_dir / "independent_attack_environment.json").write_text(json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 1 if summary["bypass"] or summary["fail"] or summary["not_implemented"] or summary["unknown"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
