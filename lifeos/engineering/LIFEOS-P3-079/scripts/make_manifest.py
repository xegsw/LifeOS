#!/usr/bin/env python3
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
files = sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
lines = ["# LIFEOS-P3-079 Evidence Manifest", "", "All paths are task-local. Historical P3-063/067/075/077 assets were read-only inputs.", "", "| File | SHA-256 |", "|---|---|"]
for p in files:
    if p.name == "MANIFEST.md": continue
    lines.append(f"| `{p.relative_to(root)}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |")
(root / "evidence/MANIFEST.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
