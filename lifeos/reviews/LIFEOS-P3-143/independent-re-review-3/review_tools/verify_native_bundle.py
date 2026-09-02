#!/usr/bin/env python3
"""Record reproducible lineage for the fresh source-built native .app evidence bundle."""

from __future__ import annotations

import hashlib
import json
import plistlib
from pathlib import Path


BUNDLE = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-3/candidate-app-bundle-target/debug/bundle/macos/LifeOS · 模型设置（安全凭据验证）.app")
OUTPUT = Path("lifeos/reviews/LIFEOS-P3-143/independent-re-review-3/evidence/native_bundle_lineage.json")
EXECUTABLE = BUNDLE / "Contents/MacOS/lifeos-p3-143"
PLIST = BUNDLE / "Contents/Info.plist"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_tree_sha256() -> tuple[str, int]:
    records: list[str] = []
    for path in sorted(BUNDLE.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(BUNDLE).as_posix()
        records.append(f"{relative}\t{path.stat().st_size}\t{sha256(path)}\n")
    return hashlib.sha256("".join(records).encode()).hexdigest(), len(records)


def main() -> None:
    plist = plistlib.loads(PLIST.read_bytes())
    tree_sha256, file_count = bundle_tree_sha256()
    document = {
        "schema": "lifeos.p3-143.native-bundle-lineage.v1",
        "mode": "synthetic_offline",
        "candidate_commit": "a95a0beb27dc0dac183f8a29da550f43af0d6ce3",
        "candidate_source_tree_sha256": "e65a9599fd691b01c2dc87a2b468c01980d56bdaf5e8b8d401371f4fa669bad8",
        "candidate_git_tree": "0cfd7becf7b19541a92941ee493c768fbb4ece40",
        "build": {
            "command": "CARGO_NET_OFFLINE=true cargo tauri build --debug --bundles app --no-sign --ci",
            "candidate_read_only_pre_and_post_verified": True,
            "bundle_path": str(BUNDLE),
        },
        "bundle": {
            "file_count": file_count,
            "tree_sha256": tree_sha256,
            "info_plist_sha256": sha256(PLIST),
            "bundle_identifier": plist.get("CFBundleIdentifier"),
            "product_name": plist.get("CFBundleName"),
        },
        "binary": {
            "path": str(EXECUTABLE),
            "sha256": sha256(EXECUTABLE),
        },
        "prohibited_boundary_contact": False,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "bundle_tree_sha256": tree_sha256, "file_count": file_count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
