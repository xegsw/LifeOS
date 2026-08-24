#!/usr/bin/env python3
"""Actual-binary fail-closed probes and tamper fixture preparation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/resume-1"
BINARY = ROOT / "target/debug/lifeos-p3-104"
SOURCE_DB = Path("/private/tmp/lifeos-p3-104-p3-106-app-resume1-20260823/capture.sqlite")
FIXTURES = {
    "dangling-final": Path("/private/tmp/lifeos-p3-104-p3-106-dangling-final-resume1-20260823"),
    "dangling-journal": Path("/private/tmp/lifeos-p3-104-p3-106-dangling-journal-resume1-20260823"),
    "dangling-wal": Path("/private/tmp/lifeos-p3-104-p3-106-dangling-wal-resume1-20260823"),
    "dangling-shm": Path("/private/tmp/lifeos-p3-104-p3-106-dangling-shm-resume1-20260823"),
    "path": Path("/private/tmp/lifeos-p3-104-p3-106-path-resume1-20260823"),
    "path-target": Path("/private/tmp/lifeos-p3-104-p3-106-path-target-resume1-20260823"),
    "tamper": Path("/private/tmp/lifeos-p3-104-p3-106-tamper-resume1-20260823"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path: Path) -> dict[str, object]:
    try:
        value = path.lstat()
        return {"exists": True, "type": stat.filemode(value.st_mode)[0], "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}
    except FileNotFoundError:
        return {"exists": False}


def prepare_dir(path: Path) -> Path:
    if metadata(path)["exists"]:
        raise RuntimeError(f"fixture must lstat missing: {path}")
    path.mkdir(mode=0o700)
    sentinel = path / "sentinel.txt"
    sentinel.write_text("LIFEOS-P3-106 resume-1 fixed non-sensitive sentinel\n", encoding="utf-8")
    return sentinel


def run_case(row_id: str, db: Path, sentinel: Path) -> dict[str, object]:
    before = digest(sentinel)
    env = os.environ.copy()
    env["LIFEOS_P3_104_DB_PATH"] = str(db)
    completed = subprocess.run([str(BINARY)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False)
    log = OUT / f"{row_id.lower()}.log"
    log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    return {
        "id": row_id,
        "db": str(db),
        "returncode": completed.returncode,
        "sentinel_before": before,
        "sentinel_after": digest(sentinel),
        "sentinel_unchanged": before == digest(sentinel),
        "log": str(log.relative_to(ROOT)),
        "log_sha256": digest(log),
        "status": "PASS" if completed.returncode != 0 and before == digest(sentinel) else "FAIL",
    }


def main() -> int:
    if not BINARY.is_file() or not SOURCE_DB.is_file():
        raise RuntimeError("binary or fixed source DB unavailable")
    occupied = [str(path) for path in FIXTURES.values() if metadata(path)["exists"]]
    if occupied:
        raise RuntimeError(f"fixtures occupied before run: {occupied}")
    rows = []

    final_root = FIXTURES["dangling-final"]
    final_sentinel = prepare_dir(final_root)
    final_db = final_root / "capture.sqlite"
    final_missing = final_root / "missing.sqlite"
    final_db.symlink_to(final_missing)
    final = run_case("ACTUAL-DANGLING-FINAL", final_db, final_sentinel)
    final.update({"link_preserved": final_db.is_symlink(), "target_absent": not final_missing.exists()})
    final["status"] = "PASS" if final["status"] == "PASS" and final_db.is_symlink() and not final_missing.exists() else "FAIL"
    rows.append(final)

    for suffix in ["journal", "wal", "shm"]:
        root = FIXTURES[f"dangling-{suffix}"]
        sentinel = prepare_dir(root)
        db = root / "capture.sqlite"
        shutil.copyfile(SOURCE_DB, db)
        sidecar = Path(f"{db}-{suffix}")
        missing = root / f"missing-{suffix}"
        sidecar.symlink_to(missing)
        item = run_case(f"ACTUAL-DANGLING-{suffix.upper()}", db, sentinel)
        item.update({"link_preserved": sidecar.is_symlink(), "target_absent": not missing.exists(), "db_unchanged": digest(db) == digest(SOURCE_DB)})
        item["status"] = "PASS" if item["status"] == "PASS" and sidecar.is_symlink() and not missing.exists() and item["db_unchanged"] else "FAIL"
        rows.append(item)

    target_root = FIXTURES["path-target"]
    path_sentinel = prepare_dir(target_root)
    path_root = FIXTURES["path"]
    path_root.symlink_to(target_root, target_is_directory=True)
    path_db = path_root / "capture.sqlite"
    path_item = run_case("ACTUAL-PARENT-SYMLINK", path_db, path_sentinel)
    path_item.update({"parent_link_preserved": path_root.is_symlink(), "db_absent": not path_db.exists()})
    path_item["status"] = "PASS" if path_item["status"] == "PASS" and path_root.is_symlink() and not path_db.exists() else "FAIL"
    rows.append(path_item)

    tamper_root = FIXTURES["tamper"]
    tamper_sentinel = prepare_dir(tamper_root)
    tamper_db = tamper_root / "capture.sqlite"
    shutil.copyfile(SOURCE_DB, tamper_db)
    with sqlite3.connect(tamper_db) as connection:
        connection.execute("UPDATE captures SET content='P3-106 resume-1 fixed tampered content'")
        connection.commit()
    tamper = {
        "id": "ACTUAL-TAMPER-CONTENT-PREPARED",
        "db": str(tamper_db),
        "sentinel": str(tamper_sentinel),
        "sentinel_sha256": digest(tamper_sentinel),
        "db_sha256": digest(tamper_db),
        "status": "PASS",
        "next": "launch actual app and observe fail-closed get_today before replacing the same fixed DB with a schema-tampered variant",
    }
    rows.append(tamper)

    payload = {"task": "LIFEOS-P3-106", "execution": "resume-1", "fixtures": [str(path) for path in FIXTURES.values()], "rows": rows}
    payload["summary"] = {"total": len(rows), "passed": sum(row["status"] == "PASS" for row in rows), "failed": sum(row["status"] != "PASS" for row in rows)}
    (OUT / "negative_actual_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
