#!/usr/bin/env python3
"""Map the full Rust negative suite to the frozen path/type and fail-closed rows."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def check(identifier: str, test_name: str, log: str) -> dict[str, object]:
    passed = f"test runtime::tests::{test_name} ... ok" in log
    return {"id": identifier, "test": test_name, "result": "PASS" if passed else "FAIL", "evidence": "build-test.log"}


def main() -> int:
    log_path = EVIDENCE / "build-test.log"
    log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    checks = [
        check("P120-M011-A", "runtime_path_is_exact_and_other_paths_are_rejected", log),
        check("P120-M011-B", "link_hardlink_and_sidecar_boundaries_fail_closed", log),
        check("P120-M011-C", "tampered_content_and_schema_fail_closed", log),
        check("P120-M012-A", "invalid_or_unpaired_input_is_rejected_before_storage", log),
        check("P120-M012-B", "extra_ipc_fields_are_rejected_before_runtime_logic", log),
        check("P120-M012-C", "injected_failure_preserves_database_and_sentinel", log),
    ]
    passed = all(entry["result"] == "PASS" for entry in checks)
    payload = {
        "schema": "lifeos-p3-120/negative-results-v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }
    (EVIDENCE / "negative-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": payload["result"], "checks": len(checks)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
