#!/usr/bin/env python3
"""Independent, static-only review verifier for LIFEOS-P3-129.

This file deliberately does not import, execute, or copy the candidate verifier.
It uses only Python's standard library and in-memory mutation copies.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "lifeos/architecture/LIFEOS-P3-129"
OUTPUT = Path(__file__).resolve().parent / "independent_verification.json"
REVIEW_MANIFEST = Path(__file__).resolve().parent / "FINAL_MANIFEST.json"
ABF = ROOT / "lifeos/tasks/LIFEOS-P3-129_architecture_v1_authority_rebaseline_and_freeze_closure_acceptance_basis_freeze.md"
V1 = ROOT / "lifeos/architecture/LifeOS架构基线V1.0.md"
FREEZE_STATUS = ROOT / "lifeos/FREEZE_STATUS.md"

EXPECTED_ABF_HASH = "df3c4e9879a624e05ef8f7eb5b71d1a5835422db0eea278e2fc88404032b40fb"
EXPECTED_V1_HASH = "2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32"
EXPECTED_POST_HASH = "1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236"

EXPECTED_FIXED_IDS = {
    "FI-TASK",
    "FI-ABF",
    "FI-V1",
    "FI-FREEZE",
    "FI-P2-016",
    "FI-P2-016-REVIEW",
    "FI-P0-003",
    "FI-P0-009",
    "FI-P3-128",
    "FI-P3-128-REVIEW",
    "FI-GOVERNANCE",
    "FI-PM",
    "FI-ROLE",
    "FI-GATES",
    "FI-REVIEW-TEMPLATE",
}

EXPECTED_ABF_HISTORY_HASHES = {
    "FI-V1": EXPECTED_V1_HASH,
    "FI-FREEZE": "3d32e56876175636c00cf36b26e18bc284ff3d13123e291bce9f28f9e8f74a10",
    "FI-P2-016": "3ab2cece5252c7d982683d1a1cae9c9106f6fa707e6a308e86d27667e4aff8fa",
    "FI-P2-016-REVIEW": "348b038cb01bde3eea27605d04c714c153ecb798131281dc08f2e859eb86152b",
    "FI-P0-003": "e7c0b03ba0b9844cc9b515eaf42f88a844502e0ad3481ee01dff88e001d3cf29",
    "FI-P0-009": "1c6759df1da2f9a95d6b1072c157eda023b9a985439290599dfae19577f90305",
    "FI-P3-128": "c385beb8267724945c7665f7a419e1358b5f1571a389055d7642fb660fca1a6b",
    "FI-P3-128-REVIEW": "490ad63606597724465f594c63a49f2d370a9a8aebd236ad1f0ec819cda3dab3",
}

JSON_FILES = {
    "fixed": "fixed_inputs.json",
    "reconciliation": "v0_to_v1_reconciliation.json",
    "compatibility": "cross_baseline_compatibility.json",
    "scope": "freeze_scope.json",
    "transition": "runtime_transition.json",
    "promotion": "canonical_promotion_patch.json",
    "history": "history_verification.json",
    "manifest": "FINAL_MANIFEST.json",
    "candidate_verification": "verification.json",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(name: str) -> dict[str, Any]:
    return json.loads((CANDIDATE / JSON_FILES[name]).read_text(encoding="utf-8"))


def reject_if(condition: bool, reason: str, errors: list[str]) -> None:
    if condition:
        errors.append(reason)


def validate_fixed(fixed: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = fixed.get("inputs", [])
    by_id = {row.get("id"): row for row in rows}
    reject_if(len(rows) != 15, "fixed-input count is not 15", errors)
    reject_if(set(by_id) != EXPECTED_FIXED_IDS, "fixed-input IDs differ from independent contract", errors)
    for item_id, row in by_id.items():
        path = ROOT / row.get("path", "")
        reject_if(not path.is_file(), f"{item_id} path is missing", errors)
        if path.is_file():
            reject_if(sha256_file(path) != row.get("sha256"), f"{item_id} SHA-256 mismatch", errors)
    for item_id, expected_hash in EXPECTED_ABF_HISTORY_HASHES.items():
        reject_if(by_id.get(item_id, {}).get("sha256") != expected_hash, f"{item_id} conflicts with ABF history hash", errors)
    reject_if(by_id.get("FI-ABF", {}).get("sha256") != EXPECTED_ABF_HASH, "FI-ABF hash differs from frozen ABF", errors)
    return errors


def validate_reconciliation(reconciliation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = reconciliation.get("rows", [])
    ids = [row.get("id") for row in rows]
    classifications = {row.get("id"): row.get("classification") for row in rows}
    reject_if(ids != [f"V0-{number:02d}" for number in range(1, 17)], "V0.1 reconciliation rows are incomplete or reordered", errors)
    reject_if(reconciliation.get("unclassified_v0_norms") != [], "unclassified V0.1 norm remains", errors)
    reject_if(reconciliation.get("classification_counts") != {"retained": 13, "changed": 1, "superseded": 1, "deferred": 1}, "V0.1 classification counts differ", errors)
    reject_if(classifications.get("V0-04") != "retained", "outbox/job safety norm is not retained", errors)
    reject_if(classifications.get("V0-14") != "changed", "target layering change is not explicit", errors)
    reject_if(classifications.get("V0-15") != "deferred", "future implementation products are not deferred", errors)
    reject_if(classifications.get("V0-16") != "superseded", "V0.1 forward-authority treatment is not explicit", errors)
    return errors


def validate_compatibility(compatibility: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = compatibility.get("rows", [])
    results = {row.get("id"): row.get("result") for row in rows}
    reject_if(compatibility.get("candidate_v1_sha256") != EXPECTED_V1_HASH, "compatibility uses an unexpected V1 canonical", errors)
    reject_if(len(rows) != 13, "compatibility row count is not 13", errors)
    reject_if([results.get(f"CB-{number:02d}") for number in range(1, 13)] != ["PASS"] * 12, "Gate 1-4 compatibility rows are not all PASS", errors)
    reject_if(results.get("CB-13") != "N/A", "Gate 5 is not honestly N/A", errors)
    reject_if(compatibility.get("summary") != {"pass": 12, "na": 1, "fail": 0, "unresolved_conflict": 0}, "compatibility summary differs", errors)
    reject_if(len(compatibility.get("counterexamples", [])) < 5, "fewer than five compatibility counterexamples", errors)
    return errors


def validate_scope(scope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    normative = "\n".join(scope.get("proposed_frozen_normative_scope", [])).lower()
    excluded = "\n".join(scope.get("explicitly_not_frozen", [])).lower()
    reject_if("freeze candidate" not in scope.get("state_before_final_user_gate", "").lower(), "scope claims a final frozen state", errors)
    for required in ("modular monolith", "orchestrator", "model and agent", "sqlite", "fts-first", "authorization"):
        reject_if(required not in normative, f"missing proposed frozen norm: {required}", errors)
    for forbidden in ("schema", "ipc", "capability", "pragma", "provider", "stage 4"):
        reject_if(forbidden not in excluded, f"missing explicit exclusion: {forbidden}", errors)
    reject_if("sqlite schema" in normative or "ipc command signatures" in normative, "scope expands to implementation detail", errors)
    reject_if(len(scope.get("negative_scope_cases", [])) < 4, "scope negative cases are incomplete", errors)
    return errors


def validate_transition(transition: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = transition.get("rules", [])
    treatments = {row.get("id"): row.get("treatment") for row in rows}
    reject_if(treatments != {"RT-01": "preserve", "RT-02": "preserve", "RT-03": "adapt", "RT-04": "adapt", "RT-05": "defer"}, "runtime transition preserve/adapt/defer coverage differs", errors)
    text = json.dumps(transition, ensure_ascii=False).lower()
    for required in ("not freeze product runtime", "ipc signatures", "new explicit authorization", "real data/files/vault/export/network/model/agent"):
        reject_if(required not in text, f"runtime transition lacks boundary: {required}", errors)
    return errors


def validate_promotion(promotion: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lines = V1.read_text(encoding="utf-8").splitlines(keepends=True)
    allowed = promotion.get("allowed_line_change", {})
    reject_if(sha256_file(V1) != EXPECTED_V1_HASH, "current canonical preimage differs from frozen V1 hash", errors)
    reject_if(lines[2].rstrip("\n") != allowed.get("before"), "canonical status preimage does not match patch", errors)
    reject_if(allowed.get("line_number") != 3, "promotion patch permits a non-status line", errors)
    replacement = allowed.get("after", "") + ("\n" if lines[2].endswith("\n") else "")
    post_lines = list(lines)
    post_lines[2] = replacement
    reject_if(sha256_bytes("".join(post_lines).encode("utf-8")) != EXPECTED_POST_HASH, "independently computed promotion post-hash differs", errors)
    reject_if(promotion.get("post_sha256") != EXPECTED_POST_HASH, "promotion receipt post-hash differs", errors)
    reject_if(promotion.get("state") != "Proposed only / not executed", "promotion is not declared proposed-only", errors)
    return errors


def validate_history(fixed: dict[str, Any], history: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixed_by_id = {row["id"]: row["sha256"] for row in fixed.get("inputs", [])}
    rows = history.get("records", [])
    reject_if(len(rows) != 15, "history verification does not cover 15 fixed inputs", errors)
    for row in rows:
        item_id = row.get("id")
        expected = fixed_by_id.get(item_id)
        reject_if(row.get("sha256_before") != expected or row.get("sha256_after") != expected, f"history hash mismatch for {item_id}", errors)
        reject_if(row.get("result") != "MATCH", f"history result is not MATCH for {item_id}", errors)
    reject_if(history.get("summary", {}).get("canonical_promotion_executed") is not False, "history claims promotion executed", errors)
    return errors


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = manifest.get("candidate_entries", [])
    names = {entry.get("path") for entry in entries}
    actual_names = {path.name for path in CANDIDATE.iterdir() if path.is_file()} - {"FINAL_MANIFEST.json"}
    reject_if(manifest.get("self_reference") != "excluded", "candidate Final Manifest is self-referential", errors)
    reject_if("FINAL_MANIFEST.json" in names, "candidate Final Manifest inventories itself", errors)
    reject_if(names != actual_names, "candidate Final Manifest inventory does not equal candidate files excluding itself", errors)
    for entry in entries:
        path = CANDIDATE / entry["path"]
        reject_if(not path.is_file() or sha256_file(path) != entry.get("sha256"), f"candidate Manifest mismatch: {entry.get('path')}", errors)
    return errors


def validate_candidate_state(candidate_verification: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = {row.get("id"): row.get("result") for row in candidate_verification.get("candidate_side_rows", [])}
    for number in range(1, 13):
        reject_if(rows.get(f"ABF-M-{number:03d}") != "PASS", f"candidate ABF-M-{number:03d} is not PASS", errors)
    reject_if(rows.get("ABF-M-013") != "PENDING_MANDATORY_INDEPENDENT_REVIEW", "candidate misstates independent-review status", errors)
    reject_if(rows.get("ABF-M-014") != "PENDING_GATE_CLOSURE", "candidate misstates final-gate status", errors)
    status_text = V1.read_text(encoding="utf-8") + FREEZE_STATUS.read_text(encoding="utf-8")
    reject_if("> 状态：Architecture Baseline Draft" not in status_text, "canonical Draft status was altered before final Gate", errors)
    reject_if("Replacement Direction Confirmed / Gate Pending / Not Frozen" not in status_text, "FREEZE_STATUS promotion guard is absent", errors)
    return errors


def validate_review_manifest() -> list[str]:
    errors: list[str] = []
    if not REVIEW_MANIFEST.is_file():
        return ["independent review Final Manifest is missing"]
    manifest = json.loads(REVIEW_MANIFEST.read_text(encoding="utf-8"))
    expected = {
        "independent_review_plan.md",
        "independent_verifier.py",
        "independent_verification.json",
        "independent_review.md",
        "execution_exception.json",
    }
    entries = manifest.get("review_entries", [])
    names = {entry.get("path") for entry in entries}
    reject_if(manifest.get("self_reference") != "excluded", "independent Final Manifest is self-referential", errors)
    reject_if("FINAL_MANIFEST.json" in names, "independent Final Manifest inventories itself", errors)
    reject_if(names != expected, "independent Final Manifest inventory differs from review-owned files", errors)
    for entry in entries:
        path = REVIEW_MANIFEST.parent / entry.get("path", "")
        reject_if(not path.is_file() or sha256_file(path) != entry.get("sha256"), f"independent Manifest mismatch: {entry.get('path')}", errors)
    return errors


def model_errors(models: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_fixed(models["fixed"]))
    errors.extend(validate_reconciliation(models["reconciliation"]))
    errors.extend(validate_scope(models["scope"]))
    allowed_line = models["promotion"].get("allowed_line_change", {}).get("line_number")
    reject_if(allowed_line != 3, "promotion allows a non-metadata line", errors)
    return errors


def run_mutations(models: dict[str, Any]) -> list[dict[str, str]]:
    cases: list[tuple[str, str, Any]] = [
        ("MUT-HASH", "replace FI-V1 SHA-256 in an in-memory fixed-input copy", lambda m: next(row for row in m["fixed"]["inputs"] if row["id"] == "FI-V1").update({"sha256": "0" * 64})),
        ("MUT-LEGACY-OMISSION", "remove V0-04 from an in-memory reconciliation copy", lambda m: m["reconciliation"].update({"rows": [row for row in m["reconciliation"]["rows"] if row["id"] != "V0-04"]})),
        ("MUT-SCOPE-EXPANSION", "add SQLite Schema to in-memory proposed frozen scope", lambda m: m["scope"]["proposed_frozen_normative_scope"].append("SQLite Schema is Frozen")),
        ("MUT-BODY-CHANGE", "allow line 4 rather than line 3 in in-memory promotion patch", lambda m: m["promotion"]["allowed_line_change"].update({"line_number": 4})),
    ]
    results: list[dict[str, str]] = []
    for case_id, mutation, mutate in cases:
        disposable = copy.deepcopy(models)
        mutate(disposable)
        errors = model_errors(disposable)
        results.append({
            "id": case_id,
            "mutation": mutation,
            "expected": "REJECT",
            "actual": "REJECT" if errors else "ACCEPT",
            "reason": errors[0] if errors else "mutation was incorrectly accepted",
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write independent_verification.json in this review directory")
    parser.add_argument("--verify-review-manifest", action="store_true", help="also verify the independent review's non-self Final Manifest")
    args = parser.parse_args()
    if args.verify_review_manifest:
        manifest_errors = validate_review_manifest()
        if manifest_errors:
            print(json.dumps({"review_manifest_result": "FAIL", "errors": manifest_errors}, ensure_ascii=False, indent=2))
            return 1
    models = {name: load_json(name) for name in JSON_FILES}
    checks = {
        "ABF-M-001": validate_fixed(models["fixed"]),
        "ABF-M-002": validate_reconciliation(models["reconciliation"]),
        "ABF-M-003": validate_compatibility(models["compatibility"]),
        "ABF-M-004": validate_scope(models["scope"]),
        "ABF-M-005": validate_transition(models["transition"]),
        "ABF-M-006": validate_promotion(models["promotion"]),
        "ABF-M-007": model_errors(models),
        "ABF-M-012": validate_history(models["fixed"], models["history"]),
        "ABF-M-013": ["review session made an unauthorized temporary stdout write; see execution_exception.json"],
        "INDEPENDENT-MANIFEST": validate_manifest(models["manifest"]),
        "STATE-GUARD": validate_candidate_state(models["candidate_verification"]),
    }
    mutations = run_mutations(models)
    for mutation in mutations:
        checks[mutation["id"]] = [] if mutation["actual"] == "REJECT" else [mutation["reason"]]
    independent_checks = []
    for item_id, errors in checks.items():
        independent_checks.append({"id": item_id, "result": "PASS" if not errors else "FAIL", "errors": errors})
    pristine_errors = [error for item in independent_checks if item["id"] not in {"ABF-M-013"} for error in item["errors"]]
    abf_matrix = [
        {"id": "ABF-M-001", "result": "PASS" if not checks["ABF-M-001"] else "FAIL", "evidence": "independent fixed-input recomputation"},
        {"id": "ABF-M-002", "result": "PASS" if not checks["ABF-M-002"] else "FAIL", "evidence": "independent 16-row V0.1 reconciliation check"},
        {"id": "ABF-M-003", "result": "PASS" if not checks["ABF-M-003"] else "FAIL", "evidence": "independent compatibility and Gate 1-5 check"},
        {"id": "ABF-M-004", "result": "PASS" if not checks["ABF-M-004"] else "FAIL", "evidence": "independent normative/exclusion scope check"},
        {"id": "ABF-M-005", "result": "PASS" if not checks["ABF-M-005"] else "FAIL", "evidence": "independent preserve/adapt/defer check"},
        {"id": "ABF-M-006", "result": "PASS" if not checks["ABF-M-006"] else "FAIL", "evidence": "independent byte-level promotion construction"},
        {"id": "ABF-M-007", "result": "PASS" if not checks["ABF-M-007"] else "FAIL", "evidence": "independent pristine verifier"},
        {"id": "ABF-M-008", "result": "PASS" if not checks["MUT-HASH"] else "FAIL", "evidence": "MUT-HASH"},
        {"id": "ABF-M-009", "result": "PASS" if not checks["MUT-LEGACY-OMISSION"] else "FAIL", "evidence": "MUT-LEGACY-OMISSION"},
        {"id": "ABF-M-010", "result": "PASS" if not checks["MUT-SCOPE-EXPANSION"] else "FAIL", "evidence": "MUT-SCOPE-EXPANSION"},
        {"id": "ABF-M-011", "result": "PASS" if not checks["MUT-BODY-CHANGE"] else "FAIL", "evidence": "MUT-BODY-CHANGE"},
        {"id": "ABF-M-012", "result": "PASS" if not checks["ABF-M-012"] else "FAIL", "evidence": "independent before/after history hash check"},
        {"id": "ABF-M-013", "result": "NOT_PASS_UNAUTHORIZED_TEMP_WRITE", "evidence": "execution_exception.json; a new fresh isolated review is required"},
        {"id": "ABF-M-014", "result": "PENDING_PM_GATE_CLOSURE", "evidence": "PM must combine candidate and this review, then obtain final user Gate confirmation"},
    ]
    payload: dict[str, Any] = {
        "schema": "lifeos.p3-129.independent-verification.v1",
        "task_id": "LIFEOS-P3-129",
        "independence": {
            "candidate_verifier_imported": False,
            "candidate_verifier_executed": False,
            "mutation_mode": "in-memory only",
            "temporary_directory_used": False,
            "write_scope_deviation": True,
            "temporary_stdout_file_cleanup": "completed; the deviation remains disqualifying for ABF-M-013",
        },
        "command": "python3 -B lifeos/reviews/LIFEOS-P3-129/independent_verifier.py --write",
        "fixed_contract": {
            "abf_sha256": sha256_file(ABF),
            "canonical_v1_pre_sha256": sha256_file(V1),
            "candidate_final_manifest_sha256": sha256_file(CANDIDATE / "FINAL_MANIFEST.json"),
        },
        "independent_checks": independent_checks,
        "abf_matrix": abf_matrix,
        "mutations": mutations,
        "result": "STATIC_CANDIDATE_CHECK_PASS_REVIEW_INVALID" if not pristine_errors else "STATIC_CANDIDATE_CHECK_FAIL_REVIEW_INVALID",
        "review_finding_counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 1},
        "gate_status_after_independent_review": "ABF-M-013 NOT PASS due to unauthorized temporary write; ABF-M-014 remains unimplemented; V1.0 remains Draft / Not Frozen",
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not pristine_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
