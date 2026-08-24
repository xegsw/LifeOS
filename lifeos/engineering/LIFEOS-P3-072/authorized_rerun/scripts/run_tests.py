#!/usr/bin/env python3
"""Execute each task-local test and create structured synthetic-only evidence."""
from __future__ import annotations
import importlib.util, json, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("authorized_tests", ROOT / "tests" / "test_sandbox_export.py")
module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
cases = []
for name in sorted(key for key in dir(module) if key.startswith("test_")):
    try: getattr(module, name)(); cases.append({"id": name, "result": "PASS"})
    except Exception: cases.append({"id": name, "result": "FAIL", "detail": traceback.format_exc()})
result = {"task": "LIFEOS-P3-072", "run": "authorized_rerun", "test_count": len(cases), "passed": sum(c["result"] == "PASS" for c in cases), "failed": sum(c["result"] == "FAIL" for c in cases), "cases": cases, "boundary": "synthetic records + newly created system temporary sandbox only"}
(ROOT / "evidence" / "test_results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: result[key] for key in ("task", "run", "test_count", "passed", "failed")}))
raise SystemExit(0 if result["failed"] == 0 else 1)
