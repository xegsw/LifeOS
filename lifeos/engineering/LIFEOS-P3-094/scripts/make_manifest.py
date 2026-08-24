#!/usr/bin/env python3
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [p for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name != "MANIFEST.md" and "__pycache__" not in p.parts]
lines = ["# LIFEOS-P3-094 Evidence Manifest", "", "所有条目是工程源码或不含原文的 Evidence。运行期 SQLite 与 today.html 位于系统临时目录，已在自检后清理。", "", "| 文件 | SHA-256 |", "|---|---|"]
for path in files:
    lines.append(f"| `{path.relative_to(ROOT)}` | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |")
(ROOT / "evidence/MANIFEST.md").write_text("\n".join(lines) + "\n")
