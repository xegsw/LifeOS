#!/usr/bin/env python3
"""Record exact task-local cleanup only after the authorized path is absent."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMP = pathlib.Path("/private/tmp/lifeos-p3-115-prototype-v1")
result = {"status": "PASS" if not TEMP.exists() else "FAIL", "exact_temporary_root": str(TEMP), "exists_after_cleanup": TEMP.exists(), "scope": "only the exact P3-115 task-local root"}
(ROOT / "evidence" / "results" / "cleanup.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
