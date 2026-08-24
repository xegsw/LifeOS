"""Synthetic-only, fail-closed permission settings for LIFEOS-P3-065."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

CONTROLLED_PROJECT_ID = "project-synthetic-001"
ALLOWED = {
    "category": {"synthetic_note", "synthetic_task"},
    "purpose": {"local_recovery", "local_summary"},
    "location": {"local_sqlite", "local_cache"},
    "processor": {"local_rules", "local_summary_engine"},
}


class PermissionErrorVisible(ValueError):
    pass


def _id(prefix: str, *parts: str) -> str:
    return prefix + "-" + hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


class PermissionSettings:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript("""
          CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, controlled INTEGER NOT NULL CHECK(controlled=1)
          );
          CREATE TABLE IF NOT EXISTS authorizations (
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), category TEXT NOT NULL,
            purpose TEXT NOT NULL, location TEXT NOT NULL, processor TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('granted','denied','revoked')),
            expires_at_ms INTEGER NOT NULL, version INTEGER NOT NULL, operator_confirmation TEXT NOT NULL,
            idempotency_key TEXT NOT NULL UNIQUE, created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL
          );
          CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY, event_type TEXT NOT NULL, authorization_id TEXT,
            decision TEXT NOT NULL, operator_confirmation TEXT NOT NULL,
            detail_json TEXT NOT NULL, occurred_at_ms INTEGER NOT NULL
          );
          CREATE TABLE IF NOT EXISTS revocation_commands (
            idempotency_key TEXT PRIMARY KEY, authorization_id TEXT NOT NULL REFERENCES authorizations(id),
            confirmation TEXT NOT NULL, occurred_at_ms INTEGER NOT NULL
          );
        """)
        self.conn.execute("INSERT OR IGNORE INTO projects VALUES (?,?,1)", (CONTROLLED_PROJECT_ID, "合成权限项目"))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def _validate(self, *, project_id: str, category: str, purpose: str, location: str, processor: str, expires_at_ms: int) -> None:
        values = {"category": category, "purpose": purpose, "location": location, "processor": processor}
        if project_id != CONTROLLED_PROJECT_ID or not all(isinstance(v, str) and v in ALLOWED[k] for k, v in values.items()):
            raise PermissionErrorVisible("设置被拒绝：输入不在受控合成范围")
        if not isinstance(expires_at_ms, int) or expires_at_ms <= 0:
            raise PermissionErrorVisible("设置被拒绝：有效期必须为正整数毫秒")

    def _audit(self, event_type: str, authorization_id: str | None, decision: str, confirmation: str, now_ms: int, **detail: object) -> None:
        payload = json.dumps(detail, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        sequence = self.conn.execute("SELECT count(*) FROM audit_events").fetchone()[0]
        self.conn.execute("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)", (_id("audit", event_type, str(authorization_id), str(now_ms), payload, str(sequence)), event_type, authorization_id, decision, confirmation, payload, now_ms))

    def preview(self, **settings: object) -> dict:
        return {"settings": settings, "scope": "synthetic SQLite only", "default_decision": "deny", "external_action": "none", "ai_consumption": "disabled_until_local_allow"}

    def decide(self, *, project_id: str, category: str, purpose: str, location: str, processor: str, expires_at_ms: int, decision: str, confirmation: str, idempotency_key: str, now_ms: int) -> dict:
        self._validate(project_id=project_id, category=category, purpose=purpose, location=location, processor=processor, expires_at_ms=expires_at_ms)
        if decision not in {"grant", "deny"} or confirmation != "CONFIRM" or not idempotency_key.strip():
            raise PermissionErrorVisible("设置被拒绝：需要明确 CONFIRM、合法决定和幂等键")
        canonical = (project_id, category, purpose, location, processor, expires_at_ms, decision)
        existing = self.conn.execute("SELECT * FROM authorizations WHERE idempotency_key=?", (idempotency_key,)).fetchone()
        if existing:
            old = tuple(existing[k] for k in ("project_id","category","purpose","location","processor","expires_at_ms")) + (("grant" if existing["status"] == "granted" else "deny"),)
            if old != canonical:
                raise PermissionErrorVisible("设置失败：幂等键已用于不同决定")
            return {"authorization_id": existing["id"], "status": existing["status"], "duplicate": True, "message": "设置已存在，未重复写入"}
        authorization_id = _id("auth", idempotency_key)
        status = "granted" if decision == "grant" else "denied"
        with self.conn:
            self.conn.execute("INSERT INTO authorizations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (authorization_id, project_id, category, purpose, location, processor, status, expires_at_ms, 1, confirmation, idempotency_key, now_ms, now_ms))
            self._audit("authorization." + decision, authorization_id, status, confirmation, now_ms, project_id=project_id, category=category, purpose=purpose, location=location, processor=processor, expires_at_ms=expires_at_ms, version=1)
        return {"authorization_id": authorization_id, "status": status, "duplicate": False, "message": "已授予受控本地许可" if status == "granted" else "已明确拒绝"}

    def revoke(self, *, authorization_id: str, confirmation: str, idempotency_key: str, now_ms: int) -> dict:
        if confirmation != "REVOKE" or not idempotency_key.strip():
            raise PermissionErrorVisible("撤回被拒绝：需要明确 REVOKE 和幂等键")
        row = self.conn.execute("SELECT * FROM authorizations WHERE id=?", (authorization_id,)).fetchone()
        if not row:
            raise PermissionErrorVisible("撤回失败：授权不存在")
        command = self.conn.execute("SELECT * FROM revocation_commands WHERE idempotency_key=?", (idempotency_key,)).fetchone()
        if command:
            if command["authorization_id"] != authorization_id:
                raise PermissionErrorVisible("撤回失败：幂等键已用于另一项授权")
            return {"authorization_id": authorization_id, "status": "revoked", "duplicate": True, "message": "已撤回（重复请求未重复写入）"}
        if row["status"] == "revoked":
            return {"authorization_id": authorization_id, "status": "revoked", "duplicate": True, "message": "已撤回（重复请求未重复写入）"}
        if row["status"] != "granted":
            raise PermissionErrorVisible("撤回失败：只有已授予授权可撤回")
        with self.conn:
            self.conn.execute("INSERT INTO revocation_commands VALUES (?,?,?,?)", (idempotency_key, authorization_id, confirmation, now_ms))
            self.conn.execute("UPDATE authorizations SET status='revoked', version=version+1, updated_at_ms=? WHERE id=?", (now_ms, authorization_id))
            self._audit("authorization.revoke", authorization_id, "revoked", confirmation, now_ms, idempotency_key=idempotency_key, version=2)
        return {"authorization_id": authorization_id, "status": "revoked", "duplicate": False, "message": "已撤回；后续消费默认阻断"}

    def consume(self, *, project_id: str, category: str, purpose: str, location: str, processor: str, now_ms: int) -> dict:
        try:
            self._validate(project_id=project_id, category=category, purpose=purpose, location=location, processor=processor, expires_at_ms=1)
        except PermissionErrorVisible:
            result = {"allowed": False, "reason": "invalid_context", "external_action": "none", "ai_consumption": "none"}
        else:
            rows = self.conn.execute("SELECT * FROM authorizations WHERE project_id=? AND category=? AND purpose=? AND location=? AND processor=? ORDER BY created_at_ms, id", (project_id, category, purpose, location, processor)).fetchall()
            current = [r for r in rows if r["status"] in {"granted", "denied"} and r["expires_at_ms"] > now_ms]
            grants = [r for r in current if r["status"] == "granted"]
            denies = [r for r in current if r["status"] == "denied"]
            if denies:
                allowed, reason = False, "explicit_deny_current"
            elif len(grants) == 1:
                allowed, reason = True, "allowed_local_synthetic"
            elif len(grants) > 1:
                allowed, reason = False, "ambiguous_multiple_current_grants"
            else:
                allowed, reason = False, "default_deny" if not rows else "authorization_not_current_or_not_matching"
            result = {"allowed": allowed, "reason": reason, "external_action": "none", "ai_consumption": "local_decision_only" if allowed else "none", "current_grant_ids": [r["id"] for r in grants], "current_deny_ids": [r["id"] for r in denies]}
        with self.conn:
            self._audit("consumption.check", None, "allow" if result["allowed"] else "deny", "N/A", now_ms, **result)
        return result

    def snapshot(self) -> dict:
        return {"authorizations": [dict(r) for r in self.conn.execute("SELECT * FROM authorizations ORDER BY created_at_ms, id")], "revocation_commands": [dict(r) for r in self.conn.execute("SELECT * FROM revocation_commands ORDER BY occurred_at_ms, idempotency_key")], "audit_events": [dict(r) for r in self.conn.execute("SELECT * FROM audit_events ORDER BY occurred_at_ms, id")], "boundaries": {"network": "disabled", "tauri_ipc": "not_used", "real_paths": "not_used", "external_action": "none"}}
