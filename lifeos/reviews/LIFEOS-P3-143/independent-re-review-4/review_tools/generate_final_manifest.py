#!/usr/bin/env python3
"""Generate the non-self-referential re-review-4 manifest from an explicit allowlist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "test_design.md", "allowlist.md", "prohibited_path_declaration.md", "precontact_seal.md", "fixed_input_matrix.json",
    "evidence_static_contract.json", "evidence_root_authority.json", "evidence_build_profile.json", "evidence_bundle_lineage.json", "evidence_candidate_lineage.json",
    "evidence_native_pid_ax.json", "evidence_native_pid_ax_roles.json", "evidence_screenshot_geometry.json", "cleanup_receipt.json", "checkpoint.json",
    "native_desktop_target_only.png", "native_compact_target_only.png", "native_narrow_target_only.png",
    "review_matrix.md", "independent_review.md",
    "review_runtime_harness/Cargo.toml", "review_runtime_harness/Cargo.lock", "review_runtime_harness/build.rs", "review_runtime_harness/tauri.conf.json", "review_runtime_harness/capabilities/main.json", "review_runtime_harness/src/lib.rs",
    "review_tools/verify_static_contract.py", "review_tools/marker_gated_cleanup.py", "review_tools/native_pid_ax_capture.swift", "review_tools/probe_exact_pid_ax.swift", "review_tools/record_bundle_lineage.py", "review_tools/generate_final_manifest.py"
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    entries = []
    for relative in FILES:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"required_manifest_input_missing:{relative}")
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
    document = {
        "schema": "lifeos.p3-143.independent-rereview4.final-manifest.v1",
        "task": "LIFEOS-P3-143",
        "review": "independent-re-review-4",
        "self_referential": False,
        "excluded_from_hash_set": ["FINAL_MANIFEST.json", "review_tools/verify_final_manifest.py", "manifest_verification.json"],
        "fixed_commit": "4f4e6ff25e1821d170e47a7fc87a8c001af65361",
        "candidate_business_commit": "dcbc32518d92e16e26f8c7dfec682630f5d51cde",
        "profile": "independent-review",
        "run_id": "finalgui-20260902",
        "literal_root": "/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902",
        "counts": {"p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0},
        "conclusion": "INDEPENDENT_PASS_SYNTHETIC_OFFLINE_SCOPE",
        "entries": entries,
    }
    (ROOT / "FINAL_MANIFEST.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "entry_count": len(entries)}))

if __name__ == "__main__":
    main()
