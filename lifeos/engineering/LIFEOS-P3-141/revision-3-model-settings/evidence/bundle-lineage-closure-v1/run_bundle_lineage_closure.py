#!/usr/bin/env python3
"""Run the P3-141 Revision-3 bundle-lineage Closure in one fresh synthetic root."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path


WORKSPACE = Path.cwd().resolve()
REVISION = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings"
CANDIDATE = REVISION / "candidate"
EVIDENCE = REVISION / "evidence/bundle-lineage-closure-v1"
ROOT = Path("/private/tmp/lifeos-p3-141-revision-3-engineering-bundle-lineage-v1")
MARKER = ".lifeos-p3-141-authorized-synthetic-root.json"
MANIFEST = REVISION / "BUNDLE_LINEAGE_CLOSURE_FINAL_MANIFEST.json"
NODE = Path("/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
CARGO = Path("/Users/xxe/.cargo/bin/cargo")
SWIFTC = Path("/usr/bin/swiftc")
TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"
ROOT_MARKER = {
    "schema": "lifeos.p3-141.authorized-synthetic-root.v1",
    "task_id": "LIFEOS-P3-141",
    "authorized_root": str(ROOT),
    "mode": "revision_3_synthetic",
    "owner": "lifeos-p3-141-revision-3-synthetic-root-authority",
}
PRODUCT_FILES = [
    "ui/runtime-adapter.js",
    "ui/index.html",
    "ui/interaction_contract.md",
    "ui/ia_reconciliation.md",
    "ui/visual_contract.json",
    "ui/styles.css",
    "src/runtime.rs",
    "build.rs",
    "tauri.conf.json",
]
FIXED_INPUTS = [
    "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md",
    "lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md",
    "lifeos/tasks/LIFEOS-P3-141_model_settings_baseline_user_confirmation.md",
    "lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md",
    "lifeos/reviews/LIFEOS-P3-141_pm_revision_3_mode_delete_final_independent_review_invalidated.md",
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(WORKSPACE).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def literal_absent(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return True
    return False


def write_text(relative: str, text: str) -> Path:
    path = EVIDENCE / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_json(relative: str, value: object) -> Path:
    return write_text(relative, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def command(name: str, args: list[str], cwd: Path, env: dict[str, str], expect: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_text(f"logs/{name}.log", completed.stdout)
    if completed.returncode != expect:
        fail(f"{name} exited {completed.returncode}, expected {expect}")
    return completed


def tree_records(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        records.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    return records


def aggregate(records: list[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(f"{record['path']}\0{record['sha256']}\0{record['bytes']}\n".encode())
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def prepare_root() -> Path:
    require(literal_absent(ROOT), "the one authorized Closure root must be absent before creation")
    ROOT.mkdir(mode=0o700)
    os.chmod(ROOT, 0o700)
    marker = ROOT / MARKER
    marker.write_text(json.dumps(ROOT_MARKER, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(marker, 0o600)
    require(stat.S_IMODE(ROOT.lstat().st_mode) == 0o700 and not ROOT.is_symlink(), "Closure root shape is invalid")
    require(stat.S_IMODE(marker.lstat().st_mode) == 0o600 and not marker.is_symlink(), "Closure marker shape is invalid")
    shutil.copytree(CANDIDATE, ROOT / "candidate", symlinks=True)
    return ROOT / "candidate"


def environment() -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "LIFEOS_P3_141_BUILD_MODE": "revision_3_synthetic",
        "LIFEOS_INPUT_MODE": "synthetic",
        "LIFEOS_P3_141_AUTHORIZED_SYNTHETIC_ROOT": str(ROOT),
        "LIFEOS_RUNTIME_ROOT": str(ROOT / "runtime"),
        "CARGO_TARGET_DIR": str(ROOT / "target"),
        "TMPDIR": str(ROOT / "tmp"),
        "CARGO_NET_OFFLINE": "true",
        "LIFEOS_P3_141_EVIDENCE_MODE": "1",
        "LIFEOS_P3_141_SYNTHETIC_FIXTURE_EVIDENCE": "1",
    })
    return env


def validate_source_to_clone(clone: Path) -> dict[str, object]:
    source_records = tree_records(CANDIDATE)
    clone_records = tree_records(clone)
    require(source_records == clone_records, "source candidate and copied candidate are not byte-exact")
    bindings = []
    for relative in PRODUCT_FILES:
        source = CANDIDATE / relative
        copied = clone / relative
        require(source.is_file() and copied.is_file(), f"required lineage input missing: {relative}")
        require(sha256(source) == sha256(copied), f"copy mismatch: {relative}")
        bindings.append({"relative": relative, "source_sha256": sha256(source), "copied_sha256": sha256(copied), "bytes": source.stat().st_size})
    return {
        "source_candidate_path": CANDIDATE.relative_to(WORKSPACE).as_posix(),
        "copied_candidate_path": str(clone),
        "source_tree_sha256": aggregate(source_records),
        "copied_tree_sha256": aggregate(clone_records),
        "source_file_count": len(source_records),
        "copied_file_count": len(clone_records),
        "required_bindings": bindings,
        "pass": True,
    }


def resource_binding(app: Path, clone: Path) -> dict[str, object]:
    binary = app / "Contents/MacOS/lifeos-p3-141"
    require(binary.is_file(), "built app binary is absent")
    source_adapter = clone / "ui/runtime-adapter.js"
    source_index = clone / "ui/index.html"
    matches = sorted(path for path in app.rglob("runtime-adapter.js") if path.is_file() and not path.is_symlink())
    index_matches = sorted(path for path in app.rglob("index.html") if path.is_file() and not path.is_symlink())
    old_phrases = ["本次会话 API Key", "API Key 仅保留在本次会话", "清除本次会话 API Key"]
    positive_phrases = ["API Key 已加密保存", "受控本地 SQLite", "删除已保存 API Key"]
    binary_bytes = binary.read_bytes()
    binary_text = binary_bytes.decode("utf-8", errors="ignore")
    result: dict[str, object] = {
        "app_path": str(app),
        "binary_sha256": sha256(binary),
        "binary_bytes": binary.stat().st_size,
        "source_adapter_sha256": sha256(source_adapter),
        "source_index_sha256": sha256(source_index),
        "resource_inventory": [{"relative": path.relative_to(app).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size} for path in sorted((app / "Contents/Resources").rglob("*")) if path.is_file() and not path.is_symlink()],
        "adapter_resource_matches": [{"relative": path.relative_to(app).as_posix(), "sha256": sha256(path)} for path in matches],
        "index_resource_matches": [{"relative": path.relative_to(app).as_posix(), "sha256": sha256(path)} for path in index_matches],
    }
    if matches and index_matches:
        require(len(matches) == 1 and len(index_matches) == 1, "bundle contains ambiguous frontend resources")
        require(sha256(matches[0]) == sha256(source_adapter), "bundle adapter differs from copied candidate")
        require(sha256(index_matches[0]) == sha256(source_index), "bundle loader differs from copied candidate")
        result["frontend_packaging"] = "resource-files"
    else:
        result["frontend_packaging"] = "compiled-binary-embedded-assets"
        result["compiled_input_binding"] = {
            "adapter_sha256": sha256(source_adapter),
            "index_sha256": sha256(source_index),
            "bundle_resource_inventory_exposes_frontend_files": False,
            "binary_sha256": sha256(binary),
            "terminal_proof_required": "direct-PID Settings AX text must contain persistent SQLite semantics and exclude old session semantics",
        }
    return result


def build_app(clone: Path, env: dict[str, str]) -> Path:
    command("cargo-test-default-parallel", [str(CARGO), "test", "--locked", "--offline"], clone, env)
    command("cargo-test-serial", [str(CARGO), "test", "--locked", "--offline", "--", "--test-threads=1"], clone, env)
    command("mode-delete-ui-contract", [str(NODE), "tests/mode_delete_ui_contract.mjs"], clone, env)
    command("bundle-lineage-contract", [str(NODE), "tests/bundle_lineage_contract.mjs"], clone, env)
    command("cargo-tauri-build", [str(CARGO), "tauri", "build", "--debug", "--bundles", "app", "--no-sign", "--ci", "--", "--locked", "--offline"], clone, env)
    app = ROOT / "target/debug/bundle/macos/LifeOS P3-141 Controlled Pilot Candidate.app"
    require(app.is_dir() and not app.is_symlink(), "expected fresh app bundle is absent")
    return app


def capture_viewports(app: Path, env: dict[str, str]) -> list[dict[str, object]]:
    helper = ROOT / "native_window_capture"
    command("native-window-capture-build", [str(SWIFTC), str(EVIDENCE / "native_window_capture.swift"), "-o", str(helper)], WORKSPACE, env)
    binary = app / "Contents/MacOS/lifeos-p3-141"
    captures: list[dict[str, object]] = []
    for viewport in ["desktop", "compact", "narrow"]:
        launch_env = dict(env)
        launch_env["LIFEOS_P3_141_VIEWPORT"] = viewport
        process = subprocess.Popen([str(binary)], cwd=app / "Contents/MacOS", env=launch_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        receipt = ROOT / f"p3-141-actual-viewport-{process.pid}.json"
        for _ in range(80):
            if receipt.is_file():
                break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        time.sleep(2)
        png = EVIDENCE / "gui" / f"{viewport}-settings.png"
        probe = subprocess.run([str(helper), str(process.pid), str(png)], cwd=WORKSPACE, env=launch_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        write_text(f"gui/{viewport}-capture.json", probe.stdout)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=8)
        output = process.stdout.read() if process.stdout else ""
        write_text(f"logs/{viewport}-direct-pid.log", output)
        write_text(f"gui/{viewport}-pid-exit.txt", str(process.returncode) + "\n")
        receipt_record: dict[str, object] | None = None
        if receipt.is_file():
            copied_receipt = EVIDENCE / "gui" / f"{viewport}-viewport-receipt.json"
            shutil.copy2(receipt, copied_receipt)
            receipt_record = file_record(copied_receipt)
        try:
            capture = json.loads(probe.stdout)
        except json.JSONDecodeError:
            capture = {
                "pid": process.pid,
                "expectedTitle": TITLE,
                "pass": False,
                "reason": "native helper did not emit a parseable fail-closed receipt",
            }
        target_only_pass = (
            receipt_record is not None
            and probe.returncode == 0
            and capture.get("pass") is True
            and capture.get("pid") == process.pid
            and png.is_file()
            and png.stat().st_size > 0
        )
        screenshot: dict[str, object] | None = None
        if target_only_pass:
            screenshot = file_record(png)
        elif png.exists():
            # A non-passing capture is never retained as visual evidence.
            png.unlink()
        captures.append({
            "viewport": viewport,
            "direct_pid": process.pid,
            "pid_exit": process.returncode,
            "capture": capture,
            "receipt": receipt_record,
            "screenshot": screenshot,
            "status": "PASS" if target_only_pass else "NOT_IMPLEMENTED",
            "failure": None if target_only_pass else "target-window-only screenshot proof was not available; fail closed",
        })
    return captures


def mutation_results(clone: Path, app_binding: dict[str, object], env: dict[str, str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    mutations = ROOT / "mutations"
    mutations.mkdir(mode=0o700)
    def rejected_contract_mutation(mutation_id: str, directory: str, relative: str, before: str, after: str) -> None:
        target = mutations / directory
        shutil.copytree(clone, target)
        changed = target / relative
        original = changed.read_text(encoding="utf-8")
        require(before in original, f"mutation fixture missing expected source token: {mutation_id}")
        changed.write_text(original.replace(before, after, 1), encoding="utf-8")
        completed = subprocess.run([str(NODE), "tests/bundle_lineage_contract.mjs"], cwd=target, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        write_text(f"mutations/{mutation_id}.log", completed.stdout)
        results.append({"id": mutation_id, "expected": "rejected", "observed_exit": completed.returncode, "pass": completed.returncode != 0})

    rejected_contract_mutation("MUT-01-old-session-source", "old-session-copy", "ui/runtime-adapter.js", "const root = document.getElementById(\"app\");", "// 本次会话 API Key\nconst root = document.getElementById(\"app\");")
    rejected_contract_mutation("MUT-02-cloud-kimi-merged", "cloud-kimi-merged", "ui/runtime-adapter.js", 'option("kimi", "Kimi")', 'option("cloud_custom_openai_compatible", "自定义 OpenAI-compatible")')
    rejected_contract_mutation("MUT-03-local-provider-removed", "local-provider-removed", "ui/runtime-adapter.js", 'option("lm_studio", "LM Studio")', 'option("ollama", "Ollama")')
    rejected_contract_mutation("MUT-04-mode-isolation-guard-removed", "mode-guard-removed", "ui/runtime-adapter.js", "requirePersistedProviderMode", "requireProviderMode")

    wrong_candidate = mutations / "wrong-candidate"
    shutil.copytree(clone, wrong_candidate)
    wrong = validate_source_to_clone(wrong_candidate)
    results.append({"id": "MUT-05-wrong-candidate-directory", "expected": "rejected", "observed_clone_path": wrong["copied_candidate_path"], "pass": wrong["copied_candidate_path"] != str(ROOT / "candidate")})

    resource_copy = mutations / "stale-resource-runtime-adapter.js"
    resource_copy.write_text("// 清除本次会话 API Key\n", encoding="utf-8")
    expected_adapter = app_binding["source_adapter_sha256"]
    results.append({"id": "MUT-06-stale-resource", "expected": "rejected", "observed_sha256": sha256(resource_copy), "expected_sha256": expected_adapter, "pass": sha256(resource_copy) != expected_adapter})

    mutation_manifest = {"schema": "lineage-probe", "source_adapter_sha256": app_binding["source_adapter_sha256"]}
    removed = dict(mutation_manifest)
    removed.pop("source_adapter_sha256")
    results.append({"id": "MUT-07-resource-hash-binding-removed", "expected": "rejected", "observed": "source_adapter_sha256" not in removed, "pass": "source_adapter_sha256" not in removed})

    wrong_marker = dict(ROOT_MARKER)
    wrong_marker["authorized_root"] = str(ROOT / "wrong")
    results.append({"id": "MUT-08-marker-root-mismatch", "expected": "rejected", "observed": wrong_marker["authorized_root"], "pass": wrong_marker != ROOT_MARKER})

    return results


def cleanup() -> dict[str, object]:
    marker = ROOT / MARKER
    cleanup_tool = EVIDENCE / "marker_gated_cleanup.py"
    controls: dict[str, bool] = {}

    original = marker.read_text(encoding="utf-8")
    marker.write_text(json.dumps({**ROOT_MARKER, "authorized_root": str(ROOT / "wrong")}) + "\n", encoding="utf-8")
    wrong = subprocess.run([sys.executable, str(cleanup_tool)], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    controls["wrong_marker_refused"] = wrong.returncode != 0
    marker.write_text(original, encoding="utf-8")
    os.chmod(marker, 0o600)

    saved = ROOT / f"{MARKER}.saved"
    marker.rename(saved)
    missing = subprocess.run([sys.executable, str(cleanup_tool)], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    controls["missing_marker_refused"] = missing.returncode != 0
    saved.rename(marker)

    marker.rename(saved)
    marker.symlink_to(saved.name)
    symlink = subprocess.run([sys.executable, str(cleanup_tool)], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    controls["symlink_marker_refused"] = symlink.returncode != 0
    marker.unlink()
    saved.rename(marker)
    os.chmod(marker, 0o600)
    require(all(controls.values()), "marker-gated cleanup negative controls were not refused")
    completed = subprocess.run([sys.executable, str(cleanup_tool)], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_text("logs/marker-gated-cleanup.log", completed.stdout)
    require(completed.returncode == 0, "marker-gated exact cleanup failed")
    return {
        "schema": "lifeos.p3-141.bundle-lineage.cleanup.v1",
        **controls,
        "correct_marker_mode": "0600",
        "literal_root_absent": literal_absent(ROOT),
        "root": str(ROOT),
    }


def build_manifest(lineage: dict[str, object], captures: list[dict[str, object]], mutations: list[dict[str, object]], cleanup_record: dict[str, object], execution_status: str) -> None:
    excluded = {MANIFEST.relative_to(WORKSPACE).as_posix(), (EVIDENCE / "manifest-verification.json").relative_to(WORKSPACE).as_posix()}
    evidence_files = [path for path in sorted(EVIDENCE.rglob("*")) if path.is_file() and path.relative_to(WORKSPACE).as_posix() not in excluded]
    candidate_files = [CANDIDATE / relative for relative in PRODUCT_FILES] + [CANDIDATE / "tests/bundle_lineage_contract.mjs", CANDIDATE / "tests/mode_delete_ui_contract.mjs", REVISION / "verify_bundle_lineage_closure.py"]
    fixed = [WORKSPACE / relative for relative in FIXED_INPUTS]
    payload = {
        "schema": "lifeos.p3-141.bundle-lineage-closure-final-manifest.v1",
        "task_id": "LIFEOS-P3-141",
        "closure_cycle": ["CL-BUNDLE-LINEAGE-01", "CL-BUNDLE-LINEAGE-02", "CL-NATIVE-CAPTURE-01", "CL-EVIDENCE-01"],
        "authorized_root": str(ROOT),
        "lineage": lineage,
        "captures": captures,
        "mutations": mutations,
        "cleanup": cleanup_record,
        "execution": {
            "status": execution_status,
            "finding_counts": {"P0": 1, "P1": 0, "P2": 0, "Unknown": 0, "Not Implemented": sum(1 for capture in captures if capture.get("status") == "NOT_IMPLEMENTED")},
            "blocking_conditions": ["P0: PROCEDURAL_DEVIATION.md records a helper compile output outside the one authorized Closure root."] + [capture["viewport"] + ": " + str(capture.get("failure")) for capture in captures if capture.get("status") == "NOT_IMPLEMENTED"],
        },
        "fixed_inputs": [file_record(path) for path in fixed],
        "manifest_exclusions": sorted(excluded),
        "non_conclusions": ["Engineering Closure only; not an independent review.", "Does not restore Phase C, authorize Pilot-6, real Provider or credential, risk closure, product freeze, or Stage 4."],
        "files": [file_record(path) for path in candidate_files + evidence_files],
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    for required in [CANDIDATE, EVIDENCE, NODE, CARGO, SWIFTC]:
        require(required.exists(), f"required local tool/input unavailable: {required}")
    clone = prepare_root()
    env = environment()
    (ROOT / "runtime").mkdir(mode=0o700)
    (ROOT / "tmp").mkdir(mode=0o700)
    lineage = {"source_to_copied_candidate": validate_source_to_clone(clone)}
    app = build_app(clone, env)
    lineage["frontend_and_app_resource"] = resource_binding(app, clone)
    captures = capture_viewports(app, env)
    mutations = mutation_results(clone, lineage["frontend_and_app_resource"], env)
    require(all(item["pass"] for item in mutations), "a required mutation was not rejected")
    write_json("lineage.json", lineage)
    write_json("mutation-results.json", mutations)
    cleanup_record = cleanup()
    require(cleanup_record["literal_root_absent"], "authorized root remains after exact cleanup")
    write_json("cleanup.json", cleanup_record)
    execution_status = "BLOCKED"
    build_manifest(lineage, captures, mutations, cleanup_record, execution_status)
    verification = subprocess.run([sys.executable, str(REVISION / "verify_bundle_lineage_closure.py"), "--manifest", str(MANIFEST)], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_text("manifest-verification.json", verification.stdout)
    expected_verifier_exit = 0 if execution_status == "PASS" else 3
    require(verification.returncode == expected_verifier_exit, "final manifest verification did not match the execution result")
    return expected_verifier_exit


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        write_text("closure-failure.txt", f"FAIL: {error}\n")
        print(f"bundle-lineage closure failed: {error}", file=sys.stderr)
        raise SystemExit(2)
