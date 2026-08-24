"""Controlled, synthetic-only local MVP loop for LIFEOS-P3-063."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


CONTROLLED_PROJECT_ID = "project-synthetic-001"


class VisibleSaveError(RuntimeError):
    """A capture failure which must never be represented as saved."""


@dataclass(frozen=True)
class CaptureReceipt:
    record_id: str
    saved: bool
    message: str
    duplicate: bool


class LocalMvp:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._migrate()
        self._seed_project()

    def close(self) -> None:
        self.conn.close()

    def _migrate(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
              id TEXT PRIMARY KEY, name TEXT NOT NULL, context_text TEXT NOT NULL,
              controlled INTEGER NOT NULL CHECK (controlled = 1)
            );
            CREATE TABLE IF NOT EXISTS records (
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
              original_text TEXT NOT NULL, source_identity TEXT NOT NULL,
              content_identity TEXT NOT NULL CHECK (content_identity = 'user_original'),
              idempotency_key TEXT NOT NULL UNIQUE, created_at_ms INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS next_step_confirmations (
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
              next_step_text TEXT NOT NULL, confirmation_identity TEXT NOT NULL
                CHECK (confirmation_identity = 'user_confirmed'),
              created_at_ms INTEGER NOT NULL
            );
            """
        )
        self.conn.commit()

    def _seed_project(self) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO projects VALUES (?,?,?,1)",
            (CONTROLLED_PROJECT_ID, "合成研究项目", "仅用于 P3-063 受控本地恢复演示"),
        )
        self.conn.commit()

    def capture(self, *, original_text: str, idempotency_key: str, now_ms: int,
                fail_before_commit: bool = False) -> CaptureReceipt:
        if not original_text.strip() or not idempotency_key.strip():
            raise VisibleSaveError("保存失败：原文与幂等键均不能为空")
        record_id = "rec-" + hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            existing = self.conn.execute(
                "SELECT id, original_text FROM records WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing:
                if existing["original_text"] != original_text:
                    raise VisibleSaveError("保存失败：幂等键已用于不同原文")
                self.conn.rollback()
                return CaptureReceipt(existing["id"], True, "已保存（重复提交未重复写入）", True)
            self.conn.execute(
                "INSERT INTO records VALUES (?,?,?,?,?,?,?)",
                (record_id, CONTROLLED_PROJECT_ID, original_text, "user_local_entry",
                 "user_original", idempotency_key, now_ms),
            )
            if fail_before_commit:
                raise sqlite3.OperationalError("injected write failure before commit")
            self.conn.commit()
            return CaptureReceipt(record_id, True, "已保存", False)
        except Exception as exc:
            if self.conn.in_transaction:
                self.conn.rollback()
            if isinstance(exc, VisibleSaveError):
                raise
            raise VisibleSaveError("保存失败：未完成提交") from exc

    def view_record(self, record_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
        if not row:
            raise KeyError("record not found")
        return {"record_id": row["id"], "original_text": row["original_text"],
                "source_identity": row["source_identity"], "content_identity": row["content_identity"],
                "ai_features": "disabled"}

    def restore_project(self, project_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM projects WHERE id=? AND controlled=1", (project_id,)).fetchone()
        if not row:
            raise PermissionError("恢复失败：项目不在本次受控范围内")
        return {"project_id": row["id"], "project_name": row["name"],
                "context": row["context_text"], "restore_identity": "controlled_local_project"}

    def confirm_next_step(self, *, project_id: str, next_step_text: str, now_ms: int) -> dict:
        self.restore_project(project_id)
        if not next_step_text.strip():
            raise ValueError("确认失败：下一步不能为空")
        confirmation_id = "confirm-" + hashlib.sha256((project_id + next_step_text).encode()).hexdigest()[:16]
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO next_step_confirmations VALUES (?,?,?,?,?)",
                              (confirmation_id, project_id, next_step_text, "user_confirmed", now_ms))
        return {"confirmation_id": confirmation_id, "confirmation_identity": "user_confirmed",
                "external_action": "none", "autonomy_level": "L0"}

    def snapshot(self, record_id: str) -> dict:
        return {"record": self.view_record(record_id),
                "project": self.restore_project(CONTROLLED_PROJECT_ID),
                "ai_features": "disabled", "network": "disabled", "tauri_ipc": "not_used"}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
