#!/usr/bin/env python3
"""Execute the six disposable semantic-verifier mutations and retain only their outputs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
VERIFIER = EVIDENCE / "semantic_verifier.py"
MUTATIONS = ["missing_file", "hash_changed", "cleanup_residue", "negative_exit_zero", "db_count_wrong", "geometry_wrong"]
OUT = EVIDENCE / "mutations"
OUT.mkdir(exist_ok=True)
results = []
for mutation in MUTATIONS:
    process = subprocess.run([sys.executable, str(VERIFIER), "--mutation", mutation], text=True, capture_output=True)
    path = OUT / f"{mutation}.json"
    path.write_text(process.stdout, encoding="utf-8")
    results.append({"mutation": mutation, "exit_code": process.returncode, "output": str(path.relative_to(ROOT))})
payload = {"all_nonzero": all(item["exit_code"] != 0 for item in results), "results": results}
(EVIDENCE / "mutation-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if not payload["all_nonzero"]:
    raise SystemExit(1)
