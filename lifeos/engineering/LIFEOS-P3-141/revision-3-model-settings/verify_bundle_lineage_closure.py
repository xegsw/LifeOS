#!/usr/bin/env python3
"""Read-only verifier for the P3-141 Revision-3 bundle-lineage Closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


WORKSPACE = Path.cwd().resolve()
REVISION = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings"
TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"
PRODUCT_FILES = ["ui/runtime-adapter.js", "ui/interaction_contract.md", "ui/ia_reconciliation.md", "ui/visual_contract.json", "ui/state_machine.json"]
EXPECTED_MUTATIONS = {
    "MUT-01-old-session-source",
    "MUT-02-cloud-kimi-merged",
    "MUT-03-local-provider-removed",
    "MUT-04-mode-isolation-guard-removed",
    "MUT-05-wrong-candidate-directory",
    "MUT-06-stale-resource",
    "MUT-07-resource-hash-binding-removed",
    "MUT-08-marker-root-mismatch",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    manifest_path = args.manifest.resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as error:
        print(json.dumps({"result": "FAIL", "errors": [f"manifest unreadable: {error}"]}, ensure_ascii=False, indent=2))
        return 2
    require(manifest.get("schema") == "lifeos.p3-141.bundle-lineage-closure-final-manifest.v1", "manifest schema mismatch")
    require(manifest.get("task_id") == "LIFEOS-P3-141", "task id mismatch")
    execution = manifest.get("execution", {})
    require(execution.get("status") == "BLOCKED", "this package must retain its procedural P0 as Blocked")
    finding_counts = execution.get("finding_counts", {})
    require(finding_counts.get("P0") == 1, "procedural P0 count is not preserved")
    listed = manifest.get("files", [])
    listed_paths = [record.get("path") for record in listed]
    excluded = set(manifest.get("manifest_exclusions", []))
    relative_manifest = manifest_path.relative_to(WORKSPACE).as_posix()
    require(relative_manifest not in listed_paths and relative_manifest in excluded, "manifest self-reference is not excluded")
    for record in listed:
        relative = record.get("path")
        path = WORKSPACE / str(relative)
        require(path.is_file(), f"manifest file missing: {relative}")
        if path.is_file():
            require(record.get("sha256") == sha256(path), f"manifest hash mismatch: {relative}")
            require(record.get("bytes") == path.stat().st_size, f"manifest byte mismatch: {relative}")

    source = REVISION / "candidate"
    lineage = manifest.get("lineage", {})
    copied = lineage.get("source_to_copied_candidate", {})
    require(copied.get("source_candidate_path") == source.relative_to(WORKSPACE).as_posix(), "lineage source path is not the authorized candidate")
    require(copied.get("copied_candidate_path") == "/private/tmp/lifeos-p3-141-revision-3-engineering-bundle-lineage-v1/candidate", "lineage copied candidate path is not the exact authorized root")
    require(copied.get("source_tree_sha256") == copied.get("copied_tree_sha256"), "source/copy tree aggregate mismatch")
    for binding in copied.get("required_bindings", []):
        require(binding.get("source_sha256") == binding.get("copied_sha256"), f"source/copy binding mismatch: {binding.get('relative')}")

    contracts = "\n".join((source / relative).read_text(encoding="utf-8") for relative in PRODUCT_FILES)
    for phrase in ["本次会话 API Key", "仅保留在本次会话", "清除本次会话 API Key", "环境变量名引用", "环境变量凭据"]:
        require(phrase not in contracts, f"forbidden credential product semantics remain: {phrase}")
    for phrase in ["API Key 已加密保存", "受控本地 SQLite", "密钥材料与数据库分离", "跨重启保留", "删除已保存 API Key"]:
        require(phrase in contracts, f"persistent credential product semantics missing: {phrase}")

    bundle = lineage.get("frontend_and_app_resource", {})
    require(bundle.get("source_adapter_sha256") == sha256(source / "ui/runtime-adapter.js"), "source adapter hash is not bound into bundle lineage")
    require(bundle.get("source_index_sha256") == sha256(source / "ui/index.html"), "source index hash is not bound into bundle lineage")
    require(bundle.get("frontend_packaging") in {"resource-files", "compiled-binary-embedded-assets"}, "bundle frontend packaging method is missing")
    if bundle.get("frontend_packaging") == "resource-files":
        adapters = bundle.get("adapter_resource_matches", [])
        indexes = bundle.get("index_resource_matches", [])
        require(len(adapters) == 1 and adapters[0].get("sha256") == bundle.get("source_adapter_sha256"), "bundle adapter resource hash is not exact")
        require(len(indexes) == 1 and indexes[0].get("sha256") == bundle.get("source_index_sha256"), "bundle index resource hash is not exact")
    else:
        compiled = bundle.get("compiled_input_binding", {})
        require(compiled.get("adapter_sha256") == bundle.get("source_adapter_sha256"), "embedded adapter input is not bound")
        require(compiled.get("index_sha256") == bundle.get("source_index_sha256"), "embedded index input is not bound")
        require(compiled.get("bundle_resource_inventory_exposes_frontend_files") is False, "embedded frontend inventory state is invalid")

    captures = manifest.get("captures", [])
    require({capture.get("viewport") for capture in captures} == {"desktop", "compact", "narrow"}, "three direct-PID viewports are incomplete")
    for capture in captures:
        proof = capture.get("capture", {})
        require(capture.get("direct_pid") == proof.get("pid"), f"direct PID binding mismatch: {capture.get('viewport')}")
        require(proof.get("expectedTitle") == TITLE and proof.get("matchingWindowCount") == 1, f"exact AXWindow missing: {capture.get('viewport')}")
        require(bool(proof.get("webRoles")), f"AXWebArea/WebView missing: {capture.get('viewport')}")
        require(proof.get("captureScope") in {"direct_pid_exact_title_axwindow_webview_and_pid_title_bounds_cgwindow_only", "direct_pid_exact_title_axwindow_webview_frontmost_focused_ax_bounded_region_only", "fail_closed_ax_bounded_region_preconditions"}, f"capture scope is not target-window-only: {capture.get('viewport')}")
        require(proof.get("positiveTextPresent") is True and proof.get("forbiddenTextPresent") is False, f"Settings text contract failed: {capture.get('viewport')}")
        if capture.get("status") == "PASS":
            require(proof.get("pass") is True and capture.get("screenshot") is not None, f"passing native capture is incomplete: {capture.get('viewport')}")
        else:
            require(capture.get("status") == "NOT_IMPLEMENTED" and proof.get("pass") is False and capture.get("screenshot") is None, f"failed native capture did not fail closed: {capture.get('viewport')}")
        if proof.get("captureMethod") == "ax-bounded-region":
            require(proof.get("appWasFrontmost") is True and proof.get("windowWasFocused") is True and proof.get("foreignOverlayCount") == 0, f"AX-bounded-region preconditions are incomplete: {capture.get('viewport')}")
            require(proof.get("requestedRegion") is not None and proof.get("pixelDimensionsMatch") is True, f"AX-bounded-region geometry proof is incomplete: {capture.get('viewport')}")

    mutations = manifest.get("mutations", [])
    mutation_ids = {item.get("id") for item in mutations}
    require(EXPECTED_MUTATIONS <= mutation_ids, "required source/resource mutations are incomplete")
    require(all(item.get("pass") is True and item.get("expected") == "rejected" for item in mutations), "a mutation did not fail closed")
    cleanup = manifest.get("cleanup") or {}
    require(cleanup.get("literal_root_absent") is True, "cleanup did not prove literal root absence")
    require(not Path(cleanup.get("root", "/invalid")).exists(), "authorized root still exists after cleanup")
    evidence = REVISION / "evidence/bundle-lineage-closure-v1"
    deviation = evidence / "PROCEDURAL_DEVIATION.md"
    require(deviation.is_file() and "procedural P0" in deviation.read_text(encoding="utf-8"), "procedural deviation record is missing")
    for log, expected in [("logs/cargo-test-default-parallel.log", "52 passed; 0 failed"), ("logs/cargo-test-serial.log", "52 passed; 0 failed"), ("logs/mode-delete-ui-contract.log", "mode-delete-ui-contract: PASS"), ("logs/bundle-lineage-contract.log", "bundle-lineage-contract: PASS")]:
        path = evidence / log
        require(path.is_file() and expected in path.read_text(encoding="utf-8"), f"missing regression proof: {log}")

    result = {"schema": "lifeos.p3-141.bundle-lineage-closure-verification.v1", "result": "BLOCKED" if not errors else "FAIL", "checked_files": len(listed), "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 3 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
