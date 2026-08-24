"""Task-local, offline SQLite capture runtime for LIFEOS-P3-096.

The runtime intentionally supports one process and one task-local directory. It
does not claim hostile concurrent path-swap, crash, WAL-recovery, or network-FS
support. Every public entry point still uses one descriptor-backed path gate and
fails closed when that finite boundary cannot be proved.
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import stat
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class CaptureError(Exception):
    """Safe, user-visible failure without source text."""


SCHEMA = """
CREATE TABLE IF NOT EXISTS captures (
  id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at TEXT NOT NULL,
  source TEXT NOT NULL CHECK(source = 'local_capture'), idem_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, capture_id TEXT,
  created_at TEXT NOT NULL, detail TEXT NOT NULL
);
"""

DB_NAME = "capture.sqlite"
PAGE_NAME = "today.html"
SIDECAR_SUFFIXES = ("-journal", "-wal", "-shm")
_CLEAR_DETAIL = re.compile(r"^count=(0|[1-9][0-9]*);today_view=invalidated$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _boundary_error(operation: str, detail: str) -> CaptureError:
    noun = {"capture": "捕获", "list": "读取", "snapshot": "快照", "render": "生成", "clear": "清理"}[operation]
    return CaptureError(f"{noun}失败：{detail}，文件与数据库未更改。")


class _PathGate:
    def __init__(self, operation: str, db_path: Path, page_path: Path, parent_fd: int,
                 parent_identity: tuple[int, int], db_identity: tuple[int, int, int] | None,
                 page_identity: tuple[int, int, int] | None, sidecars: tuple[str, ...]) -> None:
        self.operation = operation
        self.db_path = db_path
        self.page_path = page_path
        self.parent_fd = parent_fd
        self.parent_identity = parent_identity
        self.db_identity = db_identity
        self.page_identity = page_identity
        self.sidecars = sidecars

    def close(self) -> None:
        if self.parent_fd >= 0:
            os.close(self.parent_fd)
            self.parent_fd = -1

    def __enter__(self) -> "_PathGate":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def assert_parent_stable(self) -> None:
        current = os.fstat(self.parent_fd)
        if (current.st_dev, current.st_ino) != self.parent_identity or not stat.S_ISDIR(current.st_mode):
            raise _boundary_error(self.operation, "数据库父目录在操作期间发生变化")

    def assert_db_stable(self, *, allow_missing: bool = False) -> None:
        self.assert_parent_stable()
        try:
            current = os.stat(DB_NAME, dir_fd=self.parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            if allow_missing and self.db_identity is None:
                return
            raise _boundary_error(self.operation, "数据库对象在操作期间消失")
        if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
            raise _boundary_error(self.operation, "数据库对象在操作期间失去普通单链接文件边界")
        identity = (current.st_dev, current.st_ino, current.st_nlink)
        if self.db_identity is not None and identity != self.db_identity:
            raise _boundary_error(self.operation, "数据库对象在操作期间被替换")


def _raw_path(value: os.PathLike[str] | str) -> tuple[str, Path]:
    try:
        raw = os.fspath(value)
    except TypeError as exc:
        raise CaptureError("数据库路径边界无法确认。") from exc
    if not isinstance(raw, str) or not raw:
        raise CaptureError("数据库路径边界无法确认。")
    return raw, Path(raw)


def _exists_at(parent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise CaptureError("本地文件状态无法确认。") from exc


def _open_path_gate(db_path: os.PathLike[str] | str, operation: str) -> _PathGate:
    """Validate one exact task-local DB and its sibling display capability."""
    raw, path = _raw_path(db_path)
    if not raw.startswith("/") or not path.is_absolute() or path.name != DB_NAME:
        raise _boundary_error(operation, "数据库必须是绝对路径且文件名为 capture.sqlite")
    if raw != os.path.normpath(raw) or "//" in raw or "/./" in raw or "/../" in raw or raw.endswith(("/.", "/..", "/")):
        raise _boundary_error(operation, "数据库路径词法规范化后不严格等价")

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        parent_fd = os.open("/", flags)
    except OSError as exc:
        raise _boundary_error(operation, "根目录边界无法确认") from exc
    try:
        for component in path.parent.parts[1:]:
            try:
                next_fd = os.open(component, flags, dir_fd=parent_fd)
            except OSError as exc:
                raise _boundary_error(operation, "父目录缺失或目录组件不是无链接真实目录") from exc
            os.close(parent_fd)
            parent_fd = next_fd
        parent_stat = os.fstat(parent_fd)
        if not stat.S_ISDIR(parent_stat.st_mode):
            raise _boundary_error(operation, "数据库父对象不是目录")

        def inspect(name: str) -> tuple[int, int, int] | None:
            try:
                item = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                return None
            except OSError as exc:
                raise _boundary_error(operation, f"{name} 类型无法确认") from exc
            if not stat.S_ISREG(item.st_mode) or item.st_nlink != 1:
                raise _boundary_error(operation, f"{name} 不是允许的普通单链接文件")
            return (item.st_dev, item.st_ino, item.st_nlink)

        db_identity = inspect(DB_NAME)
        page_identity = inspect(PAGE_NAME)
        sidecars = tuple(suffix for suffix in SIDECAR_SUFFIXES if _exists_at(parent_fd, DB_NAME + suffix))
        return _PathGate(operation, path, path.parent / PAGE_NAME, parent_fd,
                         (parent_stat.st_dev, parent_stat.st_ino), db_identity, page_identity, sidecars)
    except Exception:
        os.close(parent_fd)
        raise


def _normalize_sql(sql: str | None) -> str | None:
    return None if sql is None else " ".join(sql.strip().split()).lower()


def _schema_contract_from_connection(conn: sqlite3.Connection) -> dict[str, Any]:
    master = [
        {"type": row[0], "name": row[1], "table": row[2], "sql": _normalize_sql(row[3])}
        for row in conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
    ]
    tables: dict[str, Any] = {}
    indexes: dict[str, Any] = {}
    for table in ("captures", "audit"):
        tables[table] = [list(row) for row in conn.execute(f"PRAGMA table_xinfo({table})").fetchall()]
        table_indexes = []
        for row in conn.execute(f"PRAGMA index_list({table})").fetchall():
            name = row[1]
            table_indexes.append(list(row[1:]))
            indexes[name] = [list(item) for item in conn.execute(f"PRAGMA index_xinfo('{name}')").fetchall()]
        indexes[f"@{table}"] = table_indexes
    return {"master": master, "tables": tables, "indexes": indexes}


def canonical_schema_contract() -> dict[str, Any]:
    """Return the structured contract generated from the unchanged SCHEMA."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(SCHEMA)
        return _schema_contract_from_connection(conn)
    finally:
        conn.close()


_CANONICAL_SCHEMA = canonical_schema_contract()


def _open_read_only(gate: _PathGate) -> sqlite3.Connection:
    if gate.db_identity is None:
        raise CaptureError("数据库不存在，未显示任何记录。")
    if gate.sidecars:
        raise CaptureError("数据库存在未支持的 sidecar 状态，未显示任何记录。")
    try:
        conn = sqlite3.connect(f"{gate.db_path.as_uri()}?mode=ro&immutable=1", uri=True)
        conn.execute("PRAGMA query_only = ON")
        gate.assert_db_stable()
        if conn.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise CaptureError("数据库完整性检查失败，未显示任何记录。")
        if _schema_contract_from_connection(conn) != _CANONICAL_SCHEMA:
            raise CaptureError("数据库结构或约束不符合 canonical 合同，未显示任何记录。")
        return conn
    except CaptureError:
        if "conn" in locals(): conn.close()
        raise
    except (sqlite3.DatabaseError, OSError, ValueError) as exc:
        if "conn" in locals(): conn.close()
        raise CaptureError("数据库不可读，未显示任何记录。") from exc


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise CaptureError("记录时间格式不可信，未显示任何记录。") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CaptureError("记录时间缺少时区，未显示任何记录。")
    return parsed


def _valid_uuid4(value: str) -> bool:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        return False
    return parsed.version == 4 and str(parsed) == value


def _validated_records(conn: sqlite3.Connection) -> list[dict[str, str]]:
    capture_rows = conn.execute(
        "SELECT id,content,created_at,source,idem_key,typeof(id),typeof(content),"
        "typeof(created_at),typeof(source),typeof(idem_key) FROM captures ORDER BY created_at,id"
    ).fetchall()
    records: list[dict[str, str]] = []
    ids: set[str] = set(); keys: set[str] = set(); created: dict[str, datetime] = {}
    future_limit = datetime.now(timezone.utc) + timedelta(minutes=5)
    for row in capture_rows:
        values = row[:5]
        if row[5:] != ("text", "text", "text", "text", "text") or not all(isinstance(v, str) for v in values):
            raise CaptureError("记录字段类型不可信，未显示任何记录。")
        capture_id, content, created_at, source, idem_key = values
        if not _valid_uuid4(capture_id) or not content.strip() or not idem_key.strip() or source != "local_capture":
            raise CaptureError("记录身份、来源或内容不可信，未显示任何记录。")
        if capture_id in ids or idem_key in keys:
            raise CaptureError("记录身份或幂等键重复，未显示任何记录。")
        capture_time = _parse_timestamp(created_at)
        if capture_time > future_limit:
            raise CaptureError("记录时间位于未来，未显示任何记录。")
        ids.add(capture_id); keys.add(idem_key); created[capture_id] = capture_time
        records.append({"id": capture_id, "content": content, "created_at": created_at,
                        "source": source, "idem_key": idem_key})

    audit_rows = conn.execute(
        "SELECT id,event,capture_id,created_at,detail,typeof(id),typeof(event),"
        "typeof(capture_id),typeof(created_at),typeof(detail) FROM audit ORDER BY id"
    ).fetchall()
    active: set[str] = set()
    saved: dict[str, tuple[int, datetime]] = {}
    seen_audit_ids: set[int] = set()
    previous_audit_time: datetime | None = None
    for row in audit_rows:
        audit_id, event, capture_id, created_at, detail = row[:5]; types = row[5:]
        if types[0] != "integer" or types[1] != "text" or types[3:] != ("text", "text"):
            raise CaptureError("审计字段类型不可信，未显示任何记录。")
        if not isinstance(audit_id, int) or audit_id <= 0 or audit_id in seen_audit_ids:
            raise CaptureError("审计身份不可信，未显示任何记录。")
        seen_audit_ids.add(audit_id); audit_time = _parse_timestamp(created_at)
        if audit_time > future_limit or (previous_audit_time is not None and audit_time < previous_audit_time):
            raise CaptureError("审计时间顺序不可信，未显示任何记录。")
        previous_audit_time = audit_time
        if event == "captures_cleared":
            if types[2] != "null" or capture_id is not None or not _CLEAR_DETAIL.fullmatch(detail):
                raise CaptureError("清理审计不可信，未显示任何记录。")
            declared_count = int(_CLEAR_DETAIL.fullmatch(detail).group(1))
            if declared_count != len(active):
                raise CaptureError("清理审计计数与历史状态不一致，未显示任何记录。")
            active.clear()
        elif event in ("capture_saved", "capture_repeat"):
            expected = "local_capture" if event == "capture_saved" else "same_idempotency_key"
            if types[2] != "text" or not isinstance(capture_id, str) or detail != expected:
                raise CaptureError("捕获审计不可信，未显示任何记录。")
            if event == "capture_saved":
                if capture_id in active or capture_id in saved:
                    raise CaptureError("capture_saved 审计重复，未显示任何记录。")
                saved[capture_id] = (audit_id, audit_time); active.add(capture_id)
            elif capture_id not in active or capture_id not in saved or audit_time < saved[capture_id][1]:
                raise CaptureError("capture_repeat 审计顺序不可信，未显示任何记录。")
        else:
            raise CaptureError("存在未允许的审计事件，未显示任何记录。")
    if active != ids:
        raise CaptureError("当前记录与审计重放状态不一致，未显示任何记录。")
    for capture_id in ids:
        match = saved.get(capture_id)
        if match is None or match[1] != created[capture_id]:
            raise CaptureError("记录与 capture_saved 审计不一致，未显示任何记录。")
    return records


def _read_validated(gate: _PathGate) -> list[dict[str, str]]:
    conn = _open_read_only(gate)
    try:
        records = _validated_records(conn); gate.assert_db_stable(); return records
    except CaptureError:
        raise
    except (sqlite3.DatabaseError, OSError) as exc:
        raise CaptureError("读取失败：未显示部分记录。") from exc
    finally:
        conn.close()


def _audit(conn: sqlite3.Connection, event: str, capture_id: str | None, detail: str,
           *, created_at: str | None = None) -> None:
    conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES(?,?,?,?)",
                 (event, capture_id, created_at or _now(), detail))


def _unlink_exact(gate: _PathGate, name: str, *, missing_ok: bool = True) -> None:
    try:
        os.unlink(name, dir_fd=gate.parent_fd)
    except FileNotFoundError:
        if not missing_ok: raise


def _invalidate_today(gate: _PathGate) -> None:
    noun = "清理" if gate.operation == "clear" else "生成"
    try:
        _unlink_exact(gate, PAGE_NAME)
    except OSError as exc:
        raise CaptureError(f"{noun}失败：内部今日页无法失效，数据库未更改。") from exc
    if _exists_at(gate.parent_fd, PAGE_NAME):
        raise CaptureError(f"{noun}失败：内部今日页仍可展示，数据库未更改。")


def _invalidate_then_raise(gate: _PathGate, failure: CaptureError) -> None:
    try:
        _invalidate_today(gate)
    except CaptureError as exc:
        raise CaptureError("今日页生成失败：数据库内容无法确认，且既有今日页无法失效；数据库未更改。") from exc
    raise failure


def _cleanup_temp(gate: _PathGate, names: list[str]) -> None:
    errors = []
    for name in names:
        last_error = None
        for _ in range(3):
            try:
                _unlink_exact(gate, name); last_error = None; break
            except OSError as exc:
                last_error = exc
        if last_error is not None: errors.append(last_error)
    if errors: raise CaptureError("临时工件无法清理，操作未报告成功。") from errors[0]


def _stage_page(gate: _PathGate) -> str | None:
    if gate.page_identity is None: return None
    staged = f".today.html.{uuid.uuid4().hex}.stale"
    os.rename(PAGE_NAME, staged, src_dir_fd=gate.parent_fd, dst_dir_fd=gate.parent_fd)
    if _exists_at(gate.parent_fd, PAGE_NAME): raise CaptureError("既有今日页无法失效，数据库未更改。")
    return staged


def _page_backup(gate: _PathGate) -> bytes | None:
    if gate.page_identity is None:
        return None
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(PAGE_NAME, flags, dir_fd=gate.parent_fd)
    try:
        current = os.fstat(fd)
        if (current.st_dev, current.st_ino, current.st_nlink) != gate.page_identity or not stat.S_ISREG(current.st_mode):
            raise _boundary_error(gate.operation, "内部今日页在备份前发生变化")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            return handle.read()
    finally:
        os.close(fd)


def _restore_page(gate: _PathGate, staged: str | None, backup: bytes | None = None) -> None:
    if staged is not None and _exists_at(gate.parent_fd, staged):
        os.rename(staged, PAGE_NAME, src_dir_fd=gate.parent_fd, dst_dir_fd=gate.parent_fd)
        return
    if backup is None or _exists_at(gate.parent_fd, PAGE_NAME):
        return
    temp = f".today.html.{uuid.uuid4().hex}.restore"
    fd = -1
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temp, flags, 0o600, dir_fd=gate.parent_fd)
        with os.fdopen(fd, "wb") as handle:
            fd = -1; handle.write(backup); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, PAGE_NAME, src_dir_fd=gate.parent_fd, dst_dir_fd=gate.parent_fd); temp = ""
    finally:
        if fd >= 0: os.close(fd)
        if temp: _unlink_exact(gate, temp)


def _create_new_capture(gate: _PathGate, content: str, idem_key: str, inject_failure: bool) -> dict:
    temp = f".capture.sqlite.{uuid.uuid4().hex}.tmp"; staged = None; fd = -1
    page_backup = _page_backup(gate)
    try:
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temp, flags, 0o600, dir_fd=gate.parent_fd); os.close(fd); fd = -1
        temp_path = gate.db_path.parent / temp
        conn = sqlite3.connect(temp_path)
        try:
            conn.executescript(SCHEMA); conn.execute("BEGIN IMMEDIATE")
            capture_id = str(uuid.uuid4())
            created_at = _now()
            conn.execute("INSERT INTO captures(id,content,created_at,source,idem_key) VALUES(?,?,?,'local_capture',?)",
                         (capture_id, content, created_at, idem_key))
            _audit(conn, "capture_saved", capture_id, "local_capture", created_at=created_at)
            if inject_failure: raise sqlite3.OperationalError("injected_atomic_failure")
            if _schema_contract_from_connection(conn) != _CANONICAL_SCHEMA: raise sqlite3.DatabaseError("schema mismatch")
            _validated_records(conn); conn.commit()
        finally: conn.close()
        if any(_exists_at(gate.parent_fd, temp + suffix) for suffix in SIDECAR_SUFFIXES):
            raise CaptureError("新数据库初始化留下未支持的 sidecar。")
        with open(temp_path, "rb") as handle: os.fsync(handle.fileno())
        staged = _stage_page(gate)
        if staged is not None:
            _cleanup_temp(gate, [staged]); staged = None
        os.replace(temp, DB_NAME, src_dir_fd=gate.parent_fd, dst_dir_fd=gate.parent_fd); temp = ""
        gate.assert_parent_stable(); return {"status": "saved", "id": capture_id}
    except CaptureError:
        _restore_page(gate, staged, page_backup); raise
    except (sqlite3.DatabaseError, OSError) as exc:
        _restore_page(gate, staged, page_backup); raise CaptureError("保存失败：未显示成功，也未保留半成品。") from exc
    finally:
        if fd >= 0: os.close(fd)
        if temp: _cleanup_temp(gate, [temp, *(temp + suffix for suffix in SIDECAR_SUFFIXES)])


def capture(db_path: os.PathLike[str] | str, content: str, idem_key: str, *, inject_failure: bool = False) -> dict:
    with _open_path_gate(db_path, "capture") as gate:
        if not isinstance(content, str) or not content.strip(): raise CaptureError("捕获被拒绝：内容不能为空。")
        if not isinstance(idem_key, str) or not idem_key.strip(): raise CaptureError("捕获被拒绝：缺少幂等键。")
        if gate.sidecars: raise CaptureError("捕获被拒绝：数据库存在未支持的 sidecar 状态。")
        if gate.db_identity is None: return _create_new_capture(gate, content, idem_key, inject_failure)
        _read_validated(gate); before_hash = hashlib.sha256(gate.db_path.read_bytes()).hexdigest()
        page_backup = _page_backup(gate)
        committed = False
        try:
            conn = sqlite3.connect(f"{gate.db_path.as_uri()}?mode=rw", uri=True)
            prior = conn.execute("SELECT id,content,created_at FROM captures WHERE idem_key=?", (idem_key,)).fetchone()
            if prior:
                if prior[1] != content: raise CaptureError("捕获被拒绝：幂等键与已有记录冲突。")
                with conn: _audit(conn, "capture_repeat", prior[0], "same_idempotency_key"); _validated_records(conn)
                committed = True
                return {"status": "idempotent_repeat", "id": prior[0], "created_at": prior[2]}
            staged = None
            try:
                conn.execute("BEGIN IMMEDIATE"); capture_id = str(uuid.uuid4())
                created_at = _now()
                conn.execute("INSERT INTO captures(id,content,created_at,source,idem_key) VALUES(?,?,?,'local_capture',?)",
                             (capture_id, content, created_at, idem_key))
                _audit(conn, "capture_saved", capture_id, "local_capture", created_at=created_at)
                if inject_failure: raise sqlite3.OperationalError("injected_atomic_failure")
                _validated_records(conn); staged = _stage_page(gate)
                if staged is not None:
                    _cleanup_temp(gate, [staged]); staged = None
                conn.commit()
                committed = True
            except Exception:
                conn.rollback(); _restore_page(gate, staged, page_backup)
                if hashlib.sha256(gate.db_path.read_bytes()).hexdigest() != before_hash:
                    raise CaptureError("保存失败且数据库原子性无法确认。")
                raise
            return {"status": "saved", "id": capture_id}
        except CaptureError: raise
        except (sqlite3.DatabaseError, OSError) as exc:
            raise CaptureError("保存失败：未显示成功，也未保留半成品。") from exc
        finally:
            if "conn" in locals():
                try:
                    conn.close()
                except (sqlite3.DatabaseError, OSError):
                    if not committed:
                        raise
            gate.assert_db_stable()
            if any(_exists_at(gate.parent_fd, DB_NAME + suffix) for suffix in SIDECAR_SUFFIXES):
                raise CaptureError("保存结束后存在未支持的 sidecar，未报告成功。")


def list_today(db_path: os.PathLike[str] | str) -> list[dict]:
    with _open_path_gate(db_path, "list") as gate:
        return [{key: row[key] for key in ("id", "content", "created_at", "source")} for row in _read_validated(gate)]


def safe_snapshot(db_path: os.PathLike[str] | str) -> dict:
    with _open_path_gate(db_path, "snapshot") as gate:
        records = _read_validated(gate)
        return {"record_count": len(records), "ids": [row["id"] for row in records],
                "content_sha256": [hashlib.sha256(row["content"].encode()).hexdigest() for row in records]}


def render_today(db_path: os.PathLike[str] | str, output_path: Path | None = None) -> dict:
    from html import escape
    if output_path is not None:
        with _open_path_gate(db_path, "render"): raise _boundary_error("render", "不接受调用方指定的展示目标")
    with _open_path_gate(db_path, "render") as gate:
        try: records = _read_validated(gate)
        except CaptureError as exc: _invalidate_then_raise(gate, exc)
        if not records: _invalidate_then_raise(gate, CaptureError("今日页未生成：没有可信记录，既有今日页已失效。"))
        cards = "\n".join(
            f"<article><p class='label'>用户原文</p><p>{escape(row['content'])}</p>"
            f"<p class='meta'>记录时间：{escape(row['created_at'])} · 来源：本地捕获</p></article>" for row in records)
        document = f"""<!doctype html><meta charset='utf-8'><title>LifeOS 今日页（内部）</title>
<style>body{{font-family:-apple-system,sans-serif;background:#f6f7fb;color:#182033;max-width:760px;margin:48px auto;padding:0 20px}}article{{background:#fff;border-radius:14px;padding:18px 20px;margin:14px 0;box-shadow:0 2px 12px #18203314}}.label{{color:#57657c;font-weight:650}}.meta{{color:#65738b;font-size:.9rem}}</style>
<main><h1>今日</h1><p>内部本地展示 · 不同步、不导出</p>{cards}</main>"""
        temp = f".today.html.{uuid.uuid4().hex}.tmp"; fd = -1
        try:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(temp, flags, 0o600, dir_fd=gate.parent_fd)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                fd = -1; handle.write(document); handle.flush(); os.fsync(handle.fileno())
            gate.assert_db_stable()
            if _exists_at(gate.parent_fd, PAGE_NAME):
                current = os.stat(PAGE_NAME, dir_fd=gate.parent_fd, follow_symlinks=False)
                if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
                    raise _boundary_error("render", "内部今日页在发布前失去普通单链接边界")
            os.replace(temp, PAGE_NAME, src_dir_fd=gate.parent_fd, dst_dir_fd=gate.parent_fd); temp = ""
            gate.assert_db_stable()
        except CaptureError: raise
        except OSError as exc: raise CaptureError("今日页生成失败：未显示成功，既有可信页面保持不变。") from exc
        finally:
            if fd >= 0: os.close(fd)
            if temp: _cleanup_temp(gate, [temp])
        return {"status": "rendered", "record_count": len(records), "path": str(gate.page_path)}


def delete_all(db_path: os.PathLike[str] | str, confirmation: str, output_path: Path | None = None) -> dict:
    if output_path is not None:
        with _open_path_gate(db_path, "clear"): raise _boundary_error("clear", "不接受调用方指定的展示目标")
    with _open_path_gate(db_path, "clear") as gate:
        if confirmation != "DELETE": raise CaptureError("清理被拒绝：需要精确确认 DELETE。")
        try: records = _read_validated(gate)
        except CaptureError as exc: _invalidate_then_raise(gate, exc)
        _invalidate_today(gate)
        try:
            conn = sqlite3.connect(f"{gate.db_path.as_uri()}?mode=rw", uri=True); conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM captures")
            _audit(conn, "captures_cleared", None, f"count={len(records)};today_view=invalidated")
            _validated_records(conn); conn.commit()
        except (sqlite3.DatabaseError, CaptureError) as exc:
            if "conn" in locals(): conn.rollback()
            raise CaptureError("清理失败：数据库事务已回滚，内部今日页保持失效。") from exc
        finally:
            if "conn" in locals(): conn.close()
        gate.assert_db_stable()
        if any(_exists_at(gate.parent_fd, DB_NAME + suffix) for suffix in SIDECAR_SUFFIXES):
            raise CaptureError("清理结束后存在未支持的 sidecar，未报告成功。")
        return {"status": "cleared", "count": len(records), "today_view": "invalidated"}
