#!/usr/bin/env python3
"""PM verifier for LIFEOS-P3-103.

Never opens the retained real DB or page. Real retained assets are checked by
lstat and exact filename listing only. Dynamic checks use fixed non-sensitive
fixtures under /private/tmp and never invoke clear.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


PROJECT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
SUBMITTED = PROJECT / "lifeos/reviews/LIFEOS-P3-103/evidence"
REAL_ROOT = Path("/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1")
REAL_DB = REAL_ROOT / "capture.sqlite"
REAL_PAGE = REAL_ROOT / "today.html"
CLI = PROJECT / "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py"
TEXT_A = "LIFEOS P3 103 PM FIXED NONSENSITIVE NOTE ALPHA"
TEXT_B = "LIFEOS P3 103 PM FIXED NONSENSITIVE NOTE BETA"
KEY_A = "p3-103-pm-fixed-nonsensitive-key"
SIDECARS = ("-journal", "-wal", "-shm")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_submitted_manifest() -> dict[str, Any]:
    manifest = SUBMITTED / "MANIFEST.md"
    rows = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([0-9a-f]{64})` \| `([^`]+)` \|", line)
        if not match:
            continue
        expected, rel = match.groups()
        actual = sha(PROJECT / rel)
        rows.append({"path": rel, "match": actual == expected})
    return {"verified": sum(r["match"] for r in rows), "total": len(rows), "mismatches": [r["path"] for r in rows if not r["match"]]}


def verify_fixed_inputs() -> dict[str, Any]:
    source = json.loads((SUBMITTED / "source_history_hashes.json").read_text(encoding="utf-8"))
    before = source["before"]
    groups = {}
    for name, expected_count in (("fixed", 10), ("engineering_manifest_entries", 17), ("pm_manifest_entries", 5)):
        rows = before[name]["rows"]
        current = [sha(PROJECT / row["path"]) == row["expected"] == row["actual"] for row in rows]
        groups[name] = {"verified": sum(current), "total": len(current), "expected_total": expected_count}
    groups["submitted_before_after_unchanged"] = source.get("unchanged") is True
    return groups


def verify_matrix() -> dict[str, Any]:
    data = json.loads((SUBMITTED / "acceptance_matrix.json").read_text(encoding="utf-8"))
    parents = data["rows"]
    leaves = data["lifecycle_leaves"] + data["boundary_leaves"] + data["negative_gate_cases"]
    uniqueness = {}
    for kind in ("test_id", "fixture_id", "execution_id"):
        values = [row[kind] for row in parents + leaves]
        uniqueness[kind] = len(values) == len(set(values))
    return {
        "parent_pass": sum(row["status"] == "PASS" for row in parents),
        "parent_total": len(parents),
        "lifecycle_leaves": len(data["lifecycle_leaves"]),
        "boundary_leaves": len(data["boundary_leaves"]),
        "negative_gate_cases": len(data["negative_gate_cases"]),
        "all_assertions_executed": all(row.get("assertion_executed") is True for row in parents + leaves),
        "unique_ids": uniqueness,
    }


def retained_metadata() -> dict[str, Any]:
    def one(path: Path) -> dict[str, Any]:
        value = path.lstat()
        return {
            "path": str(path),
            "mode": stat.S_IMODE(value.st_mode),
            "type": "directory" if stat.S_ISDIR(value.st_mode) else "regular" if stat.S_ISREG(value.st_mode) else "other",
            "nlink": value.st_nlink,
            "device": value.st_dev,
            "inode": value.st_ino,
            "size": value.st_size,
            "mtime_ns": value.st_mtime_ns,
            "ctime_ns": value.st_ctime_ns,
        }

    ancestors = [Path("/"), Path("/Users"), Path("/Users/xxe"), Path("/Users/xxe/Documents")]
    return {
        "ancestors": [one(path) for path in ancestors],
        "directory": one(REAL_ROOT),
        "db": one(REAL_DB),
        "page": one(REAL_PAGE),
        "filenames": sorted(path.name for path in REAL_ROOT.iterdir()),
        "sidecars": [REAL_DB.name + suffix for suffix in SIDECARS if (REAL_ROOT / (REAL_DB.name + suffix)).exists()],
        "content_read": False,
        "content_hashed": False,
    }


def cli(db: Path, command: str, *args: str, cwd: Path | None = None) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run([sys.executable, "-B", str(CLI), "--db", str(db), command, *args], cwd=cwd, text=True, capture_output=True, timeout=30)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"parseable": False}
    return proc.returncode, payload


def file_hashes(root: Path) -> dict[str, str | None]:
    return {name: sha(root / name) if (root / name).is_file() else None for name in ("capture.sqlite", "today.html")}


def lifecycle(root: Path) -> dict[str, bool]:
    root.mkdir(mode=0o700, exist_ok=True)
    db = root / "capture.sqlite"
    code, result = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    saved = code == 0 and result.get("status") == "saved"
    code, result = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    repeat = code == 0 and result.get("status") == "idempotent_repeat"
    before = file_hashes(root)
    code, result = cli(db, "capture", "--text", TEXT_B, "--key", KEY_A)
    conflict = code != 0 and result.get("status") == "blocked" and file_hashes(root) == before
    code, result = cli(db, "today")
    today = code == 0 and len(result.get("records", [])) == 1 and result["records"][0].get("content") == TEXT_A
    code, result = cli(db, "render")
    page = root / "today.html"
    body = page.read_text(encoding="utf-8") if page.is_file() else ""
    render = code == 0 and result.get("status") == "rendered" and TEXT_A in body
    del body
    before = file_hashes(root)
    code, result = cli(db, "capture", "--text", TEXT_B, "--key", "p3-103-pm-failure", "--inject-failure")
    failure = code != 0 and result.get("status") == "blocked" and file_hashes(root) == before and not any(path.name.startswith(".capture") or path.name.endswith(SIDECARS) for path in root.iterdir())
    return {"saved": saved, "repeat": repeat, "conflict": conflict, "today": today, "render": render, "failure": failure}


def create_valid_db(root: Path) -> Path:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = root / "capture.sqlite"
    code, result = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    if code != 0 or result.get("status") != "saved":
        raise RuntimeError("fixture setup failed")
    return db


def boundary_case(name: str, setup: Callable[[Path], dict[str, Any]], invoke: Callable[[Path, dict[str, Any]], tuple[int, bool]]) -> bool:
    root = Path(tempfile.mkdtemp(prefix=f"lifeos-p3-103-pm-{name}-", dir="/private/tmp"))
    try:
        context = setup(root)
        before = {str(path): sha(path) for path in context.get("sentinels", []) if path.is_file()}
        code, blocked = invoke(root, context)
        after = {str(path): sha(path) for path in context.get("sentinels", []) if path.is_file()}
        return code != 0 and blocked and before == after
    finally:
        shutil.rmtree(root)


def boundaries() -> dict[str, bool]:
    out: dict[str, bool] = {}

    def capture_invoke(root: Path, context: dict[str, Any]) -> tuple[int, bool]:
        code, payload = cli(context["db"], "capture", "--text", TEXT_A, "--key", KEY_A, cwd=root)
        return code, payload.get("status") == "blocked"

    out["relative"] = boundary_case("relative", lambda root: {"db": Path("capture.sqlite")}, capture_invoke)
    out["dotdot"] = boundary_case("dotdot", lambda root: {"db": Path(str(root / "inner" / ".." / "capture.sqlite"))}, capture_invoke)

    def ancestor(root: Path) -> dict[str, Any]:
        real = root / "real"; real.mkdir(); link = root / "link"; link.symlink_to(real, target_is_directory=True)
        return {"db": link / "capture.sqlite"}
    out["ancestor_symlink"] = boundary_case("ancestor", ancestor, capture_invoke)

    def db_symlink(root: Path) -> dict[str, Any]:
        target = root / "sentinel"; target.write_text("sentinel"); (root / "capture.sqlite").symlink_to(target)
        return {"db": root / "capture.sqlite", "sentinels": [target]}
    out["final_db_symlink"] = boundary_case("db-symlink", db_symlink, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "today")))

    def page_symlink(root: Path) -> dict[str, Any]:
        db = create_valid_db(root); target = root / "sentinel"; target.write_text("sentinel"); (root / "today.html").symlink_to(target)
        return {"db": db, "sentinels": [target]}
    out["final_page_symlink"] = boundary_case("page-symlink", page_symlink, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "render")))

    def db_hardlink(root: Path) -> dict[str, Any]:
        db = create_valid_db(root); link = root / "db-link"; os.link(db, link); return {"db": db, "sentinels": [db, link]}
    out["db_hardlink"] = boundary_case("db-hardlink", db_hardlink, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "today")))

    def page_hardlink(root: Path) -> dict[str, Any]:
        db = create_valid_db(root); cli(db, "render"); page = root / "today.html"; link = root / "page-link"; os.link(page, link); return {"db": db, "sentinels": [page, link]}
    out["page_hardlink"] = boundary_case("page-hardlink", page_hardlink, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "render")))

    def fifo(root: Path) -> dict[str, Any]:
        os.mkfifo(root / "capture.sqlite"); return {"db": root / "capture.sqlite"}
    out["fifo"] = boundary_case("fifo", fifo, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "today")))

    def directory(root: Path) -> dict[str, Any]:
        (root / "capture.sqlite").mkdir(); return {"db": root / "capture.sqlite"}
    out["directory"] = boundary_case("directory", directory, lambda root, c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "today")))

    def external(root: Path) -> dict[str, Any]:
        db = create_valid_db(root); target = root / "sentinel"; target.write_text("sentinel"); return {"db": db, "target": target, "sentinels": [target]}
    def external_invoke(root: Path, context: dict[str, Any]) -> tuple[int, bool]:
        code = "import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from local_capture import render_today,CaptureError\ntry: render_today(Path(sys.argv[2]),Path(sys.argv[3]));raise SystemExit(0)\nexcept CaptureError: raise SystemExit(2)"
        proc = subprocess.run([sys.executable, "-B", "-c", code, str((PROJECT / "lifeos/engineering/LIFEOS-P3-097/src")), str(context["db"]), str(context["target"])], capture_output=True, text=True)
        return proc.returncode, proc.returncode == 2
    out["external_output"] = boundary_case("external", external, external_invoke)
    return out


def main() -> int:
    submitted_manifest = verify_submitted_manifest()
    fixed = verify_fixed_inputs()
    matrix = verify_matrix()
    retained_before = retained_metadata()
    root = Path(tempfile.mkdtemp(prefix="lifeos-p3-103-pm-lifecycle-", dir="/private/tmp"))
    try:
        fresh_lifecycle = lifecycle(root)
    finally:
        shutil.rmtree(root)
    fresh_boundaries = boundaries()
    retained_after = retained_metadata()
    residue = [path.name for path in Path("/private/tmp").glob("lifeos-p3-103-pm-*")]
    retained_contract = (
        all(item["type"] == "directory" for item in retained_before["ancestors"])
        and retained_before["directory"]["type"] == "directory"
        and retained_before["directory"]["mode"] == 0o700
        and retained_before["db"]["type"] == retained_before["page"]["type"] == "regular"
        and retained_before["db"]["mode"] == retained_before["page"]["mode"] == 0o600
        and retained_before["db"]["nlink"] == retained_before["page"]["nlink"] == 1
        and retained_before["filenames"] == ["capture.sqlite", "today.html"]
        and retained_before["sidecars"] == []
    )
    ok = (
        submitted_manifest == {"verified": 20, "total": 20, "mismatches": []}
        and all(fixed[name]["verified"] == fixed[name]["total"] == fixed[name]["expected_total"] for name in ("fixed", "engineering_manifest_entries", "pm_manifest_entries"))
        and fixed["submitted_before_after_unchanged"]
        and matrix["parent_pass"] == matrix["parent_total"] == 12
        and [matrix["lifecycle_leaves"], matrix["boundary_leaves"], matrix["negative_gate_cases"]] == [6, 10, 4]
        and matrix["all_assertions_executed"] and all(matrix["unique_ids"].values())
        and retained_contract and retained_before == retained_after
        and all(fresh_lifecycle.values()) and all(fresh_boundaries.values())
        and not residue
    )
    result = {
        "task_id": "LIFEOS-P3-103",
        "status": "PASS" if ok else "FAIL",
        "submitted_manifest": submitted_manifest,
        "fixed_inputs": fixed,
        "submitted_matrix": matrix,
        "retained_metadata_contract": retained_contract,
        "retained_metadata_unchanged": retained_before == retained_after,
        "retained_content_read_by_pm": False,
        "retained_content_hashed_by_pm": False,
        "fresh_fixed_lifecycle": fresh_lifecycle,
        "fresh_fixed_boundaries": fresh_boundaries,
        "clear_invoked": False,
        "temporary_residue": residue,
    }
    (OUT / "verification_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "manifest": submitted_manifest, "lifecycle": sum(fresh_lifecycle.values()), "boundaries": sum(fresh_boundaries.values()), "retained_unchanged": result["retained_metadata_unchanged"], "temporary_residue": len(residue)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
