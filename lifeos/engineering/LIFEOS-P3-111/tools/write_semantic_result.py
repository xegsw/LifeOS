#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_verifier import verify
ROOT = Path(__file__).resolve().parents[1]
result = verify(ROOT / "evidence")
(ROOT / "evidence" / "semantic-verifier-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
