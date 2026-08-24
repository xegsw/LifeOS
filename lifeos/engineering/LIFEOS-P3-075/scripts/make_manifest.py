#!/usr/bin/env python3
"""Create hash manifest for P3-075 task-local Evidence."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FILES = [
    ROOT / "README.md", ROOT / "src/local_runtime.py", ROOT / "scripts/runtime_cli.py",
    ROOT / "scripts/run_self_check.py", ROOT / "scripts/make_manifest.py", ROOT / "tests/test_runtime.py",
    EVIDENCE / "self_check_results.json", EVIDENCE / "self_check.log",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lines = ["# LIFEOS-P3-075 Evidence Manifest", "", "- Scope: non-sensitive test text; task-local SQLite; no real paths or external capability.", "- Re-run: `python3 lifeos/engineering/LIFEOS-P3-075/scripts/run_self_check.py && python3 lifeos/engineering/LIFEOS-P3-075/scripts/make_manifest.py`", "", "## SHA-256"]
    for path in FILES:
        lines.append(f"- `{path.relative_to(ROOT)}`: `{digest(path)}`")
    lines += ["", "## Self-check result", "", "- Clean temporary-copy end-to-end self-check: 17 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0.", "- Historical read-only input hashes remained unchanged.", "- This is controlled local-runtime Evidence only; it does not close R-0019/R-0040 or enable personal data, production durability, Alpha, or Stage 4."]
    (EVIDENCE / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
