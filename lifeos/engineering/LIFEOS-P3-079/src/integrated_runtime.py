"""P3-079 synthetic-only integrated local MVP drill.

The caller supplies the SQLite location.  This module has no network, cloud,
file export, IPC, Vault, AI-consumption, or real-user-data integration.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

BOUNDARIES = {
    "ai_consumption": "disabled", "cloud": "disabled", "export": "not_used",
    "external_action": "none", "external_user": "not_used", "l3": "not_used",
    "multi_device": "not_used", "network": "disabled", "real_paths": "not_used",
    "sync": "not_used", "tauri_ipc": "not_used", "vault": "not_used",
}
CONTEXT = {"purpose": "local_synthetic_restore", "location": "task_local_sqlite",
           "processor": "local_synthetic_runtime"}


class OperatorError(RuntimeError):
    pass


class IntegratedRuntime:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._schema()

    def close(self) -> None:
        self.conn.close()

    def _schema(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS records (
          id TEXT PRIMARY KEY, original_text TEXT NOT NULL, source TEXT NOT NULL,
          version INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('saved','revoked')),
          restored INTEGER NOT NULL DEFAULT 0, idempotency_key TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS permissions (
          id TEXT PRIMARY KEY, decision TEXT NOT NULL CHECK(decision IN ('grant','deny')),
          purpose TEXT NOT NULL, location TEXT NOT NULL, processor TEXT NOT NULL,
          expires_at_ms INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('current','revoked')),
          idempotency_key TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audits (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, record_id TEXT,
          detail_json TEXT NOT NULL
        );
        """)
        self.conn.commit()

    @staticmethod
    def _now() -> int:
        return int(time.time() * 1000)

    def _audit(self, event: str, record_id: str | None = None, **detail: object) -> None:
        detail["boundaries"] = BOUNDARIES
        self.conn.execute("INSERT INTO audits(event,record_id,detail_json) VALUES (?,?,?)",
                          (event, record_id, json.dumps(detail, ensure_ascii=False, sort_keys=True)))

    def _failure(self, event: str, reason: str, record_id: str | None = None, **detail: object) -> dict:
        with self.conn:
            self._audit(event, record_id, reason=reason, **detail)
        return {"ok": False, "saved": False, "reason": reason, "external_action": "none"}

    def save(self, text: str, key: str, confirmation: str, *, inject_fault: bool = False) -> dict:
        if confirmation != "CONFIRM":
            return self._failure("save_blocked", "explicit_confirmation_required")
        if not text.strip() or not key.strip():
            return self._failure("save_failed", "invalid_synthetic_input")
        record_id = "rec-" + hashlib.sha256(key.encode()).hexdigest()[:16]
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            old = self.conn.execute("SELECT * FROM records WHERE idempotency_key=?", (key,)).fetchone()
            if old:
                if old["original_text"] == text:
                    self.conn.rollback()
                    with self.conn: self._audit("save_idempotent", old["id"], key=key)
                    return {"ok": True, "saved": True, "duplicate": True, "record_id": old["id"]}
                raise OperatorError("idempotency_conflict")
            self.conn.execute("INSERT INTO records VALUES (?,?,?,1,'saved',0,?)",
                              (record_id, text, "operator_local_entry", key))
            self._audit("save_pending", record_id, key=key)
            if inject_fault:
                raise sqlite3.OperationalError("injected_precommit_failure")
            self.conn.commit()
            return {"ok": True, "saved": True, "duplicate": False, "record_id": record_id}
        except Exception as error:
            if self.conn.in_transaction: self.conn.rollback()
            return self._failure("save_failed", str(error), record_id)

    def view(self, record_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
        if not row: return self._failure("view_blocked", "unknown_record", record_id)
        return {"ok": True, "record_id": row["id"], "original_text": row["original_text"],
                "source": row["source"], "status": row["status"], "version": row["version"],
                "restored": bool(row["restored"]), "boundaries": BOUNDARIES}

    def permission_preview(self) -> dict:
        return {"default": "deny", "confirmation": "CONFIRM", "context": CONTEXT,
                "allowed_result": "allowed_local_synthetic", "boundaries": BOUNDARIES}

    def set_permission(self, decision: str, expires_at_ms: int, confirmation: str, key: str) -> dict:
        if decision not in {"grant", "deny"} or confirmation != "CONFIRM" or not key or expires_at_ms <= self._now():
            return self._failure("permission_blocked", "invalid_permission_request")
        old = self.conn.execute("SELECT * FROM permissions WHERE idempotency_key=?", (key,)).fetchone()
        if old:
            same = old["decision"] == decision and old["expires_at_ms"] == expires_at_ms
            with self.conn: self._audit("permission_idempotent" if same else "permission_blocked", None,
                                        reason="idempotent_repeat" if same else "idempotency_conflict")
            return {"ok": same, "permission_id": old["id"], "reason": "idempotent_repeat" if same else "idempotency_conflict"}
        pid = "perm-" + hashlib.sha256(key.encode()).hexdigest()[:16]
        with self.conn:
            self.conn.execute("INSERT INTO permissions VALUES (?,?,?,?,?,?,'current',?)",
              (pid, decision, CONTEXT["purpose"], CONTEXT["location"], CONTEXT["processor"], expires_at_ms, key))
            self._audit("permission_set", None, permission_id=pid, decision=decision, expires_at_ms=expires_at_ms)
        return {"ok": True, "permission_id": pid, "decision": decision}

    def revoke_permission(self, permission_id: str, confirmation: str, key: str) -> dict:
        row = self.conn.execute("SELECT * FROM permissions WHERE id=?", (permission_id,)).fetchone()
        if confirmation != "REVOKE" or not key or not row:
            return self._failure("revoke_blocked", "invalid_revoke", key=key, permission_id=permission_id,
                                 confirmation=confirmation, operation="permission_revoke")
        prior = self.conn.execute("SELECT detail_json FROM audits WHERE event='permission_revoked'").fetchall()
        for audit in prior:
            receipt = json.loads(audit[0])
            if receipt.get("key") != key:
                continue
            same_request = (receipt.get("permission_id") == permission_id
                            and receipt.get("confirmation") == confirmation
                            and receipt.get("operation") == "permission_revoke")
            if same_request:
                with self.conn:
                    self._audit("revoke_idempotent", None, permission_id=permission_id, key=key,
                                confirmation=confirmation, operation="permission_revoke")
                return {"ok": True, "permission_id": permission_id, "reason": "idempotent_repeat"}
            return self._failure("revoke_blocked", "idempotency_conflict", key=key,
                                 permission_id=permission_id, confirmation=confirmation,
                                 operation="permission_revoke")
        if row["status"] != "current": return self._failure("revoke_blocked", "not_current")
        with self.conn:
            self.conn.execute("UPDATE permissions SET status='revoked' WHERE id=?", (permission_id,))
            self._audit("permission_revoked", None, permission_id=permission_id, key=key,
                        confirmation=confirmation, operation="permission_revoke")
        return {"ok": True, "permission_id": permission_id, "reason": "revoked"}

    def _permission(self, confirmation: str) -> tuple[bool, str]:
        if confirmation != "CONFIRM": return False, "explicit_confirmation_required"
        rows = self.conn.execute("SELECT * FROM permissions WHERE status='current' AND expires_at_ms>? AND purpose=? AND location=? AND processor=?", (self._now(), CONTEXT["purpose"], CONTEXT["location"], CONTEXT["processor"])).fetchall()
        if any(r["decision"] == "deny" for r in rows): return False, "explicit_deny_current"
        grants = [r for r in rows if r["decision"] == "grant"]
        return (True, "allowed_local_synthetic") if len(grants) == 1 else (False, "ambiguous_grant" if grants else "default_deny")

    def restore_preview(self, record_id: str, source: str, version: int, confirmation: str) -> dict:
        row = self.conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
        if not row: return self._failure("restore_blocked", "unknown_record", record_id)
        if row["status"] == "revoked": return self._failure("restore_blocked", "revoked_content", record_id)
        if row["source"] != source or row["version"] != version: return self._failure("restore_blocked", "binding_mismatch", record_id)
        allowed, reason = self._permission(confirmation)
        if not allowed: return self._failure("restore_blocked", reason, record_id)
        return {"ok": True, "status": "ready", "record_id": record_id, "source": source, "version": version,
                "allowed": "allowed_local_synthetic", "boundaries": BOUNDARIES}

    def restore_confirm(self, record_id: str, source: str, version: int, confirmation: str) -> dict:
        preview = self.restore_preview(record_id, source, version, confirmation)
        if not preview["ok"]: return preview
        row = self.conn.execute("SELECT restored FROM records WHERE id=?", (record_id,)).fetchone()
        with self.conn:
            if row["restored"]:
                self._audit("restore_idempotent", record_id)
                return {"ok": True, "recovered": True, "idempotent": True, "record_id": record_id}
            self.conn.execute("UPDATE records SET restored=1 WHERE id=?", (record_id,))
            self._audit("restore_completed", record_id)
        return {"ok": True, "recovered": True, "idempotent": False, "record_id": record_id}

    def revoke_record(self, record_id: str) -> dict:
        with self.conn:
            changed = self.conn.execute("UPDATE records SET status='revoked',version=version+1 WHERE id=? AND status='saved'", (record_id,)).rowcount
            self._audit("record_revoked" if changed else "revoke_blocked", record_id)
        return {"ok": bool(changed), "record_id": record_id, "reason": "revoked" if changed else "not_current"}

    def snapshot(self) -> dict:
        return {"records": [dict(r) for r in self.conn.execute("SELECT * FROM records ORDER BY id")],
          "permissions": [dict(r) for r in self.conn.execute("SELECT * FROM permissions ORDER BY id")],
          "audits": [dict(r) for r in self.conn.execute("SELECT * FROM audits ORDER BY seq")], "boundaries": BOUNDARIES}
