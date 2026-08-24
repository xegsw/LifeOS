"""Synthetic-only capture and recovery drill for LIFEOS-P3-067.

This module intentionally has no network, filesystem discovery, IPC, or export code.
All SQLite files are supplied by the task-local runner/tests.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


BOUNDARIES = {
    "network": "disabled", "tauri_ipc": "not_used", "vault": "not_used",
    "real_paths": "not_used", "export": "not_used", "cloud": "not_used",
    "sync": "not_used", "multi_device": "not_used", "l3": "not_used",
    "external_user": "not_used", "external_action": "none",
}


@dataclass(frozen=True)
class RecoveryPlan:
    source: str
    record_id: str
    version: int
    expected_status: str


class SyntheticRecovery:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._schema()

    def _schema(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS records (
          id TEXT PRIMARY KEY, source TEXT NOT NULL, body TEXT NOT NULL,
          version INTEGER NOT NULL CHECK(version > 0), state TEXT NOT NULL
            CHECK(state IN ('saved','revoked','tombstoned')),
          restored INTEGER NOT NULL DEFAULT 0 CHECK(restored IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS audit (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
          record_id TEXT, detail_json TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def _audit(self, event: str, record_id: str | None, **detail: object) -> None:
        detail["boundaries"] = BOUNDARIES
        self.conn.execute("INSERT INTO audit(event, record_id, detail_json) VALUES (?, ?, ?)",
                          (event, record_id, json.dumps(detail, sort_keys=True)))

    def capture(self, record_id: str, source: str, body: str, *, fault: str | None = None) -> dict:
        if not all(isinstance(v, str) and v.strip() for v in (record_id, source, body)):
            return {"status": "failed", "reason": "invalid_synthetic_input", "saved": False, "boundaries": BOUNDARIES}
        try:
            with self.conn:
                self.conn.execute("INSERT INTO records(id, source, body, version, state) VALUES (?, ?, ?, 1, 'saved')",
                                  (record_id, source, body))
                self._audit("capture_pending", record_id, source=source, status="pending_commit")
                if fault == "before_commit":
                    raise RuntimeError("injected_before_commit")
            return {"status": "saved", "saved": True, "record_id": record_id, "version": 1, "boundaries": BOUNDARIES}
        except (sqlite3.Error, RuntimeError) as error:
            return {"status": "failed", "saved": False, "reason": str(error), "record_id": record_id, "boundaries": BOUNDARIES}

    def revoke(self, record_id: str, state: str = "tombstoned") -> dict:
        if state not in {"revoked", "tombstoned"}:
            return {"status": "failed", "reason": "invalid_revocation_state", "boundaries": BOUNDARIES}
        with self.conn:
            changed = self.conn.execute("UPDATE records SET state = ?, version = version + 1 WHERE id = ?", (state, record_id)).rowcount
            self._audit("record_revoked", record_id, state=state, changed=changed)
        return {"status": "revoked" if changed else "failed", "record_id": record_id, "reason": None if changed else "unknown_record", "boundaries": BOUNDARIES}

    def preview(self, plan: RecoveryPlan | object) -> dict:
        if not isinstance(plan, RecoveryPlan) or not all(isinstance(v, (str, int)) for v in (getattr(plan, 'source', None), getattr(plan, 'record_id', None), getattr(plan, 'version', None), getattr(plan, 'expected_status', None))):
            return {"status": "failed", "reason": "invalid_or_unknown_plan", "boundaries": BOUNDARIES}
        row = self.conn.execute("SELECT * FROM records WHERE id = ?", (plan.record_id,)).fetchone()
        if not row:
            return {"status": "blocked", "reason": "unknown_record", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        if row["state"] in {"revoked", "tombstoned"}:
            return {"status": "blocked", "reason": "revoked_or_tombstoned", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        if row["source"] != plan.source:
            return {"status": "blocked", "reason": "source_mismatch", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        if row["version"] != plan.version:
            return {"status": "blocked", "reason": "version_mismatch", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        if row["state"] != plan.expected_status:
            return {"status": "blocked", "reason": "status_mismatch", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        return {"status": "ready", "record_id": row["id"], "source": row["source"], "version": row["version"], "saved_status": row["state"], "boundaries": BOUNDARIES}

    def recover(self, plan: RecoveryPlan | object, confirmation: str) -> dict:
        preview = self.preview(plan)
        if preview["status"] != "ready":
            # A blocked recovery is material failure-disclosure evidence.  Commit
            # it before returning so a subsequent reopen can still verify it.
            with self.conn:
                self._audit("recovery_blocked", getattr(plan, "record_id", None), reason=preview["reason"])
            return preview
        if confirmation != "CONFIRM":
            # Keep a rejected confirmation durable for the same reason; it must
            # not disappear merely because the caller closes the drill afterwards.
            with self.conn:
                self._audit("recovery_not_confirmed", plan.record_id, reason="explicit_confirmation_required")
            return {"status": "blocked", "reason": "explicit_confirmation_required", "record_id": plan.record_id, "boundaries": BOUNDARIES}
        with self.conn:
            row = self.conn.execute("SELECT restored FROM records WHERE id = ?", (plan.record_id,)).fetchone()
            if row["restored"]:
                self._audit("recovery_idempotent", plan.record_id, version=plan.version)
                return {"status": "recovered", "idempotent": True, "record_id": plan.record_id, "boundaries": BOUNDARIES}
            self.conn.execute("UPDATE records SET restored = 1 WHERE id = ?", (plan.record_id,))
            self._audit("recovery_completed", plan.record_id, version=plan.version)
        return {"status": "recovered", "idempotent": False, "record_id": plan.record_id, "boundaries": BOUNDARIES}

    def snapshot(self) -> dict:
        return {"records": [dict(r) for r in self.conn.execute("SELECT * FROM records ORDER BY id")],
                "audit": [dict(r) for r in self.conn.execute("SELECT * FROM audit ORDER BY seq")],
                "boundaries": BOUNDARIES}

    def close(self) -> None:
        self.conn.close()
