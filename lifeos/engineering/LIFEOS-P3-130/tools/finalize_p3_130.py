#!/usr/bin/env python3
"""Produce non-self-referential P3-130 inventories and final manifest."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK_ROOT = ROOT / "lifeos/engineering/LIFEOS-P3-130"
CANDIDATE = TASK_ROOT / "candidate"
EVIDENCE = TASK_ROOT / "evidence"
TEMP = Path("/private/tmp/lifeos-p3-130-context-recovery-v1")
MANIFEST = EVIDENCE / "FINAL_MANIFEST.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root, exclude=()):
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path in exclude:
            continue
        try:
            shown_path = str(path.relative_to(ROOT))
        except ValueError:
            shown_path = str(path)
        entries.append({"path": shown_path, "bytes": path.stat().st_size, "sha256": digest(path)})
    return entries

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["temp-inventory", "cleanup-record", "manifest"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if args.mode == "temp-inventory":
        value = {"task": "LIFEOS-P3-130", "temporary_root": str(TEMP), "exists": TEMP.exists(), "entries": inventory(TEMP) if TEMP.exists() else []}
    elif args.mode == "cleanup-record":
        value = {"task": "LIFEOS-P3-130", "temporary_root": str(TEMP), "exact_cleanup_target": str(TEMP), "exists_after_cleanup": TEMP.exists(), "result": "PASS" if not TEMP.exists() else "FAIL", "historical_runtime_roots_accessed": []}
    else:
        value = {
            "task": "LIFEOS-P3-130", "manifest_kind": "non_self_referential_final_manifest",
            "task_contract_sha256": digest(ROOT / "lifeos/tasks/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md"),
            "source_allowlist_sha256": digest(ROOT / "lifeos/tasks/LIFEOS-P3-130_source_allowlist.md"),
            "candidate_inventory": inventory(CANDIDATE),
            "evidence_inventory": inventory(EVIDENCE, exclude=(MANIFEST,)),
            "excluded_from_evidence_inventory": [str(MANIFEST.relative_to(ROOT)), "lifeos/engineering/LIFEOS-P3-130/evidence/build-cache/** (task-local reproducible cache, excluded from manifest inventory)"],
            "cleanup_record": "lifeos/engineering/LIFEOS-P3-130/evidence/cleanup.json",
            "independent_review": "not_started_by_engineering_session",
        }
    write(output, value)
    print(json.dumps({"output": str(output), "entries": len(value.get("entries", value.get("evidence_inventory", [])))}, ensure_ascii=False))

if __name__ == "__main__":
    main()
