#!/usr/bin/env python3
"""Read-only verifier for LIFEOS-P3-114 Rework 1 frozen-row mapping."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[7]
ORIGINAL_EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-114/evidence"
REWORK_EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence"
ABF = ROOT / "lifeos/tasks/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review_acceptance_basis_freeze.md"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: pathlib.Path, with_bytes: bool) -> list[tuple[str, int | None, pathlib.Path]]:
    rows: list[tuple[str, int | None, pathlib.Path]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if with_bytes:
            match = re.match(r"^\| `([0-9a-f]{64})` \| (\d+) \| `([^`]+)` \|", line)
        else:
            match = re.match(r"^\| `([0-9a-f]{64})` \| `([^`]+)` \|", line)
        if not match:
            continue
        checksum = match.group(1)
        size = int(match.group(2)) if with_bytes else None
        rel = match.group(3) if with_bytes else match.group(2)
        target = ROOT / rel if rel.startswith("lifeos/") else path.parent / rel
        rows.append((checksum, size, target))
    return rows


def verify_manifest(path: pathlib.Path, with_bytes: bool) -> tuple[bool, list[dict[str, object]]]:
    rows = parse_manifest(path, with_bytes)
    results: list[dict[str, object]] = []
    for expected_hash, expected_bytes, target in rows:
        present = target.is_file()
        hash_match = present and sha256(target) == expected_hash
        byte_match = expected_bytes is None or (present and target.stat().st_size == expected_bytes)
        results.append({
            "path": str(target.relative_to(ROOT)),
            "hash_match": hash_match,
            "byte_match": byte_match,
        })
    return bool(rows) and all(row["hash_match"] and row["byte_match"] for row in results), results


def abf_rows() -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    for line in ABF.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ABF-M-"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        row_id = cells[1]
        rows[row_id] = {
            "frozen_action": cells[4],
            "test_id": cells[7],
            "abf_evidence": re.findall(r"`([^`]+)`", cells[8]),
        }
    return rows


def main() -> int:
    original_manifest = ORIGINAL_EVIDENCE / "MANIFEST.md"
    original_ok, original_rows = verify_manifest(original_manifest, with_bytes=True)
    original_manifest_hash = sha256(original_manifest)
    expected_original_manifest_hash = "89983ca8ab70698e90d8fff44ff9bdaf040107c310199d58a3e408c6cb0b16b3"

    initial_ok, initial_rows = verify_manifest(ROOT / "lifeos/reviews/LIFEOS-P3-113/evidence/MANIFEST.md", with_bytes=False)
    candidate_rework_ok, candidate_rework_rows = verify_manifest(ROOT / "lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/MANIFEST.md", with_bytes=True)

    matrix = json.loads((REWORK_EVIDENCE / "matrix_mapping.json").read_text(encoding="utf-8"))
    frozen = abf_rows()
    mapping_rows: list[dict[str, object]] = []
    for row in matrix["rows"]:
        row_id = row["row_id"]
        expected = frozen.get(row_id)
        actual_paths = [ROOT / item for item in row["actual_evidence"]]
        actions_match = expected is not None and row["frozen_action"] == expected["frozen_action"]
        test_match = expected is not None and row["test_id"] == expected["test_id"]
        declared_evidence_match = expected is not None and row["abf_evidence"] == expected["abf_evidence"]
        actual_evidence_match = [path.name for path in actual_paths] == row["abf_evidence"] and all(path.is_file() for path in actual_paths)
        mapping_rows.append({
            "row_id": row_id,
            "frozen_action_match": actions_match,
            "test_id_match": test_match,
            "abf_evidence_match": declared_evidence_match,
            "actual_evidence_match": actual_evidence_match,
        })

    authorization = json.loads((REWORK_EVIDENCE / "rework_authorization.json").read_text(encoding="utf-8"))
    auth_ok = (
        authorization["unchanged_basis"]["abf_sha256"] == sha256(ABF)
        and authorization["unchanged_basis"]["task_card_sha256"] == sha256(ROOT / "lifeos/tasks/LIFEOS-P3-114_p3_113_human_centered_dual_domain_product_rebaseline_fresh_isolated_independent_review.md")
        and authorization["authorization"]["pm_review_sha256"] == sha256(ROOT / "lifeos/reviews/LIFEOS-P3-114_pm_review.md")
    )
    temp_root_absent = not pathlib.Path("/private/tmp/lifeos-p3-114-product-review-v1").exists()
    mapping_ok = len(mapping_rows) == 13 and set(frozen) == {row["row_id"] for row in matrix["rows"]} and all(
        row["frozen_action_match"] and row["test_id_match"] and row["abf_evidence_match"] and row["actual_evidence_match"]
        for row in mapping_rows
    )
    results = json.loads((REWORK_EVIDENCE / "results.json").read_text(encoding="utf-8"))
    result_rows: list[dict[str, object]] = []
    for row in results["rows"]:
        expected = frozen.get(row["row_id"])
        evidence_paths = [ROOT / value if value.startswith("lifeos/") else REWORK_EVIDENCE / value for value in row["actual_evidence"]]
        actual_names = [path.name for path in evidence_paths]
        expected_names = expected["abf_evidence"] if expected else []
        result_rows.append({
            "row_id": row["row_id"],
            "frozen_action_match": expected is not None and row["frozen_action"] == expected["frozen_action"],
            "test_id_match": expected is not None and row["test_id"] == expected["test_id"],
            "required_evidence_prefix_match": actual_names[:len(expected_names)] == expected_names,
            "actual_evidence_exists": all(path.is_file() for path in evidence_paths),
            "result_is_pass": row["result"] == "PASS",
        })
    results_ok = len(result_rows) == 13 and set(frozen) == {row["row_id"] for row in results["rows"]} and all(
        row["frozen_action_match"] and row["test_id_match"] and row["required_evidence_prefix_match"] and row["actual_evidence_exists"] and row["result_is_pass"]
        for row in result_rows
    )
    passed = all([original_ok, original_manifest_hash == expected_original_manifest_hash, initial_ok, candidate_rework_ok, auth_ok, temp_root_absent, mapping_ok, results_ok])
    output = {
        "runner": "verify_rework_mapping.py",
        "mode": "read-only hashes, bytes and frozen-row mapping; no application, database, model, network, external or real-data access",
        "original_p3_114_manifest": {"entries": len(original_rows), "all_match": original_ok, "self_hash_match": original_manifest_hash == expected_original_manifest_hash},
        "p3_113_initial_manifest": {"entries": len(initial_rows), "all_match": initial_ok},
        "p3_113_rework_manifest": {"entries": len(candidate_rework_rows), "all_match": candidate_rework_ok},
        "authorization_and_abf_unchanged": auth_ok,
        "temporary_root_absent": temp_root_absent,
        "frozen_matrix_rows": mapping_rows,
        "results_rows": result_rows,
        "passed": passed,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
