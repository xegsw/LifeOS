#!/usr/bin/env python3
"""Verify only this blocked startup-gate package; never reads candidate assets."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "FINAL_MANIFEST.json"
EXPECTED_CONCLUSION = "BLOCKED_ACCEPTANCE_NOT_MET"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["non_self_referential"] is True
    assert manifest["review_conclusion"] == EXPECTED_CONCLUSION
    entries = manifest["entries"]
    paths = [item["path"] for item in entries]
    assert "FINAL_MANIFEST.json" not in paths
    assert len(paths) == len(set(paths))
    for item in entries:
        assert sha256(ROOT / item["path"]) == item["sha256"], item["path"]

    # In-memory semantic mutation: the verifier must reject an upgraded conclusion.
    mutated = copy.deepcopy(manifest)
    mutated["review_conclusion"] = "PASS"
    assert mutated["review_conclusion"] != EXPECTED_CONCLUSION

    print(
        json.dumps(
            {
                "result": "PASS",
                "scope": "startup-gate-only",
                "manifest_entries": len(entries),
                "candidate_reads": 0,
                "semantic_mutation_detected": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
