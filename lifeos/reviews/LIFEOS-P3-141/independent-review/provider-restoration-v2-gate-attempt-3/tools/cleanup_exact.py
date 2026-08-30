#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

ROOT = Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-independent-review-attempt-3-v1")
MARKER = ROOT / ".lifeos-review-marker.json"
EXPECTED = {
    "marker": "LIFEOS-P3-141 provider-restoration-v2-gate attempt-3",
    "task_id": "LIFEOS-P3-141",
    "purpose": "synthetic-only independent review temporary root",
    "cleanup_rule": "exact marker-gated removal of this root only",
}

if ROOT != Path("/private/tmp/lifeos-p3-141-provider-restoration-v2-independent-review-attempt-3-v1"):
    raise SystemExit("unexpected cleanup target")
if not ROOT.is_dir() or json.loads(MARKER.read_text(encoding="utf-8")) != EXPECTED:
    raise SystemExit("marker gate rejected cleanup")
shutil.rmtree(ROOT)
print(json.dumps({"schema": "lifeos.p3-141.cleanup.v1", "target": str(ROOT), "marker_gated": True, "exists_after": ROOT.exists()}, sort_keys=True))
