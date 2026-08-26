#!/usr/bin/env python3
"""Read-only verifier for the P3-129 architecture-freeze candidate.

It intentionally performs no product execution, network access, temporary-directory
creation, or file mutation. Mutation controls are in-memory copies of parsed JSON.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
V1_PATH = ROOT / "lifeos/architecture/LifeOS架构基线V1.0.md"
V1_SHA = "2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32"
REQUIRED_INPUT_IDS = {
    "FI-TASK", "FI-ABF", "FI-V1", "FI-FREEZE", "FI-P2-016", "FI-P2-016-REVIEW",
    "FI-P0-003", "FI-P0-009", "FI-P3-128", "FI-P3-128-REVIEW", "FI-GOVERNANCE",
    "FI-PM", "FI-ROLE", "FI-GATES", "FI-REVIEW-TEMPLATE",
}
REQUIRED_V0_IDS = {f"V0-{number:02d}" for number in range(1, 17)}
REQUIRED_TREATMENTS = {"preserve", "adapt", "defer"}
FORBIDDEN_SCOPE_TERMS = {
    "SQLite Schema", "IPC command signatures", "Tauri capability configuration",
    "production SLA", "Stage 4",
}


def load_json(name: str) -> dict:
    with (PACKAGE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate_fixed_inputs(fixed: dict, errors: list[str]) -> None:
    rows = fixed.get("inputs", [])
    by_id = {row.get("id"): row for row in rows}
    error(errors, set(by_id) == REQUIRED_INPUT_IDS, "fixed input IDs are missing or extra")
    for input_id in REQUIRED_INPUT_IDS:
        row = by_id.get(input_id)
        if not row:
            continue
        path = ROOT / row.get("path", "")
        error(errors, path.is_file(), f"{input_id} path is absent")
        if path.is_file():
            error(errors, sha256_path(path) == row.get("sha256"), f"{input_id} SHA-256 mismatch")
    error(errors, by_id.get("FI-V1", {}).get("sha256") == V1_SHA, "V1 canonical hash substitution")
    error(errors, sha256_path(V1_PATH) == V1_SHA, "V1 canonical bytes drifted")


def validate_reconciliation(reconciliation: dict, errors: list[str]) -> None:
    rows = reconciliation.get("rows", [])
    identifiers = [row.get("id") for row in rows]
    error(errors, set(identifiers) == REQUIRED_V0_IDS and len(identifiers) == len(REQUIRED_V0_IDS), "omitted or duplicate V0.1 norm row")
    allowed = {"retained", "changed", "superseded", "deferred"}
    for row in rows:
        error(errors, row.get("classification") in allowed, f"{row.get('id')} has invalid classification")
        error(errors, bool(row.get("v1_anchor")), f"{row.get('id')} has no V1 anchor")
        error(errors, bool(row.get("forward_rule")), f"{row.get('id')} has no forward rule")
    error(errors, reconciliation.get("unclassified_v0_norms") == [], "unclassified V0.1 norms")
    counts = reconciliation.get("classification_counts", {})
    actual = {kind: sum(1 for row in rows if row.get("classification") == kind) for kind in allowed}
    error(errors, counts == actual, "reconciliation classification counts disagree")


def validate_scope(scope: dict, errors: list[str]) -> None:
    frozen = scope.get("proposed_frozen_normative_scope", [])
    not_frozen = set(scope.get("explicitly_not_frozen", []))
    error(errors, len(frozen) >= 8, "freeze scope is incomplete")
    for term in FORBIDDEN_SCOPE_TERMS:
        error(errors, not any(term in item for item in frozen), f"scope expansion freezes {term}")
        error(errors, any(term in item for item in not_frozen), f"scope omission does not exclude {term}")
    error(errors, len(scope.get("negative_scope_cases", [])) >= 4, "scope negative cases missing")
    error(errors, all(case.get("expected") == "FAIL" for case in scope.get("negative_scope_cases", [])), "scope negative case is not fail-closed")


def validate_promotion(promotion: dict, errors: list[str]) -> None:
    change = promotion.get("allowed_line_change", {})
    before = "> 状态：Architecture Baseline Draft"
    expected_after = "> 状态：Architecture Baseline Frozen / V1.0 — supersedes V0.1 for forward technical architecture authority; V0.1 history and Evidence remain preserved."
    pre_bytes = V1_PATH.read_bytes()
    pre_text = pre_bytes.decode("utf-8")
    error(errors, promotion.get("state") == "Proposed only / not executed", "promotion is marked as executed")
    error(errors, promotion.get("pre_sha256") == V1_SHA, "promotion pre-hash mismatch")
    error(errors, change.get("line_number") == 3, "promotion allows a non-metadata line")
    error(errors, change.get("before") == before and change.get("after") == expected_after, "promotion replacement is not exact")
    error(errors, pre_text.count(before) == 1, "canonical preimage status line is not unique")
    lines = pre_text.splitlines(keepends=True)
    error(errors, len(lines) >= 3 and lines[2].rstrip("\r\n") == before, "canonical status is not the expected Draft line")
    proposed = pre_text.replace(before, expected_after, 1)
    proposed_lines = proposed.splitlines(keepends=True)
    changed_lines = [index + 1 for index, (old, new) in enumerate(zip(lines, proposed_lines)) if old != new]
    error(errors, changed_lines == [3], "promotion changes canonical body bytes")
    error(errors, promotion.get("post_sha256") == hashlib.sha256(proposed.encode("utf-8")).hexdigest(), "promotion post-hash mismatch")
    error(errors, "Architecture Baseline Draft" in pre_text, "canonical was promoted before final Gate")


def validate_compatibility(compatibility: dict, errors: list[str]) -> None:
    rows = compatibility.get("rows", [])
    result_by_id = {row.get("id"): row.get("result") for row in rows}
    for identifier in [f"CB-{number:02d}" for number in range(1, 14)]:
        error(errors, identifier in result_by_id, f"compatibility row {identifier} missing")
    error(errors, all(result_by_id.get(f"CB-{number:02d}") == "PASS" for number in range(1, 13)), "compatibility PASS row missing")
    error(errors, result_by_id.get("CB-13") == "N/A", "Gate 5 is not honestly marked N/A")
    summary = compatibility.get("summary", {})
    error(errors, summary == {"pass": 12, "na": 1, "fail": 0, "unresolved_conflict": 0}, "compatibility summary mismatch")
    error(errors, len(compatibility.get("counterexamples", [])) >= 5, "compatibility counterexamples missing")


def validate_transition(transition: dict, errors: list[str]) -> None:
    treatments = {row.get("treatment") for row in transition.get("rules", [])}
    error(errors, treatments == REQUIRED_TREATMENTS, "runtime transition omits preserve/adapt/defer")
    error(errors, len(transition.get("rules", [])) == 5, "runtime transition rows missing")
    text = json.dumps(transition, ensure_ascii=False)
    error(errors, "Not Frozen" in text and "three existing IPC" in text, "P3-126 treatment is incomplete")


def validate_manifest(errors: list[str]) -> None:
    manifest_path = PACKAGE / "FINAL_MANIFEST.json"
    error(errors, manifest_path.is_file(), "Final Manifest absent")
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("candidate_entries", [])
    entry_paths = {row.get("path") for row in entries}
    error(errors, "FINAL_MANIFEST.json" not in entry_paths, "Final Manifest is self-referential")
    required = {
        "README.md", "fixed_inputs.json", "v0_to_v1_reconciliation.json",
        "cross_baseline_compatibility.json", "freeze_scope.json", "runtime_transition.json",
        "canonical_promotion_patch.json", "verifier.py", "verification.json",
        "mutation_results.json", "history_verification.json",
    }
    error(errors, entry_paths == required, "Final Manifest does not cover the complete candidate package")
    for row in entries:
        path = PACKAGE / row.get("path", "")
        error(errors, path.is_file(), f"manifest candidate entry absent: {row.get('path')}")
        if path.is_file():
            error(errors, sha256_path(path) == row.get("sha256"), f"manifest candidate hash mismatch: {row.get('path')}")
    error(errors, manifest.get("self_reference") == "excluded", "Final Manifest self-reference declaration missing")


def validate_all(include_manifest: bool = True) -> list[str]:
    errors: list[str] = []
    fixed = load_json("fixed_inputs.json")
    reconciliation = load_json("v0_to_v1_reconciliation.json")
    compatibility = load_json("cross_baseline_compatibility.json")
    scope = load_json("freeze_scope.json")
    transition = load_json("runtime_transition.json")
    promotion = load_json("canonical_promotion_patch.json")
    validate_fixed_inputs(fixed, errors)
    validate_reconciliation(reconciliation, errors)
    validate_scope(scope, errors)
    validate_promotion(promotion, errors)
    validate_compatibility(compatibility, errors)
    validate_transition(transition, errors)
    if include_manifest:
        validate_manifest(errors)
    return errors


def mutation_results() -> list[dict[str, str]]:
    fixed = load_json("fixed_inputs.json")
    reconciliation = load_json("v0_to_v1_reconciliation.json")
    scope = load_json("freeze_scope.json")
    promotion = load_json("canonical_promotion_patch.json")
    controls: list[tuple[str, list[str]]] = []

    mutated_fixed = copy.deepcopy(fixed)
    next(row for row in mutated_fixed["inputs"] if row["id"] == "FI-V1")["sha256"] = "0" * 64
    errors: list[str] = []
    validate_fixed_inputs(mutated_fixed, errors)
    controls.append(("MUT-HASH", errors))

    mutated_reconciliation = copy.deepcopy(reconciliation)
    mutated_reconciliation["rows"] = [row for row in mutated_reconciliation["rows"] if row["id"] != "V0-04"]
    errors = []
    validate_reconciliation(mutated_reconciliation, errors)
    controls.append(("MUT-LEGACY-OMISSION", errors))

    mutated_scope = copy.deepcopy(scope)
    mutated_scope["proposed_frozen_normative_scope"].append("SQLite Schema")
    errors = []
    validate_scope(mutated_scope, errors)
    controls.append(("MUT-SCOPE-EXPANSION", errors))

    mutated_promotion = copy.deepcopy(promotion)
    mutated_promotion["allowed_line_change"]["line_number"] = 20
    errors = []
    validate_promotion(mutated_promotion, errors)
    controls.append(("MUT-BODY-CHANGE", errors))

    return [
        {"id": identifier, "expected": "REJECT", "actual": "REJECT" if result else "UNEXPECTED_PASS", "reason": result[0] if result else "no failure"}
        for identifier, result in controls
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify", "mutations"])
    parser.add_argument("--skip-manifest", action="store_true")
    args = parser.parse_args()
    if args.command == "verify":
        errors = validate_all(include_manifest=not args.skip_manifest)
        result = {"command": "verify", "status": "PASS" if not errors else "FAIL", "error_count": len(errors), "errors": errors}
    else:
        results = mutation_results()
        failed = [row for row in results if row["actual"] != "REJECT"]
        result = {"command": "mutations", "status": "PASS" if not failed else "FAIL", "total": len(results), "rejected": len(results) - len(failed), "results": results}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
