#!/usr/bin/env python3
"""Create and verify a non-self-referential manifest after marker-gated cleanup."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"


def inventory(root: Path, excluded: set[str] | None = None) -> tuple[dict[str, dict[str, object]], str]:
    excluded = excluded or set()
    tree = hashlib.sha256()
    entries: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        if path.is_symlink():
            raise RuntimeError(f"symlink not permitted: {rel}")
        if not path.is_file():
            continue
        raw = path.read_bytes()
        name = rel.encode("utf-8")
        tree.update(len(name).to_bytes(8, "big"))
        tree.update(name)
        tree.update(len(raw).to_bytes(8, "big"))
        tree.update(raw)
        entries[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return entries, tree.hexdigest()


def selected_inventory(root: Path, names: list[str]) -> tuple[dict[str, dict[str, object]], str]:
    tree = hashlib.sha256()
    entries: dict[str, dict[str, object]] = {}
    for rel in sorted(names):
        path = root / rel
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"required regular closure document missing: {rel}")
        raw = path.read_bytes()
        encoded = rel.encode("utf-8")
        tree.update(len(encoded).to_bytes(8, "big"))
        tree.update(encoded)
        tree.update(len(raw).to_bytes(8, "big"))
        tree.update(raw)
        entries[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return entries, tree.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    output = EVIDENCE / "FINAL_MANIFEST.json"
    verifier = EVIDENCE / "manifest_verification.json"
    if output.exists() or verifier.exists():
        raise RuntimeError("refusing to overwrite final manifest or verifier")
    cleanup = json.loads((EVIDENCE / "cleanup_receipt.json").read_text(encoding="utf-8"))
    if cleanup.get("status") != "REMOVED_EXACT_TASK_ROOT" or cleanup.get("root_exists_after") is not False:
        raise RuntimeError("exact cleanup receipt is not PASS")
    source_lineage = json.loads((EVIDENCE / "source_lineage.json").read_text(encoding="utf-8"))
    actual = json.loads((EVIDENCE / "actual_tauri_provider_viewports.json").read_text(encoding="utf-8"))
    tests = json.loads((EVIDENCE / "test_result.json").read_text(encoding="utf-8"))
    candidate_entries, candidate_tree = inventory(ROOT / "candidate")
    tools_entries, tools_tree = inventory(ROOT / "tools")
    evidence_entries, evidence_tree = inventory(EVIDENCE, {"FINAL_MANIFEST.json", "manifest_verification.json"})
    document_names = ["ABF2_matrix.md", "engineering_report.md", "precontact_seal.json", "replay.sh", "test_design.md", "write_allowlist.md"]
    document_entries, document_tree = selected_inventory(ROOT, document_names)
    manifest = {
        "schema": "lifeos.p3-141.provider-restoration.final-manifest.v1",
        "result": "ENGINEERING_READY_FOR_FRESH_INDEPENDENT_REVIEW",
        "scope": "P3-141 Provider Restoration Closure synthetic offline only",
        "non_self_referential": True,
        "self_entry_present": False,
        "excluded_from_evidence_inventory": ["FINAL_MANIFEST.json", "manifest_verification.json"],
        "conclusions": {
            "engineering": "READY_FOR_FRESH_INDEPENDENT_REVIEW",
            "independent_review": "PENDING_MANDATORY_SEPARATE_SESSION",
            "pm_acceptance": "PENDING_PM",
            "phase_c_d_e": "PENDING",
            "old_phase_b_pass": "WITHDRAWN_NOT_RESTORED",
        },
        "acceptance": {"ABF2_M001_to_M007": "PASS", "ABF2_M008": "PENDING_SEPARATE_INDEPENDENT_REVIEW", "ABF2_M009": "PASS", "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0},
        "lineage": source_lineage,
        "tests": tests,
        "actual_tauri": {"result": actual["result"], "views": {name: {"direct_pid": value["direct_pid"], "native_web_role": value["native_web_role"], "ax_window_frame": value["ax_window_frame"]} for name, value in actual["views"].items()}},
        "candidate": {"file_count": len(candidate_entries), "length_framed_tree_sha256": candidate_tree, "entries": candidate_entries},
        "closure_documents": {"file_count": len(document_entries), "length_framed_tree_sha256": document_tree, "entries": document_entries},
        "closure_tools": {"file_count": len(tools_entries), "length_framed_tree_sha256": tools_tree, "entries": tools_entries},
        "evidence": {"file_count": len(evidence_entries), "length_framed_tree_sha256": evidence_tree, "entries": evidence_entries},
        "cleanup": cleanup,
    }
    write_json(output, manifest)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    re_entries, re_tree = inventory(EVIDENCE, {"FINAL_MANIFEST.json", "manifest_verification.json"})
    re_document_entries, re_document_tree = selected_inventory(ROOT, document_names)
    verification = {
        "schema": "lifeos.p3-141.provider-restoration.manifest-verification.v1",
        "result": "PASS",
        "manifest_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "self_entry_present": "FINAL_MANIFEST.json" in loaded["evidence"]["entries"],
        "evidence_tree_matches": re_tree == loaded["evidence"]["length_framed_tree_sha256"],
        "evidence_entries_match": re_entries == loaded["evidence"]["entries"],
        "candidate_tree_matches": candidate_tree == loaded["candidate"]["length_framed_tree_sha256"],
        "closure_documents_tree_matches": re_document_tree == loaded["closure_documents"]["length_framed_tree_sha256"],
        "closure_documents_entries_match": re_document_entries == loaded["closure_documents"]["entries"],
        "tools_tree_matches": tools_tree == loaded["closure_tools"]["length_framed_tree_sha256"],
    }
    verification_checks = [value for key, value in verification.items() if key.endswith("_matches") or key.endswith("_entries_match")]
    if verification["self_entry_present"] or not all(value is True for value in verification_checks):
        raise RuntimeError("manifest verification failed")
    write_json(verifier, verification)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
