#!/usr/bin/env python3
"""Build a non-self-referential manifest for raw P3-111 evidence payload."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
MANIFEST = EVIDENCE / "PAYLOAD_MANIFEST.json"
EXCLUDE = {"PAYLOAD_MANIFEST.json", "MANIFEST.md"}

def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": path.relative_to(EVIDENCE).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def main() -> None:
    files = [digest(path) for path in sorted(EVIDENCE.rglob("*")) if path.is_file() and path.name not in EXCLUDE and "/disposable/" not in path.as_posix()]
    payload = {"scope": "P3-111 evidence payload; excludes only manifest/index and disposable copies", "file_count": len(files), "files": files}
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": len(files), "manifest": str(MANIFEST)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
