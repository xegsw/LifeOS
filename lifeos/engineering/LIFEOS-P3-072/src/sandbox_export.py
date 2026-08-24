"""Synthetic-only, one-time export to a newly created system temporary sandbox.

This module deliberately has no network, Tauri/IPC, Vault, cloud, sync, real
database, user-path, or external-user capability.  A successful export is a
JSON file in a fresh ``tempfile.mkdtemp`` directory created by this process.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BOUNDARIES = {
    "network": "disabled",
    "tauri_ipc": "not_used",
    "vault": "not_used",
    "real_database": "not_used",
    "cloud": "not_used",
    "sync": "not_used",
    "multi_device": "not_used",
    "l3": "not_used",
    "external_user": "not_used",
    "non_temporary_path": "blocked",
}


@dataclass(frozen=True)
class ExportPlan:
    source: str
    content_id: str
    version: int
    scope: str
    target_category: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class ControlledSandboxExport:
    """In-memory synthetic record state and a fail-closed temporary exporter."""

    def __init__(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE records (
              content_id TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              version INTEGER NOT NULL,
              payload TEXT NOT NULL,
              state TEXT NOT NULL CHECK(state IN ('active', 'revoked', 'tombstoned')),
              conflict INTEGER NOT NULL DEFAULT 0,
              exported_plan_hash TEXT
            );
            CREATE TABLE previews (
              token TEXT PRIMARY KEY,
              plan_hash TEXT NOT NULL,
              content_id TEXT NOT NULL
            );
            CREATE TABLE audit (
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,
              event TEXT NOT NULL,
              content_id TEXT,
              detail_json TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        self.conn.close()

    def _audit(self, event: str, content_id: str | None, **detail: Any) -> None:
        detail["boundaries"] = BOUNDARIES
        self.conn.execute(
            "INSERT INTO audit(event, content_id, detail_json) VALUES (?, ?, ?)",
            (event, content_id, json.dumps(detail, ensure_ascii=False, sort_keys=True)),
        )

    def register(self, content_id: str, source: str, payload: str, version: int = 1) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (content_id, source, payload)):
            raise ValueError("invalid_synthetic_record")
        if not isinstance(version, int) or version < 1:
            raise ValueError("invalid_synthetic_record")
        with self.conn:
            self.conn.execute(
                "INSERT INTO records(content_id, source, version, payload, state) VALUES (?, ?, ?, ?, 'active')",
                (content_id, source, version, payload),
            )
            self._audit("record_registered", content_id, source=source, version=version)

    def set_state(self, content_id: str, state: str) -> None:
        if state not in {"revoked", "tombstoned"}:
            raise ValueError("invalid_state")
        with self.conn:
            changed = self.conn.execute("UPDATE records SET state=? WHERE content_id=?", (state, content_id)).rowcount
            self._audit("record_state_changed", content_id, state=state, changed=changed)

    def set_conflict(self, content_id: str) -> None:
        with self.conn:
            changed = self.conn.execute("UPDATE records SET conflict=1 WHERE content_id=?", (content_id,)).rowcount
            self._audit("record_conflict_marked", content_id, changed=changed)

    def _validated(self, plan: ExportPlan | object) -> tuple[sqlite3.Row | None, str | None]:
        if not isinstance(plan, ExportPlan):
            return None, "invalid_or_unknown_plan"
        if not all(isinstance(value, str) and value.strip() for value in (plan.source, plan.content_id, plan.scope, plan.target_category)):
            return None, "invalid_or_unknown_plan"
        if not isinstance(plan.version, int) or plan.version < 1:
            return None, "invalid_or_unknown_plan"
        row = self.conn.execute("SELECT * FROM records WHERE content_id=?", (plan.content_id,)).fetchone()
        if not row:
            return None, "unknown_content"
        if row["state"] != "active":
            return None, "revoked_or_tombstoned"
        if row["source"] != plan.source:
            return None, "source_mismatch"
        if row["version"] != plan.version:
            return None, "identity_version_mismatch"
        if row["conflict"]:
            return None, "conflict_detected"
        return row, None

    def _blocked(self, reason: str, content_id: str | None) -> dict[str, Any]:
        with self.conn:
            self._audit("sandbox_export_blocked", content_id, reason=reason)
        return {"status": "blocked", "reason": reason, "external_action": "none", "boundaries": BOUNDARIES}

    def preview(self, plan: ExportPlan | object) -> dict[str, Any]:
        row, reason = self._validated(plan)
        if reason:
            return self._blocked(reason, getattr(plan, "content_id", None))
        assert isinstance(plan, ExportPlan) and row is not None
        identity = {"id": plan.content_id, "version": plan.version, "content_hash": _sha256(row["payload"])}
        plan_body = {"source": plan.source, "content_identity": identity, "scope": plan.scope, "target_category": plan.target_category}
        plan_hash = _sha256(plan_body)
        token = _sha256({"kind": "preview", "plan_hash": plan_hash})
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO previews(token, plan_hash, content_id) VALUES (?, ?, ?)", (token, plan_hash, plan.content_id))
            self._audit("sandbox_export_previewed", plan.content_id, plan_hash=plan_hash)
        return {
            "status": "ready", **plan_body, "plan_hash": plan_hash, "preview_token": token,
            "confirmation_required": "CONFIRM", "target_semantics": "new_system_temporary_sandbox_only",
            "overwrite_semantics": "blocked", "failure_semantics": "fail_closed_audited_no_visible_output",
            "external_action": "none", "boundaries": BOUNDARIES,
        }

    @staticmethod
    def _new_sandbox() -> Path:
        sandbox = Path(tempfile.mkdtemp(prefix="lifeos-p3-072-export-")).resolve()
        if not sandbox.is_dir() or sandbox.parent != Path(tempfile.gettempdir()).resolve():
            raise RuntimeError("temporary_sandbox_validation_failed")
        return sandbox

    @staticmethod
    def _atomic_new_file(sandbox: Path, filename: str, body: bytes, *, inject_failure: bool = False) -> Path:
        destination = (sandbox / filename).resolve()
        if destination.parent != sandbox.resolve() or destination.exists():
            raise RuntimeError("destination_not_new_temporary_sandbox_file")
        temporary = sandbox / ".pending-export.json"
        try:
            with open(temporary, "xb") as handle:
                if inject_failure:
                    raise OSError("injected_write_failure")
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            # link() fails if destination exists, so it never overwrites a collision.
            os.link(temporary, destination)
            temporary.unlink()
            return destination
        except Exception:
            if temporary.exists():
                temporary.unlink()
            if destination.exists():
                destination.unlink()
            raise

    def confirm_and_export(
        self, plan: ExportPlan | object, confirmation: str, preview_token: str, *, inject_failure: bool = False,
        simulate_destination_collision: bool = False,
    ) -> dict[str, Any]:
        preview = self.preview(plan)
        content_id = getattr(plan, "content_id", None)
        if preview["status"] != "ready":
            return preview
        if confirmation != "CONFIRM":
            return self._blocked("explicit_confirmation_required", content_id)
        if preview_token != preview["preview_token"]:
            return self._blocked("preview_token_mismatch", content_id)
        assert isinstance(plan, ExportPlan)
        row = self.conn.execute("SELECT * FROM records WHERE content_id=?", (plan.content_id,)).fetchone()
        assert row is not None
        if row["exported_plan_hash"] is not None:
            return self._blocked("one_time_export_already_consumed", content_id)
        sandbox: Path | None = None
        try:
            sandbox = self._new_sandbox()
            exported = {
                "kind": "lifeos_synthetic_controlled_export",
                "source": plan.source,
                "content_identity": preview["content_identity"],
                "scope": plan.scope,
                "target_category": plan.target_category,
                "payload": row["payload"],
                "plan_hash": preview["plan_hash"],
            }
            export_hash = _sha256(exported)
            filename = f"lifeos-export-{export_hash}.json"
            if simulate_destination_collision:
                (sandbox / filename).write_bytes(b"existing synthetic collision")
            destination = self._atomic_new_file(sandbox, filename, _canonical(exported), inject_failure=inject_failure)
            with self.conn:
                self.conn.execute("UPDATE records SET exported_plan_hash=? WHERE content_id=?", (preview["plan_hash"], plan.content_id))
                self._audit("sandbox_export_completed", plan.content_id, plan_hash=preview["plan_hash"], export_hash=export_hash, sandbox_id=sandbox.name)
            return {
                "status": "exported", "receipt": "synthetic_temporary_sandbox_export_once",
                "content_identity": preview["content_identity"], "source": plan.source,
                "plan_hash": preview["plan_hash"], "export_hash": export_hash,
                "sandbox_id": sandbox.name, "filename": destination.name,
                "content_matches_receipt": _sha256(json.loads(destination.read_text("utf-8"))) == export_hash,
                "external_action": "temporary_sandbox_file_only", "boundaries": BOUNDARIES,
            }
        except Exception as error:
            if sandbox is not None:
                for entry in sandbox.iterdir():
                    entry.unlink()
                visible = [entry.name for entry in sandbox.iterdir() if not entry.name.startswith(".")]
                sandbox.rmdir()
            else:
                visible = []
            with self.conn:
                self._audit("sandbox_export_failed", content_id, reason="write_failed", visible_output_count=len(visible))
            return {"status": "blocked", "reason": "write_failed", "visible_output_count": len(visible), "external_action": "none", "boundaries": BOUNDARIES}

    def audit_events(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.conn.execute("SELECT * FROM audit ORDER BY sequence")]
