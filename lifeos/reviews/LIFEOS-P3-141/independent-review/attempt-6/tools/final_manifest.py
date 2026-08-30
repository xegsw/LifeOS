#!/usr/bin/env python3
"""Create or independently verify attempt-6's non-self-referential manifest."""
import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = "FINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != MANIFEST:
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def expected(root: Path) -> dict:
    files = inventory(root)
    return {
        "schema": "lifeos.p3-141.attempt6.final-manifest.v1",
        "attempt": 6,
        "candidate_commit": "e4eeb73395151955c0b833965979be1806406ce5",
        "scope": "attempt-6 review directory only; task temporary root is excluded after exact cleanup",
        "file_count_excluding_manifest": len(files),
        "files": files,
        "self_reference": "excluded: FINAL_MANIFEST.json",
        "review_conclusion": "Blocked: P0-IR-AX-001; P1-IR-LINEAGE-001",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / MANIFEST
    if args.verify:
        actual = json.loads(manifest_path.read_text(encoding="utf-8"))
        wanted = expected(root)
        status = "PASS" if actual == wanted else "FAIL"
        print(json.dumps({"status": status, "expected_file_count": wanted["file_count_excluding_manifest"], "actual_file_count": actual.get("file_count_excluding_manifest"), "mismatches": [] if status == "PASS" else ["manifest content differs from independent inventory"]}, ensure_ascii=False, sort_keys=True))
        return 0 if status == "PASS" else 1
    manifest_path.write_text(json.dumps(expected(root), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
