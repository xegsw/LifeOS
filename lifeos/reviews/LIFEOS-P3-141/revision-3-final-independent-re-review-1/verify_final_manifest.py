#!/usr/bin/env python3
"""Independently verify every non-self manifest entry and candidate identity."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
WORKTREE = Path("/Users/xxe/.codex/worktrees/506c/No.2")
CANDIDATE_RELATIVE = "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate"
COMMIT = "476e5f069671dc7d0dc53be88f9d328901d6d543"

def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

manifest = json.loads((REVIEW / "FINAL_MANIFEST.json").read_text(encoding="utf-8"))
records = []
for entry in manifest["entries"]:
    path = REVIEW / entry["path"]
    actual = sha256(path) if path.is_file() and not path.is_symlink() else None
    records.append({"path": entry["path"], "present_regular_file": path.is_file() and not path.is_symlink(), "sha256_match": actual == entry["sha256"]})
payload = {
    "schema": "lifeos.p3-141.final-independent-re-review-manifest-verification.v1",
    "manifest_schema": manifest.get("schema"),
    "entry_count": len(records),
    "all_entries_present_regular": all(row["present_regular_file"] for row in records),
    "all_entry_hashes_match": all(row["sha256_match"] for row in records),
    "candidate_matches_fixed_commit": subprocess.run(["/usr/bin/git", "diff", "--quiet", COMMIT, "--", CANDIDATE_RELATIVE], cwd=WORKTREE).returncode == 0,
    "records": records,
}
(REVIEW / "final_manifest_verification.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
raise SystemExit(0 if payload["all_entries_present_regular"] and payload["all_entry_hashes_match"] and payload["candidate_matches_fixed_commit"] else 1)
