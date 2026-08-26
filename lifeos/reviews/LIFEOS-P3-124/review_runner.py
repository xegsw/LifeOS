#!/usr/bin/env python3
"""P3-124 task-local independent preflight and candidate-copy runner.

This file was written for P3-124.  It deliberately uses only Python's standard
library and does not import, execute, or copy any historical review runner.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REVIEW = Path(__file__).resolve().parent
EVIDENCE = REVIEW / "evidence"
TEMP = Path("/private/tmp/lifeos-p3-124-independent-review-v1")
ALLOWLIST = ROOT / "lifeos/tasks/LIFEOS-P3-124_candidate_source_allowlist.md"

FIXED = {
    "lifeos/tasks/LIFEOS-P3-124_p3_122_combined_candidate_fresh_isolated_independent_review_final_successor.md": "5e4ac7f914c968af1f27c243be4fda11bcba870df8d2a3a45cd78cc9323adb6b",
    "lifeos/tasks/LIFEOS-P3-124_p3_122_combined_candidate_fresh_isolated_independent_review_final_successor_acceptance_basis_freeze.md": "b8504298cdc20dd3425eb519f556d27a3867640de3f8fb5a4476f81095356efc",
    "lifeos/tasks/LIFEOS-P3-124_candidate_source_allowlist.md": "198875e445c15469f4d02e7799368ac7d5ca05f7da1f672b356969a46dd593f5",
    "lifeos/tasks/LIFEOS-P3-124_authorization/MANIFEST.md": "5036cd762888ef09cb985c1de416d17a9a244dff63e779ad08fb591b5e363cd7",
    "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json": "b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c",
    "lifeos/reviews/LIFEOS-P3-122_pm_review.md": "1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe",
    "lifeos/reviews/LIFEOS-P3-122/pm_evidence/acceptance/MANIFEST.md": "c8fac52c00df7fa1308bb6f6143c8a13fec83568e19b31afb6bd17dd9b1a7966",
    "lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md": "fc65335b73280b64888c5803bcacf4402771c5b9cb69eaeac7117c20076adecc",
    "lifeos/reviews/LIFEOS-P3-123/independent_review.md": "2732f7ae29543ae6cbf7b80a6b950f702d9fff23981a1076248662c33f763f8f",
    "lifeos/reviews/LIFEOS-P3-123_pm_review.md": "7d8c1cb73ed08a016c624ff70affa106478e3b569a4c6487b8fa6ea191b27120",
    "lifeos/reviews/LIFEOS-P3-123/pm_evidence/final-adoption/MANIFEST.md": "fe1f6d2c3d34b0f109c8ca951618fe088bd2ff9d49a764ec739c7632aea6c65b",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows() -> list[tuple[str, int, str]]:
    raw = ALLOWLIST.read_bytes()
    result = []
    for line in raw.decode("utf-8").splitlines():
        if line.startswith("| `lifeos/engineering/LIFEOS-P3-122/candidate/"):
            parts = line.split("`")
            result.append((parts[1], int(parts[2].split("|")[1].strip()), parts[3]))
    return result


def preflight() -> dict:
    raw = ALLOWLIST.read_bytes()
    parsed = rows()
    file_issues = []
    for rel, expected_bytes, expected_hash in parsed:
        path = ROOT / rel
        if not path.is_file():
            file_issues.append({"path": rel, "reason": "missing"})
        elif path.stat().st_size != expected_bytes or digest(path) != expected_hash:
            file_issues.append({"path": rel, "reason": "bytes_or_hash_mismatch"})
    hashes = {path: digest(ROOT / path) for path in FIXED}
    result = {
        "test_id": "P124-M001",
        "actual_model": "gpt-5.6-terra",
        "reasoning_effort": "xhigh",
        "model_metadata_source": "node_repl.requestMeta x-codex-turn-metadata",
        "allowlist": {
            "utf8": True,
            "crlf": b"\r\n" in raw,
            "physical_lines": len(raw.decode("utf-8").splitlines()),
            "candidate_rows": len(parsed),
            "literal_backslash_n": b"\\n" in raw,
            "sha256": digest(ALLOWLIST),
            "file_match_count": len(parsed) - len(file_issues),
            "issues": file_issues,
        },
        "fixed_hashes": hashes,
        "fixed_hash_mismatches": [p for p, h in hashes.items() if h != FIXED[p]],
        "roots_before_copy": {"review_root": REVIEW.exists(), "temp_root": TEMP.exists()},
        "pass": len(parsed) == 75 and len(raw.decode("utf-8").splitlines()) == 87 and not file_issues and not [p for p, h in hashes.items() if h != FIXED[p]] and not (b"\r\n" in raw) and b"\\n" not in raw,
    }
    return result


def copy_candidate() -> dict:
    check = preflight()
    if not check["pass"] or TEMP.exists():
        raise SystemExit("refusing candidate copy: preflight fail or temp root already exists")
    candidate = TEMP / "candidate"
    for rel, _, _ in rows():
        source = ROOT / rel
        dest = candidate / Path(rel).relative_to("lifeos/engineering/LIFEOS-P3-122/candidate")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    return {"test_id": "P124-M004", "copied_files": len(rows()), "candidate": str(candidate)}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"preflight", "copy"}:
        print("usage: review_runner.py preflight|copy", file=sys.stderr)
        return 2
    result = preflight() if sys.argv[1] == "preflight" else copy_candidate()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    output = EVIDENCE / ("preflight.json" if sys.argv[1] == "preflight" else "copy-result.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("pass", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
