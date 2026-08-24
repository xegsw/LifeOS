#!/usr/bin/env python3
"""P3-108 独立复评的只读核验、allowlist 副本与离线构建 runner。

该文件在 P3-108 测试设计冻结后独立编写。它不导入、复制或执行 P3-104/106/107
的 runner、tests 或 tools；唯一执行的候选测试是 ABF 明确例外许可的冻结 Rust unit tests。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-106"
WORK = Path("/private/tmp/lifeos-p3-108-review-work-p3108a1")
OLD_METADATA = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")
OLD_P3107 = [
    Path("/private/tmp/lifeos-p3-107-review-work-r1"),
    Path("/private/tmp/lifeos-p3-107-review-work-r2"),
    Path("/private/tmp/lifeos-p3-104-p3-107-review-nominal-r1"),
]
ALLOW_FILES = [".gitignore", "Cargo.lock", "Cargo.toml", "README.md", "build.rs", "rust-toolchain.toml", "tauri.conf.json"]
ALLOW_DIRS = ["capabilities", "icons", "src", "ui"]
FORBIDDEN = {"evidence", "scripts", "tests", "target", "write_path_inventory.json"}
SNAPSHOT = {
    "lifeos/engineering/LIFEOS-P3-106/Cargo.lock": "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1",
    "lifeos/engineering/LIFEOS-P3-106/Cargo.toml": "9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e",
    "lifeos/engineering/LIFEOS-P3-106/src/runtime.rs": "0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529",
    "lifeos/engineering/LIFEOS-P3-106/src/main.rs": "4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c",
    "lifeos/engineering/LIFEOS-P3-106/capabilities/main.json": "ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b",
    "lifeos/engineering/LIFEOS-P3-106/tauri.conf.json": "d44e1e03ade7ecc5dc75f5431295de78735ccf0596a421eae0f553411294e0f0",
    "lifeos/engineering/LIFEOS-P3-106/ui/default-recovery.html": "4a6464236b03ad5ffee1d50268169558320ca90484fe646933ff19c2497a5d56",
    "lifeos/engineering/LIFEOS-P3-106/ui/no-reliable-suggestion.html": "1fdd0129ffa056fd64a08e0c6227cdf84b90cc8e964ff811dde2efabfaa85ce2",
    "lifeos/engineering/LIFEOS-P3-106/ui/restricted-offline.html": "fa918f044fa9cbb4f3eafcb117af97bc039c5bbeb075ada2e91f9da34eecd27d",
    "lifeos/engineering/LIFEOS-P3-106/ui/app.js": "62d6685c8911efb5ccaabadde350e267cb0ce58b829abbeca0580ff7025a6507",
    "lifeos/engineering/LIFEOS-P3-106/ui/styles.css": "5b93977e863bd33a6f505e585080cdf85a547c08cee1bca9c7fa05008d26d50d",
    "lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md": "7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe",
    "lifeos/reviews/LIFEOS-P3-106_pm_review.md": "97b1ad439729155588b3fbcc134f1a55144273976041f80e15443aa53c1e875f",
    "lifeos/reviews/LIFEOS-P3-106/pm_evidence/rework-1/MANIFEST.md": "a4a8a56e31703c7636f7b3a10a8d8e55ffc2a910ad5ac2187b981681a0946b38",
    "lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md": "8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1",
    "lifeos/reviews/LIFEOS-P3-104_pm_review.md": "8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795",
    "lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md": "e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4",
    "lifeos/reviews/LIFEOS-P3-107_pm_review.md": "4b87f341bc673409c37c8a022944e087757db1c4195cb432154849a809cb667d",
    "lifeos/reviews/LIFEOS-P3-107/evidence/MANIFEST.md": "206bb4cc47593475b2089b092e58f0264008cd93e12acbc2fbaa78be2475b105",
    "lifeos/reviews/LIFEOS-P3-107/pm_evidence/resume-1/MANIFEST.md": "c2a244fb3b721e3f945134aaab7b53834abfca28a4a6551fb93b1e8b95534a77",
    "lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md": "370c88454c809369f80e53f993702e9e61577d623b2a7c10cab61ab44c944b1b",
}
OLD_REVIEW_HASH = "da83f2adbe4aff8449d153c9eb32a6000a2b9dce54c24a218ab4e89b2b0d8aba"
CURRENT_REVIEW_HASH = SNAPSHOT["lifeos/reviews/LIFEOS-P3-104_pm_review.md"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lstat_dict(path: Path) -> dict[str, object]:
    try:
        value = os.lstat(path)
    except FileNotFoundError:
        return {"path": str(path), "exists": False}
    return {
        "path": str(path), "exists": True, "mode": stat.S_IFMT(value.st_mode),
        "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns,
        "is_symlink": stat.S_ISLNK(value.st_mode), "nlink": value.st_nlink,
    }


def write_json(name: str, value: object) -> Path:
    path = EVIDENCE / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run(command: list[str], name: str) -> dict[str, object]:
    env = dict(os.environ)
    env["CARGO_NET_OFFLINE"] = "true"
    # 本专项 shell 的 PATH 不包含用户已冻结的 Rust 工具链；显式指向既有
    # `~/.cargo/bin` 不下载、不安装、不改变工具链，并保留调用路径于日志。
    cargo_bin = str(Path.home() / ".cargo/bin")
    env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    output = subprocess.run(command, cwd=WORK, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = EVIDENCE / "build" / f"{name}.log"
    log.parent.mkdir(exist_ok=True)
    log.write_text(output.stdout, encoding="utf-8")
    return {"id": f"P3108-M005-{name}", "command": command, "returncode": output.returncode, "log": str(log.relative_to(EVIDENCE)), "log_sha256": sha(log), "network_tokens": sum(token in output.stdout.lower() for token in ("http://", "https://", "downloading", "updating registry"))}


def snapshot() -> int:
    actual = {path: sha(ROOT / path) for path in SNAPSHOT}
    mismatches = [path for path, expected in SNAPSHOT.items() if actual[path] != expected]
    legacy_before = lstat_dict(OLD_METADATA)
    old_paths = [lstat_dict(path) for path in OLD_P3107]
    result = {
        "id": "P3108-M001-identity", "time": utc_now(), "abf_sha256": sha(ROOT / "lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor_acceptance_basis_freeze.md"),
        "task_sha256": sha(ROOT / "lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md"),
        "expected_snapshot_count": len(SNAPSHOT), "actual": actual, "mismatches": mismatches,
        "legacy_metadata_only": legacy_before, "p3107_old_paths": old_paths,
        "pass": not mismatches and all(not item["exists"] for item in old_paths),
    }
    write_json("snapshot.json", result)
    return 0 if result["pass"] else 1


def parse_manifest_106() -> tuple[list[tuple[Path, str]], list[str]]:
    manifest = ROOT / "lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md"
    entries: list[tuple[Path, str]] = []
    bad: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", line)
        if match:
            entries.append((ROOT / match.group(1), match.group(2)))
    if len(entries) != 325:
        bad.append(f"expected 325 entries, parsed {len(entries)}")
    for path, expected in entries:
        if not path.is_file() or sha(path) != expected:
            bad.append(str(path.relative_to(ROOT)))
    return entries, bad


def parse_manifest_104() -> tuple[int, list[str], bool]:
    manifest = ROOT / "lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md"
    entries: list[tuple[str, str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.match(r"([0-9a-f]{64})\s+(.+)$", line.strip())
        if match:
            entries.append((match.group(1), match.group(2)))
    unexpected: list[str] = []
    qualified = False
    base = manifest.parent
    for expected, relative in entries:
        resolved = (base / relative).resolve()
        if resolved == ROOT / "lifeos/reviews/LIFEOS-P3-104_pm_review.md":
            qualified = expected == OLD_REVIEW_HASH and sha(resolved) == CURRENT_REVIEW_HASH
            if not qualified:
                unexpected.append("P3-104 PM Review time-qualified pair mismatch")
            continue
        if not resolved.is_file() or sha(resolved) != expected:
            unexpected.append(relative)
    return len(entries), unexpected, qualified


def manifests() -> int:
    e106, bad106 = parse_manifest_106()
    count104, bad104, qualified = parse_manifest_104()
    result = {
        "id": "P3108-M003-manifests", "time": utc_now(), "p3106_entries": len(e106), "p3106_bad": bad106,
        "p3104_entries": count104, "p3104_bad": bad104, "p3104_pm_review": "PASS_TIME_QUALIFIED" if qualified else "FAIL",
        "exception": {"manifest_recorded": OLD_REVIEW_HASH, "current": CURRENT_REVIEW_HASH},
        "pass": not bad106 and not bad104 and qualified,
    }
    write_json("manifest-verification.json", result)
    return 0 if result["pass"] else 1


def no_symlink_ancestors(path: Path) -> bool:
    for parent in reversed(path.parents):
        if parent == Path("/"):
            continue
        if parent.exists() and os.path.islink(parent):
            return False
    return True


def copy_inventory() -> int:
    if lstat_dict(WORK)["exists"]:
        raise RuntimeError(f"work path already exists: {WORK}")
    if not no_symlink_ancestors(WORK):
        raise RuntimeError(f"work path has linked ancestor: {WORK}")
    WORK.mkdir(mode=0o700)
    copied: list[str] = []
    for name in ALLOW_FILES:
        source, destination = CANDIDATE / name, WORK / name
        if not source.is_file():
            raise RuntimeError(f"missing allowlisted source {source}")
        shutil.copy2(source, destination)
        copied.append(name)
    for name in ALLOW_DIRS:
        source, destination = CANDIDATE / name, WORK / name
        if not source.is_dir():
            raise RuntimeError(f"missing allowlisted source dir {source}")
        shutil.copytree(source, destination, symlinks=True)
        copied.append(f"{name}/")
    all_paths = sorted(path.relative_to(WORK).as_posix() for path in WORK.rglob("*") if path.name != "target")
    forbidden_hits = [value for value in all_paths if value.split("/")[0] in FORBIDDEN or value.startswith(".") and value != ".gitignore"]
    top = sorted({value.split("/")[0] for value in all_paths})
    allowed_top = set(ALLOW_FILES + ALLOW_DIRS)
    extra_top = [value for value in top if value not in allowed_top]
    result = {
        "id": "P3108-M004-copy", "time": utc_now(), "work": str(WORK), "copied_roots": copied,
        "inventory": all_paths, "forbidden_hits": forbidden_hits, "extra_top": extra_top,
        "pass": not forbidden_hits and not extra_top,
    }
    write_json("copy-inventory.json", result)
    return 0 if result["pass"] else 1


def static_results() -> int:
    runtime = (WORK / "src/runtime.rs").read_text(encoding="utf-8")
    main = (WORK / "src/main.rs").read_text(encoding="utf-8")
    capability = json.loads((WORK / "capabilities/main.json").read_text(encoding="utf-8"))
    config = json.loads((WORK / "tauri.conf.json").read_text(encoding="utf-8"))
    ui = "\n".join((WORK / "ui" / name).read_text(encoding="utf-8") for name in ("default-recovery.html", "no-reliable-suggestion.html", "restricted-offline.html", "app.js", "styles.css"))
    checks = {
        "runtime_identity": sha(WORK / "src/runtime.rs") == SNAPSHOT["lifeos/engineering/LIFEOS-P3-106/src/runtime.rs"],
        "main_identity": sha(WORK / "src/main.rs") == SNAPSHOT["lifeos/engineering/LIFEOS-P3-106/src/main.rs"],
        "cargo_identity": sha(WORK / "Cargo.toml") == SNAPSHOT["lifeos/engineering/LIFEOS-P3-106/Cargo.toml"],
        "lock_identity": sha(WORK / "Cargo.lock") == SNAPSHOT["lifeos/engineering/LIFEOS-P3-106/Cargo.lock"],
        "three_commands_only": runtime.count("#[tauri::command]") == 3 and all(f"fn {name}" in runtime for name in ("capture_record", "get_today", "runtime_status")),
        "no_direct_permissions": capability.get("permissions") == [],
        "csp_no_network": "connect-src ipc:" in config["app"]["security"]["csp"] and not any(token in ui for token in ("fetch(", "XMLHttpRequest", "WebSocket", "http://", "https://")),
        "deny_unknown_fields": runtime.count("deny_unknown_fields") >= 2,
        "fail_closed_sidecars": all(token in runtime for token in ("database_sidecar_rejected", "database_type_rejected", "candidate_residue_rejected")),
        "identity_labels": all(token in ui for token in ("你的记录 · 原文", "AI 建议 · 未启用", "外部来源：未启用", "你已确认")),
        "unimplemented_no_invoke": "data-unimplemented" in ui and "未启用；没有调用 IPC" in ui,
        "a11y_structure": all(token in ui for token in ("skip-link", "aria-live=\"polite\"", "prefers-reduced-motion", ":focus-visible")),
        "no_reference_embedding": not any(token in ui.lower() for token in ("01_default_recovery_preview", "02_no_reliable_suggestion_preview", "03_permission_offline_preview", "base64,")),
        "entrypoint": "runtime::run()" in main,
    }
    result = {"id": "P3108-M006-static", "time": utc_now(), "checks": checks, "pass": all(checks.values())}
    write_json("static-results.json", result)
    return 0 if result["pass"] else 1


def build() -> int:
    if not WORK.exists():
        raise RuntimeError("copy action must run before build")
    units_before = sorted(str(path) for path in Path("/private/tmp").glob("lifeos-p3-104-unit-*-*"))
    outcomes = [
        run(["cargo", "test", "--locked"], "cargo-test"),
        run(["cargo", "build", "--locked"], "cargo-build"),
        run(["cargo", "tauri", "build", "--debug", "--", "--locked"], "cargo-tauri-build"),
    ]
    units_after = sorted(str(path) for path in Path("/private/tmp").glob("lifeos-p3-104-unit-*-*"))
    # `bundle.active=false` 的冻结配置仍会产出可启动的 Tauri debug binary；
    # 这是 ABF 许可的 actual-app 入口，不能把缺少发布 bundle 误判为构建失败。
    app_candidates = [str(WORK / "target/debug/lifeos-p3-104")] if (WORK / "target/debug/lifeos-p3-104").is_file() else []
    result = {"id": "P3108-M005-build", "time": utc_now(), "outcomes": outcomes, "unit_paths_before": units_before, "unit_paths_after": units_after, "app_candidates": app_candidates,
              "pass": all(item["returncode"] == 0 and item["network_tokens"] == 0 for item in outcomes) and units_before == units_after and bool(app_candidates)}
    write_json("build-results.json", result)
    return 0 if result["pass"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("snapshot", "manifests", "copy", "static", "build"))
    args = parser.parse_args()
    return {"snapshot": snapshot, "manifests": manifests, "copy": copy_inventory, "static": static_results, "build": build}[args.action]()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        write_json("runner-error.json", {"time": utc_now(), "error": repr(error)})
        raise
