#!/usr/bin/env python3
"""Read-only verifier for the P3-141 Phase A synthetic candidate.

It intentionally names only authorized fixture, candidate, and fixed-input
locations.  It neither accepts nor probes a real-pilot root.
"""
from __future__ import annotations

import hashlib
import json
import re
import argparse
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[4]
TASK_ROOT = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141"
CANDIDATE = TASK_ROOT / "candidate"
DEFAULT_P3_140_CANDIDATE = Path(
    "/Users/xxe/.codex/worktrees/a2e2/No.2/"
    "lifeos/engineering/LIFEOS-P3-140/closure-1/candidate"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def framed_tree(root: Path) -> tuple[int, str]:
    tree = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        tree.update(len(relative).to_bytes(8, "big"))
        tree.update(relative)
        tree.update(len(content).to_bytes(8, "big"))
        tree.update(content)
    return len(files), tree.hexdigest()


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P3-141 read-only verifier")
    parser.add_argument(
        "--input-root",
        type=Path,
        default=WORKSPACE,
        help="absolute root containing lifeos/tasks fixed inputs; explicit for portable replay",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=DEFAULT_P3_140_CANDIDATE,
        help="read-only P3-140 candidate baseline",
    )
    parsed = parser.parse_args()
    if not parsed.input_root.is_absolute() or not parsed.baseline_root.is_absolute():
        parser.error("--input-root and --baseline-root must be absolute paths")
    return parsed


def main() -> None:
    args = arguments()
    fixed_path = args.input_root / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json"
    fixed = json.loads(fixed_path.read_text(encoding="utf-8"))
    verified_inputs: dict[str, bool] = {}
    for item in fixed["entries"]:
        path = Path(item["path"])
        if not path.is_absolute():
            path = args.input_root / path
        verified_inputs[item["role"]] = digest(path) == item["sha256"]

    baseline_count, baseline_tree = framed_tree(args.baseline_root)
    source = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    ipc_match = re.search(r"const IPC: \[&str; (\d+)\] = \[(.*?)\];", source, re.S)
    ipc = re.findall(r'"([a-z_]+)"', ipc_match.group(2)) if ipc_match else []
    profile_match = re.search(r"fn provider_profiles\(\).*?vec!\[(.*?)\]", source)
    profiles = re.findall(r'"([a-z_]+)"', profile_match.group(1)) if profile_match else []

    prohibited_marker = b"LifeOS-Self-Use-" + b"Pilot-6"
    forbidden_content_hits = []
    for path in sorted(TASK_ROOT.rglob("*")):
        if path.is_file() and path != Path(__file__):
            if prohibited_marker in path.read_bytes():
                forbidden_content_hits.append(path.relative_to(TASK_ROOT).as_posix())

    result = {
        "schema": "lifeos.p3-141.phase-a-readonly-verifier.v1",
        "input_root": str(args.input_root),
        "fixed_inventory": str(fixed_path),
        "baseline_root": str(args.baseline_root),
        "fixed_input_hashes": verified_inputs,
        "fixed_input_all_match": all(verified_inputs.values()),
        "p3_140_baseline": {
            "file_count": baseline_count,
            "tree_sha256": baseline_tree,
            "expected_file_count": 79,
            "expected_tree_sha256": "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e",
            "match": baseline_count == 79
            and baseline_tree == "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e",
        },
        "precontact_seal": {
            "test_design_sha256": digest(TASK_ROOT / "test_design.md"),
            "write_allowlist_sha256": digest(TASK_ROOT / "write_allowlist.md"),
        },
        "candidate": {
            "file_count": framed_tree(CANDIDATE)[0],
            "tree_sha256": framed_tree(CANDIDATE)[1],
            "ipc_count": len(ipc),
            "ipc_exactly_20": len(ipc) == 20,
            "profiles": profiles,
            "profiles_closed_four": profiles == ["openai", "anthropic", "ollama", "lm_studio"],
            "provider_lock_present": "provider_locked_after_first_send" in source,
            "phase_b_gate_present": "phase_b_independent_pass_required" in source,
            "loopback_only_present": "synthetic_loopback_only" in source,
        },
        "content_exclusion": {
            "prohibited_pilot_marker_hits": forbidden_content_hits,
            "pass": not forbidden_content_hits,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
