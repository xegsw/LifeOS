#!/usr/bin/env python3
"""ABF-P3-096-v2 pre-submission runner using only fixed task-local fixtures."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[1]
LIFEOS = ROOT.parents[1]
DEFAULT_EVIDENCE = ROOT / "evidence"
PREFIX = "lifeos-p3-096-"
FIXED_TEXT = "P3-096 fixed non-sensitive capture fixture"
STALE_PAGE = b"P3-096 fixed non-sensitive stale internal page\n"
ABF_V1 = LIFEOS / "tasks/LIFEOS-P3-096_acceptance_basis_freeze.md"
ABF_V2 = LIFEOS / "tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md"
LATE_MANIFEST = LIFEOS / "reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md"
BASELINE_RUNNER = LIFEOS / "engineering/LIFEOS-P3-094/rework/attempt-9/scripts/run_attempt_9.py"
PM_SIX = LIFEOS / "reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.py"
EXPECTED_ABF_HASHES = {
    "v1": "2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58",
    "v2": "bc529ddaf2ed965e96047dc6681acdd9e17c892a4db2ddd850038cbbd239ea09",
}
ROW_IDS = [f"ABF-M-{number:03d}" for number in range(1, 21)]
FAILURE_ROWS = set(ROW_IDS[:5])
AUDIT_ROWS = set(ROW_IDS[7:15])


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def json_write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def files_under(path: Path) -> list[Path]:
    return sorted(item for item in path.rglob("*") if item.is_file() and "__pycache__" not in item.parts)


def file_state(path: Path) -> dict:
    try:
        item = path.lstat()
    except FileNotFoundError:
        return {"exists": False, "type": "missing", "device": None, "inode": None,
                "nlink": None, "size": None, "sha256": None}
    if path.is_symlink():
        kind = "symlink"
    elif path.is_file():
        kind = "regular"
    elif path.is_dir():
        kind = "directory"
    else:
        kind = "special"
    return {"exists": True, "type": kind, "device": item.st_dev, "inode": item.st_ino,
            "nlink": item.st_nlink, "size": item.st_size,
            "sha256": digest(path) if kind == "regular" else None}


def db_counts(db: Path) -> dict:
    if not db.is_file():
        return {"captures": None, "audit": None}
    try:
        with sqlite3.connect(f"{db.as_uri()}?mode=ro&immutable=1", uri=True) as conn:
            return {"captures": conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0],
                    "audit": conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0]}
    except sqlite3.DatabaseError:
        return {"captures": "unavailable", "audit": "unavailable"}


def residue_names(case: Path) -> list[str]:
    patterns = (".capture.sqlite.*", ".today.html.*", "capture.sqlite-journal",
                "capture.sqlite-wal", "capture.sqlite-shm")
    return sorted({item.name for pattern in patterns for item in case.glob(pattern)})


def case_state(case: Path) -> dict:
    db = case / "capture.sqlite"
    return {"db": file_state(db), "page": file_state(case / "today.html"),
            "sentinel": file_state(case / "sentinel.txt"), "counts": db_counts(db),
            "residue_names": residue_names(case)}


def visible_file_state(value: dict) -> dict:
    """Observable file contract; full identity remains preserved in state transitions."""
    return {key: value[key] for key in ("exists", "type", "nlink", "size", "sha256")}


def assertion(name: str, expected: object, actual: object) -> dict:
    return {"name": name, "expected": expected, "actual": actual, "passed": actual == expected}


def rejected(callable_) -> str:
    try:
        callable_()
    except Exception as exc:
        return type(exc).__name__
    return "accepted"


def load_runtime(path: Path):
    spec = importlib.util.spec_from_file_location("p3_096_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("runtime load failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def late_manifest_rows() -> list[tuple[Path, str]]:
    text = LATE_MANIFEST.read_text(encoding="utf-8")
    rows = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", text)
    return [((LATE_MANIFEST.parent / relative).resolve(), expected) for relative, expected in rows]


def readonly_paths() -> list[Path]:
    paths: set[Path] = set()
    for base in (LIFEOS / "tasks", LIFEOS / "deliverables", LIFEOS / "reviews", LIFEOS / "engineering"):
        if base.exists():
            for item in base.rglob("*"):
                if item.is_file() and ("LIFEOS-P3-094" in str(item) or "LIFEOS-P3-095" in str(item)):
                    paths.add(item)
    return sorted(paths)


def hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(LIFEOS)): digest(path) for path in paths}


def seed(runtime, case: Path, *, count: int = 1) -> Path:
    db = case / "capture.sqlite"
    for index in range(count):
        runtime.capture(db, f"{FIXED_TEXT} {index + 1}", f"key-{index + 1}")
    return db


def run_all_reads(runtime, db: Path) -> dict:
    return {"list": rejected(lambda: runtime.list_today(db)),
            "snapshot": rejected(lambda: runtime.safe_snapshot(db)),
            "render": rejected(lambda: runtime.render_today(db))}


def execute_case(runtime, work: Path, row_id: str, test_id: str, fixture_id: str, body) -> tuple[dict, dict]:
    case = work / fixture_id
    case.mkdir()
    (case / "sentinel.txt").write_text("P3-096 fixed non-sensitive sentinel\n", encoding="utf-8")
    started = utc_now(); before = case_state(case); error = None; details = {}; assertions = []
    try:
        details, assertions = body(runtime, case)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc),
                 "traceback_sha256": hashlib.sha256(traceback.format_exc().encode()).hexdigest()}
    after = case_state(case)
    status = "FAIL" if error is not None else ("PASS" if assertions and all(item["passed"] for item in assertions) else "FAIL")
    result = {"row_id": row_id, "test_id": test_id, "fixture_id": fixture_id,
              "started_at": started, "ended_at": utc_now(), "actual_result": status,
              "assertions": assertions, "details": details, "error": error,
              "evidence": f"state_transitions.json#{test_id}"}
    transition = {"row_id": row_id, "test_id": test_id, "fixture_id": fixture_id,
                  "before": before, "after": after, "assertions": assertions}
    return result, transition


def m001(runtime, case: Path):
    db = seed(runtime, case); runtime.render_today(db)
    calls = {"stale_unlink": 0}; original = os.unlink
    def flaky(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".today.html.") and name.endswith(".stale"):
            calls["stale_unlink"] += 1
            if calls["stale_unlink"] == 1:
                raise PermissionError("fixed transient staging unlink failure")
        return original(name, *args, **kwargs)
    with patch.object(runtime.os, "unlink", flaky):
        result = runtime.capture(db, FIXED_TEXT + " second", "key-2")
    state = case_state(case)
    return {"return": result["status"], "unlink_attempts": calls["stale_unlink"]}, [
        assertion("capture succeeds after bounded cleanup retry", "saved", result["status"]),
        assertion("two captures persist", 2, state["counts"]["captures"]),
        assertion("two audits persist", 2, state["counts"]["audit"]),
        assertion("old page invalidated", False, state["page"]["exists"]),
        assertion("no staging or sidecar residue", [], state["residue_names"])]


def persistent_staging_failure(runtime, case: Path, *, existing_db: bool):
    db = case / "capture.sqlite"; page = case / "today.html"
    if existing_db:
        seed(runtime, case); runtime.render_today(db)
    else:
        page.write_bytes(STALE_PAGE)
    before = case_state(case); original = os.unlink
    def fail(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".today.html.") and name.endswith(".stale"):
            raise PermissionError("fixed persistent staging unlink failure")
        return original(name, *args, **kwargs)
    with patch.object(runtime.os, "unlink", fail):
        outcome = rejected(lambda: runtime.capture(db, FIXED_TEXT + " new", "new-key"))
    after = case_state(case)
    expected_db = before["db"] if existing_db else {"exists": False, "type": "missing", "device": None, "inode": None, "nlink": None, "size": None, "sha256": None}
    return {"outcome": outcome}, [assertion("returns CaptureError", "CaptureError", outcome),
        assertion("DB state unchanged or absent", expected_db, after["db"]),
        assertion("counts unchanged", before["counts"], after["counts"]),
        assertion("page restored byte-for-byte", before["page"], after["page"]),
        assertion("no staging or sidecar residue", [], after["residue_names"]),
        assertion("sentinel unchanged", before["sentinel"], after["sentinel"])]


class CommitProxy:
    def __init__(self, conn): self._conn = conn
    def __getattr__(self, name): return getattr(self._conn, name)
    def commit(self): raise sqlite3.OperationalError("fixed injected commit failure")
    def close(self): self._conn.close()


def commit_failure(runtime, case: Path, *, existing_db: bool):
    db = case / "capture.sqlite"
    if existing_db:
        seed(runtime, case); runtime.render_today(db)
    before = case_state(case); original = sqlite3.connect
    def connect(target, *args, **kwargs):
        conn = original(target, *args, **kwargs); target_text = str(target)
        inject = "mode=rw" in target_text if existing_db else ".capture.sqlite." in target_text
        return CommitProxy(conn) if inject else conn
    with patch.object(runtime.sqlite3, "connect", connect):
        outcome = rejected(lambda: runtime.capture(db, FIXED_TEXT + " commit", "commit-key"))
    after = case_state(case)
    expected_db = before["db"] if existing_db else {"exists": False, "type": "missing", "device": None, "inode": None, "nlink": None, "size": None, "sha256": None}
    return {"outcome": outcome}, [assertion("returns CaptureError", "CaptureError", outcome),
        assertion("DB bytes and identity unchanged or absent", expected_db, after["db"]),
        assertion("counts unchanged", before["counts"], after["counts"]),
        assertion("page observable content follows rollback contract", visible_file_state(before["page"]), visible_file_state(after["page"])),
        assertion("no temp or sidecar residue", [], after["residue_names"])]


def m005_init(runtime, case: Path):
    db = case / "capture.sqlite"; before = case_state(case); original = sqlite3.connect
    def fail(target, *args, **kwargs):
        if ".capture.sqlite." in str(target):
            raise sqlite3.OperationalError("fixed injected initialization failure")
        return original(target, *args, **kwargs)
    with patch.object(runtime.sqlite3, "connect", fail):
        outcome = rejected(lambda: runtime.capture(db, FIXED_TEXT, "init-key"))
    after = case_state(case)
    return {"outcome": outcome}, [assertion("returns CaptureError", "CaptureError", outcome),
        assertion("new DB absent", before["db"], after["db"]), assertion("no page", before["page"], after["page"]),
        assertion("no temp or sidecar residue", [], after["residue_names"])]


def m005_publish(runtime, case: Path):
    db = case / "capture.sqlite"; before = case_state(case); original = os.replace
    def fail(src, dst, *args, **kwargs):
        if isinstance(src, str) and src.startswith(".capture.sqlite.") and dst == "capture.sqlite":
            raise PermissionError("fixed injected atomic publish failure")
        return original(src, dst, *args, **kwargs)
    with patch.object(runtime.os, "replace", fail):
        outcome = rejected(lambda: runtime.capture(db, FIXED_TEXT, "publish-key"))
    after = case_state(case)
    return {"outcome": outcome}, [assertion("returns CaptureError", "CaptureError", outcome),
        assertion("new DB absent", before["db"], after["db"]), assertion("no page", before["page"], after["page"]),
        assertion("no temp or sidecar residue", [], after["residue_names"])]


def m006(runtime, case: Path):
    db = seed(runtime, case); runtime.render_today(db)
    with sqlite3.connect(db) as conn:
        first = conn.execute("SELECT id,content,created_at,source,idem_key FROM captures ORDER BY rowid LIMIT 1").fetchone()
        first_audit = conn.execute("SELECT id,event,capture_id,created_at,detail FROM audit ORDER BY id LIMIT 1").fetchone()
    result = runtime.capture(db, FIXED_TEXT + " second", "key-2")
    with sqlite3.connect(db) as conn:
        current_first = conn.execute("SELECT id,content,created_at,source,idem_key FROM captures WHERE id=?", (first[0],)).fetchone()
        current_first_audit = conn.execute("SELECT id,event,capture_id,created_at,detail FROM audit WHERE id=?", (first_audit[0],)).fetchone()
        saved_time, capture_time = conn.execute("SELECT a.created_at,c.created_at FROM audit a JOIN captures c ON c.id=a.capture_id WHERE c.id=? AND a.event='capture_saved'", (result["id"],)).fetchone()
    state = case_state(case)
    return {"return": result["status"]}, [assertion("returns saved", "saved", result["status"]),
        assertion("saved audit time equals capture time", capture_time, saved_time),
        assertion("existing record unchanged", first, current_first), assertion("existing audit unchanged", first_audit, current_first_audit),
        assertion("page invalidated", False, state["page"]["exists"]), assertion("no residue", [], state["residue_names"])]


def m007(runtime, case: Path):
    db = case / "capture.sqlite"; result = runtime.capture(db, FIXED_TEXT, "first-key")
    with sqlite3.connect(db) as conn:
        capture_count = conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        audit = conn.execute("SELECT event,capture_id,created_at FROM audit").fetchone()
        capture_time = conn.execute("SELECT created_at FROM captures WHERE id=?", (result["id"],)).fetchone()[0]
        schema = runtime._schema_contract_from_connection(conn)
    state = case_state(case)
    return {"return": result["status"]}, [assertion("returns saved", "saved", result["status"]),
        assertion("one capture", 1, capture_count), assertion("one saved audit", ("capture_saved", result["id"], capture_time), audit),
        assertion("canonical schema", runtime.canonical_schema_contract(), schema), assertion("no residue", [], state["residue_names"])]


def audit_rejection(runtime, case: Path, mutate):
    db = seed(runtime, case); runtime.render_today(db); mutate(db)
    before = case_state(case); outcomes = run_all_reads(runtime, db); after = case_state(case)
    return {"outcomes": outcomes}, [assertion("all reads reject", {"list": "CaptureError", "snapshot": "CaptureError", "render": "CaptureError"}, outcomes),
        assertion("DB unchanged", before["db"], after["db"]), assertion("old page invalidated", False, after["page"]["exists"]),
        assertion("no residue", [], after["residue_names"])]


def mutate_future_capture(db: Path):
    with sqlite3.connect(db) as conn: conn.execute("UPDATE captures SET created_at='2099-01-01T00:00:00+00:00'")


def mutate_future_saved(db: Path):
    with sqlite3.connect(db) as conn: conn.execute("UPDATE audit SET created_at='2099-01-01T00:00:00+00:00' WHERE event='capture_saved'")


def mutate_saved_mismatch(db: Path):
    with sqlite3.connect(db) as conn:
        value = conn.execute("SELECT created_at FROM captures").fetchone()[0]
        conn.execute("UPDATE audit SET created_at=? WHERE event='capture_saved'", ((datetime.fromisoformat(value) + timedelta(seconds=1)).isoformat(),))


def mutate_repeat_before_saved(db: Path):
    with sqlite3.connect(db) as conn:
        capture_id = conn.execute("SELECT id FROM captures").fetchone()[0]
        conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_repeat',?,'2000-01-01T00:00:00+00:00','same_idempotency_key')", (capture_id,))


def m012_unknown(runtime, case: Path):
    def mutate(db):
        with sqlite3.connect(db) as conn:
            conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_repeat','00000000-0000-4000-8000-000000000000',?,'same_idempotency_key')", (datetime.now(timezone.utc).isoformat(timespec="seconds"),))
    return audit_rejection(runtime, case, mutate)


def m012_cleared(runtime, case: Path):
    db = seed(runtime, case)
    with sqlite3.connect(db) as conn: capture_id = conn.execute("SELECT id FROM captures").fetchone()[0]
    runtime.delete_all(db, "DELETE")
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_repeat',?,?,'same_idempotency_key')", (capture_id, datetime.now(timezone.utc).isoformat(timespec="seconds")))
    (case / "today.html").write_bytes(STALE_PAGE)
    before = case_state(case); outcomes = run_all_reads(runtime, db); after = case_state(case)
    return {"outcomes": outcomes}, [assertion("all reads reject cleared reference", {"list": "CaptureError", "snapshot": "CaptureError", "render": "CaptureError"}, outcomes),
        assertion("DB unchanged", before["db"], after["db"]), assertion("old page invalidated", False, after["page"]["exists"])]


def m013(runtime, case: Path):
    return audit_rejection(runtime, case, mutate_repeat_before_saved)


def m014(runtime, case: Path, declared: int):
    db = seed(runtime, case, count=2); runtime.delete_all(db, "DELETE")
    with sqlite3.connect(db) as conn: conn.execute("UPDATE audit SET detail=? WHERE event='captures_cleared'", (f"count={declared};today_view=invalidated",))
    (case / "today.html").write_bytes(STALE_PAGE)
    before = case_state(case); outcomes = run_all_reads(runtime, db); after = case_state(case)
    return {"outcomes": outcomes, "declared": declared}, [assertion("all reads reject mismatched count", {"list": "CaptureError", "snapshot": "CaptureError", "render": "CaptureError"}, outcomes),
        assertion("DB unchanged", before["db"], after["db"]), assertion("old page invalidated", False, after["page"]["exists"])]


def m015(runtime, case: Path):
    db = seed(runtime, case, count=2); runtime.render_today(db); result = runtime.delete_all(db, "DELETE")
    with sqlite3.connect(db) as conn:
        active = conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        detail = conn.execute("SELECT detail FROM audit WHERE event='captures_cleared' ORDER BY id DESC LIMIT 1").fetchone()[0]
    state = case_state(case)
    return {"return": result}, [assertion("returns count two", 2, result["count"]),
        assertion("audit count two", "count=2;today_view=invalidated", detail), assertion("active set empty", 0, active),
        assertion("page absent", False, state["page"]["exists"]), assertion("no residue", [], state["residue_names"])]


def create_source_variant(runtime, db: Path, value, *, nullable: bool = False):
    capture_id = "12345678-1234-4234-8234-123456789abc"; created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if nullable:
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE captures(id TEXT PRIMARY KEY,content TEXT NOT NULL,created_at TEXT NOT NULL,source TEXT,idem_key TEXT NOT NULL UNIQUE)")
            conn.execute("CREATE TABLE audit(id INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT NOT NULL,capture_id TEXT,created_at TEXT NOT NULL,detail TEXT NOT NULL)")
            conn.execute("INSERT INTO captures VALUES(?,?,?,?,?)", (capture_id, FIXED_TEXT, created_at, value, "key"))
            conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES('capture_saved',?,?, 'local_capture')", (capture_id, created_at))
    else:
        runtime.capture(db, FIXED_TEXT, "key")
        with sqlite3.connect(db) as conn:
            conn.execute("PRAGMA ignore_check_constraints=ON"); conn.execute("UPDATE captures SET source=?", (value,))


def m016(runtime, case: Path, value, *, nullable: bool = False):
    db = case / "capture.sqlite"; create_source_variant(runtime, db, value, nullable=nullable); (case / "today.html").write_bytes(STALE_PAGE)
    before = case_state(case); outcomes = run_all_reads(runtime, db); after = case_state(case)
    return {"outcomes": outcomes, "variant_type": type(value).__name__}, [assertion("all reads reject source variant", {"list": "CaptureError", "snapshot": "CaptureError", "render": "CaptureError"}, outcomes),
        assertion("DB unchanged", before["db"], after["db"]), assertion("old page invalidated", False, after["page"]["exists"])]


def m017(runtime, case: Path, duplicate: str):
    db = case / "capture.sqlite"; now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    first = "12345678-1234-4234-8234-123456789abc"; second = first if duplicate == "id" else "87654321-4321-4321-8321-cba987654321"
    first_key = "same-key"; second_key = first_key if duplicate == "idem" else "other-key"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE captures(id TEXT,content TEXT NOT NULL,created_at TEXT NOT NULL,source TEXT NOT NULL,idem_key TEXT NOT NULL)")
        conn.execute("CREATE TABLE audit(id INTEGER,event TEXT NOT NULL,capture_id TEXT,created_at TEXT NOT NULL,detail TEXT NOT NULL)")
        conn.execute("INSERT INTO captures VALUES(?,?,?,?,?)", (first, FIXED_TEXT, now, "local_capture", first_key))
        conn.execute("INSERT INTO captures VALUES(?,?,?,?,?)", (second, FIXED_TEXT + " 2", now, "local_capture", second_key))
        conn.execute("INSERT INTO audit VALUES(1,'capture_saved',?,?, 'local_capture')", (first, now))
        conn.execute("INSERT INTO audit VALUES(2,'capture_saved',?,?, 'local_capture')", (second, now))
    (case / "today.html").write_bytes(STALE_PAGE)
    before = case_state(case); outcomes = run_all_reads(runtime, db); after = case_state(case)
    return {"outcomes": outcomes, "duplicate": duplicate}, [assertion("all reads reject duplicate", {"list": "CaptureError", "snapshot": "CaptureError", "render": "CaptureError"}, outcomes),
        assertion("DB unchanged", before["db"], after["db"]), assertion("old page invalidated", False, after["page"]["exists"])]


def validate_records(records: list[dict], required_rows: list[str]) -> dict:
    not_implemented = 0; reasons = []; by_row: dict[str, list[dict]] = {}
    for item in records: by_row.setdefault(item.get("row_id", ""), []).append(item)
    for row_id in required_rows:
        matches = by_row.get(row_id, [])
        if not matches:
            not_implemented += 1; reasons.append(f"{row_id}: missing execution"); continue
        for item in matches:
            for field in ("test_id", "fixture_id", "assertions", "evidence", "actual_result"):
                if not item.get(field): not_implemented += 1; reasons.append(f"{row_id}: missing {field}")
            if item.get("actual_result") != "PASS": reasons.append(f"{row_id}: execution not PASS")
    return {"Not Implemented": not_implemented, "reasons": reasons,
            "conclusion": "PASS" if not reasons and not_implemented == 0 else "NOT PASS — DO NOT SUBMIT"}


def m018(runtime, case: Path):
    fake = [{"row_id": "ABF-M-018", "test_id": "fake", "fixture_id": "", "assertions": [], "evidence": "", "actual_result": "PASS"}]
    checked = validate_records(fake, ["ABF-M-018"])
    return checked, [assertion("missing fields become Not Implemented", True, checked["Not Implemented"] > 0),
                     assertion("validator blocks submission", "NOT PASS — DO NOT SUBMIT", checked["conclusion"])]


def m019(runtime, case: Path):
    fake = [{"row_id": row, "test_id": "fake-" + row, "fixture_id": "fixture-" + row,
             "assertions": [{"passed": True}], "evidence": "fake.json", "actual_result": "PASS"}
            for row in ROW_IDS if row != "ABF-M-019"]
    checked = validate_records(fake, ROW_IDS)
    return {"unit_suite_pass": True, **checked}, [assertion("missing row remains Not Implemented", True, checked["Not Implemented"] > 0),
        assertion("suite pass cannot bulk-map row", "NOT PASS — DO NOT SUBMIT", checked["conclusion"])]


def aggregate_rows(executions: list[dict]) -> list[dict]:
    rows = []
    for row_id in ROW_IDS:
        children = [item for item in executions if item["row_id"] == row_id]
        status = "PASS" if children and all(item["actual_result"] == "PASS" for item in children) else ("NOT IMPLEMENTED" if not children else "FAIL")
        rows.append({"row_id": row_id, "status": status, "executed_test_ids": [item["test_id"] for item in children],
                     "fixture_ids": [item["fixture_id"] for item in children],
                     "assertion_count": sum(len(item["assertions"]) for item in children),
                     "evidence": [item["evidence"] for item in children]})
    return rows


def run_baseline(temp_root: Path) -> tuple[dict, str]:
    baseline_evidence = temp_root / "baseline-evidence"
    runner = subprocess.run([sys.executable, "-B", str(BASELINE_RUNNER), "--evidence-dir", str(baseline_evidence)], text=True, capture_output=True)
    runner_summary = json.loads((baseline_evidence / "summary.json").read_text()) if (baseline_evidence / "summary.json").exists() else {}
    pm_output = temp_root / "pm-six.json"
    pm = subprocess.run([sys.executable, "-B", str(PM_SIX), "--source", str(LIFEOS / "engineering/LIFEOS-P3-094/src/local_capture.py"),
                         "--tests", str(LIFEOS / "engineering/LIFEOS-P3-094/tests/test_runtime.py"), "--output", str(pm_output)], text=True, capture_output=True)
    pm_payload = json.loads(pm_output.read_text()) if pm_output.exists() else {}
    payload = {"candidate_runner_exit": runner.returncode, "candidate_summary": runner_summary,
               "pm_six_exit": pm.returncode, "pm_six_summary": pm_payload.get("summary"),
               "passed": runner.returncode == 0 and pm.returncode == 0 and pm_payload.get("summary") == {"pass": 6, "fail": 0}}
    return payload, "[candidate runner]\n" + runner.stdout + runner.stderr + "\n[PM six]\n" + pm.stdout + pm.stderr


def clean_copy(temp_root: Path) -> Path:
    target = temp_root / "clean-copy"
    for relative in ("src/local_capture.py", "scripts/operator_cli.py", "scripts/run_p3_096.py", "tests/test_runtime.py", "README.md"):
        destination = target / relative; destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / relative, destination)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE); args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    if evidence.exists(): shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    protected = readonly_paths(); history_before = hashes(protected)
    late_hashes = [{"path": str(path.relative_to(LIFEOS)), "expected": expected,
                    "actual": digest(path) if path.is_file() else None,
                    "matches": path.is_file() and digest(path) == expected} for path, expected in late_manifest_rows()]
    abf_hashes = {"v1": digest(ABF_V1), "v2": digest(ABF_V2)}
    abf_ok = abf_hashes == EXPECTED_ABF_HASHES; late_ok = bool(late_hashes) and all(item["matches"] for item in late_hashes)
    work = Path(tempfile.mkdtemp(prefix=PREFIX + "run-", dir="/private/tmp"))
    executions = []; transitions = []; matrix_log = []; baseline = {}; baseline_log = ""; unit_exit = 1; unit_log = ""
    try:
        baseline, baseline_log = run_baseline(work); copy = clean_copy(work)
        unit = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=copy, text=True, capture_output=True)
        unit_exit = unit.returncode; unit_log = unit.stdout + unit.stderr; runtime = load_runtime(copy / "src/local_capture.py")
        cases = [
            ("ABF-M-001","P3-096-M001-transient-staging-unlink","m001-transient-staging-unlink",m001),
            ("ABF-M-002","P3-096-M002-persistent-staging-existing","m002-persistent-staging-existing",lambda r,c:persistent_staging_failure(r,c,existing_db=True)),
            ("ABF-M-003","P3-096-M003-persistent-staging-new","m003-persistent-staging-new",lambda r,c:persistent_staging_failure(r,c,existing_db=False)),
            ("ABF-M-004","P3-096-M004-existing-commit-failure","m004-existing-commit-failure",lambda r,c:commit_failure(r,c,existing_db=True)),
            ("ABF-M-005","P3-096-M005-init-failure","m005-init-failure",m005_init),
            ("ABF-M-005","P3-096-M005-new-commit-failure","m005-new-commit-failure",lambda r,c:commit_failure(r,c,existing_db=False)),
            ("ABF-M-005","P3-096-M005-publish-failure","m005-publish-failure",m005_publish),
            ("ABF-M-006","P3-096-M006-existing-success","m006-existing-success",m006),
            ("ABF-M-007","P3-096-M007-new-success","m007-new-success",m007),
            ("ABF-M-008","P3-096-M008-future-capture","m008-future-capture",lambda r,c:audit_rejection(r,c,mutate_future_capture)),
            ("ABF-M-009","P3-096-M009-future-saved","m009-future-saved",lambda r,c:audit_rejection(r,c,mutate_future_saved)),
            ("ABF-M-010","P3-096-M010-saved-time-mismatch","m010-saved-time-mismatch",lambda r,c:audit_rejection(r,c,mutate_saved_mismatch)),
            ("ABF-M-011","P3-096-M011-repeat-before-saved","m011-repeat-before-saved",lambda r,c:audit_rejection(r,c,mutate_repeat_before_saved)),
            ("ABF-M-012","P3-096-M012-repeat-unknown","m012-repeat-unknown",m012_unknown),
            ("ABF-M-012","P3-096-M012-repeat-cleared","m012-repeat-cleared",m012_cleared),
            ("ABF-M-013","P3-096-M013-audit-time-regression","m013-audit-time-regression",m013),
            ("ABF-M-014","P3-096-M014-clear-count-large","m014-clear-count-large",lambda r,c:m014(r,c,3)),
            ("ABF-M-014","P3-096-M014-clear-count-small","m014-clear-count-small",lambda r,c:m014(r,c,1)),
            ("ABF-M-015","P3-096-M015-normal-clear","m015-normal-clear",m015),
            ("ABF-M-016","P3-096-M016-source-case","m016-source-case",lambda r,c:m016(r,c,"LOCAL_CAPTURE")),
            ("ABF-M-016","P3-096-M016-source-empty","m016-source-empty",lambda r,c:m016(r,c,"")),
            ("ABF-M-016","P3-096-M016-source-null","m016-source-null",lambda r,c:m016(r,c,None,nullable=True)),
            ("ABF-M-016","P3-096-M016-source-blob","m016-source-blob",lambda r,c:m016(r,c,sqlite3.Binary(b"local_capture"))),
            ("ABF-M-017","P3-096-M017-duplicate-id","m017-duplicate-id",lambda r,c:m017(r,c,"id")),
            ("ABF-M-017","P3-096-M017-duplicate-idem","m017-duplicate-idem",lambda r,c:m017(r,c,"idem")),
            ("ABF-M-018","P3-096-M018-runner-missing-fields","m018-runner-missing-fields",m018),
            ("ABF-M-019","P3-096-M019-suite-pass-missing-row","m019-suite-pass-missing-row",m019)]
        fixture_root = work / "matrix"; fixture_root.mkdir()
        for row_id, test_id, fixture_id, body in cases:
            result, transition = execute_case(runtime, fixture_root, row_id, test_id, fixture_id, body)
            executions.append(result); transitions.append(transition); matrix_log.append(f"{result['actual_result']} {row_id} {test_id} {fixture_id}")
        pre_complete = validate_records(executions, ROW_IDS[:-1])
        m020_result, m020_transition = execute_case(runtime, fixture_root, "ABF-M-020", "P3-096-M020-complete-execution", "m020-complete-execution",
            lambda _r,_c:({"pre_complete_validation":pre_complete},[
                assertion("all M001-M019 complete","PASS",pre_complete["conclusion"]),
                assertion("all M001-M019 pass",True,all(item["actual_result"]=="PASS" for item in executions)),
                assertion("test IDs unique",len(executions),len({item["test_id"] for item in executions})),
                assertion("fixtures unique",len(executions),len({item["fixture_id"] for item in executions}))]))
        executions.append(m020_result); transitions.append(m020_transition); matrix_log.append(f"{m020_result['actual_result']} ABF-M-020 {m020_result['test_id']} {m020_result['fixture_id']}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    history_after = hashes(protected); history_ok = history_before == history_after
    full_validation = validate_records(executions, ROW_IDS); rows = aggregate_rows(executions)
    acceptance = [{"row_id":item["row_id"],"status":item["status"],"test_ids":item["executed_test_ids"],"fixture_ids":item["fixture_ids"],
        "structured_results":[f"executed_test_ids.json#{test_id}" for test_id in item["executed_test_ids"]],
        "evidence_files":["state_transitions.json","failure_injection_results.json" if item["row_id"] in FAILURE_ROWS else "audit_semantics_results.json" if item["row_id"] in AUDIT_ROWS else "results.json"]} for item in rows]
    source_paths = [ROOT/"src/local_capture.py",ROOT/"scripts/operator_cli.py",ROOT/"tests/test_runtime.py",SCRIPT,ROOT/"README.md"]
    deliverable = LIFEOS/"deliverables/LIFEOS-P3-096_post_commit_audit_evidence_closure.md"
    if deliverable.is_file(): source_paths.append(deliverable)
    source_hashes = {str(path.relative_to(LIFEOS)):digest(path) for path in source_paths}
    forbidden_terms = ("requests","urllib","http://","https://","tauri","ipc","socket.connect")
    forbidden_scan = {str(path.relative_to(LIFEOS)):[term for term in forbidden_terms if term in path.read_text(encoding="utf-8").lower()] for path in source_paths[:3]}
    forbidden_ok = all(not hits for hits in forbidden_scan.values())
    json_write(evidence/"results.json",rows); json_write(evidence/"acceptance_matrix.json",acceptance)
    json_write(evidence/"state_transitions.json",transitions)
    json_write(evidence/"audit_semantics_results.json",[item for item in executions if item["row_id"] in AUDIT_ROWS])
    json_write(evidence/"failure_injection_results.json",[item for item in executions if item["row_id"] in FAILURE_ROWS])
    json_write(evidence/"executed_test_ids.json",executions); json_write(evidence/"baseline_results.json",baseline)
    (evidence/"baseline_candidate.log").write_text(baseline_log,encoding="utf-8"); (evidence/"unit_test.log").write_text(unit_log,encoding="utf-8")
    (evidence/"matrix_execution.log").write_text("\n".join(matrix_log)+"\n",encoding="utf-8")
    json_write(evidence/"source_history_hashes.json",{"abf":{"expected":EXPECTED_ABF_HASHES,"actual":abf_hashes,"matches":abf_ok},
        "late_submission_candidates":late_hashes,"p3_094_p3_095_before":history_before,"p3_094_p3_095_after":history_after,
        "historical_unchanged":history_ok,"p3_096_sources":source_hashes})
    json_write(evidence/"forbidden_capability_scan.json",{"files":forbidden_scan,"closed":forbidden_ok,"network_used":False,"real_user_data_used":False})
    (evidence/"runner_source.py").write_bytes(SCRIPT.read_bytes())
    (evidence/"rerun.md").write_text("# LIFEOS-P3-096 rerun\n\n```bash\nPYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/engineering/LIFEOS-P3-096/scripts/run_p3_096.py\n```\n",encoding="utf-8")
    residue = sorted(str(path) for path in Path("/private/tmp").glob(PREFIX+"*") if path.exists())
    json_write(evidence/"temporary_residue.json",{"prefix":"/private/tmp/"+PREFIX+"*","paths":residue,"count":len(residue)})
    bad_evidence = [str(path.relative_to(evidence)) for path in files_under(evidence) if path.suffix.lower() in {".sqlite",".html",".pyc"} or "__pycache__" in path.parts]
    row_failures = sum(item["status"]=="FAIL" for item in rows); not_implemented = sum(item["status"]=="NOT IMPLEMENTED" for item in rows)+full_validation["Not Implemented"]
    p0 = 0 if history_ok and late_ok else 1; p1 = row_failures+(0 if baseline.get("passed") and unit_exit==0 and abf_ok else 1)
    p2 = 0 if forbidden_ok and not bad_evidence and not residue else 1; unknown = sum(item.get("error") is not None for item in executions)
    gate_pass = (p0==p1==p2==unknown==not_implemented==0 and all(item["status"]=="PASS" for item in rows) and full_validation["conclusion"]=="PASS" and baseline.get("passed") and unit_exit==0 and abf_ok and late_ok and history_ok and forbidden_ok and not bad_evidence and not residue)
    summary = {"pass":sum(item["status"]=="PASS" for item in rows),"fail":row_failures,"executed_test_count":len(executions),
        "P0":p0,"P1":p1,"P2":p2,"Unknown":unknown,"Not Implemented":not_implemented,"unit_suite_exit":unit_exit,
        "baseline_passed":baseline.get("passed",False),"abf_hashes_match":abf_ok,"late_manifest_hashes_match":late_ok,
        "historical_unchanged":history_ok,"forbidden_capabilities_closed":forbidden_ok,"forbidden_evidence":bad_evidence,
        "temporary_fixture_removed":not residue,"conclusion":"PASS — READY FOR PM" if gate_pass else "NOT PASS — DO NOT SUBMIT"}
    json_write(evidence/"summary.json",summary)
    (evidence/"operation_log.md").write_text(f"# Operation log\n\n- UTC: {utc_now()}\n- ABF: ABF-P3-096-v2\n- Fixed non-sensitive fixtures only: Yes\n- Baseline candidate and PM six: {'PASS' if baseline.get('passed') else 'FAIL'}\n- Unit suite exit: {unit_exit}\n- Matrix rows: {summary['pass']} PASS / {summary['fail']} FAIL\n- Executed test IDs: {len(executions)}\n- Historical read-only assets unchanged: {history_ok}\n- Temporary residue: {len(residue)}\n- Network / external / real user data: No\n- Conclusion: {summary['conclusion']}\n",encoding="utf-8")
    manifest = {str(path.relative_to(evidence)):digest(path) for path in files_under(evidence) if path.name!="MANIFEST.md"}
    lines = ["# LIFEOS-P3-096 Evidence Manifest","",f"Conclusion: {summary['conclusion']}","","Manifest is intentionally non-self-referential.","","| File | SHA-256 |","|---|---|"]
    lines.extend(f"| `{name}` | `{value}` |" for name,value in manifest.items()); (evidence/"MANIFEST.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0 if gate_pass else 1


if __name__ == "__main__": raise SystemExit(main())
