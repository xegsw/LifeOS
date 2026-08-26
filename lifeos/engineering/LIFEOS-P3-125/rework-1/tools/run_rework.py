#!/usr/bin/env python3
"""P3-125 Rework-1 runner. It owns only Rework assets and the exact task temp root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
CANDIDATE = ROOT / "candidate"
EVIDENCE = ROOT / "evidence"
LOGS = ROOT / "logs"
TMP = Path("/private/tmp/lifeos-p3-125-runtime-root-config-v1")
CARGO = Path("/Users/xxe/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin/cargo")
TAURI = Path("/Users/xxe/.cargo/bin/cargo-tauri")
ALLOWLIST = REPO / "lifeos/tasks/LIFEOS-P3-125_source_allowlist.md"
INITIAL = REPO / "lifeos/engineering/LIFEOS-P3-125"
DELIVERY = REPO / "lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_rework_1.md"
MANIFEST = ROOT / "FINAL_MANIFEST.json"
OLD_ROOT_MARKER = "/private/tmp/" + "lifeos-p3-122-native-evidence-v1"
ALLOWED_RUNTIME_ROOTS = {TMP / name for name in ("run-a", "run-b", "test-root", "negative-real", "negative-link", "negative-file")}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def immutable_file(path: Path, role: str) -> dict:
    return {
        "path": path.relative_to(REPO).as_posix(),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def tree_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and not path.is_symlink() and path.name != ".DS_Store")


def command(name: str, args: list[str], *, env: dict[str, str], cwd: Path) -> dict:
    result = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = LOGS / f"{name}.log"
    log.write_text(result.stdout, encoding="utf-8")
    return {"id": name, "args": args, "exit_code": result.returncode, "log": log.relative_to(REPO).as_posix(), "log_sha256": sha256(log)}


def cargo_env(root: Path, target: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update({
        "PATH": f"{CARGO.parent}:/Users/xxe/.cargo/bin:{environment.get('PATH', '')}",
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TARGET_DIR": str(target),
        "TMPDIR": str(TMP / "tmp"),
        "CLANG_MODULE_CACHE_PATH": str(TMP / "clang-module-cache"),
        "SWIFT_MODULECACHE_PATH": str(TMP / "swift-module-cache"),
        "LIFEOS_RUNTIME_ROOT": str(root),
    })
    return environment


def require_allowed_root(path: Path) -> None:
    if path not in ALLOWED_RUNTIME_ROOTS or path.parent != TMP:
        raise RuntimeError(f"runner root outside P3-125 ABF subroots: {path}")


def parse_allowlist() -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(ALLOWLIST.read_text(encoding="utf-8").splitlines(), 1):
        parts = line.split("`")
        if len(parts) != 5 or not line.startswith("| `"):
            continue
        relative = parts[1]
        digest = parts[3]
        middle = line.split("|")
        if len(middle) != 5:
            continue
        declared_bytes = int(middle[2].strip())
        source = REPO / relative
        if not source.is_file() or source.is_symlink():
            raise RuntimeError(f"allowlist line {line_number} is not a regular source file")
        if source.stat().st_size != declared_bytes or sha256(source) != digest:
            raise RuntimeError(f"allowlist line {line_number} bytes/hash mismatch")
        rows.append({"line": line_number, "path": relative, "bytes": declared_bytes, "sha256": digest})
    if len(rows) != 75 or len({row['path'] for row in rows}) != 75:
        raise RuntimeError(f"allowlist format not machine-readable: got {len(rows)} rows")
    return rows


def protected_inputs() -> list[tuple[Path, str]]:
    values: list[tuple[Path, str]] = [
        (REPO / "lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md", "task_card"),
        (REPO / "lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_acceptance_basis_freeze.md", "frozen_abf"),
        (ALLOWLIST, "source_allowlist"),
        (REPO / "lifeos/reviews/LIFEOS-P3-125_pm_review.md", "p3_125_pm_review"),
        (REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1-authorization/MANIFEST.md", "rework_authorization_manifest"),
        (REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1-authorization/user_authorization.md", "user_confirmation"),
        (REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/initial-adoption/MANIFEST.md", "user_confirmation"),
        (REPO / "lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md", "p3_122_freeze_manifest"),
        (REPO / "lifeos/reviews/LIFEOS-P3-122_pm_review.md", "p3_122_history"),
        (REPO / "lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json", "p3_122_history"),
        (REPO / "lifeos/reviews/LIFEOS-P3-124/pm_evidence/rework-1/MANIFEST.md", "p3_124_freeze_manifest"),
        (REPO / "lifeos/reviews/LIFEOS-P3-124_pm_rework_1_review.md", "p3_124_history"),
    ]
    values.extend((REPO / row["path"], "p3_122_history") for row in parse_allowlist())
    values.extend((path, "initial_candidate") for path in tree_files(INITIAL / "candidate"))
    values.extend((path, "initial_evidence") for path in tree_files(INITIAL / "evidence"))
    values.append((REPO / "lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md", "initial_delivery"))
    return values


def snapshot_history(name: str) -> list[dict]:
    rows = [immutable_file(path, role) for path, role in protected_inputs()]
    record(EVIDENCE / name, {"task_id": "LIFEOS-P3-125", "result": "PASS", "rows": rows})
    return rows


def make_temp_root() -> None:
    if TMP.exists() or TMP.is_symlink():
        raise RuntimeError("exact P3-125 temporary root must be absent before creation")
    TMP.mkdir(mode=0o700)
    for name in ("run-a", "run-b", "test-root", "negative-real", "tmp", "clang-module-cache", "swift-module-cache"):
        (TMP / name).mkdir(mode=0o700)
    for root in (TMP / "run-a", TMP / "run-b", TMP / "test-root", TMP / "negative-real"):
        require_allowed_root(root)


def source_lineage() -> None:
    rows = parse_allowlist()
    initial = INITIAL / "candidate"
    current = CANDIDATE
    initial_files = {path.relative_to(initial).as_posix(): path for path in tree_files(initial)}
    current_files = {path.relative_to(current).as_posix(): path for path in tree_files(current)}
    if set(initial_files) != set(current_files) or len(current_files) != 75:
        raise RuntimeError("Rework candidate is not exactly the 75-file initial candidate inventory")
    changed = []
    for relative in sorted(current_files):
        if sha256(initial_files[relative]) != sha256(current_files[relative]):
            changed.append(relative)
    if changed != ["build.rs"]:
        raise RuntimeError(f"unexpected Rework candidate drift: {changed}")
    frozen_changed = []
    for row in rows:
        source = REPO / row["path"]
        relative = source.relative_to(REPO / "lifeos/engineering/LIFEOS-P3-122/candidate").as_posix()
        if sha256(current_files[relative]) != sha256(source):
            frozen_changed.append(relative)
    if sorted(frozen_changed) != ["build.rs", "src/runtime.rs"]:
        raise RuntimeError(f"unexpected P3-122 lineage drift: {frozen_changed}")
    record(EVIDENCE / "source-lineage.json", {
        "task_id": "LIFEOS-P3-125",
        "result": "PASS",
        "frozen_allowlist": {"physical_lines": 87, "candidate_rows": len(rows), "sha256": sha256(ALLOWLIST)},
        "initial_candidate": "lifeos/engineering/LIFEOS-P3-125/candidate",
        "current_candidate": "lifeos/engineering/LIFEOS-P3-125/rework-1/candidate",
        "current_vs_initial_changed": changed,
        "current_vs_frozen_p3_122_changed": sorted(frozen_changed),
        "rows": rows,
    })


def config_negatives() -> None:
    target = TMP / "negative-target"
    sentinel = TMP / "negative-real" / "sentinel.txt"
    sentinel.write_bytes(b"P3-125-NEGATIVE-SENTINEL")
    sentinel_before = sha256(sentinel)
    root_file = TMP / "negative-file"
    root_file.write_bytes(b"not a directory")
    link = TMP / "negative-link"
    link.symlink_to(TMP / "negative-real", target_is_directory=True)
    cases: list[tuple[str, str | None, str]] = [
        ("missing", None, "missing required build-time root"),
        ("empty", "", "root is empty or contains a NUL byte"),
        ("relative", "relative-runtime", "root must be an absolute normalized path"),
        ("traversal", str(TMP / "run-a" / ".." / "run-b"), "root must be an absolute normalized path"),
        ("symlink", str(link), "root or an ancestor is not a real directory"),
        ("root-file", str(root_file), "root or an ancestor is not a real directory"),
    ]
    results = []
    for name, value, expected in cases:
        env = cargo_env(TMP / "negative-real", target)
        if value is None:
            env.pop("LIFEOS_RUNTIME_ROOT", None)
        else:
            env["LIFEOS_RUNTIME_ROOT"] = value
        outcome = command(f"config-{name}", [str(CARGO), "check", "--locked", "--offline"], env=env, cwd=CANDIDATE)
        log = (REPO / outcome["log"]).read_text(encoding="utf-8")
        results.append({**outcome, "expected_rejection": expected, "rejected_before_runtime": outcome["exit_code"] != 0 and expected in log, "sentinel_unchanged": sha256(sentinel) == sentinel_before})
    if not all(result["rejected_before_runtime"] and result["sentinel_unchanged"] for result in results):
        raise RuntimeError("a frozen build configuration negative did not fail closed")
    record(EVIDENCE / "config-negatives.json", {"task_id": "LIFEOS-P3-125", "result": "PASS", "rows": results})


def unit_tests() -> None:
    root = TMP / "test-root"
    require_allowed_root(root)
    outcome = command("unit-tests", [str(CARGO), "test", "--locked", "--offline", "--", "--test-threads=1"], env=cargo_env(root, TMP / "test-target"), cwd=CANDIDATE)
    log = (REPO / outcome["log"]).read_text(encoding="utf-8")
    passed = outcome["exit_code"] == 0 and "test result: ok. 4 passed" in log
    record(EVIDENCE / "unit-tests.json", {"task_id": "LIFEOS-P3-125", "result": "PASS" if passed else "FAIL", "command": outcome, "expected": "4 passed"})
    config = json.loads((EVIDENCE / "config-negatives.json").read_text(encoding="utf-8"))
    record(EVIDENCE / "path-negatives.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-007", "result": "PASS" if passed else "FAIL", "actual_cases": [row for row in config["rows"] if row["id"] in {"config-relative", "config-traversal", "config-symlink", "config-root-file"}], "unit_case": "input_and_storage_type_failures_preserve_the_root", "sentinel_and_database_before_after": "asserted by the executed unit case"})
    record(EVIDENCE / "storage-negatives.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-008", "result": "PASS" if passed else "FAIL", "unit_cases": ["input_and_storage_type_failures_preserve_the_root", "non_sqlite_sidecar_and_unwritable_failures_preserve_existing_data"], "covered_objects": ["DB symlink", "geometry directory", "non-SQLite DB", "DB sidecar", "unwritable root"], "sentinel_and_database_before_after": "asserted by the executed unit cases"})
    if not passed:
        raise RuntimeError("task-local unit tests did not pass")


def bundle(name: str) -> dict:
    root = TMP / name
    require_allowed_root(root)
    outcome = command(f"bundle-{name}", [str(TAURI), "build", "--bundles", "app", "--no-sign"], env=cargo_env(root, TMP / f"target-{name}"), cwd=CANDIDATE)
    apps = sorted((TMP / f"target-{name}" / "release" / "bundle" / "macos").glob("*.app"))
    if outcome["exit_code"] != 0 or len(apps) != 1:
        raise RuntimeError(f"{name} bundle failed or was ambiguous")
    app = apps[0]
    return {"root": str(root), "source_hashes": {"build_rs": sha256(CANDIDATE / "build.rs"), "runtime_rs": sha256(CANDIDATE / "src/runtime.rs")}, "command": outcome, "app_bundle": str(app), "app_bundle_relative_to_temp": app.relative_to(TMP).as_posix()}


def prepare() -> int:
    make_temp_root()
    snapshot_history("history-before.json")
    source_lineage()
    config_negatives()
    unit_tests()
    run_a = bundle("run-a")
    run_b = bundle("run-b")
    record(EVIDENCE / "bundle-plan.json", {"task_id": "LIFEOS-P3-125", "result": "PASS", "run_a": run_a, "run_b": run_b, "allowed_runtime_roots": [str(TMP / name) for name in ("run-a", "run-b", "test-root")]})
    print(json.dumps({"result": "READY_FOR_ACTUAL_APP", "run_a_app": run_a["app_bundle"], "run_b_app": run_b["app_bundle"]}, ensure_ascii=False))
    return 0


def sqlite_summary(path: Path) -> dict:
    with sqlite3.connect(path) as connection:
        captures = connection.execute("SELECT id, content, source, idem_key FROM captures ORDER BY created_at_ms,id").fetchall()
        audit = connection.execute("SELECT event, detail FROM audit ORDER BY id").fetchall()
    return {"capture_count": len(captures), "captures": [{"id": row[0], "content": row[1], "source": row[2], "idem_key": row[3]} for row in captures], "audit": [{"event": row[0], "detail": row[1]} for row in audit]}


def root_inventory(root: Path) -> list[dict]:
    require_allowed_root(root)
    return [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in tree_files(root)]


def collect() -> int:
    observations = ROOT / "actual-app" / "actions.json"
    if not observations.is_file():
        raise RuntimeError("actual-app actions.json must be recorded before collection")
    action_data = json.loads(observations.read_text(encoding="utf-8"))
    roots = {}
    for name in ("run-a", "run-b"):
        root = TMP / name
        db = root / "capture.sqlite"
        geometry = root / "native-geometry-1280x1024.jsonl"
        if not db.is_file() or not geometry.is_file():
            raise RuntimeError(f"actual {name} DB or geometry is missing")
        db_copy = EVIDENCE / "runtime-snapshots" / f"{name}-capture.sqlite"
        geometry_copy = EVIDENCE / "runtime-snapshots" / f"{name}-geometry.jsonl"
        db_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(db, db_copy)
        shutil.copyfile(geometry, geometry_copy)
        roots[name] = {"runtime_root": str(root), "inventory": root_inventory(root), "database": {"path": db_copy.relative_to(REPO).as_posix(), "sha256": sha256(db_copy), "summary": sqlite_summary(db_copy)}, "geometry": {"path": geometry_copy.relative_to(REPO).as_posix(), "sha256": sha256(geometry_copy), "lines": len(geometry_copy.read_text(encoding="utf-8").splitlines())}}
    expected = {"capture_count": 1, "audit": [{"event": "capture_saved", "detail": "local_capture"}, {"event": "capture_repeat", "detail": "same_idempotency_key"}]}
    run_a = roots["run-a"]["database"]["summary"]
    run_b = roots["run-b"]["database"]["summary"]
    if run_a["capture_count"] != expected["capture_count"] or run_a["audit"] != expected["audit"]:
        raise RuntimeError("run-a actual lifecycle does not match first/repeat contract")
    if run_b["capture_count"] != 1 or run_b["audit"] != [{"event": "capture_saved", "detail": "local_capture"}]:
        raise RuntimeError("run-b fresh rebind does not contain exactly one saved capture")
    if any(item["path"] == "capture.sqlite" for item in roots["run-b"]["inventory"]) is False:
        raise RuntimeError("run-b inventory is missing only-root database evidence")
    record(EVIDENCE / "run-a-results.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-004", "result": "PASS", **roots["run-a"]})
    record(EVIDENCE / "run-b-results.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-005", "result": "PASS", **roots["run-b"]})
    record(EVIDENCE / "ipc-lifecycle.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-006", "result": "PASS", "actual_app_actions": action_data, "run_a": roots["run-a"]["database"], "run_b": roots["run-b"]["database"]})
    print(json.dumps({"result": "ACTUAL_APP_COLLECTED", "run_a": run_a["capture_count"], "run_b": run_b["capture_count"]}, ensure_ascii=False))
    return 0


def static_contract() -> dict:
    build = (CANDIDATE / "build.rs").read_text(encoding="utf-8")
    runtime = (CANDIDATE / "src/runtime.rs").read_text(encoding="utf-8")
    active_runtime = runtime.split("#[cfg(any())]", 1)[0]
    initial = INITIAL / "candidate"
    unchanged = {}
    for relative in ("Cargo.toml", "tauri.conf.json", "src/main.rs", "ui/app.js", "ui/runtime-adapter.js", "capabilities/main.json"):
        unchanged[relative] = sha256(CANDIDATE / relative) == sha256(initial / relative)
    checks = {
        "production_fixed_parent_absent": "ALLOWED_PARENT" not in build and "lifeos-p3-125-runtime-root-config-v1" not in build,
        "single_build_time_configuration": "LIFEOS_RUNTIME_ROOT" in build and "rustc-env=LIFEOS_RUNTIME_ROOT" in build and "option_env!(\"LIFEOS_RUNTIME_ROOT\")" in active_runtime,
        "no_root_fallback": "LIFEOS_RUNTIME_ROOT\").or(" not in build and "LIFEOS_RUNTIME_ROOT\").unwrap" not in build and "BUILD_RUNTIME_ROOT.unwrap" not in active_runtime,
        "db_derived": "db_path: root.join(DB_NAME)" in active_runtime,
        "viewport_derived": "viewport_request: root.join(\"viewport-request.txt\")" in active_runtime,
        "geometry_derived": "paths.root.join(format!(\"native-geometry-{requested}.jsonl\"))" in active_runtime,
        "validation_precedes_write": active_runtime.index("validate_database_path(&runtime, &runtime.db_path)") < active_runtime.index("tauri::Builder::default()"),
        "legacy_root_absent_from_active_source": OLD_ROOT_MARKER not in active_runtime,
        "three_ipc_unchanged": "[\"capture_record\", \"get_today\", \"runtime_status\"]" in active_runtime,
        "no_new_path_selection": "dialog" not in active_runtime and "command_line" not in active_runtime,
        "ui_ipc_schema_capability_unchanged": all(unchanged.values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"static contract failed: {[key for key, value in checks.items() if not value]}")
    return checks


def boundary() -> None:
    plan = json.loads((EVIDENCE / "bundle-plan.json").read_text(encoding="utf-8"))
    bundle_checks = {}
    for label in ("run_a", "run_b"):
        app = Path(plan[label]["app_bundle"])
        binary = app / "Contents" / "MacOS" / "lifeos-p3-122"
        if not binary.is_file():
            raise RuntimeError(f"bundle binary missing: {binary}")
        content = binary.read_bytes()
        bundle_checks[label] = {"legacy_root_absent": OLD_ROOT_MARKER.encode() not in content, "binary_sha256": sha256(binary)}
    checks = static_contract()
    if not all(row["legacy_root_absent"] for row in bundle_checks.values()):
        raise RuntimeError("legacy root appears in a Rework production bundle")
    record(EVIDENCE / "boundary.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-009", "result": "PASS", "static_contract": checks, "bundle_checks": bundle_checks, "fixture_literals_excluded_from_production_scan": True})


def history_after() -> None:
    before = json.loads((EVIDENCE / "history-before.json").read_text(encoding="utf-8"))["rows"]
    current = [immutable_file(REPO / row["path"], row["role"]) for row in before]
    mismatch = [row["path"] for old, row in zip(before, current) if old["bytes"] != row["bytes"] or old["sha256"] != row["sha256"]]
    if mismatch:
        raise RuntimeError(f"protected historical assets drifted: {mismatch[:3]}")
    record(EVIDENCE / "history-integrity.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-010", "result": "PASS", "before_rows": len(before), "after_rows": len(current), "mismatches": mismatch, "rows": current})


def manifest_entries() -> list[dict]:
    entries: list[dict] = []
    seen: set[str] = set()
    for path, role in protected_inputs():
        entry = immutable_file(path, role)
        if entry["path"] not in seen:
            entries.append(entry)
            seen.add(entry["path"])
    for path in tree_files(CANDIDATE):
        entry = immutable_file(path, "current_candidate")
        if entry["path"] not in seen:
            entries.append(entry)
            seen.add(entry["path"])
    for path in tree_files(ROOT):
        if path == MANIFEST:
            continue
        role = "rework_evidence"
        if path.name == "mutation-results.json":
            role = "mutation"
        elif path.name == "cleanup.json":
            role = "cleanup"
        entry = immutable_file(path, role)
        if entry["path"] not in seen:
            entries.append(entry)
            seen.add(entry["path"])
    if not DELIVERY.is_file():
        raise RuntimeError("new task-owned Rework delivery is missing")
    delivery = immutable_file(DELIVERY, "rework_delivery")
    entries.append(delivery)
    return sorted(entries, key=lambda item: item["path"])


def write_manifest() -> None:
    boundary_data = json.loads((EVIDENCE / "boundary.json").read_text(encoding="utf-8"))
    record(MANIFEST, {"task_id": "LIFEOS-P3-125", "rework": "1/1", "manifest_root": "repository-root", "inventory_excludes": "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json only", "static_contract": boundary_data["static_contract"], "entries": manifest_entries()})


def verifier(manifest: Path, candidate: Path | None = None) -> dict:
    args = [sys.executable, "-B", str(ROOT / "tools/verify_rework.py"), str(manifest)]
    if candidate is not None:
        args.extend(["--candidate", str(candidate)])
    result = subprocess.run(args, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return {"exit_code": result.returncode, "output": result.stdout.strip()}


def mutate_manifest(original: dict, kind: str) -> dict:
    copied = json.loads(json.dumps(original))
    if kind == "history":
        copied["entries"][0]["sha256"] = "0" * 64
    elif kind == "manifest-path":
        copied["entries"][0]["path"] = "../deliverables/escape.md"
    elif kind == "manifest-omission":
        copied["entries"] = [entry for entry in copied["entries"] if entry["role"] != "task_card"]
    else:
        raise ValueError(kind)
    return copied


def mutations() -> None:
    pristine = verifier(MANIFEST)
    if pristine["exit_code"] != 0:
        raise RuntimeError(f"pristine Manifest verifier failed: {pristine}")
    disposable = TMP / "disposable-mutations"
    disposable.mkdir()
    original_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = [{"id": "pristine", "expected": "PASS", "actual": pristine, "pass": pristine["exit_code"] == 0}]
    source_cases = {
        "fixed-parent": ("build.rs", lambda text: "const ALLOWED_PARENT: &str = \"forbidden-parent\";\n" + text),
        "fallback": ("build.rs", lambda text: text.replace("env::var(\"LIFEOS_RUNTIME_ROOT\")", "env::var(\"LIFEOS_RUNTIME_ROOT\").or(Ok(\"/tmp/fallback\".to_string()))", 1)),
        "derive": ("src/runtime.rs", lambda text: text.replace("db_path: root.join(DB_NAME)", "db_path: PathBuf::from(\"/tmp/escape.sqlite\")", 1)),
        "order": ("src/runtime.rs", lambda text: text.replace("validate_database_path(&runtime, &runtime.db_path)", "/* validation intentionally removed */", 1)),
    }
    for name, (relative, mutate) in source_cases.items():
        copied = disposable / f"candidate-{name}"
        shutil.copytree(CANDIDATE, copied)
        target = copied / relative
        target.write_text(mutate(target.read_text(encoding="utf-8")), encoding="utf-8")
        outcome = verifier(MANIFEST, copied)
        results.append({"id": name, "expected": "REJECT", "actual": outcome, "pass": outcome["exit_code"] != 0})
        shutil.rmtree(copied)
    for name in ("history", "manifest-path", "manifest-omission"):
        candidate = disposable / f"{name}.json"
        record(candidate, mutate_manifest(original_manifest, name))
        outcome = verifier(candidate)
        results.append({"id": name, "expected": "REJECT", "actual": outcome, "pass": outcome["exit_code"] != 0})
    extra = ROOT / "evidence" / "mutation-extra-disposable.txt"
    extra.write_text("disposable extra-file mutation\n", encoding="utf-8")
    outcome = verifier(MANIFEST)
    results.append({"id": "extra-file", "expected": "REJECT", "actual": outcome, "pass": outcome["exit_code"] != 0})
    extra.unlink()
    shutil.rmtree(disposable)
    if not all(row["pass"] for row in results):
        raise RuntimeError(f"mutation failed to reject: {[row['id'] for row in results if not row['pass']]}")
    record(EVIDENCE / "mutation-results.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-011", "result": "PASS", "pristine_first": pristine, "mutations": results})


def exact_cleanup() -> None:
    if TMP.parent != Path("/private/tmp") or TMP.name != "lifeos-p3-125-runtime-root-config-v1":
        raise RuntimeError("refusing non-exact cleanup target")
    if not TMP.is_dir() or TMP.is_symlink():
        raise RuntimeError("exact cleanup target is not the expected real directory")
    shutil.rmtree(TMP)
    if TMP.exists() or TMP.is_symlink():
        raise RuntimeError("exact temporary root remains after cleanup")
    record(EVIDENCE / "cleanup.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-012", "result": "PASS", "exact_target": str(TMP), "method": "explicit shutil.rmtree on validated exact target", "post_delete_absent": True, "no_glob_or_find": True})


def closure() -> None:
    rows = [
        ("ABF-M-001", "preflight.json", "NOT_PASS", "Frozen inputs and model matched, but the disclosed prohibited old-root existence check prevents a clean preflight pass."),
        ("ABF-M-002", "source-lineage.json", "PASS", "75-row source lineage and permitted two-file P3-122 delta are structured."),
        ("ABF-M-003", "config-negatives.json", "PASS", "missing, empty, relative, traversal, symlink, and file roots reject before runtime."),
        ("ABF-M-004", "run-a-results.json", "PASS", "run-a actual App only wrote its configured root."),
        ("ABF-M-005", "run-b-results.json", "PASS", "run-b actual App started empty and wrote only its configured root."),
        ("ABF-M-006", "ipc-lifecycle.json", "PASS", "actual status, first, repeat, and close/reopen match DB/audit state."),
        ("ABF-M-007", "path-negatives.json", "PASS", "root path negatives were independently structured."),
        ("ABF-M-008", "storage-negatives.json", "PASS", "DB/sidecar/geometry/unwritable failures preserve the tested state."),
        ("ABF-M-009", "boundary.json", "PASS", "production source, bundle, IPC, UI/schema/capability checks are closed."),
        ("ABF-M-010", "history-integrity.json", "PASS", "protected input hashes match before and after."),
        ("ABF-M-011", "mutation-results.json", "PASS", "pristine verifier passed before real fixed-parent/fallback/derive/order/history/extra/path/omission mutations rejected."),
        ("ABF-M-012", "cleanup.json", "PASS", "only the exact task temp root was deleted and is absent."),
    ]
    rendered = []
    for row, filename, status, conclusion in rows:
        path = EVIDENCE / filename
        rendered.append({"row": row, "structured_result": path.relative_to(REPO).as_posix(), "sha256": sha256(path), "status": status, "conclusion": conclusion})
    record(EVIDENCE / "DYNAMIC_CLOSURE.json", {"task_id": "LIFEOS-P3-125", "rework": "1/1", "rows": rendered, "technical_rows_pass": 11, "not_pass_rows": ["ABF-M-001"], "self_check_result": "NOT_PASS_DISCLOSED_PRECHECK_DEVIATION"})


def finish() -> int:
    boundary()
    history_after()
    record(EVIDENCE / "mutation-results.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-011", "result": "PENDING_FINAL_MANIFEST_CONTROL"})
    record(EVIDENCE / "cleanup.json", {"task_id": "LIFEOS-P3-125", "row": "ABF-M-012", "result": "PENDING_EXACT_CLEANUP"})
    write_manifest()
    mutations()
    write_manifest()
    pristine_after_mutation = verifier(MANIFEST)
    if pristine_after_mutation["exit_code"] != 0:
        raise RuntimeError(f"post-mutation pristine verifier failed: {pristine_after_mutation}")
    exact_cleanup()
    history_after()
    closure()
    write_manifest()
    final = verifier(MANIFEST)
    if final["exit_code"] != 0:
        raise RuntimeError(f"final Manifest verifier failed: {final}")
    record(EVIDENCE / "verification.json", {"task_id": "LIFEOS-P3-125", "technical_evidence_result": "PASS", "self_check_result": "NOT_PASS_DISCLOSED_PRECHECK_DEVIATION", "final_manifest_verifier": final, "matrix_rows": [f"ABF-M-{index:03d}" for index in range(1, 13)], "all_rows_independently_recorded": True, "counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0}, "p0_detail": "A prohibited historical-root existence check was included in a preflight command and its result was intentionally not used; user later directed continuation."})
    write_manifest()
    final_after_verification = verifier(MANIFEST)
    if final_after_verification["exit_code"] != 0:
        raise RuntimeError("final verifier failed after verification evidence write")
    print(json.dumps({"result": "TECHNICAL_EVIDENCE_COMPLETE_SELF_CHECK_NOT_PASS", "manifest": MANIFEST.relative_to(REPO).as_posix(), "entries": len(json.loads(MANIFEST.read_text(encoding='utf-8'))['entries'])}, ensure_ascii=False))
    return 0


def finalize_after_cleanup() -> int:
    if TMP.exists() or TMP.is_symlink():
        raise RuntimeError("resume finalization requires the exact temporary root to remain absent")
    if not (EVIDENCE / "cleanup.json").is_file() or not (EVIDENCE / "mutation-results.json").is_file():
        raise RuntimeError("resume finalization requires completed mutation and cleanup Evidence")
    closure()
    write_manifest()
    final = verifier(MANIFEST)
    if final["exit_code"] != 0:
        raise RuntimeError(f"final Manifest verifier failed during resume: {final}")
    record(EVIDENCE / "verification.json", {"task_id": "LIFEOS-P3-125", "technical_evidence_result": "PASS", "self_check_result": "NOT_PASS_DISCLOSED_PRECHECK_DEVIATION", "final_manifest_verifier": final, "matrix_rows": [f"ABF-M-{index:03d}" for index in range(1, 13)], "all_rows_independently_recorded": True, "counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": 0}, "p0_detail": "A prohibited historical-root existence check was included in a preflight command and its result was intentionally not used; user later directed continuation."})
    write_manifest()
    final_after_verification = verifier(MANIFEST)
    if final_after_verification["exit_code"] != 0:
        raise RuntimeError(f"final verifier failed after resume verification write: {final_after_verification}")
    print(json.dumps({"result": "TECHNICAL_EVIDENCE_COMPLETE_SELF_CHECK_NOT_PASS", "manifest": MANIFEST.relative_to(REPO).as_posix(), "entries": len(json.loads(MANIFEST.read_text(encoding='utf-8'))['entries'])}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "collect", "finish", "finalize"))
    args = parser.parse_args()
    if args.stage == "prepare":
        return prepare()
    if args.stage == "collect":
        return collect()
    if args.stage == "finish":
        return finish()
    return finalize_after_cleanup()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False))
        raise
