#!/usr/bin/env python3
"""Independent, offline P3-110 copy/build/static runner.

This script is newly authored for P3-110.  It intentionally copies only a
positive source allowlist, never imports or executes P3-107--P3-109 runners.
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
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
SOURCE = ROOT / "lifeos/engineering/LIFEOS-P3-106"
EVIDENCE = ROOT / "lifeos/reviews/LIFEOS-P3-110/evidence"
WORK = Path("/private/tmp/lifeos-p3-110-review-work-v1")
UNIT_PATTERNS = [
    re.compile(r"^lifeos-p3-104-unit-(lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+$"),
    re.compile(r"^lifeos-p3-104-unit-link-target-[0-9]+$"),
    re.compile(r"^lifeos-p3-104-unit-link-[0-9]+$"),
]
ALLOWLIST = [
    ".gitignore", "Cargo.lock", "Cargo.toml", "README.md", "build.rs", "rust-toolchain.toml", "tauri.conf.json",
    "capabilities/main.json", "src/main.rs", "src/runtime.rs", "ui/app.js", "ui/default-recovery.html",
    "ui/no-reliable-suggestion.html", "ui/restricted-offline.html", "ui/styles.css", "icons/icon.png",
]
EXPECTED = {
    "Cargo.lock": "430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1",
    "Cargo.toml": "9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e",
    "src/runtime.rs": "0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529",
    "src/main.rs": "4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c",
    "capabilities/main.json": "ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(name: str, value: object) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unit_names() -> list[str]:
    # Deliberately only list immediate names; non-matches are not stat'ed/read.
    return sorted(
        name for name in os.listdir("/private/tmp") if any(pattern.fullmatch(name) for pattern in UNIT_PATTERNS)
    )


def cargo_children(cargo_pid: int) -> list[int]:
    try:
        out = subprocess.run(["pgrep", "-P", str(cargo_pid)], check=False, text=True, capture_output=True).stdout
        return sorted(int(line) for line in out.splitlines() if line.strip().isdigit())
    except OSError:
        return []


def run_cargo(command: list[str], label: str, env: dict[str, str]) -> dict[str, object]:
    log = EVIDENCE / f"{label}.log"
    started = now()
    observed_paths: list[str] = []
    observed_child_pids: list[int] = []
    with log.open("w", encoding="utf-8") as handle:
        handle.write(f"command={command!r}\nstarted_at_utc={started}\n")
        process = subprocess.Popen(command, cwd=WORK, env=env, stdout=handle, stderr=subprocess.STDOUT, text=True)
        while process.poll() is None:
            observed_paths.extend(name for name in unit_names() if name not in observed_paths)
            for pid in cargo_children(process.pid):
                if pid not in observed_child_pids:
                    observed_child_pids.append(pid)
            time.sleep(0.01)
        observed_paths.extend(name for name in unit_names() if name not in observed_paths)
        handle.write(f"finished_at_utc={now()}\nexit_code={process.returncode}\n")
    return {
        "label": label,
        "command": command,
        "cargo_pid": process.pid,
        "child_pids_observed": observed_child_pids,
        "unit_paths_observed": sorted(observed_paths),
        "exit_code": process.returncode,
        "log": str(log.relative_to(ROOT)),
        "started_at_utc": started,
        "ended_at_utc": now(),
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(WORK):
        write_json("build-results.json", {"status": "BLOCKED", "reason": "work path exists before copy", "work": str(WORK)})
        return 2

    for rel in ALLOWLIST:
        source = SOURCE / rel
        destination = WORK / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    copied = sorted(str(path.relative_to(WORK)) for path in WORK.rglob("*") if path.is_file())
    forbidden_tokens = ["evidence", "tests", "scripts", "target", "runner", "tool"]
    forbidden_present = [item for item in copied if any(token in item.split("/") for token in forbidden_tokens)]
    copy_inventory = {
        "source": str(SOURCE.relative_to(ROOT)),
        "work": str(WORK),
        "allowlist": ALLOWLIST,
        "copied_files": copied,
        "copied_file_count": len(copied),
        "forbidden_component_tokens": forbidden_tokens,
        "forbidden_present": forbidden_present,
        "pass": copied == sorted(ALLOWLIST) and not forbidden_present,
    }
    write_json("copy-inventory.json", copy_inventory)
    if not copy_inventory["pass"]:
        return 3

    static_hashes = {}
    for rel, expected in EXPECTED.items():
        actual = sha256(WORK / rel)
        static_hashes[rel] = {"expected": expected, "actual": actual, "match": expected == actual}
    runtime = (WORK / "src/runtime.rs").read_text(encoding="utf-8")
    capability = json.loads((WORK / "capabilities/main.json").read_text(encoding="utf-8"))
    command_block = re.search(r"generate_handler!\s*\[([^]]+)\]", runtime, flags=re.S)
    commands = re.findall(r"\b(capture_record|get_today|runtime_status)\b", command_block.group(1) if command_block else "")
    static_results = {
        "hashes": static_hashes,
        "registered_ipc": commands,
        "registered_ipc_exact": commands == ["capture_record", "get_today", "runtime_status"],
        "capability_permissions": capability.get("permissions"),
        "capability_empty": capability.get("permissions") == [],
        "forbidden_command_tokens_absent": all(token not in runtime for token in ["clear_record", "export_record", "Command::new", "reqwest", "tauri_plugin"]),
        "ui_network_tokens_absent": "http://" not in (WORK / "ui/app.js").read_text(encoding="utf-8") and "https://" not in (WORK / "ui/app.js").read_text(encoding="utf-8"),
    }
    static_results["pass"] = all(item["match"] for item in static_hashes.values()) and static_results["registered_ipc_exact"] and static_results["capability_empty"] and static_results["forbidden_command_tokens_absent"] and static_results["ui_network_tokens_absent"]
    write_json("static-results.json", static_results)
    if not static_results["pass"]:
        return 4

    cargo = shutil.which("cargo") or "/Users/xxe/.cargo/bin/cargo"
    if not Path(cargo).is_file():
        cargo = None
    if cargo is None:
        write_json("build-results.json", {"status": "BLOCKED", "reason": "cargo unavailable"})
        return 5
    env = os.environ.copy()
    env.update({"CARGO_NET_OFFLINE": "true", "CARGO_TARGET_DIR": str(WORK / "target")})
    unit_before = unit_names()
    if unit_before:
        write_json("build-results.json", {"status": "BLOCKED", "reason": "unit regex pre-baseline nonempty", "matches": unit_before})
        return 6
    cargo_test = run_cargo([cargo, "test", "--locked", "--", "--test-threads=1"], "cargo-test", env)
    cargo_build = run_cargo([cargo, "build", "--locked"], "cargo-build", env)
    tauri_bundle = run_cargo([cargo, "tauri", "build", "--debug"], "cargo-tauri-build", env)
    unit_after = unit_names()
    ledger_path = EVIDENCE / "unit-path-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["during_execution"] = {
        "cargo_pid": cargo_test["cargo_pid"],
        "test_process_pids": cargo_test["child_pids_observed"],
        "started_at_utc": cargo_test["started_at_utc"],
        "ended_at_utc": cargo_test["ended_at_utc"],
        "new_matching_paths": cargo_test["unit_paths_observed"],
    }
    ledger["post_execution"] = {"matches": unit_after, "pass": unit_after == []}
    write_json("unit-path-ledger.json", ledger)
    result = {
        "status": "PASS" if all(item["exit_code"] == 0 for item in [cargo_test, cargo_build, tauri_bundle]) and not unit_after else "FAIL",
        "network": "CARGO_NET_OFFLINE=true",
        "test": cargo_test,
        "build": cargo_build,
        "tauri_build": tauri_bundle,
        "unit_pre": unit_before,
        "unit_post": unit_after,
        "work_exists": WORK.exists(),
        "debug_binary": str(WORK / "target/debug/lifeos-p3-104"),
    }
    write_json("build-results.json", result)
    return 0 if result["status"] == "PASS" else 7


if __name__ == "__main__":
    sys.exit(main())
