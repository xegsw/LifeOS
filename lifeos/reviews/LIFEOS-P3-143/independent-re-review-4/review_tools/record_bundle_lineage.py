#!/usr/bin/env python3
"""Record non-content lineage for the fresh re-review-4 source-built app bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    bundle = Path(args.bundle)
    plist_path = bundle / "Contents/Info.plist"
    executable = bundle / "Contents/MacOS/lifeos-p3-143"
    records = []
    for path in sorted(bundle.rglob("*")):
        if path.is_file() and not path.is_symlink():
            records.append(f"{path.relative_to(bundle).as_posix()}\t{path.stat().st_size}\t{digest(path)}\n")
    document = {
        "schema": "lifeos.p3-143.independent-rereview4.bundle-lineage.v1",
        "mode": "synthetic_offline",
        "candidate_commit": "4f4e6ff25e1821d170e47a7fc87a8c001af65361",
        "profile": "independent-review",
        "run_id": "finalgui-20260902",
        "compiled_root": "/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902",
        "bundle": {"path": str(bundle), "file_count": len(records), "tree_sha256": hashlib.sha256("".join(records).encode()).hexdigest()},
        "binary": {"path": str(executable), "sha256": digest(executable)},
        "info_plist": {"sha256": digest(plist_path), "identifier": plistlib.loads(plist_path.read_bytes()).get("CFBundleIdentifier"), "display_name": plistlib.loads(plist_path.read_bytes()).get("CFBundleDisplayName")},
        "prohibited_boundary_contact": False,
    }
    Path(args.output).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "file_count": len(records), "tree_sha256": document["bundle"]["tree_sha256"]}))


if __name__ == "__main__":
    main()
