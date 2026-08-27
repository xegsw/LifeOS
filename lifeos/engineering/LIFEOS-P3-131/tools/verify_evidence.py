#!/usr/bin/env python3
"""Read-only verifier and task-local Evidence snapshot writer for LIFEOS-P3-131."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ENGINEERING = ROOT / "lifeos/engineering/LIFEOS-P3-131"
CANDIDATE = ENGINEERING / "candidate"
EVIDENCE = ENGINEERING / "evidence"
P3_130_MANIFEST = ROOT / "lifeos/engineering/LIFEOS-P3-130/evidence/FINAL_MANIFEST.json"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-131-next-action-v1")
EXPECTED_COMMANDS = [
    "capture_record",
    "get_today",
    "runtime_status",
    "confirm_capture_context",
    "get_context_recovery",
    "get_context_next_action",
    "decide_context_next_action",
    "record_action_result",
]
ALLOWED_MODIFIED = {
    "Cargo.lock",
    "Cargo.toml",
    "capabilities/main.json",
    "gen/schemas/capabilities.json",
    "src/runtime.rs",
    "tauri.conf.json",
    "ui/app.js",
    "ui/index.html",
    "ui/runtime-adapter.js",
}
TABLES = [
    "captures", "projects", "capture_project_links", "derivations", "candidate_actions",
    "feedback", "actions", "action_results", "audit",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def regular(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode) and info.st_nlink == 1


def atomic_json(destination: Path, data: object) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".pending")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, destination)


def source_lineage() -> dict[str, object]:
    manifest = json.loads(P3_130_MANIFEST.read_text(encoding="utf-8"))
    listed = manifest["candidate_inventory"]
    problems: list[str] = []
    rows: list[dict[str, object]] = []
    expected = set()
    for entry in listed:
        source = ROOT / entry["path"]
        relative = source.relative_to(ROOT / "lifeos/engineering/LIFEOS-P3-130/candidate")
        destination = CANDIDATE / relative
        key = relative.as_posix()
        expected.add(key)
        source_ok = regular(source) and source.stat().st_size == entry["bytes"] and digest(source) == entry["sha256"]
        target_ok = destination.exists() and regular(destination)
        target_hash = digest(destination) if target_ok else None
        state = "unchanged" if target_hash == entry["sha256"] else "modified_in_task_scope"
        if not source_ok:
            problems.append(f"source mismatch: {key}")
        if not target_ok:
            problems.append(f"candidate missing/nonregular: {key}")
        if state == "modified_in_task_scope" and key not in ALLOWED_MODIFIED:
            problems.append(f"unexpected candidate modification: {key}")
        rows.append({
            "path": key,
            "source_bytes": entry["bytes"],
            "source_sha256": entry["sha256"],
            "candidate_sha256": target_hash,
            "state": state,
        })
    actual = {path.relative_to(CANDIDATE).as_posix() for path in CANDIDATE.rglob("*") if path.is_file()}
    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    if extra:
        problems.append("extra candidate paths: " + ", ".join(extra))
    if missing:
        problems.append("missing candidate paths: " + ", ".join(missing))
    return {
        "task": "LIFEOS-P3-131",
        "source_manifest": str(P3_130_MANIFEST.relative_to(ROOT)),
        "source_allowlist_sha256": manifest["source_allowlist_sha256"],
        "source_inventory_count": len(listed),
        "candidate_inventory_count": len(actual),
        "expected_modified_paths": sorted(ALLOWED_MODIFIED),
        "problems": problems,
        "rows": rows,
    }


def snapshot(runtime_root: Path, label: str) -> dict[str, object]:
    if runtime_root.parent != TEMP_ROOT or not runtime_root.name.startswith("run-"):
        raise SystemExit("runtime root is not a direct P3-131 task-owned run directory")
    db = runtime_root / "capture.sqlite"
    if not regular(db):
        raise SystemExit("runtime database is not a regular single-link file")
    uri = f"file:{db}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only=ON")
    tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    unexpected = sorted(set(tables) - set(TABLES) - {"sqlite_sequence"})
    counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES}
    rows = {
        "captures": [dict(zip(["id", "content", "source", "source_id", "artifact_version", "idem_key"], row)) for row in connection.execute("SELECT id,content,source,source_id,artifact_version,idem_key FROM captures ORDER BY id")],
        "links": [dict(zip(["capture_id", "project_id", "context_id", "link_status", "source_id", "artifact_version"], row)) for row in connection.execute("SELECT capture_id,project_id,context_id,link_status,source_id,artifact_version FROM capture_project_links ORDER BY capture_id")],
        "derivations": [dict(zip(["id", "capture_id", "processor", "processor_version", "basis_refs"], row)) for row in connection.execute("SELECT id,capture_id,processor,processor_version,basis_refs FROM derivations ORDER BY id")],
        "candidates": [dict(zip(["id", "capture_id", "derivation_id", "candidate_text", "candidate_state"], row)) for row in connection.execute("SELECT id,capture_id,derivation_id,candidate_text,candidate_state FROM candidate_actions ORDER BY id")],
        "feedback": [dict(zip(["id", "target_kind", "target_id", "decision", "idem_key", "detail"], row)) for row in connection.execute("SELECT id,target_kind,target_id,decision,idem_key,detail FROM feedback ORDER BY id")],
        "actions": [dict(zip(["id", "candidate_id", "context_id", "action_text", "confirmation_kind", "action_state"], row)) for row in connection.execute("SELECT id,candidate_id,context_id,action_text,confirmation_kind,action_state FROM actions ORDER BY id")],
        "action_results": [dict(zip(["id", "action_id", "result_kind", "result_text", "idem_key"], row)) for row in connection.execute("SELECT id,action_id,result_kind,result_text,idem_key FROM action_results ORDER BY id")],
        "audit": [dict(zip(["id", "event", "target_id", "detail"], row)) for row in connection.execute("SELECT id,event,target_id,detail FROM audit ORDER BY id")],
    }
    quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    connection.close()
    return {
        "task": "LIFEOS-P3-131",
        "kind": "actual_tauri_sqlite_snapshot",
        "label": label,
        "runtime_root": str(runtime_root),
        "database": {"bytes": db.stat().st_size, "sha256": digest(db), "quick_check": quick_check, "user_version": version, "tables": tables, "unexpected_tables": unexpected},
        "counts": counts,
        "rows": rows,
    }


def source_scan() -> dict[str, object]:
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    renderer = (CANDIDATE / "ui/app.js").read_text(encoding="utf-8")
    commands = []
    for line in runtime.splitlines():
        if "#[tauri::command]" in line:
            commands.append(line.split("fn ", 1)[1].split("(", 1)[0])
    direct_renderer_forbidden = [term for term in ["sqlite", "fetch(", "XMLHttpRequest", "ModelPort", "AgentPort", "fs.", "readFile", "writeFile"] if term in renderer]
    return {
        "task": "LIFEOS-P3-131",
        "commands": commands,
        "commands_exact": commands == EXPECTED_COMMANDS,
        "renderer_forbidden_matches": direct_renderer_forbidden,
        "capabilities_main": json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8")),
        "tauri_identifier": json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))["identifier"],
    }


def closure_check() -> dict[str, object]:
    closure = EVIDENCE / "UI_DYNAMIC_CLOSURE.md"
    content = closure.read_text(encoding="utf-8")
    expected = [f"D-{number:02d}" for number in range(1, 13)]
    rows = {row.split("|", 3)[1].strip(): row for row in content.splitlines() if row.startswith("| D-")}
    missing = [item for item in expected if item not in rows]
    non_pass = [item for item in expected if item in rows and "| PASS |" not in rows[item]]
    return {
        "task": "LIFEOS-P3-131",
        "closure": str(closure.relative_to(ROOT)),
        "required_rows": expected,
        "missing_rows": missing,
        "non_pass_rows": non_pass,
        "status": "PASS" if not missing and not non_pass else "NOT_PASS",
    }


def final_manifest() -> dict[str, object]:
    candidate_inventory = []
    for path in sorted(item for item in CANDIDATE.rglob("*") if item.is_file()):
        if not regular(path):
            raise SystemExit(f"candidate contains nonregular file: {path}")
        candidate_inventory.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)})
    evidence_inventory = []
    for path in sorted(item for item in EVIDENCE.rglob("*") if item.is_file()):
        if path.name == "FINAL_MANIFEST.json" or "build-cache" in path.parts:
            continue
        if not regular(path):
            raise SystemExit(f"evidence contains nonregular file: {path}")
        evidence_inventory.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)})
    task_card = ROOT / "lifeos/tasks/LIFEOS-P3-131_evidence_backed_context_recovery_candidate_next_action_feedback_loop.md"
    return {
        "task": "LIFEOS-P3-131",
        "manifest_kind": "non_self_referential_final_manifest",
        "task_contract_sha256": digest(task_card),
        "candidate_inventory_count": len(candidate_inventory),
        "candidate_inventory": candidate_inventory,
        "evidence_inventory_count": len(evidence_inventory),
        "evidence_inventory": evidence_inventory,
        "excluded_from_evidence_inventory": [
            {"path": str((EVIDENCE / "FINAL_MANIFEST.json").relative_to(ROOT)), "reason": "self-reference prohibited"},
            {"path": str((EVIDENCE / "build-cache").relative_to(ROOT)), "reason": "task-local rebuild cache; no verification assertion depends on cache bytes"},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True, dest="command")
    lineage_parser = sub.add_parser("lineage")
    lineage_parser.add_argument("--out", type=Path, required=True)
    scan_parser = sub.add_parser("scan")
    scan_parser.add_argument("--out", type=Path, required=True)
    snapshot_parser = sub.add_parser("snapshot")
    snapshot_parser.add_argument("--runtime-root", type=Path, required=True)
    snapshot_parser.add_argument("--label", required=True)
    snapshot_parser.add_argument("--out", type=Path, required=True)
    closure_parser = sub.add_parser("closure")
    closure_parser.add_argument("--out", type=Path, required=True)
    manifest_parser = sub.add_parser("manifest")
    manifest_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "lineage":
        payload = source_lineage()
    elif args.command == "scan":
        payload = source_scan()
    elif args.command == "closure":
        payload = closure_check()
    elif args.command == "manifest":
        payload = final_manifest()
    else:
        payload = snapshot(args.runtime_root, args.label)
    atomic_json(args.out, payload)
    print(json.dumps({"output": str(args.out), "problems": payload.get("problems", []), "counts": payload.get("counts", {})}, ensure_ascii=False))


if __name__ == "__main__":
    main()
