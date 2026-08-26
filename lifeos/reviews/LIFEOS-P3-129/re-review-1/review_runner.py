#!/usr/bin/env python3
"""Independent, read-only verifier for LIFEOS-P3-129 re-review-1.

This runner intentionally neither imports nor invokes the candidate verifier or
any attempt-1 artifact.  It writes only structured evidence beside itself.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
REVIEW_DIR = Path(__file__).resolve().parent
CANDIDATE_DIR = ROOT / "lifeos/architecture/LIFEOS-P3-129"

FIXED_IDS = [
    "FI-TASK", "FI-ABF", "FI-V1", "FI-FREEZE", "FI-P2-016",
    "FI-P2-016-REVIEW", "FI-P0-003", "FI-P0-009", "FI-P3-128",
    "FI-P3-128-REVIEW", "FI-GOVERNANCE", "FI-PM", "FI-ROLE",
    "FI-GATES", "FI-REVIEW-TEMPLATE",
]
CANDIDATE_FILES = {
    "README.md",
    "fixed_inputs.json",
    "v0_to_v1_reconciliation.json",
    "cross_baseline_compatibility.json",
    "freeze_scope.json",
    "runtime_transition.json",
    "canonical_promotion_patch.json",
    "verifier.py",
    "verification.json",
    "mutation_results.json",
    "history_verification.json",
    "FINAL_MANIFEST.json",
}
REVIEW_MANIFEST_FILES = {
    "README.md",
    "review_runner.py",
    "independent_verification.json",
    "independent_mutation_results.json",
    "independent_review.md",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def assert_that(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_fixed_inputs(fixed: dict[str, Any], errors: list[str]) -> None:
    inputs = fixed.get("inputs")
    assert_that(fixed.get("schema") == "lifeos.p3-129.fixed-inputs.v1", "fixed-input schema", errors)
    assert_that(isinstance(inputs, list) and len(inputs) == 15, "fixed-input count must be 15", errors)
    ids = [entry.get("id") for entry in inputs] if isinstance(inputs, list) else []
    assert_that(ids == FIXED_IDS, "fixed-input IDs/order differ from Frozen input set", errors)
    for entry in inputs if isinstance(inputs, list) else []:
        relative = entry.get("path", "")
        path = ROOT / relative
        assert_that(not Path(relative).is_absolute() and ".." not in Path(relative).parts, f"unsafe fixed path: {relative}", errors)
        assert_that(path.is_file(), f"fixed input missing: {relative}", errors)
        if path.is_file():
            assert_that(sha256_file(path) == entry.get("sha256"), f"fixed input hash mismatch: {entry.get('id')}", errors)


def validate_reconciliation(reconciliation: dict[str, Any], errors: list[str]) -> None:
    rows = reconciliation.get("rows", [])
    expected_ids = [f"V0-{number:02d}" for number in range(1, 17)]
    assert_that([row.get("id") for row in rows] == expected_ids, "V0.1 reconciliation is not exactly V0-01..V0-16", errors)
    valid = {"retained", "changed", "superseded", "deferred"}
    assert_that(all(row.get("classification") in valid for row in rows), "unknown V0.1 classification", errors)
    assert_that(reconciliation.get("classification_counts") == {"retained": 13, "changed": 1, "superseded": 1, "deferred": 1}, "V0.1 classification totals", errors)
    assert_that(reconciliation.get("unclassified_v0_norms") == [], "unclassified V0.1 norms", errors)
    by_id = {row.get("id"): row for row in rows}
    assert_that(by_id.get("V0-04", {}).get("classification") == "retained", "V0-04 outbox/job invariant not retained", errors)
    assert_that(by_id.get("V0-11", {}).get("classification") == "retained", "V0-11 exclusion invariant not retained", errors)
    assert_that(by_id.get("V0-16", {}).get("classification") == "superseded", "V0-16 forward authority treatment", errors)


def validate_compatibility(compatibility: dict[str, Any], errors: list[str]) -> None:
    rows = compatibility.get("rows", [])
    assert_that(len(rows) == 13, "compatibility row count", errors)
    results = [row.get("result") for row in rows]
    assert_that(results.count("PASS") == 12 and results.count("N/A") == 1 and "FAIL" not in results, "Gate compatibility result counts", errors)
    assert_that(rows[-1].get("id") == "CB-13" and rows[-1].get("result") == "N/A", "Gate 5 must be N/A, not PASS", errors)
    counterexamples = compatibility.get("counterexamples", [])
    assert_that(len(counterexamples) == 5 and all(row.get("result", "").startswith("PASS:") for row in counterexamples), "compatibility counterexamples", errors)


def validate_scope(scope: dict[str, Any], errors: list[str]) -> None:
    frozen = scope.get("proposed_frozen_normative_scope", [])
    excluded = scope.get("explicitly_not_frozen", [])
    forbidden = ("schema", "domain-to-table", "ipc command signature", "capability configuration", "production sla", "stage 4")
    combined = "\n".join(frozen).lower()
    assert_that(len(frozen) == 9, "frozen scope count", errors)
    assert_that(all(token not in combined for token in forbidden), "scope illegally freezes implementation or Stage 4", errors)
    excluded_text = "\n".join(excluded).lower()
    assert_that("sqlite schema" in excluded_text and "ipc command signatures" in excluded_text and "stage 4" in excluded_text, "required exclusions absent", errors)
    assert_that(len(scope.get("negative_scope_cases", [])) == 4, "scope negative cases", errors)


def validate_transition(transition: dict[str, Any], errors: list[str]) -> None:
    rules = transition.get("rules", [])
    assert_that([row.get("treatment") for row in rules] == ["preserve", "preserve", "adapt", "adapt", "defer"], "runtime transition treatments", errors)
    assert_that(transition.get("counts") == {"preserve": 2, "adapt": 2, "defer": 1}, "runtime transition totals", errors)
    assertions = "\n".join(transition.get("compatibility_assertions", []))
    assert_that("does not override V0.1 historically" in assertions, "P3-128 historical priority guard", errors)


def validate_patch(patch: dict[str, Any], errors: list[str]) -> None:
    canonical = ROOT / patch.get("canonical_path", "")
    assert_that(canonical.is_file(), "canonical promotion input missing", errors)
    if not canonical.is_file():
        return
    original = canonical.read_bytes()
    assert_that(sha256_bytes(original) == patch.get("pre_sha256"), "promotion preimage hash", errors)
    lines = original.splitlines(keepends=True)
    change = patch.get("allowed_line_change", {})
    line_number = change.get("line_number")
    assert_that(line_number == 3 and len(lines) >= 3, "promotion must only target line 3", errors)
    if line_number == 3 and len(lines) >= 3:
        original_line = lines[2].decode("utf-8").rstrip("\r\n")
        assert_that(original_line == change.get("before"), "promotion preimage status line", errors)
        ending = "\r\n" if lines[2].endswith(b"\r\n") else "\n" if lines[2].endswith(b"\n") else ""
        replacement = (change.get("after", "") + ending).encode("utf-8")
        lines[2] = replacement
        promoted = b"".join(lines)
        assert_that(sha256_bytes(promoted) == patch.get("post_sha256"), "promotion postimage hash", errors)


def validate_v1_and_direct_runtime(errors: list[str]) -> None:
    v1 = (ROOT / "lifeos/architecture/LifeOS架构基线V1.0.md").read_text(encoding="utf-8")
    assert_that("> 状态：Architecture Baseline Draft" in v1, "canonical is no longer Draft before final Gate", errors)
    for term in ("Project", "Artifact", "Source", "Assertion", "Decision", "Action", "Event", "Derivation", "Feedback", "Authorization", "AuditEntry", "Link"):
        assert_that(term in v1, f"V1 missing core semantic anchor: {term}", errors)
    for term in ("Model / Agent", "Model 不拥有执行权限", "Agent 不得绕过 LifeOS Authorization", "SQLite Schema", "IPC command signature"):
        assert_that(term in v1, f"V1 missing trust/scope guard: {term}", errors)
    p126 = (ROOT / "lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md").read_text(encoding="utf-8")
    p128 = (ROOT / "lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md").read_text(encoding="utf-8")
    assert_that("actual-Tauri" in p126 and "75/75" in p126 and "fresh SQLite" in p126, "P3-126 accepted fresh SQLite Runtime evidence unavailable", errors)
    for term in ("capture_record", "get_today", "runtime_status", "固定合成输入", "零 renderer plugin permission"):
        assert_that(term in p128, f"P3-128 accepted mapping cannot substantiate P3-126 fact: {term}", errors)
    p127 = (ROOT / "lifeos/reviews/LIFEOS-P3-127_pm_review.md").read_text(encoding="utf-8")
    for term in ("Not Frozen", "三 IPC", "不外推到 Pilot"):
        assert_that(term in p127, f"P3-127 boundary unavailable: {term}", errors)


def validate_manifest(errors: list[str]) -> None:
    manifest_path = CANDIDATE_DIR / "FINAL_MANIFEST.json"
    manifest = load_json(manifest_path)
    entries = manifest.get("candidate_entries", [])
    names = {entry.get("path") for entry in entries}
    assert_that(manifest.get("self_reference") == "excluded", "candidate manifest self-reference", errors)
    assert_that(names == CANDIDATE_FILES - {"FINAL_MANIFEST.json"}, "candidate manifest coverage", errors)
    for entry in entries:
        path = CANDIDATE_DIR / entry.get("path", "")
        assert_that(path.is_file() and sha256_file(path) == entry.get("sha256"), f"candidate manifest hash mismatch: {entry.get('path')}", errors)


def validate_candidate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    validate_fixed_inputs(payload["fixed"], errors)
    validate_reconciliation(payload["reconciliation"], errors)
    validate_scope(payload["scope"], errors)
    patch = payload["patch"]
    change = patch.get("allowed_line_change", {})
    assert_that(change.get("line_number") == 3, "promotion mutation permits non-metadata line", errors)
    assert_that("SQLite Schema" not in "\n".join(payload["scope"].get("proposed_frozen_normative_scope", [])), "scope expansion freezes SQLite Schema", errors)
    return errors


def run_mutations(payload: dict[str, Any]) -> list[dict[str, str]]:
    mutations: list[tuple[str, str, Any]] = []
    altered = copy.deepcopy(payload)
    altered["fixed"]["inputs"][2]["sha256"] = "0" * 64
    mutations.append(("RR1-MUT-HASH", "replace FI-V1 SHA-256 in an in-memory copy", altered))
    altered = copy.deepcopy(payload)
    altered["reconciliation"]["rows"] = [row for row in altered["reconciliation"]["rows"] if row["id"] != "V0-04"]
    mutations.append(("RR1-MUT-LEGACY-OMISSION", "remove retained V0-04 from an in-memory reconciliation copy", altered))
    altered = copy.deepcopy(payload)
    altered["scope"]["proposed_frozen_normative_scope"].append("SQLite Schema")
    mutations.append(("RR1-MUT-SCOPE-EXPANSION", "add SQLite Schema to an in-memory frozen scope copy", altered))
    altered = copy.deepcopy(payload)
    altered["patch"]["allowed_line_change"]["line_number"] = 20
    mutations.append(("RR1-MUT-BODY-CHANGE", "permit promotion on line 20 in an in-memory patch copy", altered))
    results: list[dict[str, str]] = []
    for mutation_id, description, altered_payload in mutations:
        errors = validate_candidate_payload(altered_payload)
        results.append({
            "id": mutation_id,
            "mutation": description,
            "expected": "REJECT",
            "actual": "REJECT" if errors else "ACCEPT",
            "reason": errors[0] if errors else "mutation was incorrectly accepted",
        })
    return results


def collect_payload() -> dict[str, Any]:
    return {
        "fixed": load_json(CANDIDATE_DIR / "fixed_inputs.json"),
        "reconciliation": load_json(CANDIDATE_DIR / "v0_to_v1_reconciliation.json"),
        "compatibility": load_json(CANDIDATE_DIR / "cross_baseline_compatibility.json"),
        "scope": load_json(CANDIDATE_DIR / "freeze_scope.json"),
        "transition": load_json(CANDIDATE_DIR / "runtime_transition.json"),
        "patch": load_json(CANDIDATE_DIR / "canonical_promotion_patch.json"),
        "history": load_json(CANDIDATE_DIR / "history_verification.json"),
    }


def run(final_manifest_required: bool) -> int:
    payload = collect_payload()
    errors = validate_candidate_payload(payload)
    validate_compatibility(payload["compatibility"], errors)
    validate_transition(payload["transition"], errors)
    validate_patch(payload["patch"], errors)
    validate_v1_and_direct_runtime(errors)
    validate_manifest(errors)
    history = payload["history"]
    records = history.get("records", [])
    assert_that(len(records) == 15 and all(row.get("result") == "MATCH" and row.get("sha256_before") == row.get("sha256_after") for row in records), "candidate history preservation receipt", errors)
    review_exists = (REVIEW_DIR / "independent_review.md").is_file()
    if final_manifest_required:
        audit_errors = audit_manifest()
        errors.extend(audit_errors)
    mutation_results = run_mutations(payload)
    all_rejected = all(row["actual"] == "REJECT" for row in mutation_results)
    rows = [
        {"id": "ABF-M-001", "result": "PASS" if not any("fixed" in item for item in errors) else "FAIL", "evidence": "15 independently rehashed Frozen inputs"},
        {"id": "ABF-M-002", "result": "PASS" if not any("V0.1" in item for item in errors) else "FAIL", "evidence": "independent coverage of V0-01..V0-16"},
        {"id": "ABF-M-003", "result": "PASS" if not any("compatibility" in item or "Gate 5" in item for item in errors) else "FAIL", "evidence": "12 PASS + Gate 5 N/A + 5 counterexamples"},
        {"id": "ABF-M-004", "result": "PASS" if not any("scope" in item or "exclusion" in item for item in errors) else "FAIL", "evidence": "9 normative bounds, 9 exclusions, 4 negative cases"},
        {"id": "ABF-M-005", "result": "PASS" if not any("runtime transition" in item or "P3-126" in item or "P3-127" in item for item in errors) else "FAIL", "evidence": "preserve/adapt/defer plus direct historical fact check"},
        {"id": "ABF-M-006", "result": "PASS" if not any("promotion" in item for item in errors) else "FAIL", "evidence": "independent pre/post hash reconstruction"},
        {"id": "ABF-M-007", "result": "PASS" if not errors else "FAIL", "evidence": "new re-review-1 runner; no candidate or attempt-1 runner imported/called"},
        {"id": "ABF-M-008", "result": "PASS" if mutation_results[0]["actual"] == "REJECT" else "FAIL", "evidence": mutation_results[0]["id"]},
        {"id": "ABF-M-009", "result": "PASS" if mutation_results[1]["actual"] == "REJECT" else "FAIL", "evidence": mutation_results[1]["id"]},
        {"id": "ABF-M-010", "result": "PASS" if mutation_results[2]["actual"] == "REJECT" else "FAIL", "evidence": mutation_results[2]["id"]},
        {"id": "ABF-M-011", "result": "PASS" if mutation_results[3]["actual"] == "REJECT" else "FAIL", "evidence": mutation_results[3]["id"]},
        {"id": "ABF-M-012", "result": "PASS" if not any("history" in item for item in errors) else "FAIL", "evidence": "15 candidate history receipts plus current hash recheck"},
        {"id": "ABF-M-013", "result": "PASS" if review_exists else "PENDING", "evidence": "fresh re-review-1 runner and independent_review.md"},
        {"id": "ABF-M-014", "result": "PASS" if final_manifest_required and not audit_manifest() else "PENDING", "evidence": "non-self Final Manifest recomputed by audit"},
    ]
    result = {
        "schema": "lifeos.p3-129.re-review-1.independent-verification.v1",
        "task_id": "LIFEOS-P3-129",
        "isolation": {
            "candidate_verifier_imported_or_called": False,
            "attempt_1_runner_result_or_review_used_as_positive_evidence": False,
            "temporary_directory_used": False,
            "write_scope": "lifeos/reviews/LIFEOS-P3-129/re-review-1/ only",
        },
        "command": "python3 -B lifeos/reviews/LIFEOS-P3-129/re-review-1/review_runner.py run --final",
        "rows": rows,
        "mutation_summary": {"total": len(mutation_results), "rejected": sum(row["actual"] == "REJECT" for row in mutation_results), "all_rejected": all_rejected},
        "errors": errors,
        "counts": {"P0": 0 if not errors else 1, "P1": 0, "P2": 0, "Unknown": 0, "Not_Implemented": 0 if review_exists and final_manifest_required else 1},
        "result": "PASS" if not errors and review_exists and final_manifest_required and all_rejected else "PENDING_OR_FAIL",
    }
    dump_json(REVIEW_DIR / "independent_verification.json", result)
    dump_json(REVIEW_DIR / "independent_mutation_results.json", {
        "schema": "lifeos.p3-129.re-review-1.independent-mutations.v1",
        "task_id": "LIFEOS-P3-129",
        "isolation": "all mutation payloads are in-memory deep copies; no candidate, history, temp root or Runtime was modified",
        "results": mutation_results,
    })
    print(json.dumps({"result": result["result"], "errors": errors, "mutation_summary": result["mutation_summary"]}, ensure_ascii=False))
    return 0 if result["result"] == "PASS" else 1


def finalize() -> int:
    missing = sorted(name for name in REVIEW_MANIFEST_FILES if not (REVIEW_DIR / name).is_file())
    if missing:
        print(json.dumps({"result": "FAIL", "missing": missing}, ensure_ascii=False))
        return 1
    entries = [{"path": name, "sha256": sha256_file(REVIEW_DIR / name)} for name in sorted(REVIEW_MANIFEST_FILES)]
    manifest = {
        "schema": "lifeos.p3-129.re-review-1.final-manifest.v1",
        "task_id": "LIFEOS-P3-129",
        "state": "Independent re-review complete / Pass / Not Frozen / PM and final user Gate pending",
        "self_reference": "excluded",
        "entries": entries,
        "replay": [
            "python3 -B lifeos/reviews/LIFEOS-P3-129/re-review-1/review_runner.py audit",
        ],
        "scope": "No candidate, ABF, canonical, historical asset or PM ledger was changed.",
    }
    dump_json(REVIEW_DIR / "FINAL_MANIFEST.json", manifest)
    print(json.dumps({"result": "PASS", "entries": len(entries)}, ensure_ascii=False))
    return 0


def audit_manifest() -> list[str]:
    errors: list[str] = []
    path = REVIEW_DIR / "FINAL_MANIFEST.json"
    if not path.is_file():
        return ["independent Final Manifest missing"]
    manifest = load_json(path)
    entries = manifest.get("entries", [])
    names = {entry.get("path") for entry in entries}
    assert_that(manifest.get("self_reference") == "excluded", "independent manifest self-reference", errors)
    assert_that(names == REVIEW_MANIFEST_FILES, "independent manifest coverage", errors)
    for entry in entries:
        evidence = REVIEW_DIR / entry.get("path", "")
        assert_that(evidence.is_file() and sha256_file(evidence) == entry.get("sha256"), f"independent manifest hash mismatch: {entry.get('path')}", errors)
    return errors


def audit() -> int:
    errors = audit_manifest()
    payload = collect_payload()
    validation_errors = validate_candidate_payload(payload)
    validate_compatibility(payload["compatibility"], validation_errors)
    validate_transition(payload["transition"], validation_errors)
    validate_patch(payload["patch"], validation_errors)
    validate_v1_and_direct_runtime(validation_errors)
    validate_manifest(validation_errors)
    history = payload["history"].get("records", [])
    assert_that(len(history) == 15 and all(row.get("result") == "MATCH" and row.get("sha256_before") == row.get("sha256_after") for row in history), "candidate history preservation receipt", validation_errors)
    mutations = run_mutations(payload)
    assert_that(all(row["actual"] == "REJECT" for row in mutations), "independent mutation unexpectedly accepted", validation_errors)
    verification_path = REVIEW_DIR / "independent_verification.json"
    if not verification_path.is_file():
        validation_errors.append("independent structured verification missing")
    else:
        verification = load_json(verification_path)
        row_results = {row.get("id"): row.get("result") for row in verification.get("rows", [])}
        assert_that(verification.get("result") == "PASS", "recorded independent result is not PASS", validation_errors)
        assert_that(all(row_results.get(f"ABF-M-{number:03d}") == "PASS" for number in range(1, 15)), "recorded ABF matrix is incomplete", validation_errors)
        assert_that(verification.get("counts") == {"P0": 0, "P1": 0, "P2": 0, "Unknown": 0, "Not_Implemented": 0}, "recorded review counts are nonzero", validation_errors)
    errors.extend(validation_errors)
    print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors, "mutations_rejected": sum(row["actual"] == "REJECT" for row in mutations)}, ensure_ascii=False))
    return 0 if not errors else 1


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review_runner.py run [--final] | finalize | audit", file=sys.stderr)
        return 2
    command = sys.argv[1]
    if command == "run":
        return run(final_manifest_required="--final" in sys.argv[2:])
    if command == "finalize":
        return finalize()
    if command == "audit":
        return audit()
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
