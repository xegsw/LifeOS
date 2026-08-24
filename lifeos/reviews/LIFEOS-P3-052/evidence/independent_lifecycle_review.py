#!/usr/bin/env python3
"""P3-052 independent SQLite lifecycle evidence review runner.

This runner was written after the P3-052 plan was sealed.  It loads only the
P3-048 candidate SQL and uses synthetic SQLite databases.  It deliberately
does not import, invoke, or copy the P3-047 runner or either historical attack
helper.  Historical comparison happens in a separate, later review step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class ReviewFailure(Exception):
    pass


class ContractBypass(Exception):
    def __init__(self, message: str, severity: str = "P2") -> None:
        super().__init__(message)
        self.severity = severity


@dataclass(frozen=True)
class Config:
    backend: str
    foreign_keys: bool
    recursive_triggers: bool

    @property
    def label(self) -> str:
        return (
            f"{self.backend}-fk_{'on' if self.foreign_keys else 'off'}"
            f"-rec_{'on' if self.recursive_triggers else 'off'}"
        )


CONFIGS = [
    Config(backend, fk, recursive)
    for backend in ("memory", "file")
    for fk in (False, True)
    for recursive in (False, True)
]


def now_ms(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT CAST(strftime('%s','now') AS INTEGER) * 1000").fetchone()[0])


def count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def row(conn: sqlite3.Connection, sql: str, args: tuple[Any, ...] = ()) -> sqlite3.Row:
    result = conn.execute(sql, args).fetchone()
    if result is None:
        raise ReviewFailure(f"expected row missing: {sql}")
    return result


def require(value: bool, message: str) -> None:
    if not value:
        raise ReviewFailure(message)


def expect_block(action: Callable[[], Any], contains: str | None = None) -> str:
    try:
        action()
    except sqlite3.DatabaseError as exc:
        message = str(exc)
        if contains is not None and contains not in message:
            raise ReviewFailure(f"expected error containing {contains!r}, got {message!r}") from exc
        return message
    raise ContractBypass("statement unexpectedly succeeded")


def hash_text(seed: str) -> str:
    return "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


def command_name(target: str) -> str:
    return {
        "revoked": "revoke_authorization",
        "expired": "expire_authorization",
        "superseded": "supersede_authorization",
    }[target]


def configure(conn: sqlite3.Connection, config: Config) -> None:
    conn.execute(f"PRAGMA foreign_keys = {'ON' if config.foreign_keys else 'OFF'}")
    conn.execute(f"PRAGMA recursive_triggers = {'ON' if config.recursive_triggers else 'OFF'}")


def open_database(schema: str, config: Config, work: Path, case_id: str) -> tuple[sqlite3.Connection, Path | None]:
    db_path: Path | None = None
    if config.backend == "file":
        db_path = work / f"{case_id}_{config.label}.db"
        conn = sqlite3.connect(db_path, isolation_level=None)
    else:
        conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(schema)
    configure(conn, config)
    return conn, db_path


def integrity(conn: sqlite3.Connection, db_path: Path | None, config: Config) -> dict[str, Any]:
    def inspect(open_conn: sqlite3.Connection) -> dict[str, Any]:
        configure(open_conn, config)
        return {
            "integrity_check": [r[0] for r in open_conn.execute("PRAGMA integrity_check")],
            "quick_check": [r[0] for r in open_conn.execute("PRAGMA quick_check")],
            "foreign_key_check": [list(r) for r in open_conn.execute("PRAGMA foreign_key_check")],
        }

    if db_path is None:
        return inspect(conn)
    conn.close()
    reopened = sqlite3.connect(db_path, isolation_level=None)
    try:
        return inspect(reopened)
    finally:
        reopened.close()


def seed_active(
    conn: sqlite3.Connection,
    label: str,
    *,
    generation: int = 1,
    revoked_at_ms: int | None = None,
) -> str:
    project_id = f"project:{label}"
    auth_id = f"auth:{label}"
    base = 1700000000000
    conn.execute(
        "INSERT INTO project(id,name,purpose,status,generation,created_at_ms,updated_at_ms) VALUES (?,?,?,?,?,?,?)",
        (project_id, "Synthetic project", "P3-052 review", "active", 1, base, base),
    )
    conn.execute(
        """INSERT INTO authorization(
          id,logical_key,grantor_ref,processor,purpose,location,status,version_no,generation,
          valid_from_ms,expires_mode,expires_at_ms,revoked_at_ms,policy_version,created_at_ms,updated_at_ms
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            auth_id,
            f"logical:{label}",
            "user:synthetic",
            "local",
            "review",
            "device",
            "proposed",
            1,
            generation,
            base,
            "indefinite",
            None,
            revoked_at_ms,
            "policy@1",
            base,
            base,
        ),
    )
    conn.execute(
        "INSERT INTO authorization_scope(id,authorization_id,effect,project_id) VALUES (?,?,?,?)",
        (f"scope:{label}", auth_id, "allow", project_id),
    )
    conn.execute(
        "INSERT INTO authorization_action(id,authorization_id,action) VALUES (?,?,?)",
        (f"action:{label}", auth_id, "read"),
    )
    conn.execute(
        """INSERT INTO authorization_policy(
          authorization_id,retention_mode,retention_deadline_ms,sensitivity_rank,training_allowed,
          external_send_allowed,recipients_json,regions_json,disclosure_json,source_license_json,
          quantity_ceiling,frequency_ceiling
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (auth_id, "indefinite", None, 1, 0, 0, "[]", "[]", "{}", "{}", 1, 1),
    )
    conn.execute("UPDATE authorization SET status='active' WHERE id=?", (auth_id,))
    return auth_id


def insert_submission(conn: sqlite3.Connection, key: str, auth_id: str, target: str, request_hash: str | None = None) -> str:
    request_hash = request_hash or hash_text(f"{key}:{auth_id}:{target}")
    conn.execute(
        """INSERT INTO submission(namespace,idempotency_key,canonical_request_hash,command,
          result_subject_id,result_version_id,committed_at_ms) VALUES (?,?,?,?,?,?,?)""",
        ("destruct@1", key, request_hash, command_name(target), auth_id, None, now_ms(conn)),
    )
    return request_hash


def insert_lifecycle_command(
    conn: sqlite3.Connection,
    key: str,
    auth_id: str,
    target: str,
    *,
    expected_generation: int = 1,
    request_hash: str | None = None,
) -> None:
    request_hash = request_hash or hash_text(f"{key}:{auth_id}:{target}")
    actor = "system:local" if target == "expired" else "user:synthetic"
    conn.execute(
        """INSERT INTO authorization_lifecycle_command(
          id,idempotency_key,authorization_id,expected_generation,target_status,scoped_actor_claim,
          canonical_request_hash,requested_at_ms
        ) VALUES (?,?,?,?,?,?,?,?)""",
        (f"cmd:{key}", key, auth_id, expected_generation, target, actor, request_hash, now_ms(conn)),
    )


def retire(conn: sqlite3.Connection, auth_id: str, key: str, target: str = "revoked") -> str:
    request_hash = insert_submission(conn, key, auth_id, target)
    insert_lifecycle_command(conn, key, auth_id, target, request_hash=request_hash)
    return f"authorization-state:{auth_id}:2:{target}"


def job_state(conn: sqlite3.Connection, job_id: str) -> sqlite3.Row:
    return row(
        conn,
        """SELECT id,status,attempts,available_at_ms,lease_owner,lease_generation,
           lease_expires_at_ms,last_error_code,job_type,subject_type,subject_id,subject_generation,payload_ref,idempotency_key
           FROM outbox_job WHERE id=?""",
        (job_id,),
    )


def runtime_command(
    conn: sqlite3.Connection,
    job_id: str,
    operation: str,
    *,
    expected: sqlite3.Row | None = None,
    owner: str | None = None,
    lease_expiry: int | None = None,
    available_at: int | None = None,
    error_code: str | None = None,
    suffix: str = "",
) -> None:
    expected = expected or job_state(conn, job_id)
    conn.execute(
        """INSERT INTO outbox_runtime_command(
          id,job_id,operation,expected_status,expected_available_at_ms,expected_lease_owner,
          expected_lease_generation,expected_lease_expires_at_ms,requested_lease_owner,
          requested_lease_expires_at_ms,requested_available_at_ms,error_code,requested_at_ms
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            f"runtime:{job_id}:{operation}:{suffix or now_ms(conn)}",
            job_id,
            operation,
            expected["status"],
            expected["available_at_ms"],
            expected["lease_owner"],
            expected["lease_generation"],
            expected["lease_expires_at_ms"],
            owner,
            lease_expiry,
            available_at,
            error_code,
            now_ms(conn),
        ),
    )


def claim(conn: sqlite3.Connection, job_id: str, owner: str = "worker:one", expiry_delta: int = 60000) -> sqlite3.Row:
    before = job_state(conn, job_id)
    runtime_command(
        conn,
        job_id,
        "claim",
        expected=before,
        owner=owner,
        lease_expiry=now_ms(conn) + expiry_delta,
        suffix=f"claim-{before['lease_generation']}",
    )
    return job_state(conn, job_id)


def insert_lifecycle_outbox(conn: sqlite3.Connection, job_id: str, auth_id: str, generation: int, payload: str, key: str, available_at: int | None = None) -> None:
    conn.execute(
        """INSERT INTO outbox_job(
          id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,
          available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            job_id,
            "authorization_state_change",
            "authorization",
            auth_id,
            generation,
            payload,
            "pending",
            0,
            now_ms(conn) if available_at is None else available_at,
            None,
            0,
            None,
            key,
            None,
        ),
    )


def assert_empty_lifecycle(conn: sqlite3.Connection, auth_id: str) -> None:
    auth = row(conn, "SELECT status,generation,revoked_at_ms FROM authorization WHERE id=?", (auth_id,))
    require(auth["status"] == "active" and auth["generation"] == 1 and auth["revoked_at_ms"] is None, "parent escaped rollback")
    require(count(conn, "authorization_lifecycle_command") == 0, "lifecycle command residue")
    require(count(conn, "submission") == 0, "submission residue")
    require(count(conn, "audit_entry") == 0, "audit residue")
    require(count(conn, "outbox_job") == 0, "outbox residue")


def valid_terminal(target: str) -> Callable[[sqlite3.Connection], dict[str, Any]]:
    def case(conn: sqlite3.Connection) -> dict[str, Any]:
        auth_id = seed_active(conn, f"valid-{target}")
        conn.execute("BEGIN")
        correlation = retire(conn, auth_id, f"valid-{target}", target)
        auth = row(conn, "SELECT status,generation,updated_at_ms,revoked_at_ms,version_no FROM authorization WHERE id=?", (auth_id,))
        audit = row(conn, "SELECT action_code,scoped_subject_ref,authorization_version,result_code,occurred_at_ms,correlation_id FROM audit_entry")
        job = row(conn, "SELECT status,subject_id,subject_generation,payload_ref,idempotency_key FROM outbox_job")
        require(auth["status"] == target and auth["generation"] == 2, "terminal parent not applied")
        require(audit["correlation_id"] == correlation and audit["occurred_at_ms"] == auth["updated_at_ms"], "audit time/correlation mismatch")
        require(audit["authorization_version"] == auth["version_no"] and audit["result_code"] == "ok", "audit binding mismatch")
        require(job["status"] == "pending" and job["subject_id"] == auth_id and job["subject_generation"] == 2, "outbox binding mismatch")
        require(job["payload_ref"] == target and job["idempotency_key"] == correlation, "outbox immutable payload mismatch")
        if target == "revoked":
            require(auth["revoked_at_ms"] == auth["updated_at_ms"], "revoke time not paired")
        else:
            require(auth["revoked_at_ms"] is None, "non-revoked terminal has revoked time")
        conn.execute("COMMIT")
        return {"terminal": target, "correlation": correlation}
    return case


def test_exact_replay(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "replay")
    retire(conn, auth_id, "replay", "revoked")
    before = [count(conn, t) for t in ("submission", "authorization_lifecycle_command", "audit_entry", "outbox_job")]
    # SQLite evaluates multiple BEFORE triggers in an implementation-dependent
    # order.  A duplicate command may therefore be rejected by the active
    # precondition before the explicit replay guard; either error is fail-closed.
    expect_block(lambda: insert_lifecycle_command(conn, "replay", auth_id, "revoked"))
    after = [count(conn, t) for t in ("submission", "authorization_lifecycle_command", "audit_entry", "outbox_job")]
    require(before == after, "replay added evidence")
    return {"counts": after}


def test_submission_mismatch(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "submission-mismatch")
    key = "submission-mismatch"
    conn.execute("BEGIN")
    wrong_hash = hash_text("wrong")
    conn.execute(
        "INSERT INTO submission(namespace,idempotency_key,canonical_request_hash,command,result_subject_id,result_version_id,committed_at_ms) VALUES (?,?,?,?,?,?,?)",
        ("destruct@1", key, wrong_hash, "expire_authorization", auth_id, None, now_ms(conn)),
    )
    expect_block(lambda: insert_lifecycle_command(conn, key, auth_id, "revoked", request_hash=wrong_hash), "submission_binding_required")
    conn.execute("ROLLBACK")
    assert_empty_lifecycle(conn, auth_id)
    return {"binding": "rejected"}


def test_malformed_hash(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "malformed-hash")
    expect_block(
        lambda: conn.execute(
            "INSERT INTO submission(namespace,idempotency_key,canonical_request_hash,command,result_subject_id,result_version_id,committed_at_ms) VALUES (?,?,?,?,?,?,?)",
            ("destruct@1", "bad-hash", "sha256:UPPER", "revoke_authorization", auth_id, None, now_ms(conn)),
        )
    )
    require(count(conn, "submission") == 0, "malformed hash stored")
    return {"malformed_hash": "rejected"}


def test_transaction_rollback(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "rollback")
    conn.execute("BEGIN")
    retire(conn, auth_id, "rollback", "revoked")
    conn.execute("ROLLBACK")
    assert_empty_lifecycle(conn, auth_id)
    return {"rollback": "all evidence surfaces restored"}


def test_later_failure_rollback(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "later-failure")
    conn.execute("BEGIN")
    retire(conn, auth_id, "later-failure", "revoked")
    expect_block(
        lambda: conn.execute(
            "INSERT INTO project(id,name,purpose,status,generation,created_at_ms,updated_at_ms) VALUES (?,?,?,?,?,?,?)",
            ("project:later-failure", "duplicate", "review", "active", 1, 1, 1),
        )
    )
    conn.execute("ROLLBACK")
    assert_empty_lifecycle(conn, auth_id)
    return {"caller_rollback": "all evidence surfaces restored"}


def test_savepoint_rollback(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "savepoint")
    conn.execute("BEGIN")
    conn.execute("SAVEPOINT lifecycle")
    retire(conn, auth_id, "savepoint", "revoked")
    conn.execute("ROLLBACK TO lifecycle")
    conn.execute("RELEASE lifecycle")
    conn.execute("COMMIT")
    assert_empty_lifecycle(conn, auth_id)
    return {"savepoint": "all evidence surfaces restored"}


def test_audit_preplacement(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "audit-preplace")
    correlation = f"authorization-state:{auth_id}:2:revoked"
    conn.execute(
        "INSERT INTO audit_entry(id,action_code,scoped_actor_ref,scoped_subject_ref,authorization_version,result_code,occurred_at_ms,correlation_id) VALUES (?,?,?,?,?,?,?,?)",
        (f"audit:{correlation}", "authorization.revoke", "fake", auth_id, 1, "ok", now_ms(conn), correlation),
    )
    conn.execute("BEGIN")
    request_hash = insert_submission(conn, "audit-preplace", auth_id, "revoked")
    expect_block(lambda: insert_lifecycle_command(conn, "audit-preplace", auth_id, "revoked", request_hash=request_hash))
    conn.execute("ROLLBACK")
    auth = row(conn, "SELECT status,generation FROM authorization WHERE id=?", (auth_id,))
    require(auth["status"] == "active" and auth["generation"] == 1, "audit preplacement retired parent")
    require(count(conn, "audit_entry") == 1 and count(conn, "outbox_job") == 0 and count(conn, "submission") == 0, "preplacement rollback residue wrong")
    return {"preplaced_audit": "blocked retirement and preserved active parent"}


def test_outbox_preplacement(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "outbox-preplace")
    correlation = f"authorization-state:{auth_id}:2:revoked"
    insert_lifecycle_outbox(conn, f"outbox:{correlation}", auth_id, 2, "revoked", correlation)
    conn.execute("BEGIN")
    request_hash = insert_submission(conn, "outbox-preplace", auth_id, "revoked")
    expect_block(lambda: insert_lifecycle_command(conn, "outbox-preplace", auth_id, "revoked", request_hash=request_hash))
    conn.execute("ROLLBACK")
    auth = row(conn, "SELECT status,generation FROM authorization WHERE id=?", (auth_id,))
    require(auth["status"] == "active" and auth["generation"] == 1, "outbox preplacement retired parent")
    require(count(conn, "outbox_job") == 1 and count(conn, "submission") == 0 and count(conn, "audit_entry") == 0, "preplacement rollback residue wrong")
    return {"preplaced_outbox": "blocked retirement and preserved active parent"}


def test_append_only_and_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "append-only")
    correlation = retire(conn, auth_id, "append-only", "revoked")
    job_id = f"outbox:{correlation}"
    checks = [
        lambda: conn.execute("UPDATE audit_entry SET result_code='bad'"),
        lambda: conn.execute("DELETE FROM audit_entry"),
        lambda: conn.execute("INSERT OR REPLACE INTO audit_entry SELECT * FROM audit_entry"),
        lambda: conn.execute("UPDATE submission SET command='expire_authorization'"),
        lambda: conn.execute("DELETE FROM submission"),
        lambda: conn.execute("UPDATE authorization_lifecycle_command SET target_status='expired'"),
        lambda: conn.execute("DELETE FROM authorization_lifecycle_command"),
        lambda: conn.execute("UPDATE outbox_job SET payload_ref='forged' WHERE id=?", (job_id,)),
        lambda: conn.execute("UPDATE outbox_job SET subject_id='other' WHERE id=?", (job_id,)),
        lambda: conn.execute("UPDATE outbox_job SET idempotency_key='forged' WHERE id=?", (job_id,)),
        lambda: conn.execute("INSERT OR REPLACE INTO outbox_job SELECT * FROM outbox_job WHERE id=?", (job_id,)),
    ]
    for check in checks:
        expect_block(check)
    current = job_state(conn, job_id)
    require(current["payload_ref"] == "revoked" and current["subject_id"] == auth_id, "immutable outbox changed")
    return {"append_only_checks": len(checks)}


def test_direct_lifecycle_and_times(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "direct-lifecycle")
    current = row(conn, "SELECT created_at_ms,updated_at_ms FROM authorization WHERE id=?", (auth_id,))
    stamp = now_ms(conn)
    expect_block(
        lambda: conn.execute(
            "UPDATE authorization SET status='revoked',generation=2,revoked_at_ms=?,updated_at_ms=? WHERE id=?",
            (stamp, stamp, auth_id),
        )
    )
    expect_block(lambda: conn.execute("UPDATE authorization SET generation=2 WHERE id=?", (auth_id,)))
    expect_block(lambda: conn.execute("UPDATE authorization SET generation=9 WHERE id=?", (auth_id,)))
    expect_block(lambda: conn.execute("UPDATE authorization SET created_at_ms=? WHERE id=?", (current["created_at_ms"] + 1, auth_id)))
    expect_block(lambda: conn.execute("UPDATE authorization SET revoked_at_ms=? WHERE id=?", (stamp, auth_id)))
    auth = row(conn, "SELECT status,generation,created_at_ms,revoked_at_ms FROM authorization WHERE id=?", (auth_id,))
    require(auth["status"] == "active" and auth["generation"] == 1 and auth["created_at_ms"] == current["created_at_ms"] and auth["revoked_at_ms"] is None, "direct mutation changed parent")
    return {"direct_lifecycle": "rejected"}


def test_initial_generation_contract(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "initial-generation", generation=7)
    auth = row(conn, "SELECT status,generation FROM authorization WHERE id=?", (auth_id,))
    if auth["status"] == "active" and auth["generation"] == 7:
        raise ContractBypass("new Authorization can become active at generation 7; contract requires generation=1", "P2")
    return {"initial_generation": "enforced"}


def test_initial_revoked_time_contract(conn: sqlite3.Connection) -> dict[str, Any]:
    preset = 1700000000999
    auth_id = seed_active(conn, "initial-revoked-time", revoked_at_ms=preset)
    auth = row(conn, "SELECT status,revoked_at_ms FROM authorization WHERE id=?", (auth_id,))
    if auth["status"] == "active" and auth["revoked_at_ms"] == preset:
        raise ContractBypass("Authorization can become active with a prewritten revoked_at_ms; non-revoked states must have NULL", "P2")
    return {"initial_revoked_time": "enforced"}


def test_false_lifecycle_outbox_injection(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "false-outbox")
    job_id = "outbox:forged-active-revoke"
    insert_lifecycle_outbox(conn, job_id, auth_id, 1, "revoked", "forged-correlation")
    claimed = claim(conn, job_id, "worker:forged")
    runtime_command(conn, job_id, "complete", expected=claimed, suffix="forged-complete")
    auth = row(conn, "SELECT status,generation FROM authorization WHERE id=?", (auth_id,))
    job = job_state(conn, job_id)
    if job["status"] == "completed" and auth["status"] == "active" and auth["generation"] == 1:
        raise ContractBypass("forged lifecycle Outbox job can complete against an active Authorization without lifecycle command/audit", "P1")
    return {"forged_outbox": "blocked"}


def test_future_claim_and_cas(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "future-cas")
    job_id = "outbox:future-cas"
    future = now_ms(conn) + 60000
    insert_lifecycle_outbox(conn, job_id, auth_id, 1, "revoked", "future-cas-key", future)
    before = job_state(conn, job_id)
    expect_block(lambda: claim(conn, job_id, "worker:early"))
    require(job_state(conn, job_id)["status"] == "pending", "future job was leased")
    # Make the same synthetic job immediately available via a fresh fixture, then test stale full-state CAS.
    available_id = "outbox:cas"
    insert_lifecycle_outbox(conn, available_id, auth_id, 1, "revoked", "cas-key")
    leased = claim(conn, available_id, "worker:one")
    stale_owner = dict(leased)
    stale_owner["lease_owner"] = "worker:two"
    expect_block(
        lambda: runtime_command(
            conn,
            available_id,
            "complete",
            expected=stale_owner,  # type: ignore[arg-type]
            suffix="wrong-owner",
        )
    )
    stale_generation = dict(leased)
    stale_generation["lease_generation"] = 0
    expect_block(
        lambda: runtime_command(
            conn,
            available_id,
            "complete",
            expected=stale_generation,  # type: ignore[arg-type]
            suffix="wrong-generation",
        )
    )
    require(job_state(conn, available_id)["status"] == "leased", "stale CAS mutated job")
    return {"future_claim": "rejected", "stale_cas": "rejected", "future_available_at_ms": before["available_at_ms"]}


def test_retry_and_terminal_paths(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "retry-terminal")
    retry_id = "outbox:retry"
    insert_lifecycle_outbox(conn, retry_id, auth_id, 1, "revoked", "retry-key")
    leased = claim(conn, retry_id)
    future = now_ms(conn) + 60000
    runtime_command(conn, retry_id, "retry", expected=leased, available_at=future, error_code="synthetic_failure", suffix="retry")
    retried = job_state(conn, retry_id)
    require(retried["status"] == "pending" and retried["lease_owner"] is None and retried["available_at_ms"] == future, "retry state incorrect")
    require(retried["attempts"] == 1 and retried["payload_ref"] == "revoked", "retry altered attempts/payload unexpectedly")
    expect_block(lambda: claim(conn, retry_id, "worker:early"))

    complete_id = "outbox:complete"
    insert_lifecycle_outbox(conn, complete_id, auth_id, 1, "revoked", "complete-key")
    complete_lease = claim(conn, complete_id)
    runtime_command(conn, complete_id, "complete", expected=complete_lease, suffix="complete")
    require(job_state(conn, complete_id)["status"] == "completed", "complete not applied")

    cancel_id = "outbox:cancel"
    insert_lifecycle_outbox(conn, cancel_id, auth_id, 1, "revoked", "cancel-key")
    cancel_pending = job_state(conn, cancel_id)
    runtime_command(conn, cancel_id, "cancel", expected=cancel_pending, suffix="cancel")
    require(job_state(conn, cancel_id)["status"] == "cancelled", "cancel not applied")

    dead_id = "outbox:dead"
    insert_lifecycle_outbox(conn, dead_id, auth_id, 1, "revoked", "dead-key")
    dead_lease = claim(conn, dead_id)
    runtime_command(conn, dead_id, "dead_letter", expected=dead_lease, error_code="synthetic_dead", suffix="dead")
    require(job_state(conn, dead_id)["status"] == "dead_letter", "dead letter not applied")

    for job_id in (complete_id, cancel_id, dead_id):
        expect_block(lambda job_id=job_id: conn.execute("UPDATE outbox_job SET status='pending' WHERE id=?", (job_id,)))
    return {"retry": "payload preserved", "terminal_paths": ["completed", "cancelled", "dead_letter"]}


def test_expired_lease(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "expired-lease")
    job_id = "outbox:expired"
    insert_lifecycle_outbox(conn, job_id, auth_id, 1, "revoked", "expired-key")
    leased = claim(conn, job_id, expiry_delta=1)
    deadline = int(leased["lease_expires_at_ms"])
    while now_ms(conn) <= deadline:
        time.sleep(0.02)
    expired = job_state(conn, job_id)
    expect_block(lambda: runtime_command(conn, job_id, "complete", expected=expired, suffix="expired-complete"))
    expect_block(
        lambda: runtime_command(
            conn,
            job_id,
            "renew",
            expected=expired,
            owner=expired["lease_owner"],
            lease_expiry=now_ms(conn) + 60000,
            suffix="expired-renew",
        )
    )
    require(job_state(conn, job_id)["status"] == "leased", "expired operation mutated job")
    return {"expired_complete_and_renew": "rejected"}


def test_retention_cleanup_and_replay(conn: sqlite3.Connection) -> dict[str, Any]:
    conn.execute("INSERT INTO outbox_retention_policy(scope,retention_ms) VALUES ('authorization_lifecycle',0)")
    auth_id = seed_active(conn, "retention-replay")
    correlation = retire(conn, auth_id, "retention-replay", "revoked")
    job_id = f"outbox:{correlation}"
    lease = claim(conn, job_id)
    runtime_command(conn, job_id, "complete", expected=lease, suffix="complete-before-delete")
    conn.execute("DELETE FROM outbox_job WHERE id=?", (job_id,))
    require(count(conn, "outbox_job") == 0, "retention cleanup did not remove terminal lifecycle job")
    # The immutable retention binding remains. Re-using its deleted job identity
    # must not recreate a lifecycle dispatch with altered payload.
    try:
        insert_lifecycle_outbox(conn, job_id, auth_id, 2, "forged-after-retention", correlation)
    except sqlite3.DatabaseError:
        return {"retention_cleanup": "allowed", "post_cleanup_replay": "blocked"}
    recreated = job_state(conn, job_id)
    raise ContractBypass(
        "deleted lifecycle Outbox identity/idempotency can be reinserted after retention cleanup despite preserved binding; payload replay is possible",
        "P1",
    )


def test_generic_cleanup_scope(conn: sqlite3.Connection) -> dict[str, Any]:
    conn.execute(
        """INSERT INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,
          available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("generic:terminal", "generic", "artifact", "artifact:1", 1, "payload", "pending", 0, now_ms(conn), None, 0, None, "generic-key", None),
    )
    generic_lease = claim(conn, "generic:terminal")
    runtime_command(conn, "generic:terminal", "complete", expected=generic_lease, suffix="generic-complete")
    conn.execute("DELETE FROM outbox_job WHERE id='generic:terminal'")
    require(count(conn, "outbox_job") == 0, "generic terminal cleanup blocked")
    conn.execute(
        """INSERT INTO outbox_job(id,job_type,subject_type,subject_id,subject_generation,payload_ref,status,attempts,
          available_at_ms,lease_owner,lease_generation,lease_expires_at_ms,idempotency_key,last_error_code)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("generic:pending", "generic", "artifact", "artifact:2", 1, "payload", "pending", 0, now_ms(conn), None, 0, None, "generic-pending-key", None),
    )
    expect_block(lambda: conn.execute("DELETE FROM outbox_job WHERE id='generic:pending'"))
    return {"generic_terminal_cleanup": "allowed", "generic_pending_cleanup": "blocked"}


def test_pm_ce04_tombstone_envelope(conn: sqlite3.Connection) -> dict[str, Any]:
    auth_id = seed_active(conn, "pm-ce04")
    retire(conn, auth_id, "pm-ce04", "revoked")
    cleanup_correlation = f"authorization-cleanup:{auth_id}:2"
    conn.execute(
        """INSERT INTO audit_entry(
          id,action_code,scoped_actor_ref,scoped_subject_ref,authorization_version,result_code,occurred_at_ms,correlation_id
        ) VALUES (?,?,?,?,?,?,?,?)""",
        ("audit:cleanup:pm-ce04", "authorization.cleanup", "user:synthetic", auth_id, 1, "redacted_by_user", now_ms(conn), cleanup_correlation),
    )
    conn.execute(
        """INSERT INTO tombstone(subject_type,subject_id,generation,command_id,reason_code,blocked_at_ms,cleanup_status,updated_at_ms)
           VALUES (?,?,?,?,?,?,?,?)""",
        ("authorization", auth_id, 2, "cleanup:pm-ce04", "user_cleanup", now_ms(conn), "accepted", now_ms(conn)),
    )
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked',updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (auth_id,))
    conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending',updated_at_ms=updated_at_ms+1 WHERE subject_type='authorization' AND subject_id=?", (auth_id,))
    expect_block(
        lambda: conn.execute(
            """UPDATE tombstone SET subject_id='forged',generation=9,command_id='forged',
               reason_code='forged',blocked_at_ms=0 WHERE subject_type='authorization' AND subject_id=?""",
            (auth_id,),
        )
    )
    current = row(conn, "SELECT subject_id,generation,command_id,reason_code FROM tombstone WHERE subject_type='authorization'")
    require(current["subject_id"] == auth_id and current["generation"] == 2 and current["command_id"] == "cleanup:pm-ce04", "tombstone envelope changed")
    return {"pm_ce_04": "control envelope immutable"}


def test_multirow_atomicity(conn: sqlite3.Connection) -> dict[str, Any]:
    first = seed_active(conn, "multirow-one")
    second = seed_active(conn, "multirow-two")
    before = [dict(row(conn, "SELECT id,status,generation,created_at_ms FROM authorization WHERE id=?", (auth_id,))) for auth_id in (first, second)]
    expect_block(
        lambda: conn.execute(
            "UPDATE authorization SET created_at_ms=created_at_ms+1 WHERE id IN (?,?)",
            (first, second),
        )
    )
    after = [dict(row(conn, "SELECT id,status,generation,created_at_ms FROM authorization WHERE id=?", (auth_id,))) for auth_id in (first, second)]
    require(before == after, "multirow rejected statement partially changed rows")
    return {"multirow": "atomic rejection"}


Case = tuple[str, str, Callable[[sqlite3.Connection], dict[str, Any]]]
CASES: list[Case] = [
    ("A01-valid-revoke", "P1", valid_terminal("revoked")),
    ("A01-valid-expire", "P1", valid_terminal("expired")),
    ("A01-valid-supersede", "P1", valid_terminal("superseded")),
    ("A02-exact-replay", "P2", test_exact_replay),
    ("A03-submission-binding", "P2", test_submission_mismatch),
    ("A06-malformed-hash", "P2", test_malformed_hash),
    ("A04-transaction-rollback", "P1", test_transaction_rollback),
    ("A04-later-failure-rollback", "P1", test_later_failure_rollback),
    ("A04-savepoint-rollback", "P1", test_savepoint_rollback),
    ("B03-audit-preplacement", "P2", test_audit_preplacement),
    ("B03-outbox-preplacement", "P2", test_outbox_preplacement),
    ("B02-C01-append-only-payload", "P2", test_append_only_and_payload),
    ("D02-direct-lifecycle-and-times", "P2", test_direct_lifecycle_and_times),
    ("D01-initial-generation", "P2", test_initial_generation_contract),
    ("D01-initial-revoked-time", "P2", test_initial_revoked_time_contract),
    ("C01-forged-lifecycle-outbox", "P1", test_false_lifecycle_outbox_injection),
    ("C02-C04-future-and-cas", "P1", test_future_claim_and_cas),
    ("C04-C06-retry-and-terminal", "P1", test_retry_and_terminal_paths),
    ("C04-expired-lease", "P1", test_expired_lease),
    ("C08-C09-retention-and-replay", "P1", test_retention_cleanup_and_replay),
    ("C09-generic-cleanup-scope", "P2", test_generic_cleanup_scope),
    ("PM-CE-04-tombstone-envelope", "P2", test_pm_ce04_tombstone_envelope),
    ("D03-multirow-atomicity", "P2", test_multirow_atomicity),
]


def run(schema: str, work: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    integrity_results: list[dict[str, Any]] = []
    for case_id, severity, case in CASES:
        for config in CONFIGS:
            conn: sqlite3.Connection | None = None
            db_path: Path | None = None
            result: dict[str, Any] = {"case": case_id, "severity": severity, "config": config.label}
            try:
                conn, db_path = open_database(schema, config, work, case_id)
                details = case(conn)
                result.update({"outcome": "PASS", "details": details})
            except ContractBypass as exc:
                result.update({"outcome": "BYPASS", "severity": exc.severity, "message": str(exc)})
            except (ReviewFailure, sqlite3.DatabaseError, AssertionError) as exc:
                result.update({"outcome": "FAIL", "message": str(exc)})
            except Exception as exc:  # pragma: no cover - review evidence must show unexpected errors.
                result.update({"outcome": "UNKNOWN", "message": f"{type(exc).__name__}: {exc}"})
            finally:
                if conn is not None:
                    try:
                        check = integrity(conn, db_path, config)
                        integrity_results.append({"case": case_id, "config": config.label, **check})
                        if check["integrity_check"] != ["ok"] or check["quick_check"] != ["ok"] or check["foreign_key_check"]:
                            if result.get("outcome") == "PASS":
                                result.update({"outcome": "FAIL", "message": "integrity or FK check failed"})
                    except Exception as exc:
                        integrity_results.append({"case": case_id, "config": config.label, "inspection_error": str(exc)})
                        if result.get("outcome") == "PASS":
                            result.update({"outcome": "FAIL", "message": f"integrity inspection error: {exc}"})
                    finally:
                        try:
                            conn.close()
                        except sqlite3.DatabaseError:
                            pass
            results.append(result)
    return results, integrity_results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    schema = args.candidate.read_text(encoding="utf-8")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-052-") as temp_dir:
        results, checks = run(schema, Path(temp_dir))
    summary = {outcome: sum(1 for result in results if result["outcome"] == outcome) for outcome in ("PASS", "BYPASS", "FAIL", "UNKNOWN")}
    bypasses = [result for result in results if result["outcome"] == "BYPASS"]
    payload = {
        "runner": "P3-052 independent_lifecycle_review.py",
        "candidate": str(args.candidate),
        "candidate_sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        "configuration_count": len(CONFIGS),
        "case_count": len(CASES),
        "summary": summary,
        "bypasses": bypasses,
        "results": results,
    }
    (args.evidence_dir / "independent_attack_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.evidence_dir / "integrity_and_fk.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.evidence_dir / "independent_attack_environment.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "sqlite": sqlite3.sqlite_version,
                "platform": sys.platform,
                "configurations": [config.label for config in CONFIGS],
                "independence": "No P3-047 runner or historical attack helper imported or executed.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    log_lines = [
        f"summary: {summary}",
        *[
            f"{result['outcome']} {result['config']} {result['case']} {result.get('message', '')}".rstrip()
            for result in results
        ],
    ]
    (args.evidence_dir / "independent_attack_run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0 if summary["BYPASS"] == summary["FAIL"] == summary["UNKNOWN"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
