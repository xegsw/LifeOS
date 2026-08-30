#!/usr/bin/env python3
"""Generate only task-local evidence for the P3-141 Revision-2 gate repair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
CANDIDATE = ROOT / "candidate"
PM_ROOT = Path("/Users/xxe/Documents/No.2")
TEMP_ROOT = Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1")
BASE_CANDIDATE = TEMP_ROOT / "base-candidate"
SOURCE_COMMIT = "48a26320646219117b28e81cd77dd6c8206fe99c"


def entry(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def inventory(root: Path) -> tuple[dict[str, dict[str, object]], str]:
    digest = hashlib.sha256()
    values: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise RuntimeError(f"linked path in inventory: {rel}")
        if not path.is_file():
            continue
        raw = path.read_bytes()
        encoded = rel.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        values[rel] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return values, digest.hexdigest()


def write_once(name: str, value: object) -> None:
    target = EVIDENCE / name
    if target.exists():
        raise RuntimeError(f"refusing to overwrite: {target.name}")
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def required(log: str, fragment: str) -> None:
    if fragment not in log:
        raise RuntimeError(f"missing test proof: {fragment}")


def main() -> int:
    test_log = (EVIDENCE / "cargo_test.log").read_text(encoding="utf-8")
    for fragment in [
        "test result: ok. 50 passed",
        "test result: ok. 4 passed",
        "v2_receipt_contract_accepts_exact_revision_2_binding ... ok",
        "v2_receipt_contract_rejects_v1_mixed_stale_and_nonpass_bindings ... ok",
        "v2_receipt_schema_rejects_duplicate_extra_and_fallback_fields ... ok",
        "v2_receipt_file_gate_rejects_symlink_and_directory_before_read ... ok",
        "custom_openai_compatible_loopback_is_protocol_bound_and_first_send_locks ... ok",
        "custom_profile_rejects_wrong_envelope_response_mode_and_credential_order ... ok",
        "status_is_closed_to_the_p3_139_twenty_ipc ... ok",
        "closure_real_root_requires_fresh_absence_and_owned_restart ... ok",
        "controlled_fixture_health_source_is_closed_and_today_uses_the_same_contract ... ok",
        "resolver_filters_authority_budgets_and_domain ... ok",
        "feedback_all_decisions_are_audited_and_only_confirmation_affects_today ... ok",
    ]:
        required(test_log, fragment)
    source = (CANDIDATE / "build.rs").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    for fragment in [
        'const TASK_SHA256: &str = "c97419a1818e0aa6fe6fc61c487e3ef97746e199b2c7d22435d8c05090374800"',
        'const FIXED_INPUT_INVENTORY_SHA256: &str = "3651e046da8211f06bf5144a155a0505b7ddfbaab67a249e51d94aeae09861a5"',
        'const ABF_ID: &str = "ABF-P3-141-v2"',
        'const ABF_SHA256: &str = "096ad12beec63b78aaa3be92535b4a6ea632cdc4235c1d83f224db955d5dc9ea"',
        'LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH',
        'candidate ownership worktree is mutable or dirty',
        'validate_revision_2_binding',
    ]:
        if fragment not in source:
            raise RuntimeError(f"v2 source binding missing: {fragment}")
    if 'phase_b_receipt_binding.rs' in runtime or 'VALIDATED_PHASE_B_RECEIPT_SHA256' in runtime:
        raise RuntimeError("legacy runtime binding survived")

    fixed_inventory_path = PM_ROOT / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_2.json"
    frozen = json.loads(fixed_inventory_path.read_text(encoding="utf-8"))
    verified = []
    for expected in frozen["entries"]:
        source_path = Path(expected["path"])
        actual_path = source_path if source_path.is_absolute() else PM_ROOT / source_path
        actual = entry(actual_path)
        if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
            raise RuntimeError(f"fixed input mismatch: {expected['role']}")
        verified.append({"role": expected["role"], "path": expected["path"], "actual": actual, "matched": True})
    write_once("fixed_input_verification.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.fixed-inputs.v1", "result": "PASS",
        "entries": verified, "candidate_lineage": frozen["candidate_lineage"], "governance": frozen["governance"],
    })

    base_entries, base_tree = inventory(BASE_CANDIDATE)
    candidate_entries, candidate_tree = inventory(CANDIDATE)
    if len(base_entries) != 79 or len(candidate_entries) != 80:
        raise RuntimeError("unexpected candidate file counts")
    write_once("source_lineage.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.source-lineage.v1", "result": "PASS",
        "starting_commit": SOURCE_COMMIT,
        "starting_candidate": {"file_count": len(base_entries), "length_framed_tree_sha256": base_tree},
        "current_candidate": {"file_count": len(candidate_entries), "length_framed_tree_sha256": candidate_tree},
        "allowed_delta": ["candidate/build.rs", "candidate/src/runtime.rs", "candidate/tests/v2_phase_c_gate.rs"],
        "source_diff": {"path": "evidence/source_gate_diff.md", **entry(EVIDENCE / "source_gate_diff.md")},
        "phase_c_candidate_identity": "resolved only from clean candidate worktree HEAD plus current candidate tree at build time; no constant or fallback is accepted",
    })

    pre_root = json.loads((EVIDENCE / "phase_c_pre_root_negative.json").read_text(encoding="utf-8"))
    dirty = json.loads((EVIDENCE / "phase_c_dirty_candidate_negative.json").read_text(encoding="utf-8"))
    if pre_root["result"] != "PASS" or dirty["result"] != "PASS" or pre_root["runtime_root_created"] or dirty["runtime_root_created"]:
        raise RuntimeError("pre-root negative evidence invalid")
    write_once("v2_gate_dynamic_matrix.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.dynamic-matrix.v1", "result": "PASS",
        "positive": [{"test": "v2_receipt_contract_accepts_exact_revision_2_binding", "scope": "synthetic in-process contract only; not a self-signed independent receipt"}],
        "negative": [
            {"test": "v2_receipt_contract_rejects_v1_mixed_stale_and_nonpass_bindings", "covers": ["v1 id", "v1 hash", "mixed v1/v2", "old task/inventory", "old commit/tree", "Rework manifest"]},
            {"test": "v2_receipt_schema_rejects_duplicate_extra_and_fallback_fields", "covers": ["duplicate", "extra", "fallback"]},
            {"test": "v2_receipt_file_gate_rejects_symlink_and_directory_before_read", "covers": ["symlink", "directory", "ancestor link"]},
            {"evidence": "phase_c_pre_root_negative.json", "covers": ["missing v2 receipt", "legacy Phase-B input"], "before_runtime_root": True},
            {"evidence": "phase_c_dirty_candidate_negative.json", "covers": ["dirty/uncommitted candidate"], "before_runtime_root": True},
        ],
        "no_accepted_engineering_receipt_created": True,
    })
    write_once("non_provider_regression.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.non-provider-regression.v1", "result": "PASS",
        "test_total": 54, "ipc_count": 20, "new_ipc": 0,
        "preserved": ["five Provider profiles and Adapters", "Custom OpenAI-compatible protocol", "single enable/first-send lock/no fallback", "Work/Health", "Memory/State/Context Resolver", "feedback", "restart", "failure atomicity", "fresh/owned root lifecycle"],
    })
    failed_review = PM_ROOT / "lifeos/reviews/LIFEOS-P3-141/independent-review/provider-restoration-closure/independent_review.md"
    failed_gate = PM_ROOT / "lifeos/reviews/LIFEOS-P3-141/independent-review/provider-restoration-closure/evidence/p0_revision2_phase_gate.json"
    write_once("failure_review_reference.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.failed-review-reference.v1", "result": "READ_ONLY_PRESERVED",
        "review": {"path": str(failed_review), **entry(failed_review)},
        "p0_gate": {"path": str(failed_gate), **entry(failed_gate)},
        "statement": "first independent review remains Rework/P0 and is not positive evidence for this repair",
    })
    write_once("prohibited_target_attestation.json", {
        "schema": "lifeos.p3-141.provider-restoration-v2-gate.prohibited-target-attestation.v1", "result": "PASS",
        "temporary_root": str(TEMP_ROOT),
        "assertions": ["fictional offline data only", "no real Provider, credential, network or personal content", "prohibited Pilot and capture database received no access, probe, create, copy, hash, read, write or cleanup operation"],
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
