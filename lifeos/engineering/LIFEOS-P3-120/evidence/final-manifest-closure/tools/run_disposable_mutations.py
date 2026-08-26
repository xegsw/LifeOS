#!/usr/bin/env python3
"""Prove the final-manifest verifier fails closed using only an exact disposable copy."""

from __future__ import annotations

import copy
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from verify_final_manifest import FINAL_ROOT, verify_manifest


DRAFT = FINAL_ROOT / "scope-payload.json"
DISPOSABLE_PARENT = FINAL_ROOT / "disposable"
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "payload-root"
OUTPUT = FINAL_ROOT / "mutation-results.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


def mutation_result(name: str, errors: list[str], expected_fragment: str) -> dict:
    passed = bool(errors) and any(expected_fragment in item for item in errors)
    return {"name": name, "result": "PASS" if passed else "NOT PASS", "expected_error_fragment": expected_fragment, "errors": errors[:8]}


def main() -> int:
    if DISPOSABLE_PARENT.exists() or DISPOSABLE_PARENT.is_symlink():
        fail("disposable parent already exists; refusing broad or ambiguous cleanup")
    payload = json.loads(DRAFT.read_text(encoding="utf-8"))
    entries = payload["layers"]["final_closure"]["entries"]
    DISPOSABLE_ROOT.mkdir(parents=True)
    try:
        for entry in entries:
            relative = Path(entry["path"])
            source = FINAL_ROOT / relative
            target = DISPOSABLE_ROOT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        control_errors = verify_manifest(payload, "draft", closure_root=DISPOSABLE_ROOT)
        control = {"result": "PASS" if not control_errors else "NOT PASS", "errors": control_errors}
        cases: list[dict] = []
        missing_delivery = copy.deepcopy(payload)
        del missing_delivery["layers"]["current_delivery"]
        cases.append(mutation_result("missing_current_delivery", verify_manifest(missing_delivery, "draft", closure_root=DISPOSABLE_ROOT), "current delivery"))
        changed_hash = copy.deepcopy(payload)
        changed_hash["layers"]["current_candidate"]["entries"][0]["sha256"] = "0" * 64
        cases.append(mutation_result("changed_candidate_payload_hash", verify_manifest(changed_hash, "draft", closure_root=DISPOSABLE_ROOT), "candidate inventory records"))
        unexpected = DISPOSABLE_ROOT / "unexpected-retained-file.txt"
        unexpected.write_text("disposable mutation only\n", encoding="utf-8")
        cases.append(mutation_result("extra_closure_file", verify_manifest(payload, "draft", closure_root=DISPOSABLE_ROOT), "final closure inventory"))
        unexpected.unlink()
        lineage_confusion = copy.deepcopy(payload)
        lineage_confusion["layers"]["initial_historical"]["entries"][0]["lineage"] = "current_candidate"
        cases.append(mutation_result("historical_current_lineage_confusion", verify_manifest(lineage_confusion, "draft", closure_root=DISPOSABLE_ROOT), "initial historical rows"))
        passed = control["result"] == "PASS" and all(case["result"] == "PASS" for case in cases)
    finally:
        if DISPOSABLE_ROOT.exists() or DISPOSABLE_ROOT.is_symlink():
            shutil.rmtree(DISPOSABLE_ROOT)
        if DISPOSABLE_PARENT.exists() and not DISPOSABLE_PARENT.is_symlink():
            DISPOSABLE_PARENT.rmdir()
    payload_out = {
        "schema": "lifeos-p3-120/final-manifest-mutations-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "disposable copy under final-manifest-closure only; no candidate, Rework-1, runtime temp root, Pilot, real asset, network, or app access",
        "pristine_control": control,
        "mutations": cases,
        "disposable_root_removed": not DISPOSABLE_PARENT.exists() and not DISPOSABLE_PARENT.is_symlink(),
        "result": "PASS" if passed and not DISPOSABLE_PARENT.exists() else "NOT PASS",
    }
    OUTPUT.write_text(json.dumps(payload_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload_out["result"], "mutation_count": len(cases), "control": control["result"]}))
    return 0 if payload_out["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"result": "NOT PASS", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
