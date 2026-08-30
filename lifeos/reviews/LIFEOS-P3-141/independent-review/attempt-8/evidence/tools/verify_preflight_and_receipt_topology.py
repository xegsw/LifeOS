#!/usr/bin/env python3
"""Review-owned, read-only preflight and Phase-B receipt-topology verifier."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def framed_tree(root: Path) -> tuple[int, str]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in dirs + names:
            candidate = current_path / name
            if candidate.is_symlink():
                raise RuntimeError(f"linked candidate entry: {candidate}")
        for name in names:
            candidate = current_path / name
            if not candidate.is_file():
                raise RuntimeError(f"non-regular candidate entry: {candidate}")
            files.append(candidate.relative_to(root))
    files.sort(key=lambda item: item.as_posix())
    hasher = hashlib.sha256()
    for relative in files:
        relative_bytes = relative.as_posix().encode("utf-8")
        content = (root / relative).read_bytes()
        hasher.update(len(relative_bytes).to_bytes(8, "big"))
        hasher.update(relative_bytes)
        hasher.update(len(content).to_bytes(8, "big"))
        hasher.update(content)
    return len(files), hasher.hexdigest()


def git(path: Path, *args: str) -> str:
    output = subprocess.run(["git", "-C", str(path), *args], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output.stdout.strip()


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: verify_preflight_and_receipt_topology.py ENGINEERING_ROOT CANDIDATE_ROOT REVIEW_ATTEMPT FIXED_INVENTORY")
    engineering, candidate, review, inventory_path = map(Path, sys.argv[1:])
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    frozen_project_root = inventory_path.parents[2]

    fixed = []
    for entry in inventory["entries"]:
        path = Path(entry["path"])
        if not path.is_absolute():
            path = frozen_project_root / path
        actual_bytes = path.stat().st_size
        actual_hash = digest(path)
        fixed.append({"role": entry["role"], "path": str(path), "bytes_match": actual_bytes == entry["bytes"], "sha256_match": actual_hash == entry["sha256"]})

    manifest_path = engineering / "evidence" / "FINAL_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_results = []
    for relative, expected in manifest["files"].items():
        path = engineering / relative
        if path.is_symlink() or not path.is_file():
            manifest_results.append({"path": relative, "status": "not_regular"})
        else:
            manifest_results.append({"path": relative, "status": "match" if digest(path) == expected else "mismatch"})

    candidate_count, candidate_tree = framed_tree(candidate)
    lineage = json.loads((engineering / "evidence" / "source_lineage.json").read_text(encoding="utf-8"))
    source = (candidate / "src" / "runtime.rs").read_text(encoding="utf-8")
    ipc_match = re.search(r"const IPC: \[&str; 20\] = \[(.*?)\];", source, flags=re.DOTALL)
    ipc_count = len(re.findall(r'"[^"\\n]+"', ipc_match.group(1))) if ipc_match else -1

    build = (candidate / "build.rs").read_text(encoding="utf-8")
    contract = (engineering / "evidence" / "phase_b_receipt_contract.md").read_text(encoding="utf-8")
    candidate_top = git(candidate, "rev-parse", "--show-toplevel")
    review_top = git(review, "rev-parse", "--show-toplevel")
    candidate_status = git(candidate, "status", "--porcelain=v1", "--untracked-files=all")
    review_status = git(review, "status", "--porcelain=v1", "--untracked-files=all")
    call_index = build.index("Some(validate_phase_b_receipt())")
    root_index = build.index("let root = frozen_runtime_root")
    same_top = candidate_top == review_top
    topology = "BLOCKED_SAME_GIT_TOP" if same_top else "PEER_TOPOLOGY_POSSIBLE"

    result = {
        "schema": "lifeos.p3-141.attempt-8.review-preflight-topology.v1",
        "task_id": "LIFEOS-P3-141",
        "review_owned": True,
        "candidate_commit": git(candidate, "rev-parse", "HEAD"),
        "fixed_inputs": {"expected": 12, "verified": len(fixed), "all_match": all(item["bytes_match"] and item["sha256_match"] for item in fixed), "entries": fixed},
        "candidate": {"file_count": candidate_count, "tree_sha256": candidate_tree, "expected_file_count": 79, "expected_tree_sha256": lineage["p3_141_candidate"]["tree_sha256"], "tree_matches_lineage": candidate_tree == lineage["p3_141_candidate"]["tree_sha256"], "ipc_count": ipc_count},
        "engineering_manifest": {"declared_entries": manifest["file_count_excluding_manifest"], "verified_entries": len(manifest_results), "all_hashes_match": all(item["status"] == "match" for item in manifest_results)},
        "receipt_gate": {"legacy_string_rejected_in_source": "legacy receipt string is prohibited" in build, "receipt_before_runtime_root_in_source": call_index < root_index, "peer_worktree_required_in_source": "review_top == candidate_top" in build and "declared peer-worktree" in build, "separate_worktree_required_in_contract": "separately owned Git worktree" in contract},
        "topology": {"candidate_git_top": candidate_top, "review_git_top": review_top, "same_git_top": same_top, "candidate_worktree_dirty": bool(candidate_status), "review_worktree_dirty": bool(review_status), "result": topology, "reason": "The approved attempt-8 write root resolves to the candidate Git top, while the verifier requires a distinct declared peer review worktree. Committing only attempt-8 cannot change that equality; changing it requires an unauthorized new review worktree or a changed Task Contract."},
        "verdict": "BLOCKED" if same_top else "NOT_BLOCKED_BY_TOPOLOGY",
        "positive_evidence_used": False
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if same_top and result["fixed_inputs"]["all_match"] and result["candidate"]["tree_matches_lineage"] and result["candidate"]["ipc_count"] == 20 and result["engineering_manifest"]["all_hashes_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
