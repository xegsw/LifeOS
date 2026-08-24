#!/usr/bin/env python3
"""P3-112 standalone verifier.  It deliberately does not import P3-111 tools."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / "lifeos/reviews/LIFEOS-P3-112/evidence"
SOURCE_CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-111/candidate"
INITIAL = ROOT / "lifeos/engineering/LIFEOS-P3-111/evidence"
REWORK = INITIAL / "rework-1"
SUBMITTED_VERIFIER = ROOT / "lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py"
TMP = Path("/private/tmp/lifeos-p3-112-review-v1")
EXCLUDE = {"PAYLOAD_MANIFEST.json", "MANIFEST.md", "semantic-verifier-result.json"}
MUTATIONS = {
    "missing_file": ("raw/geometry.json", "remove"),
    "hash_changed": ("raw/static-results.json", "append"),
    "cleanup_residue": ("raw/cleanup.json", "cleanup"),
    "negative_exit_zero": ("raw/negative-results.json", "negative"),
    "db_count_wrong": ("raw/fixed-lifecycle.json", "lifecycle"),
    "geometry_wrong": ("raw/geometry.json", "geometry"),
}


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path: Path) -> tuple[int, str]:
    value = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(chunk)
            value.update(chunk)
    return size, value.hexdigest()


def payload_paths(root: Path) -> set[str]:
    return {
        item.relative_to(root).as_posix()
        for item in root.rglob("*")
        if item.is_file()
        and item.name not in EXCLUDE
        and not item.relative_to(root).parts[0] == "disposable"
    }


def verify_dynamic(root: Path, errors: list[str]) -> None:
    closure = root / "UI_DYNAMIC_EVIDENCE_CLOSURE.md"
    try:
        lines = closure.read_text(encoding="utf-8").splitlines()
    except OSError:
        errors.append("dynamic-closure-unreadable")
        return
    rows: dict[str, list[str]] = {}
    for line in lines:
        if line.startswith("| D-"):
            cells = [part.strip() for part in line.split("|")[1:-1]]
            if len(cells) != 8:
                errors.append("dynamic-row-shape")
            else:
                rows[cells[0]] = cells
    expected = {f"D-{number:03d}" for number in range(1, 13)}
    if set(rows) != expected:
        errors.append("dynamic-row-set")
        return
    for row_id in sorted(expected):
        cells = rows[row_id]
        if cells[6] != "PASS":
            errors.append(f"dynamic-status:{row_id}")
        paths = [item.strip().strip("`") for item in cells[4].split(";")]
        hashes = [item.strip().strip("`") for item in cells[5].split(";")]
        if len(paths) != len(hashes) or not paths:
            errors.append(f"dynamic-contract:{row_id}")
            continue
        for relative, expected_hash in zip(paths, hashes):
            path = root / relative
            if not path.is_file():
                errors.append(f"dynamic-missing:{relative}")
            elif digest(path)[1] != expected_hash:
                errors.append(f"dynamic-hash:{relative}")


def verify_privacy_and_semantics(root: Path, errors: list[str]) -> dict[str, object]:
    summary: dict[str, object] = {"json_content_or_key_fields": [], "raw_text_size": 0}
    raw = root / "raw"
    for path in raw.rglob("*"):
        if path.is_file():
            summary["raw_text_size"] = int(summary["raw_text_size"]) + path.stat().st_size
            if path.suffix == ".json":
                value = json.loads(path.read_text(encoding="utf-8"))
                encoded = json.dumps(value, ensure_ascii=False).lower()
                if '"content"' in encoded or '"text"' in encoded or '"key"' in encoded:
                    summary["json_content_or_key_fields"].append(path.relative_to(root).as_posix())
    if summary["json_content_or_key_fields"]:
        errors.append("privacy-content-or-key-in-json")
    try:
        lifecycle = json.loads((raw / "fixed-lifecycle.json").read_text(encoding="utf-8"))
        negative = json.loads((raw / "negative-results.json").read_text(encoding="utf-8"))
        geometry = json.loads((raw / "geometry.json").read_text(encoding="utf-8"))
        cleanup = json.loads((raw / "cleanup.json").read_text(encoding="utf-8"))
        if lifecycle.get("cargo_test_exit") != 0 or lifecycle.get("passed_tests") != 8:
            errors.append("lifecycle")
        if negative.get("unknown_ipc_exit") != 1 or negative.get("argument_reject_exit") != 1:
            errors.append("negative")
        if geometry.get("three_pages") != 3 or geometry.get("keyboard_capture") is not True:
            errors.append("geometry")
        if cleanup.get("fixture_residue_count") != 0 or cleanup.get("candidate_shadow_residue_count") != 0:
            errors.append("cleanup")
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        errors.append("raw-semantic-unreadable")
    return summary


def verify_payload(root: Path) -> dict[str, object]:
    manifest = json.loads((root / "PAYLOAD_MANIFEST.json").read_text(encoding="utf-8"))
    entries = {item["path"]: item for item in manifest.get("files", [])}
    actual = payload_paths(root)
    missing = sorted(set(entries) - actual)
    extra = sorted(actual - set(entries))
    drift: list[str] = []
    for relative, item in entries.items():
        path = root / relative
        if path.is_file() and digest(path) != (item["bytes"], item["sha256"]):
            drift.append(relative)
    errors: list[str] = []
    verify_dynamic(root, errors)
    privacy = verify_privacy_and_semantics(root, errors)
    return {
        "passed": not missing and not extra and not drift and not errors,
        "manifest_file_count": manifest.get("file_count"),
        "actual_file_count": len(actual),
        "missing": missing,
        "extra": extra,
        "drift_paths": drift,
        "semantic_errors": errors,
        "privacy_summary": privacy,
    }


def copy_candidate() -> dict[str, object]:
    destination = TMP / "candidate"
    shutil.copytree(SOURCE_CANDIDATE, destination, symlinks=True)
    source = sorted(path for path in SOURCE_CANDIDATE.rglob("*") if path.is_file() and not path.is_symlink())
    copied = sorted(path for path in destination.rglob("*") if path.is_file() and not path.is_symlink())
    source_map = {path.relative_to(SOURCE_CANDIDATE).as_posix(): digest(path) for path in source}
    copied_map = {path.relative_to(destination).as_posix(): digest(path) for path in copied}
    prohibited_components = {"evidence", "tools", "target", "tests"}
    prohibited = [key for key in copied_map if set(Path(key).parts) & prohibited_components]
    return {
        "operation": "positive copy of fixed P3-111 candidate only",
        "source_file_count": len(source_map),
        "copied_file_count": len(copied_map),
        "identical": source_map == copied_map,
        "prohibited_components_in_copy": prohibited,
        "pass": source_map == copied_map and len(copied_map) == 72 and not prohibited,
    }


def run_offline(candidate: Path) -> dict[str, object]:
    environment = dict(os.environ)
    environment["CARGO_TARGET_DIR"] = str(TMP / "cargo-target")
    environment["CARGO_NET_OFFLINE"] = "true"
    records = []
    for label, command in [
        ("cargo-test", ["cargo", "test", "--locked", "--offline"]),
        ("cargo-build", ["cargo", "build", "--locked", "--offline"]),
    ]:
        result = subprocess.run(command, cwd=candidate, text=True, capture_output=True, env=environment)
        (OUT / f"{label}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        passed = int(re.search(r"(\\d+) passed", result.stdout + result.stderr).group(1)) if re.search(r"(\\d+) passed", result.stdout + result.stderr) else None
        records.append({"id": label, "command": command, "exit_code": result.returncode, "reported_passed_tests": passed})
    return {"network_mode": "cargo --offline and CARGO_NET_OFFLINE=true", "results": records,
            "pass": records[0]["exit_code"] == 0 and records[0]["reported_passed_tests"] == 8 and records[1]["exit_code"] == 0}


def static_scan(candidate: Path) -> dict[str, object]:
    runtime = (candidate / "src/runtime.rs").read_text(encoding="utf-8")
    cargo = (candidate / "Cargo.toml").read_text(encoding="utf-8")
    tauri = json.loads((candidate / "tauri.conf.json").read_text(encoding="utf-8"))
    capability = json.loads((candidate / "capabilities/main.json").read_text(encoding="utf-8"))
    ui = "\n".join(path.read_text(encoding="utf-8") for path in (candidate / "ui").glob("*") if path.suffix in {".js", ".html", ".css"})
    expected_ipc = ["capture_record", "get_today", "runtime_status"]
    source_files = [runtime, cargo, ui]
    forbidden_tokens = ["reqwest", "ureq", "TcpStream", "Command::new", "std::process::Command", "tauri-plugin", "ShellExt"]
    findings = [token for token in forbidden_tokens if any(token in source for source in source_files)]
    invoked = sorted(set(re.findall(r"invoke\\(\\s*[\"']([a-z_]+)[\"']", ui)))
    result = {
        "expected_ipc": expected_ipc,
        "runtime_commands_found": [name for name in expected_ipc if f"fn {name}" in runtime],
        "ui_invokes": invoked,
        "capability_permissions": capability.get("permissions"),
        "csp_connect_src_ipc_only": "connect-src ipc:" in tauri["app"]["security"]["csp"],
        "forbidden_dependency_or_process_tokens": findings,
        "closed_status_fields_present": all(f"{name}: false" in runtime for name in ["filesystem", "raw_database", "generic_path_api", "shell", "process_spawn", "network", "vault", "export", "sync"]),
    }
    result["pass"] = (result["runtime_commands_found"] == expected_ipc and set(invoked) <= set(expected_ipc)
                      and result["capability_permissions"] == [] and result["csp_connect_src_ipc_only"]
                      and not findings and result["closed_status_fields_present"])
    return result


def mutate(root: Path, name: str) -> None:
    relative, kind = MUTATIONS[name]
    path = root / relative
    if kind == "remove":
        path.unlink()
    elif kind == "append":
        path.write_bytes(path.read_bytes() + b" ")
    else:
        value = json.loads(path.read_text(encoding="utf-8"))
        if kind == "cleanup": value["fixture_residue_count"] = 1
        if kind == "negative": value["unknown_ipc_exit"] = 0
        if kind == "lifecycle": value["passed_tests"] = 6
        if kind == "geometry": value["three_pages"] = 2
        path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def submitted(root: Path) -> dict[str, object]:
    result = subprocess.run([sys.executable, str(SUBMITTED_VERIFIER), str(root)], text=True, capture_output=True)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        value = {"parse_error": True}
    return {"exit_code": result.returncode, "passed": value.get("passed"), "missing": value.get("missing"),
            "drift": [item.get("path") for item in value.get("hash_or_bytes_drift", [])],
            "semantic_errors": value.get("semantic_errors")}


def mutation_matrix() -> tuple[dict[str, object], dict[str, object]]:
    source = TMP / "review-payload" / "rework-1"
    control = TMP / "disposable" / "noop" / "rework-1"
    control.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REWORK, source)
    shutil.copytree(source, control)
    control_result = verify_payload(control)
    source_result = verify_payload(source)
    rows = []
    cross = {"baseline": submitted(source), "control": submitted(control), "mutations": []}
    for name in MUTATIONS:
        target = TMP / "disposable" / name / "rework-1"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
        mutate(target, name)
        result = verify_payload(target)
        expected_error = {"cleanup_residue": "cleanup", "negative_exit_zero": "negative", "db_count_wrong": "lifecycle", "geometry_wrong": "geometry"}.get(name)
        expected_missing = ["raw/geometry.json"] if name == "missing_file" else []
        expected_drift = [] if name == "missing_file" else [MUTATIONS[name][0]]
        exact = (not result["passed"] and result["missing"] == expected_missing and result["drift_paths"] == expected_drift
                 and (expected_error in result["semantic_errors"] if expected_error else True))
        rows.append({"mutation": name, "exit_code": 1 if not result["passed"] else 0, "exact_expected_failure": exact,
                     "missing": result["missing"], "drift_paths": result["drift_paths"], "semantic_errors": result["semantic_errors"]})
        cross["mutations"].append({"mutation": name, **submitted(target)})
    matrix = {"baseline": source_result, "unchanged_control": control_result, "mutations": rows,
              "pass": source_result["passed"] and control_result["passed"] and all(row["exact_expected_failure"] for row in rows)}
    cross["pass"] = (cross["baseline"]["exit_code"] == 0 and cross["control"]["exit_code"] == 0
                     and all(row["exit_code"] == 1 and row["passed"] is False for row in cross["mutations"]))
    return matrix, cross


def main() -> int:
    if TMP.exists() or TMP.is_symlink():
        print(json.dumps({"blocked": "temporary-root-preexists"}))
        return 2
    TMP.mkdir(parents=True)
    copy = copy_candidate()
    offline = run_offline(TMP / "candidate")
    static = static_scan(TMP / "candidate")
    initial = verify_payload(INITIAL)
    rework = verify_payload(REWORK)
    mutations, cross = mutation_matrix()
    for name, value in [("copy-inventory.json", copy), ("offline-results.json", offline), ("static-results.json", static),
                        ("dynamic-privacy-audit.json", {"initial": initial, "rework": rework}),
                        ("independent-verifier-results.json", {"initial": initial, "rework": rework}),
                        ("mutation-matrix.json", mutations), ("submitted-verifier-cross-check.json", cross)]:
        write(name, value)
    result = {"copy": copy["pass"], "offline": offline["pass"], "static": static["pass"],
              "initial_37": initial["passed"] and initial["manifest_file_count"] == 37,
              "rework_38": rework["passed"] and rework["manifest_file_count"] == 38,
              "control_and_mutations": mutations["pass"], "submitted_cross_check": cross["pass"]}
    result["pass"] = all(result.values())
    write("runner-summary.json", {"created_at_utc": datetime.now(timezone.utc).isoformat(), "result": result})
    print(json.dumps(result, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
