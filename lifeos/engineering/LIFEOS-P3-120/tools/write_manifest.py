#!/usr/bin/env python3
"""Write a non-self-referential manifest for every retained P3-120 deliverable artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
EVIDENCE = ROOT / "evidence"
MANIFEST = EVIDENCE / "MANIFEST.md"
DELIVERABLE = WORKSPACE / "lifeos/deliverables/LIFEOS-P3-120_person_centered_product_runtime_mvp_implementation.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(WORKSPACE).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
    }


def main() -> int:
    required_results = ["fixed-inputs.json", "build-results.json", "static-results.json", "actual-app-results.json", "runtime-results.json", "negative-results.json", "ui-state-contract-results.json", "cleanup.json", "matrix-results.json"]
    result_status = {name: json.loads((EVIDENCE / name).read_text(encoding="utf-8")).get("result") for name in required_results}
    if not DELIVERABLE.is_file() or any(status != "PASS" for status in result_status.values()):
        print(json.dumps({"result": "FAIL", "result_status": result_status, "deliverable_exists": DELIVERABLE.is_file()}))
        return 1
    retained_roots = [ROOT / "candidate", ROOT / "tests", ROOT / "tools", EVIDENCE, ROOT / "REPRODUCE.md", DELIVERABLE]
    entries: list[dict[str, object]] = []
    for item in retained_roots:
        if item.is_file():
            if item != MANIFEST:
                entries.append(record(item))
        else:
            entries.extend(record(path) for path in sorted(item.rglob("*")) if path.is_file() and path != MANIFEST)
    entries.sort(key=lambda item: str(item["path"]))
    groups = {
        "candidate": sum(1 for item in entries if "/candidate/" in str(item["path"])),
        "tests": sum(1 for item in entries if "/tests/" in str(item["path"])),
        "tools": sum(1 for item in entries if "/tools/" in str(item["path"])),
        "evidence": sum(1 for item in entries if "/evidence/" in str(item["path"])),
        "deliverables": sum(1 for item in entries if "/deliverables/" in str(item["path"])),
    }
    lines = [
        "# LIFEOS-P3-120 Evidence Manifest",
        "",
        "- Schema: `lifeos-p3-120/manifest-v1`",
        "- Non-self-referential: this Manifest is intentionally excluded from its own entries.",
        f"- Generated UTC: `{datetime.now(UTC).isoformat()}`",
        f"- Result inputs: `{json.dumps(result_status, ensure_ascii=False, sort_keys=True)}`",
        f"- Retained file count: `{len(entries)}`",
        f"- Group counts: `{json.dumps(groups, ensure_ascii=False, sort_keys=True)}`",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    lines.extend(f"| `{entry['path']}` | {entry['bytes']} | `{entry['sha256']}` |" for entry in entries)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "entries": len(entries), "groups": groups}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
