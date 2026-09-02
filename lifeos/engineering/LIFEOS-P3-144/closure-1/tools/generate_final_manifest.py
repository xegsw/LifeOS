#!/usr/bin/env python3
"""Generate the Closure-1 manifest without declaring the manifest itself."""

import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
CLOSURE = REPO / "lifeos/engineering/LIFEOS-P3-144/closure-1"
OUTPUT = CLOSURE / "FINAL_MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(paths: list[Path]) -> list[dict[str, str]]:
    return [
        {"path": str(path.relative_to(REPO)), "sha256": digest(path)}
        for path in sorted(paths)
    ]


candidate = entries([
    path for path in (REPO / "lifeos/engineering/LIFEOS-P3-144/candidate").rglob("*")
    if path.is_file()
])

fixed_inputs = entries([
    REPO / "lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md",
    REPO / "lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop_acceptance_basis_freeze.md",
    REPO / "lifeos/tasks/LIFEOS-P3-144_acceptance_freeze_manifest.json",
])

preserved_history = entries([
    REPO / "lifeos/deliverables/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md",
    REPO / "lifeos/engineering/LIFEOS-P3-144/FINAL_MANIFEST.json",
    REPO / "lifeos/reviews/LIFEOS-P3-144/independent-review/independent_review.md",
])

closure_files = [
    path for path in CLOSURE.rglob("*")
    if path.is_file() and path not in {OUTPUT, CLOSURE / "evidence/manifest_verification.json"}
]
payload = {
    "schema": "lifeos.p3-144.closure-1.final-manifest.v1",
    "task": "LIFEOS-P3-144",
    "closure": "independent_review_root_authority",
    "self_exclusion": True,
    "candidate": candidate,
    "fixed_inputs": fixed_inputs,
    "preserved_history": preserved_history,
    "closure_evidence": entries(closure_files),
}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"manifest": str(OUTPUT.relative_to(REPO)), "entries": sum(len(payload[key]) for key in ("candidate", "fixed_inputs", "preserved_history", "closure_evidence"))}, ensure_ascii=False))
