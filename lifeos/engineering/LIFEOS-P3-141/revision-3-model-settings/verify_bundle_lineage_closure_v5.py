#!/usr/bin/env python3
"""Read-only verifier for the P3-141 Revision 3 v5 engineering closure."""

import hashlib
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
EVIDENCE = BASE / "evidence" / "bundle-lineage-closure-v5"
MANIFEST = BASE / "BUNDLE_LINEAGE_CLOSURE_V5_FINAL_MANIFEST.json"
RESULT = EVIDENCE / "BUNDLE_LINEAGE_CLOSURE_V5_VERIFIER_RESULT.json"
TEMP_ROOT = "/private/tmp/lifeos-p3-141-revision-3-engineering-bundle-lineage-v5"
TITLE = "LifeOS · P3-141 Controlled Pilot Candidate"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


try:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
except Exception as exc:  # noqa: BLE001
    print(f"manifest unreadable: {exc}", file=sys.stderr)
    raise SystemExit(2)

require(manifest.get("schema") == "lifeos.p3-141.bundle-lineage-closure-v5.final-manifest.v1", "manifest schema")
require(manifest.get("conclusion") == "Engineering Pass — synthetic/offline scope only", "manifest conclusion")
require(manifest.get("non_self_referential") is True, "manifest must declare non-self-referential")
for rel, expected in manifest.get("artifact_sha256", {}).items():
    artifact = BASE / rel
    require(artifact.is_file(), f"missing artifact: {rel}")
    if artifact.is_file():
        require(sha256(artifact) == expected, f"hash mismatch: {rel}")

seal = load("precontact_seal.json")
require(seal.get("v5_candidate_or_history_contact_before_seal") is False, "precontact order")
require(seal.get("authorized_temporary_root") == TEMP_ROOT, "sealed temp root")
require(seal.get("candidate_delta", {}).get("paths") == ["candidate/build.rs", "candidate/src/runtime.rs"], "sealed candidate write allowlist")

static = load("static_contract_prebuild_final.json")
mutations = load("mutation_matrix_static_final.json")
lineage = load("source_bundle_binary_lineage_retry.json")
delta = load("candidate_v5_delta_retry.json")
require(static.get("pass") is True, "static contract")
require(mutations.get("all_rejected") is True, "mutation matrix")
require(len(mutations.get("results", [])) == 8 and all(x.get("rejected") for x in mutations.get("results", [])), "eight rejected mutations")
require(lineage.get("pass") is True, "source/bundle/binary lineage")
require(lineage.get("candidate", {}).get("file_count") == 82, "candidate file count")
require(lineage.get("copied_build_input", {}).get("equals_candidate") is True, "clean build input binding")
require(lineage.get("binary_matches_debug") is True, "app/debug binary binding")
require(delta.get("matches_recorded_v3_tree") is True, "reconstructed v3 identity")
require(delta.get("only_expected_paths_changed") is True, "v5 delta scope")
require(delta.get("changed_paths_from_reconstructed_v3") == ["build.rs", "src/runtime.rs"], "v5 changed paths")

for name in ("cargo_test_serial.log", "cargo_test_parallel.log"):
    require("52 passed; 0 failed" in (EVIDENCE / name).read_text(encoding="utf-8"), f"offline regression: {name}")
require("bundle-lineage-contract: PASS" in (EVIDENCE / "bundle_lineage_contract.log").read_text(encoding="utf-8"), "bundle lineage contract")
require("mode-delete-ui-contract: PASS" in (EVIDENCE / "mode_delete_ui_contract.log").read_text(encoding="utf-8"), "mode/delete UI contract")
bundle_log = (EVIDENCE / "cargo_tauri_bundle.log").read_text(encoding="utf-8")
require("Finished 1 bundle" in bundle_log and "Controlled Pilot Candidate.app" in bundle_log, "Tauri app bundle")

required_markers = ("模型设置", "OpenAI", "DeepSeek", "Kimi", "Ollama", "LM Studio", "加密保存")
for viewport in ("desktop", "compact", "narrow"):
    launch = load(f"direct_launch_{viewport}_framefallback.json")
    pre = load(f"native_{viewport}_ax_pre_framefallback.json")
    click = load(f"target_click_{viewport}_framefallback.json")
    post = load(f"native_{viewport}_ax_settings_framefallback.json")
    geometry = load(f"settings_{viewport}_framefallback_geometry.json")
    require(launch.get("viewport") == viewport and launch.get("title") == TITLE, f"{viewport}: direct launch identity")
    require(launch.get("pid") == pre.get("pid") == click.get("pid") == post.get("pid"), f"{viewport}: one PID chain")
    for record, stage in ((pre, "pre"), (post, "post")):
        require(record.get("status") == "ready_for_bounded_target_capture", f"{viewport}: {stage} ready")
        require(record.get("exact_title") == TITLE, f"{viewport}: {stage} exact title")
        require(record.get("ax_role") == "AXWindow" and record.get("ax_window_count") == 1 and record.get("matching_title_count") == 1, f"{viewport}: {stage} unique AXWindow")
        require(record.get("ax_web_area_count", 0) >= 1, f"{viewport}: {stage} AXWebArea")
        require(record.get("frame_stable") is True and record.get("target_frontmost") is True and record.get("overlap_count") == 0, f"{viewport}: {stage} stable/frontmost/no-overlap")
    require(click.get("status") == "target_bound_settings_click_sent", f"{viewport}: target-bound Settings click")
    require(click.get("method") in ("ax_button_frame", "ax_window_frame_relative_settings_zone"), f"{viewport}: approved click binding")
    text_presence = post.get("settings_text_presence", {})
    require(all(text_presence.get(marker) is True for marker in required_markers), f"{viewport}: Settings text markers")
    require(geometry.get("capture") == "target_ax_window_frame_only" and geometry.get("geometry_matches") is True, f"{viewport}: target-only geometry")
    require((EVIDENCE / f"settings_{viewport}_framefallback.png").is_file(), f"{viewport}: screenshot present")

for viewport, exit_name in (("desktop", "direct_launch_desktop_framefallback_exit_recovery.json"), ("compact", "direct_launch_compact_framefallback_exit_recovery.json"), ("narrow", "direct_launch_narrow_framefallback_exit.json")):
    exit_record = load(exit_name)
    require(exit_record.get("viewport") == viewport and exit_record.get("exit_state") == "exited", f"{viewport}: PID exit")

cleanup = load("cleanup_gate_matrix.json")
cleanup_final = load("cleanup_final.json")
require(cleanup.get("pass") is True, "cleanup negative/positive marker matrix")
require(cleanup_final.get("status") == "cleanup_complete" and cleanup_final.get("root_absent_after_cleanup") is True, "cleanup completion")
require(not os.path.lexists(TEMP_ROOT), "temporary root must remain absent")

result = {
    "schema": "lifeos.p3-141.bundle-lineage-closure-v5.verifier-result.v1",
    "status": "PASS" if not errors else "FAIL",
    "errors": errors,
    "checked_manifest": str(MANIFEST.relative_to(ROOT)),
    "checked_temp_root_absent": not os.path.lexists(TEMP_ROOT),
}
RESULT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if not errors else 1)
