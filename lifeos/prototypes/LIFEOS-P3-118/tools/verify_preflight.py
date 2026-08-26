#!/usr/bin/env python3
"""Recompute P3-118 Frozen inputs without launching or querying Chrome."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[4]
TMP_ROOT = Path("/private/tmp/lifeos-p3-118-native-capture-v1")
EXPECTED = {
    "lifeos/prototypes/LIFEOS-P3-116/index.html": "d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b",
    "lifeos/prototypes/LIFEOS-P3-116/app.js": "c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f",
    "lifeos/prototypes/LIFEOS-P3-116/styles.css": "cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3",
    "lifeos/prototypes/LIFEOS-P3-116/fixtures.js": "a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93",
    "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md": "584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393",
    "lifeos/prototypes/LIFEOS-P3-116/state_machine.json": "2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc",
    "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json": "c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49",
    "lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md": "bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467",
    "lifeos/reviews/LIFEOS-P3-116_pm_review.md": "09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa",
    "lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md": "19ea3fecef60bfa491a3b4e85c009dfeab3aa228bdab2881f0d08af3a1d34ec1",
    "lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor_acceptance_basis_freeze.md": "57d6016e338103f4f53b5e979d3ec2d5eca708e7622ade33c3ccfd8be1c2b0e0",
    "lifeos/deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md": "8530b08e241355fd169b543863f25d5a492c3dd8f00968ab7cea95c94d79ad39",
    "lifeos/prototypes/LIFEOS-P3-117/MANIFEST.md": "8fd17280974a1a3889d4c4ac9d469e7ca02522c584e9fa9cf6df7b41d1d04c0a",
    "lifeos/reviews/LIFEOS-P3-117_pm_review.md": "d80747f2b36e03917affdda10a95fd16a8b87e5d4816b7300a060e34339cdaca",
    "lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/MANIFEST.md": "d02523ba33e1eee085bb2dec921ebf8ab4e25918b7de3330659b09055c166cf7",
    "lifeos/reviews/LIFEOS-P3-117/pm_evidence/initial/blocked_assessment.md": "948a43294faeeb9b70679d2a740ad36b2582a105bf0cb4d0a40094621c3f4351",
    "lifeos/ACCEPTANCE_GOVERNANCE.md": "86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c",
}
TASK = "lifeos/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md"
ABF = "lifeos/tasks/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor_acceptance_basis_freeze.md"
TASK_SHA = "3172457dc2c60080100d367acb979f92fbb060f4c4bd6383f60e9d7cfe76ec1b"
ABF_SHA = "d6f12523683beea42ecd9d9db586b41c489991286e0ee41e2eb4afeab5e5c18c"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CHROME_SHA = "97385e62510154852fd10da11c697bf5066dcc300e3b0c31633bd52ad940b984"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    values = {}
    for relative, expected in EXPECTED.items():
        actual = digest(REPO / relative)
        values[relative] = {"expected": expected, "actual": actual, "result": "PASS" if actual == expected else "FAIL"}
    task_actual = digest(REPO / TASK)
    abf_actual = digest(REPO / ABF)
    chrome_actual = digest(CHROME) if CHROME.is_file() else ""
    all_fixed = all(item["result"] == "PASS" for item in values.values())
    result = {
        "schema_version": "1.0",
        "abf": {"id": "ABF-P3-118-v1", "expected": ABF_SHA, "actual": abf_actual, "result": "PASS" if abf_actual == ABF_SHA else "FAIL"},
        "task_card": {"expected": TASK_SHA, "actual": task_actual, "result": "PASS" if task_actual == TASK_SHA else "FAIL"},
        "fixed_inputs": values,
        "fixed_input_count": len(values),
        "chrome_executable": {"expected": CHROME_SHA, "actual": chrome_actual, "result": "PASS" if chrome_actual == CHROME_SHA else "FAIL"},
        "temporary_root_existed_before_any_p3_118_browser_action": TMP_ROOT.exists(),
        "browser_or_computer_use_action_attempted": False,
        "result": "PASS" if all_fixed and task_actual == TASK_SHA and abf_actual == ABF_SHA and chrome_actual == CHROME_SHA and not TMP_ROOT.exists() else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["result"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
