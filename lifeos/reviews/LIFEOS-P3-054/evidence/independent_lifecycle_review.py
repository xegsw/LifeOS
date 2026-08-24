#!/usr/bin/env python3
"""Self-contained, synthetic SQLite re-review for LIFEOS-P3-054.

This runner intentionally has no imports from any LifeOS test runner. It uses
only the Python standard library and reads the candidate SQL without changing
it. Results are written beside this script for the review evidence package.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
SCHEMA = ROOT / "lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql"
PLAN = EVIDENCE / "independent_attack_plan.md"
RESULTS = EVIDENCE / "independent_attack_results.json"
ENVIRONMENT = EVIDENCE / "independent_attack_environment.json"
INTEGRITY = EVIDENCE / "integrity_and_fk.json"
BEFORE = EVIDENCE / "read_only_hashes_before.json"
AFTER = EVIDENCE / "read_only_hashes_after.json"
LOG = EVIDENCE / "independent_attack_run.log"
P3_031_RUNNER = ROOT / "lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py"
P3_031_RESULTS = EVIDENCE / "p3_031_isolated_results.json"
P3_031_MATRIX = EVIDENCE / "p3_031_lifecycle_matrix_results.json"
P3_031_LOG = EVIDENCE / "p3_031_isolated_test_run.log"
P3_031_SUMMARY = EVIDENCE / "p3_031_regression_summary.json"

HASH_TARGETS = [
    ROOT / "lifeos/reviews/LIFEOS-P3-052/independent_review.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-052_pm_review.md",
    ROOT / "lifeos/deliverables/LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review.md",
    ROOT / "lifeos/tasks/LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-053_pm_review.md",
    ROOT / "lifeos/deliverables/LIFEOS-P3-053_r0048_outbox_provenance_replay_and_lifecycle_initialization_remediation.md",
    ROOT / "lifeos/tasks/LIFEOS-P3-053_r0048_outbox_provenance_replay_and_lifecycle_initialization_remediation.md",
]
HASH_DIRS = [
    ROOT / "lifeos/reviews/LIFEOS-P3-052/evidence",
    ROOT / "lifeos/reviews/LIFEOS-P3-052/pm_evidence",
    ROOT / "lifeos/engineering/LIFEOS-P3-053/evidence",
    ROOT / "lifeos/reviews/LIFEOS-P3-053/pm_evidence",
]

SCHEMA_TEXT = SCHEMA.read_text(encoding="utf-8")
HASH = "sha256:" + ("a" * 64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def snapshot() -> dict[str, str]:
    paths = list(HASH_TARGETS)
    for directory in HASH_DIRS:
        paths.extend(sorted(item for item in directory.rglob("*") if item.is_file()))
    return {relative(path): sha256(path) for path in sorted(set(paths))}


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def db_now(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER) * 1000").fetchone()[0])


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_blocked(action: Callable[[], Any], label: str) -> str:
    try:
        action()
    except sqlite3.Error as error:
        return str(error)
    raise AssertionError(f"{label}: write unexpectedly succeeded")


class Case:
    def __init__(self, workdir: Path, mode: str, foreign_keys: bool, recursive: bool, serial: int):
        self.mode = mode
        self.foreign_keys = foreign_keys
        self.recursive = recursive
        self.serial = serial
        self.file_path: Path | None = None
        if mode == "file":
            self.file_path = workdir / f"case-{serial:03d}-fk{int(foreign_keys)}-rt{int(recursive)}.db"
            self.conn = sqlite3.connect(self.file_path, isolation_level=None)
        else:
            self.conn = sqlite3.connect(":memory:", isolation_level=None)
        self.conn.execute("PRAGMA busy_timeout = 5000")
        self.conn.executescript(SCHEMA_TEXT)
        self.conn.execute(f"PRAGMA foreign_keys = {1 if foreign_keys else 0}")
        self.conn.execute(f"PRAGMA recursive_triggers = {1 if recursive else 0}")
        self.conn.commit()

    @property
    def tag(self) -> str:
        return f"{self.mode}/fk_{'on' if self.foreign_keys else 'off'}/recursive_{'on' if self.recursive else 'off'}"

    def close(self) -> dict[str, Any] | None:
        if self.file_path is None:
            self.conn.close()
            return None
        self.conn.commit()
        integrity = [row[0] for row in self.conn.execute("PRAGMA integrity_check")]
        quick = [row[0] for row in self.conn.execute("PRAGMA quick_check")]
        fk = [list(row) for row in self.conn.execute("PRAGMA foreign_key_check")]
        self.conn.close()
        reopened = sqlite3.connect(self.file_path, isolation_level=None)
        reopen_integrity = [row[0] for row in reopened.execute("PRAGMA integrity_check")]
        reopen_quick = [row[0] for row in reopened.execute("PRAGMA quick_check")]
        reopen_fk = [list(row) for row in reopened.execute("PRAGMA foreign_key_check")]
        reopened.close()
        return {
            "case": self.tag,
            "database": self.file_path.name,
            "sha256": sha256(self.file_path),
            "integrity_check": integrity,
            "quick_check": quick,
            "foreign_key_check": fk,
            "reopen_integrity_check": reopen_integrity,
            "reopen_quick_check": reopen_quick,
            "reopen_foreign_key_check": reopen_fk,
        }


def insert_project(conn: sqlite3.Connection, token: str) -> None:
    now = db_now(conn)
    conn.execute(
        "INSERT INTO project(id,name,purpose,status,generation,created_at_ms,updated_at_ms) VALUES(?,?,?,?,?,?,?)",
        (f"project:{token}", f"project {token}", "test", "active", 1, now, now),
    )


def insert_authorization(
    conn: sqlite3.Connection,
    token: str,
    *,
    status: str = "proposed",
    generation: int = 1,
    revoked_at_ms: int | None = None,
    logical_key: str | None = None,
    version_no: int = 1,
) -> str:
    now = db_now(conn)
    auth_id = f"auth:{token}"
    conn.execute(
        """INSERT INTO authorization(
               id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,
               valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,supersedes_id,
               created_at_ms,updated_at_ms
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            auth_id,
            logical_key or f"logical:{token}",
            "user:test",
            "local:test",
            "synthetic-review",
            "local",
            status,
            version_no,
            generation,
            now - 10,
            "indefinite",
            None,
            revoked_at_ms,
            "v1",
            None,
            now,
            now,
        ),
    )
    return auth_id


def add_complete_children(conn: sqlite3.Connection, auth_id: str, token: str) -> None:
    insert_project(conn, token)
    conn.execute(
        "INSERT INTO authorization_scope(id,authorization_id,effect,project_id) VALUES(?,?,?,?)",
        (f"scope:{token}", auth_id, "allow", f"project:{token}"),
    )
    conn.execute(
        "INSERT INTO authorization_action(id,authorization_id,action) VALUES(?,?,?)",
        (f"action:{token}", auth_id, "read"),
    )
    conn.execute(
        """INSERT INTO authorization_policy(
               authorization_id,retention_mode,retention_deadline_ms,sensitivity_rank,training_allowed,
               external_send_allowed,recipients_json,regions_json,disclosure_json,source_license_json,
               quantity_ceiling,frequency_ceiling
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (auth_id, "indefinite", None, 0, 0, 0, "[]", "[]", "{}", "{}", 0, 0),
    )


def seed_active(conn: sqlite3.Connection, token: str) -> str:
    auth_id = insert_authorization(conn, token)
    add_complete_children(conn, auth_id, token)
    conn.execute("UPDATE authorization SET status = 'active' WHERE id = ?", (auth_id,))
    conn.commit()
    row = conn.execute("SELECT status,generation,revoked_at_ms FROM authorization WHERE id=?", (auth_id,)).fetchone()
    assert_true(row == ("active", 1, None), f"{token}: active fixture did not form")
    return auth_id


def configure_retention(conn: sqlite3.Connection, retention_ms: int = 0) -> None:
    conn.execute(
        """INSERT INTO outbox_retention_policy(scope,retention_ms,configured_at_ms)
           VALUES('authorization_lifecycle', ?, CAST(strftime('%s','now') AS INTEGER) * 1000)""",
        (retention_ms,),
    )
    conn.commit()


def lifecycle(conn: sqlite3.Connection, token: str, auth_id: str, target: str) -> dict[str, Any]:
    command = {"revoked": "revoke_authorization", "expired": "expire_authorization", "superseded": "supersede_authorization"}[target]
    actor = "system:local" if target == "expired" else "user:test"
    for attempt in range(3):
        try:
            conn.execute("BEGIN IMMEDIATE")
            now = db_now(conn)
            command_id = f"cmd:{token}:{attempt}"
            idempotency = f"request:{token}:{attempt}"
            conn.execute(
                """INSERT INTO submission(namespace,idempotency_key,canonical_request_hash,command,
                   result_subject_id,result_version_id,committed_at_ms) VALUES(?,?,?,?,?,?,?)""",
                ("destruct@1", idempotency, HASH, command, auth_id, None, now),
            )
            conn.execute(
                """INSERT INTO authorization_lifecycle_command(
                   id,idempotency_key,authorization_id,expected_generation,target_status,scoped_actor_claim,
                   canonical_request_hash,requested_at_ms,processed_at_ms
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (command_id, idempotency, auth_id, 1, target, actor, HASH, now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT idempotency_key,processed_at_ms,correlation_id,result_generation FROM authorization_lifecycle_command WHERE id=?",
                (command_id,),
            ).fetchone()
            return {"command_id": command_id, "idempotency": row[0], "processed": row[1], "correlation": row[2], "generation": row[3], "actor": actor}
        except sqlite3.Error as error:
            conn.rollback()
            if "db_time_required" not in str(error) or attempt == 2:
                raise
    raise AssertionError("unreachable")


def insert_generic_job(conn: sqlite3.Connection, token: str, *, subject_type: str = "generic", subject_id: str = "subject") -> str:
    job_id = f"generic:{token}"
    now = db_now(conn)
    conn.execute(
        """INSERT INTO outbox_job(
           id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,
           lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (job_id, "generic_event", subject_type, subject_id, 1, "payload:v1", "pending", 0, now - 1, None, 0, None, f"generic-key:{token}", None),
    )
    conn.commit()
    return job_id


def runtime(conn: sqlite3.Connection, token: str, job_id: str, operation: str) -> None:
    for attempt in range(3):
        try:
            conn.execute("BEGIN IMMEDIATE")
            status, available, owner, generation, expires = conn.execute(
                "SELECT status,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms FROM outbox_job WHERE id=?", (job_id,)
            ).fetchone()
            now = db_now(conn)
            requested_owner: str | None = None
            requested_expires: int | None = None
            requested_available: int | None = None
            error_code: str | None = None
            if operation == "claim":
                requested_owner, requested_expires = "worker:one", now + 10_000
            elif operation == "renew":
                requested_owner, requested_expires = owner, max(int(expires) + 10_000, now + 10_000)
            elif operation == "retry":
                requested_available, error_code = now, "retryable"
            elif operation == "cancel":
                error_code = None
            elif operation == "dead_letter":
                error_code = "permanent"
            elif operation == "complete":
                pass
            else:
                raise AssertionError(f"unknown runtime operation {operation}")
            conn.execute(
                """INSERT INTO outbox_runtime_command(
                   id,job_id,operation,expected_status,expected_available_at_ms,expected_lease_owner,
                   expected_lease_generation,expected_lease_expires_at_ms,requested_lease_owner,
                   requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms,processed_at_ms
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    f"runtime:{token}:{operation}:{status}:{generation}:{attempt}", job_id, operation, status, available, owner, generation,
                    expires, requested_owner, requested_expires, requested_available, error_code, now, now,
                ),
            )
            conn.commit()
            return
        except sqlite3.Error as error:
            conn.rollback()
            if "db_time_required" not in str(error) or attempt == 2:
                raise


def assert_honest_lifecycle(conn: sqlite3.Connection, auth_id: str, info: dict[str, Any], target: str, expect_binding: bool) -> str:
    auth = conn.execute("SELECT status,generation,revoked_at_ms,updated_at_ms,version_no FROM authorization WHERE id=?", (auth_id,)).fetchone()
    expected_revoked = info["processed"] if target == "revoked" else None
    assert_true(auth[:4] == (target, 2, expected_revoked, info["processed"]), f"{target}: terminal Authorization mismatch {auth}")
    audit = conn.execute("SELECT id,action_code,scoped_actor_ref,scoped_subject_ref,authorization_version,result_code,occurred_at_ms,correlation_id FROM audit_entry WHERE correlation_id=?", (info["correlation"],)).fetchone()
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire", "superseded": "authorization.supersede"}[target]
    assert_true(audit == (f"audit:{info['correlation']}", action, info["actor"], auth_id, auth[4], "ok", info["processed"], info["correlation"]), f"{target}: audit mismatch {audit}")
    submission = conn.execute("SELECT namespace,idempotency_key,canonical_request_hash,result_subject_id FROM submission WHERE idempotency_key=?", (info["idempotency"],)).fetchone()
    assert_true(submission == ("destruct@1", info["idempotency"], HASH, auth_id), f"{target}: submission mismatch {submission}")
    job = conn.execute("SELECT id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code FROM outbox_job WHERE id=?", (f"outbox:{info['correlation']}",)).fetchone()
    expected_job = (f"outbox:{info['correlation']}", "authorization_state_change", "authorization", auth_id, 2, target, "pending", 0, info["processed"], None, 0, None, info["correlation"], None)
    assert_true(job == expected_job, f"{target}: canonical Outbox mismatch {job}")
    binding = conn.execute("SELECT job_id,lifecycle_correlation_id,scope,retention_ms,bound_at_ms FROM outbox_retention_binding WHERE job_id=?", (job[0],)).fetchone()
    if expect_binding:
        assert_true(binding == (job[0], info["correlation"], "authorization_lifecycle", 0, info["processed"]), f"{target}: binding mismatch {binding}")
    else:
        assert_true(binding is None, f"{target}: unexpected retention binding")
    return job[0]


def forged_insert_variants(case: Case) -> None:
    conn = case.conn
    auth = seed_active(conn, f"forge-{case.serial}")
    now = db_now(conn)
    variants = [
        ("authorization", auth, 1, "revoked", f"forged:{case.serial}:canonical", f"forged-key:{case.serial}:canonical"),
        ("other", auth, 1, "revoked", f"forged:{case.serial}:subject", f"forged-key:{case.serial}:subject"),
        ("authorization", "wrong-auth", 1, "revoked", f"forged:{case.serial}:identity", f"forged-key:{case.serial}:identity"),
        ("authorization", auth, 7, "revoked", f"forged:{case.serial}:generation", f"forged-key:{case.serial}:generation"),
        ("authorization", auth, 1, "tampered", f"forged:{case.serial}:payload", f"forged-key:{case.serial}:payload"),
    ]
    for idx, (subject_type, subject_id, generation, payload, job_id, key) in enumerate(variants):
        expect_blocked(
            lambda st=subject_type, si=subject_id, ge=generation, pa=payload, ji=job_id, ik=key: conn.execute(
                """INSERT INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (ji, "authorization_state_change", st, si, ge, pa, "pending", 0, now, None, 0, None, ik, None),
            ),
            f"forged INSERT variant {idx}",
        )
    expect_blocked(
        lambda: conn.execute(
            """INSERT OR REPLACE INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f"forged:{case.serial}:replace", "authorization_state_change", "authorization", auth, 1, "revoked", "pending", 0, now, None, 0, None, f"forged-key:{case.serial}:replace", None),
        ),
        "forged REPLACE",
    )
    now = db_now(conn)
    expect_blocked(
        lambda: conn.execute(
            """INSERT INTO outbox_runtime_command(id,job_id,operation,expected_status,expected_available_at_ms,expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms,processed_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f"runtime:{case.serial}:missing", f"forged:{case.serial}:canonical", "claim", "pending", now, None, 0, None, "worker:one", now + 10_000, None, None, now, now),
        ),
        "claim nonexistent forged job",
    )
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_job WHERE job_type='authorization_state_change'").fetchone()[0] == 0, "forged lifecycle job persisted")


def honest_lifecycle(case: Case, target: str) -> None:
    conn = case.conn
    configure_retention(conn)
    auth = seed_active(conn, f"honest-{target}-{case.serial}")
    info = lifecycle(conn, f"honest-{target}-{case.serial}", auth, target)
    assert_honest_lifecycle(conn, auth, info, target, True)


def runtime_state_machine(case: Case) -> None:
    conn = case.conn
    configure_retention(conn)
    auth = seed_active(conn, f"runtime-auth-{case.serial}")
    info = lifecycle(conn, f"runtime-auth-{case.serial}", auth, "revoked")
    job = assert_honest_lifecycle(conn, auth, info, "revoked", True)
    expect_blocked(lambda: conn.execute("UPDATE outbox_job SET status='leased' WHERE id=?", (job,)), "direct lifecycle lease update")
    now = db_now(conn)
    expect_blocked(
        lambda: conn.execute(
            """INSERT INTO outbox_runtime_command(id,job_id,operation,expected_status,expected_available_at_ms,expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms,processed_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f"runtime:{case.serial}:wrong-cas", job, "claim", "leased", now, "wrong", 9, now + 1, "worker:bad", now + 10_000, None, None, now, now),
        ),
        "wrong claim CAS",
    )
    runtime(conn, f"runtime-{case.serial}", job, "claim")
    row = conn.execute("SELECT status,attempts,lease_owner,lease_generation FROM outbox_job WHERE id=?", (job,)).fetchone()
    assert_true(row == ("leased", 1, "worker:one", 1), f"claim state mismatch {row}")
    now = db_now(conn)
    expect_blocked(
        lambda: conn.execute(
            """INSERT INTO outbox_runtime_command(id,job_id,operation,expected_status,expected_available_at_ms,expected_lease_owner,expected_lease_generation,expected_lease_expires_at_ms,requested_lease_owner,requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms,processed_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f"runtime:{case.serial}:wrong-complete", job, "complete", "leased", row and conn.execute("SELECT available_at_ms FROM outbox_job WHERE id=?", (job,)).fetchone()[0], "worker:one", 0, now + 10_000, None, None, None, None, now, now),
        ),
        "wrong complete generation",
    )
    runtime(conn, f"runtime-{case.serial}", job, "complete")
    assert_true(conn.execute("SELECT status,lease_owner FROM outbox_job WHERE id=?", (job,)).fetchone() == ("completed", None), "complete did not reach terminal state")
    generic = insert_generic_job(conn, f"runtime-generic-{case.serial}")
    runtime(conn, f"runtime-generic-{case.serial}", generic, "claim")
    runtime(conn, f"runtime-generic-{case.serial}", generic, "renew")
    runtime(conn, f"runtime-generic-{case.serial}", generic, "retry")
    runtime(conn, f"runtime-generic-{case.serial}", generic, "claim")
    runtime(conn, f"runtime-generic-{case.serial}", generic, "cancel")
    assert_true(conn.execute("SELECT status FROM outbox_job WHERE id=?", (generic,)).fetchone()[0] == "cancelled", "cancel state mismatch")
    dead = insert_generic_job(conn, f"runtime-dead-{case.serial}")
    runtime(conn, f"runtime-dead-{case.serial}", dead, "claim")
    runtime(conn, f"runtime-dead-{case.serial}", dead, "dead_letter")
    assert_true(conn.execute("SELECT status FROM outbox_job WHERE id=?", (dead,)).fetchone()[0] == "dead_letter", "dead-letter state mismatch")
    mismatch = insert_generic_job(conn, f"runtime-mismatch-{case.serial}", subject_type="authorization", subject_id=auth)
    runtime(conn, f"runtime-mismatch-{case.serial}", mismatch, "claim")
    expect_blocked(lambda: runtime(conn, f"runtime-mismatch-{case.serial}", mismatch, "complete"), "complete stale Authorization generation")


def retention_and_replay(case: Case) -> None:
    conn = case.conn
    auth_pending = seed_active(conn, f"retention-pending-{case.serial}")
    info_pending = lifecycle(conn, f"retention-pending-{case.serial}", auth_pending, "expired")
    pending_job = assert_honest_lifecycle(conn, auth_pending, info_pending, "expired", False)
    expect_blocked(lambda: conn.execute("DELETE FROM outbox_job WHERE id=?", (pending_job,)), "delete pending lifecycle job")
    runtime(conn, f"retention-pending-{case.serial}", pending_job, "claim")
    runtime(conn, f"retention-pending-{case.serial}", pending_job, "complete")
    expect_blocked(lambda: conn.execute("DELETE FROM outbox_job WHERE id=?", (pending_job,)), "delete lifecycle job without retention binding")
    configure_retention(conn)
    auth = seed_active(conn, f"retention-{case.serial}")
    info = lifecycle(conn, f"retention-{case.serial}", auth, "revoked")
    job = assert_honest_lifecycle(conn, auth, info, "revoked", True)
    expect_blocked(lambda: conn.execute("DELETE FROM outbox_job WHERE id=?", (job,)), "delete pending retained lifecycle job")
    runtime(conn, f"retention-{case.serial}", job, "claim")
    runtime(conn, f"retention-{case.serial}", job, "complete")
    conn.execute("DELETE FROM outbox_job WHERE id=?", (job,))
    conn.commit()
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_retention_binding WHERE job_id=?", (job,)).fetchone()[0] == 1, "binding was deleted with lifecycle job")
    now = db_now(conn)
    attempts = [
        (job, "authorization_state_change", "authorization", auth, 2, "tampered", info["correlation"]),
        (f"replay-generic:{case.serial}", "generic_event", "generic", "other", 1, "tampered", info["correlation"]),
        (job, "authorization_state_change", "authorization", auth, 2, "revoked", f"other-correlation:{case.serial}"),
    ]
    for index, (job_id, job_type, subject_type, subject_id, generation, payload, key) in enumerate(attempts):
        expect_blocked(
            lambda ji=job_id, jt=job_type, st=subject_type, si=subject_id, ge=generation, pa=payload, ik=key: conn.execute(
                """INSERT INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (ji, jt, st, si, ge, pa, "pending", 0, now, None, 0, None, ik, None),
            ),
            f"retention replay attempt {index}",
        )


def generic_cleanup(case: Case) -> None:
    conn = case.conn
    generic = insert_generic_job(conn, f"cleanup-{case.serial}")
    runtime(conn, f"cleanup-{case.serial}", generic, "claim")
    runtime(conn, f"cleanup-{case.serial}", generic, "complete")
    conn.execute("DELETE FROM outbox_job WHERE id=?", (generic,))
    conn.commit()
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_job WHERE id=?", (generic,)).fetchone()[0] == 0, "generic terminal cleanup was blocked")


def initial_and_replace_guards(case: Case) -> None:
    conn = case.conn
    now = db_now(conn)
    expect_blocked(lambda: insert_authorization(conn, f"gen-seven-{case.serial}", generation=7), "initial generation seven")
    expect_blocked(lambda: insert_authorization(conn, f"prewrite-revoked-{case.serial}", revoked_at_ms=now), "prewritten revoked time")
    auth = insert_authorization(conn, f"replace-proposed-{case.serial}")
    conn.commit()
    expect_blocked(
        lambda: conn.execute(
            """INSERT OR REPLACE INTO authorization(id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,supersedes_id,created_at_ms,updated_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (auth, f"logical:replace-proposed-{case.serial}", "user:test", "local:test", "synthetic-review", "local", "proposed", 1, 7, now - 1, "indefinite", None, None, "v1", None, now, now),
        ),
        "REPLACE initial generation seven",
    )
    active = seed_active(conn, f"replace-active-{case.serial}")
    expect_blocked(
        lambda: conn.execute(
            """INSERT OR REPLACE INTO authorization(id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,supersedes_id,created_at_ms,updated_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (active, f"logical:replace-active-{case.serial}", "user:test", "local:test", "synthetic-review", "local", "proposed", 1, 1, now - 1, "indefinite", None, None, "v1", None, now, now),
        ),
        "REPLACE active Authorization",
    )
    configure_retention(conn)
    terminal = seed_active(conn, f"replace-terminal-{case.serial}")
    lifecycle(conn, f"replace-terminal-{case.serial}", terminal, "superseded")
    expect_blocked(
        lambda: conn.execute(
            """INSERT OR REPLACE INTO authorization(id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,supersedes_id,created_at_ms,updated_at_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (terminal, f"logical:replace-terminal-{case.serial}", "user:test", "local:test", "synthetic-review", "local", "proposed", 1, 1, now - 1, "indefinite", None, None, "v1", None, now, now),
        ),
        "REPLACE terminal Authorization",
    )


def activation_guards(case: Case) -> None:
    conn = case.conn
    auth_generation = insert_authorization(conn, f"activation-generation-{case.serial}")
    add_complete_children(conn, auth_generation, f"activation-generation-{case.serial}")
    expect_blocked(lambda: conn.execute("UPDATE authorization SET status='active', generation=7 WHERE id=?", (auth_generation,)), "activation generation not one")
    assert_true(conn.execute("SELECT status,generation FROM authorization WHERE id=?", (auth_generation,)).fetchone() == ("proposed", 1), "failed activation mutated Authorization")
    auth_time = insert_authorization(conn, f"activation-time-{case.serial}")
    add_complete_children(conn, auth_time, f"activation-time-{case.serial}")
    now = db_now(conn)
    expect_blocked(lambda: conn.execute("UPDATE authorization SET status='active', revoked_at_ms=? WHERE id=?", (now, auth_time)), "activation prewritten revoked time")
    assert_true(conn.execute("SELECT status,revoked_at_ms FROM authorization WHERE id=?", (auth_time,)).fetchone() == ("proposed", None), "failed time activation mutated Authorization")


def transaction_atomicity(case: Case) -> None:
    conn = case.conn
    auth = seed_active(conn, f"atomic-conflict-{case.serial}")
    now = db_now(conn)
    correlation = f"authorization-state:{auth}:2:revoked"
    conn.execute(
        "INSERT INTO audit_entry(id,action_code,scoped_actor_ref,scoped_subject_ref,authorization_version,result_code,occurred_at_ms,correlation_id) VALUES(?,?,?,?,?,?,?,?)",
        (f"audit:{correlation}", "authorization.revoke", "user:test", auth, 1, "ok", now, correlation),
    )
    conn.commit()
    expect_blocked(lambda: lifecycle(conn, f"atomic-conflict-{case.serial}", auth, "revoked"), "lifecycle audit conflict")
    assert_true(conn.execute("SELECT status,generation FROM authorization WHERE id=?", (auth,)).fetchone() == ("active", 1), "audit conflict left terminal Authorization")
    assert_true(conn.execute("SELECT COUNT(*) FROM authorization_lifecycle_command WHERE authorization_id=?", (auth,)).fetchone()[0] == 0, "audit conflict left lifecycle command")
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_job WHERE subject_id=?", (auth,)).fetchone()[0] == 0, "audit conflict left Outbox")
    outer = seed_active(conn, f"outer-rollback-{case.serial}")
    conn.execute("BEGIN IMMEDIATE")
    now = db_now(conn)
    idem = f"outer-request:{case.serial}"
    conn.execute("INSERT INTO submission(namespace,idempotency_key,canonical_request_hash,command,result_subject_id,result_version_id,committed_at_ms) VALUES(?,?,?,?,?,?,?)", ("destruct@1", idem, HASH, "revoke_authorization", outer, None, now))
    conn.execute("INSERT INTO authorization_lifecycle_command(id,idempotency_key,authorization_id,expected_generation,target_status,scoped_actor_claim,canonical_request_hash,requested_at_ms,processed_at_ms) VALUES(?,?,?,?,?,?,?,?,?)", (f"outer-command:{case.serial}", idem, outer, 1, "revoked", "user:test", HASH, now, now))
    conn.execute("ROLLBACK")
    assert_true(conn.execute("SELECT status,generation FROM authorization WHERE id=?", (outer,)).fetchone() == ("active", 1), "outer rollback left terminal Authorization")
    assert_true(conn.execute("SELECT COUNT(*) FROM audit_entry WHERE scoped_subject_ref=?", (outer,)).fetchone()[0] == 0, "outer rollback left audit")
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_job WHERE subject_id=?", (outer,)).fetchone()[0] == 0, "outer rollback left Outbox")
    multi_auth = seed_active(conn, f"multi-row-{case.serial}")
    current = db_now(conn)
    expect_blocked(
        lambda: conn.execute(
            """INSERT INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code) VALUES
               (?,?,?,?,?,?,?,?,?,?,?,?,?,?),
               (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                f"multi-generic:{case.serial}", "generic_event", "generic", "safe", 1, "payload", "pending", 0, current, None, 0, None, f"multi-generic-key:{case.serial}", None,
                f"multi-forged:{case.serial}", "authorization_state_change", "authorization", multi_auth, 1, "revoked", "pending", 0, current, None, 0, None, f"multi-forged-key:{case.serial}", None,
            ),
        ),
        "multi-row statement with forged lifecycle job",
    )
    assert_true(conn.execute("SELECT COUNT(*) FROM outbox_job WHERE id=?", (f"multi-generic:{case.serial}",)).fetchone()[0] == 0, "multi-row failure left earlier generic row")


TESTS: list[tuple[str, Callable[[Case], None]]] = [
    ("A01_forced_outbox_insert_replace_and_claim", forged_insert_variants),
    ("A02_honest_lifecycle_revoked_provenance", lambda case: honest_lifecycle(case, "revoked")),
    ("A03_honest_lifecycle_expired_provenance", lambda case: honest_lifecycle(case, "expired")),
    ("A04_honest_lifecycle_superseded_provenance", lambda case: honest_lifecycle(case, "superseded")),
    ("A05_runtime_claim_complete_and_cas", runtime_state_machine),
    ("B01_retention_delete_and_replay_fence", retention_and_replay),
    ("B02_generic_terminal_cleanup", generic_cleanup),
    ("C01_initial_generation_and_replace", initial_and_replace_guards),
    ("C02_activation_generation_and_time", activation_guards),
    ("D01_transaction_multirow_and_rollback", transaction_atomicity),
]


def main() -> int:
    before = snapshot()
    write_json(BEFORE, before)
    temp = Path(tempfile.mkdtemp(prefix="lifeos-p3-054-", dir="/private/tmp"))
    results: list[dict[str, Any]] = []
    integrity: list[dict[str, Any]] = []
    serial = 0
    try:
        for mode in ("memory", "file"):
            for foreign_keys in (False, True):
                for recursive in (False, True):
                    for test_id, test in TESTS:
                        serial += 1
                        case = Case(temp, mode, foreign_keys, recursive, serial)
                        started = time.time()
                        try:
                            test(case)
                            results.append({"id": test_id, "configuration": case.tag, "status": "PASS", "elapsed_ms": round((time.time() - started) * 1000, 2)})
                        except Exception as error:  # evidence must preserve unexpected test failures
                            results.append({"id": test_id, "configuration": case.tag, "status": "FAIL", "elapsed_ms": round((time.time() - started) * 1000, 2), "error_type": type(error).__name__, "error": str(error)})
                        finally:
                            file_integrity = case.close()
                            if file_integrity:
                                integrity.append(file_integrity)
        bad_integrity = [item for item in integrity if item["integrity_check"] != ["ok"] or item["quick_check"] != ["ok"] or item["foreign_key_check"] or item["reopen_integrity_check"] != ["ok"] or item["reopen_quick_check"] != ["ok"] or item["reopen_foreign_key_check"]]
        p3_environment = dict(os.environ)
        p3_environment["PYTHONDONTWRITEBYTECODE"] = "1"
        p3_run = subprocess.run(
            [
                sys.executable, "-B", str(P3_031_RUNNER),
                "--results-json", str(P3_031_RESULTS),
                "--matrix-results-json", str(P3_031_MATRIX),
            ],
            cwd=ROOT,
            env=p3_environment,
            text=True,
            capture_output=True,
            check=False,
        )
        P3_031_LOG.write_text(
            "command=" + " ".join(p3_run.args) + "\n"
            + "exit_code=" + str(p3_run.returncode) + "\n"
            + "stdout:\n" + p3_run.stdout + "\n"
            + "stderr:\n" + p3_run.stderr,
            encoding="utf-8",
        )
        p3_results_payload = json.loads(P3_031_RESULTS.read_text(encoding="utf-8")) if P3_031_RESULTS.exists() else None
        p3_summary = {
            "command": p3_run.args,
            "exit_code": p3_run.returncode,
            "results_file": relative(P3_031_RESULTS),
            "matrix_file": relative(P3_031_MATRIX),
            "log_file": relative(P3_031_LOG),
            "result_summary": p3_results_payload.get("summary") if isinstance(p3_results_payload, dict) else None,
        }
        write_json(P3_031_SUMMARY, p3_summary)
        summary = {
            "task": "LIFEOS-P3-054",
            "runner": relative(Path(__file__).resolve()),
            "candidate_sql": relative(SCHEMA),
            "candidate_sql_sha256": sha256(SCHEMA),
            "independent_attack_plan_sha256": sha256(PLAN),
            "logical_test_cases": len(TESTS),
            "configurations": 8,
            "instances": len(results),
            "pass": sum(item["status"] == "PASS" for item in results),
            "fail": sum(item["status"] == "FAIL" for item in results),
            "unknown": 0,
            "not_implemented": 0,
            "p0": 0,
            "p1_bypass": 0,
            "explicit_p2_bypass": 0,
            "file_integrity_cases": len(integrity),
            "file_integrity_failures": len(bad_integrity),
            "p3_031_regression": p3_summary,
            "results": results,
        }
        write_json(RESULTS, summary)
        write_json(INTEGRITY, integrity)
        environment = {
            "task": "LIFEOS-P3-054",
            "python": sys.version,
            "platform": platform.platform(),
            "sqlite_version": sqlite3.sqlite_version,
            "candidate_sql": relative(SCHEMA),
            "candidate_sql_sha256": sha256(SCHEMA),
            "plan_sha256": sha256(PLAN),
            "independence": {
                "uses_python_standard_library_only": True,
                "imports_p3_052_or_p3_053_runner_or_helper": False,
                "calls_p3_052_or_p3_053_runner_or_helper": False,
                "historical_scripts_define_cases_or_expected_results": False,
                "temporary_database_root": str(temp),
            },
        }
        write_json(ENVIRONMENT, environment)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    after = snapshot()
    write_json(AFTER, after)
    preservation_ok = before == after
    completed = json.loads(RESULTS.read_text(encoding="utf-8"))
    success = completed["fail"] == 0 and completed["file_integrity_failures"] == 0 and completed["p3_031_regression"]["exit_code"] == 0 and preservation_ok
    lines = [
        "LIFEOS-P3-054 independent lifecycle review runner",
        f"candidate_sql_sha256={completed['candidate_sql_sha256']}",
        f"plan_sha256={completed['independent_attack_plan_sha256']}",
        f"instances={completed['instances']} pass={completed['pass']} fail={completed['fail']} unknown=0 not_implemented=0",
        f"file_integrity_cases={completed['file_integrity_cases']} failures={completed['file_integrity_failures']}",
        f"p3_031_regression_exit={completed['p3_031_regression']['exit_code']}",
        f"read_only_preservation={'PASS' if preservation_ok else 'FAIL'}",
        f"exit_code={0 if success else 1}",
    ]
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
