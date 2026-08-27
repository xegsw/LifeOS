#!/usr/bin/env python3
"""Independent, read-only static verification for LIFEOS-P3-130.

This program intentionally does not import, copy, call, or parse the Engineering
runner. It reads only immutable inputs and the submitted candidate/Evidence, then
writes one JSON result beneath this review directory.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REVIEW = Path(__file__).resolve().parent
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-130/candidate"
SOURCE = ROOT / "lifeos/engineering/LIFEOS-P3-126/candidate"
EVIDENCE = ROOT / "lifeos/engineering/LIFEOS-P3-130/evidence"
ALLOWLIST = ROOT / "lifeos/tasks/LIFEOS-P3-130_source_allowlist.md"
TASK = ROOT / "lifeos/tasks/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md"
ARCH = ROOT / "lifeos/architecture/LifeOS架构基线V1.0.md"
HANDOFF = ROOT / "lifeos/architecture/LIFEOS-P3-128/fast_track_handoff.json"
FINAL = EVIDENCE / "FINAL_MANIFEST.json"

EXPECTED_HASHES = {
    str(TASK.relative_to(ROOT)): "f39f1ca8460389fa637f8e1e175f43ef67742697efbb5ea1e8081ed8aacd10ec",
    str(ALLOWLIST.relative_to(ROOT)): "af8fe84d2c809821bd076903ee2bfc303ae397b512c628adc4cf6e6ed7ef6b9c",
    str(ARCH.relative_to(ROOT)): "1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236",
    str(HANDOFF.relative_to(ROOT)): "4e15c8006275b10058d6c307a35ac4e04ebcb63e59a249ed0eaf09962eefd3fd",
    str(FINAL.relative_to(ROOT)): "539d5dc984afe51cbed63009599ae89d2923542a52256f087a8b158ffb076584",
}
ALLOWED_COMMANDS = [
    "capture_record",
    "get_today",
    "runtime_status",
    "confirm_capture_context",
    "get_context_recovery",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(name: str, ok: bool, **detail: object) -> dict[str, object]:
    return {"check": name, "status": "PASS" if ok else "FAIL", **detail}


def inventory(root: Path) -> set[str]:
    return {str(item.relative_to(root)) for item in root.rglob("*") if item.is_file()}


def main() -> int:
    checks: list[dict[str, object]] = []
    for relative, expected in EXPECTED_HASHES.items():
        actual = digest(ROOT / relative)
        checks.append(record("fixed_hash", actual == expected, path=relative, expected=expected, actual=actual))

    raw = ALLOWLIST.read_text(encoding="utf-8")
    rows = re.findall(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", raw, flags=re.M)
    paths = [row[0] for row in rows]
    checks.append(record("physical_allowlist", len(rows) == 75 and len(set(paths)) == 75,
                         physical_data_rows=len(rows), unique_paths=len(set(paths)), literal_backslash_n="\\n" in raw))

    source_rows = []
    source_ok = True
    for rel, bytes_text, expected_sha in rows:
        item = SOURCE / rel
        exists = item.is_file()
        actual_bytes = item.stat().st_size if exists else None
        actual_sha = digest(item) if exists else None
        ok = exists and actual_bytes == int(bytes_text) and actual_sha == expected_sha
        source_ok = source_ok and ok
        source_rows.append({"path": rel, "status": "PASS" if ok else "FAIL", "expected_bytes": int(bytes_text),
                            "actual_bytes": actual_bytes, "expected_sha256": expected_sha, "actual_sha256": actual_sha})
    checks.append(record("source_allowlist_75_of_75", source_ok, rows=source_rows))

    candidate_paths = inventory(CANDIDATE)
    path_set_ok = candidate_paths == set(paths)
    changed = []
    for rel, _, source_sha in rows:
        candidate_sha = digest(CANDIDATE / rel) if (CANDIDATE / rel).is_file() else None
        if candidate_sha != source_sha:
            changed.append({"path": rel, "source_sha256": source_sha, "candidate_sha256": candidate_sha})
    checks.append(record("candidate_path_lineage", path_set_ok, candidate_file_count=len(candidate_paths),
                         allowlist_file_count=len(paths), extra=sorted(candidate_paths - set(paths)),
                         missing=sorted(set(paths) - candidate_paths), changed_from_p3_126=changed))

    manifest = json.loads(FINAL.read_text(encoding="utf-8"))
    candidate_entries = manifest["candidate_inventory"]
    evidence_entries = manifest["evidence_inventory"]
    manifest_rows = candidate_entries + evidence_entries
    manifest_ok = len(candidate_entries) == 75 and len(evidence_entries) == 26 and len(manifest_rows) == 101
    manifest_paths: set[str] = set()
    manifest_mismatches = []
    for entry in manifest_rows:
        path = ROOT / entry["path"]
        manifest_paths.add(entry["path"])
        actual_bytes = path.stat().st_size if path.is_file() else None
        actual_sha = digest(path) if path.is_file() else None
        if actual_bytes != entry["bytes"] or actual_sha != entry["sha256"]:
            manifest_ok = False
            manifest_mismatches.append({"path": entry["path"], "expected_bytes": entry["bytes"], "actual_bytes": actual_bytes,
                                        "expected_sha256": entry["sha256"], "actual_sha256": actual_sha})
    actual_candidate_paths = {str(path.relative_to(ROOT)) for path in CANDIDATE.rglob("*") if path.is_file()}
    actual_evidence_paths = {str(path.relative_to(ROOT)) for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "FINAL_MANIFEST.json" and "build-cache" not in path.parts}
    expected_paths = actual_candidate_paths | actual_evidence_paths
    if manifest_paths != expected_paths:
        manifest_ok = False
        manifest_mismatches.append({"manifest_extra": sorted(manifest_paths - expected_paths), "manifest_missing": sorted(expected_paths - manifest_paths)})
    checks.append(record("engineering_nonself_manifest_101", manifest_ok, candidate_entries=len(candidate_entries),
                         evidence_entries=len(evidence_entries), mismatches=manifest_mismatches,
                         self_excluded=str(FINAL.relative_to(ROOT)) not in manifest_paths))

    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    ui = (CANDIDATE / "ui/app.js").read_text(encoding="utf-8")
    capability = json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8"))
    conf = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    declared = re.findall(r"#\[tauri::command\]\s*fn\s+([a-z_]+)", runtime)
    generated = re.search(r"generate_handler!\[([^]]+)\]", runtime)
    generated_commands = [item.strip() for item in generated.group(1).split(",")] if generated else []
    ui_commands = re.findall(r'invoke\("([a-z_]+)"', ui)
    command_ok = declared == ALLOWED_COMMANDS and generated_commands == ALLOWED_COMMANDS and sorted(set(ui_commands)) == sorted(ALLOWED_COMMANDS)
    checks.append(record("exactly_five_ipc", command_ok, declared=declared, generated=generated_commands, ui=sorted(set(ui_commands))))

    static_forbidden = {
        "ui_direct_sql": re.search(r"sqlite|SELECT\s+|INSERT\s+|UPDATE\s+|DELETE\s+", ui, flags=re.I) is None,
        "ui_network": re.search(r"fetch\s*\(|XMLHttpRequest|WebSocket|https?://", ui, flags=re.I) is None,
        "ui_model_agent": re.search(r"invoke\([^)]*(model|agent)", ui, flags=re.I) is None,
        "no_renderer_permissions": capability.get("permissions") == [],
        "no_prohibited_command_surface": command_ok and all(name not in declared for name in ["create_context", "clear", "delete", "export", "sync"]),
        "offline_runtime_flags": all(f"{key}: false" in runtime for key in ["filesystem", "raw_database", "generic_path_api", "shell", "process_spawn", "network", "vault", "export", "sync"]),
        "no_generic_context_or_memory_table": "CREATE TABLE IF NOT EXISTS contexts" not in runtime and "CREATE TABLE IF NOT EXISTS memory" not in runtime,
        "layers_observable": "UI and Orchestrator must never hold a SQLite handle" not in ui and "sqlite" not in ui.lower(),
        "csp_ipc_only": "connect-src ipc:" in conf["app"]["security"]["csp"],
    }
    checks.append(record("static_boundary", all(static_forbidden.values()), assertions=static_forbidden))

    final_ok = all(item["status"] == "PASS" for item in checks)
    payload = {
        "task": "LIFEOS-P3-130",
        "kind": "independent_static_verification",
        "test_design_sha256": digest(REVIEW / "test_design.md"),
        "engineering_runner_imported_or_called": False,
        "checks": checks,
        "status": "PASS" if final_ok else "FAIL",
    }
    target = REVIEW / "static_verification.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "output": str(target)}, ensure_ascii=False))
    return 0 if final_ok else 1


if __name__ == "__main__":
    sys.exit(main())
