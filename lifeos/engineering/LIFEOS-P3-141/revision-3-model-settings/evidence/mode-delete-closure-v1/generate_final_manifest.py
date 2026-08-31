#!/usr/bin/env python3
"""Generate the non-self-referential Closure Cycle manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE = Path.cwd().resolve()
RELATIVE_REVISION = Path("lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings")
REVISION = WORKSPACE / RELATIVE_REVISION
EVIDENCE = REVISION / "evidence/mode-delete-closure-v1"
MANIFEST = REVISION / "MODE_DELETE_CLOSURE_FINAL_MANIFEST.json"
EXCLUDED = {
    "generate_final_manifest.py",
    "verify_mode_delete_closure.py",
    "manifest-verification.json",
}


def digest(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(WORKSPACE).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


def main() -> None:
    if not (REVISION / "candidate/ui/runtime-adapter.js").is_file():
        raise SystemExit("candidate root is absent")
    evidence_files = sorted(
        path for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name not in EXCLUDED
    )
    candidate_files = [
        REVISION / "candidate/ui/runtime-adapter.js",
        REVISION / "candidate/tests/mode_delete_ui_contract.mjs",
    ]
    frozen_inputs = [
        WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md",
        WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md",
        WORKSPACE / "lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md",
        WORKSPACE / "lifeos/reviews/LIFEOS-P3-141_pm_revision_3_final_independent_re_review_1.md",
        WORKSPACE / "lifeos/reviews/LIFEOS-P3-141/revision-3-final-independent-re-review-1/P2-001_mode_display_backend_divergence.json",
    ]
    manifest = {
        "schema": "lifeos.p3-141.mode-delete-closure-final-manifest.v1",
        "task_id": "LIFEOS-P3-141",
        "closure_cycle": "CL-MODE-DELETE-01",
        "candidate_lineage": {
            "fixed_candidate_commit": "476e5f069671dc7d0dc53be88f9d328901d6d543",
            "candidate_path": "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate",
            "change": "Persisted provider mode is separated from an unsaved visual draft; credential actions require the persisted mode to match the display mode.",
        },
        "frozen_inputs": [digest(path) for path in frozen_inputs],
        "verification_summary": {
            "offline_rust": "51 passed; 0 failed with the default --locked --offline command after a test-only race fixture was narrowed to its unique request id.",
            "ui_contract": "mode-delete-ui-contract: PASS before and after the test-only race fix.",
            "offline_bundle": "cargo tauri build --bundles app --no-sign --ci -- --locked --offline completed after the final candidate change.",
            "actual_app": "Direct-PID desktop, compact, and narrow native AX evidence; visible Cloud draft while persisted Local disables credential management; confirmed synthetic UI deletion gives SQLite row count 0 and a fresh direct-PID restart has no saved credential.",
            "mutations": "Wrong marker, non-0700 runtime directory, stale visual delete action, and shared-runtime contamination were fail-closed or isolated. The preserved parallel test fixture race was corrected as a test-only change and the default suite now passes; historical outputs are retained.",
        },
        "residuals_within_engineering_closure": {
            "P0": 0,
            "P1": 0,
            "P2": 0,
            "Unknown": 0,
            "Not_Implemented": 0,
            "scope": "Only the P2-001 mode/delete divergence closure and its authorized synthetic evidence.",
        },
        "non_conclusions": [
            "This is not an independent review conclusion.",
            "This does not authorize Phase C, real Provider, real credential, Pilot-6, risk closure, product freeze, or stage change.",
        ],
        "manifest_exclusions": [
            MANIFEST.relative_to(WORKSPACE).as_posix(),
            (EVIDENCE / "generate_final_manifest.py").relative_to(WORKSPACE).as_posix(),
            (EVIDENCE / "verify_mode_delete_closure.py").relative_to(WORKSPACE).as_posix(),
            (EVIDENCE / "manifest-verification.json").relative_to(WORKSPACE).as_posix(),
        ],
        "files": [digest(path) for path in candidate_files + evidence_files],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
