#!/usr/bin/env python3
"""Read-only SHA-256 and JSON validation for the P3-113 candidate package."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[5]
REWORK_ROOT = ROOT / "lifeos/reviews/LIFEOS-P3-113/evidence/rework-1"
INITIAL_ROOT = ROOT / "lifeos/reviews/LIFEOS-P3-113/evidence"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: pathlib.Path, has_bytes: bool) -> list[tuple[str, int | None, pathlib.Path]]:
    rows: list[tuple[str, int | None, pathlib.Path]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if has_bytes:
            match = re.match(r"^\| `([0-9a-f]{64})` \| (\d+) \| `([^`]+)` \|", line)
        else:
            match = re.match(r"^\| `([0-9a-f]{64})` \| `([^`]+)` \|", line)
        if not match:
            continue
        expected_hash = match.group(1)
        expected_size = int(match.group(2)) if has_bytes else None
        rel = match.group(3) if has_bytes else match.group(2)
        candidate = ROOT / rel if rel.startswith("lifeos/") else path.parent / rel
        rows.append((expected_hash, expected_size, candidate))
    return rows


def verify_rows(rows: list[tuple[str, int | None, pathlib.Path]]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for expected_hash, expected_size, path in rows:
        actual_hash = digest(path) if path.is_file() else None
        actual_size = path.stat().st_size if path.is_file() else None
        results.append({
            "path": str(path.relative_to(ROOT)),
            "hash_match": actual_hash == expected_hash,
            "byte_match": expected_size is None or actual_size == expected_size,
        })
    return results


def main() -> int:
    initial_manifest = INITIAL_ROOT / "MANIFEST.md"
    rework_manifest = REWORK_ROOT / "MANIFEST.md"
    initial_results = verify_rows(parse_manifest(initial_manifest, has_bytes=False))
    rework_results = verify_rows(parse_manifest(rework_manifest, has_bytes=True))
    json_files = sorted(REWORK_ROOT.glob("*.json"))
    json_status = []
    for path in json_files:
        parsed = json.loads(path.read_text(encoding="utf-8"))
        json_status.append({"path": str(path.relative_to(ROOT)), "status": parsed.get("status")})

    current_pm_review = ROOT / "lifeos/reviews/LIFEOS-P3-113_pm_review.md"
    pm_evidence_manifest = ROOT / "lifeos/reviews/LIFEOS-P3-113/pm_evidence/rework-1/MANIFEST.md"
    current_pm_hash = digest(current_pm_review)
    pm_manifest_text = pm_evidence_manifest.read_text(encoding="utf-8")
    historical_pm_hash = "84fb8a698030b73fdc95b50bcaf354dc558975940c7cbe909746955f360292fd"
    adopted_pm_hash = "fc387595ec31db54aaa58daf293c18e1602365f23c2f8a210d924b98f4ec1512"
    post_adoption_followup = (
        current_pm_hash == adopted_pm_hash
        and historical_pm_hash in pm_manifest_text
        and current_pm_hash != historical_pm_hash
    )

    all_candidate_hashes = all(row["hash_match"] and row["byte_match"] for row in initial_results + rework_results)
    all_json_pass = len(json_status) == 10 and all(row["status"] == "PASS" for row in json_status)
    output = {
        "runner": "verify_candidate_integrity.py",
        "mode": "read-only hash/byte/JSON inspection; no app, database, model, network or real-data access",
        "initial_manifest": {"count": len(initial_results), "all_match": all(row["hash_match"] for row in initial_results), "rows": initial_results},
        "rework_manifest": {"count": len(rework_results), "all_match": all(row["hash_match"] and row["byte_match"] for row in rework_results), "rows": rework_results},
        "rework_json": {"count": len(json_status), "all_status_pass": all_json_pass, "rows": json_status},
        "post_adoption_pm_followup": {
            "current_pm_review_sha256": current_pm_hash,
            "historical_pm_evidence_manifest_references_sha256": historical_pm_hash,
            "expected_current_user_adoption_sha256": adopted_pm_hash,
            "disclosed_not_candidate_drift": post_adoption_followup,
        },
        "passed": all_candidate_hashes and all_json_pass and post_adoption_followup,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
