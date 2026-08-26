#!/usr/bin/env python3
"""Preserve the initial P3-120 submission and record the adopted rework authority."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REWORK = SCRIPT.parents[1]
P3_ROOT = SCRIPT.parents[3]
WORKSPACE = P3_ROOT.parents[2]
TEMP_ROOT = Path("/private/tmp/lifeos-p3-120-runtime-mvp-v1")
OUTPUT = REWORK / "preflight.json"

EXPECTED = {
    "initial_engineering_manifest": (P3_ROOT / "evidence/MANIFEST.md", "56f27d9e144f59b8e73cc24a398882fa6c7c6ec9750b84ff4572a5c3c99a70b0"),
    "initial_matrix": (P3_ROOT / "evidence/matrix-results.json", "68bf59499aae369520d4b001a3f1ae700a73406aa9618e5b7ff590e1eaf654e0"),
    "initial_delivery": (WORKSPACE / "lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md", "ef644706a21976053b81fe1019ff9294dce89099e4ab9d199b52df13fda5bdec"),
    "task_card": (WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md", "d61a1cd92924c70c5b83121d78911b90c289d0b27280e752182a19d72cb2902f"),
    "frozen_abf": (WORKSPACE / "lifeos/tasks/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation_acceptance_basis_freeze.md", "e18c463ffb59f1bb80ba55d48a61009792cbd36190d998867d6f08a7aaebe219"),
    "pm_review": (WORKSPACE / "lifeos/reviews/LIFEOS-P3-120_pm_review.md", None),
}


def sha256(path: Path) -> str | None:
    if not path.is_file() or path.is_symlink():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    files = {}
    for label, (path, expected) in EXPECTED.items():
        actual = sha256(path)
        files[label] = {
            "path": path.relative_to(WORKSPACE).as_posix(),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "result": "PASS" if actual is not None and (expected is None or actual == expected) else "FAIL",
        }
    temporary_root_absent = not TEMP_ROOT.exists() and not TEMP_ROOT.is_symlink()
    passed = all(item["result"] == "PASS" for item in files.values()) and temporary_root_absent
    payload = {
        "schema": "lifeos-p3-120/rework-1-preflight-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority": {
            "status": "Rework 1/2 / User Adopted / Remediation Authorized",
            "source": "lifeos/reviews/LIFEOS-P3-120_pm_review.md",
            "scope": "evidence/rework-1 actual-app closure only; candidate and initial Evidence remain read-only",
            "actual_model": "gpt-5.6-terra",
            "actual_reasoning_effort": "xhigh",
            "model_confirmation_source": "PM Review lines 22 and 153; user confirmation recorded by PM",
        },
        "initial_readonly_files": files,
        "temporary_root": {"path": str(TEMP_ROOT), "absent_before_rework": temporary_root_absent},
        "result": "PASS" if passed else "FAIL",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "temporary_root_absent": temporary_root_absent}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
