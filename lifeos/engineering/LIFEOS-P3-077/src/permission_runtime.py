"""Task-local, synthetic-only permission settings runtime for LIFEOS-P3-077.

This module intentionally has no network, file-export, AI, or external-action
integration.  Its only persistence target is a caller-supplied SQLite database.
"""
from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any


BOUNDARY = {
    "project": "project-synthetic-077",
    "category": "non_sensitive_test_text",
    "purpose": "local_permission_settings_demo",
    "location": "task_local_sqlite",
    "processor": "local_synthetic_runtime",
    "external_action": "none",
    "ai_consumption": "disabled",
}


class PermissionRuntime:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_db()

    def close(self) -> None:
        self.conn.close()

    def _init_db(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS permissions (
              id TEXT PRIMARY KEY, decision TEXT NOT NULL,
              project TEXT NOT NULL, category TEXT NOT NULL, purpose TEXT NOT NULL,
              location TEXT NOT NULL, processor TEXT NOT NULL,
              expires_at_ms INTEGER NOT NULL, status TEXT NOT NULL,
              confirmation TEXT NOT NULL, idempotency_key TEXT UNIQUE NOT NULL,
              created_at_ms INTEGER NOT NULL, revoked_at_ms INTEGER
            );
            CREATE TABLE IF NOT EXISTS audits (
              id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
              permission_id TEXT, reason TEXT NOT NULL, confirmation TEXT,
              idempotency_key TEXT, created_at_ms INTEGER NOT NULL,
              FOREIGN KEY(permission_id) REFERENCES permissions(id)
            );
            """
        )
        self.conn.commit()

    @staticmethod
    def _now() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def _valid_context(context: dict[str, str]) -> bool:
        return all(context.get(k) == BOUNDARY[k] for k in ("project", "category", "purpose", "location", "processor"))

    def preview(self) -> dict[str, Any]:
        return {"default_decision": "deny", "boundary": BOUNDARY.copy(), "confirm_token": "CONFIRM"}

    def _audit(self, event: str, reason: str, permission_id: str | None = None,
               confirmation: str | None = None, idempotency_key: str | None = None) -> None:
        self.conn.execute(
            "INSERT INTO audits(event, permission_id, reason, confirmation, idempotency_key, created_at_ms) VALUES (?, ?, ?, ?, ?, ?)",
            (event, permission_id, reason, confirmation, idempotency_key, self._now()),
        )

    def set_decision(self, decision: str, context: dict[str, str], expires_at_ms: int,
                     confirmation: str, idempotency_key: str) -> dict[str, Any]:
        if decision not in {"grant", "deny"} or not self._valid_context(context) or expires_at_ms <= self._now() or confirmation != "CONFIRM" or not idempotency_key:
            self._audit("rejected", "invalid_request", confirmation=confirmation, idempotency_key=idempotency_key)
            self.conn.commit()
            return {"ok": False, "reason": "invalid_request", "external_action": "none"}
        existing = self.conn.execute("SELECT * FROM permissions WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        if existing:
            stored_decision = "granted" if decision == "grant" else "denied"
            same = existing["decision"] == stored_decision and all(existing[k] == context[k] for k in context) and existing["expires_at_ms"] == expires_at_ms
            reason = "idempotent_repeat" if same else "idempotency_conflict"
            self._audit("decision_replayed" if same else "rejected", reason, existing["id"], confirmation, idempotency_key)
            self.conn.commit()
            return {"ok": same, "permission_id": existing["id"], "reason": reason, "external_action": "none"}
        permission_id = f"perm-{uuid.uuid4()}"
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO permissions VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'current', ?, ?, ?, NULL)",
                    (permission_id, "granted" if decision == "grant" else "denied", *(context[k] for k in ("project", "category", "purpose", "location", "processor")), expires_at_ms, confirmation, idempotency_key, self._now()),
                )
                self._audit("decision_set", decision, permission_id, confirmation, idempotency_key)
        except sqlite3.Error:
            return {"ok": False, "reason": "atomic_write_failed", "external_action": "none"}
        return {"ok": True, "permission_id": permission_id, "reason": f"{decision}_recorded", "external_action": "none"}

    def revoke(self, permission_id: str, confirmation: str, idempotency_key: str) -> dict[str, Any]:
        row = self.conn.execute("SELECT * FROM permissions WHERE id = ?", (permission_id,)).fetchone()
        if confirmation != "REVOKE" or not idempotency_key or not row:
            self._audit("rejected", "invalid_revoke", permission_id, confirmation, idempotency_key)
            self.conn.commit()
            return {"ok": False, "reason": "invalid_revoke", "external_action": "none"}
        prior = self.conn.execute("SELECT * FROM audits WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        if prior:
            same = prior["permission_id"] == permission_id and prior["event"] == "revoked"
            return {"ok": same, "permission_id": permission_id, "reason": "idempotent_repeat" if same else "idempotency_conflict", "external_action": "none"}
        if row["status"] != "current":
            self._audit("rejected", "not_current", permission_id, confirmation, idempotency_key)
            self.conn.commit()
            return {"ok": False, "reason": "not_current", "external_action": "none"}
        with self.conn:
            self.conn.execute("UPDATE permissions SET status = 'revoked', revoked_at_ms = ? WHERE id = ?", (self._now(), permission_id))
            self._audit("revoked", "operator_revoked", permission_id, confirmation, idempotency_key)
        return {"ok": True, "permission_id": permission_id, "reason": "revoked", "external_action": "none"}

    def consume(self, context: dict[str, str], confirmation: str) -> dict[str, Any]:
        if confirmation != "CONFIRM" or not self._valid_context(context):
            reason = "confirmation_required" if confirmation != "CONFIRM" else "invalid_context"
            self._audit("rejected", reason, confirmation=confirmation)
            self.conn.commit()
            return {"allowed": False, "reason": reason, "external_action": "none", "ai_consumption": "none"}
        now = self._now()
        rows = self.conn.execute(
            "SELECT * FROM permissions WHERE status = 'current' AND expires_at_ms > ? AND project=? AND category=? AND purpose=? AND location=? AND processor=?",
            (now, *(context[k] for k in ("project", "category", "purpose", "location", "processor"))),
        ).fetchall()
        denies = [r for r in rows if r["decision"] == "denied"]
        grants = [r for r in rows if r["decision"] == "granted"]
        if denies:
            reason = "explicit_deny_current"
        elif len(grants) == 1:
            self._audit("consumed", "allowed_local_synthetic", grants[0]["id"], confirmation)
            self.conn.commit()
            return {"allowed": True, "reason": "allowed_local_synthetic", "permission_id": grants[0]["id"], "external_action": "none", "ai_consumption": "none"}
        elif len(grants) > 1:
            reason = "ambiguous_multiple_current_grants"
        else:
            reason = "default_deny"
        self._audit("rejected", reason, confirmation=confirmation)
        self.conn.commit()
        return {"allowed": False, "reason": reason, "external_action": "none", "ai_consumption": "none"}

    def snapshot(self) -> dict[str, Any]:
        return {"permissions": [dict(x) for x in self.conn.execute("SELECT * FROM permissions ORDER BY created_at_ms, id")], "audits": [dict(x) for x in self.conn.execute("SELECT * FROM audits ORDER BY id")]}
