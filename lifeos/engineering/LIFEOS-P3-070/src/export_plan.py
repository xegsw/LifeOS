"""Synthetic-only export-plan confirmation drill for LIFEOS-P3-070.

This module creates plans and audit receipts only.  It deliberately has no
filesystem, network, IPC, Vault, cloud, or export implementation.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


BOUNDARIES = {
    "network": "disabled",
    "paths": "not_used",
    "tauri_ipc": "not_used",
    "vault": "not_used",
    "real_export": "not_used",
    "cloud": "not_used",
    "sync": "not_used",
    "multi_device": "not_used",
    "l3": "not_used",
    "external_user": "not_used",
    "external_action": "none",
}


@dataclass(frozen=True)
class ExportPlan:
    source: str
    content_id: str
    version: int
    scope: str
    target_category: str


class SyntheticExportPlans:
    """An in-memory, fail-closed plan/receipt state machine."""

    def __init__(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
          CREATE TABLE records (
            content_id TEXT PRIMARY KEY, source TEXT NOT NULL, version INTEGER NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('active','revoked','tombstoned'))
          );
          CREATE TABLE audit (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
            content_id TEXT, detail_json TEXT NOT NULL
          );
        """)

    def close(self) -> None:
        self.conn.close()

    def _audit(self, event: str, content_id: str | None, **detail: object) -> None:
        detail["boundaries"] = BOUNDARIES
        self.conn.execute(
            "INSERT INTO audit(event, content_id, detail_json) VALUES (?, ?, ?)",
            (event, content_id, json.dumps(detail, ensure_ascii=False, sort_keys=True)),
        )

    def register(self, content_id: str, source: str, version: int = 1) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (content_id, source)) or not isinstance(version, int) or version < 1:
            raise ValueError("invalid_synthetic_record")
        with self.conn:
            self.conn.execute("INSERT INTO records VALUES (?, ?, ?, 'active')", (content_id, source, version))
            self._audit("record_registered", content_id, source=source, version=version)

    def revoke(self, content_id: str, state: str) -> None:
        if state not in {"revoked", "tombstoned"}:
            raise ValueError("invalid_revocation_state")
        with self.conn:
            changed = self.conn.execute("UPDATE records SET state=? WHERE content_id=?", (state, content_id)).rowcount
            self._audit("record_state_changed", content_id, state=state, changed=changed)

    def preview(self, plan: ExportPlan | object) -> dict:
        if not isinstance(plan, ExportPlan) or not all(isinstance(value, str) and value.strip() for value in (getattr(plan, "source", None), getattr(plan, "content_id", None), getattr(plan, "scope", None), getattr(plan, "target_category", None))) or not isinstance(getattr(plan, "version", None), int):
            return self._blocked("invalid_or_unknown_plan", None)
        row = self.conn.execute("SELECT * FROM records WHERE content_id=?", (plan.content_id,)).fetchone()
        if not row:
            return self._blocked("unknown_content", plan.content_id)
        if row["state"] != "active":
            return self._blocked("revoked_or_tombstoned", plan.content_id)
        if row["source"] != plan.source:
            return self._blocked("source_mismatch", plan.content_id)
        if row["version"] != plan.version:
            return self._blocked("identity_version_mismatch", plan.content_id)
        return {
            "status": "ready", "source": plan.source, "content_identity": {"id": plan.content_id, "version": plan.version},
            "scope": plan.scope, "target_category": plan.target_category,
            "confirmation_required": "CONFIRM", "conflict_semantics": "blocked_on_any_conflict",
            "failure_semantics": "fail_closed_and_audited", "external_action": "none", "boundaries": BOUNDARIES,
        }

    def _blocked(self, reason: str, content_id: str | None) -> dict:
        with self.conn:
            self._audit("export_plan_blocked", content_id, reason=reason)
        return {"status": "blocked", "reason": reason, "external_action": "none", "boundaries": BOUNDARIES}

    def confirm(self, plan: ExportPlan | object, confirmation: str, *, conflict: bool = False) -> dict:
        preview = self.preview(plan)
        content_id = getattr(plan, "content_id", None)
        if preview["status"] != "ready":
            return preview
        if confirmation != "CONFIRM":
            return self._blocked("explicit_confirmation_required", content_id)
        if conflict:
            return self._blocked("conflict_detected", content_id)
        with self.conn:
            self._audit("export_plan_confirmed", content_id, confirmation="CONFIRM", external_action="none")
        return {"status": "confirmed_plan", "content_identity": preview["content_identity"], "receipt": "local_confirmed_plan_only", "external_action": "none", "boundaries": BOUNDARIES}

    def snapshot(self) -> dict:
        return {
            "records": [dict(row) for row in self.conn.execute("SELECT * FROM records ORDER BY content_id")],
            "audit": [dict(row) for row in self.conn.execute("SELECT * FROM audit ORDER BY sequence")],
            "boundaries": BOUNDARIES,
        }
