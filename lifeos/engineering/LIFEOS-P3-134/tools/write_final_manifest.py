#!/usr/bin/env python3
"""Generate the final-closure non-self-referential Final Manifest."""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

TASK_ROOT = Path("/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-134")
FINAL_ROOT = TASK_ROOT / "evidence/final-closure"
MANIFEST = FINAL_ROOT / "FINAL_MANIFEST.json"
SCOPE_PREFIXES = ("candidate/", "tools/", "evidence/final-closure/")


def main() -> None:
    assets = []
    for path in sorted(TASK_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(TASK_ROOT))
        if relative == "evidence/final-closure/FINAL_MANIFEST.json" or not relative.startswith(SCOPE_PREFIXES):
            continue
        mode = os.lstat(path).st_mode
        if not stat.S_ISREG(mode):
            raise SystemExit(f"non-regular scoped asset: {relative}")
        content = path.read_bytes()
        assets.append({
            "path": relative,
            "type": "regular",
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    result = {
        "task": "LIFEOS-P3-134",
        "kind": "final_closure_non_self_referential_manifest",
        "scope": "candidate/, tools/, evidence/final-closure/ under P3-134; historical closure evidence excluded",
        "self_excluded": "evidence/final-closure/FINAL_MANIFEST.json",
        "asset_count": len(assets),
        "assets": assets,
    }
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"manifest": str(MANIFEST), "asset_count": len(assets)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
