#!/usr/bin/env python3
"""LifeOS deterministic governance and synthetic regression checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TASK_ID = re.compile(r"LIFEOS-P3-(\d+)")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_checkpoint(data: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "schema", "task_id", "attempt_id", "task_contract_sha256",
        "candidate_sha256", "stage", "status", "completed_checks",
        "pending_checks", "rerun_checks", "excluded_artifacts",
        "prohibited_boundary_contact", "candidate_or_history_mutated",
        "positive_evidence_separable", "runtime", "resume_from",
        "safe_to_resume",
    }
    missing = sorted(required - data.keys())
    if missing:
        errors.append(f"checkpoint missing fields: {', '.join(missing)}")
    if data.get("schema") != "lifeos.execution-checkpoint.v1":
        errors.append("checkpoint schema mismatch")
    if data.get("status") not in {"in_progress", "paused_resumable", "blocked", "invalidated", "completed"}:
        errors.append("checkpoint status invalid")
    for name in ("task_contract_sha256", "candidate_sha256"):
        value = data.get(name, "")
        if value != "64-lowercase-hex" and not HEX64.fullmatch(str(value)):
            errors.append(f"checkpoint {name} invalid")
    if data.get("safe_to_resume") and (
        data.get("prohibited_boundary_contact")
        or data.get("candidate_or_history_mutated")
        or not data.get("positive_evidence_separable")
    ):
        errors.append("checkpoint cannot be safe_to_resume after irrecoverable facts")
    return errors


def validate_repo() -> int:
    errors: list[str] = []
    baseline_file = ROOT / "lifeos/ci/confirmed_baselines.json"
    baseline_data = load_json(baseline_file)
    decision_id = baseline_data.get("decision_id", "")
    decision_log = (ROOT / "lifeos/DECISION_LOG.md").read_text(encoding="utf-8")
    if decision_id not in decision_log:
        errors.append(f"baseline decision {decision_id} absent from DECISION_LOG")
    for item in baseline_data.get("baselines", []):
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"baseline missing: {item['path']}")
        elif sha256(path) != item["sha256"]:
            errors.append(f"baseline hash drift: {item['path']}")

    checkpoint_path = ROOT / "lifeos/templates/EXECUTION_CHECKPOINT_TEMPLATE.json"
    errors.extend(validate_checkpoint(load_json(checkpoint_path)))

    required_phrases = {
        "lifeos/ACCEPTANCE_GOVERNANCE.md": ["Paused — Resumable", "Irrecoverable Invalidation"],
        "lifeos/PM_OPERATING_MODEL.md": ["Paused — Resumable", "resume_from"],
        "lifeos/templates/TASK_BRIEF_TEMPLATE.md": ["CI 检查清单", "可恢复执行"],
        "lifeos/templates/PM_REVIEW_TEMPLATE.md": ["Paused — Resumable", "最早受影响阶段"],
    }
    for relative, phrases in required_phrases.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"governance clause missing in {relative}: {phrase}")

    for task_path in sorted((ROOT / "lifeos/tasks").glob("LIFEOS-P3-*.md")):
        match = TASK_ID.search(task_path.name)
        if not match or int(match.group(1)) < 142:
            continue
        text = task_path.read_text(encoding="utf-8")
        for phrase in ("CI 检查清单", "可恢复执行", "最早受影响阶段"):
            if phrase not in text:
                errors.append(f"future task contract missing '{phrase}': {task_path.relative_to(ROOT)}")

    checks = load_json(ROOT / "lifeos/ci/task_checks.json")
    if checks.get("schema") != "lifeos.task-checks.v1":
        errors.append("task_checks schema mismatch")
    for entry in checks.get("checks", []):
        cwd = ROOT / entry.get("working_directory", "")
        if not cwd.is_dir():
            errors.append(f"registered working directory missing: {cwd.relative_to(ROOT)}")
        if not entry.get("commands"):
            errors.append(f"registered task has no commands: {entry.get('task_id')}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("LifeOS governance guard: PASS")
    return 0


def ensure_clean_root(config: dict) -> tuple[Path, Path]:
    root = Path(config["path"])
    if root.parent != Path("/private/tmp") or root.exists() or root.is_symlink():
        raise RuntimeError(f"synthetic root must be a new direct /private/tmp child: {root}")
    root.mkdir(mode=0o700)
    os.chmod(root, 0o700)
    marker = root / config["marker_name"]
    marker.write_text(json.dumps(config["marker"], ensure_ascii=False, sort_keys=True), encoding="utf-8")
    os.chmod(marker, 0o600)
    runtime = root / config["runtime_child"]
    runtime.mkdir(mode=0o700)
    os.chmod(runtime, 0o700)
    return root, marker


def safe_cleanup(root: Path, marker: Path, expected: dict) -> None:
    if root.parent != Path("/private/tmp") or not root.exists() or root.is_symlink():
        raise RuntimeError("cleanup root identity rejected")
    metadata = marker.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1 or stat.S_IMODE(metadata.st_mode) != 0o600:
        raise RuntimeError("cleanup marker identity rejected")
    if load_json(marker) != expected:
        raise RuntimeError("cleanup marker content rejected")
    shutil.rmtree(root)
    if root.exists():
        raise RuntimeError("cleanup did not remove exact synthetic root")


def run_checks(task_id: str | None) -> int:
    registry = load_json(ROOT / "lifeos/ci/task_checks.json")
    selected = [item for item in registry["checks"] if task_id in (None, item["task_id"])]
    if not selected:
        print(f"ERROR: no registered checks for {task_id}")
        return 1
    for entry in selected:
        root = marker = None
        config = entry.get("synthetic_root")
        try:
            if config:
                root, marker = ensure_clean_root(config)
            env = os.environ.copy()
            env.update(entry.get("environment", {}))
            cwd = ROOT / entry["working_directory"]
            for command in entry["commands"]:
                executable = shutil.which(command[0], path=env.get("PATH"))
                if executable is None:
                    local_fallbacks = {
                        "node": Path("/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"),
                        "cargo": Path("/Users/xxe/.cargo/bin/cargo"),
                    }
                    fallback = local_fallbacks.get(command[0])
                    if fallback is not None and fallback.is_file():
                        executable = str(fallback)
                if executable is None:
                    raise RuntimeError(f"required deterministic tool unavailable: {command[0]}")
                resolved_command = [executable, *command[1:]]
                print(f"[{entry['task_id']}] $ {' '.join(command)}", flush=True)
                subprocess.run(resolved_command, cwd=cwd, env=env, check=True)
        finally:
            if root is not None and root.exists():
                safe_cleanup(root, marker, config["marker"])
    print("LifeOS deterministic regression: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    run_parser = subparsers.add_parser("run-checks")
    run_parser.add_argument("--task")
    checkpoint_parser = subparsers.add_parser("validate-checkpoint")
    checkpoint_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "validate":
        return validate_repo()
    if args.command == "run-checks":
        return run_checks(args.task)
    errors = validate_checkpoint(load_json(args.path))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print("Execution checkpoint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
