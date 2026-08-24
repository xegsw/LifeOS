#!/usr/bin/env python3
"""Build the non-self-referential P3-112 Rework 1 evidence manifest."""
from __future__ import annotations

import hashlib
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1]
OUTPUT = EVIDENCE / "MANIFEST.md"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    files = sorted(path for path in EVIDENCE.rglob("*") if path.is_file() and path != OUTPUT)
    lines = [
        "# LIFEOS-P3-112 Rework 1 Independent Review Evidence Manifest",
        "",
        "- Scope: task-local P3-112 Rework 1 Evidence only; this Manifest is excluded from its own payload.",
        "- Result scope: independent Pass pending PM acceptance; this does not close risks, freeze assets, restore a baseline, admit Stage 4, or constitute user adoption.",
        "- Pilot-2 access: 0; real app launch: 0; network: 0; historical P3-111 writes: 0.",
        "- Temporary root: /private/tmp/lifeos-p3-112-review-v1 was absent before the final run and absent after exact cleanup.",
        "",
        "| File | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for path in files:
        relative = path.relative_to(EVIDENCE).as_posix()
        lines.append(f"| {relative} | {path.stat().st_size} | {sha256(path)} |")
    lines += ["", f"Payload file count (excluding MANIFEST.md): {len(files)}.", ""]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
