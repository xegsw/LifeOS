#!/usr/bin/env python3
"""P3-108 rework-1 independent evidence runner.

Written after this attempt's test design. It neither imports nor executes any
P3-104/P3-106/P3-107 submitted runner, tool, or Evidence.
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
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-106"
WORK = Path("/private/tmp/lifeos-p3-108-review-work-p3108r1a1")
NOMINAL = Path("/private/tmp/lifeos-p3-104-p3-108-review-nominal-p3108r1a1")
FIXTURES = {name: Path(f"/private/tmp/lifeos-p3-104-p3-108-review-{name}-p3108r1a1") for name in (
    "repeat", "conflict", "failure", "reopen", "dangling-final", "dangling-journal",
    "dangling-wal", "dangling-shm", "path", "link", "hardlink", "tamper", "a11y", "narrow"
)}
ALL_TEMP = [WORK, NOMINAL, *FIXTURES.values()]
OLD_METADATA = Path("/private/tmp/lifeos-p3-104-rework-static-results.json")
OLD_P3107 = [Path(p) for p in (
    "/private/tmp/lifeos-p3-107-review-work-r1",
    "/private/tmp/lifeos-p3-107-review-work-r2",
    "/private/tmp/lifeos-p3-104-p3-107-review-nominal-r1",
)]
ALLOW_FILES = [".gitignore", "Cargo.lock", "Cargo.toml", "README.md", "build.rs", "rust-toolchain.toml", "tauri.conf.json"]
ALLOW_DIRS = ["capabilities", "icons", "src", "ui"]
FORBIDDEN_TOP = {"evidence", "scripts", "tests", "write_path_inventory.json", "target"}
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

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def lstat(path: Path) -> dict:
    try:
        s = os.lstat(path)
    except FileNotFoundError:
        return {"path": str(path), "exists": False}
    return {"path": str(path), "exists": True, "kind": stat.S_IFMT(s.st_mode), "mode": s.st_mode,
            "size": s.st_size, "nlink": s.st_nlink, "mtime_ns": s.st_mtime_ns, "ctime_ns": s.st_ctime_ns,
            "is_symlink": stat.S_ISLNK(s.st_mode)}

def write(name: str, value: object) -> Path:
    path = EVIDENCE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path

def assert_absent_and_real_ancestors(path: Path) -> None:
    if os.path.lexists(path):
        raise RuntimeError(f"already exists: {path}")
    for ancestor in path.parents:
        if ancestor == Path("/"):
            break
        if ancestor.exists() and os.path.islink(ancestor):
            raise RuntimeError(f"symlink ancestor: {ancestor}")

def cargo_env() -> dict:
    env = dict(os.environ)
    env["CARGO_NET_OFFLINE"] = "true"
    env["PATH"] = str(Path.home() / ".cargo/bin") + os.pathsep + env.get("PATH", "")
    return env

def run(command: list[str], cwd: Path, log_name: str) -> dict:
    result = subprocess.run(command, cwd=cwd, env=cargo_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = EVIDENCE / "build" / log_name
    log.parent.mkdir(exist_ok=True)
    log.write_text(result.stdout, encoding="utf-8")
    lowered = result.stdout.lower()
    return {"command": command, "returncode": result.returncode, "log": str(log.relative_to(EVIDENCE)),
            "log_sha256": sha(log), "network_tokens": sum(t in lowered for t in ("http://", "https://", "downloading", "updating registry"))}

def snapshot() -> int:
    current = {p: sha(ROOT / p) for p in SNAPSHOT}
    mismatch = [p for p, expected in SNAPSHOT.items() if current[p] != expected]
    out = {"id": "P3108R1-M001-snapshot", "time": now(), "abf_sha256": sha(ROOT / "lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor_acceptance_basis_freeze.md"),
           "task_sha256": sha(ROOT / "lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md"),
           "current": current, "mismatches": mismatch, "legacy_metadata_only": lstat(OLD_METADATA),
           "p3107_old_paths": [lstat(p) for p in OLD_P3107], "pass": not mismatch and all(not lstat(p)["exists"] for p in OLD_P3107)}
    write("snapshot-before.json", out)
    return 0 if out["pass"] else 1

def manifests() -> int:
    m106 = ROOT / "lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md"
    entries106 = [(ROOT / p, h) for p, h in re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", m106.read_text(encoding="utf-8"))]
    bad106 = [str(p.relative_to(ROOT)) for p, h in entries106 if not p.is_file() or sha(p) != h]
    m104 = ROOT / "lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md"
    entries104 = [(h, r) for h, r in re.findall(r"^([0-9a-f]{64})\s+(.+)$", m104.read_text(encoding="utf-8"), re.M)]
    bad104 = []
    qualified = False
    for expected, relative in entries104:
        p = (m104.parent / relative).resolve()
        if p == ROOT / "lifeos/reviews/LIFEOS-P3-104_pm_review.md":
            qualified = expected == OLD_REVIEW_HASH and sha(p) == SNAPSHOT["lifeos/reviews/LIFEOS-P3-104_pm_review.md"]
        elif not p.is_file() or sha(p) != expected:
            bad104.append(relative)
    out = {"id": "P3108R1-M003-manifests", "time": now(), "p3106_entries": len(entries106), "p3106_bad": bad106,
           "p3104_entries": len(entries104), "p3104_bad": bad104, "p3104_pm_review": "PASS_TIME_QUALIFIED" if qualified else "FAIL",
           "exception": {"manifest_recorded": OLD_REVIEW_HASH, "current": SNAPSHOT["lifeos/reviews/LIFEOS-P3-104_pm_review.md"]},
           "pass": len(entries106) == 325 and not bad106 and not bad104 and qualified}
    write("manifest-verification.json", out)
    return 0 if out["pass"] else 1

def copy() -> int:
    assert_absent_and_real_ancestors(WORK)
    WORK.mkdir(mode=0o700)
    copied = []
    for name in ALLOW_FILES:
        shutil.copy2(CANDIDATE / name, WORK / name); copied.append(name)
    for name in ALLOW_DIRS:
        shutil.copytree(CANDIDATE / name, WORK / name, symlinks=True); copied.append(name + "/")
    inventory = sorted(p.relative_to(WORK).as_posix() for p in WORK.rglob("*") if p.name != "target")
    tops = sorted({p.split("/")[0] for p in inventory})
    allowed = set(ALLOW_FILES + ALLOW_DIRS)
    forbidden = [p for p in inventory if p.split("/")[0] in FORBIDDEN_TOP]
    extra = [p for p in tops if p not in allowed]
    out = {"id": "P3108R1-M004-copy", "time": now(), "work": str(WORK), "copied_roots": copied,
           "inventory": inventory, "forbidden_hits": forbidden, "extra_top": extra, "pass": not forbidden and not extra}
    write("copy-inventory.json", out)
    return 0 if out["pass"] else 1

def static_check() -> int:
    runtime = (WORK / "src/runtime.rs").read_text(encoding="utf-8")
    ui = "\n".join((WORK / "ui" / n).read_text(encoding="utf-8") for n in ("default-recovery.html", "no-reliable-suggestion.html", "restricted-offline.html", "app.js", "styles.css"))
    capability = json.loads((WORK / "capabilities/main.json").read_text(encoding="utf-8"))
    config = json.loads((WORK / "tauri.conf.json").read_text(encoding="utf-8"))
    checks = {
        "candidate_hashes": all(sha(WORK / Path(p).relative_to("lifeos/engineering/LIFEOS-P3-106")) == h for p, h in SNAPSHOT.items() if p.startswith("lifeos/engineering/LIFEOS-P3-106/") and (WORK / Path(p).relative_to("lifeos/engineering/LIFEOS-P3-106")).is_file()),
        "three_ipc": runtime.count("#[tauri::command]") == 3 and all(f"fn {n}" in runtime for n in ("capture_record", "get_today", "runtime_status")),
        "no_permissions": capability.get("permissions") == [],
        "no_renderer_network": "connect-src ipc:" in config["app"]["security"]["csp"] and not any(t in ui for t in ("fetch(", "XMLHttpRequest", "WebSocket", "http://", "https://")),
        "fail_closed": all(t in runtime for t in ("database_type_rejected", "database_sidecar_rejected", "candidate_residue_rejected", "record_identity_rejected", "database_schema_rejected")),
        "identity_and_a11y": all(t in ui for t in ("你的记录 · 原文", "AI 建议 · 未启用", "外部来源", "skip-link", "aria-live=\"polite\"", "prefers-reduced-motion")),
        "no_embedded_stitch": not any(t in ui.lower() for t in ("base64,", "01_default_recovery_preview", "02_no_reliable_suggestion_preview", "03_permission_offline_preview")),
    }
    out = {"id": "P3108R1-M006-static", "time": now(), "checks": checks, "pass": all(checks.values())}
    write("static-results.json", out)
    return 0 if out["pass"] else 1

def build() -> int:
    if not WORK.exists(): raise RuntimeError("copy must precede build")
    before = [lstat(p) for p in ALL_TEMP]
    outcomes = [
        run(["cargo", "test", "--locked"], WORK, "cargo-test.log"),
        run(["cargo", "build", "--locked"], WORK, "cargo-build.log"),
        run(["cargo", "tauri", "build", "--debug", "--", "--locked"], WORK, "cargo-tauri-build.log"),
        # The source configuration intentionally disables distribution bundles.  This
        # explicit debug-app packaging step creates an independently built local
        # macOS app solely so that the dynamic review can address its own candidate.
        run(["cargo", "tauri", "bundle", "--debug", "--bundles", "app", "--no-sign"], WORK, "cargo-tauri-bundle-app.log"),
        # Give the local review app a distinct bundle identifier, without changing
        # candidate source/configuration, so macOS UI automation cannot select one
        # of the historical same-name candidate apps.
        run(["cargo", "tauri", "bundle", "--debug", "--bundles", "app", "--no-sign", "--config", '{"identifier":"local.lifeos.p3-104.p3108r1"}'], WORK, "cargo-tauri-bundle-unique-id.log"),
        run(["cargo", "tauri", "bundle", "--debug", "--bundles", "app", "--no-sign", "--config", '{"identifier":"local.lifeos.p3-104.p3108r1.ui","productName":"LifeOS P3-104 P3108R1 UI"}'], WORK, "cargo-tauri-bundle-ui-isolated.log"),
        run(["cargo", "tauri", "bundle", "--debug", "--bundles", "app", "--no-sign", "--config", '{"identifier":"local.lifeos.p3-104.p3108r1.lifecycle","productName":"LifeOS P3-104 P3108R1 Lifecycle"}'], WORK, "cargo-tauri-bundle-lifecycle-isolated.log"),
    ]
    binary = WORK / "target/debug/lifeos-p3-104"
    out = {"id": "P3108R1-M005-build", "time": now(), "outcomes": outcomes, "binary": str(binary), "binary_sha256": sha(binary) if binary.is_file() else None,
           "preexisting_temp": before, "pass": binary.is_file() and all(x["returncode"] == 0 and x["network_tokens"] == 0 for x in outcomes)}
    write("build-results.json", out)
    return 0 if out["pass"] else 1

def prepare() -> int:
    for path in [NOMINAL, *FIXTURES.values()]: assert_absent_and_real_ancestors(path)
    NOMINAL.mkdir(mode=0o700)
    (NOMINAL / "sentinel.txt").write_text("P3108R1-NOMINAL-SENTINEL", encoding="utf-8")
    for path in FIXTURES.values(): path.mkdir(mode=0o700)
    (FIXTURES["path"] / "capture.sqlite").mkdir()
    os.symlink("missing.sqlite", FIXTURES["link"] / "capture.sqlite")
    os.symlink("missing.sqlite", FIXTURES["dangling-final"] / "capture.sqlite")
    out = {"id": "P3108R1-fixture-prepare", "time": now(), "ledger": [lstat(p) for p in ALL_TEMP], "pass": True}
    write("fixture-ledger-before.json", out)
    return 0

def snapshot_fixture(name: str, result_id: str, note: str) -> int:
    path = NOMINAL if name == "nominal" else FIXTURES[name]
    members = [lstat(p) for p in [path, path / "capture.sqlite", path / "capture.sqlite-journal", path / "capture.sqlite-wal", path / "capture.sqlite-shm", path / "sentinel.txt"]]
    out = {"id": result_id, "time": now(), "fixture": str(path), "note": note, "members": members}
    write(f"fixture-{name}-{result_id}.json", out)
    return 0

def inspect_db(name: str, result_id: str) -> int:
    """Read only the controlled fixture database and record normalized facts."""
    path = NOMINAL if name == "nominal" else FIXTURES[name]
    db = path / "capture.sqlite"
    out = {"id": result_id, "time": now(), "fixture": str(path), "db": lstat(db), "tables": [], "schema": {}, "rows": {}}
    if db.is_file() and not db.is_symlink():
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as con:
            out["tables"] = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
            for table in out["tables"]:
                columns = [r[1] for r in con.execute(f"pragma table_info({table})")]
                out["schema"][table] = columns
                out["rows"][table] = [dict(zip(columns, row)) for row in con.execute(f"select * from {table} order by rowid")]
    out["record_count"] = len(out["rows"].get("captures", []))
    write(f"db-{name}-{result_id}.json", out)
    return 0

def make_negative(name: str, result_id: str) -> int:
    """Construct one bounded adversarial fixture from the nominal local DB."""
    if name not in {"hardlink", "dangling-journal", "dangling-wal", "dangling-shm", "tamper"}:
        raise RuntimeError(f"unsupported negative fixture: {name}")
    destination = FIXTURES[name] / "capture.sqlite"
    if os.path.lexists(destination):
        raise RuntimeError(f"negative destination already exists: {destination}")
    source = NOMINAL / "capture.sqlite"
    if not source.is_file() or source.is_symlink():
        raise RuntimeError("nominal database is unavailable for fixture construction")
    shutil.copy2(source, destination)
    if name == "hardlink":
        os.link(destination, FIXTURES[name] / "peer.sqlite")
    elif name.startswith("dangling-"):
        suffix = name.removeprefix("dangling-")
        os.symlink("missing-sidecar", FIXTURES[name] / f"capture.sqlite-{suffix}")
    elif name == "tamper":
        with sqlite3.connect(destination) as con:
            con.execute("create table unexpected_rework_fixture (id integer primary key)")
    out = {"id": result_id, "time": now(), "name": name, "source": lstat(source), "destination": lstat(destination),
           "members": [lstat(p) for p in sorted(FIXTURES[name].iterdir())], "pass": True}
    write(f"negative-{name}-{result_id}.json", out)
    return 0

def boundary_processes() -> int:
    binary = WORK / "target/debug/lifeos-p3-104"
    cases = {
        "path": FIXTURES["path"] / "capture.sqlite", "link": FIXTURES["link"] / "capture.sqlite",
        "dangling-final": FIXTURES["dangling-final"] / "capture.sqlite", "hardlink": FIXTURES["hardlink"] / "capture.sqlite",
        "dangling-journal": FIXTURES["dangling-journal"] / "capture.sqlite", "dangling-wal": FIXTURES["dangling-wal"] / "capture.sqlite",
        "dangling-shm": FIXTURES["dangling-shm"] / "capture.sqlite",
        "external-path": Path("/private/tmp/not-p3-104-p3108r1a1/capture.sqlite"),
    }
    results = []
    for name, db in cases.items():
        env = dict(cargo_env()); env["LIFEOS_P3_104_DB_PATH"] = str(db)
        run_result = subprocess.run([str(binary)], cwd=WORK, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
        log = EVIDENCE / "raw-logs" / f"boundary-{name}.log"; log.parent.mkdir(exist_ok=True); log.write_text(run_result.stdout, encoding="utf-8")
        results.append({"case": name, "db": str(db), "returncode": run_result.returncode, "log": str(log.relative_to(EVIDENCE)), "log_sha256": sha(log), "output_code": re.findall(r"code=([a-z_]+)", run_result.stdout), "db_lstat_after": lstat(db)})
    out = {"id": "P3108R1-M013-bootstrap-boundaries", "time": now(), "results": results,
           "excluded": {"tamper": "schema contract is validated by the actual UI read path, recorded separately"},
           "pass": all(r["returncode"] == 101 and r["output_code"] for r in results)}
    write("boundary/bootstrap.json", out)
    return 0 if out["pass"] else 1

def cleanup() -> int:
    # Exact ledger only; no glob/find/prefix deletion.
    for path in ALL_TEMP:
        if os.path.lexists(path): shutil.rmtree(path)
    out = {"id": "P3108R1-M016-cleanup", "time": now(), "paths": [lstat(p) for p in ALL_TEMP],
           "p3107": [lstat(p) for p in OLD_P3107], "legacy_metadata_only": lstat(OLD_METADATA),
           "pass": all(not os.path.lexists(p) for p in ALL_TEMP) and all(not os.path.lexists(p) for p in OLD_P3107)}
    write("cleanup.json", out)
    return 0 if out["pass"] else 1

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("action", choices=("snapshot", "manifests", "copy", "static", "build", "prepare", "fixture-snapshot", "inspect-db", "make-negative", "boundary-processes", "cleanup")); parser.add_argument("--name"); parser.add_argument("--id"); parser.add_argument("--note", default="")
    args = parser.parse_args(); action = args.action
    if action == "fixture-snapshot":
        if not args.name or not args.id: raise RuntimeError("fixture-snapshot requires --name and --id")
        return snapshot_fixture(args.name, args.id, args.note)
    if action == "inspect-db":
        if not args.name or not args.id: raise RuntimeError("inspect-db requires --name and --id")
        return inspect_db(args.name, args.id)
    if action == "make-negative":
        if not args.name or not args.id: raise RuntimeError("make-negative requires --name and --id")
        return make_negative(args.name, args.id)
    return {"snapshot": snapshot, "manifests": manifests, "copy": copy, "static": static_check, "build": build, "prepare": prepare, "boundary-processes": boundary_processes, "cleanup": cleanup}[action]()

if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception as e:
        write("runner-error.json", {"time": now(), "error": repr(e)})
        raise
