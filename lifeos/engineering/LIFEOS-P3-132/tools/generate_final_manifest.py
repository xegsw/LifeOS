#!/usr/bin/env python3
"""Generate the non-self P3-132 Final Manifest after closure artifacts exist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT.parents[1] / "tasks" / "LIFEOS-P3-132_global_ai_context_evidence_backed_understanding_and_today_intelligence_lite.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path, excluded: set[str]) -> list[dict[str, object]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded or any(rel.startswith(prefix + "/") for prefix in excluded):
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path)})
    return rows


def main() -> int:
    candidate = inventory(ROOT / "candidate", {"target"})
    evidence = inventory(ROOT / "evidence", {"FINAL_MANIFEST.json", "build-cache"})
    document = {
        "manifest_kind": "LIFEOS-P3-132 engineering final manifest (non-self)",
        "task": "LIFEOS-P3-132",
        "task_contract_sha256": sha(TASK),
        "candidate_inventory_count": len(candidate),
        "candidate_inventory": candidate,
        "evidence_inventory_count": len(evidence),
        "evidence_inventory": evidence,
        "excluded_from_evidence_inventory": [
            "evidence/FINAL_MANIFEST.json (self)",
            "evidence/build-cache/ (rebuildable task-local cache; dynamic bundle identity is retained separately)",
        ],
    }
    (ROOT / "evidence/FINAL_MANIFEST.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"candidate": len(candidate), "evidence": len(evidence)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
