#!/usr/bin/env python3
"""Independent ABF-P3-098-v1 runner; stdlib only, synthetic task-local data."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import traceback
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]
RUNTIME_PATH = REPO / "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py"
CLI_PATH = REPO / "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py"
ENG_MANIFEST = REPO / "lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md"
PM_MANIFEST = REPO / "lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md"
HISTORY_SOURCE = REPO / "lifeos/engineering/LIFEOS-P3-097/evidence/source_history_hashes.json"
PREFIX = "lifeos-p3-098-"

FIXED_HASHES = {
    "lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md": "3355c7f3e744abfd3be392902217f8abfa02bb783a492d87e88d8a63ddb2a09f",
    "lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md": "0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048",
    "lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md": "a214e681ebf9449af9097edde42cd04b02dc83be2a09eec472e1a3b67c386ee1",
    "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py": "1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453",
    "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py": "ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659",
    "lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py": "9cc727e7510a4a269f5c8cb1f41e95662b84fc48311a7f229e47ab8bd395d986",
    "lifeos/engineering/LIFEOS-P3-097/tests/test_runtime.py": "e6cb780daa9b271adce01022c95dd414f9b34c0248f6b727785e9167a75306bf",
    "lifeos/engineering/LIFEOS-P3-097/README.md": "7fa834dbb9ecaf78200af01c37c2ba8029a3c511affce9c184a3042c8cfa6adf",
    "lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md": "63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311",
    "lifeos/reviews/LIFEOS-P3-097_pm_review.md": "057cbf047f412c38cc606ef033604a9e7591de83272ad2523ab0e02d86a58fee",
    "lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md": "90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183",
}

ROW_SEVERITY = {f"ABF-M-{i:03d}": "P1" for i in range(1, 16)}
ROW_SEVERITY["ABF-M-011"] = "P0"

EXPECTED_IDS = [
    "IR-P3-098-001-RUNTIME", "IR-P3-098-001-CLI", "IR-P3-098-001-REOPEN",
    "IR-P3-098-002-REPEAT", "IR-P3-098-002-CONFLICT",
    "IR-P3-098-003-SAVED-REPLACE", "IR-P3-098-004-REPEAT-REPLACE",
    "IR-P3-098-005-MISSING-REPLACE", "IR-P3-098-006-CANDIDATE-CLOSE",
    "IR-P3-098-007-SIDECAR-TRANSIENT", "IR-P3-098-007-SIDECAR-PERSISTENT",
    "IR-P3-098-008-PAGE-INVALIDATE", "IR-P3-098-008-PUBLISH-AFTER-PAGE",
    "IR-P3-098-009-SAVED-FD-CLOSE", "IR-P3-098-010-REPEAT-FD-CLOSE",
    "IR-P3-098-011-ANCESTOR-DB-LINK", "IR-P3-098-011-FINAL-DB-LINK",
    "IR-P3-098-011-FINAL-PAGE-LINK", "IR-P3-098-011-DB-HARDLINK",
    "IR-P3-098-011-PAGE-HARDLINK", "IR-P3-098-011-DB-FIFO",
    "IR-P3-098-011-DB-DIR", "IR-P3-098-011-PAGE-FIFO",
    "IR-P3-098-011-PAGE-DIR", "IR-P3-098-011-DB-NONCANON",
    "IR-P3-098-011-PAGE-NONCANON", "IR-P3-098-012-RENDER-EXTERNAL",
    "IR-P3-098-012-CLEAR-EXTERNAL", "IR-P3-098-013-SCHEMA-PK",
    "IR-P3-098-013-SCHEMA-NOTNULL", "IR-P3-098-013-SCHEMA-UNIQUE",
    "IR-P3-098-013-SOURCE", "IR-P3-098-013-AUDIT-FUTURE",
    "IR-P3-098-013-AUDIT-REVERSE", "IR-P3-098-014-MISSING-ROW",
    "IR-P3-098-014-DUP-EXEC", "IR-P3-098-014-MISSING-ASSERT",
    "IR-P3-098-014-UNREPRODUCIBLE", "IR-P3-098-015-HASH-PRE",
    "IR-P3-098-015-HASH-POST", "IR-P3-098-015-ENG-MANIFEST",
    "IR-P3-098-015-PM-MANIFEST", "IR-P3-098-015-HISTORY",
    "IR-P3-098-015-FORBIDDEN-SCAN", "IR-P3-098-015-RESIDUE",
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(131072), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_runtime():
    spec = importlib.util.spec_from_file_location("p3_098_candidate_runtime", RUNTIME_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RT = load_runtime()


def db_rows(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        conn = sqlite3.connect(f"{path.as_uri()}?mode=ro&immutable=1", uri=True)
        try:
            return {
                "captures": [list(x) for x in conn.execute("SELECT id,content,created_at,source,idem_key FROM captures ORDER BY id")],
                "audit": [list(x) for x in conn.execute("SELECT id,event,capture_id,created_at,detail FROM audit ORDER BY id")],
            }
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        return {"unreadable": True}


def object_state(path: Path) -> dict[str, Any]:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return {"exists": False}
    kind = "other"
    if stat.S_ISREG(st.st_mode): kind = "regular"
    elif stat.S_ISDIR(st.st_mode): kind = "directory"
    elif stat.S_ISLNK(st.st_mode): kind = "symlink"
    elif stat.S_ISFIFO(st.st_mode): kind = "fifo"
    out: dict[str, Any] = {"exists": True, "type": kind, "nlink": st.st_nlink, "size": st.st_size}
    if kind == "regular": out["sha256"] = sha(path)
    if kind == "symlink": out["target"] = os.readlink(path)
    return out


def snapshot(root: Path) -> dict[str, Any]:
    db = root / "capture.sqlite"; page = root / "today.html"; sentinel = root / "sentinel.txt"
    residue = sorted(p.name for p in root.iterdir() if p.name.startswith((".capture.sqlite.", ".today.html.")) or p.name.endswith(("-journal", "-wal", "-shm")))
    return {"db": object_state(db), "rows": db_rows(db), "page": object_state(page),
            "sentinel": object_state(sentinel), "residue": residue,
            "entries": sorted(p.name for p in root.iterdir())}


def assert_eq(actual: Any, expected: Any, name: str, assertions: list[dict[str, Any]]) -> None:
    ok = actual == expected
    assertions.append({"name": name, "pass": ok, "actual": actual, "expected": expected})
    if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def expect_blocked(fn: Callable[[], Any], assertions: list[dict[str, Any]]) -> str:
    try:
        fn()
    except RT.CaptureError as exc:
        assertions.append({"name": "explicit_candidate_failure", "pass": True, "actual": type(exc).__name__})
        return str(exc)
    raise AssertionError("candidate unexpectedly succeeded")


def fresh_fixture(work: Path, fixture_id: str) -> tuple[Path, Path]:
    root = work / fixture_id.lower(); root.mkdir()
    (root / "sentinel.txt").write_text("sentinel-p3-098", encoding="utf-8")
    return root, root / "capture.sqlite"


def seed(work: Path, fixture_id: str, *, page: bool = True) -> tuple[Path, Path, dict[str, Any]]:
    root, db = fresh_fixture(work, fixture_id)
    result = RT.capture(db, "alpha", "key-alpha")
    if page: RT.render_today(db)
    return root, db, result


@contextmanager
def hook(callback: Callable[[str], None]):
    old = RT._TEST_FAILURE_HOOK; RT._TEST_FAILURE_HOOK = callback
    try: yield
    finally: RT._TEST_FAILURE_HOOK = old


@contextmanager
def actual_replace_failure(trace: list[dict[str, Any]]):
    original = RT.os.replace
    def replacement(src: Any, dst: Any, *args: Any, **kwargs: Any):
        if dst == RT.DB_NAME and kwargs.get("dst_dir_fd") is not None:
            trace.append({"syscall": "os.replace", "source_requested": str(src), "destination": str(dst), "actual_source": ".p3-098-missing-source"})
            try:
                return original(".p3-098-missing-source", dst, *args, **kwargs)
            except OSError as exc:
                trace[-1].update({"actual_syscall_executed": True, "errno": exc.errno, "error": type(exc).__name__})
                raise
        return original(src, dst, *args, **kwargs)
    RT.os.replace = replacement
    try: yield
    finally: RT.os.replace = original


def row_from_id(test_id: str) -> str:
    return f"ABF-M-{int(test_id.split('-')[3]):03d}"


def valid_state_checks(root: Path, status: str, assertions: list[dict[str, Any]], *, audit_events: list[str], page_exists: bool, capture_count: int = 1) -> None:
    s = snapshot(root); rows = s["rows"]
    assert_eq(status in ("saved", "idempotent_repeat"), True, "public_status_allowed", assertions)
    assert_eq(len(rows["captures"]), capture_count, "capture_count", assertions)
    assert_eq([r[1] for r in rows["audit"]], audit_events, "audit_events", assertions)
    assert_eq(s["page"]["exists"], page_exists, "page_contract", assertions)
    assert_eq(s["sentinel"].get("sha256"), hashlib.sha256(b"sentinel-p3-098").hexdigest(), "sentinel_unchanged", assertions)
    assert_eq(s["residue"], [], "zero_residue", assertions)


def schema_db(path: Path, capture_sql: str) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds"); cid = str(uuid.uuid4())
    conn = sqlite3.connect(path)
    try:
        conn.executescript(capture_sql + """
CREATE TABLE audit (id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, capture_id TEXT,
created_at TEXT NOT NULL, detail TEXT NOT NULL);
""")
        conn.execute("INSERT INTO captures VALUES(?,?,?,?,?)", (cid, "alpha", now, "local_capture", "key-alpha"))
        conn.execute("INSERT INTO audit(event,capture_id,created_at,detail) VALUES(?,?,?,?)", ("capture_saved", cid, now, "local_capture"))
        conn.commit()
    finally: conn.close()


def manifest_entries(path: Path) -> list[tuple[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| `"):
            parts = line.split("`")
            rows.append((parts[1], parts[3]))
    return rows


def verify_manifest(path: Path) -> dict[str, Any]:
    base = path.parent; checks = []
    for rel, expected in manifest_entries(path):
        target = base / rel; actual = sha(target) if target.is_file() else None
        checks.append({"path": str(target.relative_to(REPO)), "expected": expected, "actual": actual, "match": actual == expected})
    return {"manifest": str(path.relative_to(REPO)), "count": len(checks), "all_match": all(x["match"] for x in checks), "checks": checks}


def fixed_hash_report(phase: str) -> dict[str, Any]:
    checks = []
    for rel, expected in FIXED_HASHES.items():
        actual = sha(REPO / rel)
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
    return {"phase": phase, "count": len(checks), "all_match": all(x["match"] for x in checks), "checks": checks}


def history_report() -> dict[str, Any]:
    source = json.loads(HISTORY_SOURCE.read_text(encoding="utf-8")); checks = []
    for entry in source["entries"]:
        target = REPO / entry["path"]; actual = sha(target) if target.is_file() else None
        checks.append({"path": entry["path"], "group": entry["group"], "expected": entry["expected"], "actual": actual, "match": actual == entry["expected"]})
    return {"source_declared_count": source["checked_count"], "count": len(checks), "all_match": all(x["match"] for x in checks), "checks": checks}


def forbidden_scan() -> dict[str, Any]:
    allowed = {"__future__", "hashlib", "os", "re", "shutil", "sqlite3", "stat", "uuid", "datetime", "pathlib", "typing", "html", "argparse", "json", "sys", "local_capture"}
    files = [RUNTIME_PATH, CLI_PATH]; imports = []; findings = []
    for path in files:
        text = path.read_text(encoding="utf-8"); tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.extend(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module: imports.append(node.module.split(".")[0])
        for needle in ("http://", "https://", "requests.", "socket.", "subprocess.", "tauri", "vault", "sync_client", "cloud"):
            if needle in text.lower(): findings.append({"path": str(path.relative_to(REPO)), "needle": needle})
    unexpected = sorted(set(imports) - allowed)
    return {"files": [str(x.relative_to(REPO)) for x in files], "imports": sorted(set(imports)), "unexpected_imports": unexpected, "forbidden_string_findings": findings, "pass": not unexpected and not findings}


def evidence_gate(items: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [x.get("test_id") for x in items]; executions = [x.get("execution_id") for x in items]
    missing = sorted(set(EXPECTED_IDS) - set(ids)); duplicates = sorted({x for x in executions if x and executions.count(x) > 1})
    missing_assertions = sorted(x.get("test_id", "unknown") for x in items if not x.get("assertions"))
    unreproducible = sorted(x.get("test_id", "unknown") for x in items if not x.get("fixture_id") or not x.get("before") or not x.get("after"))
    ni = len(missing) + len(duplicates) + len(missing_assertions) + len(unreproducible)
    return {"missing_rows": missing, "duplicate_execution_ids": duplicates, "missing_assertions": missing_assertions,
            "unreproducible": unreproducible, "not_implemented": ni, "exit_code": 0 if ni == 0 else 1}


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    if output.resolve() != HERE:
        shutil.copy2(__file__, output / "runner_source.py")
    work = Path(tempfile.mkdtemp(prefix=PREFIX, dir="/private/tmp"))
    results: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []; op_log: list[str] = []
    pre_hash = fixed_hash_report("pre")

    def execute(test_id: str, action: Callable[[Path, Path, list[dict[str, Any]], list[dict[str, Any]]], None]) -> None:
        row = row_from_id(test_id); fixture_id = f"FX-{test_id}"; execution_id = f"EX-{uuid.uuid4()}"
        root, db = fresh_fixture(work, fixture_id); before = snapshot(root); assertions: list[dict[str, Any]] = []; trace: list[dict[str, Any]] = []
        status = "PASS"; error = None
        try: action(root, db, assertions, trace)
        except Exception as exc:
            status = "FAIL"; error = f"{type(exc).__name__}: {exc}"
            trace.append({"traceback": traceback.format_exc()})
        after = snapshot(root)
        item = {"abf_row": row, "test_id": test_id, "fixture_id": fixture_id, "execution_id": execution_id,
                "action": action.__name__, "status": status, "severity_on_failure": ROW_SEVERITY[row],
                "before": before, "after": after, "assertions": assertions, "trace": trace, "error": error}
        results.append(item); op_log.append(f"{test_id} {status} {execution_id}")
        if status != "PASS": failures.append(item)

    def saved_runtime(root, db, a, t):
        r = RT.capture(db, "alpha", "key-alpha"); valid_state_checks(root, r["status"], a, audit_events=["capture_saved"], page_exists=False)
    execute("IR-P3-098-001-RUNTIME", saved_runtime)

    def saved_cli(root, db, a, t):
        p = subprocess.run([sys.executable, "-B", str(CLI_PATH), "--db", str(db), "capture", "--text", "alpha", "--key", "key-alpha"], text=True, capture_output=True)
        assert_eq(p.returncode, 0, "cli_exit", a); r = json.loads(p.stdout); valid_state_checks(root, r["status"], a, audit_events=["capture_saved"], page_exists=False)
        t.append({"stdout": r, "stderr": p.stderr})
    execute("IR-P3-098-001-CLI", saved_cli)

    def reopen(root, db, a, t):
        r = RT.capture(db, "alpha", "key-alpha"); rows = RT.list_today(db); snap = RT.safe_snapshot(db)
        assert_eq(r["status"], "saved", "saved", a); assert_eq(len(rows), 1, "reopen_rows", a); assert_eq(snap["record_count"], 1, "reopen_snapshot", a)
        valid_state_checks(root, r["status"], a, audit_events=["capture_saved"], page_exists=False)
    execute("IR-P3-098-001-REOPEN", reopen)

    def repeat(root, db, a, t):
        first = RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); page = sha(root / "today.html")
        r = RT.capture(db, "alpha", "key-alpha"); assert_eq(r["id"], first["id"], "same_capture_id", a)
        valid_state_checks(root, r["status"], a, audit_events=["capture_saved", "capture_repeat"], page_exists=True); assert_eq(sha(root / "today.html"), page, "trusted_page_retained", a)
    execute("IR-P3-098-002-REPEAT", repeat)

    def conflict(root, db, a, t):
        RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); before = snapshot(root)
        expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-alpha"), a); assert_eq(snapshot(root), before, "conflict_zero_change", a)
    execute("IR-P3-098-002-CONFLICT", conflict)

    def replace_case(existing: bool, repeat_case: bool = False):
        def action(root, db, a, t):
            if existing: RT.capture(db, "alpha", "key-alpha"); RT.render_today(db)
            before = snapshot(root); syscall_trace = []
            with actual_replace_failure(syscall_trace):
                expect_blocked(lambda: RT.capture(db, "alpha" if repeat_case else "alpha-conflict", "key-alpha" if repeat_case else "key-beta"), a)
            assert_eq(snapshot(root), before, "actual_replace_failure_zero_change", a); assert_eq(len(syscall_trace), 1, "one_actual_live_replace_syscall", a)
            assert_eq(syscall_trace[0].get("actual_syscall_executed"), True, "actual_syscall_failed", a); t.extend(syscall_trace)
        return action
    execute("IR-P3-098-003-SAVED-REPLACE", replace_case(True, False))
    execute("IR-P3-098-004-REPEAT-REPLACE", replace_case(True, True))
    execute("IR-P3-098-005-MISSING-REPLACE", replace_case(False, False))

    def close_fail(root, db, a, t):
        RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); before = snapshot(root)
        def h(point):
            t.append({"point": point})
            if point == "candidate_close_raise": raise OSError("independent candidate close failure")
        with hook(h): expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-beta"), a)
        assert_eq(snapshot(root), before, "candidate_close_zero_change", a)
    execute("IR-P3-098-006-CANDIDATE-CLOSE", close_fail)

    def sidecar_case(persistent: bool):
        def action(root, db, a, t):
            RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); before = snapshot(root); attempts = []
            def h(point):
                t.append({"point": point})
                if point == "candidate_close_sidecar":
                    shadow = next(root.glob(".capture.sqlite.*.shadow")); Path(str(shadow) + "-journal").write_bytes(b"synthetic-sidecar")
                if point.startswith("sidecar_cleanup_attempt_"):
                    attempts.append(point)
                    if persistent or point.endswith("_1"): raise OSError("synthetic cleanup failure")
            with hook(h):
                if persistent: expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-beta"), a)
                else:
                    r = RT.capture(db, "alpha-conflict", "key-beta"); assert_eq(r["status"], "saved", "transient_cleanup_recovers", a)
            if persistent: assert_eq(snapshot(root), before, "persistent_cleanup_no_publish", a)
            else: valid_state_checks(root, "saved", a, audit_events=["capture_saved", "capture_saved"], page_exists=False, capture_count=2)
            assert_eq(len(attempts), 3 if persistent else 2, "bounded_cleanup_attempts", a)
        return action
    execute("IR-P3-098-007-SIDECAR-TRANSIENT", sidecar_case(False))
    execute("IR-P3-098-007-SIDECAR-PERSISTENT", sidecar_case(True))

    def page_fail(root, db, a, t):
        RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); before = snapshot(root)
        def h(point):
            t.append({"point": point})
            if point == "page_invalidate": raise OSError("synthetic page invalidation failure")
        with hook(h): expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-beta"), a)
        assert_eq(snapshot(root), before, "page_failure_consistent_before", a)
    execute("IR-P3-098-008-PAGE-INVALIDATE", page_fail)
    execute("IR-P3-098-008-PUBLISH-AFTER-PAGE", replace_case(True, False))

    def fd_close_case(repeat_case: bool):
        def action(root, db, a, t):
            if repeat_case: RT.capture(db, "alpha", "key-alpha"); RT.render_today(db)
            def h(point):
                t.append({"point": point})
                if point == "post_publish_gate_fd_close": raise OSError("synthetic post-publish fd close")
            with hook(h): r = RT.capture(db, "alpha", "key-alpha")
            expected = ["capture_saved", "capture_repeat"] if repeat_case else ["capture_saved"]
            valid_state_checks(root, r["status"], a, audit_events=expected, page_exists=repeat_case)
            assert_eq(r["status"], "idempotent_repeat" if repeat_case else "saved", "accurate_success_after_fd_close", a)
        return action
    execute("IR-P3-098-009-SAVED-FD-CLOSE", fd_close_case(False))
    execute("IR-P3-098-010-REPEAT-FD-CLOSE", fd_close_case(True))

    def boundary(kind: str):
        def action(root, db, a, t):
            external = root / "external.txt"; external.write_text("sentinel-p3-098", encoding="utf-8")
            if kind == "ancestor":
                real = root / "real"; real.mkdir(); link = root / "linked"; link.symlink_to(real, target_is_directory=True); target = link / "capture.sqlite"
            elif kind == "db_symlink": db.symlink_to(external); target = db
            elif kind == "db_hardlink":
                RT.capture(db, "alpha", "key-alpha"); os.link(db, root / "db-hardlink"); target = db
            elif kind == "db_fifo": os.mkfifo(db); target = db
            elif kind == "db_dir": db.mkdir(); target = db
            else:
                RT.capture(db, "alpha", "key-alpha"); page = root / "today.html"
                if kind == "page_symlink": page.symlink_to(external)
                elif kind == "page_hardlink": page.write_text("trusted", encoding="utf-8"); os.link(page, root / "page-hardlink")
                elif kind == "page_fifo": os.mkfifo(page)
                elif kind == "page_dir": page.mkdir()
                target = db
            before = {"root": snapshot(root), "external": object_state(external)}
            expect_blocked(lambda: RT.capture(target, "alpha-conflict", "key-beta"), a)
            after = {"root": snapshot(root), "external": object_state(external)}
            assert_eq(after, before, f"{kind}_refused_before_change", a)
        return action
    for tid, kind in [
        ("IR-P3-098-011-ANCESTOR-DB-LINK", "ancestor"), ("IR-P3-098-011-FINAL-DB-LINK", "db_symlink"),
        ("IR-P3-098-011-FINAL-PAGE-LINK", "page_symlink"), ("IR-P3-098-011-DB-HARDLINK", "db_hardlink"),
        ("IR-P3-098-011-PAGE-HARDLINK", "page_hardlink"), ("IR-P3-098-011-DB-FIFO", "db_fifo"),
        ("IR-P3-098-011-DB-DIR", "db_dir"), ("IR-P3-098-011-PAGE-FIFO", "page_fifo"),
        ("IR-P3-098-011-PAGE-DIR", "page_dir")]: execute(tid, boundary(kind))

    def db_noncanon(root, db, a, t):
        raw = str(root) + "/./capture.sqlite"; before = snapshot(root); expect_blocked(lambda: RT.capture(raw, "alpha", "key-alpha"), a); assert_eq(snapshot(root), before, "noncanonical_db_zero_change", a)
    execute("IR-P3-098-011-DB-NONCANON", db_noncanon)
    def page_noncanon(root, db, a, t):
        RT.capture(db, "alpha", "key-alpha"); before = snapshot(root); expect_blocked(lambda: RT.render_today(db, Path(str(root) + "/./today.html")), a); assert_eq(snapshot(root), before, "noncanonical_output_zero_change", a)
    execute("IR-P3-098-011-PAGE-NONCANON", page_noncanon)

    def external_output(clear: bool):
        def action(root, db, a, t):
            RT.capture(db, "alpha", "key-alpha"); RT.render_today(db); outside = work / f"outside-{uuid.uuid4()}.txt"; outside.write_text("sentinel-p3-098", encoding="utf-8")
            before = {"root": snapshot(root), "outside": object_state(outside)}
            if clear: expect_blocked(lambda: RT.delete_all(db, "DELETE", outside), a)
            else: expect_blocked(lambda: RT.render_today(db, outside), a)
            assert_eq({"root": snapshot(root), "outside": object_state(outside)}, before, "external_output_zero_change", a)
        return action
    execute("IR-P3-098-012-RENDER-EXTERNAL", external_output(False)); execute("IR-P3-098-012-CLEAR-EXTERNAL", external_output(True))

    schemas = {
        "PK": "CREATE TABLE captures (id TEXT, content TEXT NOT NULL, created_at TEXT NOT NULL, source TEXT NOT NULL CHECK(source='local_capture'), idem_key TEXT NOT NULL UNIQUE);",
        "NOTNULL": "CREATE TABLE captures (id TEXT PRIMARY KEY, content TEXT, created_at TEXT NOT NULL, source TEXT NOT NULL CHECK(source='local_capture'), idem_key TEXT NOT NULL UNIQUE);",
        "UNIQUE": "CREATE TABLE captures (id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at TEXT NOT NULL, source TEXT NOT NULL CHECK(source='local_capture'), idem_key TEXT NOT NULL);",
    }
    def schema_case(name: str, entry: str):
        def action(root, db, a, t):
            schema_db(db, schemas[name]); (root / "today.html").write_text("stale", encoding="utf-8"); before_db = sha(db); before_sentinel = sha(root / "sentinel.txt")
            if entry == "list": expect_blocked(lambda: RT.list_today(db), a)
            elif entry == "render": expect_blocked(lambda: RT.render_today(db), a)
            else: expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-beta"), a)
            assert_eq(sha(db), before_db, "mutated_schema_db_unchanged", a); assert_eq(sha(root / "sentinel.txt"), before_sentinel, "sentinel_unchanged", a)
            if entry == "render": assert_eq((root / "today.html").exists(), False, "stale_page_invalidated_on_untrusted_render", a)
        return action
    execute("IR-P3-098-013-SCHEMA-PK", schema_case("PK", "list")); execute("IR-P3-098-013-SCHEMA-NOTNULL", schema_case("NOTNULL", "render")); execute("IR-P3-098-013-SCHEMA-UNIQUE", schema_case("UNIQUE", "capture"))

    def semantic_case(kind: str):
        def action(root, db, a, t):
            RT.capture(db, "alpha", "key-alpha")
            if kind == "reverse": RT.capture(db, "alpha", "key-alpha")
            conn = sqlite3.connect(db)
            try:
                if kind == "source":
                    conn.execute("PRAGMA ignore_check_constraints=ON"); conn.execute("UPDATE captures SET source='external'")
                elif kind == "future": conn.execute("UPDATE audit SET created_at=? WHERE id=1", ((datetime.now(timezone.utc)+timedelta(days=1)).isoformat(timespec="seconds"),))
                else: conn.execute("UPDATE audit SET created_at=? WHERE id=2", ((datetime.now(timezone.utc)-timedelta(days=1)).isoformat(timespec="seconds"),))
                conn.commit()
            finally: conn.close()
            (root / "today.html").write_text("stale", encoding="utf-8"); before_db = sha(db)
            if kind == "source": expect_blocked(lambda: RT.list_today(db), a)
            elif kind == "future": expect_blocked(lambda: RT.render_today(db), a); assert_eq((root / "today.html").exists(), False, "future_audit_stale_page_invalidated", a)
            else: expect_blocked(lambda: RT.capture(db, "alpha-conflict", "key-beta"), a)
            assert_eq(sha(db), before_db, "semantic_mutation_db_unchanged", a)
        return action
    execute("IR-P3-098-013-SOURCE", semantic_case("source")); execute("IR-P3-098-013-AUDIT-FUTURE", semantic_case("future")); execute("IR-P3-098-013-AUDIT-REVERSE", semantic_case("reverse"))

    def gate_case(defect: str):
        def action(root, db, a, t):
            synthetic = [{"test_id": x, "execution_id": f"EX-{i}", "fixture_id": f"FX-{i}", "assertions": [{"pass": True}], "before": {"x": 1}, "after": {"x": 1}} for i, x in enumerate(EXPECTED_IDS)]
            if defect == "missing": synthetic.pop()
            elif defect == "duplicate": synthetic[1]["execution_id"] = synthetic[0]["execution_id"]
            elif defect == "assertion": synthetic[0]["assertions"] = []
            else: synthetic[0]["before"] = {}
            gate = evidence_gate(synthetic); assert_eq(gate["exit_code"], 1, "negative_gate_nonzero", a); assert_eq(gate["not_implemented"] > 0, True, "negative_gate_not_implemented", a); t.append(gate)
        return action
    execute("IR-P3-098-014-MISSING-ROW", gate_case("missing")); execute("IR-P3-098-014-DUP-EXEC", gate_case("duplicate")); execute("IR-P3-098-014-MISSING-ASSERT", gate_case("assertion")); execute("IR-P3-098-014-UNREPRODUCIBLE", gate_case("unreproducible"))

    eng = verify_manifest(ENG_MANIFEST); pm = verify_manifest(PM_MANIFEST); hist = history_report(); scan = forbidden_scan()
    def meta(test_id: str, predicate: bool, detail: Any):
        def action(root, db, a, t): assert_eq(predicate, True, test_id, a); t.append(detail)
        execute(test_id, action)
    meta("IR-P3-098-015-HASH-PRE", pre_hash["all_match"], pre_hash); meta("IR-P3-098-015-ENG-MANIFEST", eng["all_match"] and eng["count"] == 16, eng)
    meta("IR-P3-098-015-PM-MANIFEST", pm["all_match"] and pm["count"] == 23, pm); meta("IR-P3-098-015-HISTORY", hist["all_match"] and hist["count"] == 310, {"count": hist["count"], "all_match": hist["all_match"]})
    meta("IR-P3-098-015-FORBIDDEN-SCAN", scan["pass"], scan)

    post_hash = fixed_hash_report("post")
    meta("IR-P3-098-015-HASH-POST", post_hash["all_match"], post_hash)

    shutil.rmtree(work)
    residue_paths = sorted(str(p) for p in Path("/private/tmp").glob(PREFIX + "*"))
    def residue_action(root, db, a, t): assert_eq(residue_paths, [], "system_task_prefix_residue_zero", a)
    # The residue leaf cannot use execute(), which would itself create a fixture under the removed root.
    rid = "IR-P3-098-015-RESIDUE"; results.append({"abf_row": "ABF-M-015", "test_id": rid, "fixture_id": "FX-RESIDUE-SCAN", "execution_id": f"EX-{uuid.uuid4()}", "action": "system_prefix_residue_scan", "status": "PASS" if not residue_paths else "FAIL", "severity_on_failure": "P1", "before": {"prefix": PREFIX}, "after": {"residue_paths": residue_paths}, "assertions": [{"name": "system_task_prefix_residue_zero", "pass": not residue_paths, "actual": residue_paths, "expected": []}], "trace": [], "error": None if not residue_paths else "task-local residue remains"})
    if residue_paths: failures.append(results[-1])

    full_gate = evidence_gate(results)
    counts = {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": full_gate["not_implemented"]}
    for item in failures: counts[item.get("severity_on_failure", "Unknown")] += 1
    conclusion = "PASS" if not failures and full_gate["exit_code"] == 0 and all(v == 0 for v in counts.values()) else "REWORK"
    summary = {"task_id": "LIFEOS-P3-098", "abf_id": "ABF-P3-098-v1", "conclusion": conclusion,
               "total": len(results), "pass": sum(x["status"] == "PASS" for x in results), "fail": len(failures),
               "counts": counts, "evidence_gate": full_gate, "runner_exit_code": 0 if conclusion == "PASS" else 1,
               "frozen_test_design_sha256": sha(HERE / "frozen_test_design.md"), "temporary_residue": residue_paths}
    dump(output / "acceptance_matrix.json", results); dump(output / "executed_test_ids.json", [{k: x[k] for k in ("abf_row", "test_id", "fixture_id", "execution_id", "status")} for x in results])
    dump(output / "state_transitions.json", [{"test_id": x["test_id"], "before": x["before"], "after": x["after"]} for x in results])
    dump(output / "failure_injection_results.json", [{"test_id": x["test_id"], "trace": x["trace"], "status": x["status"]} for x in results if x["trace"]])
    dump(output / "source_history_hashes.json", {"fixed_pre": pre_hash, "fixed_post": post_hash, "engineering_manifest": eng, "pm_manifest": pm, "history": hist})
    dump(output / "static_scan.json", scan); dump(output / "temporary_residue.json", {"prefix": PREFIX, "paths": residue_paths, "count": len(residue_paths)})
    dump(output / "results.json", summary); (output / "matrix_execution.log").write_text("\n".join(op_log) + "\n", encoding="utf-8")
    (output / "operation_log.md").write_text("# LIFEOS-P3-098 operation log\n\n" + "\n".join(f"- {x}" for x in op_log) + "\n", encoding="utf-8")
    (output / "rerun.md").write_text(f"# Rerun\n\n```bash\npython3 -B {HERE / 'runner_source.py'} --output /private/tmp/p3-098-independent-rerun-evidence\n```\n\nExpected exit: `{summary['runner_exit_code']}`. Remove the explicit rerun output after inspection.\n", encoding="utf-8")
    manifest_files = sorted(p for p in output.iterdir() if p.is_file() and p.name != "MANIFEST.md")
    lines = ["# LIFEOS-P3-098 Independent Evidence Manifest", "", f"Conclusion: {conclusion}", "", "Manifest is intentionally non-self-referential.", "", "| File | SHA-256 | Purpose |", "|---|---|---|"]
    for p in manifest_files: lines.append(f"| `{p.name}` | `{sha(p)}` | independent P3-098 Evidence |")
    (output / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary["runner_exit_code"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=HERE); args = parser.parse_args()
    raise SystemExit(run(args.output.resolve()))
