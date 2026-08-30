#!/usr/bin/env python3
"""Read-only, review-owned Phase B static verifier for LIFEOS-P3-141."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding",
    "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings",
    "set_ai_provider_session_credential", "test_ai_provider_connection", "set_ai_provider_enabled",
    "upsert_durable_memory", "update_current_state", "resolve_request_context",
    "get_context_disclosure_receipt",
]
EXPECTED_PROVIDERS = ["openai", "anthropic", "ollama", "lm_studio"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def framed_tree(root: Path) -> tuple[int, str, list[dict[str, object]]]:
    digest = hashlib.sha256()
    rows: list[dict[str, object]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
        rows.append({"path": rel.decode("utf-8"), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    return len(rows), digest.hexdigest(), rows


def fixed_inputs(inventory_path: Path, master_root: Path) -> dict[str, object]:
    inv = json.loads(inventory_path.read_text(encoding="utf-8"))
    rows = []
    for entry in inv["entries"]:
        raw = Path(entry["path"])
        path = raw if raw.is_absolute() else master_root / raw
        rows.append({
            "role": entry["role"], "path": str(path), "expected_bytes": entry["bytes"],
            "actual_bytes": path.stat().st_size, "expected_sha256": entry["sha256"],
            "actual_sha256": sha256(path),
        })
    for row in rows:
        row["match"] = row["expected_bytes"] == row["actual_bytes"] and row["expected_sha256"] == row["actual_sha256"]
    return {"inventory_sha256": sha256(inventory_path), "entries": rows, "all_match": all(row["match"] for row in rows)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--p3-140-candidate", type=Path, required=True)
    parser.add_argument("--master-root", type=Path, required=True)
    args = parser.parse_args()

    candidate_count, candidate_tree, candidate_rows = framed_tree(args.candidate)
    baseline_count, baseline_tree, _ = framed_tree(args.p3_140_candidate)
    lineage = json.loads((args.task_root / "evidence/source_lineage.json").read_text(encoding="utf-8"))
    manifest_path = args.task_root / "evidence/FINAL_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = {
        path.relative_to(args.task_root).as_posix(): sha256(path)
        for path in sorted(args.task_root.rglob("*"))
        if path.is_file() and path != manifest_path
    }
    declared = manifest.get("files", {})
    runtime = (args.candidate / "src/runtime.rs").read_text(encoding="utf-8")
    build_script = (args.candidate / "build.rs").read_text(encoding="utf-8")
    match = re.search(r"const IPC: \[&str; (\d+)\] = \[(.*?)\];", runtime, re.S)
    ipc = re.findall(r'"([a-z_]+)"', match.group(2)) if match else []
    profiles = re.findall(r'"([a-z_]+)"', re.search(r"fn provider_profiles\(\).*?vec!\[(.*?)\]", runtime, re.S).group(1))
    fixed_path = args.master_root / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json"

    result = {
        "schema": "lifeos.p3_141.attempt_7.review_owned_static.v1",
        "fixed_inputs": fixed_inputs(fixed_path, args.master_root),
        "candidate": {
            "root": str(args.candidate), "file_count": candidate_count, "tree_sha256": candidate_tree,
            "rows": candidate_rows,
            "source_lineage_file_count": lineage["p3_141_candidate"]["file_count"],
            "source_lineage_tree_sha256": lineage["p3_141_candidate"]["tree_sha256"],
            "source_lineage_match": candidate_count == lineage["p3_141_candidate"]["file_count"] and candidate_tree == lineage["p3_141_candidate"]["tree_sha256"],
        },
        "p3_140": {
            "file_count": baseline_count, "tree_sha256": baseline_tree,
            "expected_file_count": 79,
            "expected_tree_sha256": "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e",
            "match": baseline_count == 79 and baseline_tree == "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e",
        },
        "ipc": {
            "declared_length": int(match.group(1)) if match else None, "commands": ipc,
            "unique_count": len(set(ipc)), "exactly_expected": ipc == EXPECTED_IPC,
            "exactly_20": len(ipc) == 20 and len(set(ipc)) == 20,
        },
        "provider_closure": {
            "profiles": profiles, "exactly_four": profiles == EXPECTED_PROVIDERS,
            "has_first_send_lock": "provider_locked_after_first_send" in runtime,
            "has_no_fallback_guard": "provider_locked_after_first_send" in runtime,
            "synthetic_loopback_marker": "synthetic_loopback_only" in runtime,
        },
        "phase_gate": {
            "runtime_requires_receipt_literal": "LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS" in runtime,
            "build_accepts_env_literal": "LIFEOS_P3_141_PHASE_B_RECEIPT" in build_script and "LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS" in build_script,
            "build_verifies_review_artifact": any(token in build_script for token in ["FINAL_MANIFEST", "independent_review", "review receipt", "signature"]),
        },
        "engineering_manifest": {
            "declared_count": manifest.get("file_count_excluding_manifest"), "actual_count": len(actual),
            "self_reference_excluded": "evidence/FINAL_MANIFEST.json" not in declared,
            "missing": sorted(set(declared) - set(actual)), "extra": sorted(set(actual) - set(declared)),
            "hash_mismatch": sorted(name for name in set(declared) & set(actual) if declared[name] != actual[name]),
        },
    }
    result["engineering_manifest"]["all_149_match"] = (
        result["engineering_manifest"]["declared_count"] == 149 and result["engineering_manifest"]["actual_count"] == 149
        and not result["engineering_manifest"]["missing"] and not result["engineering_manifest"]["extra"]
        and not result["engineering_manifest"]["hash_mismatch"] and result["engineering_manifest"]["self_reference_excluded"]
    )
    result["pass"] = all([
        result["fixed_inputs"]["all_match"], result["candidate"]["source_lineage_match"], result["p3_140"]["match"],
        result["ipc"]["exactly_20"], result["ipc"]["exactly_expected"], result["provider_closure"]["exactly_four"],
        result["engineering_manifest"]["all_149_match"], result["phase_gate"]["build_verifies_review_artifact"],
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
