#!/usr/bin/env python3
"""LIFEOS-P3-048 synthetic Tombstone rebind remediation runner.

Only fresh in-memory and task-local file SQLite databases are used. P3-047,
P3-046 and every PM counterexample asset listed below are read-only baselines.
"""

import hashlib
import importlib.util
import json
import platform
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


TASK = Path(__file__).resolve().parents[1]
LIFEOS = TASK.parents[1]
ROOT = LIFEOS.parent
CANDIDATE = LIFEOS / "engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
P31_SHELL = LIFEOS / "engineering/LIFEOS-P3-031/scripts/run_validation.sh"
P31_TESTS = LIFEOS / "engineering/LIFEOS-P3-031/tests/run_contract_tests.py"
P47_RUNNER = LIFEOS / "engineering/LIFEOS-P3-047/scripts/run_validation.py"
SNAPSHOT = TASK / "input/001_candidate_schema.sql"
EVIDENCE = TASK / "evidence"
WORK = TASK / "work"
NOW = 1786550400000
CONFIGS = [
    (backend, foreign_keys, recursive_triggers)
    for backend in ("memory", "file")
    for foreign_keys in (True, False)
    for recursive_triggers in (True, False)
]

READ_ONLY = {
    "lifeos/tasks/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md": "28a7fee6c12fca7f2744ff71c209229ac5c416e911e27f37697585091f91fa02",
    "lifeos/deliverables/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md": "1e38966d41f2b8eb17ca47c145696490ab5e886cc1f072b5c059d492914a08b2",
    "lifeos/engineering/LIFEOS-P3-047/input/001_candidate_schema.sql": "7000ca397db8c737681bee1edff05caefcebffb1555f30697b61feb4a0df2854",
    "lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.py": "b5ff216ba75cea3cb88a22dcba821306ee772bcdfc792997db983e3bce959e22",
    "lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.sh": "385981b4b0637198ef142d3943732da9383f47d21d4eb060969044cb3702b800",
    "lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md": "8c59b572e56da026625d66398714cc496795e3b1e919820dc5d9b584ad9184a5",
    "lifeos/engineering/LIFEOS-P3-047/evidence/atomic_snapshots.json": "7b91ff714348e66dc51c5fcccbb67d1eb117e3c7285d236b4c355dcd5b0904dc",
    "lifeos/engineering/LIFEOS-P3-047/evidence/checks/integrity_and_fk.json": "268e4a743896af25bb70a2196b375378873bc0d0778d7d1c888b069e377b8018",
    "lifeos/engineering/LIFEOS-P3-047/evidence/environment.json": "57bca0510a649ec85f1970ea6f718ae910be3f88b4038192ac7fe7cd01ba2ef2",
    "lifeos/engineering/LIFEOS-P3-047/evidence/input/read_only_preservation.json": "b358b8fbc624bdace2658fedeaf7abd7329cfa2e9fb96896f03ef180bdf0ed27",
    "lifeos/engineering/LIFEOS-P3-047/evidence/input/source_hashes.json": "194af5ebfb41eab968cb4da910c59a7d80650797457d7ddc9c4c6e510657b62b",
    "lifeos/engineering/LIFEOS-P3-047/evidence/regressions/p3_031_test_results.json": "2e1c04a9fa721b01c44e75681d08c5df4a52690fa04de36ae678e5d3359a9261",
    "lifeos/engineering/LIFEOS-P3-047/evidence/regressions/p3_031_test_run.log": "4e5740af03f25ebdb85543c01ec69c984f0bd58faaf8e553b6f3a389a0dd48d1",
    "lifeos/engineering/LIFEOS-P3-047/evidence/state_machine_traces.json": "560076f8e66308570f78fece965eef564a6ca81bb3a4e5a8438997a06fa27e6d",
    "lifeos/engineering/LIFEOS-P3-047/evidence/test_results.json": "46cf1d4e38b9e673e6d9a998477d2ae10176dd355fc7b813476c30c6fd4bea7d",
    "lifeos/engineering/LIFEOS-P3-047/evidence/test_run.log": "f958b3c9afdf57fa03e9e3dbd2f04afa2328c2452e478649bb1160eba6b602f0",
    "lifeos/reviews/LIFEOS-P3-047_pm_review.md": "e1db24b3f0a2144125972bc6add0c295760a1a5d9fa9fe8c1749d69ba5f61481",
    "lifeos/reviews/LIFEOS-P3-047/evidence/MANIFEST.md": "0a9e68b2aab707a3d68e583820ebfcaf7c8a7dfa5660bb9d272566d4cfcf1855",
    "lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py": "54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50",
    "lifeos/reviews/LIFEOS-P3-047/evidence/counterexample_results.json": "f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5",
    "lifeos/tasks/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md": "c1c07e14ed31952b373bd91730e866666f14d181acd5bded5ae1cda6b12f0dbb",
    "lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md": "94dac087ee1dfacbdf9b448b7fef08a90109ee7282a89293739342b9dbb800b9",
    "lifeos/reviews/LIFEOS-P3-046_pm_review.md": "0ce9b79aa212065f53b9f8a7cffe10e7a1587b6e37b5ab5acb7305b2260a04b5",
    "lifeos/reviews/LIFEOS-P3-046/evidence/MANIFEST.md": "b5f3c954f932f068cd192ba74a792e2a0c55f47fb93132e98bf94d9909286aaf",
    "lifeos/reviews/LIFEOS-P3-046/evidence/pm_counterexample_attacks.py": "725dc0b2a4e36e9eac9949c9dbc9cb969493a67c303f5684ad268d63d8edb777",
    "lifeos/reviews/LIFEOS-P3-046/evidence/counterexample_results.json": "541fe7980e7ab7d4ce6c38188aeacac477813760ff0810ada0cfee40ff16e560",
    "lifeos/engineering/LIFEOS-P3-046/input/001_candidate_schema.sql": "1d8ea2f5d8095bd254291c6e0e54aa14ca921175da6757ae6c66e6e6e06769fe",
    "lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.py": "106a959cb9dedd49d8b2866e80aef3f4ee7010bf26800d7b3da9d83a4d851e4a",
    "lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.sh": "268c4c0a6a04017222cc1d1838fd9c1c3baa0d930f66087ef4767eaf142bd028",
    "lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md": "9ef071fa5c74c2283125b48f0cc8c91c07f3f667849c2eac1cc14f0654a463fb",
    "lifeos/engineering/LIFEOS-P3-046/evidence/atomic_snapshots.json": "6acd7d65c92752b61b96174d04a28c3320314cff260bf6d280e0267c6bca38dd",
    "lifeos/engineering/LIFEOS-P3-046/evidence/checks/integrity_and_fk.json": "ffb7557407eb113d269e5042f1758ddf6f95457260f8d13420932d825279ef3c",
    "lifeos/engineering/LIFEOS-P3-046/evidence/environment.json": "98e16eae0c263606cb92e71916b70b62b5a69437e4b46371967cf8842817f805",
    "lifeos/engineering/LIFEOS-P3-046/evidence/input/p3_044_preservation.json": "349b7befca98472416503d4b38da9e790a4b365efddf739a8a08b1fc63080593",
    "lifeos/engineering/LIFEOS-P3-046/evidence/input/source_hashes.json": "19e1c9a58d77dd85e6120b99278975a23d6d865d38336b4c89fb9254c4eecd1b",
    "lifeos/engineering/LIFEOS-P3-046/evidence/regressions/p3_031_test_results.json": "7fb8bbc1f688267efc84c17674f2f527f6c2c6fe54f0a81e393c20340b0319a5",
    "lifeos/engineering/LIFEOS-P3-046/evidence/regressions/p3_031_test_run.log": "fe20e2f76225199e647c892f78c6fe365a0b2ebb77ff433190083b6c447b5600",
    "lifeos/engineering/LIFEOS-P3-046/evidence/state_machine_traces.json": "9484580f4ff676081fb128cc935709510baa02244333fc45ce72f7d95e2fa56f",
    "lifeos/engineering/LIFEOS-P3-046/evidence/test_results.json": "6e918b089196077bbca7e6ac0ee24b122ab2c9fb4eeb2ab358d514a622b332bb",
    "lifeos/engineering/LIFEOS-P3-046/evidence/test_run.log": "152ef9022c18ed3bfd0c566bb50f4e9564a3f461e2fff737038666914427dce9",
}

RESULTS = []
SNAPSHOTS = []
INTEGRITY = []
DATABASES = []


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cfg_name(backend, fk, rec):
    return "%s-fk_%s-rec_%s" % (
        backend, "on" if fk else "off", "on" if rec else "off"
    )


def fresh(backend, fk, rec, case):
    if backend == "memory":
        path = ":memory:"
    else:
        path = str(WORK / (case.replace("/", "_").replace(":", "_") + ".db"))
        Path(path).unlink(missing_ok=True)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SNAPSHOT.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk else "OFF"))
    conn.execute("PRAGMA recursive_triggers=%s" % ("ON" if rec else "OFF"))
    assert bool(conn.execute("PRAGMA foreign_keys").fetchone()[0]) == fk
    assert bool(conn.execute("PRAGMA recursive_triggers").fetchone()[0]) == rec
    DATABASES.append(path)
    return conn


def expect_rejected(fn):
    try:
        fn()
    except sqlite3.DatabaseError as exc:
        return str(exc)
    raise AssertionError("operation unexpectedly succeeded")


def record(ident, config, passed, detail, category, **extra):
    row = {
        "id": ident, "severity": "P2", "config": config,
        "status": "PASS" if passed else "FAIL", "detail": detail,
        "category": category,
    }
    row.update(extra)
    RESULTS.append(row)


def health(conn, case, fk):
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    foreign = [list(row) for row in conn.execute("PRAGMA foreign_key_check")]
    passed = integrity == quick == "ok" and not foreign
    INTEGRITY.append({
        "case": case, "foreign_keys_enabled": fk,
        "integrity_check": integrity, "quick_check": quick,
        "foreign_key_check": foreign, "passed": passed,
    })
    return passed


def row(conn, subject_type, subject_id):
    value = conn.execute(
        "SELECT * FROM tombstone WHERE subject_type=? AND subject_id=?",
        (subject_type, subject_id),
    ).fetchone()
    return tuple(value) if value is not None else None


def generic(conn, subject_id="generic", generation=1):
    conn.execute(
        "INSERT INTO tombstone VALUES ('artifact',?,?,?,'seed-reason',?,'accepted',?)",
        (subject_id, generation, "seed:" + subject_id, NOW, NOW),
    )


def authorization_tombstone(p47, conn, aid="auth1", target="accepted"):
    p47.active(conn, aid, "logical:" + aid)
    p47.retire(conn, "revoked", aid)
    auth = conn.execute(
        "SELECT version_no,generation FROM authorization WHERE id=?", (aid,)
    ).fetchone()
    correlation = "authorization-cleanup:%s:%s" % (aid, auth["generation"])
    conn.execute(
        "INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
        ("audit:" + correlation, "authorization.cleanup", "actor:user", aid,
         auth["version_no"], "redacted_by_user", NOW, correlation),
    )
    conn.execute(
        "INSERT INTO tombstone VALUES ('authorization',?,?,?,'user_cleanup',?,'accepted',?)",
        (aid, auth["generation"], "cleanup:" + aid, NOW, NOW),
    )
    if target != "accepted":
        conn.execute(
            "UPDATE tombstone SET cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id=?", (aid,)
        )
    if target not in ("accepted", "active_blocked"):
        conn.execute(
            "UPDATE tombstone SET cleanup_status='cleanup_pending',updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id=?", (aid,)
        )
    if target in ("cleanup_failed", "vendor_limited"):
        conn.execute(
            "UPDATE tombstone SET cleanup_status=?,updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id=?", (target, aid)
        )
    if target == "cleaned":
        for table in ("authorization_scope", "authorization_action", "authorization_policy"):
            conn.execute("DELETE FROM %s WHERE authorization_id=?" % table, (aid,))
        conn.execute(
            "UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 "
            "WHERE subject_type='authorization' AND subject_id=?", (aid,)
        )


def run_original(p47):
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        case = "PM-CE-06/original/%s" % config
        conn = fresh(backend, fk, rec, case)
        try:
            p47.active(conn); p47.retire(conn, "revoked"); generic(conn, "placeholder")
            before = row(conn, "artifact", "placeholder")
            error = expect_rejected(lambda: conn.execute(
                """UPDATE tombstone SET subject_type='authorization',subject_id='auth1',
                   generation=2,command_id='forged-cleanup',reason_code='user_cleanup',
                   blocked_at_ms=? WHERE subject_type='artifact' AND subject_id='placeholder'""",
                (NOW,),
            ))
            after = row(conn, "artifact", "placeholder")
            passed = before == after and row(conn, "authorization", "auth1") is None
            detail = "original PM-CE-06 rejected: " + error
            SNAPSHOTS.append({"case": case, "before": list(before), "after": list(after)})
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk):
            passed, detail = False, "file integrity/FK check failed"
        conn.close()
        record("PM-CE-06", config, passed, detail, "original")


def run_direction_attacks(p47):
    attacks = ("generic_to_authorization", "authorization_to_generic", "authorization_a_to_b")
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for attack in attacks:
            case = "ADJACENT/direction/%s/%s" % (attack, config)
            conn = fresh(backend, fk, rec, case)
            try:
                if attack == "generic_to_authorization":
                    p47.active(conn); p47.retire(conn, "revoked"); generic(conn)
                    before = row(conn, "artifact", "generic")
                    error = expect_rejected(lambda: conn.execute(
                        "UPDATE tombstone SET subject_type='authorization',subject_id='auth1',generation=2 "
                        "WHERE subject_type='artifact' AND subject_id='generic'"
                    ))
                    after = row(conn, "artifact", "generic")
                elif attack == "authorization_to_generic":
                    authorization_tombstone(p47, conn)
                    before = row(conn, "authorization", "auth1")
                    error = expect_rejected(lambda: conn.execute(
                        "UPDATE tombstone SET subject_type='artifact',subject_id='generic' "
                        "WHERE subject_type='authorization' AND subject_id='auth1'"
                    ))
                    after = row(conn, "authorization", "auth1")
                else:
                    authorization_tombstone(p47, conn, "auth1")
                    p47.active(conn, "auth2", "logical:auth2"); p47.retire(conn, "revoked", "auth2")
                    before = row(conn, "authorization", "auth1")
                    error = expect_rejected(lambda: conn.execute(
                        "UPDATE tombstone SET subject_id='auth2' "
                        "WHERE subject_type='authorization' AND subject_id='auth1'"
                    ))
                    after = row(conn, "authorization", "auth1")
                passed = before == after
                detail = "%s rejected: %s" % (attack, error)
            except Exception as exc:
                passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
            if backend == "file" and not health(conn, case, fk):
                passed, detail = False, "file integrity/FK check failed"
            conn.close()
            record("ADJ-DIRECTION", config, passed, detail, "direction", attack=attack)


def run_field_and_combo_attacks(p47):
    states = ("accepted", "active_blocked", "cleanup_pending", "cleanup_failed", "vendor_limited", "cleaned")
    assignments = {
        "subject_type": "subject_type='artifact'",
        "subject_id": "subject_id='ghost'",
        "generation": "generation=generation+1",
        "command_id": "command_id='forged'",
        "reason_code": "reason_code='forged'",
        "blocked_at_ms": "blocked_at_ms=0",
        "compound": "subject_type='artifact',subject_id='ghost',generation=generation+1,command_id='forged',reason_code='forged',blocked_at_ms=0",
    }
    next_status = {
        "accepted": "active_blocked", "active_blocked": "cleanup_pending",
        "cleanup_pending": "cleanup_failed", "cleanup_failed": "cleanup_pending",
        "vendor_limited": "cleanup_pending", "cleaned": "cleaned",
    }
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for index, state_name in enumerate(states):
            case = "ADJACENT/fields/%s/%s" % (state_name, config)
            conn = fresh(backend, fk, rec, case)
            aid = "auth%s" % index
            try:
                authorization_tombstone(p47, conn, aid, state_name)
                baseline = row(conn, "authorization", aid)
                for field, assignment in assignments.items():
                    try:
                        error = expect_rejected(lambda assignment=assignment: conn.execute(
                            "UPDATE tombstone SET %s WHERE subject_type='authorization' AND subject_id=?" % assignment,
                            (aid,),
                        ))
                        passed = row(conn, "authorization", aid) == baseline
                        detail = "%s/%s rejected: %s" % (state_name, field, error)
                    except Exception as exc:
                        passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
                    record("ADJ-FIELD", config, passed, detail, "field", cleanup_state=state_name, field=field)
                try:
                    target = next_status[state_name]
                    error = expect_rejected(lambda: conn.execute(
                        "UPDATE tombstone SET subject_type='artifact',subject_id=?,cleanup_status=?,updated_at_ms=updated_at_ms+1 "
                        "WHERE subject_type='authorization' AND subject_id=?",
                        ("combo:" + aid, target, aid),
                    ))
                    passed = row(conn, "authorization", aid) == baseline
                    detail = "%s identity/status/time combination rejected: %s" % (state_name, error)
                except Exception as exc:
                    passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
                record("ADJ-COMBO", config, passed, detail, "status_time_combo", cleanup_state=state_name)
                SNAPSHOTS.append({"case": case, "state": state_name, "protected": list(baseline)})
            except Exception as exc:
                for field in assignments:
                    record("ADJ-FIELD", config, False, "%s: %s" % (type(exc).__name__, exc), "field", cleanup_state=state_name, field=field)
                record("ADJ-COMBO", config, False, "%s: %s" % (type(exc).__name__, exc), "status_time_combo", cleanup_state=state_name)
            if backend == "file" and not health(conn, case, fk):
                record("FILE-HEALTH", config, False, "file integrity/FK check failed", "health", cleanup_state=state_name)
            conn.close()


def run_replace_attacks(p47):
    attacks = ("insert_or_replace", "conflict_insert", "delete_reinsert", "update_or_replace", "upsert_update")
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        for attack in attacks:
            case = "ADJACENT/replace/%s/%s" % (attack, config)
            conn = fresh(backend, fk, rec, case)
            try:
                if attack in ("insert_or_replace", "conflict_insert", "delete_reinsert"):
                    authorization_tombstone(p47, conn)
                    before = row(conn, "authorization", "auth1")
                    values = ("authorization", "auth1", 2, "forged", "forged", NOW, "accepted", NOW)
                    if attack == "insert_or_replace":
                        error = expect_rejected(lambda: conn.execute(
                            "INSERT OR REPLACE INTO tombstone VALUES (?,?,?,?,?,?,?,?)", values
                        ))
                    elif attack == "conflict_insert":
                        error = expect_rejected(lambda: conn.execute(
                            "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)", values
                        ))
                    else:
                        conn.execute("BEGIN IMMEDIATE")
                        error = expect_rejected(lambda: conn.execute(
                            "DELETE FROM tombstone WHERE subject_type='authorization' AND subject_id='auth1'"
                        ))
                        conn.rollback()
                    after = row(conn, "authorization", "auth1")
                else:
                    p47.active(conn); p47.retire(conn, "revoked"); generic(conn)
                    before = row(conn, "artifact", "generic")
                    if attack == "update_or_replace":
                        error = expect_rejected(lambda: conn.execute(
                            "UPDATE OR REPLACE tombstone SET subject_type='authorization',subject_id='auth1',generation=2 "
                            "WHERE subject_type='artifact' AND subject_id='generic'"
                        ))
                    else:
                        error = expect_rejected(lambda: conn.execute(
                            """INSERT INTO tombstone VALUES ('artifact','generic',1,'new','new',?,'accepted',?)
                               ON CONFLICT(subject_type,subject_id) DO UPDATE SET
                                 subject_type='authorization',subject_id='auth1',generation=2,
                                 command_id='forged',reason_code='forged'""", (NOW, NOW)
                        ))
                    after = row(conn, "artifact", "generic")
                passed = before == after
                detail = "%s rejected: %s" % (attack, error)
            except Exception as exc:
                passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
            if backend == "file" and not health(conn, case, fk):
                passed, detail = False, "file integrity/FK check failed"
            conn.close()
            record("ADJ-REPLACE", config, passed, detail, "replace", attack=attack)


def run_multirow(p47):
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        case = "ADJACENT/multirow/%s" % config
        conn = fresh(backend, fk, rec, case)
        try:
            p47.active(conn); p47.retire(conn, "revoked"); generic(conn, "legal"); generic(conn, "rebind")
            before = [tuple(x) for x in conn.execute("SELECT * FROM tombstone ORDER BY subject_id")]
            error = expect_rejected(lambda: conn.execute(
                """UPDATE tombstone SET
                     subject_type=CASE WHEN subject_id='rebind' THEN 'authorization' ELSE subject_type END,
                     subject_id=CASE WHEN subject_id='rebind' THEN 'auth1' ELSE subject_id END,
                     generation=CASE WHEN subject_id='rebind' THEN 2 ELSE generation END,
                     cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1
                   WHERE subject_id IN ('legal','rebind')"""
            ))
            after = [tuple(x) for x in conn.execute("SELECT * FROM tombstone ORDER BY subject_id")]
            passed = before == after
            detail = "multi-row statement rolled back atomically: " + error
            SNAPSHOTS.append({"case": case, "before": [list(x) for x in before], "after": [list(x) for x in after]})
        except Exception as exc:
            passed, detail = False, "%s: %s" % (type(exc).__name__, exc)
        if backend == "file" and not health(conn, case, fk):
            passed, detail = False, "file integrity/FK check failed"
        conn.close()
        record("ADJ-MULTIROW", config, passed, detail, "multirow")


def run_legal_paths(p47):
    for backend, fk, rec in CONFIGS:
        config = cfg_name(backend, fk, rec)
        case = "LEGAL/cleanup/%s" % config
        conn = fresh(backend, fk, rec, case)
        try:
            authorization_tombstone(p47, conn, "auth1", "accepted")
            aid = "auth1"
            steps = (
                ("LEGAL-01", "active_blocked"), ("LEGAL-02", "cleanup_pending"),
                ("LEGAL-03", "cleanup_failed"), ("LEGAL-04", "cleanup_pending"),
                ("LEGAL-05", "vendor_limited"), ("LEGAL-06", "cleanup_pending"),
            )
            trace = ["accepted"]
            for ident, target in steps:
                old_time = conn.execute("SELECT updated_at_ms FROM tombstone WHERE subject_id=?", (aid,)).fetchone()[0]
                conn.execute(
                    "UPDATE tombstone SET cleanup_status=?,updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?",
                    (target, aid),
                )
                current = conn.execute("SELECT cleanup_status,updated_at_ms FROM tombstone WHERE subject_id=?", (aid,)).fetchone()
                passed = current[0] == target and current[1] > old_time
                record(ident, config, passed, "legal cleanup transition", "legal", target=target)
                trace.append(target)
            for table in ("authorization_scope", "authorization_action", "authorization_policy"):
                conn.execute("DELETE FROM %s WHERE authorization_id=?" % table, (aid,))
            old_time = conn.execute("SELECT updated_at_ms FROM tombstone WHERE subject_id=?", (aid,)).fetchone()[0]
            conn.execute(
                "UPDATE tombstone SET cleanup_status='cleaned',updated_at_ms=updated_at_ms+1 "
                "WHERE subject_type='authorization' AND subject_id=?", (aid,)
            )
            current = conn.execute("SELECT cleanup_status,updated_at_ms FROM tombstone WHERE subject_id=?", (aid,)).fetchone()
            record("LEGAL-07", config, current[0] == "cleaned" and current[1] > old_time,
                   "legal cleaned transition", "legal", target="cleaned")
            trace.append("cleaned")

            generic(conn, "generic-legal")
            changed = conn.execute(
                "UPDATE tombstone SET generation=2,command_id='generic-v2',reason_code='retry',"
                "cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1 "
                "WHERE subject_type='artifact' AND subject_id='generic-legal' AND generation=1"
            ).rowcount
            record("LEGAL-08", config, changed == 1, "pre-existing generic semantics preserved", "legal")

            auth_before = row(conn, "authorization", aid)
            error = expect_rejected(lambda: conn.execute(
                "UPDATE tombstone SET updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (aid,)
            ))
            record("LEGAL-09", config, row(conn, "authorization", aid) == auth_before,
                   "time without status rejected: " + error, "time")

            authorization_tombstone(p47, conn, "auth2", "cleanup_failed")
            auth2_before = row(conn, "authorization", "auth2")
            error = expect_rejected(lambda: conn.execute(
                "UPDATE tombstone SET cleanup_status='cleanup_pending',updated_at_ms=updated_at_ms-1 "
                "WHERE subject_type='authorization' AND subject_id='auth2'"
            ))
            record("LEGAL-10", config, row(conn, "authorization", "auth2") == auth2_before,
                   "decreasing status time rejected: " + error, "time")

            conn.execute(
                "UPDATE tombstone SET subject_type=subject_type,subject_id=subject_id,generation=generation,"
                "command_id=command_id,reason_code=reason_code,blocked_at_ms=blocked_at_ms "
                "WHERE subject_type='authorization' AND subject_id='auth2'"
            )
            record("LEGAL-11", config, row(conn, "authorization", "auth2") == auth2_before,
                   "no-op envelope update remains legal", "legal")
            SNAPSHOTS.append({"case": case, "legal_trace": trace, "final": list(row(conn, "authorization", aid))})
        except Exception as exc:
            existing = {(x["id"], x["config"]) for x in RESULTS}
            for index in range(1, 12):
                ident = "LEGAL-%02d" % index
                if (ident, config) not in existing:
                    record(ident, config, False, "%s: %s" % (type(exc).__name__, exc), "legal")
        if backend == "file" and not health(conn, case, fk):
            record("FILE-HEALTH", config, False, "file integrity/FK check failed", "health")
        conn.close()


def load_p47():
    spec = importlib.util.spec_from_file_location("lifeos_p3047_read_only", P47_RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SNAPSHOT = SNAPSHOT
    module.WORK = WORK
    module.RESULTS = []
    module.SNAPSHOTS = []
    module.TRACES = []
    module.INTEGRITY = []
    module.DATABASES = []
    return module


def run_p47_equivalent(p47):
    for ident, severity, scenario in p47.STANDARD_AC:
        p47.run_standard("AC", ident, severity, scenario)
    p47.run_ac14(); p47.run_ac16()
    p47.run_standard("PM-CE", "PM-CE-01", "P2", p47.ce01)
    p47.run_standard("PM-CE", "PM-CE-02", "P1", p47.ce02)
    p47.run_standard("PM-CE", "PM-CE-03", "P1", p47.ce03)
    p47.run_expired_lease()
    p47.run_standard("PM-CE", "PM-CE-04", "P2", p47.ce04)
    p47.run_retention()
    p47.run_standard("REGRESSION", "P3-044-CURRENT", "P1", p47.p3044)
    return p47.summary()


def run_p31():
    result = subprocess.run(["sh", str(P31_SHELL)], cwd=ROOT, text=True, capture_output=True)
    (EVIDENCE / "regressions/p3_031_test_run.log").write_text(
        result.stdout + result.stderr, encoding="utf-8"
    )
    shutil.copyfile(
        LIFEOS / "engineering/LIFEOS-P3-031/evidence/test_results.json",
        EVIDENCE / "regressions/p3_031_test_results.json",
    )
    return result.returncode


def read_only_state():
    return {
        name: {"expected_sha256": expected, "actual_sha256": digest(ROOT / name),
               "matches_expected": digest(ROOT / name) == expected}
        for name, expected in READ_ONLY.items()
    }


def category_stats():
    output = {}
    for category in sorted({row["category"] for row in RESULTS}):
        selected = [row for row in RESULTS if row["category"] == category]
        output[category] = {
            "instances": len(selected),
            "pass": sum(row["status"] == "PASS" for row in selected),
            "fail": sum(row["status"] == "FAIL" for row in selected),
        }
    return output


def write_evidence(p31_exit, p47, p47_stats, preservation):
    p48_summary = {
        "P0": {"PASS": 0, "FAIL": 0, "NOT_IMPLEMENTED": 0, "UNKNOWN": 0},
        "P1": {"PASS": 0, "FAIL": 0, "NOT_IMPLEMENTED": 0, "UNKNOWN": 0},
        "P2": {
            "PASS": sum(row["status"] == "PASS" for row in RESULTS),
            "FAIL": sum(row["status"] == "FAIL" for row in RESULTS),
            "NOT_IMPLEMENTED": 0, "UNKNOWN": 0,
        },
    }
    p48_summary["total"] = dict(p48_summary["P2"])
    payload = {
        "task_id": "LIFEOS-P3-048", "route": "gpt-5.6-sol+xhigh",
        "scope": "synthetic SQLite only", "summary": p48_summary,
        "categories": category_stats(), "p3_047_equivalent_summary": p47_stats,
        "p3_031_exit": p31_exit, "results": RESULTS,
    }
    (EVIDENCE / "test_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "atomic_snapshots.json").write_text(
        json.dumps(SNAPSHOTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "checks/integrity_and_fk.json").write_text(
        json.dumps({"all_passed": all(row["passed"] for row in INTEGRITY), "results": INTEGRITY}, indent=2) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE / "input/read_only_preservation.json").write_text(
        json.dumps(preservation, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "input/source_hashes.json").write_text(json.dumps({
        "candidate_source": digest(CANDIDATE), "candidate_snapshot": digest(SNAPSHOT),
        "p3_031_tests": digest(P31_TESTS), "p3_031_shell": digest(P31_SHELL),
        "p3_048_runner": digest(Path(__file__)), "p3_047_read_only_runner": digest(P47_RUNNER),
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "environment.json").write_text(json.dumps({
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "platform": platform.platform(), "machine": platform.machine(),
        "network_used": False, "real_db_vault_file_tauri_ipc_used": False,
        "real_migration_executed": False, "data_classification": "synthetic only",
        "pragma_matrix": {"foreign_keys": ["ON", "OFF"], "recursive_triggers": ["ON", "OFF"]},
        "database_paths": DATABASES + p47.DATABASES,
    }, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "regressions/p3_047_equivalent_results.json").write_text(json.dumps({
        "task_id": "LIFEOS-P3-047-equivalent-on-P3-048-candidate",
        "summary": p47_stats, "results": p47.RESULTS,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "regressions/p3_047_equivalent_atomic_snapshots.json").write_text(
        json.dumps(p47.SNAPSHOTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "regressions/p3_047_equivalent_state_machine_traces.json").write_text(
        json.dumps(p47.TRACES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "regressions/p3_047_equivalent_integrity_and_fk.json").write_text(
        json.dumps({"all_passed": all(row["passed"] for row in p47.INTEGRITY), "results": p47.INTEGRITY}, indent=2) + "\n",
        encoding="utf-8",
    )
    return p48_summary


def main():
    for path in (SNAPSHOT.parent, EVIDENCE / "checks", EVIDENCE / "input", EVIDENCE / "regressions", WORK):
        path.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob("*.db"):
        old.unlink()
    before = read_only_state()
    if not all(row["matches_expected"] for row in before.values()):
        print("read-only baseline mismatch", file=sys.stderr)
        return 2
    shutil.copyfile(CANDIDATE, SNAPSHOT)
    p31_exit = run_p31()
    p47 = load_p47()
    p47_stats = run_p47_equivalent(p47)
    run_original(p47)
    run_direction_attacks(p47)
    run_field_and_combo_attacks(p47)
    run_replace_attacks(p47)
    run_multirow(p47)
    run_legal_paths(p47)
    after = read_only_state()
    preservation = {
        name: {
            "expected_sha256": READ_ONLY[name],
            "before_sha256": before[name]["actual_sha256"],
            "after_sha256": after[name]["actual_sha256"],
            "unchanged": before[name]["actual_sha256"] == after[name]["actual_sha256"]
                         and after[name]["matches_expected"],
        }
        for name in READ_ONLY
    }
    p48_summary = write_evidence(p31_exit, p47, p47_stats, preservation)
    for result in RESULTS:
        print("%-16s %-28s %-4s %s" % (result["id"], result["config"], result["status"], result["detail"]))
    print("P3_048_SUMMARY " + json.dumps(p48_summary, sort_keys=True))
    print("P3_047_EQUIVALENT " + json.dumps(p47_stats, sort_keys=True))
    print("P3_031_EXIT", p31_exit)
    print("READ_ONLY_PRESERVED", all(row["unchanged"] for row in preservation.values()))
    bad = p31_exit != 0 or any(row["status"] != "PASS" for row in RESULTS)
    bad = bad or p47_stats.get("total", {}).get("PASS") != 297
    bad = bad or any(p47_stats.get("total", {}).get(key, 0) for key in ("FAIL", "NOT_IMPLEMENTED", "UNKNOWN"))
    bad = bad or not all(row["passed"] for row in INTEGRITY)
    bad = bad or not all(row["passed"] for row in p47.INTEGRITY)
    bad = bad or not all(row["unchanged"] for row in preservation.values())
    bad = bad or digest(CANDIDATE) != digest(SNAPSHOT)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
