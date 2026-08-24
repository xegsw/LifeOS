#!/usr/bin/env python3
"""P3-109 independent, allowlist-only build and static review runner.

This runner deliberately does not import, copy, or execute any P3-107/P3-108
runner, tool, or Evidence. It prepares only P3-109 task-local Evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-109/evidence"
WORK = Path("/private/tmp/lifeos-p3-109-review-work-v1")
P106 = ROOT / "lifeos/engineering/LIFEOS-P3-106"
P104 = ROOT / "lifeos/engineering/LIFEOS-P3-104"
ABF = ROOT / "lifeos/tasks/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor_acceptance_basis_freeze.md"
TASK = ROOT / "lifeos/tasks/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor.md"
P108_REVIEW = ROOT / "lifeos/reviews/LIFEOS-P3-108_pm_review.md"
P106_MANIFEST = P106 / "evidence/rework-1/MANIFEST.md"
LEGACY = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")

ALLOWED_TEMP_NAMES = {
    "lifeos-p3-109-review-work-v1",
    "lifeos-p3-104-p3-109-review-nominal-v1",
    "lifeos-p3-104-p3-109-review-reopen-v1",
    "lifeos-p3-104-p3-109-review-failure-v1",
    "lifeos-p3-104-p3-109-review-dangling-final-v1",
    "lifeos-p3-104-p3-109-review-dangling-journal-v1",
    "lifeos-p3-104-p3-109-review-dangling-wal-v1",
    "lifeos-p3-104-p3-109-review-dangling-shm-v1",
    "lifeos-p3-104-p3-109-review-path-v1",
    "lifeos-p3-104-p3-109-review-link-v1",
    "lifeos-p3-104-p3-109-review-hardlink-v1",
    "lifeos-p3-104-p3-109-review-tamper-v1",
    "lifeos-p3-104-p3-109-review-a11y-v1",
    "lifeos-p3-104-p3-109-review-narrow-v1",
}

# This positive list is intentionally small. No candidate Evidence, scripts,
# tests, target/, generated output, or P3-107/P3-108 material enters WORK.
ALLOWLIST = [
    ".gitignore", "Cargo.lock", "Cargo.toml", "build.rs", "rust-toolchain.toml", "tauri.conf.json",
    "capabilities/main.json", "src/main.rs", "src/runtime.rs",
    "ui/app.js", "ui/styles.css", "ui/default-recovery.html",
    "ui/no-reliable-suggestion.html", "ui/restricted-offline.html",
]

FIXED = {
    "stitch_default": (ROOT / "lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg", "7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1"),
    "stitch_no_suggestion": (ROOT / "lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg", "55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697"),
    "stitch_restricted": (ROOT / "lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg", "9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661"),
    "p106_default": (P106 / "evidence/rework-1/m004-default-1280x1024.png", "d64921229aab0bbae1fdca0c29cf107e8e11dd7aa7ade732f5a71f3d2c024c5f"),
    "p106_no_suggestion": (P106 / "evidence/rework-1/m005-no-suggestion-1280x1024.png", "373c16c24cb334f34de6c3d4cddb8818905814efec75e83a9fcf09a7b1187f1b"),
    "p106_restricted": (P106 / "evidence/rework-1/m006-restricted-1280x1024.png", "05fa817ab31c874e8505c5c4091f6a438dab56f86b51930003bb1a68d5442da6"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lstat(path: Path) -> dict:
    try:
        value = path.lstat()
    except FileNotFoundError:
        return {"path": str(path), "exists": False}
    kind = "symlink" if path.is_symlink() else "directory" if path.is_dir() else "regular" if path.is_file() else "other"
    return {"path": str(path), "exists": True, "type": kind, "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns, "nlink": value.st_nlink}


def write_json(relative: str, value: object) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def record_command(label: str, command: list[str], cwd: Path, environment: dict[str, str]) -> dict:
    started = time.time()
    completed = subprocess.run(command, cwd=cwd, env=environment, text=True, capture_output=True, check=False)
    log_dir = EVIDENCE / "build"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{label}.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (log_dir / f"{label}.stderr.log").write_text(completed.stderr, encoding="utf-8")
    return {"id": label, "command": command, "cwd": str(cwd), "exit_code": completed.returncode, "duration_ms": round((time.time() - started) * 1000), "stdout": str(log_dir / f"{label}.stdout.log"), "stderr": str(log_dir / f"{label}.stderr.log")}


def ensure_allowed_temp() -> list[dict]:
    output = []
    for name in sorted(ALLOWED_TEMP_NAMES):
        path = Path("/private/tmp") / name
        meta = lstat(path)
        output.append(meta)
        if meta["exists"]:
            raise RuntimeError(f"ABF temporary path is not empty: {path}")
    return output


def copy_allowlist() -> dict:
    if WORK.exists() or WORK.is_symlink():
        raise RuntimeError(f"WORK must be absent before copy: {WORK}")
    if WORK.parent != Path("/private/tmp") or WORK.name not in ALLOWED_TEMP_NAMES:
        raise RuntimeError("work path violates ABF contract")
    WORK.mkdir(mode=0o700)
    entries = []
    for rel in ALLOWLIST:
        source = P106 / rel
        destination = WORK / rel
        if not source.is_file() or source.is_symlink():
            raise RuntimeError(f"allowlist source invalid: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)
        entries.append({"path": rel, "sha256": sha256(destination), "bytes": destination.stat().st_size})
    names = sorted(str(path.relative_to(WORK)) for path in WORK.rglob("*") if path.is_file())
    forbidden = [name for name in names if name.startswith(("evidence/", "scripts/", "tests/", "target/", "gen/")) or "/tools/" in name]
    return {"work": str(WORK), "allowlist": entries, "copied_files": names, "forbidden_paths": forbidden, "pass": not forbidden and sorted(names) == sorted(ALLOWLIST)}


def verify_p106_manifest() -> dict:
    expected = []
    for line in P106_MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([^`]+)` \| `([0-9a-f]{64})` \| (\d+) \|$", line)
        if match:
            expected.append((ROOT / match.group(1), match.group(2), int(match.group(3))))
    mismatches = []
    for path, digest, size in expected:
        if not path.is_file() or sha256(path) != digest or path.stat().st_size != size:
            mismatches.append(str(path))
    return {"manifest": str(P106_MANIFEST), "entries": len(expected), "mismatches": mismatches, "pass": len(expected) == 325 and not mismatches}


def fixed_inputs() -> dict:
    checks = {}
    for name, (path, expected) in FIXED.items():
        actual = sha256(path) if path.is_file() else None
        checks[name] = {"path": str(path), "expected": expected, "actual": actual, "pass": actual == expected}
    checks["task"] = {"path": str(TASK), "actual": sha256(TASK), "expected": "706a666fa40b5d7a59b95929d72945468ee3567a7de483ae8fbeb9e063f402b0", "pass": sha256(TASK) == "706a666fa40b5d7a59b95929d72945468ee3567a7de483ae8fbeb9e063f402b0"}
    checks["abf"] = {"path": str(ABF), "actual": sha256(ABF), "expected": "212b66b320a4ad8cc55db0e9818407368d6ccb31104f6b12a130e06bdd20ac5d", "pass": sha256(ABF) == "212b66b320a4ad8cc55db0e9818407368d6ccb31104f6b12a130e06bdd20ac5d"}
    checks["p106_manifest"] = {"path": str(P106_MANIFEST), "actual": sha256(P106_MANIFEST), "expected": "7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe", "pass": sha256(P106_MANIFEST) == "7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe"}
    checks["p108_review"] = {"path": str(P108_REVIEW), "actual": sha256(P108_REVIEW), "expected": "d961328c948e724eb668d564f47c5c00e3089434a2280af567e0a7bb2b9f5608", "pass": sha256(P108_REVIEW) == "d961328c948e724eb668d564f47c5c00e3089434a2280af567e0a7bb2b9f5608"}
    return {"checks": checks, "pass": all(value["pass"] for value in checks.values())}


def static_checks() -> dict:
    runtime = (WORK / "src/runtime.rs").read_text(encoding="utf-8")
    app = (WORK / "ui/app.js").read_text(encoding="utf-8")
    capability = json.loads((WORK / "capabilities/main.json").read_text(encoding="utf-8"))
    config = json.loads((WORK / "tauri.conf.json").read_text(encoding="utf-8"))
    checks = {
        "runtime_p3_104_hash": sha256(WORK / "src/runtime.rs") == "0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529",
        "cargo_lock_hash": sha256(WORK / "Cargo.lock") == "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1",
        "three_handlers": all(f"fn {name}(" in runtime for name in ("capture_record", "get_today", "runtime_status")),
        "deny_unknown": runtime.count("deny_unknown_fields") >= 2,
        "no_extra_handler": "generate_handler![\n            capture_record,\n            get_today,\n            runtime_status" in runtime,
        "capability_empty": capability.get("permissions") == [],
        "csp_network_closed": "connect-src ipc:" in config["app"]["security"]["csp"] and "http:" not in config["app"]["security"]["csp"],
        "renderer_three_invokes": all(f'"{name}"' in app for name in ("capture_record", "get_today", "runtime_status")),
        "renderer_no_network_api": not any(token in app for token in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource")),
        "identity_labels": all(label in (WORK / "ui/default-recovery.html").read_text(encoding="utf-8") for label in ("你的记录 · 原文", "AI 建议 · 未确认", "你已确认")),
        "reduced_motion": "prefers-reduced-motion: reduce" in (WORK / "ui/styles.css").read_text(encoding="utf-8"),
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    write_json("preflight/temp-before.json", ensure_allowed_temp())
    write_json("preflight/legacy-metadata-before.json", lstat(LEGACY))
    inputs = fixed_inputs()
    write_json("fixed-inputs.json", inputs)
    if not inputs["pass"]:
        return 2
    inventory = copy_allowlist()
    write_json("copy-inventory.json", inventory)
    manifest = verify_p106_manifest()
    write_json("manifest-verification.json", manifest)
    statics = static_checks()
    write_json("static-results.json", statics)
    environment = dict(os.environ, CARGO_NET_OFFLINE="true", CARGO_TARGET_DIR=str(WORK / "target"))
    builds = [
        record_command("cargo-test", ["cargo", "test", "--locked"], WORK, environment),
        record_command("cargo-build", ["cargo", "build", "--locked"], WORK, environment),
        record_command("tauri-app-bundle", ["cargo", "tauri", "build", "--debug", "--bundles", "app", "--locked"], WORK, environment),
    ]
    bundle = next(iter((WORK / "target").glob("debug/bundle/macos/*.app/Contents/MacOS/lifeos-p3-104")), None)
    build_result = {"commands": builds, "bundle_binary": str(bundle) if bundle else None, "pass": all(item["exit_code"] == 0 for item in builds) and bundle is not None}
    write_json("build-results.json", build_result)
    write_json("preflight/legacy-metadata-after-build.json", lstat(LEGACY))
    ok = inventory["pass"] and manifest["pass"] and statics["pass"] and build_result["pass"]
    print(json.dumps({"pass": ok, "bundle_binary": build_result["bundle_binary"]}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
