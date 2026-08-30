#!/usr/bin/env python3
"""Review-owned preflight. Stops before source/tree/build contact when candidate is dirty."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EXPECTED_COMMIT = "c7087586d89a52bc252765ec89fa63611f585d0e"


def git(path: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(path), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def value(path: Path, *args: str) -> str:
    return git(path, *args).decode("utf-8").strip()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_peer_worktree_preflight.py CANDIDATE_WORKTREE REVIEW_ATTEMPT")
    candidate, review = map(Path, sys.argv[1:])
    candidate_top = value(candidate, "rev-parse", "--show-toplevel")
    review_top = value(review, "rev-parse", "--show-toplevel")
    candidate_common = value(candidate, "rev-parse", "--path-format=absolute", "--git-common-dir")
    review_common = value(review, "rev-parse", "--path-format=absolute", "--git-common-dir")
    status = git(candidate, "status", "--porcelain=v1", "--untracked-files=all", "-z")
    dirty_entries = len([entry for entry in status.split(b"\0") if entry])
    result = {
        "schema": "lifeos.p3-141.attempt-8.peer-worktree-preflight.v1",
        "task_id": "LIFEOS-P3-141",
        "candidate_commit": value(candidate, "rev-parse", "HEAD"),
        "expected_candidate_commit": EXPECTED_COMMIT,
        "candidate_commit_matches": value(candidate, "rev-parse", "HEAD") == EXPECTED_COMMIT,
        "candidate_git_top": candidate_top,
        "review_git_top": review_top,
        "distinct_worktrees": candidate_top != review_top,
        "candidate_git_common_dir": candidate_common,
        "review_git_common_dir": review_common,
        "same_git_common_dir": candidate_common == review_common,
        "candidate_dirty_entry_count": dirty_entries,
        "candidate_worktree_clean": dirty_entries == 0,
        "candidate_tree_or_build_contact": "NOT_STARTED_BECAUSE_CLEAN_PRECONDITION_FAILED",
        "phase_b_receipt": "NOT_CREATED",
        "phase_c_gate": "NOT_ATTEMPTED",
        "verdict": "BLOCKED" if dirty_entries else "PRECONDITION_PASS"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if dirty_entries else 1


if __name__ == "__main__":
    raise SystemExit(main())
