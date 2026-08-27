#!/usr/bin/env python3
"""Check review artifacts for dynamically generated synthetic input bodies only."""
from __future__ import annotations

import json
from pathlib import Path


REVIEW = Path("/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-133/re-review-1")
TOKENS = [
    chr(0x7532) * 200,
    chr(0x4E59) * 200,
    chr(0x4E19) * 200,
    chr(0x4E01) * 201,
]


def main() -> None:
    matches: list[str] = []
    images: list[str] = []
    for path in sorted(REVIEW.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(REVIEW).as_posix()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            images.append(relative)
        data = path.read_bytes()
        if any(token.encode("utf-8") in data for token in TOKENS):
            matches.append(relative)
    output = {
        "kind": "P3-133 re-review-1 privacy scan",
        "review_artifacts_scanned": sum(1 for path in REVIEW.rglob("*") if path.is_file()),
        "synthetic_input_body_matches": matches,
        "review_image_artifacts": images,
        "passed": not matches and not images,
    }
    (REVIEW / "privacy-scan.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
