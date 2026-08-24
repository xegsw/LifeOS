#!/usr/bin/env python3
"""Create an honest blocked-state visual constraint record and non-self manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
MANIFEST = EVIDENCE / "MANIFEST.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError(f"not JPEG: {path}")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in (0xD8, 0xD9):
            continue
        length = int.from_bytes(data[offset : offset + 2], "big")
        if marker in range(0xC0, 0xC4):
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        offset += length
    raise ValueError(f"JPEG dimensions unavailable: {path}")


def main() -> None:
    required = {
        "ABF-M-004": EVIDENCE / "screenshots/actual-default.jpg",
        "ABF-M-005": EVIDENCE / "screenshots/actual-no-suggestion.jpg",
        "ABF-M-006": EVIDENCE / "screenshots/actual-restricted.jpg",
    }
    rows = []
    for row_id, path in required.items():
        width, height = jpeg_size(path)
        rows.append({
            "id": row_id,
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
            "actual_pixels": [width, height],
            "required_pixels": [1280, 1024],
            "status": "PASS" if (width, height) == (1280, 1024) else "BLOCKED",
            "reason": "Actual app window was clamped by the current logical display workspace; no resize, upscale, browser, DOM, or mock substitute was used.",
        })
    constraint = {
        "task": "LIFEOS-P3-106",
        "source": "Computer Use screenshots of the built Tauri .app",
        "result": "BLOCKED" if any(row["status"] != "PASS" for row in rows) else "PASS",
        "rows": rows,
        "evidence_honesty": "The retained files preserve their actual pixel dimensions. They were not resized, padded, composited, or represented as 1280x1024.",
    }
    constraint_path = EVIDENCE / "visual_environment_constraint.json"
    constraint_path.write_text(json.dumps(constraint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST or "target" in path.parts:
            continue
        files.append((str(path.relative_to(ROOT)), digest(path)))
    lines = [
        "# LIFEOS-P3-106 Evidence Manifest (Blocked Candidate)",
        "",
        "- Status: `Blocked — Acceptance Not Met candidate; PM confirmation required`",
        "- Manifest self-entry: excluded by construction",
        "- Coverage: all current P3-106 live files except generated `target/` and this manifest",
        "- Required 1280x1024 actual-app rows: 0/3 PASS; actual screenshots retained without transformation",
        "",
        "| Path | SHA-256 |",
        "|---|---|",
    ]
    lines.extend(f"| `{name}` | `{sha}` |" for name, sha in files)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"manifest_entries": len(files), "visual_status": constraint["result"]}))


if __name__ == "__main__":
    main()
