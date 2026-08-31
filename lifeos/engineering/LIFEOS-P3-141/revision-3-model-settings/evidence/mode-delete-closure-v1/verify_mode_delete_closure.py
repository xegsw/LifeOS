#!/usr/bin/env python3
"""Verify the final Closure Cycle manifest and its key behavioural evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE = Path.cwd().resolve()
REVISION = WORKSPACE / "lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings"
EVIDENCE = REVISION / "evidence/mode-delete-closure-v1"
MANIFEST_PATH = REVISION / "MODE_DELETE_CLOSURE_FINAL_MANIFEST.json"
TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, description: str, errors: list[str]) -> None:
    if not condition:
        errors.append(description)


def main() -> int:
    errors: list[str] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest.get("schema") == "lifeos.p3-141.mode-delete-closure-final-manifest.v1", "manifest schema mismatch", errors)
    listed = manifest.get("files", [])
    listed_paths = [item.get("path") for item in listed]
    excluded = set(manifest.get("manifest_exclusions", []))
    manifest_relative = MANIFEST_PATH.relative_to(WORKSPACE).as_posix()
    require(manifest_relative not in listed_paths, "manifest self-reference", errors)
    require(manifest_relative in excluded, "manifest exclusion missing", errors)
    for record in listed:
        relative = record.get("path", "")
        path = WORKSPACE / relative
        require(path.is_file(), f"missing manifest file: {relative}", errors)
        if path.is_file():
            require(record.get("sha256") == sha256(path), f"hash mismatch: {relative}", errors)
            require(record.get("bytes") == path.stat().st_size, f"size mismatch: {relative}", errors)
    adapter = (REVISION / "candidate/ui/runtime-adapter.js").read_text(encoding="utf-8")
    for token in ["draftProvider", "providerModePending", "requirePersistedProviderMode", "先保存 Cloud 配置后管理 API Key"]:
        require(token in adapter, f"missing adapter guard: {token}", errors)
    ui_contract = (EVIDENCE / "mode-delete-ui-contract.log").read_text(encoding="utf-8")
    require("mode-delete-ui-contract: PASS" in ui_contract, "UI contract did not pass", errors)
    cargo = (EVIDENCE / "cargo-test-locked-offline.log").read_text(encoding="utf-8")
    require("51 passed; 0 failed" in cargo, "offline Rust suite did not pass 51/51", errors)
    default_cargo = (EVIDENCE / "cargo-test-locked-offline-default-after-race-fix.log").read_text(encoding="utf-8")
    require("51 passed; 0 failed" in default_cargo, "default parallel Rust suite did not pass 51/51", errors)
    default_ui_contract = (EVIDENCE / "mode-delete-ui-contract-after-race-fix.log").read_text(encoding="utf-8")
    require("mode-delete-ui-contract: PASS" in default_ui_contract, "post-race-fix UI contract did not pass", errors)
    wrong_marker = (EVIDENCE / "wrong-marker-rejection.log").read_text(encoding="utf-8")
    require("marker does not bind this exact task root" in wrong_marker, "wrong marker was not rejected", errors)
    permission_rejection = (EVIDENCE / "cargo-test-locked-offline-attempt-4-runtime-permission-rejected.log").read_text(encoding="utf-8")
    require("canonical 0700 non-symlink directory" in permission_rejection, "runtime permission mutation was not rejected", errors)
    parallel_race = (EVIDENCE / "cargo-test-locked-offline-attempt-5-parallel-test-race.log").read_text(encoding="utf-8")
    require("49 passed; 2 failed" in parallel_race, "parallel fixture race was not preserved", errors)
    for file_name in ["final-delete-db-row-count.txt", "final-restart-db-row-count.txt"]:
        require((EVIDENCE / file_name).read_text(encoding="utf-8").strip() == "0", f"expected zero credential rows: {file_name}", errors)
    pending = (EVIDENCE / "gui/desktop-pending-mode.ax.txt").read_text(encoding="utf-8")
    require("当前显示为 Cloud，但活动模式仍是 Local" in pending, "pending-mode notice absent", errors)
    require("button (disabled) 先保存 Cloud 配置后管理 API Key" in pending, "pending-mode management was not disabled", errors)
    require("删除已保存 API Key" not in pending, "delete action remained in pending mode", errors)
    for file_name in ["final-delete-post-ui.ax.txt", "final-restart-no-credential.ax.txt"]:
        state = (EVIDENCE / "gui" / file_name).read_text(encoding="utf-8")
        require("输入 API Key" in state and "删除已保存 API Key" not in state, f"deleted credential visible in {file_name}", errors)
    for viewport in ["desktop", "compact", "narrow", "final-restart"]:
        ax = json.loads((EVIDENCE / "gui" / f"{viewport}-ax.json").read_text(encoding="utf-8"))
        windows = ax.get("windows", [])
        roles = {node.get("role") for node in ax.get("webNodes", [])}
        require(len(windows) == 1 and windows[0].get("title") == TITLE, f"PID/title chain invalid: {viewport}", errors)
        require("AXWebArea" in roles or "AXWebView" in roles, f"web node missing: {viewport}", errors)
    expected_sizes = {"desktop": (1280, 949), "compact": (1160, 768), "narrow": (700, 760)}
    for viewport, expected in expected_sizes.items():
        ax = json.loads((EVIDENCE / "gui" / f"{viewport}-ax.json").read_text(encoding="utf-8"))
        frame = ax["windows"][0]["frame"]["size"]
        actual = (frame.get("width"), frame.get("height"))
        require(actual == expected, f"window size mismatch {viewport}: {actual}", errors)
    result = {
        "schema": "lifeos.p3-141.mode-delete-closure-manifest-verification.v1",
        "result": "PASS" if not errors else "FAIL",
        "checked_files": len(listed),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
