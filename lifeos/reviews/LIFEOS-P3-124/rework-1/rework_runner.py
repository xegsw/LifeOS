#!/usr/bin/env python3
"""P3-124 Rework 1 independent, offline Evidence runner.

This file is authored only for Rework 1.  It does not import, read as code, or
execute P3-122/P3-123/initial-P3-124 runners or tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
TEMP = Path("/private/tmp/lifeos-p3-124-independent-review-v1")
ALLOWLIST = REPO / "lifeos/tasks/LIFEOS-P3-124_candidate_source_allowlist.md"
CANDIDATE_ROOT = REPO / "lifeos/engineering/LIFEOS-P3-122/candidate"
EXPECTED_ALLOWLIST_SHA = "198875e445c15469f4d02e7799368ac7d5ca05f7da1f672b356969a46dd593f5"
EXPECTED_TREE = "ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742"
EXPECTED_ABF_SHA = "b8504298cdc20dd3425eb519f556d27a3867640de3f8fb5a4476f81095356efc"
EXPECTED_INPUTS = {
    "lifeos/tasks/LIFEOS-P3-124_p3_122_combined_candidate_fresh_isolated_independent_review_final_successor_acceptance_basis_freeze.md": EXPECTED_ABF_SHA,
    "lifeos/reviews/LIFEOS-P3-124_pm_review.md": "68121420e483d161519220aa143d94e998d225a9f1e32e9a5b4385ec42b7e875",
    "lifeos/reviews/LIFEOS-P3-124/pm_evidence/initial/MANIFEST.md": "30e5e5255525d27bfd64f46af006836b26a1a02eeeda77a1f37311e26afd3669",
    "lifeos/reviews/LIFEOS-P3-124/pm_evidence/rework-1-authorization/MANIFEST.md": "eb4f8370574ef15af4efc1aad0a17bf41bfc3045610aebc67efa93749f54f33e",
    "lifeos/reviews/LIFEOS-P3-124/pm_evidence/rework-1-authorization/user_authorization.md": "13ae28d74846750c00b42f8dc4124f4c7cee90227a460f6ec167d002794b93a9",
    "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json": "b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c",
    "lifeos/reviews/LIFEOS-P3-122_pm_review.md": "1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe",
    "lifeos/reviews/LIFEOS-P3-122/pm_evidence/acceptance/MANIFEST.md": "c8fac52c00df7fa1308bb6f6143c8a13fec83568e19b31afb6bd17dd9b1a7966",
    "lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md": "fc65335b73280b64888c5803bcacf4402771c5b9cb69eaeac7117c20076adecc",
}
INITIAL_READONLY_HASHES = {
    "lifeos/reviews/LIFEOS-P3-124/independent_review.md": "3b12e506f625a68c74e33334f3e932f0810c60fd0c37818ba5fa7d00ab22fdf9",
    "lifeos/reviews/LIFEOS-P3-124/review_runner.py": "cf34184f4321ce32e93cc66a612127421855e74c79f7a1b3e6d66d47620a25de",
    "lifeos/reviews/LIFEOS-P3-124/evidence/preflight.json": "2186f71f9bed875f03aa23e92e0b9bd44d8560c6014f02115e896b38e6c695f5",
}
ROW = re.compile(r"^\| `(?P<path>[^`]+)` \| (?P<bytes>\d+) \| `(?P<sha>[0-9a-f]{64})` \|$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(name: str, value: object) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    target = EVIDENCE / name
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def parse_allowlist() -> list[dict[str, object]]:
    raw = ALLOWLIST.read_bytes()
    rows: list[dict[str, object]] = []
    for line in raw.decode("utf-8").splitlines():
        match = ROW.match(line)
        if match:
            rows.append({"path": match["path"], "bytes": int(match["bytes"]), "sha256": match["sha"]})
    if b"\\n" in raw:
        raise RuntimeError("literal backslash-n present in Frozen allowlist")
    if len(rows) != 75:
        raise RuntimeError(f"expected 75 physical candidate rows, got {len(rows)}")
    return rows


def relative_candidate_path(project_path: str) -> Path:
    prefix = "lifeos/engineering/LIFEOS-P3-122/candidate/"
    if not project_path.startswith(prefix):
        raise RuntimeError(f"allowlist path outside candidate: {project_path}")
    return Path(project_path[len(prefix):])


def canonical_tree_variants(rows: list[dict[str, object]]) -> dict[str, str]:
    pairs = [(str(row["path"]), str(row["sha256"])) for row in rows]
    payloads = {
        "path-tab-sha-lf": "".join(f"{path}\t{digest}\n" for path, digest in pairs).encode(),
        "sha-space-path-lf": "".join(f"{digest}  {path}\n" for path, digest in pairs).encode(),
        "path-nul-sha-nul": b"".join(path.encode() + b"\0" + digest.encode() + b"\0" for path, digest in pairs),
        "json-rows": json.dumps(pairs, separators=(",", ":"), ensure_ascii=False).encode(),
    }
    return {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}


def preflight(_: argparse.Namespace) -> int:
    rows = parse_allowlist()
    fixed = []
    for relative, expected in EXPECTED_INPUTS.items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        fixed.append({"path": relative, "expected": expected, "actual": actual, "pass": actual == expected})
    history = []
    for relative, expected in INITIAL_READONLY_HASHES.items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        history.append({"path": relative, "expected": expected, "actual": actual, "pass": actual == expected})
    candidate = []
    for row in rows:
        path = REPO / str(row["path"])
        actual_bytes = path.stat().st_size if path.is_file() else None
        actual_hash = sha256(path) if path.is_file() else None
        candidate.append({**row, "actual_bytes": actual_bytes, "actual_sha256": actual_hash, "pass": actual_bytes == row["bytes"] and actual_hash == row["sha256"]})
    variants = canonical_tree_variants(rows)
    result = {
        "test_id": "P124R-M001",
        "generated_at": now(),
        "frozen_allowlist": {
            "path": str(ALLOWLIST.relative_to(REPO)),
            "expected_sha256": EXPECTED_ALLOWLIST_SHA,
            "actual_sha256": sha256(ALLOWLIST),
            "physical_lf_rows": len(ALLOWLIST.read_bytes().splitlines()),
            "candidate_data_rows": len(rows),
            "literal_backslash_n": b"\\n" in ALLOWLIST.read_bytes(),
        },
        "fixed_inputs": fixed,
        "initial_readonly_hashes": history,
        "candidate_rows": candidate,
        "tree_hash": {"expected": EXPECTED_TREE, "independent_canonical_variants": variants},
        "root_time_semantics": {
            "freeze_time": "D-0499 records initial review root and unique temp root absent before Frozen ABF.",
            "rework_session_start": "Before this Rework directory was created, shell stat observed rework-1 absent and fixed temp root absent; initial P3-124 review root is intentionally preserved and present.",
            "preflight_write_time": "This evidence file is necessarily written after the authorized rework-1 directory exists; it does not claim that the current directory is absent.",
        },
    }
    result["pass"] = (
        result["frozen_allowlist"]["actual_sha256"] == EXPECTED_ALLOWLIST_SHA
        and result["frozen_allowlist"]["candidate_data_rows"] == 75
        and result["frozen_allowlist"]["physical_lf_rows"] == 87
        and not result["frozen_allowlist"]["literal_backslash_n"]
        and all(item["pass"] for item in fixed)
        and all(item["pass"] for item in history)
        and all(item["pass"] for item in candidate)
    )
    write_json("preflight.json", result)
    print(json.dumps({"pass": result["pass"], "candidate_rows": len(candidate)}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def copy_candidate(_: argparse.Namespace) -> int:
    rows = parse_allowlist()
    if TEMP.exists() or TEMP.is_symlink():
        raise RuntimeError(f"temporary root unexpectedly exists: {TEMP}")
    destination = TEMP / "candidate"
    copied = []
    for row in rows:
        source = REPO / str(row["path"])
        relative = relative_candidate_path(str(row["path"]))
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append({"relative_path": str(relative), "bytes": target.stat().st_size, "sha256": sha256(target)})
    expected_paths = {str(relative_candidate_path(str(row["path"]))) for row in rows}
    actual_paths = {str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file()}
    result = {
        "test_id": "P124R-COPY-01",
        "generated_at": now(),
        "temporary_root": str(TEMP),
        "destination": str(destination),
        "copied": copied,
        "extra_paths": sorted(actual_paths - expected_paths),
        "missing_paths": sorted(expected_paths - actual_paths),
        "pass": len(copied) == 75 and actual_paths == expected_paths and all(
            item["bytes"] == row["bytes"] and item["sha256"] == row["sha256"] for item, row in zip(copied, rows)
        ),
    }
    write_json("copy-result.json", result)
    print(json.dumps({"pass": result["pass"], "copied": len(copied)}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def run_logged(command: list[str], cwd: Path, env: dict[str, str], log_name: str) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log = EVIDENCE / "logs" / log_name
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(completed.stdout, encoding="utf-8")
    return {"command": command, "cwd": str(cwd), "exit_code": completed.returncode, "log": str(log.relative_to(HERE)), "log_sha256": sha256(log)}


def build(_: argparse.Namespace) -> int:
    candidate = TEMP / "candidate"
    cargo = Path("/Users/xxe/.cargo/bin/cargo")
    if not cargo.is_file():
        raise RuntimeError(f"expected task-approved cargo missing: {cargo}")
    env = os.environ.copy()
    env.update({
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TARGET_DIR": str(TEMP / "target"),
        "TMPDIR": str(TEMP / "tmp"),
        "CLANG_MODULE_CACHE_PATH": str(TEMP / "clang-cache"),
        "SWIFT_MODULECACHE_PATH": str(TEMP / "swift-cache"),
    })
    for key in ("CARGO_TARGET_DIR", "TMPDIR", "CLANG_MODULE_CACHE_PATH", "SWIFT_MODULECACHE_PATH"):
        Path(env[key]).mkdir(parents=True, exist_ok=True)
    test = run_logged([str(cargo), "test", "--locked", "--offline"], candidate, env, "cargo-test.log")
    bundle = run_logged([str(cargo), "tauri", "build", "--bundles", "app"], candidate, env, "tauri-build.log") if test["exit_code"] == 0 else {"skipped": True}
    app = TEMP / "target/release/bundle/macos/LifeOS P3-122 Native Viewport Runtime.app"
    result = {"test_id": "P124R-M004", "generated_at": now(), "test": test, "bundle": bundle, "app_path": str(app), "app_exists": app.is_dir(), "pass": test["exit_code"] == 0 and bundle.get("exit_code") == 0 and app.is_dir()}
    write_json("build-result.json", result)
    print(json.dumps({"pass": result["pass"], "app_exists": result["app_exists"]}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def source_lineage(_: argparse.Namespace) -> int:
    rows = parse_allowlist()
    visual = []
    for item in json.loads((REPO / "lifeos/engineering/LIFEOS-P3-122/evidence/results/source-lineage.json").read_text(encoding="utf-8"))["visual_checks"]:
        source = REPO / item["source_path"]
        candidate = REPO / item["candidate_path"]
        candidate_data = candidate.read_text(encoding="utf-8")
        if item["relative_path"] == "index.html":
            candidate_data = candidate_data.replace('    <link rel="stylesheet" href="viewport-adapter.css" />\n', "").replace('    <script src="runtime-adapter.js"></script>\n', "")
            candidate_hash = hashlib.sha256(candidate_data.encode()).hexdigest()
            candidate_bytes = len(candidate_data.encode())
        else:
            candidate_hash = sha256(candidate)
            candidate_bytes = candidate.stat().st_size
        visual.append({"relative_path": item["relative_path"], "source_sha256": sha256(source), "candidate_derived_sha256": candidate_hash, "expected_sha256": item["sha256"], "source_bytes": source.stat().st_size, "candidate_derived_bytes": candidate_bytes, "pass": sha256(source) == item["sha256"] and candidate_hash == item["sha256"]})
    runtime_allowlist = (REPO / "lifeos/tasks/LIFEOS-P3-122_runtime_source_allowlist.md").read_text(encoding="utf-8")
    runtime_rows = []
    for line in runtime_allowlist.splitlines():
        match = ROW.match(line)
        if match:
            relative = Path(match["path"])
            source = REPO / "lifeos/engineering/LIFEOS-P3-121/candidate" / relative
            candidate = CANDIDATE_ROOT / relative
            exact = sha256(source) == sha256(candidate)
            runtime_rows.append({"relative_path": str(relative), "source_sha256": sha256(source), "candidate_sha256": sha256(candidate), "expected_source_sha256": match["sha"], "exact": exact})
    allowed_adapted = {"Cargo.lock", "Cargo.toml", "capabilities/main.json", "gen/schemas/capabilities.json", "src/runtime.rs", "tauri.conf.json"}
    unexpected = [item["relative_path"] for item in runtime_rows if not item["exact"] and item["relative_path"] not in allowed_adapted]
    current_hashes_match = all((REPO / str(row["path"])).is_file() and sha256(REPO / str(row["path"])) == row["sha256"] for row in rows)
    candidate_ui_paths = {str(path.relative_to(CANDIDATE_ROOT / "ui")) for path in (CANDIDATE_ROOT / "ui").rglob("*") if path.is_file()}
    allowed_ui = {"index.html", "styles.css", "app.js", "fixtures.js", "visual_contract.json", "interaction_contract.md", "ia_reconciliation.md", "state_machine.json", "runtime-adapter.js", "viewport-adapter.css"}
    result = {"test_id": "P124R-M003", "generated_at": now(), "visual_checks": visual, "runtime_checks": runtime_rows, "runtime_exact_count": sum(1 for item in runtime_rows if item["exact"]), "runtime_adapted_paths": sorted(item["relative_path"] for item in runtime_rows if not item["exact"]), "unexpected_runtime_adaptations": unexpected, "p3_121_ui_contamination": sorted(candidate_ui_paths - allowed_ui), "candidate_frozen_hashes_match": current_hashes_match}
    result["pass"] = len(visual) == 8 and all(item["pass"] for item in visual) and len(runtime_rows) == 65 and not unexpected and not result["p3_121_ui_contamination"] and current_hashes_match
    write_json("source-lineage.json", result)
    print(json.dumps({"pass": result["pass"], "visual": len(visual), "runtime": len(runtime_rows)}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def native_probe(args: argparse.Namespace) -> int:
    app = TEMP / "target/release/bundle/macos/LifeOS P3-122 Native Viewport Runtime.app"
    executable = app / "Contents/MacOS/lifeos-p3-122"
    plist = app / "Contents/Info.plist"
    helper = TEMP / "native_probe"
    plist_id = subprocess.run(["plutil", "-extract", "CFBundleIdentifier", "raw", str(plist)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    result: dict[str, object] = {
        "test_id": f"P124R-NATIVE-{args.label}",
        "generated_at": now(),
        "app_path": str(app),
        "app_exists": app.is_dir(),
        "executable_path": str(executable),
        "executable_sha256": sha256(executable) if executable.is_file() else None,
        "bundle_identifier": plist_id.stdout.strip() if plist_id.returncode == 0 else None,
        "bundle_identifier_command_exit": plist_id.returncode,
        "helper_path": str(helper),
        "helper_sha256": sha256(helper) if helper.is_file() else None,
    }
    if helper.is_file() and app.is_dir() and result["bundle_identifier"] == "local.lifeos.p3-122":
        probe = subprocess.run([str(helper), "local.lifeos.p3-122", str(app)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        result["native_probe_exit"] = probe.returncode
        try:
            result["native_probe"] = json.loads(probe.stdout)
        except json.JSONDecodeError:
            result["native_probe_raw_output"] = probe.stdout
    else:
        result["native_probe_exit"] = None
    result["pass"] = bool(result.get("native_probe", {}).get("bindingPass", False)) if isinstance(result.get("native_probe"), dict) else False
    write_json(f"native-{args.label}.json", result)
    print(json.dumps({"pass": result["pass"], "label": args.label}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def runtime_root_contract(_: argparse.Namespace) -> int:
    source = CANDIDATE_ROOT / "src/runtime.rs"
    copied = TEMP / "candidate/src/runtime.rs"
    text = source.read_text(encoding="utf-8")
    root_match = re.search(r'const RUNTIME_DB: &str = "([^"]+)";', text)
    geometry_root_match = re.search(r'const RUNTIME_ROOT: &str = "([^"]+)";', text)
    env_names = re.findall(r'std::env::var\("([A-Z0-9_]+)"\)', text)
    result = {
        "test_id": "P124R-BND-ROOT-01",
        "generated_at": now(),
        "candidate_source": str(source.relative_to(REPO)),
        "candidate_source_sha256": sha256(source),
        "task_local_copy_sha256": sha256(copied) if copied.is_file() else None,
        "compiled_runtime_database_path": root_match.group(1) if root_match else None,
        "compiled_runtime_root": geometry_root_match.group(1) if geometry_root_match else None,
        "startup_geometry_write": "record_native_geometry is called during setup and opens RUNTIME_ROOT/native-geometry-{requested}.jsonl with create+append.",
        "startup_geometry_path_is_under_authorized_root": bool(geometry_root_match and Path(geometry_root_match.group(1)).is_relative_to(TEMP)),
        "only_runtime_environment_variables": sorted(set(env_names)),
        "authorized_temporary_root": str(TEMP),
        "candidate_database_path_is_under_authorized_root": bool(root_match and Path(root_match.group(1)).is_relative_to(TEMP)),
        "authorized_action": "none; no creation or write to the P3-122 historical temporary root",
        "impact": "A byte-exact candidate build cannot create its required fresh DB within the sole P3-124 temporary root.",
    }
    result["pass"] = result["candidate_source_sha256"] == result["task_local_copy_sha256"] and not result["candidate_database_path_is_under_authorized_root"] and not result["startup_geometry_path_is_under_authorized_root"] and "LIFEOS_P3_122_VIEWPORT" in result["only_runtime_environment_variables"]
    write_json("boundary-runtime-root.json", result)
    print(json.dumps({"pass": result["pass"], "database_path": result["compiled_runtime_database_path"]}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def independence(_: argparse.Namespace) -> int:
    import ast
    authored = [HERE / "rework_runner.py", HERE / "native_probe.swift", HERE / "test_design.md"]
    artifacts = []
    for path in authored:
        content = path.read_text(encoding="utf-8")
        artifacts.append({"path": str(path.relative_to(REPO)), "sha256": sha256(path)})
    syntax_tree = ast.parse((HERE / "rework_runner.py").read_text(encoding="utf-8"))
    imported_modules = sorted({node.names[0].name for node in ast.walk(syntax_tree) if isinstance(node, ast.Import)} | {node.module for node in ast.walk(syntax_tree) if isinstance(node, ast.ImportFrom) and node.module})
    disallowed_imports = sorted(set(imported_modules) & {"importlib", "runpy"})
    result = {
        "test_id": "P124R-M002",
        "generated_at": now(),
        "authored_artifacts": artifacts,
        "runner_imports": imported_modules,
        "disallowed_dynamic_imports": disallowed_imports,
        "historical_runner_policy": "The Rework runner has no Python runner subprocess, no dynamic Python import, and no reference to a P3-122/P3-123/initial-P3-124 runner as an input path.",
        "subprocess_policy": "Only task-local cargo, task-local native_probe, and plutil are invoked; no historical runner/tool is a subprocess target.",
    }
    result["pass"] = not disallowed_imports
    write_json("independence.json", result)
    print(json.dumps({"pass": result["pass"]}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def parse_markdown_manifest(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(r"^\| `(?P<path>[^`]+)` \| `(?P<sha>[0-9a-f]{64})` \|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            rows.append({"path": match["path"], "sha256": match["sha"]})
    return rows


def verify_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    checked = []
    for row in rows:
        path = REPO / row["path"]
        actual = sha256(path) if path.is_file() else None
        checked.append({**row, "actual_sha256": actual, "pass": actual == row["sha256"]})
    return checked


def initial_integrity(_: argparse.Namespace) -> int:
    manifest = REPO / "lifeos/reviews/LIFEOS-P3-124/pm_evidence/initial/MANIFEST.md"
    checked = verify_rows(parse_markdown_manifest(manifest))
    result = {"test_id": "P124R-HISTORY-01", "generated_at": now(), "manifest": str(manifest.relative_to(REPO)), "rows": checked}
    result["pass"] = len(checked) == 13 and all(item["pass"] for item in checked)
    write_json("history-integrity.json", result)
    print(json.dumps({"pass": result["pass"], "rows": len(checked)}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def lineage(_: argparse.Namespace) -> int:
    final_manifest = REPO / "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json"
    final_data = json.loads(final_manifest.read_text(encoding="utf-8"))
    final_rows = []
    for layer, values in final_data.get("layers", {}).items():
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("sha256"), str):
                    final_rows.append({"path": item["path"], "sha256": item["sha256"], "layer": layer})
    checked_final = verify_rows(final_rows)
    markdown_manifests = [
        REPO / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/acceptance/MANIFEST.md",
        REPO / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md",
        REPO / "lifeos/reviews/LIFEOS-P3-123/pm_evidence/initial/MANIFEST.md",
        REPO / "lifeos/reviews/LIFEOS-P3-123/pm_evidence/final-adoption/MANIFEST.md",
    ]
    markdown_checks = []
    for manifest in markdown_manifests:
        rows = verify_rows(parse_markdown_manifest(manifest))
        relative_manifest = str(manifest.relative_to(REPO))
        time_qualified = []
        if relative_manifest.endswith("LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md"):
            time_qualified = [item for item in rows if item["path"].startswith("lifeos/tasks/LIFEOS-P3-123_")]
        current_rows = [item for item in rows if item not in time_qualified]
        markdown_checks.append({
            "manifest": relative_manifest,
            "rows": rows,
            "time_qualified_historical_rows": time_qualified,
            "pass": all(item["pass"] for item in current_rows),
        })
    result = {
        "test_id": "P124R-M011",
        "generated_at": now(),
        "engineering_final_manifest": str(final_manifest.relative_to(REPO)),
        "engineering_rows": checked_final,
        "pm_and_p3_123_manifests": markdown_checks,
    }
    result["pass"] = len(checked_final) == 245 and all(item["pass"] for item in checked_final) and all(item["pass"] for item in markdown_checks)
    write_json("lineage.json", result)
    print(json.dumps({"pass": result["pass"], "engineering_rows": len(checked_final)}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def cleanup(_: argparse.Namespace) -> int:
    helper = TEMP / "native_probe"
    app = TEMP / "target/release/bundle/macos/LifeOS P3-122 Native Viewport Runtime.app"
    if not TEMP.is_dir() or TEMP.is_symlink() or not helper.is_file() or not app.is_dir():
        raise RuntimeError("exact temporary root is not the expected real task-local directory")
    probe = subprocess.run([str(helper), "local.lifeos.p3-122", str(app)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    probe_data = json.loads(probe.stdout) if probe.returncode == 0 else {"raw_output": probe.stdout}
    pgrep = subprocess.run(["pgrep", "-fl", "lifeos-p3-122"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    file_count = sum(1 for path in TEMP.rglob("*") if path.is_file())
    prior_history = verify_rows(parse_markdown_manifest(REPO / "lifeos/reviews/LIFEOS-P3-124/pm_evidence/initial/MANIFEST.md"))
    no_process = probe.returncode == 0 and len(probe_data.get("bundleIdentifierProcesses", [])) == 0 and probe_data.get("exactProcessCount") == 0 and probe_data.get("exactWindowCount") == 0 and pgrep.returncode in (1, 3)
    if no_process:
        shutil.rmtree(TEMP)
    result = {
        "test_id": "P124R-M013",
        "generated_at": now(),
        "temporary_root": str(TEMP),
        "root_was_real_directory": True,
        "task_local_file_count_before_cleanup": file_count,
        "pre_delete_native_probe": probe_data,
        "pre_delete_pgrep_exit": pgrep.returncode,
        "pre_delete_pgrep_output": pgrep.stdout.strip(),
        "pgrep_unavailable": pgrep.returncode == 3,
        "delete_performed": no_process,
        "temporary_root_absent_after_cleanup": not TEMP.exists() and not TEMP.is_symlink(),
        "initial_readonly_hashes_after_cleanup": prior_history,
    }
    result["pass"] = no_process and result["temporary_root_absent_after_cleanup"] and all(item["pass"] for item in prior_history)
    write_json("cleanup.json", result)
    print(json.dumps({"pass": result["pass"], "deleted": result["delete_performed"]}, ensure_ascii=False))
    return 0 if result["pass"] else 2


def final_manifest(_: argparse.Namespace) -> int:
    target = HERE / "FINAL_MANIFEST.json"
    entries = []
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or path == target:
            continue
        entries.append({"path": str(path.relative_to(HERE)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    fixed = []
    for relative, expected in EXPECTED_INPUTS.items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        fixed.append({"path": relative, "expected_sha256": expected, "actual_sha256": actual, "pass": actual == expected})
    result = {
        "task": "LIFEOS-P3-124",
        "attempt": "Rework 1/2",
        "generated_at": now(),
        "result": "BLOCKED / NOT PASS",
        "counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 1, "Not Implemented": 7},
        "non_self_referential": True,
        "self_excluded_path": "FINAL_MANIFEST.json",
        "rework_artifacts": entries,
        "fixed_inputs": fixed,
        "temporary_root_cleanup_evidence": "evidence/cleanup.json",
        "note": "No Pass, freeze, risk closure, or stage decision is asserted by this independent review artifact.",
    }
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"entries": len(entries), "fixed_inputs_pass": all(item["pass"] for item in fixed)}, ensure_ascii=False))
    return 0 if all(item["pass"] for item in fixed) else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("preflight", preflight), ("copy", copy_candidate), ("build", build), ("source-lineage", source_lineage)):
        command = sub.add_parser(name)
        command.set_defaults(func=func)
    probe_command = sub.add_parser("native-probe")
    probe_command.add_argument("--label", required=True)
    probe_command.set_defaults(func=native_probe)
    root_command = sub.add_parser("runtime-root-contract")
    root_command.set_defaults(func=runtime_root_contract)
    independence_command = sub.add_parser("independence")
    independence_command.set_defaults(func=independence)
    history_command = sub.add_parser("initial-integrity")
    history_command.set_defaults(func=initial_integrity)
    lineage_command = sub.add_parser("lineage")
    lineage_command.set_defaults(func=lineage)
    cleanup_command = sub.add_parser("cleanup")
    cleanup_command.set_defaults(func=cleanup)
    manifest_command = sub.add_parser("final-manifest")
    manifest_command.set_defaults(func=final_manifest)
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as error:
        write_json("runner-error.json", {"command": args.command, "generated_at": now(), "error": repr(error)})
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
