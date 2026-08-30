#!/usr/bin/env python3
"""Generate a non-self-referential manifest for this failed independent review."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_final_manifest.py REVIEW_ROOT")
    root = Path(sys.argv[1]).resolve()
    output = root / "FINAL_MANIFEST.json"
    files = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        relative = path.relative_to(root).as_posix()
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    manifest = {
        "schema": "lifeos.p3_141.provider_restoration.independent.final_manifest.v1",
        "non_self_referential": True,
        "self_entry_present": False,
        "review_conclusion": "REWORK",
        "candidate_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "counts": {"p0": 1, "p1": 0, "p2": 0, "unknown": 0, "not_implemented": 6},
        "p0_binding": "ABF2-M-008 / CL-PROV-06: candidate Phase-C receipt gate remains bound to withdrawn ABF-P3-141-v1 rather than frozen v2",
        "dynamic_evidence_status": "not_started_after_pre_dynamic_p0",
        "files": files,
        "file_count_excluding_manifest": len(files),
    }
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file_count_excluding_manifest": len(files), "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
