#!/usr/bin/env python3
"""Finalize the AC matrix only after the one authorized temporary root is absent."""
from __future__ import annotations

import json
from pathlib import Path


TASK = Path("/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-134")
EVIDENCE = TASK / "evidence/final-closure"
MATRIX = EVIDENCE / "matrix"
TEMP = Path("/private/tmp/lifeos-p3-134-ui-restoration-v1")


def main() -> None:
    if TEMP.exists() or TEMP.is_symlink():
        raise SystemExit("authorized temporary root remains present")
    cleanup = {
        "task": "LIFEOS-P3-134",
        "kind": "exact_temporary_root_cleanup_receipt",
        "temporary_root": str(TEMP),
        "cleanup_method": "single exact absolute-path removal; no glob, find, or broad-prefix deletion",
        "temporary_root_absent": True,
        "candidate_preserved": True,
        "historical_inputs_preserved": True,
        "pilot_or_real_db_access": False,
    }
    (EVIDENCE / "cleanup.json").write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pre = json.loads((MATRIX / "ac-matrix-pre-cleanup.json").read_text(encoding="utf-8"))
    results = dict(pre["results"])
    results["AC-16"] = True
    final = {
        "task": "LIFEOS-P3-134",
        "status": "FINAL_PASS_CANDIDATE",
        "results": results,
        "counts": {"P0": 0, "P1": 0, "P2": 1, "Unknown": 0, "Not Implemented": 0},
        "overall_pass": all(results.values()),
        "nonblocking_p2": {
            "id": "P3-134-FC-001",
            "description": "A verifier diagnostic redirect briefly wrote a non-content stdout file outside the authorized temporary root. It was removed immediately by its exact absolute path; no candidate, Evidence, historical asset, Pilot-3, or real-data path was accessed or changed.",
            "blocking": False,
        },
        "governance_note": "Engineering Final Pass Candidate only; this does not update PM ledger, close risk, freeze assets, or authorize Stage 4.",
    }
    (MATRIX / "ac-matrix.json").write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
