#!/usr/bin/env python3
"""Record only whether the ABF-authorized exact temporary root is absent."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP = Path("/private/tmp/lifeos-p3-116-prototype-v1")
OUT = ROOT / "evidence" / "results" / "cleanup.json"

payload = {"authorized_temp_root": str(TEMP), "exists_after_cleanup": TEMP.exists(), "status": "PASS" if not TEMP.exists() else "FAIL"}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
raise SystemExit(0 if payload["status"] == "PASS" else 1)
