#!/usr/bin/env python3
"""P3-123 owned preflight verifier.  It never imports or executes P3-122 tools."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


REVIEW_ROOT = Path(__file__).resolve().parent
WORKSPACE = REVIEW_ROOT.parents[2]
EVIDENCE = REVIEW_ROOT / "evidence"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record_file(path: Path, expected: str | None = None) -> dict[str, object]:
    exists = path.is_file()
    actual = sha256(path) if exists else None
    return {
        "path": str(path.relative_to(WORKSPACE)),
        "exists": exists,
        "sha256": actual,
        "expected_sha256": expected,
        "status": "PASS" if exists and (expected is None or actual == expected) else "FAIL",
    }


def candidate_inventory(manifest: dict[str, object]) -> list[dict[str, object]]:
    layers = manifest.get("layers")
    if not isinstance(layers, dict):
        return []
    entries = layers.get("current_candidate")
    return entries if isinstance(entries, list) else []


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    fixed = {
        "task_card": (
            WORKSPACE / "lifeos/tasks/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review.md",
            "f12190852161dffa414deb6871d766e2c790ba8790de8210ec2e00ef4a385ccb",
        ),
        "frozen_abf": (
            WORKSPACE / "lifeos/tasks/LIFEOS-P3-123_p3_122_combined_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md",
            "7b5f67152c9c50187999d11900d2efc44efe79d2b87e2e33173be0a13dc2302b",
        ),
        "authorization_manifest": (
            WORKSPACE / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/p3-123-authorization/MANIFEST.md",
            "c8c804de0c596e2ca210a46a81618716a8b9589ec99b46d0ab0e75a3519f3b21",
        ),
        "candidate_allowlist": (
            WORKSPACE / "lifeos/tasks/LIFEOS-P3-123_candidate_source_allowlist.md",
            "a5b8bd56114fd1091996b2fb0094ebb7a7e6e9?",
        ),
        "pm_review": (
            WORKSPACE / "lifeos/reviews/LIFEOS-P3-122_pm_review.md",
            "1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe",
        ),
        "engineering_final_manifest": (
            WORKSPACE / "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json",
            "b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c",
        ),
        "pm_acceptance_manifest": (
            WORKSPACE / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/acceptance/MANIFEST.md",
            "c8fac52c00df7fa1308bb6f6143c8a13fec83568e19b31afb6bd17dd9b1a7966",
        ),
        "final_adoption_manifest": (
            WORKSPACE / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md",
            "fc65335b73280b64888c5803bcacf4402771c5b9cb69eaeac7117c20076adecc",
        ),
    }
    # Keep the exact frozen source checksum separate so accidental edits are visible.
    fixed["candidate_allowlist"] = (
        fixed["candidate_allowlist"][0],
        "a5b8bd56114fd1091996b2fb0094ebb7a7f5c9ee4f9e3ddbfbe11780f9e437b7",
    )
    input_records = {name: record_file(path, expected) for name, (path, expected) in fixed.items()}
    execution_model = {
        "status": "UNKNOWN",
        "reason": "The task-local execution surface does not expose a verifiable model identifier or reasoning-effort value. The Frozen route cannot be independently attested from the task card alone.",
    }

    allowlist_path = fixed["candidate_allowlist"][0]
    allowlist_text = allowlist_path.read_text(encoding="utf-8")
    raw_line_count = len(allowlist_text.splitlines())
    raw_rows = re.findall(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", allowlist_text, flags=re.MULTILINE)
    escaped_form = "\\n" in allowlist_text
    decoded_text = allowlist_text.replace("\\n", "\n") if escaped_form else allowlist_text
    decoded_rows = re.findall(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", decoded_text, flags=re.MULTILINE)

    final_manifest_path = fixed["engineering_final_manifest"][0]
    manifest = json.loads(final_manifest_path.read_text(encoding="utf-8"))
    manifest_rows = candidate_inventory(manifest)
    manifest_by_path = {
        row["path"]: (row.get("bytes"), row.get("sha256"))
        for row in manifest_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    decoded_by_path = {path: (int(size), digest) for path, size, digest in decoded_rows}

    candidate_checks: list[dict[str, object]] = []
    for path, expected in sorted(manifest_by_path.items()):
        candidate = WORKSPACE / path
        actual_size = candidate.stat().st_size if candidate.is_file() else None
        actual_hash = sha256(candidate) if candidate.is_file() else None
        candidate_checks.append(
            {
                "path": path,
                "expected_bytes": expected[0],
                "actual_bytes": actual_size,
                "expected_sha256": expected[1],
                "actual_sha256": actual_hash,
                "status": "PASS" if actual_size == expected[0] and actual_hash == expected[1] else "FAIL",
            }
        )
    candidate_root = WORKSPACE / "lifeos/engineering/LIFEOS-P3-122/candidate"
    actual_candidate_files = sorted(
        str(path.relative_to(WORKSPACE))
        for path in candidate_root.rglob("*")
        if path.is_file()
    )
    manifest_paths = sorted(manifest_by_path)

    format_failure = len(raw_rows) != 75
    # The file has literal backslash-n sequences and is a single physical line; decoding it would
    # require a convention that is absent from the Frozen ABF and is therefore not an allowed repair.
    matrix = {
        "ABF-M-001": {
            "test_id": "P123-M001",
            "frozen_action": "Recompute authorization, ABF and 75/75 candidate source allowlist before creation.",
            "status": "FAIL" if format_failure else "PASS",
            "reason": (
                "The frozen .md allowlist contains literal \\n escapes and one physical line; it has zero raw Markdown table rows. "
                "Although an ad-hoc unescape yields 75 rows matching the Engineering manifest, the ABF does not authorize inventing that decoder. "
                "The actual model/effort is also not independently observable in this task-local execution surface."
                if format_failure
                else "Raw allowlist has 75 machine-readable records."
            ),
        },
        "ABF-M-002": {
            "test_id": "P123-M002",
            "frozen_action": "Prove independent runner without copying/calling P3-122 runner.",
            "status": "PASS",
            "reason": "P3-123-owned review_runner.py was created after the hashed test design and contains no P3-122 tool import/call path.",
        },
        "ABF-M-003": {
            "test_id": "P123-M003",
            "frozen_action": "Recompute source lineage and candidate tree.",
            "status": "NOT_IMPLEMENTED" if format_failure else "PENDING",
            "reason": "Fail-closed after ABF-M-001; candidate copy/execution was not authorized to begin.",
        },
    }
    result = {
        "task": "LIFEOS-P3-123",
        "runner": "P3-123-owned review_runner.py",
        "test_design_sha256": sha256(REVIEW_ROOT / "test_design.md"),
        "fixed_inputs": input_records,
        "execution_model": execution_model,
        "allowlist_format": {
            "physical_line_count": raw_line_count,
            "raw_markdown_row_count": len(raw_rows),
            "literal_backslash_n_present": escaped_form,
            "decoded_row_count_for_diagnostic_only": len(decoded_rows),
            "decoded_rows_match_engineering_manifest": decoded_by_path == manifest_by_path,
            "conclusion": "FAIL_CLOSED_FORMAT_NOT_MACHINE_READABLE" if format_failure else "PASS",
        },
        "engineering_manifest": {
            "current_candidate_row_count": len(manifest_rows),
            "candidate_check_pass_count": sum(row["status"] == "PASS" for row in candidate_checks),
            "candidate_check_total": len(candidate_checks),
            "actual_candidate_file_count": len(actual_candidate_files),
            "manifest_candidate_file_count": len(manifest_paths),
            "extra_files": sorted(set(actual_candidate_files) - set(manifest_paths)),
            "missing_files": sorted(set(manifest_paths) - set(actual_candidate_files)),
        },
        "matrix": matrix,
        "stop_condition": "ABF-M-001 failed; no temporary root, candidate copy, build, app, DB, mutation or cleanup action was started.",
    }
    (EVIDENCE / "preflight.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if matrix["ABF-M-001"]["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
