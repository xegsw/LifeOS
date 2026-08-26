#!/usr/bin/env python3
"""Create a non-self-referential manifest for all task-local payload files."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "MANIFEST.md"
EXCLUDE = {MANIFEST.resolve(), (ROOT / "evidence" / "results" / "manifest_build.json").resolve()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.resolve() not in EXCLUDE and "__pycache__" not in path.parts:
            rows.append((path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256(path)))
    lines = ["# P3-116 Evidence Manifest", "", "非自指：本清单自身不列入 hash 集合。", "", "| Path | Bytes | SHA-256 |", "|---|---:|---|"]
    lines.extend(f"| `{path}` | {size} | `{digest}` |" for path, size, digest in rows)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"manifest_entries={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
