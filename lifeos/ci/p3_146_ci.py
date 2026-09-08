"""CI-only orchestration; never launch GUI or production credential tests."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
CANDIDATE = REPO / "lifeos/engineering/LIFEOS-P3-146/candidate"
ROOT = Path("/private/tmp/lifeos-p3-146-conversation-source-v1")
OWNER = ROOT / ".ci-p3-146-owner.json"


def owner():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("CI-only entry; use the task-local replay locally")
    return {"run": os.environ["GITHUB_RUN_ID"],
            "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "task": "LIFEOS-P3-146"}


def root_tool():
    spec = importlib.util.spec_from_file_location("task_root", CANDIDATE / "tools/task_root.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    root_tool().verify()
    if OWNER.is_symlink() or not OWNER.is_file() or OWNER.stat().st_mode & 0o777 != 0o600:
        raise RuntimeError("CI ownership rejected")
    if json.loads(OWNER.read_text()) != owner():
        raise RuntimeError("different CI run owns root")


def main(action):
    expected = owner()
    if action == "init":
        if os.path.lexists(ROOT):
            raise RuntimeError("root already exists; do not reuse or clean")
        subprocess.run([sys.executable, "tools/task_root.py", "init"], cwd=CANDIDATE, check=True)
        fd = os.open(OWNER, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(expected, handle)
        verify()
    elif action == "run":
        verify()
        env = {k: os.environ[k] for k in ("PATH", "HOME", "RUSTUP_HOME", "CARGO_HOME") if k in os.environ}
        env.update(CARGO_TARGET_DIR=str(ROOT / "initial-build-cache"), TMPDIR=str(ROOT / "tmp"),
                   LIFEOS_P3_146_PROFILE="synthetic", CARGO_NET_OFFLINE="true")
        steps = [["cargo", "+1.98.0", "fmt", "--all", "--", "--check"],
                 ["cargo", "+1.98.0", "build", "--locked", "--offline"],
                 ["node", "--test", "--test-concurrency=1", "--test-timeout=15000", "tests/integration.mjs"]]
        for command in steps:
            subprocess.run(["/usr/bin/sandbox-exec", "-p", "(version 1)(allow default)(deny network*)"] + command,
                           cwd=CANDIDATE, env=env, check=True, timeout=900)
    elif action == "cleanup":
        if not os.path.lexists(ROOT):
            return
        verify()
        # GUI is never launched. Do not inspect historical PID receipts on an unrelated runner.
        if any(ROOT.rglob("*.sqlite-wal")):
            raise RuntimeError("possible unclosed writer; refuse cleanup")
        shutil.rmtree(ROOT)
    else:
        raise ValueError("expected init, run or cleanup")


if __name__ == "__main__":
    main(sys.argv[1])
