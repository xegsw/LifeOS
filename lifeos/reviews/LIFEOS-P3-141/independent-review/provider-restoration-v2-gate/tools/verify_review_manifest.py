#!/usr/bin/env python3
"""Verify the fail-closed review manifest without reading any candidate asset."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "FINAL_MANIFEST.json"

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    if "FINAL_MANIFEST.json" in [entry["path"] for entry in manifest["entries"]]:
        errors.append("manifest_is_self_referential")
    for entry in manifest["entries"]:
        path = ROOT / entry["path"]
        if not path.is_file():
            errors.append(f"missing:{entry['path']}")
            continue
        if path.stat().st_size != entry["bytes"]:
            errors.append(f"bytes:{entry['path']}")
        if digest(path) != entry["sha256"]:
            errors.append(f"sha256:{entry['path']}")
    print(json.dumps({"pass": not errors, "errors": errors, "entry_count": len(manifest["entries"])}, ensure_ascii=False))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
