#!/usr/bin/env python3
"""Build and exercise only P3-110 ABF-authorized negative DB fixtures."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
WORK = Path("/private/tmp/lifeos-p3-110-review-work-v1")
BINARY = WORK / "P3-110-LifeOS.app/Contents/MacOS/lifeos-p3-104"
PREFIX = "lifeos-p3-104-p3-110-review-"
NAMES = {
    "nominal", "path", "link", "hardlink", "dangling-final", "dangling-journal",
    "dangling-wal", "dangling-shm", "tamper",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def root(name: str) -> Path:
    if name not in NAMES:
        raise ValueError(f"unauthorized fixture: {name}")
    return Path("/private/tmp") / f"{PREFIX}{name}-v1"


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def sentinel(directory: Path) -> dict[str, str]:
    path = directory / "sentinel.txt"
    path.write_text("P3-110 NEGATIVE FIXTURE SENTINEL\n", encoding="utf-8")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def copy_nominal(directory: Path) -> dict[str, str]:
    source = root("nominal") / "capture.sqlite"
    if not source.is_file():
        raise RuntimeError("nominal db must exist before negative fixtures")
    directory.mkdir()
    target = directory / "capture.sqlite"
    shutil.copy2(source, target)
    return {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "target_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


def setup() -> dict[str, object]:
    for name in NAMES - {"nominal"}:
        remove(root(name))
    outcomes: dict[str, object] = {}

    path = root("path")
    path.mkdir()
    (path / "capture.sqlite").mkdir()
    outcomes["directory_object"] = {"db": str(path / "capture.sqlite"), **sentinel(path)}

    link = root("link")
    os.symlink(root("path"), link)
    outcomes["parent_symlink"] = {"db": str(link / "capture.sqlite"), "link_target": str(root("path"))}

    hard = root("hardlink")
    hard.mkdir()
    target = hard / "capture.sqlite.original"
    target.write_text("P3-110 HARDLINK TARGET\n", encoding="utf-8")
    os.link(target, hard / "capture.sqlite")
    outcomes["hardlink"] = {"db": str(hard / "capture.sqlite"), "nlink": os.stat(hard / "capture.sqlite").st_nlink, **sentinel(hard)}

    dangling = root("dangling-final")
    dangling.mkdir()
    os.symlink(dangling / "missing.sqlite", dangling / "capture.sqlite")
    outcomes["dangling_final"] = {"db": str(dangling / "capture.sqlite"), "link_target": str(dangling / "missing.sqlite"), **sentinel(dangling)}

    for suffix, name in [("-journal", "dangling-journal"), ("-wal", "dangling-wal"), ("-shm", "dangling-shm")]:
        directory = root(name)
        copy = copy_nominal(directory)
        sidecar = directory / f"capture.sqlite{suffix}"
        os.symlink(directory / f"missing{suffix}", sidecar)
        outcomes[name] = {"db": str(directory / "capture.sqlite"), "sidecar": str(sidecar), "sidecar_target": str(directory / f"missing{suffix}"), **copy, **sentinel(directory)}

    tamper = root("tamper")
    copy = copy_nominal(tamper)
    conn = sqlite3.connect(tamper / "capture.sqlite")
    conn.execute("UPDATE captures SET content='P3-110 tampered content'")
    conn.commit()
    conn.close()
    outcomes["tampered_content"] = {"db": str(tamper / "capture.sqlite"), **copy, "post_tamper_sha256": hashlib.sha256((tamper / "capture.sqlite").read_bytes()).hexdigest(), **sentinel(tamper)}
    return outcomes


def launch(label: str, database: Path) -> dict[str, object]:
    if not BINARY.is_file():
        raise RuntimeError("review wrapper executable missing")
    log = EVIDENCE / f"negative-{label}.log"
    env = os.environ.copy()
    env["LIFEOS_P3_104_DB_PATH"] = str(database)
    with log.open("w", encoding="utf-8") as handle:
        handle.write(f"started_at_utc={now()}\ndb={database}\n")
        process = subprocess.Popen([str(BINARY)], cwd=WORK, env=env, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
        exit_code = process.wait(timeout=8)
    content = log.read_text(encoding="utf-8", errors="replace")
    return {
        "label": label,
        "database": str(database),
        "pid": process.pid,
        "exit_code": exit_code,
        "log": str(log.relative_to(ROOT)),
        "panic_boundary_rejected": "controlled DB boundary rejected" in content,
        "log_tail": content[-1200:],
    }


if __name__ == "__main__":
    prepared = setup()
    checks = {
        "directory_object": root("path") / "capture.sqlite",
        "parent_symlink": root("link") / "capture.sqlite",
        "hardlink": root("hardlink") / "capture.sqlite",
        "dangling_final": root("dangling-final") / "capture.sqlite",
        "dangling_journal": root("dangling-journal") / "capture.sqlite",
        "dangling_wal": root("dangling-wal") / "capture.sqlite",
        "dangling_shm": root("dangling-shm") / "capture.sqlite",
        # No external object is created: the raw path is rejected before traversal
        # because it contains an explicit parent traversal component.
        "external_path_schema": root("path") / ".." / "p3-110-outside" / "capture.sqlite",
    }
    results = {label: launch(label, database) for label, database in checks.items()}
    payload = {"started_at_utc": now(), "prepared": prepared, "startup_rejections": results}
    (EVIDENCE / "negative-path-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({label: value["exit_code"] for label, value in results.items()}, ensure_ascii=False))
