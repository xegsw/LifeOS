#!/usr/bin/env python3
"""P3-073 independent, no-export re-review runner for P3-072 authorized assets.

This runner never imports or invokes the P3-072 test suite and never calls the
success export path.  It loads a copy of the subject module in a newly-created
system temporary directory, exercises only no-write blocked/preview paths, and
uses source-level checks for the explicitly forbidden write-path properties.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
SUBJECT_ROOT = ROOT / "lifeos/engineering/LIFEOS-P3-072/authorized_rerun"
SUBJECT = SUBJECT_ROOT / "src/sandbox_export.py"
RESULT_PATH = Path(__file__).with_name("independent_results.json")
AUTHORED = {
    "src/sandbox_export.py": "76997bded53f6aa1c943deb8705fb725ba03385bb423d05f5916ea3862c070fb",
    "tests/test_sandbox_export.py": "e3392e0f5778f6daa31ad3e39e69d5364926b166eb5ff458c440be59f28e08a5",
    "scripts/run_tests.py": "0a4d2dc3c705e32716ac5e415d947f5b00d50aa20d50f0770879bc5c14a7db8a",
    "scripts/make_evidence.py": "ac88a6d984238000859c5e8429abe16ae4f6b74e73354814639b6062a94f6fd2",
    "evidence/test_results.json": "0757dcd6ff55d3d9caf10023b5e3225fdc059239c087b2f6df80fc01f7f2ff56",
    "evidence/export_receipt.json": "dc7e89e8037fbff04406b84b120112ff90ca66ea4f724c40e679124cb69d4847",
}
OLD = {
    "src/sandbox_export.py": "5afb438bb50f92b9a7892f235429129a41215dd66d6022d3b09e96406e4412fa",
    "tests/test_sandbox_export.py": "f9106f212d635f7b7de5e995ead09e9f3bffbb6e50da04a9c0aca8a9838aed84",
    "scripts/run_tests.py": "3c1775d6ed0167963a7dc0c348887f00682678124dab95db763285d38a846590",
    "scripts/make_evidence.py": "b79baa65782a69c44ea3e7899d7b005b32e1692934e7360fd7d0ef3efb80a24d",
    "evidence/test_results.json": "8cd985c9c303f601fbe4c3e36ce0eebb9fdc8f7cbe63384b3e51b5e2969b522d",
    "evidence/export_receipt.json": "6eb8d9c2a83549106d9bbb1e70f061b62dd6e8cbeaf5f36bae8eb1b03857bcbf",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_subject() -> Any:
    with tempfile.TemporaryDirectory(prefix="lifeos-p3-073-review-") as directory:
        copied = Path(directory) / "sandbox_export.py"
        shutil.copy2(SUBJECT, copied)
        spec = importlib.util.spec_from_file_location("p3_073_subject", copied)
        require(spec is not None and spec.loader is not None, "temporary subject copy cannot load")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module


def blocked_case(module: Any, mutate: str, expected: str) -> None:
    export = module.ControlledSandboxExport()
    try:
        export.register("item", "synthetic://p3-073", "non-sensitive", 1)
        plan = module.ExportPlan("synthetic://p3-073", "item", 1, "single_record", "temporary_sandbox")
        if mutate == "source": plan = module.ExportPlan("synthetic://other", "item", 1, "single_record", "temporary_sandbox")
        if mutate == "version": plan = module.ExportPlan("synthetic://p3-073", "item", 2, "single_record", "temporary_sandbox")
        if mutate == "unknown": plan = module.ExportPlan("synthetic://p3-073", "missing", 1, "single_record", "temporary_sandbox")
        if mutate == "conflict": export.set_conflict("item")
        if mutate == "revoked": export.set_state("item", "revoked")
        if mutate == "tombstoned": export.set_state("item", "tombstoned")
        preview = export.preview(plan)
        if mutate == "after_preview":
            require(preview["status"] == "ready", "setup preview must be ready")
            export.set_state("item", "revoked")
        result = export.confirm_and_export(plan, "CONFIRM", preview.get("preview_token", "not-a-token"))
        require(result["status"] == "blocked" and result["reason"] == expected, str(result))
        require(result["external_action"] == "none", str(result))
    finally:
        export.close()


def source_checks(source: str) -> None:
    tree = ast.parse(source)
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
    require(not ({"socket", "requests", "urllib", "subprocess"} & imported), f"external import found: {imported}")
    require("os.link(pending, destination)" in source and "destination.exists()" in source, "atomic new-file guard missing")
    require("destination.parent != sandbox.resolve()" in source, "path-escape guard missing")
    require("if pending.exists(): pending.unlink()" in source and "if destination.exists(): destination.unlink()" in source, "failure cleanup missing")
    require('row["exported_plan_hash"] is not None' in source and "UPDATE records SET exported_plan_hash" in source, "single-use state guard missing")
    require("tempfile.mkdtemp" in source and "sandbox.parent != Path(tempfile.gettempdir()).resolve()" in source, "system-temp sandbox constraint missing")


def main() -> int:
    results: list[dict[str, str]] = []
    def check(name: str, fn: Any) -> None:
        try:
            fn(); results.append({"id": name, "status": "PASS"})
        except Exception as error: results.append({"id": name, "status": "FAIL", "detail": str(error)})

    check("AR-01_authorized_subject_hashes", lambda: require(all(sha256(SUBJECT_ROOT / p) == h for p, h in AUTHORED.items()), "authorized manifest hash mismatch"))
    old_root = ROOT / "lifeos/engineering/LIFEOS-P3-072"
    check("AR-02_unauthorized_history_preserved", lambda: require(all(sha256(old_root / p) == h for p, h in OLD.items()), "old asset changed"))
    source = SUBJECT.read_text(encoding="utf-8")
    def no_test_suite_dependency() -> None:
        runner_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        imports = [alias.name for node in ast.walk(runner_tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names]
        require(not any(name.startswith("tests.") for name in imports), f"runner imports subject test suite: {imports}")
    check("AR-03_no_test_suite_dependency", no_test_suite_dependency)
    check("AR-04_static_closed_external_capabilities", lambda: source_checks(source))

    module = load_subject()
    def preview_default() -> None:
        export = module.ControlledSandboxExport()
        try:
            export.register("item", "synthetic://p3-073", "non-sensitive", 1)
            plan = module.ExportPlan("synthetic://p3-073", "item", 1, "single_record", "temporary_sandbox")
            result = export.preview(plan)
            require(result["status"] == "ready" and result["external_action"] == "none", str(result))
            require(result["confirmation_required"] == "CONFIRM" and result["target_semantics"] == "new_system_temporary_sandbox_only", str(result))
            require(set(result["boundaries"].values()) >= {"disabled", "not_used", "blocked"}, str(result))
        finally: export.close()
    check("AR-05_default_preview_does_not_write", preview_default)
    def confirmation_and_token() -> None:
        export = module.ControlledSandboxExport()
        try:
            export.register("item", "synthetic://p3-073", "non-sensitive", 1)
            plan = module.ExportPlan("synthetic://p3-073", "item", 1, "single_record", "temporary_sandbox")
            preview = export.preview(plan)
            missing = export.confirm_and_export(plan, "confirm", preview["preview_token"])
            mismatch = export.confirm_and_export(plan, "CONFIRM", "wrong-token")
            require(missing["reason"] == "explicit_confirmation_required" and mismatch["reason"] == "preview_token_mismatch", f"{missing}; {mismatch}")
        finally: export.close()
    check("AR-06_exact_confirmation_and_token_block", confirmation_and_token)
    for name, mutation, reason in [
        ("AR-07_source_mismatch", "source", "source_mismatch"), ("AR-08_version_mismatch", "version", "identity_version_mismatch"),
        ("AR-09_unknown", "unknown", "unknown_content"), ("AR-10_conflict", "conflict", "conflict_detected"),
        ("AR-11_revoked", "revoked", "revoked_or_tombstoned"), ("AR-12_tombstoned", "tombstoned", "revoked_or_tombstoned"),
        ("AR-13_state_change_after_preview", "after_preview", "revoked_or_tombstoned"),
    ]:
        check(name, lambda m=mutation, r=reason: blocked_case(module, m, r))
    check("AR-14_single_use_guard", lambda: require("one_time_export_already_consumed" in source and 'row["exported_plan_hash"] is not None' in source, "single-use guard absent"))
    check("AR-15_path_escape_and_overwrite_block", lambda: require("destination.parent != sandbox.resolve()" in source and "destination.exists()" in source, "path/overwrite guard absent"))
    check("AR-16_atomic_publish", lambda: require("open(pending, \"xb\")" in source and "os.fsync(handle.fileno())" in source and "os.link(pending, destination)" in source, "atomic sequence absent"))
    check("AR-17_failed_write_cleanup", lambda: require("if pending.exists(): pending.unlink()" in source and "if destination.exists(): destination.unlink()" in source and "visible_output_count=visible" in source, "cleanup/audit absent"))
    def audit_closed() -> None:
        export = module.ControlledSandboxExport()
        try:
            export.register("item", "synthetic://p3-073", "non-sensitive", 1)
            plan = module.ExportPlan("synthetic://p3-073", "item", 1, "single_record", "temporary_sandbox")
            result = export.confirm_and_export(plan, "no", "no")
            events = export.audit_events()
            require(result["status"] == "blocked" and any(e["event"] == "sandbox_export_blocked" for e in events), str(events))
        finally: export.close()
    check("AR-18_blocked_audit_and_closed_state", audit_closed)
    payload = {"task": "LIFEOS-P3-073", "runner": "independent_runner.py", "no_export_files_created": True, "summary": {"pass": sum(x["status"] == "PASS" for x in results), "fail": sum(x["status"] == "FAIL" for x in results)}, "results": results}
    RESULT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if payload["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
