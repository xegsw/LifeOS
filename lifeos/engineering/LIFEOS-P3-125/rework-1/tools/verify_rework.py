#!/usr/bin/env python3
"""Fail-closed verifier for the P3-125 Rework-1 non-self-referential Manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


REWORK_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = REWORK_ROOT.parents[3]
MANIFEST_NAME = "FINAL_MANIFEST.json"
REQUIRED_ROLES = {
    "task_card",
    "frozen_abf",
    "source_allowlist",
    "user_confirmation",
    "rework_authorization_manifest",
    "p3_125_pm_review",
    "p3_122_freeze_manifest",
    "p3_122_history",
    "p3_124_freeze_manifest",
    "p3_124_history",
    "initial_candidate",
    "current_candidate",
    "initial_evidence",
    "initial_delivery",
    "rework_evidence",
    "rework_delivery",
    "mutation",
    "cleanup",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(reason: str, detail: str) -> int:
    print(json.dumps({"result": "FAIL", "reason": reason, "detail": detail}, ensure_ascii=False))
    return 1


def safe_repo_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        return None
    candidate = (REPOSITORY_ROOT / pure).resolve(strict=False)
    try:
        candidate.relative_to(REPOSITORY_ROOT)
    except ValueError:
        return None
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", type=Path, default=REWORK_ROOT / MANIFEST_NAME)
    parser.add_argument("--candidate", type=Path, default=REWORK_ROOT / "candidate")
    args = parser.parse_args()
    manifest_path = args.manifest.resolve(strict=False)
    if not manifest_path.is_file():
        return fail("manifest_missing", str(manifest_path))
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return fail("manifest_unparseable", str(error))
    if payload.get("task_id") != "LIFEOS-P3-125" or payload.get("rework") != "1/1":
        return fail("manifest_identity", "task_id or rework does not match frozen scope")
    if payload.get("manifest_root") != "repository-root":
        return fail("manifest_root", "manifest root must be the fixed repository-root semantic")
    if payload.get("inventory_excludes") != "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json only":
        return fail("manifest_self_reference_contract", "self-exclusion contract changed")
    candidate = args.candidate.resolve(strict=False)
    build = candidate / "build.rs"
    runtime = candidate / "src" / "runtime.rs"
    if not build.is_file() or not runtime.is_file() or build.is_symlink() or runtime.is_symlink():
        return fail("candidate_source_missing", str(candidate))
    build_text = build.read_text(encoding="utf-8")
    active_runtime = runtime.read_text(encoding="utf-8").split("#[cfg(any())]", 1)[0]
    if "ALLOWED_PARENT" in build_text or "lifeos-p3-125-runtime-root-config-v1" in build_text:
        return fail("production_fixed_parent", "build.rs has a task-ID parent restriction")
    if "LIFEOS_RUNTIME_ROOT\").or(" in build_text or "LIFEOS_RUNTIME_ROOT\").unwrap" in build_text or "BUILD_RUNTIME_ROOT.unwrap" in active_runtime:
        return fail("runtime_root_fallback", "single build-time root has a fallback")
    if "option_env!(\"LIFEOS_RUNTIME_ROOT\")" not in active_runtime or "rustc-env=LIFEOS_RUNTIME_ROOT" not in build_text:
        return fail("runtime_root_missing", "single build-time root is not embedded and consumed")
    if "db_path: root.join(DB_NAME)" not in active_runtime or "viewport_request: root.join(\"viewport-request.txt\")" not in active_runtime or "paths.root.join(format!(\"native-geometry-{requested}.jsonl\"))" not in active_runtime:
        return fail("runtime_derivation", "DB, viewport, or geometry no longer derives from the one root")
    try:
        validation_index = active_runtime.index("validate_database_path(&runtime, &runtime.db_path)")
        builder_index = active_runtime.index("tauri::Builder::default()")
    except ValueError:
        return fail("validation_order", "validation or builder marker is absent")
    if validation_index >= builder_index:
        return fail("validation_order", "runtime validation no longer precedes builder creation")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return fail("manifest_entries", "entries must be a non-empty list")

    paths: set[str] = set()
    roles: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            return fail("manifest_entry_type", f"entry {index} is not an object")
        relative = entry.get("path")
        role = entry.get("role")
        expected_hash = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        if not isinstance(role, str) or not isinstance(expected_hash, str) or len(expected_hash) != 64 or not isinstance(expected_bytes, int):
            return fail("manifest_entry_shape", f"entry {index} has invalid role, hash, or bytes")
        resolved = safe_repo_path(relative)
        if resolved is None:
            return fail("manifest_path", f"entry {index} path is not repository-relative and safe")
        if relative == "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json":
            return fail("manifest_self_included", "Final Manifest may not inventory itself")
        if relative in paths:
            return fail("manifest_duplicate_path", relative)
        if not resolved.is_file() or resolved.is_symlink():
            return fail("manifest_path_missing", str(relative))
        actual_bytes = resolved.stat().st_size
        actual_hash = sha256(resolved)
        if actual_bytes != expected_bytes or actual_hash != expected_hash:
            return fail("manifest_hash_mismatch", str(relative))
        paths.add(relative)
        roles.add(role)

    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        return fail("manifest_required_role_omission", ",".join(missing_roles))

    actual_rework_files = {
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for path in REWORK_ROOT.rglob("*")
        if path.is_file() and not path.is_symlink() and path.name != MANIFEST_NAME and path.name != ".DS_Store"
    }
    listed_rework_files = {
        path for path in paths if path.startswith("lifeos/engineering/LIFEOS-P3-125/rework-1/")
    }
    extras = sorted(actual_rework_files - listed_rework_files)
    omissions = sorted(listed_rework_files - actual_rework_files)
    if extras:
        return fail("manifest_extra_file", extras[0])
    if omissions:
        return fail("manifest_rework_path_missing", omissions[0])

    static = payload.get("static_contract")
    if not isinstance(static, dict) or static.get("production_fixed_parent_absent") is not True:
        return fail("manifest_static_contract", "Manifest lacks the independently recomputed static result")
    print(json.dumps({"result": "PASS", "entries": len(entries), "roles": len(roles)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
