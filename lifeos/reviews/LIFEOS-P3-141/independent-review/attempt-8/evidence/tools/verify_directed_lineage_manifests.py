#!/usr/bin/env python3
"""Read-only integrity verifier for task-directed P3-140 and P3-141 inputs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


P3_140_ROOT = Path("/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1")
P3_141_ROOT = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1/candidate-peer/lifeos/engineering/LIFEOS-P3-141")
P3_140_TREE = "6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e"
P3_141_MANIFEST_TREE = "fe16e3ecb83aa65f021cb4f13864aa3a91d2f4ecc41c07702353c02ad71f116a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def framed(items: dict[str, bytes]) -> str:
    hasher = hashlib.sha256()
    for rel in sorted(items, key=lambda value: tuple(value.split("/"))):
        key, body = rel.encode("utf-8"), items[rel]
        hasher.update(len(key).to_bytes(8, "big"))
        hasher.update(key)
        hasher.update(len(body).to_bytes(8, "big"))
        hasher.update(body)
    return hasher.hexdigest()


def manifest_tree(digests: dict[str, str], ordered_paths: list[str] | None = None) -> str:
    hasher = hashlib.sha256()
    names = ordered_paths if ordered_paths is not None else sorted(digests)
    for rel in names:
        digest = digests[rel]
        hasher.update(rel.encode("utf-8"))
        # The directed engineering v3 generator intentionally stores the
        # textual delimiters ``\\0`` and ``\\n``; reproduce that documented
        # byte algorithm exactly for its integrity check.
        hasher.update(b"\\0")
        hasher.update(digest.encode("ascii"))
        hasher.update(b"\\n")
    return hasher.hexdigest()


def verify_p3_140() -> dict:
    manifest = json.loads((P3_140_ROOT / "evidence/FINAL_MANIFEST.json").read_text())
    candidate = manifest["candidate"]
    entries = candidate["entries"]
    observed = {}
    all_regular = True
    for rel, metadata in entries.items():
        path = P3_140_ROOT / "candidate" / rel
        all_regular = all_regular and path.is_file() and not path.is_symlink()
        observed[rel] = sha256(path)
    calculated = framed({rel: (P3_140_ROOT / "candidate" / rel).read_bytes() for rel in entries})
    return {
        "path": str(P3_140_ROOT / "candidate"),
        "manifest_sha256": sha256(P3_140_ROOT / "evidence/FINAL_MANIFEST.json"),
        "manifest_file_count": candidate["file_count"],
        "manifest_tree_sha256": candidate["length_framed_tree_sha256"],
        "checks": {
            "exact_79_entries": len(entries) == 79 == candidate["file_count"],
            "all_listed_files_regular_not_linked": all_regular,
            "all_79_entry_hashes_match": all(observed[k] == entries[k]["sha256"] for k in entries),
            "framed_tree_matches_manifest": calculated == candidate["length_framed_tree_sha256"],
            "framed_tree_matches_frozen_inventory": calculated == P3_140_TREE,
        },
        "calculated_tree_sha256": calculated,
    }


def verify_p3_141_manifest() -> dict:
    manifest_path = P3_141_ROOT / "evidence/FINAL_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    entries = manifest["files"]
    observed = {}
    all_regular = True
    for rel, expected in entries.items():
        path = P3_141_ROOT / rel
        all_regular = all_regular and path.is_file() and not path.is_symlink()
        observed[rel] = sha256(path)
    generated_order = [
        path.relative_to(P3_141_ROOT).as_posix()
        for path in sorted(P3_141_ROOT.rglob("*"))
        if path.is_file() and path != manifest_path
    ]
    calculated = manifest_tree(observed, generated_order)
    return {
        "path": str(P3_141_ROOT),
        "manifest_sha256": sha256(manifest_path),
        "manifest_file_count": manifest["file_count_excluding_manifest"],
        "manifest_tree_sha256": manifest["tree_sha256_excluding_manifest"],
        "checks": {
            "exact_179_entries": len(entries) == 179 == manifest["file_count_excluding_manifest"],
            "all_listed_files_regular_not_linked": all_regular,
            "all_179_entry_hashes_match": all(observed[k] == entries[k] for k in entries),
            "manifest_entry_set_matches_generator_scope": set(generated_order) == set(entries),
            "digest_tree_matches_manifest": calculated == manifest["tree_sha256_excluding_manifest"],
            "digest_tree_matches_expected": calculated == P3_141_MANIFEST_TREE,
            "manifest_excludes_self": "evidence/FINAL_MANIFEST.json" not in entries,
        },
        "calculated_tree_sha256": calculated,
    }


def main() -> None:
    p3_140, p3_141 = verify_p3_140(), verify_p3_141_manifest()
    checks = list(p3_140["checks"].values()) + list(p3_141["checks"].values())
    print(json.dumps({
        "verifier_identity": "attempt-8-review-owned-directed-lineage-manifests-v1",
        "method": "read-only byte hashing; historical screenshot files, if listed, were not opened visually, copied, or used as runtime evidence",
        "p3_140": p3_140,
        "p3_141_engineering_manifest": p3_141,
        "verdict": "Pass" if all(checks) else "Rework",
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
