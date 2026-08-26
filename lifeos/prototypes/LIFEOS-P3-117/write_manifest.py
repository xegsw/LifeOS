#!/usr/bin/env python3
"""Build a non-self-referential payload Manifest for all P3-117 retained files."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "MANIFEST.md"
DELIVERY = ROOT.parents[1] / "deliverables/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries() -> list[tuple[str, int, str]]:
    result = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST or "__pycache__" in path.parts:
            continue
        result.append((str(path.relative_to(ROOT)), path.stat().st_size, digest(path)))
    return result


def main() -> None:
    payload = entries()
    delivery_hash = digest(DELIVERY) if DELIVERY.is_file() else "MISSING"
    lines = [
        "# LIFEOS-P3-117 Evidence Manifest",
        "",
        "- Current status: BLOCKED / NOT PASS. This is a retained static-preflight and cleanup manifest, not a dynamic-Evidence pass manifest.",
        "- Scope: retained P3-117 probe, runners, plans, static preflight and cleanup results. No raw/proof/clean images, geometry, action results, verifier baseline or mutation result is present because no GUI action was safely executed.",
        "- This manifest intentionally excludes itself from the payload list; it is non-self-referential.",
        "- All files are task-local. P3-116 is not included or modified.",
        f"- Delivery report reference (outside this payload): `{DELIVERY.relative_to(ROOT.parents[2])}`; SHA-256: `{delivery_hash}`.",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    lines.extend("| " + path + " | " + str(size) + " | " + value + " |" for path, size, value in payload)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("PASS " + str(len(payload)))


if __name__ == "__main__":
    main()
