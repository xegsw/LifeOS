#!/usr/bin/env python3
"""Small independent static checks for contract constants not inferred from UI."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parents[1]
CANDIDATE = Path(sys.argv[1]).resolve()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    runtime = CANDIDATE / "src" / "runtime.rs"
    build = CANDIDATE / "build.rs"
    source = runtime.read_text(encoding="utf-8")
    build_source = build.read_text(encoding="utf-8")
    ipc = re.search(r"const IPC: \[&str; (\d+)\] = \[(.*?)\];", source, flags=re.S)
    providers = re.search(r'fn provider_profiles\(\) -> Vec<&\'static str> \{ vec!\[(.*?)\] \}', source)
    phase_index = build_source.index("phase_b_independent_pass_required before runtime-root inspection")
    root_access_index = build_source.index("let parent = root.parent()")
    checks = {
        "exactly_20_ipc": ipc is not None and int(ipc.group(1)) == 20 and len(re.findall(r'"[^"]+"', ipc.group(2))) == 20,
        "closed_four_provider_profiles": providers is not None and providers.group(1).replace(" ", "") == '"openai","anthropic","ollama","lm_studio"',
        "real_mode_receipt_gate_precedes_root_resolution": phase_index < root_access_index,
        "synthetic_only_evidence_startup": '"content_recorded": false' in source and '"model_dispatch_count": 0' in source,
    }
    payload = {
        "schema": "lifeos-p3-141-independent-static-contract-v1",
        "candidate_read_only": str(CANDIDATE),
        "source_sha256": {"runtime.rs": digest(runtime), "build.rs": digest(build)},
        "checks": checks,
        "pass": all(checks.values()),
    }
    output = REVIEW / "evidence" / "static_contract.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
