#!/usr/bin/env python3
"""Build a non-self-referential SHA-256 manifest for the P3-118 evidence package."""

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"MANIFEST.md", ".swift-module-cache"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    entries = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name in EXCLUDED or ".swift-module-cache" in path.parts:
            continue
        entries.append((path.relative_to(ROOT).as_posix(), sha256(path), path.stat().st_size))
    lines = [
        "# LIFEOS-P3-118 Evidence Manifest",
        "",
        "- Scope: P3-118-only helper, plan, and fail-closed evidence. The frozen P3-116/P3-117 assets are external read-only inputs, rehashed in `evidence/preflight/fixed_inputs.json`.",
        "- Status: `Blocked` before Chrome launch, Computer Use query, native window capture, or screenshot creation.",
        "- Excluded by design: this manifest itself and ephemeral Swift module-cache artifacts; no candidate or historical asset is included or modified.",
        "- Delivery report reference: `lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md`.",
        "",
        "| Relative path | SHA-256 | Bytes |",
        "|---|---|---:|",
    ]
    lines.extend(f"| `{relative}` | `{digest}` | {size} |" for relative, digest, size in entries)
    lines.append("")
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
