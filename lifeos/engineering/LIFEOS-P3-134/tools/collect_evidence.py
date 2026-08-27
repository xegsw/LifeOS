#!/usr/bin/env python3
"""Create non-content P3-134 static/runtime evidence from allowed inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
TASK = ROOT / "lifeos/engineering/LIFEOS-P3-134"
CANDIDATE = TASK / "candidate"
P3116 = ROOT / "lifeos/prototypes/LIFEOS-P3-116"
EXPECTED = {
    "lifeos/architecture/LifeOS架构基线V1.0.md": "1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236",
    "lifeos/prototypes/LIFEOS-P3-116/index.html": "d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b",
    "lifeos/prototypes/LIFEOS-P3-116/app.js": "c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f",
    "lifeos/prototypes/LIFEOS-P3-116/styles.css": "cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3",
    "lifeos/prototypes/LIFEOS-P3-116/fixtures.js": "a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93",
    "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json": "c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49",
    "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md": "584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393",
    "lifeos/prototypes/LIFEOS-P3-116/state_machine.json": "2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc",
    "lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md": "bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467",
    "lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/FINAL_MANIFEST.json": "697d2a788e177b259bed741b8c257bcd3dbdabe550b02b1ddff947b2a2633d35",
    "lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/source-lineage.json": "35d18652df5fac1c63224996a5e2f40e8fa9de2278ce8aa3ff5f283d9de16ec0",
    "lifeos/reviews/LIFEOS-P3-133/re-review-1/independent_review.md": "2ff4c246a5913bc3a591e0b3489367577ccc353f29512177070d20efab75bf21",
    "lifeos/reviews/LIFEOS-P3-133_pm_review.md": "5bb5f7bcebd249cd6069b21685ae53338474747714ceffeb1852754770584e8b",
}
IPC = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback"]
VISUAL = ["styles.css", "fixtures.js", "visual_contract.json", "interaction_contract.md", "state_machine.json", "ia_reconciliation.md"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def regular(path: Path) -> bool:
    return stat.S_ISREG(os.lstat(path).st_mode)

def inventory(base: Path) -> list[dict]:
    entries = []
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        entries.append({"path": str(path.relative_to(base)), "type": "regular" if regular(path) else "nonregular", "bytes": path.stat().st_size if regular(path) else None, "sha256": digest(path) if regular(path) else None})
    return entries

def counts(db_path: Path) -> dict:
    tables = ["captures", "capture_project_links", "candidate_actions", "actions", "action_results", "feedback", "audit", "understandings"]
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        out = {name: conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0] for name in tables}
        out["open_actions"] = conn.execute("SELECT count(*) FROM actions WHERE action_state='open'").fetchone()[0]
        out["quick_check"] = conn.execute("PRAGMA quick_check").fetchone()[0]
        return out
    finally:
        conn.close()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-db", type=Path)
    args = parser.parse_args()
    fixed = []
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        actual = digest(path)
        fixed.append({"path": relative, "type": "regular" if regular(path) else "nonregular", "bytes": path.stat().st_size, "expected_sha256": expected, "actual_sha256": actual, "pass": regular(path) and actual == expected})
    candidate = inventory(CANDIDATE)
    runtime = (CANDIDATE / "src/runtime.rs").read_text()
    adapter = (CANDIDATE / "ui/runtime-adapter.js").read_text()
    handler = re.search(r"tauri::generate_handler!\[(.*?)\]\)", runtime, re.S)
    commands = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    actual_invokes = re.findall(r'invoke\("([a-z_]+)"', adapter)
    visual = {name: digest(CANDIDATE / "ui" / name) == digest(P3116 / name) for name in VISUAL}
    result = {
        "task": "LIFEOS-P3-134",
        "input_contract_pass": all(item["pass"] for item in fixed),
        "fixed_inputs": fixed,
        "candidate_inventory": candidate,
        "candidate_regular_file_count": sum(1 for item in candidate if item["type"] == "regular"),
        "candidate_nonregular_file_count": sum(1 for item in candidate if item["type"] != "regular"),
        "visual_byte_identical": visual,
        "visual_contract_pass": all(visual.values()),
        "ipc": {"expected": IPC, "handler": commands, "handler_exact": commands == IPC, "adapter_invokes": actual_invokes, "adapter_invokes_subset": set(actual_invokes).issubset(set(IPC))},
        "ui_prohibited_direct_capabilities": {"fetch": "fetch(" in adapter, "storage": any(token in adapter for token in ["localStorage", "sessionStorage", "indexedDB"]), "filesystem": any(token in adapter for token in ["readFile", "writeFile", "fs."])},
        "runtime_db_counts": counts(args.runtime_db) if args.runtime_db else None,
        "content_policy": "Counts and IDs only; no Capture/Action/DB content, payload, or content hash is emitted."
    }
    result["passed"] = result["input_contract_pass"] and result["candidate_regular_file_count"] == 75 and result["candidate_nonregular_file_count"] == 0 and result["visual_contract_pass"] and result["ipc"]["handler_exact"] and result["ipc"]["adapter_invokes_subset"] and not any(result["ui_prohibited_direct_capabilities"].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if not result["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
