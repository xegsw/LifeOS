#!/usr/bin/env python3
"""Verify frozen inputs and the P3-111 positive source allowlist for P3-120."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
EVIDENCE = ROOT / "evidence"
SOURCE_ROOT = WORKSPACE / "lifeos/engineering/LIFEOS-P3-111/candidate"
ALLOWLIST = WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_source_allowlist.md"
ABF = WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation_acceptance_basis_freeze.md"

EXPECTED_ABF_SHA256 = "e18c463ffb59f1bb80ba55d48a61009792cbd36190d998867d6f08a7aaebe219"
EXPECTED_INPUTS = {
    "lifeos/reviews/LIFEOS-P3-104_pm_review.md": "8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795",
    "lifeos/reviews/LIFEOS-P3-111_pm_review.md": "e8fc44bcd79b7a2d6fb0ec29f3ff23b22ece0c08fdc260236fb8113f60bb0c10",
    "lifeos/reviews/LIFEOS-P3-114_pm_review.md": "72d861e54a1b9ee57fa3d45b4a1d8352dc6202e3cc7ca252457757bc02ac4e78",
    "lifeos/reviews/LIFEOS-P3-119_pm_review.md": "b1b607642588df2c0f2fc2b3a09d28bb5a9b03e3b1a479c893c8cb8429b26ddb",
    "lifeos/architecture/LifeOS高保真原型IA-V1.0.md": "adcc9daf3b8f0fcf27a13176eabb1581c6079d47b48a26ee88cbaba209704243",
    "lifeos/architecture/LifeOS架构基线V1.0.md": "2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32",
    "lifeos/tasks/LIFEOS-P3-120_source_allowlist.md": "4965260513f63f37dd1d5eba969440a30863a9d5574be0ca06464edccef25e94",
    "lifeos/prototypes/LIFEOS-P3-116/index.html": "d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b",
    "lifeos/prototypes/LIFEOS-P3-116/app.js": "c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f",
    "lifeos/prototypes/LIFEOS-P3-116/styles.css": "cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3",
    "lifeos/prototypes/LIFEOS-P3-116/fixtures.js": "a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93",
    "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md": "584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393",
    "lifeos/prototypes/LIFEOS-P3-116/state_machine.json": "2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc",
    "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json": "c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_entry(path: Path, base: Path) -> dict[str, object]:
    stat = path.lstat()
    return {
        "path": path.relative_to(base).as_posix(),
        "type": "regular" if path.is_file() and not path.is_symlink() else "non-regular",
        "bytes": stat.st_size,
        "sha256": sha256(path) if path.is_file() and not path.is_symlink() else None,
    }


def parse_allowlist() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    in_block = False
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        if line == "```text":
            in_block = True
            continue
        if in_block and line == "```":
            break
        if in_block:
            matched = re.fullmatch(r"([0-9a-f]{64})\s+(\d+)\s{2}(.+)", line)
            if matched:
                rows.append(
                    {"sha256": matched.group(1), "bytes": int(matched.group(2)), "path": matched.group(3)}
                )
    return rows


def main() -> int:
    timestamp = datetime.now(UTC).isoformat()
    fixed_results: list[dict[str, object]] = []
    for relative, expected in EXPECTED_INPUTS.items():
        path = WORKSPACE / relative
        actual = sha256(path) if path.is_file() and not path.is_symlink() else None
        fixed_results.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "result": "PASS" if actual == expected else "FAIL",
            }
        )

    abf_actual = sha256(ABF) if ABF.is_file() and not ABF.is_symlink() else None
    fixed_results.append(
        {
            "path": ABF.relative_to(WORKSPACE).as_posix(),
            "expected_sha256": EXPECTED_ABF_SHA256,
            "actual_sha256": abf_actual,
            "result": "PASS" if abf_actual == EXPECTED_ABF_SHA256 else "FAIL",
        }
    )

    allowed_rows = parse_allowlist()
    source_results: list[dict[str, object]] = []
    for row in allowed_rows:
        path = SOURCE_ROOT / str(row["path"])
        actual = file_entry(path, SOURCE_ROOT) if path.exists() or path.is_symlink() else None
        passed = bool(
            actual
            and actual["type"] == "regular"
            and actual["bytes"] == row["bytes"]
            and actual["sha256"] == row["sha256"]
        )
        source_results.append({**row, "actual": actual, "result": "PASS" if passed else "FAIL"})

    candidate = ROOT / "candidate"
    candidate_inventory = [file_entry(path, candidate) for path in sorted(candidate.rglob("*")) if path.is_file() or path.is_symlink()]
    all_fixed_pass = len(fixed_results) == 15 and all(row["result"] == "PASS" for row in fixed_results)
    all_source_pass = len(source_results) == 72 and all(row["result"] == "PASS" for row in source_results)
    report = {
        "schema": "lifeos-p3-120/fixed-inputs-v1",
        "generated_at_utc": timestamp,
        "precreation_execution_fact": "PRECREATION_PREFLIGHT PASS frozen_inputs=14 allowlist=72 roots=absent source_root=regular was observed before positive copy; this replay verifies the same immutable inputs after candidate creation.",
        "frozen_inputs": fixed_results,
        "positive_source_allowlist": {
            "source_root": "lifeos/engineering/LIFEOS-P3-111/candidate",
            "expected_count": 72,
            "rows": source_results,
        },
        "result": "PASS" if all_fixed_pass and all_source_pass else "FAIL",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "fixed-inputs.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "candidate-inventory.json").write_text(
        json.dumps(
            {
                "schema": "lifeos-p3-120/candidate-inventory-v1",
                "generated_at_utc": timestamp,
                "candidate_root": "lifeos/engineering/LIFEOS-P3-120/candidate",
                "files": candidate_inventory,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": report["result"], "fixed_inputs": len(fixed_results), "allowlist": len(source_results)}))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
