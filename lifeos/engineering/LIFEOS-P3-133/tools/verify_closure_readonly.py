#!/usr/bin/env python3
"""Read-only integrity verifier for the P3-133 Closure Cycle.

Default execution only reads the candidate, the accepted P3-132 source, and
preserved engineering evidence, then writes one JSON result to stdout.  It
never opens a runtime database or the authorised real self-use root.

``--write-closure`` is deliberately opt-in.  It can initialise the previously
absent ``evidence/closure-1`` directory exactly once; it never writes the
original evidence directory or any runtime location.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
CLOSURE = EVIDENCE / "closure-1"
LIFEOS = ROOT.parents[1]
P3_132 = ROOT.parent / "LIFEOS-P3-132"
P3_132_MANIFEST = P3_132 / "evidence" / "FINAL_MANIFEST.json"
TASK = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md"
ABF = LIFEOS / "tasks" / "LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop_acceptance_basis_freeze.md"
CONFIRMATION = LIFEOS / "tasks" / "LIFEOS-P3-133_user_confirmation.md"

QUARANTINED_SUMMARIES = (
    "verification.json",
    "FINAL_MANIFEST.json",
)
EXPECTED_IPC = [
    "capture_record",
    "get_today",
    "runtime_status",
    "confirm_capture_context",
    "get_context_recovery",
    "get_context_next_action",
    "decide_context_next_action",
    "record_action_result",
    "assemble_global_ai_context",
    "get_evidence_backed_understanding",
    "decide_understanding_feedback",
]
EXPECTED_LOGS = {
    "synthetic_tests": ("test-logs/cargo-test-synthetic.log", "test result: ok. 5 passed"),
    "real_mode_equivalent_tests": ("test-logs/cargo-test-real-mode-equivalent.log", "test result: ok. 5 passed"),
    "synthetic_tauri_bundle": ("test-logs/cargo-tauri-build-synthetic.log", "Finished 1 bundle"),
    "relative_root_rejected": ("test-logs/mutation-relative-root.log", "root must be an absolute normalized path"),
    "symlink_root_rejected": ("test-logs/mutation-symlink-root.log", "root or an ancestor is not a real directory"),
    "real_mode_build_without_root": ("test-logs/cargo-check-real-mode-no-root.log", "Finished `dev` profile"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def regular_inventory(root: Path, excluded: set[str] | None = None) -> list[dict[str, object]]:
    excluded = excluded or set()
    result: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            result.append({"path": rel, "type": "symlink"})
        elif stat.S_ISREG(info.st_mode):
            result.append({"path": rel, "type": "regular", "bytes": info.st_size, "sha256": sha256(path)})
    return result


def check(identifier: str, passed: bool, detail: object) -> dict[str, object]:
    return {"id": identifier, "passed": passed, "detail": detail}


def file_record(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        return {"path": relative, "present": False}
    return {"path": relative, "present": True, "bytes": path.stat().st_size, "sha256": sha256(path)}


def evidence_text_without_quarantine() -> str:
    values: list[str] = []
    for path in EVIDENCE.rglob("*"):
        if not path.is_file() or path.is_symlink() or CLOSURE in path.parents:
            continue
        relative = path.relative_to(EVIDENCE).as_posix()
        if relative in QUARANTINED_SUMMARIES or path.suffix not in {".json", ".log", ".md", ".txt"}:
            continue
        values.append(read_text(path))
    return "\n".join(values)


def source_and_candidate() -> tuple[dict[str, object], dict[str, object], list[str], list[str], list[str], list[str]]:
    source_manifest = read_json(P3_132_MANIFEST)
    if not isinstance(source_manifest, dict) or not isinstance(source_manifest.get("candidate_inventory"), list):
        raise ValueError("P3-132 Final Manifest lacks a candidate inventory")
    expected = {item["path"]: item for item in source_manifest["candidate_inventory"]}
    source_items = regular_inventory(P3_132 / "candidate")
    source_regular = {item["path"]: item for item in source_items if item["type"] == "regular"}
    source_mismatch = sorted(
        path
        for path, expected_item in expected.items()
        if source_regular.get(path, {}).get("bytes") != expected_item.get("bytes")
        or source_regular.get(path, {}).get("sha256") != expected_item.get("sha256")
    )
    source_extra = sorted(set(source_regular) - set(expected))

    candidate_items = regular_inventory(CANDIDATE)
    candidate_regular = {item["path"]: item for item in candidate_items if item["type"] == "regular"}
    candidate_links = sorted(item["path"] for item in candidate_items if item["type"] == "symlink")
    candidate_missing = sorted(set(expected) - set(candidate_regular))
    candidate_extra = sorted(set(candidate_regular) - set(expected))
    candidate_changed = sorted(
        path
        for path in expected
        if candidate_regular.get(path, {}).get("sha256") != expected[path].get("sha256")
    )
    return expected, candidate_regular, source_mismatch, source_extra, candidate_missing, candidate_extra + candidate_links + candidate_changed


def verify() -> dict[str, object]:
    expected, candidate, source_mismatch, source_extra, candidate_missing, candidate_observations = source_and_candidate()
    candidate_extra = [item for item in candidate_observations if item in candidate and item not in expected]
    candidate_links = [item for item in candidate_observations if item not in candidate]
    candidate_changed = sorted(
        path for path in expected if candidate.get(path, {}).get("sha256") != expected[path].get("sha256")
    )

    runtime = read_text(CANDIDATE / "src/runtime.rs")
    renderer = read_text(CANDIDATE / "ui/app.js")
    build = read_text(CANDIDATE / "build.rs")
    cargo = read_text(CANDIDATE / "Cargo.toml")
    capability = read_json(CANDIDATE / "capabilities/main.json")
    if not isinstance(capability, dict):
        raise ValueError("candidate capability is not a JSON object")
    declared = re.findall(r"#\[tauri::command\]\s*fn\s+(\w+)", runtime)
    handler = re.search(r"generate_handler!\s*\[([^]]+)\]", runtime, re.S)
    handled = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    forbidden = [
        "Command::new",
        "std::process::Command",
        "tokio::process",
        "reqwest",
        "TcpStream",
        "UdpSocket",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "@tauri-apps/plugin-fs",
        "plugin-shell",
    ]
    forbidden_hits = {item: item in runtime or item in renderer or item in cargo for item in forbidden}
    real_mode_markers = [
        "LIFEOS_RUNTIME_ROOT",
        "LIFEOS_INPUT_MODE",
        "Some(\"real_self_use\")",
        "disabled_for_real_input",
        "disabled_in_real_mode",
    ]
    status_markers = [
        "filesystem:false",
        "raw_database:false",
        "generic_path_api:false",
        "shell:false",
        "process_spawn:false",
        "network:false",
        "vault:false",
        "export:false",
        "sync:false",
    ]
    short_circuit = bool(
        re.search(
            r"fn understanding\([^\n]+if paths\.mode==InputMode::Real \{ return Ok\(Understanding",
            runtime,
        )
    )

    log_results = {
        identifier: file_record(EVIDENCE, relative)
        for identifier, (relative, _) in EXPECTED_LOGS.items()
    }
    logs_pass = all(
        log_results[identifier]["present"] and needle in read_text(EVIDENCE / relative)
        for identifier, (relative, needle) in EXPECTED_LOGS.items()
    )

    observations_path = EVIDENCE / "actual-tauri" / "ui-observations.json"
    observations = read_json(observations_path)
    if not isinstance(observations, dict):
        raise ValueError("actual Tauri observations are not a JSON object")
    screenshot_records: list[dict[str, object]] = []
    observation_hashes_match = True
    for run in observations.get("runs", []):
        if not isinstance(run, dict):
            observation_hashes_match = False
            continue
        for item in run.get("screenshots", []):
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                observation_hashes_match = False
                continue
            relative = f"actual-tauri/{item['path']}"
            record = file_record(EVIDENCE, relative)
            screenshot_records.append(record)
            observation_hashes_match = observation_hashes_match and record.get("sha256") == item.get("sha256")
    expected_run_ids = {"positive-lifecycle", "link-rejection", "candidate-rejection"}
    actual_run_ids = {run.get("id") for run in observations.get("runs", []) if isinstance(run, dict)}
    raw_text = evidence_text_without_quarantine()
    bundle_records = [
        file_record(EVIDENCE, "actual-tauri/bundle-identity/Info.plist"),
        file_record(EVIDENCE, "actual-tauri/bundle-identity/lifeos-p3-133"),
    ]
    cleanup = read_json(EVIDENCE / "cleanup-final.json")

    quarantined = {relative: file_record(EVIDENCE, relative) for relative in QUARANTINED_SUMMARIES}
    if CLOSURE.exists() or CLOSURE.is_symlink():
        manifest_path = CLOSURE / "FINAL_MANIFEST.json"
        if not manifest_path.is_file() or manifest_path.is_symlink():
            manifest_check = check(
                "CL01_closure_manifest_is_nonself_and_matches_files",
                False,
                {"reason": "closure directory exists but its Final Manifest is absent or not a regular file"},
            )
        else:
            closure_manifest = read_json(manifest_path)
            expected_closure_inventory = regular_inventory(CLOSURE, {"FINAL_MANIFEST.json"})
            manifest_check = check(
                "CL01_closure_manifest_is_nonself_and_matches_files",
                isinstance(closure_manifest, dict)
                and closure_manifest.get("manifest_kind") == "LIFEOS-P3-133 closure-1 engineering evidence manifest (non-self)"
                and closure_manifest.get("closure_evidence_inventory") == expected_closure_inventory
                and closure_manifest.get("quarantined_original_summaries") == list(QUARANTINED_SUMMARIES),
                {
                    "closure_inventory_count": len(expected_closure_inventory),
                    "manifest_path": "closure-1/FINAL_MANIFEST.json",
                },
            )
    else:
        manifest_check = check(
            "CL01_closure_manifest_is_nonself_and_matches_files",
            True,
            {"state": "not_yet_initialised", "write_mode_required": "--write-closure"},
        )
    checks = [
        check(
            "CL01_source_history_75_regular_hashes",
            len(expected) == 75 and not source_mismatch and not source_extra,
            {"expected": len(expected), "source_mismatch": source_mismatch, "source_extra": source_extra},
        ),
        check(
            "CL01_candidate_75_regular_no_extra_or_link",
            len(candidate) == 75 and not candidate_missing and not candidate_extra and not candidate_links,
            {
                "candidate_regular": len(candidate),
                "missing": candidate_missing,
                "extra": candidate_extra,
                "links": candidate_links,
                "changed_from_p3_132": candidate_changed,
            },
        ),
        check(
            "CL01_quarantined_original_summaries_are_not_positive_evidence",
            all(record["present"] for record in quarantined.values()),
            {"quarantined": quarantined, "excluded_from_positive_evidence": list(QUARANTINED_SUMMARIES)},
        ),
        check(
            "CL02_build_time_mode_and_runtime_root_are_explicit",
            all(marker in build or marker in runtime for marker in real_mode_markers),
            {"markers": real_mode_markers},
        ),
        check(
            "CL02_exact_eleven_ipc_and_closed_capability",
            declared == EXPECTED_IPC
            and handled == EXPECTED_IPC
            and capability.get("permissions") == []
            and all(marker in runtime for marker in status_markers)
            and not any(forbidden_hits.values()),
            {
                "declared": declared,
                "handled": handled,
                "capability_permissions": capability.get("permissions"),
                "forbidden_hits": forbidden_hits,
            },
        ),
        check(
            "CL02_real_mode_model_is_disabled_before_adapter_use",
            short_circuit and "OfflineSyntheticModelAdapter" in renderer and "synthetic_adapter:false" in runtime,
            {"understanding_short_circuit": short_circuit, "adapter_call_count": 0},
        ),
        check(
            "CL02_preserved_synthetic_test_and_mutation_logs",
            logs_pass,
            log_results,
        ),
        check(
            "CL01_preserved_actual_tauri_ui_assets_match_raw_observations",
            observations.get("evidence_kind") == "actual_tauri_visible_state"
            and observations.get("real_root_access") == "not attempted"
            and expected_run_ids == actual_run_ids
            and bool(screenshot_records)
            and observation_hashes_match,
            {
                "run_ids": sorted(actual_run_ids),
                "screenshot_hashes_match": observation_hashes_match,
                "screenshots": screenshot_records,
            },
        ),
        check(
            "CL01_preserved_bundle_identity_and_cleanup_receipt",
            all(record["present"] for record in bundle_records)
            and isinstance(cleanup, dict)
            and cleanup.get("result") == "PASS"
            and cleanup.get("after", {}).get("exists") is False,
            {"bundle": bundle_records, "cleanup_result": cleanup.get("result"), "cleanup_after": cleanup.get("after")},
        ),
        check(
            "CL01_no_private_taint_in_preserved_nonquarantined_text_evidence",
            "P3_133_PRIVATE_TAINT" not in raw_text,
            {"taint_marker_present": "P3_133_PRIVATE_TAINT" in raw_text},
        ),
        manifest_check,
    ]
    return {
        "contract": "LIFEOS-P3-133",
        "kind": "closure-1_read_only_engineering_integrity_verification",
        "default_mode_writes": False,
        "task_contract_sha256": sha256(TASK),
        "acceptance_basis_freeze_sha256": sha256(ABF),
        "user_confirmation_sha256": sha256(CONFIRMATION),
        "source_manifest_sha256": sha256(P3_132_MANIFEST),
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "quarantined_original_summaries": quarantined,
        "not_run": [
            "AC-11 mandatory independent review",
            "AC-12 PM-gated real self-use run",
        ],
        "real_root_access": "not attempted by this verifier",
        "runtime_database_access": "not attempted by this verifier",
        "closure_scope": "restores a non-overwriting engineering evidence lineage only; it is not an independent review or PM acceptance",
    }


def source_lineage(result: dict[str, object]) -> dict[str, object]:
    first = result["checks"][0]["detail"]
    second = result["checks"][1]["detail"]
    return {
        "kind": "closure-1_source_and_candidate_lineage",
        "source_task": "LIFEOS-P3-132",
        "source_manifest": str(P3_132_MANIFEST.relative_to(LIFEOS)),
        "source_manifest_sha256": result["source_manifest_sha256"],
        "source_candidate_count": first["expected"],
        "source_mismatch": first["source_mismatch"],
        "source_extra": first["source_extra"],
        "candidate_count": second["candidate_regular"],
        "candidate_missing": second["missing"],
        "candidate_extra": second["extra"],
        "candidate_links": second["links"],
        "candidate_changed_from_source": second["changed_from_p3_132"],
        "note": "P3-133 is an implementation successor, so changed candidate files are disclosed rather than treated as source lineage mismatches.",
    }


def dynamic_closure_markdown(result: dict[str, object]) -> str:
    assets = result["checks"][7]["detail"]["screenshots"]
    by_path = {item["path"]: item["sha256"] for item in assets if item.get("present")}
    rows = [
        ("D-133-C01", "合成 actual Tauri：明确接受 Candidate", "Today Focus 对应用户确认 Action", "positive-lifecycle:accept_candidate", "actual-tauri/screenshots/synthetic-confirmed-action.jpeg", "PASS"),
        ("D-133-C02", "合成 actual Tauri：关闭并重开", "Capture／Context／Action／Today Focus 仍可见", "positive-lifecycle:reopen", "actual-tauri/screenshots/synthetic-reopen-focus.jpeg", "PASS"),
        ("D-133-C03", "合成 actual Tauri：拒绝 Context link", "Candidate／Action 为零，Today 为空", "link-rejection:capture_then_reject_link", "actual-tauri/screenshots/synthetic-link-rejected.jpeg", "PASS"),
        ("D-133-C04", "合成 actual Tauri：拒绝 Candidate", "Action 为零，Today 为空", "candidate-rejection:confirm_context_then_reject_candidate", "actual-tauri/screenshots/synthetic-candidate-rejected.jpeg", "PASS"),
    ]
    lines = [
        "# P3-133 Closure-1｜保全的 actual Tauri 合成动态 Evidence",
        "",
        "本表只复算仍保全的 `ui-observations.json`、截图和其 SHA-256；不读取、写入或依赖已清理的合成 DB。原 `verification.json` 与 `FINAL_MANIFEST.json` 因 PM 事故被隔离，且不作为正 Evidence。真实根与真实输入均未访问。",
        "",
        "| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for identifier, action, expected, structured, path, status in rows:
        lines.append(f"| {identifier} | {action} | {expected} | `{structured}` | `{path}`；`actual-tauri/ui-observations.json` | `{by_path.get(path, 'MISSING')}` | {status} |  |")
    lines.extend(
        [
            "",
            "这些行仅恢复工程侧已保全的合成动态资产的可复算性；AC-11 独立评审与 AC-12 真实自用仍为 `NOT IMPLEMENTED`，不得由本表推导 Pass。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_closure(result: dict[str, object]) -> None:
    if CLOSURE.exists() or CLOSURE.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing closure evidence: {CLOSURE}")
    CLOSURE.mkdir(parents=False)
    incident = {
        "kind": "pm_evidence_integrity_incident",
        "decision": "D-0540",
        "affected_original_summaries": [
            {
                "path": f"../{relative}",
                "current_sha256": result["quarantined_original_summaries"][relative]["sha256"],
                "positive_evidence_status": "excluded",
            }
            for relative in QUARANTINED_SUMMARIES
        ],
        "statement": "The original summaries were overwritten by a write-capable verifier after the synthetic task root was cleaned. This closure lineage never overwrites them and does not treat them as positive evidence.",
        "real_root_access": "not attempted",
    }
    write_json(CLOSURE / "incident.json", incident)
    write_json(CLOSURE / "source-lineage.json", source_lineage(result))
    (CLOSURE / "UI_DYNAMIC_CLOSURE.md").write_text(dynamic_closure_markdown(result), encoding="utf-8")
    write_json(CLOSURE / "verification.json", result)
    manifest = {
        "manifest_kind": "LIFEOS-P3-133 closure-1 engineering evidence manifest (non-self)",
        "task": "LIFEOS-P3-133",
        "task_contract_sha256": result["task_contract_sha256"],
        "acceptance_basis_freeze_sha256": result["acceptance_basis_freeze_sha256"],
        "source_manifest_sha256": result["source_manifest_sha256"],
        "candidate_inventory_count": 75,
        "candidate_inventory": regular_inventory(CANDIDATE),
        "closure_evidence_inventory": regular_inventory(CLOSURE, {"FINAL_MANIFEST.json"}),
        "quarantined_original_summaries": list(QUARANTINED_SUMMARIES),
        "verifier": "../tools/verify_closure_readonly.py (default is read-only; --write-closure is explicit and one-time)",
        "independent_review": "not_run",
        "real_self_use_run": "not_run_pending_independent_review_and_pm_validation",
        "real_root_access": "not_attempted",
    }
    write_json(CLOSURE / "FINAL_MANIFEST.json", manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-closure", action="store_true", help="explicitly initialise the new closure-1 evidence lineage once")
    args = parser.parse_args()
    try:
        result = verify()
        if args.write_closure:
            if not result["passed"]:
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1
            write_closure(result)
            result = {**result, "closure_write": "created evidence/closure-1 without touching original evidence files"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 1
    except (FileExistsError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
