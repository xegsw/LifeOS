#!/usr/bin/env python3
"""Write a reproducible inventory of all P3-125 task-local outputs."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence" / "FINAL_MANIFEST.json"
DELIVERABLE = ROOT.parents[1] / "deliverables" / "LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT or path.name == ".DS_Store":
            continue
        files.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    files.append(
        {
            "path": "../deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md",
            "bytes": DELIVERABLE.stat().st_size,
            "sha256": sha256(DELIVERABLE),
        }
    )
    verification = json.loads((ROOT / "evidence" / "results" / "verification.json").read_text(encoding="utf-8"))
    document = {
        "task": "LIFEOS-P3-125",
        "abf": "ABF-P3-125-v1",
        "inventory_excludes": "evidence/FINAL_MANIFEST.json itself",
        "verification_result": verification["result"],
        "files": files,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "files": len(files), "manifest": str(OUTPUT)}))


if __name__ == "__main__":
    main()
