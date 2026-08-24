#!/usr/bin/env python3
"""Independent P3-049 Tombstone/Authorization counterexample suite.

This script deliberately does not import or call P3-048/P3-047 runners.
It uses only fresh synthetic SQLite databases created from the read-only
candidate schema. Run it from an isolated workspace copy.
"""

import hashlib
import json
import platform
import sqlite3
import sys
from pathlib import Path


EVIDENCE = Path(__file__).resolve().parent
LIFEOS = EVIDENCE.parents[2]
SCHEMA = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
WORK = EVIDENCE / "work"
NOW = 1786550400000
STATES = (
    "accepted",
    "active_blocked",
    "cleanup_pending",
    "cleanup_failed",
    "vendor_limited",
    "cleaned",
)
CONFIGS = [
    (backend, fk, recursive)
    for backend in ("memory", "file")
    for fk in (True, False)
    for recursive in (True, False)
]
RESULTS = []
SNAPSHOTS = []
HEALTH = []
DATABASES = []


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def config_name(backend, fk, recursive):
    return "%s-fk_%s-rec_%s" % (
        backend,
        "on" if fk else "off",
        "on" if recursive else "off",
    )


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value)


def fresh(config, case):
    backend, fk, recursive = config
    if backend == "memory":
        db_path = ":memory:"
    else:
        db_path = str(WORK / (safe_name(case) + ".db"))
        Path(db_path).unlink(missing_ok=True)
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if recursive else "OFF"))
    assert bool(conn.execute("PRAGMA foreign_keys").fetchone()[0]) == fk
    assert bool(conn.execute("PRAGMA recursive_triggers").fetchone()[0]) == recursive
    DATABASES.append(db_path)
    return conn


def rows(conn, table):
    return [dict(row) for row in conn.execute("SELECT * FROM %s ORDER BY rowid" % table)]


def security_snapshot(conn):
    tables = (
        "authorization",
        "authorization_scope",
        "authorization_action",
        "authorization_policy",
        "authorization_lifecycle_command",
        "audit_entry",
        "outbox_job",
        "submission",
        "tombstone",
    )
    return {table: rows(conn, table) for table in tables}


def health(conn, case, fk):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
    passed = integrity == "ok" and quick == "ok" and not foreign
    HEALTH.append(
        {
            "case": case,
            "foreign_keys_enabled": fk,
            "integrity_check": integrity,
            "quick_check": quick,
            "foreign_key_check": foreign,
            "passed": passed,
        }
    )
    return passed


def record(case_id, category, config, status, detail, severity="P2", **extra):
    item = {
        "id": case_id,
        "category": category,
        "severity": severity,
        "config": config_name(*config),
        "status": status,
        "detail": detail,
    }
    item.update(extra)
    RESULTS.append(item)


def reject(conn, sql, params=(), expected=None):
    try:
        conn.execute(sql, params)
    except sqlite3.DatabaseError as exc:
        message = str(exc)
        if expected and expected not in message:
            raise AssertionError("unexpected rejection: %s" % message)
        return message
    raise AssertionError("statement unexpectedly succeeded")


def insert_project(conn):
    conn.execute(
        "INSERT OR IGNORE INTO project VALUES ('p1','Synthetic','review','active',1,?,?,?)",
        (NOW, NOW, NOW),
    )


def create_terminal_authorization(conn, aid):
    insert_project(conn)
    logical = "logical:" + aid
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            aid,
            logical,
            "actor:user",
            "local",
            "review",
            "device",
            "proposed",
            1,
            1,
            NOW,
            "indefinite",
            None,
            None,
            "policy@1",
            None,
            NOW,
            NOW,
        ),
    )
    conn.execute(
        "INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        (aid + ":scope", aid, "allow", "p1", None, None),
    )
    conn.execute(
        "INSERT INTO authorization_action VALUES (?,?,?)",
        (aid + ":action", aid, "read"),
    )
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (aid,))
    idem = "idem:%s:2:revoked" % aid
    request_hash = canonical_hash("independent-retire:%s:2:revoked" % aid)
    conn.execute(
        "INSERT INTO submission VALUES ('destruct@1',?,?,?,?,NULL,?)",
        (idem, request_hash, "revoke_authorization", aid, NOW),
    )
    conn.execute(
        """INSERT INTO authorization_lifecycle_command(
             id,idempotency_key,authorization_id,expected_generation,target_status,
             scoped_actor_claim,canonical_request_hash,requested_at_ms
           ) VALUES (?,?,?,?,?,?,?,?)""",
        ("cmd:" + aid, idem, aid, 1, "revoked", "actor:user", request_hash, NOW),
    )
    row = conn.execute(
        "SELECT status,generation FROM authorization WHERE id=?", (aid,)
    ).fetchone()
    assert tuple(row) == ("revoked", 2)


def add_authorization_tombstone(conn, aid, target="accepted"):
    create_terminal_authorization(conn, aid)
    correlation = "authorization-cleanup:%s:2" % aid
    conn.execute(
        "INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
        (
            "audit:" + correlation,
            "authorization.cleanup",
            "actor:user",
            aid,
            1,
            "redacted_by_user",
            NOW,
            correlation,
        ),
    )
    conn.execute(
        "INSERT INTO tombstone VALUES ('authorization',?,?,?,'user_cleanup',?,'accepted',?)",
        (aid, 2, "cleanup:" + aid, NOW, NOW),
    )
    path = {
        "accepted": (),
        "active_blocked": ("active_blocked",),
        "cleanup_pending": ("active_blocked", "cleanup_pending"),
        "cleanup_failed": ("active_blocked", "cleanup_pending", "cleanup_failed"),
        "vendor_limited": ("active_blocked", "cleanup_pending", "vendor_limited"),
        "cleaned": ("active_blocked", "cleanup_pending", "cleaned"),
    }[target]
    for state in path:
        if state == "cleaned":
            for table in (
                "authorization_scope",
                "authorization_action",
                "authorization_policy",
            ):
                conn.execute("DELETE FROM %s WHERE authorization_id=?" % table, (aid,))
        conn.execute(
            "UPDATE tombstone SET cleanup_status=?,updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id=?",
            (state, aid),
        )


def add_generic(conn, sid, state="accepted"):
    conn.execute(
        "INSERT INTO tombstone VALUES ('artifact',?,1,?,'generic',?,'accepted',?)",
        (sid, "generic:" + sid, NOW, NOW),
    )
    if state != "accepted":
        conn.execute(
            "UPDATE tombstone SET cleanup_status=?,updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='artifact' AND subject_id=?",
            (state, sid),
        )


def rejected_unchanged(conn, sql, params=(), expected=None):
    before = security_snapshot(conn)
    error = reject(conn, sql, params, expected)
    after = security_snapshot(conn)
    if before != after:
        raise AssertionError("failed statement left a security-table half-state")
    return error, before, after


def close_case(conn, config, case, passed, detail):
    backend, fk, _ = config
    if backend == "file" and not health(conn, case, fk):
        passed = False
        detail = "file integrity/quick/FK check failed"
    conn.close()
    return passed, detail


def run_direction_matrix(config):
    attacks = (
        (
            "generic_to_authorization",
            "UPDATE tombstone SET subject_type='authorization',subject_id='authA',generation=2 "
            "WHERE subject_type='artifact' AND subject_id='generic'",
        ),
        (
            "authorization_to_generic",
            "UPDATE tombstone SET subject_type='artifact',subject_id='escaped' "
            "WHERE subject_type='authorization' AND subject_id='authA'",
        ),
        (
            "authorization_a_to_b",
            "UPDATE tombstone SET subject_id='authB' "
            "WHERE subject_type='authorization' AND subject_id='authA'",
        ),
    )
    for attack, sql in attacks:
        case = "direction/%s/%s" % (attack, config_name(*config))
        conn = fresh(config, case)
        try:
            if attack == "generic_to_authorization":
                create_terminal_authorization(conn, "authA")
                add_generic(conn, "generic")
            elif attack == "authorization_to_generic":
                add_authorization_tombstone(conn, "authA")
            else:
                add_authorization_tombstone(conn, "authA")
                create_terminal_authorization(conn, "authB")
            error, before, after = rejected_unchanged(
                conn, sql, expected="authorization_tombstone_control_envelope_immutable"
            )
            passed = True
            detail = "%s rejected by target guard" % attack
            SNAPSHOTS.append(
                {"case": case, "error": error, "before": before, "after": after}
            )
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        passed, detail = close_case(conn, config, case, passed, detail)
        record("IND-DIRECTION", "old_new", config, "PASS" if passed else "BYPASS", detail, attack=attack)


def run_field_state_matrix(config):
    assignments = {
        "subject_type": "subject_type='artifact'",
        "subject_id": "subject_id='ghost'",
        "generation": "generation=generation+1",
        "command_id": "command_id='forged'",
        "reason_code": "reason_code='forged'",
        "blocked_at_ms": "blocked_at_ms=blocked_at_ms+1",
    }
    next_state = {
        "accepted": "active_blocked",
        "active_blocked": "cleanup_pending",
        "cleanup_pending": "cleanup_failed",
        "cleanup_failed": "cleanup_pending",
        "vendor_limited": "cleanup_pending",
        "cleaned": "cleaned",
    }
    for index, state in enumerate(STATES):
        for field, assignment in assignments.items():
            case = "field/%s/%s/%s" % (state, field, config_name(*config))
            conn = fresh(config, case)
            aid = "auth-%s-%s" % (index, field)
            try:
                add_authorization_tombstone(conn, aid, state)
                error, before, after = rejected_unchanged(
                    conn,
                    "UPDATE tombstone SET %s WHERE subject_type='authorization' AND subject_id=?" % assignment,
                    (aid,),
                    "authorization_tombstone_control_envelope_immutable",
                )
                passed, detail = True, "%s immutable in %s" % (field, state)
                if field == "subject_type":
                    SNAPSHOTS.append(
                        {"case": case, "error": error, "before": before, "after": after}
                    )
            except Exception as exc:
                passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
            passed, detail = close_case(conn, config, case, passed, detail)
            record(
                "IND-FIELD",
                "field_state",
                config,
                "PASS" if passed else "BYPASS",
                detail,
                cleanup_status=state,
                field=field,
            )

        case = "combo/%s/%s" % (state, config_name(*config))
        conn = fresh(config, case)
        aid = "combo-%s" % index
        try:
            add_authorization_tombstone(conn, aid, state)
            target = next_state[state]
            if state == "cleaned":
                sql = (
                    "UPDATE tombstone SET command_id='forged',cleanup_status=cleanup_status,"
                    "updated_at_ms=updated_at_ms WHERE subject_type='authorization' AND subject_id=?"
                )
            else:
                sql = (
                    "UPDATE tombstone SET command_id='forged',cleanup_status=?,"
                    "updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?"
                )
            params = (aid,) if state == "cleaned" else (target, aid)
            error, before, after = rejected_unchanged(
                conn, sql, params, "authorization_tombstone_control_envelope_immutable"
            )
            passed, detail = True, "field/status/time compound rejected"
            SNAPSHOTS.append(
                {"case": case, "error": error, "before": before, "after": after}
            )
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        passed, detail = close_case(conn, config, case, passed, detail)
        record(
            "IND-COMBO",
            "status_time_combo",
            config,
            "PASS" if passed else "BYPASS",
            detail,
            cleanup_status=state,
        )


def run_nullability_matrix(config):
    for field in (
        "subject_type",
        "subject_id",
        "generation",
        "command_id",
        "reason_code",
        "blocked_at_ms",
    ):
        case = "null/%s/%s" % (field, config_name(*config))
        conn = fresh(config, case)
        try:
            add_authorization_tombstone(conn, "authN")
            error, _, _ = rejected_unchanged(
                conn,
                "UPDATE tombstone SET %s=NULL WHERE subject_type='authorization' AND subject_id='authN'" % field,
            )
            passed, detail = True, "NULL rejected: %s" % error
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        passed, detail = close_case(conn, config, case, passed, detail)
        record(
            "IND-NULL",
            "nullability",
            config,
            "PASS" if passed else "BYPASS",
            detail,
            field=field,
        )


def run_replace_matrix(config):
    cases = (
        (
            "insert_or_replace_authorization",
            "INSERT OR REPLACE INTO tombstone VALUES ('authorization','authA',2,'forged','forged',?,'accepted',?)",
            (NOW, NOW),
            "tombstone_reinsert_forbidden",
        ),
        (
            "plain_conflict_authorization",
            "INSERT INTO tombstone VALUES ('authorization','authA',2,'forged','forged',?,'accepted',?)",
            (NOW, NOW),
            "tombstone_reinsert_forbidden",
        ),
        (
            "upsert_authorization",
            "INSERT INTO tombstone VALUES ('authorization','authA',2,'forged','forged',?,'accepted',?) "
            "ON CONFLICT(subject_type,subject_id) DO UPDATE SET command_id=excluded.command_id",
            (NOW, NOW),
            "tombstone_reinsert_forbidden",
        ),
        (
            "upsert_generic_to_authorization",
            "INSERT INTO tombstone VALUES ('artifact','generic',1,'new','new',?,'accepted',?) "
            "ON CONFLICT(subject_type,subject_id) DO UPDATE SET subject_type='authorization',"
            "subject_id='authA',generation=2,command_id='forged'",
            (NOW, NOW),
            "tombstone_reinsert_forbidden",
        ),
        (
            "update_or_replace",
            "UPDATE OR REPLACE tombstone SET subject_type='authorization',subject_id='authA',generation=2 "
            "WHERE subject_type='artifact' AND subject_id='generic'",
            (),
            "authorization_tombstone_control_envelope_immutable",
        ),
        (
            "delete_authorization",
            "DELETE FROM tombstone WHERE subject_type='authorization' AND subject_id='authA'",
            (),
            "tombstone_delete_forbidden",
        ),
    )
    for attack, sql, params, expected in cases:
        case = "replace/%s/%s" % (attack, config_name(*config))
        conn = fresh(config, case)
        try:
            add_authorization_tombstone(conn, "authA")
            add_generic(conn, "generic")
            error, before, after = rejected_unchanged(conn, sql, params, expected)
            passed, detail = True, "%s rejected" % attack
            SNAPSHOTS.append(
                {"case": case, "error": error, "before": before, "after": after}
            )
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        passed, detail = close_case(conn, config, case, passed, detail)
        record(
            "IND-REPLACE",
            "replace_upsert_delete",
            config,
            "PASS" if passed else "BYPASS",
            detail,
            attack=attack,
        )

    case = "replace/delete_reinsert/%s" % config_name(*config)
    conn = fresh(config, case)
    try:
        add_authorization_tombstone(conn, "authA")
        before = security_snapshot(conn)
        conn.execute("BEGIN IMMEDIATE")
        error = reject(
            conn,
            "DELETE FROM tombstone WHERE subject_type='authorization' AND subject_id='authA'",
            expected="tombstone_delete_forbidden",
        )
        conn.rollback()
        after = security_snapshot(conn)
        if before != after:
            raise AssertionError("DELETE/reinsert transaction changed security state")
        passed, detail = True, "DELETE rejected before reinsert: %s" % error
        SNAPSHOTS.append({"case": case, "before": before, "after": after})
    except Exception as exc:
        if conn.in_transaction:
            conn.rollback()
        passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
    passed, detail = close_case(conn, config, case, passed, detail)
    record(
        "IND-DELETE-REINSERT",
        "replace_upsert_delete",
        config,
        "PASS" if passed else "BYPASS",
        detail,
    )


def run_multirow_and_transaction(config):
    case = "atomic/multirow/%s" % config_name(*config)
    conn = fresh(config, case)
    try:
        add_authorization_tombstone(conn, "authA")
        add_generic(conn, "generic")
        sql = """UPDATE tombstone SET
          subject_type=CASE WHEN subject_type='artifact' THEN 'authorization' ELSE subject_type END,
          subject_id=CASE WHEN subject_type='artifact' THEN 'authA' ELSE subject_id END,
          generation=CASE WHEN subject_type='artifact' THEN 2 ELSE generation END,
          cleanup_status=CASE WHEN subject_type='artifact' THEN 'active_blocked' ELSE cleanup_status END,
          updated_at_ms=updated_at_ms+1
          WHERE (subject_type='artifact' AND subject_id='generic')
             OR (subject_type='authorization' AND subject_id='authA')"""
        # Cross-trigger order is not a contract. This compound statement may be
        # rejected first by the updated-time guard; the direct field matrix
        # separately proves that the target envelope guard itself is present.
        error, before, after = rejected_unchanged(conn, sql)
        passed = True
        detail = "multi-row statement rolled back atomically; first guard=%s" % error
        SNAPSHOTS.append(
            {"case": case, "error": error, "before": before, "after": after}
        )
    except Exception as exc:
        passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
    passed, detail = close_case(conn, config, case, passed, detail)
    record("IND-MULTIROW", "atomicity", config, "PASS" if passed else "BYPASS", detail)

    case = "atomic/explicit_rollback/%s" % config_name(*config)
    conn = fresh(config, case)
    try:
        add_authorization_tombstone(conn, "authA")
        add_generic(conn, "generic")
        baseline = security_snapshot(conn)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE tombstone SET command_id='generic-tx',updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='artifact' AND subject_id='generic'"
        )
        error = reject(
            conn,
            "UPDATE tombstone SET command_id='forged' "
            "WHERE subject_type='authorization' AND subject_id='authA'",
            expected="authorization_tombstone_control_envelope_immutable",
        )
        mid = security_snapshot(conn)
        if mid == baseline:
            raise AssertionError("transaction probe did not observe the prior legal statement")
        auth_before = baseline["tombstone"][0]
        auth_mid = [r for r in mid["tombstone"] if r["subject_type"] == "authorization"][0]
        if auth_mid != auth_before:
            raise AssertionError("rejected statement changed Authorization tombstone")
        conn.rollback()
        after = security_snapshot(conn)
        if after != baseline:
            raise AssertionError("explicit rollback did not restore entire transaction")
        passed = True
        detail = "ABORT kept prior statement pending; explicit rollback restored baseline"
        SNAPSHOTS.append(
            {"case": case, "error": error, "before": baseline, "mid": mid, "after": after}
        )
    except Exception as exc:
        if conn.in_transaction:
            conn.rollback()
        passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
    passed, detail = close_case(conn, config, case, passed, detail)
    record("IND-TRANSACTION", "atomicity", config, "PASS" if passed else "BYPASS", detail)


def run_legal_paths(config):
    case = "legal/%s" % config_name(*config)
    conn = fresh(config, case)
    checks = []
    try:
        add_generic(conn, "generic")
        changed = conn.execute(
            "UPDATE tombstone SET subject_id='generic-v2',generation=2,command_id='generic-v2',"
            "reason_code='retry',blocked_at_ms=blocked_at_ms+1,cleanup_status='active_blocked',"
            "updated_at_ms=updated_at_ms+1 WHERE subject_type='artifact' AND subject_id='generic'"
        ).rowcount
        checks.append(("generic_existing_semantics", changed == 1))

        add_authorization_tombstone(conn, "authA", "accepted")
        conn.execute(
            "UPDATE tombstone SET subject_type=subject_type,subject_id=subject_id,generation=generation,"
            "command_id=command_id,reason_code=reason_code,blocked_at_ms=blocked_at_ms "
            "WHERE subject_type='authorization' AND subject_id='authA'"
        )
        checks.append(("authorization_noop", True))

        legal_steps = (
            "active_blocked",
            "cleanup_pending",
            "cleanup_failed",
            "cleanup_pending",
            "vendor_limited",
            "cleanup_pending",
        )
        trace = ["accepted"]
        for state in legal_steps:
            conn.execute(
                "UPDATE tombstone SET cleanup_status=?,updated_at_ms=updated_at_ms+1 "
                "WHERE subject_type='authorization' AND subject_id='authA'",
                (state,),
            )
            trace.append(state)
        for table in (
            "authorization_scope",
            "authorization_action",
            "authorization_policy",
        ):
            conn.execute("DELETE FROM %s WHERE authorization_id='authA'" % table)
        conn.execute(
            "UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id='authA'"
        )
        trace.append("cleaned")
        final = conn.execute(
            "SELECT cleanup_status FROM tombstone WHERE subject_type='authorization' AND subject_id='authA'"
        ).fetchone()[0]
        checks.append(("authorization_cleanup_trace", final == "cleaned"))
        passed = all(ok for _, ok in checks)
        detail = "legal generic/no-op/cleanup paths preserved"
        SNAPSHOTS.append(
            {"case": case, "checks": checks, "trace": trace, "final": security_snapshot(conn)}
        )
    except Exception as exc:
        passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
    passed, detail = close_case(conn, config, case, passed, detail)
    record("IND-LEGAL", "legal", config, "PASS" if passed else "FAIL", detail, checks=checks)


def static_analysis():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    triggers = [
        dict(row)
        for row in conn.execute(
            "SELECT rowid,name,tbl_name,sql FROM sqlite_master "
            "WHERE type='trigger' AND (tbl_name='tombstone' OR name LIKE 'authorization_%') "
            "ORDER BY rowid"
        )
    ]
    columns = [dict(row) for row in conn.execute("PRAGMA table_info(tombstone)")]
    conn.close()
    target = next(
        row for row in triggers if row["name"] == "authorization_tombstone_control_envelope_immutable"
    )
    sql = target["sql"]
    required = (
        "subject_type",
        "subject_id",
        "generation",
        "command_id",
        "reason_code",
        "blocked_at_ms",
    )
    return {
        "candidate_sha256": sha256(SCHEMA),
        "target_trigger_present": True,
        "target_mentions_old_authorization": "OLD.subject_type = 'authorization'" in sql,
        "target_mentions_new_authorization": "NEW.subject_type = 'authorization'" in sql,
        "update_of_has_all_six": all(field in sql.split("ON tombstone", 1)[0] for field in required),
        "nullability": {row["name"]: bool(row["notnull"]) for row in columns},
        "triggers_in_sqlite_master_creation_order": triggers,
        "note": "SQLite does not promise cross-trigger execution order; direct field attacks isolate the target guard.",
    }


def summary():
    statuses = ("PASS", "FAIL", "BYPASS", "NOT_IMPLEMENTED", "UNKNOWN")
    total = {status: sum(row["status"] == status for row in RESULTS) for status in statuses}
    categories = {}
    for category in sorted({row["category"] for row in RESULTS}):
        selected = [row for row in RESULTS if row["category"] == category]
        categories[category] = {
            status: sum(row["status"] == status for row in selected) for status in statuses
        }
        categories[category]["instances"] = len(selected)
    return {"total": total, "categories": categories}


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    for config in CONFIGS:
        run_direction_matrix(config)
        run_field_state_matrix(config)
        run_nullability_matrix(config)
        run_replace_matrix(config)
        run_multirow_and_transaction(config)
        run_legal_paths(config)

    static = static_analysis()
    stats = summary()
    payload = {
        "task_id": "LIFEOS-P3-049",
        "scope": "isolated synthetic SQLite independent counterexamples",
        "independence": "does not import/call P3-048 or P3-047 runners",
        "summary": stats,
        "results": RESULTS,
    }
    (EVIDENCE / "counterexample_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "atomic_snapshots.json").write_text(
        json.dumps(SNAPSHOTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "integrity_and_fk.json").write_text(
        json.dumps(
            {"all_passed": all(row["passed"] for row in HEALTH), "results": HEALTH},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (EVIDENCE / "static_analysis.json").write_text(
        json.dumps(static, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "environment.json").write_text(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "sqlite": sqlite3.sqlite_version,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "candidate_schema": str(SCHEMA),
                "candidate_sha256": sha256(SCHEMA),
                "configurations": [config_name(*config) for config in CONFIGS],
                "database_paths": DATABASES,
                "network_used": False,
                "real_capabilities_used": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(stats, sort_keys=True))
    bad = any(stats["total"][key] for key in ("FAIL", "BYPASS", "NOT_IMPLEMENTED", "UNKNOWN"))
    bad = bad or not all(row["passed"] for row in HEALTH)
    bad = bad or not all(
        static[key]
        for key in (
            "target_trigger_present",
            "target_mentions_old_authorization",
            "target_mentions_new_authorization",
            "update_of_has_all_six",
        )
    )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
