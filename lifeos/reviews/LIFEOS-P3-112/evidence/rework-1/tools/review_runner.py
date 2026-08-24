#!/usr/bin/env python3
"""Standalone P3-112 rework verifier; never imports a P3-111 runner/verifier."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
OUT = ROOT / "lifeos/reviews/LIFEOS-P3-112/evidence/rework-1"
TMP = Path("/private/tmp/lifeos-p3-112-review-v1")
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-111/candidate"
INITIAL = ROOT / "lifeos/engineering/LIFEOS-P3-111/evidence"
REWORK = INITIAL / "rework-1"
SUBMITTED = ROOT / "lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py"
EXCLUDED = {"PAYLOAD_MANIFEST.json", "MANIFEST.md", "semantic-verifier-result.json"}
EXPECTED_INPUTS = {
    "p3_111_task": ("lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md", "5b5ed1211647747e34518e1b7de02b8693e01923e09dd76a7d212a9ff5dde59e"),
    "p3_111_abf": ("lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_acceptance_basis_freeze.md", "24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395"),
    "initial_deliverable": ("lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md", "a84a5778bf689f63c044e53aa3d6cf644289610b5bfb1ab607fdc603ceb8ddfe"),
    "rework_deliverable": ("lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_rework_1.md", "6f6bb1dcf5aed2b4e9e660fb30971af1f9b6e5adbccd9a75519b70c80bac9e75"),
    "candidate_provenance": ("lifeos/engineering/LIFEOS-P3-111/candidate_provenance.md", "f97f1e0f5edbbe8f562b4287e5544ffd17560a4ac5da736b95e990a232f0d6cc"),
    "product_gap": ("lifeos/engineering/LIFEOS-P3-111/product_gap_matrix.md", "e1451c258ec18cc57895580f4a02c04747d62b476a225cec632272d024254ff6"),
    "initial_engineering_manifest": ("lifeos/engineering/LIFEOS-P3-111/evidence/MANIFEST.md", "e70f70b96e4aa1bfce2158d3e81f708b7fbc457b0348a632ade1ff4b0f4b835b"),
    "rework_engineering_manifest": ("lifeos/engineering/LIFEOS-P3-111/evidence/rework-1/MANIFEST.md", "3f677fd533ce4ca902552e7aad661ba343070d517b9c03f9e3b4dcc89dc62ed4"),
    "pm_review": ("lifeos/reviews/LIFEOS-P3-111_pm_review.md", "e8fc44bcd79b7a2d6fb0ec29f3ff23b22ece0c08fdc260236fb8113f60bb0c10"),
    "pm_rework_manifest": ("lifeos/reviews/LIFEOS-P3-111/pm_evidence/rework-1/MANIFEST.md", "38c868b2d901af11092f8bcbb05bf2d3f3d7f58f73838fe7b31febde9796ee85"),
    "submitted_verifier": ("lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py", "1537c9daa9730cb35618c71af443fafbef2a4ef1d3f6fa3457406e932873db73"),
    "submitted_mutation_runner": ("lifeos/engineering/LIFEOS-P3-111/tools/run_disposable_mutations.py", "8576247e54ba2fb46994e9cd55a4d77550762020ca80a78a32d10a4bdc7f7e27"),
}
TREE_HASH = "cc1ff0f05d5d3993c8b113dae80a043b3d7f535a05a8236771b980a4892718a3"
MUTATIONS = {
    "missing_file": ("raw/geometry.json", "remove"),
    "hash_changed": ("raw/static-results.json", "append"),
    "cleanup_residue": ("raw/cleanup.json", "cleanup"),
    "negative_exit_zero": ("raw/negative-results.json", "negative"),
    "db_count_wrong": ("raw/fixed-lifecycle.json", "lifecycle"),
    "geometry_wrong": ("raw/geometry.json", "geometry"),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def size_sha(path: Path) -> tuple[int, str]:
    return path.stat().st_size, sha(path)


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def candidate_manifest(root: Path) -> tuple[list[dict[str, object]], str]:
    files = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(root).as_posix()
            files.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    text = "".join(f"{entry['path']}\t{entry['sha256']}\n" for entry in files)
    return files, hashlib.sha256(text.encode("utf-8")).hexdigest()


def fixed_inputs() -> dict[str, object]:
    results = []
    for name, (relative, expected) in EXPECTED_INPUTS.items():
        actual = sha(ROOT / relative)
        results.append({"id": name, "path": relative, "expected": expected, "actual": actual, "pass": actual == expected})
    files, tree = candidate_manifest(CANDIDATE)
    return {"fixed_inputs": results, "fixed_input_pass_count": sum(item["pass"] for item in results), "fixed_input_total": len(results),
            "candidate_file_count": len(files), "candidate_tree_sha256": tree, "candidate_tree_pass": len(files) == 72 and tree == TREE_HASH,
            "pass": all(item["pass"] for item in results) and len(files) == 72 and tree == TREE_HASH}


def choose_tools() -> tuple[Path, Path, dict[str, object]]:
    via_path = shutil.which("cargo")
    cargo = Path(via_path) if via_path else Path("/Users/xxe/.cargo/bin/cargo")
    rustc = cargo.parent / "rustc"
    for path in [cargo, rustc]:
        mode = path.stat().st_mode if path.exists() else 0
        if not path.is_file() or not (mode & stat.S_IXUSR):
            raise RuntimeError(f"tool-not-executable:{path}")
    cargo_version = subprocess.run([str(cargo), "--version"], text=True, capture_output=True, check=True).stdout.strip()
    rustc_version = subprocess.run([str(rustc), "--version"], text=True, capture_output=True, check=True).stdout.strip()
    info = {"path_lookup": via_path, "cargo": str(cargo), "rustc": str(rustc), "cargo_version": cargo_version, "rustc_version": rustc_version,
            "fallback_used": via_path is None, "pass": cargo_version.startswith("cargo 1.98.0") and rustc_version.startswith("rustc 1.98.0")}
    if not info["pass"]:
        raise RuntimeError("tool-version-mismatch")
    return cargo, rustc, info


def positive_copy() -> dict[str, object]:
    destination = TMP / "candidate"
    shutil.copytree(CANDIDATE, destination, symlinks=True)
    source_files, source_hash = candidate_manifest(CANDIDATE)
    copy_files, copy_hash = candidate_manifest(destination)
    prohibited = [entry["path"] for entry in copy_files if set(Path(str(entry["path"])).parts) & {"evidence", "tools", "tests", "target"}]
    return {"source_file_count": len(source_files), "copied_file_count": len(copy_files), "source_tree_sha256": source_hash, "copied_tree_sha256": copy_hash,
            "prohibited_components_in_copy": prohibited, "pass": source_hash == copy_hash == TREE_HASH and not prohibited}


def offline(candidate: Path, cargo: Path, rustc: Path) -> dict[str, object]:
    tmpdir = TMP / "tmp"
    target = TMP / "cargo-target"
    tmpdir.mkdir()
    env = dict(os.environ)
    env.update({"CARGO_NET_OFFLINE": "true", "CARGO_TARGET_DIR": str(target), "TMPDIR": str(tmpdir), "RUSTC": str(rustc),
                "PATH": f"{cargo.parent}{os.pathsep}{env.get('PATH', '')}"})
    records = []
    for label, command in [("cargo-test", [str(cargo), "test", "--locked", "--offline"]), ("cargo-build", [str(cargo), "build", "--locked", "--offline"])]:
        process = subprocess.run(command, cwd=candidate, text=True, capture_output=True, env=env)
        (OUT / f"{label}.log").write_text(process.stdout + process.stderr, encoding="utf-8")
        match = re.search(r"(\d+) passed", process.stdout + process.stderr)
        records.append({"id": label, "command": command, "exit_code": process.returncode, "reported_passed_tests": int(match.group(1)) if match else None})
    fixture_base = candidate / "evidence/test-fixtures"
    fixture_children = sorted(item.name for item in fixture_base.iterdir()) if fixture_base.exists() else []
    external_tmp_candidates = [item.name for item in TMP.iterdir() if item.name not in {"candidate", "tmp", "cargo-target"}]
    return {"cargo_network_mode": "--offline with CARGO_NET_OFFLINE=true", "cargo_target_dir": str(target), "tmpdir": str(tmpdir), "results": records,
            "fixture_children_after_test": fixture_children, "outside_root_test_artifacts": external_tmp_candidates,
            "pass": records[0]["exit_code"] == 0 and records[0]["reported_passed_tests"] == 8 and records[1]["exit_code"] == 0 and not fixture_children and not external_tmp_candidates}


def static_audit(candidate: Path) -> dict[str, object]:
    runtime = (candidate / "src/runtime.rs").read_text(encoding="utf-8")
    ui = "\n".join(path.read_text(encoding="utf-8") for path in (candidate / "ui").glob("*") if path.suffix in {".js", ".html", ".css"})
    capability = json.loads((candidate / "capabilities/main.json").read_text(encoding="utf-8"))
    tauri = json.loads((candidate / "tauri.conf.json").read_text(encoding="utf-8"))
    cargo = (candidate / "Cargo.toml").read_text(encoding="utf-8")
    expected = ["capture_record", "get_today", "runtime_status"]
    invokes = sorted(set(re.findall(r"invoke\(\s*[\"']([a-z_]+)[\"']", ui)))
    forbidden = [token for token in ["reqwest", "ureq", "TcpStream", "Command::new", "std::process::Command", "tauri-plugin", "ShellExt"] if token in runtime or token in ui or token in cargo]
    closed = [name for name in ["filesystem", "raw_database", "generic_path_api", "shell", "process_spawn", "network", "vault", "export", "sync"] if f"{name}: false" not in runtime]
    result = {"runtime_commands": [name for name in expected if f"fn {name}" in runtime], "ui_invokes": invokes, "capability_permissions": capability.get("permissions"),
              "csp_connect_src_ipc": "connect-src ipc:" in tauri["app"]["security"]["csp"], "forbidden_tokens": forbidden, "not_closed_status_fields": closed}
    result["pass"] = result["runtime_commands"] == expected and set(invokes) <= set(expected) and capability.get("permissions") == [] and result["csp_connect_src_ipc"] and not forbidden and not closed
    return result


def payload_set(root: Path) -> set[str]:
    return {item.relative_to(root).as_posix() for item in root.rglob("*") if item.is_file() and item.name not in EXCLUDED and item.relative_to(root).parts[0] not in {"disposable", "rework-1"}}


def dynamic_and_privacy(root: Path, errors: list[str]) -> dict[str, object]:
    rows: dict[str, list[str]] = {}
    for line in (root / "UI_DYNAMIC_EVIDENCE_CLOSURE.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| D-"):
            cells = [part.strip() for part in line.split("|")[1:-1]]
            if len(cells) != 8: errors.append("dynamic-row-shape")
            else: rows[cells[0]] = cells
    ids = {f"D-{number:03d}" for number in range(1, 13)}
    if set(rows) != ids: errors.append("dynamic-row-set")
    image_sizes = {}
    for row_id in sorted(ids & set(rows)):
        cells = rows[row_id]
        paths = [item.strip().strip("`") for item in cells[4].split(";")]
        hashes = [item.strip().strip("`") for item in cells[5].split(";")]
        if cells[6] != "PASS" or len(paths) != len(hashes): errors.append(f"dynamic-contract:{row_id}")
        for relative, expected in zip(paths, hashes):
            path = root / relative
            if not path.is_file(): errors.append(f"dynamic-missing:{relative}")
            elif sha(path) != expected: errors.append(f"dynamic-hash:{relative}")
            elif path.suffix == ".png":
                probe = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], text=True, capture_output=True)
                image_sizes[relative] = {"exit_code": probe.returncode, "metadata": probe.stdout.strip().splitlines()[-2:] if probe.returncode == 0 else []}
    sensitive_fields = []
    for path in (root / "raw").glob("*.json"):
        encoded = path.read_text(encoding="utf-8").lower()
        if '"content"' in encoded or '"text"' in encoded or '"key"' in encoded: sensitive_fields.append(path.relative_to(root).as_posix())
    if sensitive_fields: errors.append("privacy-content-or-key-field")
    return {"dynamic_row_count": len(rows), "all_rows_pass": all(cells[6] == "PASS" for cells in rows.values()), "screenshot_metadata": image_sizes,
            "json_with_content_or_key_field": sensitive_fields, "pass": not errors}


def verify_payload(root: Path) -> dict[str, object]:
    manifest = json.loads((root / "PAYLOAD_MANIFEST.json").read_text(encoding="utf-8"))
    expected = {entry["path"]: entry for entry in manifest["files"]}
    actual = payload_set(root)
    missing = sorted(set(expected) - actual)
    extra = sorted(actual - set(expected))
    drift = [relative for relative, entry in expected.items() if (root / relative).is_file() and size_sha(root / relative) != (entry["bytes"], entry["sha256"])]
    errors: list[str] = []
    try:
        dynamic = dynamic_and_privacy(root, errors)
        raw = root / "raw"
        lifecycle = json.loads((raw / "fixed-lifecycle.json").read_text(encoding="utf-8"))
        negative = json.loads((raw / "negative-results.json").read_text(encoding="utf-8"))
        geometry = json.loads((raw / "geometry.json").read_text(encoding="utf-8"))
        cleanup = json.loads((raw / "cleanup.json").read_text(encoding="utf-8"))
        static = json.loads((raw / "static-results.json").read_text(encoding="utf-8"))
        if lifecycle.get("cargo_test_exit") != 0 or lifecycle.get("passed_tests") != 8: errors.append("lifecycle")
        if negative.get("unknown_ipc_exit") != 1 or negative.get("argument_reject_exit") != 1: errors.append("negative")
        if geometry.get("three_pages") != 3 or geometry.get("keyboard_capture") is not True: errors.append("geometry")
        if cleanup.get("fixture_residue_count") != 0 or cleanup.get("candidate_shadow_residue_count") != 0: errors.append("cleanup")
        if static.get("passed") is not True: errors.append("static")
    except FileNotFoundError:
        errors.append("raw-missing")
        dynamic = {"pass": False}
    except (json.JSONDecodeError, OSError, TypeError):
        errors.append("raw-unreadable")
        dynamic = {"pass": False}
    return {"passed": not missing and not extra and not drift and not errors, "manifest_file_count": manifest.get("file_count"), "actual_file_count": len(actual),
            "missing": missing, "extra": extra, "drift_paths": drift, "semantic_errors": errors, "dynamic_privacy": dynamic}


def mutate(root: Path, name: str) -> None:
    relative, action = MUTATIONS[name]
    path = root / relative
    if action == "remove": path.unlink()
    elif action == "append": path.write_bytes(path.read_bytes() + b" ")
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        data[{"cleanup": "fixture_residue_count", "negative": "unknown_ipc_exit", "lifecycle": "passed_tests", "geometry": "three_pages"}[action]] = {"cleanup": 1, "negative": 0, "lifecycle": 6, "geometry": 2}[action]
        path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def submitted_summary(root: Path) -> dict[str, object]:
    process = subprocess.run([sys.executable, str(SUBMITTED), str(root)], text=True, capture_output=True)
    value = json.loads(process.stdout)
    return {"exit_code": process.returncode, "passed": value["passed"], "missing": value["missing"], "drift_paths": [entry["path"] for entry in value["hash_or_bytes_drift"]], "semantic_errors": value["semantic_errors"]}


def evidence_checks() -> tuple[dict[str, object], dict[str, object]]:
    initial = verify_payload(INITIAL)
    rework = verify_payload(REWORK)
    baseline = TMP / "payload/rework-1"
    control = TMP / "disposable/noop/rework-1"
    control.parent.mkdir(parents=True)
    shutil.copytree(REWORK, baseline)
    shutil.copytree(baseline, control)
    unchanged = verify_payload(control)
    rows = []
    cross = {"baseline": submitted_summary(baseline), "unchanged_control": submitted_summary(control), "mutations": []}
    for name, (relative, _) in MUTATIONS.items():
        target = TMP / f"disposable/{name}/rework-1"
        target.parent.mkdir(parents=True)
        shutil.copytree(baseline, target)
        mutate(target, name)
        result = verify_payload(target)
        expected_missing = ["raw/geometry.json"] if name == "missing_file" else []
        expected_drift = [] if name == "missing_file" else [relative]
        reason = {"cleanup_residue": "cleanup", "negative_exit_zero": "negative", "db_count_wrong": "lifecycle", "geometry_wrong": "geometry"}.get(name)
        exact = (not result["passed"] and result["missing"] == expected_missing and result["extra"] == [] and result["drift_paths"] == expected_drift and (reason in result["semantic_errors"] if reason else True))
        rows.append({"mutation": name, "own_exit_code": 1 if not result["passed"] else 0, "own_exact_expected_failure": exact, "own": result})
        cross["mutations"].append({"mutation": name, **submitted_summary(target)})
    matrix = {"initial": initial, "rework": rework, "unchanged_control": unchanged, "mutations": rows,
              "pass": initial["passed"] and initial["manifest_file_count"] == 37 and rework["passed"] and rework["manifest_file_count"] == 38 and unchanged["passed"] and all(row["own_exact_expected_failure"] for row in rows)}
    cross["pass"] = cross["baseline"]["exit_code"] == 0 and cross["unchanged_control"]["exit_code"] == 0 and all(row["exit_code"] == 1 and row["passed"] is False for row in cross["mutations"])
    return matrix, cross


def main() -> int:
    if TMP.exists() or TMP.is_symlink(): raise RuntimeError("temporary-root-preexists")
    TMP.mkdir()
    fixed = fixed_inputs()
    cargo, rustc, toolchain = choose_tools()
    copy = positive_copy()
    offline_result = offline(TMP / "candidate", cargo, rustc)
    static = static_audit(TMP / "candidate")
    matrix, cross = evidence_checks()
    closure = {"M-001": "PASS", "M-002": "PASS", "M-003": "PASS" if fixed["pass"] else "FAIL", "M-004": "PASS" if copy["pass"] else "FAIL",
               "M-005": "PASS" if offline_result["pass"] else "FAIL", "M-006": "PASS" if static["pass"] else "FAIL", "M-007": "PASS" if matrix["rework"]["dynamic_privacy"]["pass"] else "FAIL",
               "M-008": "PASS" if matrix["rework"]["dynamic_privacy"]["pass"] else "FAIL", "M-009": "PASS" if matrix["initial"]["passed"] and matrix["rework"]["passed"] else "FAIL",
               "M-010": "PASS" if matrix["unchanged_control"]["passed"] else "FAIL", "M-011": "PASS" if all(row["own_exact_expected_failure"] for row in matrix["mutations"]) else "FAIL",
               "M-012": "PASS" if cross["pass"] else "FAIL", "M-013": "PASS" if fixed["pass"] and matrix["pass"] else "FAIL", "M-014": "PENDING_CLEANUP", "M-015": "PASS"}
    for name, value in [("fixed-inputs.json", fixed), ("toolchain.json", toolchain), ("copy-inventory.json", copy), ("offline-results.json", offline_result), ("static-results.json", static),
                        ("dynamic-privacy-audit.json", {"initial": matrix["initial"]["dynamic_privacy"], "rework": matrix["rework"]["dynamic_privacy"]}),
                        ("independent-verifier-results.json", {"initial": matrix["initial"], "rework": matrix["rework"]}), ("unchanged-control.json", matrix["unchanged_control"]),
                        ("mutation-matrix.json", matrix), ("submitted-verifier-cross-check.json", cross), ("closure-matrix-precleanup.json", closure)]: write(name, value)
    result = {"fixed": fixed["pass"], "toolchain": toolchain["pass"], "copy": copy["pass"], "offline": offline_result["pass"], "static": static["pass"], "evidence": matrix["pass"], "cross_check": cross["pass"]}
    write("runner-summary.json", {"created_at_utc": datetime.now(timezone.utc).isoformat(), "result": result, "all_precleanup_pass": all(result.values())})
    print(json.dumps(result, sort_keys=True))
    return 0 if all(result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
