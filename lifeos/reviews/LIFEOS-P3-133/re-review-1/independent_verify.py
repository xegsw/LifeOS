#!/usr/bin/env python3
"""Read-only verification for the P3-133 Closure-2 independent re-review.

This script does not import or call an engineering verifier and never refers to
or resolves any real-use directory. Its only output is task-local review JSON.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path


WORKSPACE = Path("/Users/xxe/Documents/No.2")
REVIEW = WORKSPACE / "lifeos/reviews/LIFEOS-P3-133/re-review-1"
CANDIDATE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-133/candidate"
CLOSURE = WORKSPACE / "lifeos/engineering/LIFEOS-P3-133/evidence/closure-2"
FREEZE = WORKSPACE / "lifeos/tasks/LIFEOS-P3-133_acceptance_freeze_manifest.json"
P3132 = WORKSPACE / "lifeos/engineering/LIFEOS-P3-132/evidence/FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode)
    except FileNotFoundError:
        return False


def inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        rows.append(
            {
                "path": relative,
                "type": "regular" if regular(path) else "not_regular",
                "bytes": path.lstat().st_size,
                "sha256": sha256(path) if regular(path) else None,
            }
        )
    return rows


def compare_manifest(
    root: Path, declared: list[dict[str, object]], exclude: set[str] | None = None
) -> dict[str, object]:
    actual = [row for row in inventory(root) if row["path"] not in (exclude or set())]
    expected = {str(row["path"]): row for row in declared}
    found = {str(row["path"]): row for row in actual}
    missing = sorted(set(expected) - set(found))
    extra = sorted(set(found) - set(expected))
    mismatches: list[str] = []
    for relative in sorted(set(expected) & set(found)):
        want = expected[relative]
        got = found[relative]
        if (
            want.get("type", "regular") != got["type"]
            or want.get("bytes") != got["bytes"]
            or want.get("sha256") != got["sha256"]
        ):
            mismatches.append(relative)
    return {
        "declared": len(declared),
        "actual": len(actual),
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "passed": not missing and not extra and not mismatches,
    }


def check_fixed_inputs(freeze: dict[str, object]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    bundles = [freeze["task_contract"], freeze["acceptance_basis"], freeze["user_confirmation"]]
    bundles.extend(freeze["fixed_inputs"])
    for item in bundles:
        path = WORKSPACE / str(item["path"])
        entries.append(
            {
                "path": str(item["path"]),
                "regular": regular(path),
                "expected_sha256": str(item["sha256"]),
                "actual_sha256": sha256(path) if regular(path) else None,
            }
        )
    for entry in entries:
        entry["passed"] = entry["regular"] and entry["expected_sha256"] == entry["actual_sha256"]
    return entries


def source_checks() -> dict[str, object]:
    app = (CANDIDATE / "ui/app.js").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    build = (CANDIDATE / "build.rs").read_text(encoding="utf-8")
    capability = json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8"))
    config = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    read_marker = "const realCaptureText = name === \"capture-real\""
    busy_marker = "state.busy = true; state.error = null; render();"
    old_pattern = "state.busy = true; state.error = null; render();\n    const realCaptureText"
    expected_ipc = [
        "capture_record", "get_today", "runtime_status", "confirm_capture_context",
        "get_context_recovery", "get_context_next_action", "decide_context_next_action",
        "record_action_result", "assemble_global_ai_context",
        "get_evidence_backed_understanding", "decide_understanding_feedback",
    ]
    return {
        "read_before_busy_render": app.find(read_marker) >= 0 and app.find(read_marker) < app.find(busy_marker),
        "old_read_after_render_pattern_absent": old_pattern not in app,
        "runtime_declares_exact_eleven": all(f'\"{name}\"' in runtime for name in expected_ipc) and runtime.count("#[tauri::command]") == 11,
        "capability_permissions_empty": capability.get("permissions") == [],
        "csp_connect_only_ipc": config["app"]["security"]["csp"].find("connect-src ipc:") >= 0,
        "runtime_real_mode_model_disabled": "disabled_in_real_mode" in runtime and "disabled_for_real_input" in runtime,
        "runtime_no_generic_surface": all(token in runtime for token in ["generic_path_api:false", "shell:false", "network:false", "raw_database:false"]),
        "build_requires_explicit_root_and_mode": all(token in build for token in ["LIFEOS_RUNTIME_ROOT", "LIFEOS_INPUT_MODE", "root must be an absolute normalized path"]),
        "expected_ipc": expected_ipc,
    }


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    closure = json.loads((CLOSURE / "FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    prior = json.loads(P3132.read_text(encoding="utf-8"))
    fixed = check_fixed_inputs(freeze)
    candidate = compare_manifest(CANDIDATE, closure["candidate_inventory"])
    closure_evidence = compare_manifest(
        CLOSURE, closure["closure_evidence_inventory"], {"FINAL_MANIFEST.json"}
    )
    prior_candidate = compare_manifest(
        WORKSPACE / "lifeos/engineering/LIFEOS-P3-132/candidate", prior["candidate_inventory"]
    )
    static = source_checks()
    static_pass = all(value for key, value in static.items() if key != "expected_ipc")
    result = {
        "kind": "P3-133 re-review-1 independent read-only verification",
        "engine_verifier_imported_or_called": False,
        "fixed_inputs": fixed,
        "closure_manifest": {
            "task_contract_sha_matches_freeze": closure["task_contract_sha256"] == freeze["task_contract"]["sha256"],
            "acceptance_basis_sha_matches_freeze": closure["acceptance_basis_freeze_sha256"] == freeze["acceptance_basis"]["sha256"],
            "p3_132_source_manifest_sha_matches_freeze": closure["source_manifest_sha256"] == freeze["fixed_inputs"][1]["sha256"],
            "candidate_inventory": candidate,
            "closure_evidence_inventory": closure_evidence,
            "self_excluded": closure.get("excluded_from_closure_evidence_inventory") == ["FINAL_MANIFEST.json (self)"],
        },
        "p3_132_history_candidate": prior_candidate,
        "static_source_checks": static,
    }
    result["passed"] = (
        all(item["passed"] for item in fixed)
        and result["closure_manifest"]["task_contract_sha_matches_freeze"]
        and result["closure_manifest"]["acceptance_basis_sha_matches_freeze"]
        and result["closure_manifest"]["p3_132_source_manifest_sha_matches_freeze"]
        and candidate["passed"]
        and closure_evidence["passed"]
        and prior_candidate["passed"]
        and result["closure_manifest"]["self_excluded"]
        and static_pass
    )
    name = sys.argv[1] if len(sys.argv) == 2 else "static-verification.json"
    output = REVIEW / name
    if output.parent != REVIEW or output.name != name:
        raise SystemExit("unauthorized output")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
