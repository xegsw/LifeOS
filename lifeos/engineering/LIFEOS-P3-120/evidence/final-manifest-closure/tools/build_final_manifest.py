#!/usr/bin/env python3
"""Build the P3-120 Rework-2 draft or non-self final retained-asset manifest."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from verify_final_manifest import (
    CANDIDATE,
    CANDIDATE_INVENTORY,
    DELIVERY,
    FINAL_ROOT,
    INITIAL_MANIFEST,
    PM_REVIEW,
    REWORK_MANIFEST,
    REWORK_ROOT,
    WORKSPACE,
    expected_closure_exclusions,
    file_record,
    parse_initial_manifest,
    parse_rework_manifest,
    records_equal,
    scan_regular,
)


def with_lineage(records: list[dict], lineage: str) -> list[dict]:
    return [{**record, "lineage": lineage} for record in records]


def candidate_entries() -> list[dict]:
    inventory = json.loads(CANDIDATE_INVENTORY.read_text(encoding="utf-8"))
    expected = with_lineage(list(inventory["files"]), "current_candidate")
    actual, errors = scan_regular(CANDIDATE, set())
    if errors or not records_equal(with_lineage(actual, "current_candidate"), expected):
        raise ValueError(f"candidate inventory is not current: {errors}")
    return expected


def build(phase: str) -> dict:
    exclusions = expected_closure_exclusions(phase)
    closure, closure_errors = scan_regular(FINAL_ROOT, exclusions)
    if closure_errors:
        raise ValueError(f"final closure contains forbidden types: {closure_errors}")
    initial = parse_initial_manifest()
    rework = parse_rework_manifest()
    return {
        "schema": "lifeos-p3-120/final-retained-manifest-v1",
        "manifest_phase": phase,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "non_self_exclusions": sorted(exclusions),
        "layers": {
            "current_candidate": {"inventory_file": file_record(CANDIDATE_INVENTORY, WORKSPACE), "entries": candidate_entries()},
            "initial_historical": {"manifest_file": file_record(INITIAL_MANIFEST, WORKSPACE), "entries": initial},
            "rework_1": {"manifest_file": file_record(REWORK_MANIFEST, WORKSPACE), "entries": rework},
            "current_delivery": file_record(DELIVERY, WORKSPACE),
            "authority_pm_review": file_record(PM_REVIEW, WORKSPACE),
            "final_closure": {"entries": closure},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["draft", "final"])
    arguments = parser.parse_args()
    payload = build(arguments.phase)
    name = "scope-payload.json" if arguments.phase == "draft" else "FINAL_MANIFEST.json"
    output = FINAL_ROOT / name
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "phase": arguments.phase, "output": name, "closure_files": len(payload["layers"]["final_closure"]["entries"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
