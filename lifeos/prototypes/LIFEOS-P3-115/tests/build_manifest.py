#!/usr/bin/env python3
"""Build a non-self SHA-256 manifest for P3-115 output files."""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "MANIFEST.md"
excluded = {MANIFEST.resolve()}
paths = []
for path in sorted(ROOT.rglob("*")):
    if path.is_file() and path.resolve() not in excluded and "__pycache__" not in path.parts:
        paths.append(path)
lines = ["# P3-115 Evidence Manifest", "", "Non-self manifest: this file intentionally excludes itself.", "", "| Path | Bytes | SHA-256 |", "|---|---:|---|"]
for path in paths:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.append(f"| `{path.relative_to(ROOT)}` | {path.stat().st_size} | `{digest}` |")
MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"manifest entries: {len(paths)}")
