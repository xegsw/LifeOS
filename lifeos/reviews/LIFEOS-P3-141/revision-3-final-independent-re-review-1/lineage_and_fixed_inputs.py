#!/usr/bin/env python3
"""Review-owned fixed-input and read-only lineage verification."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("/Users/xxe/.codex/worktrees/506c/No.2")
REVIEW = Path(__file__).resolve().parent
INVENTORY = ROOT / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_3.json"
CANDIDATE = "476e5f069671dc7d0dc53be88f9d328901d6d543"
ENGINEERING_GUI_V2 = "2e39acfdf0d3a740d0e672037ba5c8e802cfa39e"
PRIOR_BLOCKED = "beca425560a74a73457802034db77484391a8231"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def subject(commit: str) -> str:
    return subprocess.check_output(["/usr/bin/git", "show", "-s", "--format=%s", commit], cwd=ROOT, text=True).strip()

inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
fixed = []
for item in inventory["inputs"]:
    actual = sha256(ROOT / item["path"])
    fixed.append({"path": item["path"], "expected_sha256": item["sha256"], "actual_sha256": actual, "match": actual == item["sha256"]})
payload = {
    "schema": "lifeos.p3-141.revision-3.review-lineage.v1",
    "fixed_inputs": fixed,
    "fixed_input_pass_count": sum(bool(row["match"]) for row in fixed),
    "fixed_input_fail_count": sum(not bool(row["match"]) for row in fixed),
    "candidate_commit": CANDIDATE,
    "candidate_subject": subject(CANDIDATE),
    "candidate_parent": subprocess.check_output(["/usr/bin/git", "show", "-s", "--format=%P", CANDIDATE], cwd=ROOT, text=True).strip(),
    "candidate_matches_worktree_path": subprocess.run(["/usr/bin/git", "diff", "--quiet", CANDIDATE, "--", "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate"], cwd=ROOT).returncode == 0,
    "engineering_gui_v2_commit": ENGINEERING_GUI_V2,
    "engineering_gui_v2_subject": subject(ENGINEERING_GUI_V2),
    "prior_blocked_review_commit": PRIOR_BLOCKED,
    "prior_blocked_review_subject": subject(PRIOR_BLOCKED),
    "history_positive_evidence_reused": False,
}
(REVIEW / "lineage_and_fixed_inputs.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
