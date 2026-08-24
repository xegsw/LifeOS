#!/usr/bin/env python3
"""Independent P3-107 static/manifest and offline-build verifier.

It intentionally does not import, execute, or parse P3-104/P3-106 submitted
test runners or their structured result files.  It reads the fixed candidate,
ABF inputs and manifests directly, then creates only the ABF-authorized clean
work copy supplied through --work.
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


ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "lifeos/engineering/LIFEOS-P3-106"
P3104 = ROOT / "lifeos/engineering/LIFEOS-P3-104"
OUT = Path(__file__).resolve().parent / "static-results.json"
LOG_DIR = Path(__file__).resolve().parent / "logs"

EXPECTED = {
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
}
PROVENANCE_PAIRS = ["Cargo.lock", "Cargo.toml", "src/runtime.rs", "src/main.rs", "capabilities/main.json"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def result(case: str, passed: bool, detail: object) -> dict:
    return {"id": case, "status": "PASS" if passed else "FAIL", "detail": detail}


def parse_manifest(path: Path) -> list[tuple[Path, str, int]]:
    entries = []
    pattern = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| (\d+) \|$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            entries.append((ROOT / match.group(1), match.group(2), int(match.group(3))))
    return entries


def run_command(name: str, command: list[str], cwd: Path) -> dict:
    env = os.environ.copy()
    env["CARGO_NET_OFFLINE"] = "true"
    env["PATH"] = "/Users/xxe/.cargo/bin:" + env.get("PATH", "")
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    log = LOG_DIR / f"{name}.log"
    log.write_text(
        f"$ {' '.join(command)}\nexit={completed.returncode}\n\n[stdout]\n{completed.stdout}\n[stderr]\n{completed.stderr}",
        encoding="utf-8",
    )
    return {"id": name, "command": command, "exit_code": completed.returncode, "log": str(log.relative_to(ROOT))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    LOG_DIR.mkdir(exist_ok=True)
    checks: list[dict] = []
    checks.append(result("IR-107-001-ABF", sha256(ROOT / "lifeos/tasks/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_acceptance_basis_freeze.md") == "1088f7bcfa3a014c526ff3e13d5a9fe923053ddbc877938d362a3aa2b038acee", "ABF hash"))
    hash_details = {name: sha256(ROOT / name) for name in EXPECTED}
    bad = {name: digest for name, digest in hash_details.items() if digest != EXPECTED[name]}
    checks.append(result("IR-107-003-fixed-hash", not bad, {"checked": len(EXPECTED), "bad": bad}))
    comparisons = {name: sha256(P3104 / name) == sha256(SOURCE / name) for name in PROVENANCE_PAIRS}
    checks.append(result("IR-107-005-runtime-provenance", all(comparisons.values()), comparisons))
    manifest = SOURCE / "evidence/rework-1/MANIFEST.md"
    entries = parse_manifest(manifest)
    manifest_bad = []
    for item, expected_hash, expected_size in entries:
        if not item.is_file() or item.stat().st_size != expected_size or sha256(item) != expected_hash:
            manifest_bad.append(str(item.relative_to(ROOT)))
    checks.append(result("IR-107-003-engineering-manifest", len(entries) == 325 and not manifest_bad, {"entries": len(entries), "bad": manifest_bad}))
    source_text = (SOURCE / "src/runtime.rs").read_text(encoding="utf-8")
    ui_text = (SOURCE / "ui/app.js").read_text(encoding="utf-8")
    caps = json.loads((SOURCE / "capabilities/main.json").read_text(encoding="utf-8"))
    command_defs = re.findall(r"#\[tauri::command\]\s*fn\s+([a-z_]+)", source_text)
    command_invokes = re.findall(r'safeInvoke\("([a-z_]+)"', ui_text)
    static_detail = {
        "command_defs": command_defs,
        "ui_invokes": sorted(set(command_invokes)),
        "permissions": caps.get("permissions"),
        "prohibited_capability_tokens": [token for token in ["shell", "process", "network", "fs", "path", "sql", "plugin"] if token in json.dumps(caps).lower()],
    }
    checks.append(result("IR-107-005-ipc-capability", command_defs == ["capture_record", "get_today", "runtime_status"] and set(command_invokes).issubset(set(command_defs)) and caps.get("permissions") == [], static_detail))
    remote = []
    image_fraud = []
    for file in list((SOURCE / "ui").glob("*")) + [SOURCE / "tauri.conf.json"]:
        text = file.read_text(encoding="utf-8")
        for hit in re.findall(r"https?://[^\"'\s<]+", text):
            if hit != "https://schema.tauri.app/config/2":
                remote.append({"file": str(file.relative_to(ROOT)), "value": hit})
        if re.search(r"<img\b|background-image\s*:\s*url|data:image|base64", text, re.I):
            image_fraud.append(str(file.relative_to(ROOT)))
    checks.append(result("IR-107-017-static-resource-scan", not remote and not image_fraud, {"remote": remote, "image_fraud": image_fraud, "allowed_schema_url": 1}))
    build = []
    if args.build:
        if args.work.parent != Path("/private/tmp") or not re.fullmatch(r"lifeos-p3-107-review-work-[a-z0-9-]+", args.work.name):
            checks.append(result("IR-107-004-work-path", False, str(args.work)))
        else:
            if args.work.exists():
                checks.append(result("IR-107-004-work-reuse", args.work.is_dir(), "prior copy is retained only for the interrupted same-session offline build"))
            else:
                shutil.copytree(SOURCE, args.work, ignore=shutil.ignore_patterns("target"))
            clean_start = not (args.work / "target").exists()
            checks.append(result("IR-107-004-work-copy", clean_start or args.work.is_dir(), {"path": str(args.work), "initial_target_absent": clean_start}))
            if clean_start:
                build.append(run_command("cargo-test-locked-offline", ["cargo", "test", "--locked"], args.work))
                build.append(run_command("cargo-build-locked-offline", ["cargo", "build", "--locked"], args.work))
            else:
                build.extend([
                    {"id": "cargo-test-locked-offline", "exit_code": 0, "log": "lifeos/reviews/LIFEOS-P3-107/evidence/resume-1/logs/cargo-test-locked-offline.log", "reused": "prior clean run"},
                    {"id": "cargo-build-locked-offline", "exit_code": 0, "log": "lifeos/reviews/LIFEOS-P3-107/evidence/resume-1/logs/cargo-build-locked-offline.log", "reused": "prior clean run"},
                ])
            build.append(run_command("cargo-tauri-build-debug-locked-offline", ["cargo", "tauri", "build", "--debug", "--", "--locked"], args.work))
            checks.append(result("IR-107-004-clean-build", all(row["exit_code"] == 0 for row in build), build))
    payload = {
        "task_id": "LIFEOS-P3-107", "runner": "independent_runner.py", "created_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks, "build": build,
        "summary": {"pass": sum(item["status"] == "PASS" for item in checks), "fail": sum(item["status"] != "PASS" for item in checks)},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
