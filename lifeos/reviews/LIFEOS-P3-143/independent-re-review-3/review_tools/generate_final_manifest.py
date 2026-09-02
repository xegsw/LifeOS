#!/usr/bin/env python3
"""Generate the non-self-referential final manifest for this invalidated review package."""

import hashlib
import json
from pathlib import Path

ROOT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-3")
OUTPUT = ROOT / "FINAL_MANIFEST.json"
INCLUDE = [
    "test_design.md", "allowlist.md", "prohibited_paths.md", "precontact_seal.md", "precontact_seal.sha256",
    "runtime_root_binding.md", "native_bundle_runtime_root_binding.md", "p0_procedural_invalidation.md", "fixed_inputs.sha256", "input_availability.md", "checkpoint.json", "cleanup_receipt.json", "native_rebind_attempt.json",
    "evidence_engineering_final_manifest.json", "evidence_phase_a_manifest.json", "evidence_p3_142_manifest.json",
    "evidence_history_manifest.json", "evidence_static_contract.json", "review_matrix.md", "independent_review.md",
    "evidence/native_bundle_lineage.json", "evidence/native_pid_ax_capture.json", "evidence/native_pid_ax_roles.json", "evidence/native_pid_target_only.png",
    "evidence/native_desktop_capture.json", "evidence/native_desktop_target_only.png", "evidence/native_compact_resize.json", "evidence/native_compact_capture.json", "evidence/native_compact_target_only.png",
    "evidence/native_narrow_resize.json", "evidence/native_narrow_capture.json", "evidence/native_narrow_target_only.png",
    "review_tools/verify_nonself_manifest.py", "review_tools/verify_static_contract.py",
    "review_tools/marker_gated_cleanup.py", "review_tools/generate_final_manifest.py",
    "review_tools/verify_review_final_manifest.py", "review_tools/native_pid_ax_capture.swift", "review_tools/probe_exact_pid_ax.swift", "review_tools/resize_exact_pid_window.swift", "review_tools/capture_exact_pid_window.swift", "review_tools/verify_native_bundle.py",
    "review_runtime_harness/Cargo.toml", "review_runtime_harness/src/lib.rs", "review_runtime_harness/src/review_probes.rs",
]


def digest(path: Path) -> dict:
    content = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def main() -> None:
    files = [digest(ROOT / relative) for relative in INCLUDE]
    document = {
        "schema": "lifeos.p3-143.independent-rereview-3.final-manifest.v1",
        "task": "LIFEOS-P3-143",
        "review_status": "INVALIDATED_PROCEDURAL_P0",
        "candidate_commit": "a95a0beb27dc0dac183f8a29da550f43af0d6ce3",
        "self_referential": False,
        "self_exclusion": ["FINAL_MANIFEST.json", "final_manifest_verification.json"],
        "excluded_artifacts": [
            "review_runtime_harness/target-run-a",
            "candidate-app-target",
            "tmp",
            "Cargo.lock and candidate-derived configuration symlinks",
        ],
        "files": files,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "entries": len(files), "self_referential": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
