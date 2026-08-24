#!/usr/bin/env python3
"""Build a non-self-referential payload manifest for P3-110 evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
EXCLUDE = {"PAYLOAD_MANIFEST.json", "MANIFEST.md"}
files = []
for path in sorted(EVIDENCE.rglob("*")):
    if not path.is_file() or path.name in EXCLUDE:
        continue
    files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
payload = {"scope": "LIFEOS-P3-110 evidence payload; excludes PAYLOAD_MANIFEST.json and MANIFEST.md to avoid self-reference", "file_count": len(files), "files": files}
(EVIDENCE / "PAYLOAD_MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
