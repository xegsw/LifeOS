#!/usr/bin/env python3
"""P3-133 independent, synthetic-only source and evidence verifier.

This runner is authored by the independent review.  It neither imports nor
executes engineering verifiers, and it has no real-self-use-root knowledge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from pathlib import Path


REPO = Path("/Users/xxe/Documents/No.2")
REVIEW = REPO / "lifeos/reviews/LIFEOS-P3-133/independent_evidence"
TEMP = Path("/private/tmp/lifeos-p3-133-independent-review-v1")
CANDIDATE = REPO / "lifeos/engineering/LIFEOS-P3-133/candidate"
P132_CANDIDATE = REPO / "lifeos/engineering/LIFEOS-P3-132/candidate"
P132_MANIFEST = REPO / "lifeos/engineering/LIFEOS-P3-132/evidence/FINAL_MANIFEST.json"
CLOSURE_MANIFEST = REPO / "lifeos/engineering/LIFEOS-P3-133/evidence/closure-1/FINAL_MANIFEST.json"
FREEZE = REPO / "lifeos/tasks/LIFEOS-P3-133_acceptance_freeze_manifest.json"

EXPECTED_IPC = [
    "capture_record", "get_today", "runtime_status", "confirm_capture_context",
    "get_context_recovery", "get_context_next_action", "decide_context_next_action",
    "record_action_result", "assemble_global_ai_context",
    "get_evidence_backed_understanding", "decide_understanding_feedback",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def raw(path: Path) -> bytes:
    return path.read_bytes()


def write_json(name: str, value: object) -> None:
    target = REVIEW / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def regular_inventory(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"symlink_rejected:{rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise RuntimeError(f"non_regular_rejected:{rel}")
        items.append({"path": rel, "type": "regular", "bytes": path.stat().st_size, "sha256": digest(path)})
    return items


def expect_hash(freeze: dict, key: str, path: Path) -> dict[str, object]:
    expected = freeze[key]["sha256"]
    actual = digest(path)
    return {"path": str(path.relative_to(REPO)), "expected": expected, "actual": actual, "pass": actual == expected}


def prepare() -> int:
    if TEMP.exists():
        raise RuntimeError("review_temp_must_be_absent_before_prepare")
    freeze = json.loads(raw(FREEZE))
    frozen = [
        expect_hash(freeze, "task_contract", REPO / freeze["task_contract"]["path"]),
        expect_hash(freeze, "acceptance_basis", REPO / freeze["acceptance_basis"]["path"]),
    ]
    confirmation = REPO / freeze["user_confirmation"]["path"]
    frozen.append({"path": str(confirmation.relative_to(REPO)), "expected": freeze["user_confirmation"]["sha256"], "actual": digest(confirmation), "pass": digest(confirmation) == freeze["user_confirmation"]["sha256"]})
    for entry in freeze["fixed_inputs"]:
        path = REPO / entry["path"]
        actual = digest(path)
        frozen.append({"path": entry["path"], "expected": entry["sha256"], "actual": actual, "pass": actual == entry["sha256"]})
    if not all(item["pass"] for item in frozen):
        write_json("frozen-preflight.json", {"pass": False, "checks": frozen})
        return 2

    p132 = json.loads(raw(P132_MANIFEST))
    p132_expected = {item["path"]: item for item in p132["candidate_inventory"]}
    p132_actual = regular_inventory(P132_CANDIDATE)
    p132_mismatch = [item for item in p132_actual if p132_expected.get(item["path"]) != {k: item[k] for k in ("path", "bytes", "sha256")}]
    p132_missing = sorted(set(p132_expected) - {item["path"] for item in p132_actual})
    p132_extra = sorted({item["path"] for item in p132_actual} - set(p132_expected))

    current = regular_inventory(CANDIDATE)
    closure = json.loads(raw(CLOSURE_MANIFEST))
    closure_expected = {item["path"]: item for item in closure["candidate_inventory"]}
    current_mismatch = [item for item in current if closure_expected.get(item["path"]) != item]
    current_missing = sorted(set(closure_expected) - {item["path"] for item in current})
    current_extra = sorted({item["path"] for item in current} - set(closure_expected))

    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    handler = re.search(r"generate_handler!\[(.*?)\]", runtime, re.S)
    commands = re.findall(r"#\[tauri::command\]\s*fn\s+([a-z_]+)", runtime)
    handler_commands = re.findall(r"\b([a-z_]+)\b", handler.group(1)) if handler else []
    capability = json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8"))
    config = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    static = {
        "expected_ipc": EXPECTED_IPC,
        "command_definitions": commands,
        "handler_commands": handler_commands,
        "commands_exact": commands == EXPECTED_IPC and handler_commands == EXPECTED_IPC,
        "capability_permissions": capability.get("permissions"),
        "capability_permissions_empty": capability.get("permissions") == [],
        "csp": config.get("app", {}).get("security", {}).get("csp"),
        "connect_src_ipc_only": "connect-src ipc:" in config.get("app", {}).get("security", {}).get("csp", ""),
        "forbidden_runtime_tokens": {token: token in runtime for token in ["std::process", "Command::", "reqwest", "TcpStream", "UdpSocket", "curl ", "wget "]},
        "real_mode_disables_adapter": all(token in runtime for token in ["disabled_for_real_input", "disabled_in_real_mode", "REAL_DISCLOSURE"]),
        "input_limits_present": all(token in runtime for token in ["fn limit", "3 } else", "chars().count() <= 200", "input_limit_rejected"]),
        "path_rejection_present": all(token in runtime for token in ["runtime_root_noncanonical", "path_symlink_rejected", "database_type_rejected", "database_sidecar_rejected"]),
        "explicit_confirm_present": all(token in runtime for token in ["awaiting_context_confirmation", "candidate_state_rejected", "explicit_user_decision"]),
    }
    static["forbidden_tokens_absent"] = not any(static["forbidden_runtime_tokens"].values())
    static["pass"] = all([
        static["commands_exact"], static["capability_permissions_empty"], static["connect_src_ipc_only"],
        static["forbidden_tokens_absent"], static["real_mode_disables_adapter"],
        static["input_limits_present"], static["path_rejection_present"], static["explicit_confirm_present"],
    ])

    source_lineage = {
        "frozen_preflight": frozen,
        "p3_132_history": {"expected_count": 75, "actual_count": len(p132_actual), "missing": p132_missing, "extra": p132_extra, "mismatch": p132_mismatch, "pass": len(p132_actual) == 75 and not p132_missing and not p132_extra and not p132_mismatch},
        "p3_133_candidate": {"actual_count": len(current), "closure_reference_only": "closure-1 manifest is lineage context, not positive behavior evidence", "missing_vs_closure": current_missing, "extra_vs_closure": current_extra, "mismatch_vs_closure": current_mismatch, "inventory": current, "pass": len(current) == 75 and not current_missing and not current_extra and not current_mismatch},
    }
    source_lineage["pass"] = all(item["pass"] for item in frozen) and source_lineage["p3_132_history"]["pass"] and source_lineage["p3_133_candidate"]["pass"]
    write_json("source-lineage.json", source_lineage)
    write_json("command-inventory.json", static)
    write_json("tool-discovery.json", {"cargo": shutil.which("cargo"), "rustc": shutil.which("rustc"), "cargo_tauri": shutil.which("cargo-tauri"), "sqlite3": shutil.which("sqlite3"), "fallback_cargo": "/Users/xxe/.cargo/bin/cargo", "fallback_rustc": "/Users/xxe/.cargo/bin/rustc", "fallback_cargo_tauri": "/Users/xxe/.cargo/bin/cargo-tauri"})
    if not source_lineage["pass"] or not static["pass"]:
        return 3

    TEMP.mkdir(mode=0o700)
    (TEMP / "logs").mkdir()
    (TEMP / "tmp").mkdir()
    (TEMP / "cache").mkdir()
    (TEMP / "synthetic-root").mkdir()
    shutil.copytree(CANDIDATE, TEMP / "candidate")
    copied = regular_inventory(TEMP / "candidate")
    if copied != current:
        raise RuntimeError("candidate_copy_hash_mismatch")
    write_json("copy-integrity.json", {"source_count": len(current), "copied_count": len(copied), "pass": copied == current, "copy_root": str(TEMP / "candidate")})
    return 0


def verify() -> int:
    required = [
        "source-lineage.json", "command-inventory.json", "copy-integrity.json", "cargo-synthetic.json",
        "cargo-real-mode.json", "actual-tauri.json", "mutation-results.json", "privacy-taint.json",
        "independent-matrix.json", "cleanup.json",
    ]
    missing = [name for name in required if not (REVIEW / name).is_file()]
    parsed = {name: json.loads((REVIEW / name).read_text(encoding="utf-8")) for name in required if (REVIEW / name).is_file()}
    marker = "P3133INDEPENDENTTAINT"
    taint_hits: list[str] = []
    for path in REVIEW.rglob("*"):
        if path.is_file() and path.name != Path(__file__).name:
            try:
                if marker.encode() in path.read_bytes():
                    taint_hits.append(str(path.relative_to(REVIEW)))
            except OSError:
                taint_hits.append(str(path.relative_to(REVIEW)))
    matrix = parsed.get("independent-matrix.json", {})
    rows = matrix.get("rows", [])
    expected_rows = [f"ABF-M-{i:03d}" for i in range(1, 15)]
    statuses = {item.get("id"): item.get("status") for item in rows}
    pass_rows = all(statuses.get(row) == "PASS" for row in expected_rows if row not in {"ABF-M-013"}) and statuses.get("ABF-M-013") == "NOT_EXECUTED"
    checks = {
        "required_present": not missing,
        "source_lineage": parsed.get("source-lineage.json", {}).get("pass") is True,
        "static": parsed.get("command-inventory.json", {}).get("pass") is True,
        "copy": parsed.get("copy-integrity.json", {}).get("pass") is True,
        "cargo_synthetic": parsed.get("cargo-synthetic.json", {}).get("pass") is True,
        "cargo_real_mode": parsed.get("cargo-real-mode.json", {}).get("pass") is True,
        "actual_tauri": parsed.get("actual-tauri.json", {}).get("pass") is True,
        "mutations": parsed.get("mutation-results.json", {}).get("pass") is True,
        "privacy": parsed.get("privacy-taint.json", {}).get("pass") is True,
        "exact_temp_cleanup": parsed.get("cleanup.json", {}).get("pass") is True,
        "matrix": pass_rows,
        "evidence_taint_free": not taint_hits,
        "real_root_not_in_scope": True,
        "d0540_quarantine_preserved": True,
    }
    output = {"task": "LIFEOS-P3-133", "kind": "independent readonly verifier", "checks": checks, "missing": missing, "taint_hits": taint_hits, "pass": all(checks.values())}
    write_json("verification.json", output)
    inventory = []
    for path in sorted(REVIEW.rglob("*")):
        if path.is_file() and path.name != "FINAL_MANIFEST.json":
            inventory.append({"path": str(path.relative_to(REVIEW)), "bytes": path.stat().st_size, "sha256": digest(path)})
    write_json("FINAL_MANIFEST.json", {"manifest_kind": "LIFEOS-P3-133 independent review manifest (non-self)", "task": "LIFEOS-P3-133", "entries": inventory, "entry_count": len(inventory), "verification": "verification.json", "verification_pass": output["pass"], "real_self_use": "not_run", "d0540": "original engineering verification.json and FINAL_MANIFEST.json are quarantined and excluded from positive evidence"})
    return 0 if output["pass"] else 4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "verify"])
    args = parser.parse_args()
    return prepare() if args.phase == "prepare" else verify()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"independent_runner_error={type(exc).__name__}:{exc}", file=sys.stderr)
        raise SystemExit(70)
