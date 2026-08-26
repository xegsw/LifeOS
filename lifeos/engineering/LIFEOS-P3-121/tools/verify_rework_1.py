#!/usr/bin/env python3
"""Fail-closed, P3-121 Rework 1 visual-contract and input verifier.

This runner writes only the Rework-1 Evidence directory.  It deliberately
does not replace the initial self-check Evidence or any P3-116/P3-120 input.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
OUT = ROOT / "evidence" / "rework-1"
WORKSPACE = ROOT.parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(ident: str, condition: bool, evidence: str) -> dict[str, str]:
    return {"id": ident, "result": "PASS" if condition else "FAIL", "evidence": evidence}


def main() -> int:
    app = (CANDIDATE / "ui" / "app.js").read_text(encoding="utf-8")
    css = (CANDIDATE / "ui" / "styles.css").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src" / "runtime.rs").read_text(encoding="utf-8")
    config = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    capability = json.loads((CANDIDATE / "capabilities" / "main.json").read_text(encoding="utf-8"))
    commands = ["capture_record", "get_today", "runtime_status"]
    results = [
        check("RW-S001", "data-tooltip" in app and "navButton" in app and "<em>${label}</em>" not in app, "M003: source has icon-only rail buttons with hover/focus tooltip, not permanent rail labels"),
        check("RW-S002", all(token in css for token in ["grid-template-columns: 92px", "width: 52px", "height: 52px", "width: 56px", "height: 56px", ".rail-button::after"]), "M003: P3-116 rail scale and tooltip relationship are explicit in the candidate CSS"),
        check("RW-S003", all(token in css for token in [".identity.user { color: #287157", ".identity.observation { color: #655392", ".identity.inference { color: #8d6428", ".identity.decision { color: #3e74a9"]), "M003/M004: mint user-confirmed, lilac observation, amber inference-candidate, and blue decision identity mapping"),
        check("RW-S004", all(token in css for token in [".focus-card { min-height: 406px", ".workspace { min-width: 0; padding: 42px", "font-size: clamp(43px,4.2vw,58px)", "padding: clamp(24px,2.5vw,32px)"]), "M004: greeting-led Today shell uses restored P3-116 card scale, type and generous whitespace"),
        check("RW-S005", all(token in css for token in [".composer { position: fixed", "left: 120px", "width: min(720px", ".ai-panel { position: fixed", "width: min(430px"]), "M003/M008: persistent Global AI bar and contextual right panel preserve frozen spatial relation"),
        check("RW-S006", all(token in css for token in ["@media (max-width: 980px)", "@media (max-width: 740px)", "grid-template-columns: 1fr", "left: 76px"]), "M009: same DOM has desktop and 700px responsive rules without a second renderer"),
        check("RW-S007", all(token in app for token in ["Today · Person", "现在的我", "Context Detail", "Memory Detail", "Identity", "Understanding", "Derivation", "Evidence", "Source"]), "M004-M007: Person-first pages and provenance layers remain in the same candidate"),
        check("RW-S008", "generate_handler![capture_record, get_today, runtime_status]" in runtime and all(runtime.count(name) >= 2 and name in app for name in commands), "M011-M015: unchanged exact three-command Tauri boundary and renderer bridge"),
        check("RW-S009", "/private/tmp/lifeos-p3-121-combined-v1" in runtime and all(token not in runtime for token in ["Command::new", "reqwest", "ureq", "tokio::net", "FileDialog"]), "M016-M018: task-local offline runtime root and static-close of process/network/dialog routes"),
        check("RW-S010", capability["permissions"] == [] and config["identifier"] == "local.lifeos.p3-121" and config["app"]["windows"][0]["width"] == 1280 and config["app"]["windows"][0]["height"] == 1024, "M009/M019: P3-121 identity, default viewport request, and empty direct permission set"),
    ]
    fixed = [
        WORKSPACE / "tasks" / "LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md",
        WORKSPACE / "tasks" / "LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md",
        WORKSPACE / "tasks" / "LIFEOS-P3-121_source_allowlist.md",
        WORKSPACE / "prototypes" / "LIFEOS-P3-116" / "visual_contract.json",
        WORKSPACE / "prototypes" / "LIFEOS-P3-116" / "interaction_contract.md",
        WORKSPACE / "prototypes" / "LIFEOS-P3-116" / "styles.css",
        WORKSPACE / "reviews" / "LIFEOS-P3-121_pm_review.md",
    ]
    OUT.joinpath("static").mkdir(parents=True, exist_ok=True)
    OUT.joinpath("preflight").mkdir(parents=True, exist_ok=True)
    payload = {
        "task": "LIFEOS-P3-121", "kind": "rework-1-static-visual-contract",
        "result": "PASS" if all(item["result"] == "PASS" for item in results) else "FAIL",
        "checks": results,
        "candidate_files": {str(path.relative_to(CANDIDATE)): digest(path) for path in sorted(CANDIDATE.rglob("*")) if path.is_file() and "target" not in path.parts},
    }
    preflight = {
        "task": "LIFEOS-P3-121", "kind": "rework-1-fixed-inputs",
        "frozen_abf_sha256_expected": "b5d3597a5460983ffda923aa65f9aa23218dc1aa6730a171b0183e5062c53a03",
        "inputs": {str(path.relative_to(WORKSPACE)): digest(path) for path in fixed},
        "initial_evidence_preserved_read_only": "evidence/actual_app and evidence/manifest were not targets of this runner",
        "pilot_access": "not performed",
    }
    preflight["frozen_abf_sha256_actual"] = preflight["inputs"]["tasks/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md"]
    preflight["result"] = "PASS" if preflight["frozen_abf_sha256_actual"] == preflight["frozen_abf_sha256_expected"] else "FAIL"
    (OUT / "static" / "visual-contract.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "preflight" / "fixed-inputs.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"P3-121-REWORK-1: {payload['result']} visual={sum(row['result'] == 'PASS' for row in results)}/{len(results)} preflight={preflight['result']}")
    return 0 if payload["result"] == "PASS" and preflight["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
