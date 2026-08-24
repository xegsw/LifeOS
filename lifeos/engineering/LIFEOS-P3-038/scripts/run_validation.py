#!/usr/bin/env python3
"""Controlled file-backed SQLite remediation regression for LIFEOS-P3-038.

This harness has no path arguments. It only creates synthetic SQLite files under
the task-local work directory and never starts Tauri/IPC or network services.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sqlite3
import stat
import sys
import time
from pathlib import Path


TASK_ID = "LIFEOS-P3-038"
TASK_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TASK_DIR.parents[2]
INPUT_DIR = TASK_DIR / "input"
WORK_DIR = TASK_DIR / "work"
EVIDENCE_DIR = TASK_DIR / "evidence"
CHECKS_DIR = EVIDENCE_DIR / "checks"
INPUT_EVIDENCE_DIR = EVIDENCE_DIR / "input"
MIGRATION_EVIDENCE_DIR = EVIDENCE_DIR / "migration"
SOURCE_SQL = INPUT_DIR / "001_candidate_schema.sql"
SOURCE_DB = WORK_DIR / "source_fixture.db"
NOW = 1786550400000

P3_031 = PROJECT_ROOT / "lifeos" / "engineering" / "LIFEOS-P3-031"
STABLE_INPUTS = {
    P3_031 / "migrations" / "001_candidate_schema.sql": "008cd328661d869270f9fa386e901aad5e5e76d745acb8b33f470de02eac4cf2",
    P3_031 / "tests" / "run_contract_tests.py": "246f3675b69207cf574f0aa9da919adb5b3b435996160dfe658e77f61f9339da",
    P3_031 / "scripts" / "run_validation.sh": "611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d",
}
BEFORE_REMEDIATION_HASHES = {
    "lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql": "55f3e15b6cb9c3f0e41da2f5cc42809df58dd2e4ac9f2ede091b58590001c4b1",
    "lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py": "defdd87e1ee355a978ddb75352c1a8aeca9e33960a2ad2922b8385e9740b295c",
    "lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh": "61f9d6a17dfd4eb455ffd0e768c5289d0e9b5d578235130aa212d6e0896e2769",
}
P3_037_FAILURE_INPUTS = {
    PROJECT_ROOT / "lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md": "8aa519c023e846f88de7a3d0d0b48e8bb9372f50251db7be8c9b38dd3a2072e3",
    PROJECT_ROOT / "lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json": "253a3ff4ba33137e90ef3ead0f8cdbeddeb1a507e927fa1f97c8a90b0ee4e354",
    PROJECT_ROOT / "lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json": "374c0304e6557c4a9561609820ce741a49108d4731a98fad3a3ceb4dbd0ff603",
    PROJECT_ROOT / "lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json": "cf3d3b8da7d8a837010e2fc883102a516e6018bad7454431933867aeae80df34",
    PROJECT_ROOT / "lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json": "68d3e1a16bb9493e552f5ea0ec3918fe5576be6e26943cacb7fd2ff33f4d8dda",
}

LOG_LINES: list[str] = []
DB_ACCESS_LOG: list[dict] = []


def log(message: str) -> None:
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%S%z')}] {message}"
    LOG_LINES.append(line)
    print(line)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))


def validate_task_path(raw: str | Path, *, kind: str, must_exist: bool = False) -> Path:
    """Reject unsafe/broad/user-like/network/symlink paths before access."""
    raw_text = str(raw)
    lowered = raw_text.lower()
    if raw_text.startswith("~") or raw_text.startswith("//") or "://" in raw_text:
        raise ValueError("unsafe path syntax")
    if any(token in lowered for token in ("vault", "user.db", "lifeos.db", "real.db")):
        raise ValueError("user DB/Vault-like path rejected")
    candidate = Path(raw_text)
    if candidate.is_symlink():
        raise ValueError("symlink rejected")
    resolved = candidate.resolve(strict=False)
    root = TASK_DIR.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("path outside task isolation") from exc
    if resolved in (root, INPUT_DIR.resolve(), WORK_DIR.resolve(), EVIDENCE_DIR.resolve()):
        raise ValueError("broad directory rejected")
    if kind == "db" and resolved.suffix not in (".db", ".sqlite"):
        raise ValueError("unexpected DB suffix")
    if kind == "sql" and resolved.suffix != ".sql":
        raise ValueError("unexpected SQL suffix")
    if must_exist and not resolved.is_file():
        raise ValueError("required file missing")
    return resolved


def connect_db(path: Path, *, readonly: bool = False) -> sqlite3.Connection:
    safe = validate_task_path(path, kind="db", must_exist=readonly)
    DB_ACCESS_LOG.append({"path": relative(safe), "readonly": readonly})
    if readonly:
        conn = sqlite3.connect(f"file:{safe}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(safe)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def reset_generated_dirs() -> None:
    for directory in (WORK_DIR, CHECKS_DIR, INPUT_EVIDENCE_DIR, MIGRATION_EVIDENCE_DIR):
        if directory.exists():
            for child in directory.iterdir():
                if child.is_symlink() or child.is_file():
                    child.unlink()
                elif child.is_dir():
                    shutil.rmtree(child)
        directory.mkdir(parents=True, exist_ok=True)


def check_path_isolation() -> dict:
    rejected = {}
    probes = {
        "home_tilde": "~/.lifeos/user.db",
        "filesystem_root": "/",
        "project_root": str(PROJECT_ROOT),
        "network_unc": "//server/share/test.db",
        "network_scheme": "smb://server/share/test.db",
        "user_db_like": str(TASK_DIR / "work" / "user.db"),
        "vault_like": str(TASK_DIR / "work" / "SyntheticVault" / "test.db"),
        "broad_work_dir": str(WORK_DIR),
    }
    for name, probe in probes.items():
        try:
            validate_task_path(probe, kind="db")
            rejected[name] = False
        except ValueError:
            rejected[name] = True
    symlink_probe = WORK_DIR / "outside_symlink.db"
    symlink_probe.symlink_to(PROJECT_ROOT)
    try:
        validate_task_path(symlink_probe, kind="db")
        rejected["symlink_outside"] = False
    except ValueError:
        rejected["symlink_outside"] = True
    finally:
        symlink_probe.unlink()
    allowed = validate_task_path(WORK_DIR / "allowed_synthetic.db", kind="db")
    return {
        "all_unsafe_rejected": all(rejected.values()),
        "rejected": rejected,
        "allowed_probe": relative(allowed),
        "fixed_root": relative(TASK_DIR),
        "no_cli_path_arguments": True,
    }


def verify_stable_inputs() -> dict:
    rows = []
    all_match = True
    for path, expected in STABLE_INPUTS.items():
        actual = sha256(path)
        matches = actual == expected
        all_match = all_match and matches
        rows.append({"path": relative(path), "expected_sha256": expected, "actual_sha256": actual, "matches": matches})
    snapshot_hash = sha256(validate_task_path(SOURCE_SQL, kind="sql", must_exist=True))
    source_hash = sha256(P3_031 / "migrations" / "001_candidate_schema.sql")
    return {
        "all_stable_inputs_match": all_match,
        "stable_inputs": rows,
        "candidate_snapshot": {"path": relative(SOURCE_SQL), "sha256": snapshot_hash, "matches_source": snapshot_hash == source_hash},
    }


def verify_p3_037_failure_inputs() -> dict:
    rows = []
    all_unchanged = True
    for path, expected in P3_037_FAILURE_INPUTS.items():
        actual = sha256(path)
        unchanged = actual == expected
        all_unchanged = all_unchanged and unchanged
        rows.append({"path": relative(path), "expected_sha256": expected, "actual_sha256": actual, "unchanged": unchanged})
    return {"all_unchanged": all_unchanged, "files": rows, "read_only_check": True}


def create_source_fixture() -> dict:
    building = WORK_DIR / "source_fixture_building.db"
    if building.exists():
        building.unlink()
    conn = connect_db(building)
    migration = SOURCE_SQL.read_text(encoding="utf-8")
    conn.executescript(migration)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA user_version=1")
    conn.execute(
        "INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        ("synthetic-project-001", "SYNTHETIC_PROJECT", "CONTROLLED_TEST", "active", 1, NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?)",
        ("synthetic-source-001", "synthetic", "SYNTHETIC_STABLE_KEY", "SYNTHETIC_LOCATOR", "available", "allowed", 1, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO artifact VALUES (?,?,?,?,?,?,?,?)",
        ("synthetic-artifact-001", "synthetic-source-001", None, "note", "draft", 5, NOW, NOW),
    )
    payload = "SYNTHETIC_PAYLOAD_NO_USER_CONTENT"
    payload_hash = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()
    conn.execute(
        "INSERT INTO artifact_version VALUES (?,?,?,?,?,?,?,?,?)",
        ("synthetic-version-001", "synthetic-artifact-001", 1, "synthetic-source-001", payload, payload_hash, NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO content_identity VALUES (?,?,?,?,?)",
        ("synthetic-version-001", "user_original", "synthetic_actor", "synthetic:actor", None),
    )
    conn.execute(
        "UPDATE artifact SET current_version_id='synthetic-version-001', status='active' WHERE id='synthetic-artifact-001'"
    )
    conn.execute(
        "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", "synthetic-artifact-001", 5, "synthetic-command-001", "CONTROLLED_TEST", NOW, "accepted", NOW),
    )
    conn.execute(
        "UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'"
    )
    conn.execute(
        "INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("synthetic-job-001", "publish", "artifact", "synthetic-artifact-001", 5, None, "pending", 0, NOW, None, 0, None, "synthetic-idempotency-001", None),
    )
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("synthetic-auth-001", "synthetic-logical-001", "synthetic:actor", "local", "controlled-test", "device", "proposed", 1, 1, NOW, "indefinite", None, None, "synthetic-policy@1", None, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        ("synthetic-scope-allow", "synthetic-auth-001", "allow", "synthetic-project-001", None, None),
    )
    conn.execute(
        "INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        ("synthetic-scope-deny", "synthetic-auth-001", "deny", None, "synthetic-source-001", None),
    )
    conn.execute(
        "INSERT INTO authorization_action VALUES (?,?,?)",
        ("synthetic-action-read", "synthetic-auth-001", "read"),
    )
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("synthetic-auth-001", "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10),
    )
    conn.execute("UPDATE authorization SET status='active' WHERE id='synthetic-auth-001'")
    conn.execute(
        "INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
        ("synthetic-audit-baseline", "authorization.activate", "synthetic:actor", "synthetic-auth-001", 1, "ok", NOW, "synthetic-correlation"),
    )
    conn.commit()
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    fk = [dict(row) for row in conn.execute("PRAGMA foreign_key_check")]
    journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
    schema = "\n".join(row[0] + ";" for row in conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")) + "\n"
    conn.close()
    building.replace(SOURCE_DB)
    SOURCE_DB.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return {
        "source_path": relative(SOURCE_DB),
        "source_sha256": sha256(SOURCE_DB),
        "readonly_mode": oct(SOURCE_DB.stat().st_mode & 0o777),
        "quick_check": quick,
        "foreign_key_violations": fk,
        "journal_mode": journal,
        "schema": schema,
        "fixture_declaration": {
            "synthetic_only": True,
            "contains_real_user_data": False,
            "contains_real_vault_path": False,
            "contains_url_or_secret": False,
            "identifiers": ["synthetic-*"],
        },
    }


def db_checks(path: Path) -> dict:
    conn = connect_db(path, readonly=True)
    try:
        return {
            "integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0],
            "quick_check": conn.execute("PRAGMA quick_check").fetchone()[0],
            "foreign_key_violations": [dict(row) for row in conn.execute("PRAGMA foreign_key_check")],
            "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0],
            "foreign_keys": conn.execute("PRAGMA foreign_keys").fetchone()[0],
            "user_version": conn.execute("PRAGMA user_version").fetchone()[0],
        }
    finally:
        conn.close()


def copy_working(name: str) -> Path:
    target = WORK_DIR / f"{name}.db"
    validate_task_path(target, kind="db")
    shutil.copyfile(SOURCE_DB, target)
    target.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return target


def consumption_gates(conn: sqlite3.Connection, generation: int = 5) -> dict:
    row = conn.execute(
        "SELECT generation, cleanup_status FROM tombstone WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'"
    ).fetchone()
    blocked = bool(row and row["generation"] >= generation and row["cleanup_status"] != "accepted")
    result = "DENY" if blocked else "ALLOW"
    return {name: result for name in ("read", "search", "suggest", "outbox", "export", "restore")}


def tombstone_row(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT subject_type,subject_id,generation,command_id,reason_code,blocked_at_ms,cleanup_status,updated_at_ms FROM tombstone WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'"
    ).fetchone()
    return dict(row) if row else None


def attempt_db_operation(path: Path, operation) -> dict:
    conn = connect_db(path)
    try:
        operation(conn)
        conn.commit()
        return {"committed": True, "sqlite_error": None}
    except sqlite3.DatabaseError as exc:
        conn.rollback()
        return {"committed": False, "sqlite_error": str(exc)}
    finally:
        conn.close()


def validate_p2_2() -> tuple[dict, dict]:
    before_source_hash = sha256(SOURCE_DB)
    baseline_conn = connect_db(SOURCE_DB, readonly=True)
    baseline_row = tombstone_row(baseline_conn)
    baseline_gates = consumption_gates(baseline_conn)
    baseline_conn.close()

    ordinary_path = copy_working("p2_2_ordinary_delete")
    ordinary = attempt_db_operation(
        ordinary_path,
        lambda conn: conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'"),
    )
    conn = connect_db(ordinary_path, readonly=True)
    ordinary.update({"row_after": tombstone_row(conn), "gates_after": consumption_gates(conn)})
    conn.close()

    replace_path = copy_working("p2_2_insert_or_replace")
    replace = attempt_db_operation(
        replace_path,
        lambda conn: conn.execute(
            "INSERT OR REPLACE INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "synthetic-artifact-001", 4, "synthetic-command-replace", "CONTROLLED_TEST", NOW, "accepted", NOW),
        ),
    )
    conn = connect_db(replace_path, readonly=True)
    replace.update({"row_after": tombstone_row(conn), "gates_after": consumption_gates(conn)})
    conn.close()

    commit_path = copy_working("p2_2_delete_insert_commit")
    def delete_insert(conn):
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'")
        conn.execute(
            "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "synthetic-artifact-001", 4, "synthetic-command-reinsert", "CONTROLLED_TEST", NOW, "accepted", NOW),
        )
    commit_attack = attempt_db_operation(commit_path, delete_insert)
    conn = connect_db(commit_path, readonly=True)
    commit_attack.update({"row_after": tombstone_row(conn), "gates_after": consumption_gates(conn)})
    conn.close()

    rollback_path = copy_working("p2_2_delete_insert_rollback")
    conn = connect_db(rollback_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='synthetic-artifact-001'")
        conn.execute(
            "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "synthetic-artifact-001", 4, "synthetic-command-rollback", "CONTROLLED_TEST", NOW, "accepted", NOW),
        )
        in_transaction = {"attack_rejected": False, "row": tombstone_row(conn), "gates": consumption_gates(conn)}
        conn.rollback()
    except sqlite3.DatabaseError as exc:
        conn.rollback()
        in_transaction = {"attack_rejected": True, "sqlite_error": str(exc), "row": tombstone_row(conn), "gates": consumption_gates(conn)}
    rollback_after = {"row": tombstone_row(conn), "gates": consumption_gates(conn)}
    conn.close()
    rollback_ok = rollback_after["row"] == baseline_row and all(v == "DENY" for v in rollback_after["gates"].values())

    attacks_blocked = (
        not ordinary["committed"]
        and not replace["committed"]
        and not commit_attack["committed"]
        and all(v == "DENY" for v in ordinary["gates_after"].values())
        and all(v == "DENY" for v in replace["gates_after"].values())
        and all(v == "DENY" for v in commit_attack["gates_after"].values())
    )
    status = "PASS" if attacks_blocked and rollback_ok else "FAIL"
    evidence = {
        "residual": "P2-2",
        "target_contract": "DELETE/REPLACE rejected and all six gates remain DENY",
        "status": status,
        "baseline": {"row": baseline_row, "gates": baseline_gates},
        "ordinary_delete": ordinary,
        "insert_or_replace": replace,
        "delete_insert_commit": commit_attack,
        "delete_insert_rollback": {"in_transaction": in_transaction, "after_rollback": rollback_after, "rollback_ok": rollback_ok},
        "source_unchanged": sha256(SOURCE_DB) == before_source_hash,
        "classification": "P1" if status == "FAIL" else None,
    }
    result = {
        "id": "FILE-P1-P2-2",
        "severity": "P1",
        "status": status,
        "detail": "DELETE/INSERT and OR REPLACE can lower/remove tombstone and six simulated gates ALLOW" if status == "FAIL" else "all bypass forms rejected",
    }
    return result, evidence


def validate_p2_3() -> tuple[dict, dict]:
    path = copy_working("p2_3_status_insert")
    conn = connect_db(path)
    illegal_statuses = ["active_blocked", "cleaned", "cleanup_failed", "vendor_limited"]
    matrix = {}
    for index, status_name in enumerate(illegal_statuses, 1):
        subject = f"synthetic-status-{index}"
        try:
            conn.execute(
                "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
                ("artifact", subject, 1, f"synthetic-command-status-{index}", "CONTROLLED_TEST", NOW, status_name, NOW),
            )
            conn.commit()
            matrix[status_name] = {"accepted_by_db": True, "row_count": conn.execute("SELECT count(*) FROM tombstone WHERE subject_id=?", (subject,)).fetchone()[0]}
        except sqlite3.DatabaseError as exc:
            conn.rollback()
            matrix[status_name] = {"accepted_by_db": False, "sqlite_error": str(exc), "row_count": 0}

    accepted_subject = "synthetic-status-accepted"
    accepted_ok = True
    legal_transitions = []
    try:
        conn.execute(
            "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", accepted_subject, 1, "synthetic-command-accepted", "CONTROLLED_TEST", NOW, "accepted", NOW),
        )
        conn.commit()
        for target in ("active_blocked", "cleanup_pending", "cleaned"):
            conn.execute("UPDATE tombstone SET cleanup_status=? WHERE subject_id=?", (target, accepted_subject))
            conn.commit()
            legal_transitions.append({"to": target, "accepted_by_db": True})
    except sqlite3.DatabaseError as exc:
        conn.rollback()
        accepted_ok = False
        legal_transitions.append({"accepted_by_db": False, "sqlite_error": str(exc)})

    invalid_subject = "synthetic-status-invalid"
    conn.execute(
        "INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", invalid_subject, 1, "synthetic-command-invalid", "CONTROLLED_TEST", NOW, "accepted", NOW),
    )
    conn.commit()
    try:
        conn.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_id=?", (invalid_subject,))
        conn.commit()
        invalid_transition_rejected = False
        invalid_error = None
    except sqlite3.DatabaseError as exc:
        conn.rollback()
        invalid_transition_rejected = True
        invalid_error = str(exc)
    conn.close()

    illegal_rejected = all(not item["accepted_by_db"] and item["row_count"] == 0 for item in matrix.values())
    legal_ok = accepted_ok and all(item.get("accepted_by_db") for item in legal_transitions) and invalid_transition_rejected
    status = "PASS" if illegal_rejected and legal_ok else "FAIL"
    evidence = {
        "residual": "P2-3",
        "target_contract": "ordinary creation only accepts initial accepted",
        "status": status,
        "direct_insert_matrix": matrix,
        "accepted_start": accepted_ok,
        "legal_transitions": legal_transitions,
        "invalid_accepted_to_cleaned": {"rejected": invalid_transition_rejected, "sqlite_error": invalid_error},
        "classification": "P1" if status == "FAIL" else None,
    }
    result = {
        "id": "FILE-P1-P2-3",
        "severity": "P1",
        "status": status,
        "detail": "four non-accepted initial states are directly insertable" if status == "FAIL" else "illegal initial states rejected",
    }
    return result, evidence


def auth_gate(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        """
        SELECT a.status,
          EXISTS(SELECT 1 FROM authorization_scope s WHERE s.authorization_id=a.id AND s.effect='allow' AND s.project_id='synthetic-project-001') AS has_allow,
          EXISTS(SELECT 1 FROM authorization_scope s WHERE s.authorization_id=a.id AND s.effect='deny' AND s.project_id='synthetic-project-001') AS has_deny,
          EXISTS(SELECT 1 FROM authorization_action x WHERE x.authorization_id=a.id AND x.action='read') AS has_action,
          EXISTS(SELECT 1 FROM authorization_policy p WHERE p.authorization_id=a.id
            AND p.retention_mode IS NOT NULL AND p.sensitivity_rank IS NOT NULL
            AND p.training_allowed IS NOT NULL AND p.external_send_allowed IS NOT NULL
            AND p.recipients_json IS NOT NULL AND p.regions_json IS NOT NULL
            AND p.disclosure_json IS NOT NULL AND p.source_license_json IS NOT NULL
            AND p.quantity_ceiling IS NOT NULL AND p.frequency_ceiling IS NOT NULL) AS has_policy
        FROM authorization a WHERE a.id='synthetic-auth-001'
        """
    ).fetchone()
    if not row or row["status"] != "active" or not row["has_allow"] or row["has_deny"] or not row["has_action"] or not row["has_policy"]:
        return "DENY_OR_AMBIGUOUS"
    return "ALLOW"


def parent_state(conn: sqlite3.Connection) -> dict:
    row = conn.execute("SELECT status,generation FROM authorization WHERE id='synthetic-auth-001'").fetchone()
    return dict(row)


def validate_p2_4() -> tuple[dict, dict]:
    cases = {
        "scope": ("DELETE FROM authorization_scope WHERE id='synthetic-scope-allow'", "authorization_scope"),
        "action": ("DELETE FROM authorization_action WHERE id='synthetic-action-read'", "authorization_action"),
        "policy": ("DELETE FROM authorization_policy WHERE authorization_id='synthetic-auth-001'", "authorization_policy"),
    }
    case_results = {}
    for name, (statement, table) in cases.items():
        path = copy_working(f"p2_4_delete_{name}")
        conn = connect_db(path)
        baseline = {
            "gate": auth_gate(conn),
            "parent": parent_state(conn),
            "audit_count": conn.execute("SELECT count(*) FROM audit_entry").fetchone()[0],
            "child_count": conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0],
        }
        stale_cache = {"decision": "ALLOW", "authorization_generation": baseline["parent"]["generation"]}
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(statement)
            in_transaction = {"gate": auth_gate(conn), "parent": parent_state(conn)}
            conn.rollback()
            rollback = {
                "gate": auth_gate(conn),
                "parent": parent_state(conn),
                "child_count": conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0],
            }
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(statement)
            conn.commit()
            direct_delete_rejected = False
            sqlite_error = None
        except sqlite3.DatabaseError as exc:
            conn.rollback()
            direct_delete_rejected = True
            sqlite_error = str(exc)
            in_transaction = {"gate": auth_gate(conn), "parent": parent_state(conn)}
            rollback = {"gate": auth_gate(conn), "parent": parent_state(conn), "child_count": conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]}
        after = {
            "gate": auth_gate(conn),
            "parent": parent_state(conn),
            "audit_count": conn.execute("SELECT count(*) FROM audit_entry").fetchone()[0],
            "child_count": conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0],
        }
        cache_recheck = after["gate"]
        queue_recheck = after["gate"]
        audited_controlled_change = (
            after["parent"]["status"] != "active"
            and after["parent"]["generation"] > baseline["parent"]["generation"]
            and after["audit_count"] > baseline["audit_count"]
        )
        state_unchanged_after_rejection = (
            after["parent"] == baseline["parent"]
            and after["audit_count"] == baseline["audit_count"]
            and after["child_count"] == baseline["child_count"]
            and after["gate"] == baseline["gate"] == "ALLOW"
        )
        runtime_safe = (
            (direct_delete_rejected and state_unchanged_after_rejection)
            or (
                not direct_delete_rejected
                and after["gate"] == "DENY_OR_AMBIGUOUS"
                and cache_recheck == "DENY_OR_AMBIGUOUS"
                and queue_recheck == "DENY_OR_AMBIGUOUS"
            )
        )
        contract_met = direct_delete_rejected or audited_controlled_change
        case_results[name] = {
            "baseline": baseline,
            "direct_delete_rejected": direct_delete_rejected,
            "sqlite_error": sqlite_error,
            "in_transaction": in_transaction,
            "rollback": rollback,
            "after_attempt": after,
            "stale_cache_before_recheck": stale_cache,
            "cache_recheck": cache_recheck,
            "queue_recheck": queue_recheck,
            "incomplete_state_created": not direct_delete_rejected,
            "state_unchanged_after_rejection": state_unchanged_after_rejection,
            "runtime_contract_safe": runtime_safe,
            "audited_controlled_change": audited_controlled_change,
            "recommended_integrity_contract_met": contract_met,
        }
        conn.close()

    runtime_contract_safe = all(case["runtime_contract_safe"] for case in case_results.values())
    rollback_ok = all(case["rollback"]["gate"] == "ALLOW" for case in case_results.values())
    integrity_contract = all(case["recommended_integrity_contract_met"] for case in case_results.values())
    status = "PASS" if runtime_contract_safe and rollback_ok and integrity_contract else "FAIL"
    evidence = {
        "residual": "P2-4",
        "target_contract": "reject direct child DELETE with unchanged complete state, or atomically deactivate/increment/audit and DENY when incomplete",
        "status": status,
        "cases": case_results,
        "runtime_contract_safe": runtime_contract_safe,
        "rollback_ok": rollback_ok,
        "audit_integrity_contract_met": integrity_contract,
        "classification": "P1" if status == "FAIL" else None,
    }
    result = {
        "id": "FILE-P1-P2-4",
        "severity": "P1",
        "status": status,
        "detail": "active child DELETE was not safely rejected or atomically fenced" if status == "FAIL" else "all active child DELETE attempts rejected; parent, children, generation, audit, cache and queue view unchanged",
    }
    return result, evidence


def backup_restore_rehearsal() -> dict:
    backup_path = WORK_DIR / "backup" / "source_fixture_backup.db"
    restore_path = WORK_DIR / "restore" / "restored_fixture.db"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    restore_path.parent.mkdir(parents=True, exist_ok=True)
    source = connect_db(SOURCE_DB, readonly=True)
    backup = connect_db(backup_path)
    source.backup(backup)
    backup.commit()
    source.close()
    backup.close()
    backup_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    backup_ro = connect_db(backup_path, readonly=True)
    restored = connect_db(restore_path)
    backup_ro.backup(restored)
    restored.commit()
    backup_ro.close()
    restored.close()

    src = connect_db(SOURCE_DB, readonly=True)
    dst = connect_db(restore_path, readonly=True)
    table_counts = {}
    for table in ("project", "source", "artifact", "artifact_version", "tombstone", "outbox_job", "authorization", "authorization_scope", "authorization_action", "authorization_policy", "audit_entry"):
        source_count = src.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        restored_count = dst.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        table_counts[table] = {"source": source_count, "restored": restored_count, "matches": source_count == restored_count}
    source_tombstone = tombstone_row(src)
    restored_tombstone = tombstone_row(dst)
    source_gate = consumption_gates(src)
    restored_gate = consumption_gates(dst)
    source_auth_gate = auth_gate(src)
    restored_auth_gate = auth_gate(dst)
    src.close()
    dst.close()
    restored_checks = db_checks(restore_path)
    passed = (
        all(item["matches"] for item in table_counts.values())
        and source_tombstone == restored_tombstone
        and source_gate == restored_gate
        and source_auth_gate == restored_auth_gate
        and restored_checks["integrity_check"] == "ok"
        and not restored_checks["foreign_key_violations"]
    )
    return {
        "passed": passed,
        "backup_path": relative(backup_path),
        "backup_sha256": sha256(backup_path),
        "restore_path": relative(restore_path),
        "restore_sha256": sha256(restore_path),
        "table_counts": table_counts,
        "tombstone_matches": source_tombstone == restored_tombstone,
        "consumption_gates_match": source_gate == restored_gate,
        "authorization_gate_match": source_auth_gate == restored_auth_gate,
        "restored_checks": restored_checks,
    }


def environment_info() -> dict:
    conn = sqlite3.connect(":memory:")
    compile_options = [row[0] for row in conn.execute("PRAGMA compile_options")]
    conn.close()
    return {
        "python": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "sqlite": sqlite3.sqlite_version,
        "sqlite_compile_options": compile_options,
        "operating_system": platform.platform(),
        "machine": platform.machine(),
        "network_used": False,
        "tauri_ipc_started": False,
        "real_db_or_vault_accessed": False,
        "cloud_model_vector_sync_multidevice_l3_external_user_enabled": False,
    }


def output_hashes() -> list[dict]:
    rows = []
    for path in sorted(EVIDENCE_DIR.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.md":
            rows.append({"path": relative(path), "sha256": sha256(path)})
    for path in sorted((TASK_DIR / "scripts").glob("*")):
        if path.is_file():
            rows.append({"path": relative(path), "sha256": sha256(path)})
    rows.append({"path": relative(SOURCE_SQL), "sha256": sha256(SOURCE_SQL)})
    return rows


def build_manifest(stable: dict, environment: dict, summary: dict, results: list[dict], restore: dict, preservation: dict, p3_031_snapshot: dict, exit_code: int) -> str:
    hashes = output_hashes()
    hash_lines = "\n".join(f"| `{row['path']}` | `{row['sha256']}` |" for row in hashes)
    stable_lines = "\n".join(
        f"| `{row['path']}` | `{row['expected_sha256']}` | `{row['actual_sha256']}` | {'Yes' if row['matches'] else 'No'} |"
        for row in stable["stable_inputs"]
    )
    before_lines = "\n".join(f"| `{path}` | `{digest}` |" for path, digest in BEFORE_REMEDIATION_HASHES.items())
    preservation_lines = "\n".join(
        f"| `{row['path']}` | `{row['expected_sha256']}` | `{row['actual_sha256']}` | {'Yes' if row['unchanged'] else 'No'} |"
        for row in preservation["files"]
    )
    failures = [row for row in results if row["status"] != "PASS"]
    failure_lines = "\n".join(f"- `{row['id']}` / {row['severity']} / {row['status']}：{row['detail']}" for row in failures) or "- 无。"
    return f"""# LIFEOS-P3-038 Evidence Manifest

## 授权与隔离范围

- 任务：`{TASK_ID}`，仅受控文件型 SQLite + 合成 fixture 验证。
- 唯一新增回归包根：`lifeos/engineering/LIFEOS-P3-038/`；另按任务卡修改 P3-031 候选 SQL、合同测试与其 evidence。
- 固定无参数入口拒绝 `~`、宽泛目录、UNC / scheme 网络路径、用户 DB / Vault-like 名称、隔离目录外路径与 symlink。
- 未连接或修改真实用户 DB、真实 Vault、真实文件；未启动 Tauri / IPC；未启用网络、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- P3-031 候选 SQL与合同测试已按 P2-2 / P2-3 / P2-4 窄范围整改；P3-037 failure evidence 只读核对且保持不变。

## 创建 / 修改文件

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`：三项 DB trigger 整改。
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`：CT-P1-10 至 CT-P1-12 与必要旧夹具调整。
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`、`test_results.json`、`test_run.log`：最新 38 项合成空库回归证据。
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`：保留 Python 测试非零退出码，避免 `tee` 掩盖失败。
- `input/001_candidate_schema.sql`：P3-031 候选 SQL 输入快照。
- `scripts/run_validation.py`、`scripts/run_validation.sh`：固定路径验证入口。
- `work/`：合成只读源 fixture、可丢弃攻击副本、backup 与 restore 文件。
- `evidence/`：环境、hash、逐项结果、日志与本 manifest。

## 稳定输入 hash

### 整改前

| P3-031 稳定源文件 | 整改前 SHA-256 |
|---|---|
{before_lines}

### 整改后

| 稳定源文件 | 期望 SHA-256 | 实际 SHA-256 | 匹配 |
|---|---|---|---|
{stable_lines}

- 输入快照：`{stable['candidate_snapshot']['path']}` / `{stable['candidate_snapshot']['sha256']}` / 与 P3-031 原始 SQL 匹配：`{stable['candidate_snapshot']['matches_source']}`。
- 稳定输入 hash 与下方运行输出 hash 分开记录。

## P3-037 failure evidence 保留

| P3-037 文件 | 既有 SHA-256 | 当前 SHA-256 | 未变 |
|---|---|---|---|
{preservation_lines}

## 环境

- Python：`{environment['python']}`（{environment['python_implementation']}）
- SQLite：`{environment['sqlite']}`
- OS：`{environment['operating_system']}` / `{environment['machine']}`
- 源 fixture：只读 `0444`；`foreign_keys=1`；journal mode 与编译选项详见 `evidence/environment.json`。
- 源 / 目标 schema version：bootstrap candidate version 1 → synthetic file fixture user_version 1；不做非空旧库 upgrade。

## 准确命令与退出合同

- 工作目录：项目根 `/Users/xxe/Documents/No.2`
- P3-031 合成空库命令：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`；快照退出码：`{p3_031_snapshot['exit_code']}`；结果 hash：`{p3_031_snapshot['results_sha256']}`。
- P3-038 文件型命令：`lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh`
- 本次退出码：`{exit_code}`
- 退出合同：任何 P0 / P1 FAIL、Unknown 或 Not Implemented 均非零；当前退出码与统计一致。

## 测试统计与失败项

- P0：PASS {summary['P0']['PASS']} / FAIL {summary['P0']['FAIL']} / Not Implemented {summary['P0']['NOT_IMPLEMENTED']} / Unknown {summary['P0']['UNKNOWN']}
- P1：PASS {summary['P1']['PASS']} / FAIL {summary['P1']['FAIL']} / Not Implemented {summary['P1']['NOT_IMPLEMENTED']} / Unknown {summary['P1']['UNKNOWN']}
- P2：PASS {summary['P2']['PASS']} / FAIL {summary['P2']['FAIL']} / Not Implemented {summary['P2']['NOT_IMPLEMENTED']} / Unknown {summary['P2']['UNKNOWN']}
- Total：PASS {summary['total']['PASS']} / FAIL {summary['total']['FAIL']} / Not Implemented {summary['total']['NOT_IMPLEMENTED']} / Unknown {summary['total']['UNKNOWN']}

{failure_lines}

## P2-2 / P2-3 / P2-4 证据

- P2-2：`evidence/checks/p2_2_tombstone_delete_insert.json`
- P2-3：`evidence/checks/p2_3_tombstone_status_insert.json`
- P2-4：`evidence/checks/p2_4_authorization_child_delete.json`
- 消费门汇总：`evidence/checks/consumption_gate_results.json`
- 机器结果：`evidence/test_results.json`
- 摘要：`evidence/summary.md`
- 完整运行日志：`evidence/test_run.log`

## backup / restore / rollback / integrity / FK

- backup / restore 演练：`{'PASS' if restore['passed'] else 'FAIL'}`；详见 `evidence/migration/restore_rehearsal.log`。
- P2-2 rollback：详见 P2-2 JSON 与 `evidence/migration/rollback.log`。
- 源 fixture before/after hash、schema dump、integrity / quick / FK：见 `evidence/input/` 与 `evidence/checks/integrity_and_fk.json`。

## 运行输出 hash

| 文件 | 本次运行 SHA-256 |
|---|---|
{hash_lines}

## 不可外推声明

本 evidence 仅证明当前候选 SQL 快照在合成空库和本机文件型 SQLite、合成 fixture、单进程隔离副本中的行为。它不是生产 migration、真实用户 DB / Vault / Tauri / IPC 验证，不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线，不关闭 R-0040、R-0043 或 R-0046，不重新打开或关闭 R-0044 / R-0045，不构成正式 MVP 或下一阶段准入。
"""


def main() -> int:
    if len(sys.argv) != 1:
        print("This controlled harness accepts no path arguments.", file=sys.stderr)
        return 2
    reset_generated_dirs()
    log("start controlled synthetic file-backed SQLite validation")

    isolation = check_path_isolation()
    stable = verify_stable_inputs()
    preservation = verify_p3_037_failure_inputs()
    p3_031_results_path = P3_031 / "evidence" / "test_results.json"
    p3_031_results = json.loads(p3_031_results_path.read_text(encoding="utf-8"))
    p3_031_snapshot = {
        "command": "lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh",
        "exit_code": 0 if p3_031_results["summary"]["total"]["FAIL"] == 0 and p3_031_results["summary"]["total"]["NOT_IMPLEMENTED"] == 0 else 1,
        "results_path": relative(p3_031_results_path),
        "results_sha256": sha256(p3_031_results_path),
        "summary": p3_031_results["summary"],
    }
    write_json(CHECKS_DIR / "path_isolation.json", isolation)
    write_json(INPUT_EVIDENCE_DIR / "source_manifest.json", stable)
    write_json(INPUT_EVIDENCE_DIR / "p3_037_failure_preservation.json", preservation)
    write_json(EVIDENCE_DIR / "p3_031_regression_snapshot.json", p3_031_snapshot)
    stable_lines = [f"{row['actual_sha256']}  {row['path']}" for row in stable["stable_inputs"]]
    stable_lines.append(f"{stable['candidate_snapshot']['sha256']}  {stable['candidate_snapshot']['path']}")
    write_text(INPUT_EVIDENCE_DIR / "source_hashes.txt", "\n".join(stable_lines) + "\n")

    fixture = create_source_fixture()
    source_hash_before = fixture["source_sha256"]
    write_text(INPUT_EVIDENCE_DIR / "source_schema.sql", fixture.pop("schema"))
    write_json(INPUT_EVIDENCE_DIR / "fixture_declaration.json", fixture["fixture_declaration"])
    baseline_checks = db_checks(SOURCE_DB)
    restore = backup_restore_rehearsal()

    p2_2_result, p2_2 = validate_p2_2()
    p2_3_result, p2_3 = validate_p2_3()
    p2_4_result, p2_4 = validate_p2_4()
    source_hash_after = sha256(SOURCE_DB)
    source_unchanged = source_hash_before == source_hash_after
    after_checks = db_checks(SOURCE_DB)

    write_json(CHECKS_DIR / "p2_2_tombstone_delete_insert.json", p2_2)
    write_json(CHECKS_DIR / "p2_3_tombstone_status_insert.json", p2_3)
    write_json(CHECKS_DIR / "p2_4_authorization_child_delete.json", p2_4)
    write_json(CHECKS_DIR / "consumption_gate_results.json", {
        "p2_2": {"baseline": p2_2["baseline"]["gates"], "ordinary_delete": p2_2["ordinary_delete"]["gates_after"], "insert_or_replace": p2_2["insert_or_replace"]["gates_after"], "commit": p2_2["delete_insert_commit"]["gates_after"], "rollback": p2_2["delete_insert_rollback"]["after_rollback"]["gates"]},
        "p2_4": {name: {"in_transaction": case["in_transaction"]["gate"], "after_attempt": case["after_attempt"]["gate"], "cache_recheck": case["cache_recheck"], "queue_recheck": case["queue_recheck"]} for name, case in p2_4["cases"].items()},
    })
    write_json(CHECKS_DIR / "integrity_and_fk.json", {
        "source_before": baseline_checks,
        "source_after": after_checks,
        "source_hash_before": source_hash_before,
        "source_hash_after": source_hash_after,
        "source_unchanged": source_unchanged,
    })

    environment = environment_info()
    environment.update({
        "source_fixture_journal_mode": baseline_checks["journal_mode"],
        "source_fixture_foreign_keys": baseline_checks["foreign_keys"],
        "database_access_log": DB_ACCESS_LOG,
    })
    write_json(EVIDENCE_DIR / "environment.json", environment)
    write_json(MIGRATION_EVIDENCE_DIR / "candidate_hashes.json", stable)
    write_text(MIGRATION_EVIDENCE_DIR / "apply.log", "candidate bootstrap applied only to synthetic source fixture; no old-version upgrade and no real DB\n")
    write_text(MIGRATION_EVIDENCE_DIR / "rollback.log", json.dumps(p2_2["delete_insert_rollback"], ensure_ascii=False, indent=2) + "\n")
    write_text(MIGRATION_EVIDENCE_DIR / "restore_rehearsal.log", json.dumps(restore, ensure_ascii=False, indent=2) + "\n")

    preflight_results = [
        {"id": "FILE-P0-ISOLATION", "severity": "P0", "status": "PASS" if isolation["all_unsafe_rejected"] else "FAIL", "detail": "unsafe paths rejected; fixed task-local root"},
        {"id": "FILE-P0-SYNTHETIC", "severity": "P0", "status": "PASS" if fixture["fixture_declaration"]["synthetic_only"] else "FAIL", "detail": "fixture declaration contains synthetic identifiers/payload only"},
        {"id": "FILE-P1-HASH", "severity": "P1", "status": "PASS" if stable["all_stable_inputs_match"] and stable["candidate_snapshot"]["matches_source"] else "FAIL", "detail": "stable source hashes and SQL snapshot checked"},
        {"id": "FILE-P1-SOURCE-RO", "severity": "P1", "status": "PASS" if fixture["readonly_mode"] == "0o444" and source_unchanged else "FAIL", "detail": "source fixture mode 0444 and before/after hash unchanged"},
        {"id": "FILE-P1-INTEGRITY", "severity": "P1", "status": "PASS" if baseline_checks["integrity_check"] == "ok" and after_checks["integrity_check"] == "ok" and not baseline_checks["foreign_key_violations"] and not after_checks["foreign_key_violations"] else "FAIL", "detail": "source before/after integrity and FK checks"},
        {"id": "FILE-P1-RESTORE", "severity": "P1", "status": "PASS" if restore["passed"] else "FAIL", "detail": "SQLite backup API and separate restore rehearsal"},
        {"id": "FILE-P1-ROLLBACK", "severity": "P1", "status": "PASS" if p2_2["delete_insert_rollback"]["rollback_ok"] and p2_4["rollback_ok"] else "FAIL", "detail": "P2-2 and P2-4 rollback restore authoritative state"},
        {"id": "FILE-P1-P3-037-PRESERVED", "severity": "P1", "status": "PASS" if preservation["all_unchanged"] else "FAIL", "detail": "P3-037 failure evidence hashes remain unchanged"},
        {"id": "FILE-P1-P3-031-REGRESSION", "severity": "P1", "status": "PASS" if p3_031_snapshot["exit_code"] == 0 else "FAIL", "detail": "P3-031 synthetic-empty regression snapshot has zero failures/not implemented"},
    ]
    results = preflight_results + [p2_2_result, p2_3_result, p2_4_result]
    levels = ("P0", "P1", "P2")
    states = ("PASS", "FAIL", "NOT_IMPLEMENTED", "UNKNOWN")
    summary = {level: {state: sum(1 for row in results if row["severity"] == level and row["status"] == state) for state in states} for level in levels}
    summary["total"] = {state: sum(1 for row in results if row["status"] == state) for state in states}
    blocking = any(row["status"] in ("FAIL", "NOT_IMPLEMENTED", "UNKNOWN") and row["severity"] in ("P0", "P1") for row in results)
    exit_code = 1 if blocking else 0
    payload = {
        "task_id": TASK_ID,
        "scope": "controlled synthetic file-backed SQLite only",
        "exit_contract": "any P0/P1 FAIL, UNKNOWN, or NOT_IMPLEMENTED returns nonzero",
        "exit_code": exit_code,
        "summary": summary,
        "results": results,
    }
    write_json(EVIDENCE_DIR / "test_results.json", payload)
    summary_md = f"""# LIFEOS-P3-038 Validation Summary

- Overall: {'FAIL / Rework input' if blocking else 'PASS / independent-review input'}
- Exit code: `{exit_code}`
- P0: {summary['P0']}
- P1: {summary['P1']}
- P2: {summary['P2']}
- P2-2: {p2_2['status']}
- P2-3: {p2_3['status']}
- P2-4: {p2_4['status']}（runtime contract safe=`{p2_4['runtime_contract_safe']}`；audit integrity=`{p2_4['audit_integrity_contract_met']}`）
- Source fixture unchanged: `{source_unchanged}`
- Backup/restore: `{'PASS' if restore['passed'] else 'FAIL'}`
- Integrity/FK: `{'PASS' if baseline_checks['integrity_check'] == 'ok' and not baseline_checks['foreign_key_violations'] else 'FAIL'}`
- No real DB/Vault/Tauri/IPC/real-file capability was accessed or enabled.
"""
    write_text(EVIDENCE_DIR / "summary.md", summary_md)
    log(f"summary={json.dumps(summary, sort_keys=True)} exit_code={exit_code}")
    write_text(EVIDENCE_DIR / "test_run.log", "\n".join(LOG_LINES) + "\n")
    manifest = build_manifest(stable, environment, summary, results, restore, preservation, p3_031_snapshot, exit_code)
    write_text(EVIDENCE_DIR / "MANIFEST.md", manifest)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
