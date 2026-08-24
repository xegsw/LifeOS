#!/usr/bin/env python3
"""Independent, read-only verification for the non-325-entry historical manifests."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).with_name("manifest-verification.json")
MANIFESTS = [
    ROOT / "lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md",
    ROOT / "lifeos/reviews/LIFEOS-P3-106/pm_evidence/rework-1/MANIFEST.md",
]
TEXT_LINE = re.compile(r"^([0-9a-f]{64})\s{2}(.+?)\s*$")
TABLE_LINE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(manifest: Path, declared: str) -> Path:
    return ROOT / declared if declared.startswith("lifeos/") else manifest.parent / declared


results = []
for manifest in MANIFESTS:
    entries, bad, self_refs = [], [], []
    for line in manifest.read_text().splitlines():
        matched = TEXT_LINE.match(line)
        if matched:
            expected, declared = matched.groups()
        else:
            table = TABLE_LINE.match(line)
            if not table:
                continue
            declared, expected = table.groups()
        path = resolve(manifest, declared).resolve()
        if path == manifest.resolve():
            self_refs.append(declared)
            continue
        actual = digest(path) if path.is_file() else None
        entries.append({"path": declared, "expected": expected, "actual": actual})
        if actual != expected:
            bad.append(declared)
    results.append({
        "manifest": str(manifest.relative_to(ROOT)),
        "entries": len(entries),
        "bad": bad,
        "self_refs": self_refs,
        "status": "PASS" if entries and not bad and not self_refs else "FAIL",
    })

OUT.write_text(json.dumps({
    "task_id": "LIFEOS-P3-107",
    "method": "P3-106 Engineering 325-entry rehash is independently recorded in static-results.json; this verifier covers the remaining P3-104 Engineering/PM and P3-106 PM inventories without importing submitted runners.",
    "results": results,
    "summary": {"pass": sum(x["status"] == "PASS" for x in results), "fail": sum(x["status"] != "PASS" for x in results)},
}, ensure_ascii=False, indent=2) + "\n")
