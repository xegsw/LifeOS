#!/usr/bin/env python3
"""Generate a non-self-referential P3-144 Closure-3 manifest."""

import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
CLOSURE = REPO / "lifeos/engineering/LIFEOS-P3-144/closure-3"
OUTPUT = CLOSURE / "FINAL_MANIFEST.json"
VERIFY_RECEIPT = CLOSURE / "evidence/manifest_verification.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(paths) -> list[dict[str, str]]:
    return [{"path": str(path.relative_to(REPO)), "sha256": digest(path)} for path in sorted(paths)]


prefix = "lifeos/engineering/LIFEOS-P3-144/candidate/"
tracked = subprocess.run(["git", "ls-files", prefix], cwd=REPO, check=True, capture_output=True, text=True).stdout.splitlines()
candidate = entries(REPO / path for path in tracked)
fixed_inputs = entries([
    REPO / "lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md",
    REPO / "lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop_acceptance_basis_freeze.md",
    REPO / "lifeos/tasks/LIFEOS-P3-144_acceptance_freeze_manifest.json",
])
preserved_history = entries([
    REPO / "lifeos/engineering/LIFEOS-P3-144/closure-2/FINAL_MANIFEST.json",
    REPO / "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/independent_review.md",
    REPO / "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3/FINAL_MANIFEST.json",
])
closure_files = [path for path in CLOSURE.rglob("*") if path.is_file() and path not in {OUTPUT, VERIFY_RECEIPT}]
payload = {
    "schema": "lifeos.p3-144.closure-3.final-manifest.v1",
    "task": "LIFEOS-P3-144",
    "closure": "pilot_7_real_gate_profile_activation",
    "self_exclusion": True,
    "candidate": candidate,
    "fixed_inputs": fixed_inputs,
    "preserved_history": preserved_history,
    "closure_evidence": entries(closure_files),
}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"result": "PASS", "manifest": str(OUTPUT.relative_to(REPO)), "candidate": len(candidate), "fixed_inputs": len(fixed_inputs), "preserved_history": len(preserved_history), "closure_evidence": len(payload["closure_evidence"])}, ensure_ascii=False))
