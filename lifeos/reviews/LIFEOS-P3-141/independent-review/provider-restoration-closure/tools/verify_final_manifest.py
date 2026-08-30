#!/usr/bin/env python3
"""Read-only verifier for the failed-review manifest, with in-memory mutations."""

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(manifest: dict, root: Path) -> list[str]:
    found: list[str] = []
    if manifest.get("schema") != "lifeos.p3_141.provider_restoration.independent.final_manifest.v1":
        found.append("schema")
    if manifest.get("review_conclusion") != "REWORK":
        found.append("conclusion")
    if manifest.get("counts") != {"p0": 1, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 6}:
        found.append("counts")
    entries = manifest.get("files")
    if not isinstance(entries, dict):
        return found + ["files"]
    if "FINAL_MANIFEST.json" in entries:
        found.append("self_entry")
    actual = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and path.name != "FINAL_MANIFEST.json")
    if sorted(entries) != actual:
        found.append("file_set")
    for relative, expected in entries.items():
        path = root / relative
        if not path.is_file() or {"bytes": path.stat().st_size, "sha256": sha256(path)} != expected:
            found.append(f"hash:{relative}")
    return found


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_final_manifest.py REVIEW_ROOT")
    root = Path(sys.argv[1]).resolve()
    manifest = json.loads((root / "FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    control = errors(manifest, root)
    changed_hash = deepcopy(manifest)
    first = next(iter(changed_hash["files"]))
    changed_hash["files"][first]["sha256"] = "0" * 64
    self_reference = deepcopy(manifest)
    self_reference["files"]["FINAL_MANIFEST.json"] = {"bytes": 1, "sha256": "0" * 64}
    false_pass = deepcopy(manifest)
    false_pass["review_conclusion"] = "PASS"
    mutations = {
        "changed_hash_rejected": bool(errors(changed_hash, root)),
        "self_reference_rejected": bool(errors(self_reference, root)),
        "false_pass_rejected": bool(errors(false_pass, root)),
    }
    result = {"control_errors": control, "mutations": mutations, "pass": not control and all(mutations.values())}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
