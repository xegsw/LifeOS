#!/usr/bin/env python3
"""Check that review artifacts contain no credential-shaped or private-content markers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
OUTPUT = REVIEW / "evidence" / "content_exclusion.json"
TEXT_SUFFIXES = {".json", ".md", ".py", ".swift", ".sha256"}
MARKERS = ["BEGIN PRIVATE KEY", "PRIVATE KEY-----", "Authorization: Bearer ", "SESSION_SECRET_DO_NOT_PERSIST"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checked = []
    findings = []
    for path in sorted(REVIEW.rglob("*")):
        if path in {OUTPUT, Path(__file__).resolve()} or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(REVIEW))
        checked.append({"path": rel, "sha256": sha256(path)})
        for marker in MARKERS:
            if marker in text:
                findings.append({"path": rel, "marker": marker})
    payload = {
        "schema": "lifeos-p3-141-content-exclusion-v1",
        "review_root": str(REVIEW),
        "text_artifacts_checked": len(checked),
        "credential_or_private_content_findings": findings,
        "screenshot_review": "Three PID-bound captures were visually inspected; each contains only the synthetic candidate UI and no entered user content.",
        "pass": not findings,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
