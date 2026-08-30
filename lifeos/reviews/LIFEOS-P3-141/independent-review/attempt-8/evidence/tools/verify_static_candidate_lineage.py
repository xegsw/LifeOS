#!/usr/bin/env python3
"""Review-owned, read-only candidate lineage verifier for attempt-8."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


EXPECTED_COMMIT = "c7087586d89a52bc252765ec89fa63611f585d0e"
EXPECTED_TREE = "ffde1eaa9d595441ee96bc50dbbfbffab933a53f0c6feac7c94ab45a3938d6ef"
EXPECTED_FILE_COUNT = 79
EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context",
    "get_evidence_backed_understanding", "decide_understanding_feedback",
    "get_ai_provider_settings", "save_ai_provider_settings",
    "set_ai_provider_session_credential", "test_ai_provider_connection",
    "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state",
    "resolve_request_context", "get_context_disclosure_receipt",
]


def git(path: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(path), *args], check=True, text=True,
                          capture_output=True).stdout.strip()


def component_key(path: Path) -> tuple[str, ...]:
    # Rust PathBuf::Ord compares path components.  String sorting would give
    # a different answer around file-vs-directory prefixes.
    return path.parts


def framed_tree(root: Path) -> tuple[int, str]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs.sort()
        for name in sorted(names):
            item = Path(current) / name
            if item.is_symlink() or not item.is_file():
                raise RuntimeError(f"non-regular-or-linked entry: {item}")
            files.append(item.relative_to(root))
    hasher = hashlib.sha256()
    for relative in sorted(files, key=component_key):
        encoded = relative.as_posix().encode("utf-8")
        body = (root / relative).read_bytes()
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
        hasher.update(len(body).to_bytes(8, "big"))
        hasher.update(body)
    return len(files), hasher.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_static_candidate_lineage.py CANDIDATE_ROOT")
    candidate = Path(sys.argv[1]).resolve(strict=True)
    file_count, tree_sha256 = framed_tree(candidate)
    runtime = (candidate / "src" / "runtime.rs").read_text(encoding="utf-8")
    match = re.search(r"\.invoke_handler\(tauri::generate_handler!\[([\s\S]*?)\]\)", runtime)
    if not match:
        raise RuntimeError("exact Tauri handler inventory unavailable")
    actual_ipc = re.findall(r"\b[a-z][a-z0-9_]*\b", match.group(1))
    actual_ipc = [item for item in actual_ipc if item not in {"tauri", "generate_handler"}]
    status = git(candidate, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    result = {
        "verifier_identity": "attempt-8-review-owned-static-candidate-lineage-v1",
        "candidate_root": str(candidate),
        "candidate_commit": git(candidate, "rev-parse", "HEAD"),
        "candidate_git_tree": git(candidate, "rev-parse", "HEAD^{tree}"),
        "candidate_status_porcelain": status,
        "candidate_file_count": file_count,
        "candidate_tree_sha256": tree_sha256,
        "candidate_tree_algorithm": "SHA-256 framed PathBuf-component-order: path-byte-length/path/content-byte-length/content",
        "ipc_count": len(actual_ipc),
        "ipc": actual_ipc,
        "checks": {
            "fixed_commit": git(candidate, "rev-parse", "HEAD") == EXPECTED_COMMIT,
            "candidate_clean": not status,
            "candidate_file_count_79": file_count == EXPECTED_FILE_COUNT,
            "candidate_tree_matches": tree_sha256 == EXPECTED_TREE,
            "exact_20_ipc": actual_ipc == EXPECTED_IPC,
        },
    }
    result["verdict"] = "Pass" if all(result["checks"].values()) else "Rework"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
