#!/usr/bin/env python3
"""Run fail-closed checks against the built P3-106 application binary.

Only fixed, non-sensitive task-local fixtures that match the frozen ABF path
grammar are created. Cleanup is deliberately left to the exact-path cleanup
ledger so the runner cannot broaden deletion scope.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "target/debug/lifeos-p3-104"
EVIDENCE = ROOT / "evidence"
SOURCE_DB = Path("/private/tmp/lifeos-p3-104-p3-106-app-main-20260823/capture.sqlite")
STAMP = "20260823"
FIXTURES = {
    "dangling-final": Path(f"/private/tmp/lifeos-p3-104-p3-106-dangling-final-main-{STAMP}"),
    "dangling-journal": Path(f"/private/tmp/lifeos-p3-104-p3-106-dangling-journal-main-{STAMP}"),
    "dangling-wal": Path(f"/private/tmp/lifeos-p3-104-p3-106-dangling-wal-main-{STAMP}"),
    "dangling-shm": Path(f"/private/tmp/lifeos-p3-104-p3-106-dangling-shm-main-{STAMP}"),
    "path": Path(f"/private/tmp/lifeos-p3-104-p3-106-path-main-{STAMP}"),
    "path-target": Path(f"/private/tmp/lifeos-p3-104-p3-106-path-target-{STAMP}"),
    "tamper": Path(f"/private/tmp/lifeos-p3-104-p3-106-tamper-main-{STAMP}"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_absent() -> None:
    occupied = [str(path) for path in FIXTURES.values() if path.exists() or path.is_symlink()]
    if occupied:
        raise RuntimeError(f"fixture paths were not empty at start: {occupied}")


def run_case(name: str, db_path: Path, sentinel: Path) -> dict[str, object]:
    before = sha256(sentinel)
    env = os.environ.copy()
    env["LIFEOS_P3_104_DB_PATH"] = str(db_path)
    try:
        completed = subprocess.run(
            [str(BINARY)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        timed_out = False
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")

    result = {
        "id": name,
        "db_path": str(db_path),
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "sentinel_before": before,
        "sentinel_after": sha256(sentinel),
        "sentinel_unchanged": before == sha256(sentinel),
        "pass": (not timed_out) and returncode not in (None, 0) and before == sha256(sentinel),
    }
    return result


def prepare_dir(path: Path) -> Path:
    path.mkdir(mode=0o700)
    sentinel = path / "sentinel.txt"
    sentinel.write_text("LIFEOS-P3-106 fixed non-sensitive sentinel\n", encoding="utf-8")
    return sentinel


def main() -> int:
    if not BINARY.is_file() or not os.access(BINARY, os.X_OK):
        raise RuntimeError(f"built binary unavailable: {BINARY}")
    if not SOURCE_DB.is_file() or SOURCE_DB.is_symlink():
        raise RuntimeError(f"source fixed test DB unavailable or linked: {SOURCE_DB}")
    require_absent()
    results: list[dict[str, object]] = []

    final_dir = FIXTURES["dangling-final"]
    final_sentinel = prepare_dir(final_dir)
    final_db = final_dir / "capture.sqlite"
    final_missing = final_dir / "missing-target.sqlite"
    final_db.symlink_to(final_missing)
    final_result = run_case("NEG-DANGLING-FINAL", final_db, final_sentinel)
    final_result.update({
        "link_preserved": final_db.is_symlink(),
        "missing_target_absent": not final_missing.exists(),
    })
    final_result["pass"] = bool(final_result["pass"] and final_db.is_symlink() and not final_missing.exists())
    results.append(final_result)

    for suffix in ("journal", "wal", "shm"):
        case_dir = FIXTURES[f"dangling-{suffix}"]
        sentinel = prepare_dir(case_dir)
        db = case_dir / "capture.sqlite"
        shutil.copyfile(SOURCE_DB, db)
        sidecar = Path(f"{db}-{suffix}")
        missing = case_dir / f"missing-{suffix}"
        sidecar.symlink_to(missing)
        item = run_case(f"NEG-DANGLING-{suffix.upper()}", db, sentinel)
        item.update({"link_preserved": sidecar.is_symlink(), "missing_target_absent": not missing.exists()})
        item["pass"] = bool(item["pass"] and sidecar.is_symlink() and not missing.exists())
        results.append(item)

    target_dir = FIXTURES["path-target"]
    path_sentinel = prepare_dir(target_dir)
    path_dir = FIXTURES["path"]
    path_dir.symlink_to(target_dir, target_is_directory=True)
    path_db = path_dir / "capture.sqlite"
    path_result = run_case("NEG-PARENT-SYMLINK", path_db, path_sentinel)
    path_result.update({"parent_link_preserved": path_dir.is_symlink(), "db_absent": not path_db.exists()})
    path_result["pass"] = bool(path_result["pass"] and path_dir.is_symlink() and not path_db.exists())
    results.append(path_result)

    tamper_dir = FIXTURES["tamper"]
    tamper_sentinel = prepare_dir(tamper_dir)
    tamper_db = tamper_dir / "capture.sqlite"
    shutil.copyfile(SOURCE_DB, tamper_db)
    with sqlite3.connect(tamper_db) as connection:
        connection.execute("UPDATE captures SET content = 'P3-106 fixed tampered content'")
        connection.commit()
    tamper_result = run_case("NEG-TAMPERED-CONTENT", tamper_db, tamper_sentinel)
    tamper_result["tampered_content_retained"] = (
        sqlite3.connect(tamper_db).execute("SELECT content FROM captures LIMIT 1").fetchone()[0]
        == "P3-106 fixed tampered content"
    )
    tamper_result["pass"] = bool(tamper_result["pass"] and tamper_result["tampered_content_retained"])
    results.append(tamper_result)

    payload = {
        "task": "LIFEOS-P3-106",
        "binary": str(BINARY),
        "source_db": str(SOURCE_DB),
        "fixtures": [str(path) for path in FIXTURES.values()],
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(bool(item["pass"]) for item in results),
            "failed": sum(not bool(item["pass"]) for item in results),
        },
    }
    output = EVIDENCE / "negative_actual_results.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
