#!/usr/bin/env python3
"""Write a non-self-referential inventory for the stopped P3-141 attempt.

This is archival only.  It deliberately makes no validation or acceptance
claim about the listed test, build, or native-capture outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE = Path.cwd().resolve()
REVISION = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings"
CANDIDATE = REVISION / "candidate"
EVIDENCE = REVISION / "evidence/bundle-lineage-closure-v1"
MANIFEST = REVISION / "BUNDLE_LINEAGE_CLOSURE_INVALIDATED_MANIFEST.json"
REPORT = WORKSPACE / "lifeos/deliverables/LIFEOS-P3-141_revision-3_bundle-lineage-and-native-capture-closure_report.md"
FIXED_INPUTS = [
    WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md",
    WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md",
    WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_model_settings_baseline_user_confirmation.md",
    WORKSPACE / "lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md",
    WORKSPACE / "lifeos/reviews/LIFEOS-P3-141_pm_revision_3_mode_delete_final_independent_review_invalidated.md",
]


def record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(WORKSPACE).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }


def main() -> None:
    package_files = sorted(
        [path for path in CANDIDATE.rglob("*") if path.is_file() and not path.is_symlink()]
        + [path for path in EVIDENCE.rglob("*") if path.is_file() and not path.is_symlink()]
        + [REVISION / "verify_bundle_lineage_closure.py", REPORT],
    )
    exclusions = [MANIFEST.relative_to(WORKSPACE).as_posix()]
    payload = {
        "schema": "lifeos.p3-141.bundle-lineage-invalidated-attempt-manifest.v1",
        "task_id": "LIFEOS-P3-141",
        "status": "INVALIDATED",
        "finding_counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0},
        "invalidation": {
            "reason": "A helper compile output was created outside the one authorized Closure root.",
            "record": (EVIDENCE / "PROCEDURAL_DEVIATION.md").relative_to(WORKSPACE).as_posix(),
            "positive_evidence_status": "All test, build, and native-capture outputs listed here are archival invalidated-attempt history only; none is valid positive Engineering Evidence.",
        },
        "authorized_root_cleanup": json.loads((EVIDENCE / "cleanup-after-invalidated-run.json").read_text(encoding="utf-8")),
        "manifest_exclusions": exclusions,
        "fixed_inputs": [record(path) for path in FIXED_INPUTS],
        "files": [record(path) for path in package_files],
        "non_conclusions": [
            "Not an Engineering Pass or independent review.",
            "Does not restore Phase C, authorize Pilot-6, real Provider, credential, risk closure, product freeze, or Stage 4.",
        ],
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "files": len(payload["files"]), "manifest": str(MANIFEST)}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
