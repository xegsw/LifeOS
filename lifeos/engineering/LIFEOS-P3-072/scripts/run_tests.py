#!/usr/bin/env python3
"""Run P3-072 tests and write task-local structured evidence."""
from __future__ import annotations

import importlib.util
import json
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "tests" / "test_sandbox_export.py"
EVIDENCE = ROOT / "evidence" / "test_results.json"


def main() -> int:
    spec = importlib.util.spec_from_file_location("p3_072_tests", TEST_FILE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    cases = []
    for name in sorted(item for item in dir(module) if item.startswith("test_")):
        try:
            getattr(module, name)()
            cases.append({"id": name, "result": "PASS"})
        except Exception:
            cases.append({"id": name, "result": "FAIL", "detail": traceback.format_exc()})
    result = {
        "task": "LIFEOS-P3-072", "test_count": len(cases),
        "passed": sum(case["result"] == "PASS" for case in cases),
        "failed": sum(case["result"] == "FAIL" for case in cases),
        "cases": cases,
        "boundary": "synthetic records + newly created system temporary sandbox only",
        "prohibited_capabilities": "network,Tauri/IPC,Vault,real DB,cloud,sync,multi-device,L3,external user,non-temporary paths",
    }
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("task", "test_count", "passed", "failed")}))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
