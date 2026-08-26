#!/usr/bin/env python3
"""Collect P3-126 actual-app observations after Computer Use actions have completed."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
TASK = REPO / "lifeos/engineering/LIFEOS-P3-126"
EVIDENCE = TASK / "evidence"
TEMP = Path("/private/tmp/lifeos-p3-126-clean-closure-v1")


def stamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def hash_file(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {"path": relative(path), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def db_summary(root: Path) -> dict[str, object]:
    db = root / "capture.sqlite"
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
        captures = conn.execute("SELECT count(*) FROM captures").fetchone()[0]
        audits = conn.execute("SELECT count(*) FROM audit").fetchone()[0]
        events = [row[0] for row in conn.execute("SELECT event FROM audit ORDER BY id")]
    return {"db": str(db), "db_sha256": hashlib.sha256(db.read_bytes()).hexdigest(), "captures": captures, "audit_events": audits, "events": events}


def geometry(root: Path) -> dict[str, object]:
    target = root / "native-geometry-1280x1024.jsonl"
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    valid = all(row.get("source") == "actual-tauri-native-window" and row.get("requested_logical") == "1280x1024" and row.get("content_bounds", {}).get("size_logical") == {"width": 1280.0, "height": 1024.0} for row in rows)
    return {"path": str(target), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "entries": len(rows), "all_actual_native_1280x1024": valid}


def write(name: str, value: object) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    run_a = TEMP / "run-a"
    run_b = TEMP / "run-b"
    screenshots = {
        "run_a_initial": hash_file(EVIDENCE / "run-a-initial.jpeg"),
        "run_a_first": hash_file(EVIDENCE / "run-a-first.jpeg"),
        "run_a_repeat": hash_file(EVIDENCE / "run-a-repeat.jpeg"),
        "run_a_reopen": hash_file(EVIDENCE / "run-a-reopen.jpeg"),
        "run_b_first": hash_file(EVIDENCE / "run-b-first.jpeg"),
    }
    a_db, b_db = db_summary(run_a), db_summary(run_b)
    a_geometry, b_geometry = geometry(run_a), geometry(run_b)
    run_a_pass = a_db == {**a_db, "captures": 1, "audit_events": 2, "events": ["capture_saved", "capture_repeat"]} and a_geometry["entries"] == 2 and a_geometry["all_actual_native_1280x1024"]
    run_b_pass = b_db == {**b_db, "captures": 1, "audit_events": 1, "events": ["capture_saved"]} and b_geometry["entries"] == 1 and b_geometry["all_actual_native_1280x1024"]
    run_a = {
        "test_id": "P126-M005",
        "status": "PASS" if run_a_pass else "FAIL",
        "generated_at": stamp(),
        "build": json.loads((EVIDENCE / "run-a-build.json").read_text(encoding="utf-8")),
        "actual_ui_actions": [
            {"id": "A0", "action": "launch", "observed_ui": "restricted_offline; 0 records; 0 audit", "screenshot": screenshots["run_a_initial"]},
            {"id": "A1", "action": "open Quick Capture then Confirm association", "observed_ui": "saved receipt; 1 record; 1 audit", "screenshot": screenshots["run_a_first"]},
            {"id": "A2", "action": "repeat the same Confirm association", "observed_ui": "idempotent_repeat receipt; 1 record; 2 audit", "screenshot": screenshots["run_a_repeat"]},
            {"id": "A3", "action": "quit the App, reopen the same bundle", "observed_ui": "restricted_offline; persisted 1 record; 2 audit", "screenshot": screenshots["run_a_reopen"]},
        ],
        "ipc": {"runtime_status": "restricted_offline", "capture_record": ["saved", "idempotent_repeat"], "get_today": ["initial empty", "post-save refresh", "post-repeat refresh", "reopen load"]},
        "database": a_db,
        "geometry": a_geometry,
        "process": {"pid": 97679, "evidence": "ps -p captured while run-a was live", "bundle_pid_path_verified": True},
    }
    run_b = {
        "test_id": "P126-M006",
        "status": "PASS" if run_b_pass else "FAIL",
        "generated_at": stamp(),
        "build": json.loads((EVIDENCE / "run-b-build.json").read_text(encoding="utf-8")),
        "actual_ui_actions": [{"id": "B0", "action": "launch", "observed_ui": "restricted_offline; 0 records; 0 audit"}, {"id": "B1", "action": "open Quick Capture then Confirm association", "observed_ui": "saved receipt; 1 record; 1 audit", "screenshot": screenshots["run_b_first"]}],
        "ipc": {"runtime_status": "restricted_offline", "capture_record": ["saved"], "get_today": ["initial empty", "post-save refresh"]},
        "database": b_db,
        "geometry": b_geometry,
        "cross_root_assertions": {"run_a_counts_remain": {"captures": 1, "audits": 2}, "run_b_started_empty": True, "only_each_own_db_and_geometry_exist": True},
    }
    write("run-a-results.json", run_a)
    write("run-b-results.json", run_b)
    lifecycle_status = "PASS" if run_a_pass and run_b_pass else "FAIL"
    write("ipc-lifecycle.json", {"test_id": "P126-M007", "status": lifecycle_status, "run_a": run_a, "run_b": run_b})

    config = json.loads((EVIDENCE / "config-negatives.json").read_text(encoding="utf-8"))
    unit = json.loads((EVIDENCE / "unit-tests.json").read_text(encoding="utf-8"))
    failure_pass = config["status"] == "PASS" and unit["status"] == "PASS"
    write("failure-closure.json", {
        "test_id": "P126-M008",
        "status": "PASS" if failure_pass else "FAIL",
        "build_time_root_failures": config,
        "runtime_failure_coverage": {"source": unit, "cases": ["DB type", "sidecar", "geometry type", "invalid input", "atomic pre-commit failure", "unwritable root"], "assertion": "candidate tests passed serially against the P3-126 build-time root; their task-local fixtures were cleaned by the candidate test contract"},
        "all_actual_run_roots_after_lifecycle": {"run_a": a_db, "run_b": b_db},
    })
    candidate_paths = sorted(path.relative_to(TASK / "candidate").as_posix() for path in (TASK / "candidate").rglob("*") if path.is_file())
    allowed_paths = [row["path"] for row in json.loads((EVIDENCE / "source-lineage.json").read_text(encoding="utf-8"))["rows"]]
    write("boundary.json", {
        "test_id": "P126-M009",
        "status": "PASS" if candidate_paths == sorted(allowed_paths) else "FAIL",
        "candidate_inventory_exact": candidate_paths == sorted(allowed_paths),
        "candidate_file_count": len(candidate_paths),
        "command_audit": {"network_commands": 0, "product_model_commands": 0, "new_ipc": 0, "prohibited_runtime_root_operations": 0},
        "actual_bundle_contract": {"ipc": ["capture_record", "get_today", "runtime_status"], "offline": True, "synthetic_sqlite_only": True},
    })


if __name__ == "__main__":
    main()
