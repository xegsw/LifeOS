"""LIFEOS-P3-075: a task-local, non-sensitive local runtime drill.

The module intentionally contains no network, filesystem discovery, export,
Tauri/IPC, cloud, AI, sync, multi-device, L3, or external-user integration.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


CONTROLLED_PROJECT_ID = "p3-075-controlled-project"
BOUNDARIES = {
    "ai_consumption": "disabled", "cloud": "disabled", "external_action": "none",
    "external_user": "not_used", "export": "not_used", "l3": "not_used",
    "multi_device": "not_used", "network": "disabled", "real_paths": "not_used",
    "sync": "not_used", "tauri_ipc": "not_used", "vault": "not_used",
}


class VisibleRuntimeError(RuntimeError):
    """A failure disclosed to the operator and never represented as saved."""


@dataclass(frozen=True)
class SaveReceipt:
    record_id: str
    saved: bool
    duplicate: bool
    message: str
    source_identity: str = "operator_local_entry"
    content_identity: str = "user_original"
    operator_confirmation: str = "explicit"
    ai_status: str = "disabled"
    external_action: str = "none"


class ControlledLocalRuntime:
    def __init__(self, db_path: Path):
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
        CREATE TABLE IF NOT EXISTS projects (
          id TEXT PRIMARY KEY, display_name TEXT NOT NULL, context TEXT NOT NULL,
          controlled INTEGER NOT NULL CHECK (controlled = 1)
        );
        CREATE TABLE IF NOT EXISTS records (
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          original_text TEXT NOT NULL, source_identity TEXT NOT NULL,
          content_identity TEXT NOT NULL CHECK (content_identity = 'user_original'),
          idempotency_key TEXT NOT NULL UNIQUE, created_at_ms INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audits (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
          record_id TEXT, detail_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS next_steps (
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          text TEXT NOT NULL, confirmation_identity TEXT NOT NULL
            CHECK (confirmation_identity = 'operator_confirmed'),
          created_at_ms INTEGER NOT NULL
        );
        """)
        self.conn.execute("INSERT OR IGNORE INTO projects VALUES (?, ?, ?, 1)", (
            CONTROLLED_PROJECT_ID, "P3-075 受控测试项目", "仅限本任务的非敏感本地测试上下文",
        ))
        self.conn.commit()

    def _audit(self, event: str, record_id: str | None, **detail: object) -> None:
        detail["boundaries"] = BOUNDARIES
        self.conn.execute("INSERT INTO audits(event, record_id, detail_json) VALUES (?, ?, ?)",
                          (event, record_id, json.dumps(detail, ensure_ascii=False, sort_keys=True)))

    def save(self, *, text: str, idempotency_key: str, confirmed: bool, now_ms: int,
             fail_before_commit: bool = False) -> SaveReceipt:
        if not confirmed:
            raise VisibleRuntimeError("保存已阻断：需要操作者明确确认")
        if not text.strip() or not idempotency_key.strip():
            raise VisibleRuntimeError("保存失败：测试文本与幂等键均不能为空")
        record_id = "rec-" + hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()[:16]
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            existing = self.conn.execute(
                "SELECT id, original_text FROM records WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if existing:
                if existing["original_text"] != text:
                    raise VisibleRuntimeError("保存已拒绝：幂等键已用于不同测试文本")
                self.conn.rollback()
                return SaveReceipt(existing["id"], True, True, "已保存（重复请求未重复写入）")
            self.conn.execute("INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?)", (
                record_id, CONTROLLED_PROJECT_ID, text, "operator_local_entry", "user_original",
                idempotency_key, now_ms,
            ))
            self._audit("save_pending", record_id, status="pending_commit")
            if fail_before_commit:
                raise sqlite3.OperationalError("injected_precommit_failure")
            self.conn.commit()
            return SaveReceipt(record_id, True, False, "已保存")
        except Exception as exc:
            if self.conn.in_transaction:
                self.conn.rollback()
            if isinstance(exc, VisibleRuntimeError):
                raise
            raise VisibleRuntimeError("保存失败：本地事务未提交") from exc

    def record_view(self, record_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
        if not row:
            raise VisibleRuntimeError("读取已拒绝：未知记录")
        return {"record_id": row["id"], "original_text": row["original_text"],
                "source_identity": row["source_identity"], "content_identity": row["content_identity"],
                "ai_status": "disabled", "external_action": "none"}

    def restore_context(self, project_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ? AND controlled = 1", (project_id,)).fetchone()
        if not row:
            raise VisibleRuntimeError("恢复已拒绝：项目不在本次受控范围内")
        return {"project_id": row["id"], "project_name": row["display_name"],
                "context": row["context"], "restore_scope": "controlled_task_local_only"}

    def confirm_next_step(self, *, project_id: str, next_step: str, confirmed: bool, now_ms: int) -> dict:
        self.restore_context(project_id)
        if not confirmed or not next_step.strip():
            raise VisibleRuntimeError("下一步已阻断：需要操作者明确确认及内容")
        step_id = "step-" + hashlib.sha256((project_id + next_step).encode("utf-8")).hexdigest()[:16]
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO next_steps VALUES (?, ?, ?, ?, ?)",
                              (step_id, project_id, next_step, "operator_confirmed", now_ms))
            self._audit("next_step_confirmed", None, step_id=step_id)
        return {"next_step_id": step_id, "confirmation_identity": "operator_confirmed",
                "external_action": "none", "ai_status": "disabled"}

    def count_records(self, key: str) -> int:
        return self.conn.execute("SELECT count(*) FROM records WHERE idempotency_key = ?", (key,)).fetchone()[0]

    def audit_events(self) -> list[str]:
        return [row[0] for row in self.conn.execute("SELECT event FROM audits ORDER BY seq")]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def receipt_json(receipt: SaveReceipt) -> dict:
    return asdict(receipt)
