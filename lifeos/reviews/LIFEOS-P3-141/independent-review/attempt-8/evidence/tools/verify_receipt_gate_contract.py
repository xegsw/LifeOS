#!/usr/bin/env python3
"""Read-only structural verifier for the candidate's Phase-B receipt gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path


CASES = {
    "legacy_any_string": "LIFEOS_P3_141_PHASE_B_RECEIPT",
    "missing": "phase_c_real requires an explicit independent receipt path before runtime-root inspection",
    "malformed": "strict_json(&receipt_bytes, \"Phase B receipt\")",
    "extra": "#[serde(deny_unknown_fields)]",
    "duplicate": "duplicate JSON key",
    "wrong_abf_or_candidate": "receipt task, ABF, schema, or Pass verdict binding rejected",
    "wrong_tree": "receipt is stale or bound to a different candidate tree",
    "wrong_manifest": "receipt review-manifest hash binding rejected",
    "non_pass": "receipt task, ABF, schema, or Pass verdict binding rejected",
    "stale": "receipt is stale or bound to a different candidate commit",
    "dirty_or_uncommitted": "review ownership worktree is mutable or dirty",
    "wrong_owner_or_unrelated_root": "receipt is not independently owned outside the candidate tree",
    "file_or_ancestor_link": "one read-only regular non-linked file",
    "directory": "must be one read-only regular non-linked file",
    "oversize": "MAX_RECEIPT_BYTES",
}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_receipt_gate_contract.py BUILD_RS")
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    main_start = source.index("fn main()")
    main_body = source[main_start:]
    order = main_body.index("let build_mode = build_mode()") < main_body.index("let root = frozen_runtime_root(build_mode)")
    enforced = {case: anchor in source for case, anchor in CASES.items()}
    result = {
        "verifier_identity": "attempt-8-review-owned-receipt-gate-contract-v1",
        "build_mode_before_runtime_root": order,
        "negative_cases": enforced,
        "all_cases_structurally_enforced": all(enforced.values()),
        "verdict": "Pass" if order and all(enforced.values()) else "Rework",
        "scope": "Static guard coverage only; separate build invocations supply the legacy and missing-path execution negatives.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "Pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
