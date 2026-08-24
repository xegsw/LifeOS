#!/usr/bin/env python3
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rework = root / "evidence/rework"
files = sorted(p for p in rework.rglob("*") if p.is_file() and p.name != "MANIFEST.md")
files += sorted(root.glob("src/*.py")) + sorted(root.glob("tests/*.py")) + [root / "scripts/operator_cli.py", root / "scripts/run_rework_self_check.py"]
lines = ["# LIFEOS-P3-079 D-0328 Rework Evidence Manifest", "", "New Rework evidence is isolated in this directory. Parent `evidence/` is read-only historical evidence.", "", "| File | SHA-256 |", "|---|---|"]
for p in files:
    lines.append(f"| `{p.relative_to(root)}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |")
(rework / "MANIFEST.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
