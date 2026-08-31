#!/usr/bin/env python3
"""Read-only candidate and built-artifact integrity probe for this review."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path("/Users/xxe/.codex/worktrees/506c/No.2")
CANDIDATE = WORKTREE / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate"
COMMIT = "476e5f069671dc7d0dc53be88f9d328901d6d543"
BINARY = Path("/private/tmp/lifeos-p3-141-revision-3-independent-review-final-v4/target/release/bundle/macos/LifeOS P3-141 Controlled Pilot Candidate.app/Contents/MacOS/lifeos-p3-141")

def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def candidate_tree_digest() -> tuple[int, str]:
    hasher = hashlib.sha256()
    files = sorted(path for path in CANDIDATE.rglob("*") if path.is_file())
    for path in files:
        name = path.relative_to(CANDIDATE).as_posix().encode("utf-8")
        body = path.read_bytes()
        hasher.update(len(name).to_bytes(8, "big")); hasher.update(name)
        hasher.update(len(body).to_bytes(8, "big")); hasher.update(body)
    return len(files), hasher.hexdigest()

if len(sys.argv) != 3 or sys.argv[1] not in {"pre-cleanup", "post-cleanup"}:
    raise SystemExit("usage: integrity_probe.py {pre-cleanup|post-cleanup} OUTPUT_JSON")
phase, output = sys.argv[1:]
file_count, tree_hash = candidate_tree_digest()
diff = subprocess.run(
    ["/usr/bin/git", "diff", "--quiet", COMMIT, "--", str(CANDIDATE.relative_to(WORKTREE))],
    cwd=WORKTREE,
)
payload = {
    "schema": "lifeos.p3-141.review-candidate-integrity.v1",
    "phase": phase,
    "candidate_commit": COMMIT,
    "candidate_currently_byte_identical_to_commit": diff.returncode == 0,
    "candidate_file_count": file_count,
    "candidate_tree_sha256": tree_hash,
    "binary_exists": BINARY.is_file(),
}
if BINARY.is_file(): payload["binary_sha256"] = digest(BINARY)
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
