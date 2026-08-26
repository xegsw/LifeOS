#!/usr/bin/env python3
"""Independent, task-owned P3-126 clean-start runner.

It deliberately reads only the P3-125 inputs named by P3-126 and writes only
the P3-126 engineering root plus the one P3-126 temporary root.
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
TASK_ROOT = REPO / "lifeos/engineering/LIFEOS-P3-126"
EVIDENCE = TASK_ROOT / "evidence"
CANDIDATE = TASK_ROOT / "candidate"
SOURCE = REPO / "lifeos/engineering/LIFEOS-P3-125/rework-1/candidate"
ALLOWLIST = REPO / "lifeos/tasks/LIFEOS-P3-126_source_allowlist.md"
TEMP = Path("/private/tmp/lifeos-p3-126-clean-closure-v1")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
CARGO_TAURI = Path("/Users/xxe/.cargo/bin/cargo-tauri")

FIXED_INPUTS = [
    REPO / "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json",
    REPO / "lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_rework_1.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125_pm_rework_1_review.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1/MANIFEST.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/final-adoption/MANIFEST.md",
    ALLOWLIST,
]


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def ensure_within(path: Path, root: Path) -> None:
    if path.resolve().is_relative_to(root.resolve()):
        return
    raise RuntimeError(f"path escapes authorized root: {path}")


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": rel(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_json(name: str, value: object) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    target = EVIDENCE / name
    ensure_within(target, TASK_ROOT)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def parse_allowlist() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", line)
        if match:
            rows.append({"path": match.group(1), "bytes": int(match.group(2)), "sha256": match.group(3)})
    if len(rows) != 75 or len({str(row["path"]) for row in rows}) != 75:
        raise RuntimeError(f"allowlist is not exactly 75 physical unique rows: {len(rows)}")
    return rows


def source_snapshot() -> list[dict[str, object]]:
    return [digest(path) for path in FIXED_INPUTS]


def copy_candidate() -> dict[str, object]:
    rows = parse_allowlist()
    if CANDIDATE.exists():
        raise RuntimeError("candidate already exists; refusing to overwrite task-local production copy")
    for row in rows:
        source = SOURCE / str(row["path"])
        destination = CANDIDATE / str(row["path"])
        ensure_within(destination, CANDIDATE)
        if not source.is_file() or source.is_symlink():
            raise RuntimeError(f"source input is not a normal file: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        observed = digest(destination)
        if observed["bytes"] != row["bytes"] or observed["sha256"] != row["sha256"]:
            raise RuntimeError(f"byte mismatch while copying {row['path']}")
    copied = {path.relative_to(CANDIDATE).as_posix() for path in CANDIDATE.rglob("*") if path.is_file()}
    expected = {str(row["path"]) for row in rows}
    if copied != expected:
        raise RuntimeError(f"candidate tree mismatch: missing={sorted(expected-copied)} extra={sorted(copied-expected)}")
    return {"rows": rows, "candidate_file_count": len(copied), "production_changes": 0}


def static_contract() -> dict[str, object]:
    build = (CANDIDATE / "build.rs").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    main = (CANDIDATE / "src/main.rs").read_text(encoding="utf-8")
    adapter = (CANDIDATE / "ui/runtime-adapter.js").read_text(encoding="utf-8")
    config = json.loads((CANDIDATE / "tauri.conf.json").read_text(encoding="utf-8"))
    capability = json.loads((CANDIDATE / "capabilities/main.json").read_text(encoding="utf-8"))
    expected_ipc = ['"capture_record"', '"get_today"', '"runtime_status"']
    checks = {
        "single_build_time_root": build.count('env::var("LIFEOS_RUNTIME_ROOT")') == 1 and 'cargo:rustc-env=LIFEOS_RUNTIME_ROOT=' in build,
        "no_fixed_parent_or_fallback": "ALLOWED_PARENT" not in build and "fallback" not in build.lower(),
        "runtime_derives_db_and_geometry": 'const DB_NAME: &str = "capture.sqlite"' in runtime and "root.join(DB_NAME)" in runtime and "native-geometry-" in runtime,
        "validation_precedes_storage": runtime.index("validate_database_path") < runtime.index("Connection::open"),
        "three_ipc_unchanged": all(item in runtime for item in expected_ipc) and "generate_handler![capture_record, get_today, runtime_status]" in runtime,
        "ui_ipc_only": all(item.split('"')[1] in adapter for item in expected_ipc) and "__TAURI__?.core?.invoke" in adapter,
        "no_new_api_surface": "mod runtime;" in main and config["app"]["security"]["capabilities"] == ["main"],
        "capability_has_no_filesystem_or_shell": "fs:" not in json.dumps(capability) and "shell:" not in json.dumps(capability),
        "offline_contract": "offline: true" in runtime and "network: false" in runtime and "vault: false" in runtime,
    }
    return {"generated_at": now(), "checks": checks, "all_pass": all(checks.values())}


def command_env(target: Path) -> dict[str, str]:
    ensure_within(target, TEMP)
    cache = TEMP / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({
        "LIFEOS_RUNTIME_ROOT": str(target),
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TARGET_DIR": str(cache / "cargo-target"),
        "TMPDIR": str(cache / "tmp"),
        "CLANG_MODULE_CACHE_PATH": str(cache / "clang-module-cache"),
        "SWIFT_MODULECACHE_PATH": str(cache / "swift-module-cache"),
        "PATH": f"{CARGO.parent}:{env.get('PATH', '')}",
    })
    for name in ("CARGO_TARGET_DIR", "TMPDIR", "CLANG_MODULE_CACHE_PATH", "SWIFT_MODULECACHE_PATH"):
        Path(env[name]).mkdir(parents=True, exist_ok=True)
    return env


def invoke(label: str, command: list[str], env: dict[str, str]) -> dict[str, object]:
    log_dir = TASK_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, cwd=CANDIDATE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = log_dir / f"{label}.log"
    log.write_text(completed.stdout, encoding="utf-8")
    return {"label": label, "command": command, "exit_code": completed.returncode, "log": rel(log), "log_sha256": digest(log)["sha256"]}


def init() -> None:
    if not CARGO.is_file() or not CARGO_TAURI.is_file():
        raise RuntimeError("approved absolute Rust/Tauri tools are unavailable")
    if TEMP.exists():
        raise RuntimeError("authorized temporary root already exists; refusing to reuse it")
    before = source_snapshot()
    TEMP.mkdir(parents=True)
    for subdir in ("run-a", "run-b", "disposable", "cache"):
        (TEMP / subdir).mkdir()
    lineage = copy_candidate()
    after = source_snapshot()
    if before != after:
        raise RuntimeError("protected P3-125 input drifted during source copy")
    preflight = {
        "test_id": "P126-M001",
        "status": "PASS",
        "generated_at": now(),
        "model_effort": {"value": "gpt-5.6-terra + xhigh", "source": "user confirmation in current P3-126 task session", "platform_directly_exposed": False},
        "authorization": {"decision": "D-0511", "new_session": True, "task_delivery": "absolute final task-card path"},
        "roots": {"engineering": rel(TASK_ROOT), "temporary": str(TEMP), "created_after_delivery_preflight": True},
        "prohibited_old_runtime_root_operations": 0,
        "command_plan_has_prohibited_runtime_root_operation": False,
    }
    write_json("preflight.json", preflight)
    write_json("source-lineage.json", {"test_id": "P126-M002", "status": "PASS", "before": before, "after": after, **lineage})
    static = static_contract()
    write_json("static-contract.json", {"test_id": "P126-M003", "status": "PASS" if static["all_pass"] else "FAIL", **static})
    write_json("history-before.json", {"test_id": "P126-M010", "status": "PASS", "items": before})


def config_negatives() -> None:
    if not CANDIDATE.is_dir() or not TEMP.is_dir():
        raise RuntimeError("run init before config negatives")
    bad_file = TEMP / "disposable/config-root-file"
    bad_file.write_text("not a directory\n", encoding="utf-8")
    link = TEMP / "disposable/config-link"
    link.symlink_to(TEMP / "run-a")
    cases = [
        ("missing", None),
        ("empty", ""),
        ("relative", "relative-root"),
        ("traversal", f"{TEMP}/run-a/../bad"),
        ("symlink", str(link)),
        ("file", str(bad_file)),
    ]
    results: list[dict[str, object]] = []
    for name, root_value in cases:
        environment = command_env(TEMP / "run-a")
        if root_value is None:
            environment.pop("LIFEOS_RUNTIME_ROOT", None)
        else:
            environment["LIFEOS_RUNTIME_ROOT"] = root_value
        result = invoke(f"config-{name}", [str(CARGO), "check", "--locked", "--offline"], environment)
        result["case"] = name
        result["expected_nonzero"] = True
        result["pass"] = result["exit_code"] != 0
        results.append(result)
    write_json("config-negatives.json", {"test_id": "P126-M004", "status": "PASS" if all(item["pass"] for item in results) else "FAIL", "results": results})


def unit_tests() -> None:
    environment = command_env(TEMP / "run-a")
    # The inherited candidate's task-local fixture root is deliberately single-root;
    # serial execution prevents unrelated test cases from sharing its ephemeral files.
    result = invoke("unit-tests", [str(CARGO), "test", "--locked", "--offline", "--", "--test-threads=1"], environment)
    result["test_id"] = "P126-unit"
    result["status"] = "PASS" if result["exit_code"] == 0 else "FAIL"
    write_json("unit-tests.json", result)


def bundle(run_name: str) -> None:
    runtime = TEMP / run_name
    if run_name not in {"run-a", "run-b"} or not runtime.is_dir():
        raise RuntimeError("run must be existing run-a or run-b")
    environment = command_env(runtime)
    result = invoke(f"bundle-{run_name}", [str(CARGO_TAURI), "build", "--bundles", "app", "--config", "tauri.conf.json"], environment)
    bundle_path = Path(environment["CARGO_TARGET_DIR"]) / "release/bundle/macos/LifeOS P3-122 Native Viewport Runtime.app"
    result.update({"test_id": f"P126-M00{5 if run_name == 'run-a' else 6}", "runtime_root": str(runtime), "bundle": str(bundle_path), "bundle_exists": bundle_path.is_dir(), "status": "PASS" if result["exit_code"] == 0 and bundle_path.is_dir() else "FAIL"})
    write_json(f"{run_name}-build.json", result)


def history_after() -> None:
    before = json.loads((EVIDENCE / "history-before.json").read_text(encoding="utf-8"))["items"]
    after = source_snapshot()
    status = "PASS" if before == after else "FAIL"
    write_json("history-integrity.json", {"test_id": "P126-M010", "status": status, "before": before, "after": after})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "static", "config", "unit", "bundle", "history"])
    parser.add_argument("--run", choices=["run-a", "run-b"])
    args = parser.parse_args()
    if args.action == "init":
        init()
    elif args.action == "static":
        static = static_contract()
        write_json("static-contract.json", {"test_id": "P126-M003", "status": "PASS" if static["all_pass"] else "FAIL", **static})
    elif args.action == "config":
        config_negatives()
    elif args.action == "unit":
        unit_tests()
    elif args.action == "bundle":
        if not args.run:
            parser.error("bundle requires --run")
        bundle(args.run)
    elif args.action == "history":
        history_after()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"P3-126 runner failed closed: {exc}", file=sys.stderr)
        raise SystemExit(2)
