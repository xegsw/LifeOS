#!/usr/bin/env python3
"""Review-owned post-contact byte verifier for the Frozen ABF input inventory."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE = Path("/Users/xxe/Documents/No.2")
INVENTORY = WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json"
ABF = WORKSPACE / "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze.md"
EXPECTED_ABF = "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    results = []
    for item in inventory["entries"]:
        raw = Path(item["path"])
        path = raw if raw.is_absolute() else WORKSPACE / raw
        results.append({
            "role": item["role"],
            "path": str(path),
            "bytes_match": path.stat().st_size == item["bytes"],
            "sha256_match": digest(path) == item["sha256"],
        })
    checks = [record["bytes_match"] and record["sha256_match"] for record in results]
    checks.append(digest(ABF) == EXPECTED_ABF)
    print(json.dumps({
        "verifier_identity": "attempt-8-review-owned-postcontact-frozen-inputs-v1",
        "inventory": str(INVENTORY),
        "abf": {"path": str(ABF), "sha256": digest(ABF), "expected_sha256": EXPECTED_ABF},
        "entries_verified": len(results),
        "inputs": results,
        "verdict": "Pass" if len(results) == 12 and all(checks) else "Rework",
        "scope": "Read-only immutable task inputs only; no Pilot, real database, credential, provider endpoint, network target, or real content was accessed.",
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
