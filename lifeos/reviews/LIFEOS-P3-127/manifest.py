#!/usr/bin/env python3
"""Build the non-self-referential P3-127 evidence manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def entry(root: Path, path: Path, role: str) -> dict[str, object]:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise ValueError(f"manifest object must be a regular file: {path}")
    return {
        "role": role,
        "path": str(path.relative_to(root)),
        "bytes": metadata.st_size,
        "sha256": digest(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    review_root = workspace / "lifeos/reviews/LIFEOS-P3-127"
    delivery = workspace / "lifeos/deliverables/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review.md"
    frozen_inputs = [
        ("task_contract", workspace / "lifeos/tasks/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review.md"),
        ("frozen_abf", workspace / "lifeos/tasks/LIFEOS-P3-127_p3_126_clean_start_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md"),
        ("source_allowlist", workspace / "lifeos/tasks/LIFEOS-P3-127_source_allowlist.md"),
        ("authorization", workspace / "lifeos/tasks/LIFEOS-P3-127_authorization/user_confirmation.md"),
        ("authorization", workspace / "lifeos/tasks/LIFEOS-P3-127_authorization/preflight.md"),
        ("authorization", workspace / "lifeos/tasks/LIFEOS-P3-127_authorization/FREEZE_MANIFEST.md"),
        ("protected_inventory", workspace / "lifeos/engineering/LIFEOS-P3-126/evidence/FINAL_MANIFEST.json"),
    ]
    entries = [entry(workspace, path, role) for role, path in frozen_inputs]
    for path in [review_root / "runner.py", review_root / "history_verify.py", review_root / "manifest.py", review_root / "test_design.md"]:
        entries.append(entry(workspace, path, "reviewer_tooling"))
    entries.append(entry(workspace, review_root / "independent_review.md", "independent_review"))
    entries.append(entry(workspace, delivery, "delivery"))
    for path in sorted((review_root / "evidence").rglob("*")):
        if path.is_file() and not path.is_symlink():
            entries.append(entry(workspace, path, "evidence"))
    output = args.output.resolve()
    if output in [workspace / item["path"] for item in entries]:
        raise ValueError("manifest_self_reference")
    output.write_text(
        json.dumps(
            {
                "task_id": "LIFEOS-P3-127",
                "manifest_root": "lifeos/reviews/LIFEOS-P3-127",
                "self_excluded": True,
                "entry_count": len(entries),
                "entries": entries,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
