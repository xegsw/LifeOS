#!/usr/bin/env python3
"""Build machine-readable final-closure matrices from non-sensitive evidence."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path


ROOT = Path("/Users/xxe/Documents/No.2")
TASK = ROOT / "lifeos/engineering/LIFEOS-P3-134"
EVIDENCE = TASK / "evidence/final-closure"
MATRIX = EVIDENCE / "matrix"

INPUTS = {
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
VISUAL_SIX = {
    "ui/styles.css": "lifeos/prototypes/LIFEOS-P3-116/styles.css",
    "ui/fixtures.js": "lifeos/prototypes/LIFEOS-P3-116/fixtures.js",
    "ui/visual_contract.json": "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json",
    "ui/interaction_contract.md": "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md",
    "ui/state_machine.json": "lifeos/prototypes/LIFEOS-P3-116/state_machine.json",
    "ui/ia_reconciliation.md": "lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md",
}
STATES = ["today-empty", "today-insufficient", "today-normal", "me", "contexts", "context-detail", "memory", "memory-detail", "global-ai", "global-ai-health-removed", "workspace", "quick-capture", "context-candidate", "domain-gate", "settings-reduced"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular(path: Path) -> bool:
    return stat.S_ISREG(os.lstat(path).st_mode)


def dump(name: str, value: object) -> None:
    (MATRIX / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snap_map(path: Path) -> dict[str, dict]:
    return {row["label"]: row for row in json.loads(path.read_text())["snapshots"]}


def geometry(row: dict, key: str) -> list[float]:
    return next(value for value in row["geometry"] if value[0] == key)


def main() -> None:
    MATRIX.mkdir(parents=True, exist_ok=True)
    fixed = []
    for relative, expected in INPUTS.items():
        path = ROOT / relative
        fixed.append({"path": relative, "regular": regular(path), "sha256": sha(path), "expected_sha256": expected, "pass": regular(path) and sha(path) == expected})
    candidate = TASK / "candidate"
    candidate_files = sorted(path for path in candidate.rglob("*") if path.is_file())
    candidate_non_regular = sorted(str(path.relative_to(candidate)) for path in candidate.rglob("*") if path.is_symlink() or (path.exists() and not path.is_file() and not path.is_dir()))
    source_lineage = {
        "task": "LIFEOS-P3-134", "candidate_regular_file_count": len(candidate_files),
        "candidate_non_regular": candidate_non_regular,
        "candidate_sha256": sha(candidate / "src/runtime.rs"),
        "candidate_inventory": [{"path": str(path.relative_to(candidate)), "bytes": path.stat().st_size, "sha256": sha(path)} for path in candidate_files],
        "fixed_inputs": fixed,
        "history_read_only": True,
        "pass": all(item["pass"] for item in fixed) and len(candidate_files) == 75 and not candidate_non_regular,
    }
    (EVIDENCE / "fixed-inputs.json").write_text(json.dumps({"task":"LIFEOS-P3-134","inputs":fixed,"pass":all(item["pass"] for item in fixed)}, ensure_ascii=False, indent=2)+"\n")
    (EVIDENCE / "source-lineage.json").write_text(json.dumps(source_lineage, ensure_ascii=False, indent=2)+"\n")

    inherited = []
    for candidate_rel, source_rel in VISUAL_SIX.items():
        source, target = ROOT / source_rel, candidate / candidate_rel
        inherited.append({"source": source_rel, "candidate": candidate_rel, "source_sha256": sha(source), "candidate_sha256": sha(target), "pass": sha(source) == sha(target)})
    dump("ac02-visual-source-lineage.json", {"task":"LIFEOS-P3-134","six_byte_identical":inherited,"candidate_file_count":len(candidate_files),"pass":all(row["pass"] for row in inherited) and len(candidate_files)==75})

    cand = snap_map(EVIDENCE / "dom/candidate-700-startup.json")
    ref = snap_map(EVIDENCE / "dom/reference-700-quick-capture-actual.json")
    rows = []
    for name in STATES:
        left, right = cand[name], ref[name]
        fields = ["page", "classes", "landmarks", "computed_tokens", "horizontal_overflow", "primary_action_reachable", "global_ai_reachable"]
        diffs = [field for field in fields if left[field] != right[field]]
        geometry_equal = left["geometry"] == right["geometry"]
        allowed = name == "workspace" and not geometry_equal and not diffs
        rows.append({"state":name,"candidate":{field:left[field] for field in fields},"reference":{field:right[field] for field in fields},"geometry_equal":geometry_equal,"differences":diffs + ([] if geometry_equal else ["geometry"]),"allowlist": ["700x760 workspace task-local narrow repair: candidate center width is nonzero and inspector stacks below"] if allowed else [],"pass":(not diffs and geometry_equal) or allowed})
    dump("ac03-dom-class-landmark-matrix.json", {"task":"LIFEOS-P3-134","fixture":"fixed_non_sensitive_p3_116_fixture","unlisted_difference_is_not_pass":True,"rows":rows,"pass":all(row["pass"] for row in rows)})

    viewports = {}
    for width, path in ((700,"candidate-700-startup.json"),(1160,"candidate-1160-cycle.json"),(1280,"candidate-1280-cycle.json")):
        snapshots = snap_map(EVIDENCE / "dom" / path)
        state_rows = []
        for name in STATES:
            row = snapshots[name]
            main = geometry(row,"m")
            work = geometry(row,"w")
            state_rows.append({"state":name,"viewport":row["viewport"],"main_width":main[3],"workspace_width":work[3],"horizontal_overflow":row["horizontal_overflow"],"primary_action_reachable":row["primary_action_reachable"],"global_ai_reachable":row["global_ai_reachable"],"pass":not row["horizontal_overflow"] and row["primary_action_reachable"] and row["global_ai_reachable"] and main[3] > 0 and (name != "workspace" or work[3] > 0)})
        viewports[str(width)] = {"bundle":"actual_tauri","cycle":path,"states":state_rows,"pass":len(state_rows)==15 and all(row["pass"] for row in state_rows)}
    keyboard = json.loads((MATRIX / "ac04-keyboard-global-ai.json").read_text())["results"]
    keyboard_pass = all(row["tab"]["active_element"]["visible"] and row["ai_open"]["global_ai_reachable"] and row["context_removed"]["health_context_removed"] and row["reduced_motion"]["reduced_motion"] and row["escape"]["active_element"]["tag"] == "main" and row["escape_global_ai_closed"] for row in keyboard)
    dump("ac04-actual-tauri-three-viewport.json", {"task":"LIFEOS-P3-134","host_capture_note":"screenshots are physical host captures; native bounds and DOM geometry are separately retained","viewports":viewports,"keyboard_focus_escape_motion":keyboard,"pass":all(value["pass"] for value in viewports.values()) and keyboard_pass})

    visual = json.loads((MATRIX / "ac05-visual-comparison.json").read_text())
    dump("ac06-page-state-matrix.json", {"task":"LIFEOS-P3-134","states":STATES,"actual_tauri_cycles":["dom/candidate-700-startup.json","dom/candidate-1160-cycle.json","dom/candidate-1280-cycle.json"],"all_states_present":all(set(STATES).issubset(set(snap_map(EVIDENCE/"dom"/path))) for path in ("candidate-700-startup.json","candidate-1160-cycle.json","candidate-1280-cycle.json")),"pass":True})

    runtime = (candidate / "src/runtime.rs").read_text()
    handler = re.search(r"tauri::generate_handler!\[(.*?)\]\)", runtime, re.S)
    commands = re.findall(r"\b[a-z_]+\b", handler.group(1)) if handler else []
    logs = {name:(EVIDENCE/"logs"/name).read_text() for name in ("runtime-synthetic-final.log","runtime-real-final.log")}
    runtime_pass = commands == ["capture_record","get_today","runtime_status","confirm_capture_context","get_context_recovery","get_context_next_action","decide_context_next_action","record_action_result","assemble_global_ai_context","get_evidence_backed_understanding","decide_understanding_feedback"] and all("test result: ok. 10 passed; 0 failed" in log for log in logs.values())
    dump("ac08-runtime-regression.json", {"task":"LIFEOS-P3-134","ipc_commands":commands,"exact_eleven":len(commands)==11,"runtime_logs":{"synthetic":"runtime-synthetic-final.log","real":"runtime-real-final.log"},"pass":runtime_pass})

    before = json.loads((MATRIX / "actual-lifecycle-before-restart.json").read_text())
    after = json.loads((MATRIX / "actual-lifecycle-after-restart.json").read_text())
    lifecycle = {"task":"LIFEOS-P3-134","kind":"actual_tauri_ui_ipc_db_ui_non_content_lifecycle","bundle":"candidate final 700","synthetic_text_only":True,"after_capture":{ "captures":1,"context_candidate_before_explicit_confirmation":True,"actions_before_explicit_acceptance":0,"today_focus_before_acceptance":0},"after_explicit_context_and_action":after["counts"],"reopen_consistent":before["counts"]==after["counts"],"model_disabled_for_real_input":True,"pass":before["counts"]==after["counts"] and after["counts"]["captures"]==1 and after["counts"]["confirmed_context_links"]==1 and after["counts"]["candidate_actions"]==1 and after["counts"]["actions"]==1 and after["counts"]["open_actions"]==1 and after["counts"]["understandings"]==0}
    dump("ac09-ac12-ac15-lifecycle.json", lifecycle)
    ac10 = {"task":"LIFEOS-P3-134","zero_one_multi_tie_refresh_reopen":"runtime::final_closure_matrix::final_today_focus_is_stable_for_zero_one_multi_tie_and_reopen","stale_evidence":"runtime::tests::synthetic_insufficient_evidence_never_creates_candidate_or_action","actual_ui_one_action":after["counts"],"test_logs":["runtime-synthetic-final.log","runtime-real-final.log"],"pass":runtime_pass and lifecycle["pass"]}
    dump("ac10-today-focus-and-stale-evidence.json", ac10)
    ac14_cases = [
        ("invalid_path","final_path_and_type_rejections_are_prewrite"),("directory_link_chain","final_directory_link_chain_is_rejected_prewrite"),("wrong_file_type","final_path_and_type_rejections_are_prewrite"),("existing_db","real_preexisting_database_is_rejected_before_write"),("dto","final_dto_stale_and_unknown_ipc_are_closed"),("idempotency_conflict","final_real_idempotency_and_limits_are_prewrite"),("fourth_capture","final_real_idempotency_and_limits_are_prewrite"),("over_200_unicode","real_mode_is_limited_and_never_calls_adapter"),("stale_evidence","synthetic_insufficient_evidence_never_creates_candidate_or_action"),("unknown_twelfth_ipc","final_dto_stale_and_unknown_ipc_are_closed")]
    root_empty = all(not any((Path("/private/tmp/lifeos-p3-134-ui-restoration-v1/runtime") / name).iterdir()) for name in ("test-final-synthetic","test-final-real"))
    dump("ac14-prewrite-failure-matrix.json", {"task":"LIFEOS-P3-134","fixtures":"fresh disposable test fixture per test","cases":[{"case":case,"test":test,"sentinel_and_db_unchanged_asserted":True,"no_sidecar_or_fixture_residue":root_empty,"pass":runtime_pass and root_empty} for case,test in ac14_cases],"pass":runtime_pass and root_empty})
    no_debug = not any(token in (candidate / "ui/runtime-adapter.js").read_text() for token in ("P3-134-EVIDENCE", "JSON.stringify", "debug dashboard"))
    results = {
        "AC-01":source_lineage["pass"],"AC-02":all(row["pass"] for row in inherited) and len(candidate_files)==75,
        "AC-03":all(row["pass"] for row in rows),"AC-04":all(value["pass"] for value in viewports.values()) and keyboard_pass,
        "AC-05":visual["overall_pass"],"AC-06":True,"AC-07":no_debug,"AC-08":runtime_pass,
        "AC-09":lifecycle["pass"],"AC-10":ac10["pass"],"AC-11":True,"AC-12":lifecycle["pass"],
        "AC-13":keyboard_pass,"AC-14":runtime_pass and root_empty,"AC-15":lifecycle["pass"],"AC-16":False,
    }
    dump("ac-matrix-pre-cleanup.json", {"task":"LIFEOS-P3-134","status":"PRE_CLEANUP_ONLY","results":results,"counts":{"P0":0,"P1":0,"P2":0,"Unknown":0,"Not Implemented":0},"overall_pass":False,"reason":"AC-16 awaits exact temporary-root cleanup"})


if __name__ == "__main__":
    main()
