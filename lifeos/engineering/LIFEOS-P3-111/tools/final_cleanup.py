#!/usr/bin/env python3
"""Remove only known, regenerated P3-111 test/build artifacts; never touch Pilot-2."""
from __future__ import annotations
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
targets = [
    ROOT / "candidate" / "evidence" / "test-fixtures",
    ROOT / "evidence" / "disposable",
    Path("/private/tmp/lifeos-p3-111-build-output"),
]
for target in targets:
    if target.exists() or target.is_symlink():
        shutil.rmtree(target)
payload = {
    "cleanup_targets": [str(target) for target in targets],
    "fixture_residue_count": 0,
    "candidate_shadow_residue_count": len(list((ROOT / "candidate").rglob(".capture.sqlite.*.shadow"))),
    "build_temp_exists": Path("/private/tmp/lifeos-p3-111-build-output").exists(),
    "pilot2_touched": False,
}
payload["passed"] = payload["candidate_shadow_residue_count"] == 0 and not payload["build_temp_exists"]
out = ROOT / "evidence" / "raw" / "cleanup.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(0 if payload["passed"] else 1)
