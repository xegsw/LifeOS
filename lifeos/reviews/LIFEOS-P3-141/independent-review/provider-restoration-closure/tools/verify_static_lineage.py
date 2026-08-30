#!/usr/bin/env python3
"""Review-owned, read-only lineage and provider-surface check after a P0 stop."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_entry(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def manifest_candidate_check(root: Path, manifest: Path) -> dict:
    declared = json.loads(manifest.read_text(encoding="utf-8"))["candidate"]
    expected = declared["entries"]
    actual_paths = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    missing = sorted(set(expected) - set(actual_paths))
    extra = sorted(set(actual_paths) - set(expected))
    mismatches = {}
    for relative in sorted(set(expected) & set(actual_paths)):
        actual = file_entry(root / relative)
        if actual != expected[relative]:
            mismatches[relative] = {"expected": expected[relative], "actual": actual}
    return {
        "manifest": str(manifest),
        "manifest_sha256": sha256(manifest),
        "declared_file_count": declared["file_count"],
        "actual_file_count": len(actual_paths),
        "declared_length_framed_tree_sha256": declared["length_framed_tree_sha256"],
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "pass": not missing and not extra and not mismatches and len(actual_paths) == declared["file_count"],
    }


def one_line(path: Path, prefix: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line
    raise ValueError(f"missing {prefix!r} in {path}")


def main() -> int:
    if len(sys.argv) != 7:
        raise SystemExit("usage: verify_static_lineage.py MAIN_ROOT P3140_CANDIDATE P3140_MANIFEST P3141_CANDIDATE P3141_MANIFEST OUTPUT")
    main_root, p3140_candidate, p3140_manifest, p3141_candidate, p3141_manifest, output = map(Path, sys.argv[1:])
    main_root = main_root.resolve()
    p3140_candidate = p3140_candidate.resolve()
    p3140_manifest = p3140_manifest.resolve()
    p3141_candidate = p3141_candidate.resolve()
    p3141_manifest = p3141_manifest.resolve()
    output = output.resolve()

    inventory = json.loads((main_root / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_2.json").read_text(encoding="utf-8"))
    fixed = []
    for entry in inventory["entries"]:
        path = Path(entry["path"])
        path = path if path.is_absolute() else main_root / path
        actual = file_entry(path)
        fixed.append({"role": entry["role"], "path": str(path), "expected": {"bytes": entry["bytes"], "sha256": entry["sha256"]}, "actual": actual, "pass": actual == {"bytes": entry["bytes"], "sha256": entry["sha256"]}})

    runtime_140 = p3140_candidate / "src/runtime.rs"
    runtime_141 = p3141_candidate / "src/runtime.rs"
    ui_140 = p3140_candidate / "ui/runtime-adapter.js"
    ui_141 = p3141_candidate / "ui/runtime-adapter.js"
    provider_lines = [
        "enum ProviderProfile ",
        "fn provider_profiles() ",
        "fn profile_name(",
        "fn profile_matches_mode(",
        "fn model_port(",
    ]
    comparison = {prefix: {"p3_140": one_line(runtime_140, prefix), "p3_141": one_line(runtime_141, prefix)} for prefix in provider_lines}
    for item in comparison.values():
        item["pass"] = item["p3_140"] == item["p3_141"]
    ui_lines = [
        "    const profiles = cloudMode ?",
        "      <section class=\"panel provider-panel provider-mode-panel\"",
    ]
    ui_comparison = {prefix: {"p3_140": one_line(ui_140, prefix), "p3_141": one_line(ui_141, prefix)} for prefix in ui_lines}
    for item in ui_comparison.values():
        item["pass"] = item["p3_140"] == item["p3_141"]

    command_names = []
    for line in runtime_141.read_text(encoding="utf-8").splitlines():
        marker = "#[tauri::command] fn "
        if marker in line:
            command_names.append(line.split(marker, 1)[1].split("(", 1)[0])
    previous_receipt = main_root / "lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-8/phase_b_pass_receipt.json"
    receipt = json.loads(previous_receipt.read_text(encoding="utf-8"))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    p140 = manifest_candidate_check(p3140_candidate, p3140_manifest)
    p141 = manifest_candidate_check(p3141_candidate, p3141_manifest)
    result = {
        "schema": "lifeos.p3_141.provider_restoration.independent.static_lineage.v1",
        "review_owned": True,
        "candidate_commit_current_worktree": head,
        "fixed_inputs": fixed,
        "p3_140_manifest_candidate": p140,
        "p3_141_engineering_manifest_candidate": p141,
        "provider_source_exact_line_comparison": comparison,
        "settings_label_exact_line_comparison": ui_comparison,
        "p3_141_ipc": {"count": len(command_names), "names": command_names, "pass_exactly_20": len(command_names) == 20},
        "attempt_8_read_only_history": {
            "receipt_path": str(previous_receipt),
            "receipt_sha256": sha256(previous_receipt),
            "abf_id": receipt["abf_id"],
            "abf_sha256": receipt["abf_sha256"],
            "verdict": receipt["verdict"],
            "status_in_revision_2": "superseded_for_positive_acceptance",
        },
        "overall_static_facts_pass": all(item["pass"] for item in fixed) and p140["pass"] and p141["pass"] and all(item["pass"] for item in comparison.values()) and all(item["pass"] for item in ui_comparison.values()) and len(command_names) == 20,
        "scope_note": "These are read-only static facts collected after the Phase-C gate P0. They do not establish dynamic loopback, mutation, actual-Tauri, or a positive review conclusion.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall_static_facts_pass": result["overall_static_facts_pass"], "fixed_inputs": len(fixed), "ipc_count": len(command_names)}, ensure_ascii=False))
    return 0 if result["overall_static_facts_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
