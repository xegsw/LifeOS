#!/usr/bin/env python3
"""P3-130 task-local structural verifier and read-only SQLite snapshotter."""
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "lifeos/tasks/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md"
ALLOW = ROOT / "lifeos/tasks/LIFEOS-P3-130_source_allowlist.md"
SOURCE = ROOT / "lifeos/engineering/LIFEOS-P3-126/candidate"
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-130/candidate"
EXPECTED_TASK = "f39f1ca8460389fa637f8e1e175f43ef67742697efbb5ea1e8081ed8aacd10ec"
EXPECTED_ALLOW = "af8fe84d2c809821bd076903ee2bfc303ae397b512c628adc4cf6e6ed7ef6b9c"
IPC = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery"]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows():
    result = []
    for line in ALLOW.read_text().splitlines():
        match = re.match(r"\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", line)
        if match:
            result.append((match.group(1), int(match.group(2)), match.group(3)))
    return result

def verify():
    allow_rows = rows()
    problems, changes = [], []
    for relative, expected_bytes, expected_hash in allow_rows:
        source = SOURCE / relative
        candidate = CANDIDATE / relative
        if not source.is_file() or source.stat().st_size != expected_bytes or digest(source) != expected_hash:
            problems.append(f"source_allowlist_mismatch:{relative}")
        if not candidate.is_file():
            problems.append(f"candidate_missing:{relative}")
        elif digest(candidate) != expected_hash:
            changes.append(relative)
    runtime = (CANDIDATE / "src/runtime.rs").read_text()
    app = (CANDIDATE / "ui/app.js").read_text()
    index = (CANDIDATE / "ui/index.html").read_text()
    commands = re.findall(r"#\[tauri::command\]\s*fn\s+(\w+)", runtime)
    invokes = re.findall(r'invoke\("([a-z_]+)"', app)
    if commands != IPC:
        problems.append(f"ipc_command_set:{commands}")
    if sorted(set(invokes)) != sorted(IPC):
        problems.append(f"ipc_renderer_set:{sorted(set(invokes))}")
    for forbidden in ["CREATE TABLE IF NOT EXISTS contexts", "CREATE TABLE IF NOT EXISTS memory", "Person Profile", "Domain ACL"]:
        if forbidden in runtime:
            problems.append(f"forbidden_runtime_token:{forbidden}")
    if "fixtures.js" in index or "runtime-adapter.js" in index:
        problems.append("legacy_runtime_script_loaded")
    return {
        "task": "LIFEOS-P3-130", "result": "PASS" if not problems else "FAIL",
        "task_contract_sha256": digest(TASK), "task_contract_expected": EXPECTED_TASK,
        "source_allowlist_sha256": digest(ALLOW), "source_allowlist_expected": EXPECTED_ALLOW,
        "source_rows": len(allow_rows), "source_lineage": f"{len(allow_rows)}/{len(allow_rows)}",
        "candidate_modified_from_inherited_allowlist": changes,
        "five_ipc_commands": commands, "renderer_invoked_ipc": sorted(set(invokes)),
        "ui_shell": {"app_shell": "app-shell" in app, "icon_rail": "icon-rail" in app, "fixtures_loaded": "fixtures.js" in index},
        "problems": problems,
    }

def snapshot(runtime_root):
    db = Path(runtime_root) / "capture.sqlite"
    result = {"task": "LIFEOS-P3-130", "runtime_root": str(Path(runtime_root)), "database_present": db.exists(), "database_sha256": digest(db) if db.exists() else None}
    if not db.exists():
        return result
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    result["user_version"] = conn.execute("PRAGMA user_version").fetchone()[0]
    result["tables"] = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    result["captures"] = [dict(row) for row in conn.execute("SELECT id,content,source,source_id,artifact_version,idem_key FROM captures ORDER BY id")]
    result["projects"] = [dict(row) for row in conn.execute("SELECT id,person_id,title,source_id,artifact_version,source_available,generation_current,tombstoned,authorized,evidence_ready FROM projects ORDER BY id")]
    result["typed_links"] = [dict(row) for row in conn.execute("SELECT capture_id,project_id,context_id,link_status,source_id,artifact_version FROM capture_project_links ORDER BY capture_id")]
    result["feedback"] = [dict(row) for row in conn.execute("SELECT capture_id,context_id,decision,idem_key FROM feedback ORDER BY id")]
    result["audit"] = [dict(row) for row in conn.execute("SELECT event,capture_id,detail FROM audit ORDER BY id")]
    conn.close()
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["verify", "snapshot"])
    parser.add_argument("--runtime-root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = verify() if args.mode == "verify" else snapshot(args.runtime_root)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": result.get("result", "SNAPSHOT"), "output": args.output}, ensure_ascii=False))

if __name__ == "__main__":
    main()
