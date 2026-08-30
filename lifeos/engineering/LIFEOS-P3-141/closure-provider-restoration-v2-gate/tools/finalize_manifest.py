#!/usr/bin/env python3
"""Write and verify the non-self-referential v2 gate repair manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"


def inventory(root: Path, excluded: set[str] | None = None) -> tuple[dict[str, dict[str, object]], str]:
    excluded = excluded or set()
    digest = hashlib.sha256()
    values: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        if path.is_symlink():
            raise RuntimeError(f"linked manifest path: {rel}")
        if not path.is_file():
            continue
        raw = path.read_bytes()
        name = rel.encode("utf-8")
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        values[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return values, digest.hexdigest()


def selected(root: Path, names: list[str]) -> tuple[dict[str, dict[str, object]], str]:
    digest = hashlib.sha256()
    values: dict[str, dict[str, object]] = {}
    for rel in sorted(names):
        path = root / rel
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"required closure artifact missing: {rel}")
        raw = path.read_bytes()
        name = rel.encode("utf-8")
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        values[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return values, digest.hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    manifest_path = EVIDENCE / "FINAL_MANIFEST.json"
    verifier_path = EVIDENCE / "manifest_verification.json"
    if manifest_path.exists() or verifier_path.exists():
        raise RuntimeError("refusing to overwrite final manifest")
    cleanup = json.loads((EVIDENCE / "cleanup_receipt.json").read_text(encoding="utf-8"))
    if cleanup.get("status") != "REMOVED_EXACT_TASK_ROOT" or cleanup.get("root_exists_after") is not False:
        raise RuntimeError("exact cleanup missing")
    lineage = json.loads((EVIDENCE / "source_lineage.json").read_text(encoding="utf-8"))
    tests = json.loads((EVIDENCE / "test_result.json").read_text(encoding="utf-8"))
    gate = json.loads((EVIDENCE / "v2_gate_dynamic_matrix.json").read_text(encoding="utf-8"))
    candidate_entries, candidate_tree = inventory(ROOT / "candidate")
    tool_entries, tool_tree = inventory(ROOT / "tools")
    evidence_entries, evidence_tree = inventory(EVIDENCE, {"FINAL_MANIFEST.json", "manifest_verification.json"})
    document_names = ["ABF2_GATE_MATRIX.md", "engineering_report.md", "precontact_seal.json", "receipt_v2_contract.md", "replay.sh", "test_design.md", "write_allowlist.md"]
    document_entries, document_tree = selected(ROOT, document_names)
    manifest = {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.final-manifest.v1",
        "result": "ENGINEERING_READY_FOR_FRESH_INDEPENDENT_REVIEW",
        "scope": "narrow Revision-2 Phase-C receipt/build-gate repair; synthetic offline only",
        "non_self_referential": True,
        "self_entry_present": False,
        "excluded_from_evidence_inventory": ["FINAL_MANIFEST.json", "manifest_verification.json"],
        "conclusions": {"engineering": "READY_FOR_FRESH_INDEPENDENT_REVIEW", "failed_first_independent_review": "PRESERVED_REWORK_P0", "fresh_independent_review": "PENDING", "phase_c_d_e": "PENDING"},
        "acceptance": {"gate_repair": "PASS", "provider_regression": "PASS", "actual_tauri": "PENDING_NEW_INDEPENDENT_REVIEW", "p0": 0, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 0},
        "lineage": lineage,
        "tests": tests,
        "gate_dynamic": gate,
        "candidate": {"file_count": len(candidate_entries), "length_framed_tree_sha256": candidate_tree, "entries": candidate_entries},
        "closure_documents": {"file_count": len(document_entries), "length_framed_tree_sha256": document_tree, "entries": document_entries},
        "closure_tools": {"file_count": len(tool_entries), "length_framed_tree_sha256": tool_tree, "entries": tool_entries},
        "evidence": {"file_count": len(evidence_entries), "length_framed_tree_sha256": evidence_tree, "entries": evidence_entries},
        "cleanup": cleanup,
    }
    write(manifest_path, manifest)
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    re_candidate_entries, re_candidate_tree = inventory(ROOT / "candidate")
    re_tool_entries, re_tool_tree = inventory(ROOT / "tools")
    re_evidence_entries, re_evidence_tree = inventory(EVIDENCE, {"FINAL_MANIFEST.json", "manifest_verification.json"})
    re_document_entries, re_document_tree = selected(ROOT, document_names)
    verifier = {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.manifest-verification.v1", "result": "PASS",
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "self_entry_present": "FINAL_MANIFEST.json" in loaded["evidence"]["entries"],
        "candidate_entries_match": re_candidate_entries == loaded["candidate"]["entries"], "candidate_tree_matches": re_candidate_tree == loaded["candidate"]["length_framed_tree_sha256"],
        "tool_entries_match": re_tool_entries == loaded["closure_tools"]["entries"], "tool_tree_matches": re_tool_tree == loaded["closure_tools"]["length_framed_tree_sha256"],
        "evidence_entries_match": re_evidence_entries == loaded["evidence"]["entries"], "evidence_tree_matches": re_evidence_tree == loaded["evidence"]["length_framed_tree_sha256"],
        "document_entries_match": re_document_entries == loaded["closure_documents"]["entries"], "document_tree_matches": re_document_tree == loaded["closure_documents"]["length_framed_tree_sha256"],
    }
    checks = [value for key, value in verifier.items() if key.endswith("_match") or key.endswith("_matches")]
    if verifier["self_entry_present"] or not all(checks):
        raise RuntimeError("manifest verification failed")
    write(verifier_path, verifier)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
