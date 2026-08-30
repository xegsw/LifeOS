#!/usr/bin/env python3
"""Review-owned static P0 check for the P3-141 Revision-2 authorization gate."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(pattern: str, text: str, description: str, failures: list[str]) -> bool:
    if re.search(pattern, text, re.S):
        return True
    failures.append(description)
    return False


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_revision2_phase_gate.py CANDIDATE ABF_V2 OUTPUT")
    candidate = Path(sys.argv[1]).resolve()
    abf_v2 = Path(sys.argv[2]).resolve()
    output = Path(sys.argv[3]).resolve()
    build = candidate / "build.rs"
    text = build.read_text(encoding="utf-8")
    abf_text = abf_v2.read_text(encoding="utf-8")
    expected_id = re.search(r"ABF ID／版本：([A-Za-z0-9._-]+)", abf_text)
    if not expected_id:
        raise SystemExit("could not read Revision-2 ABF identifier")
    expected = expected_id.group(1)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    file_count = sum(1 for path in candidate.rglob("*") if path.is_file())

    constants = re.findall(r'const (ABF_ID|ABF_SHA256): &str = "([^"]+)";', text)
    constant_map = dict(constants)
    failures: list[str] = []
    static = {
        "candidate_build_rs_sha256": digest(build),
        "revision_2_abf_sha256": digest(abf_v2),
        "expected_revision_2_abf_id": expected,
        "compiled_abf_id": constant_map.get("ABF_ID"),
        "compiled_abf_sha256": constant_map.get("ABF_SHA256"),
        "phase_c_calls_receipt_validation": require(
            r"if build_mode == BuildMode::PhaseCReal \{ Some\(validate_phase_b_receipt\(\)\) \}",
            text,
            "phase_c_real does not call the receipt validator in the expected explicit branch",
            failures,
        ),
        "receipt_validator_binds_receipt_to_compiled_abf": require(
            r"receipt\.abf_id != ABF_ID \|\| receipt\.abf_sha256 != ABF_SHA256",
            text,
            "receipt validator does not expose the compiled ABF binding comparison",
            failures,
        ),
        "revision_2_supersedes_v1_for_positive_acceptance": "Supersedes ABF-P3-141-v1 for positive acceptance" in abf_text,
    }
    static["compiled_abf_matches_revision_2"] = constant_map.get("ABF_ID") == expected
    if not static["compiled_abf_matches_revision_2"]:
        failures.append(
            f"Phase-C build gate is hard-coded to {constant_map.get('ABF_ID')!r}, not frozen {expected!r}; a Revision-2 independent PASS cannot satisfy its receipt binding."
        )
    if not static["revision_2_supersedes_v1_for_positive_acceptance"]:
        failures.append("Revision-2 ABF supersession wording missing")

    result = {
        "schema": "lifeos.p3_141.provider_restoration.independent.phase_gate.v1",
        "review_owned": True,
        "candidate_commit": head,
        "candidate_file_count": file_count,
        "candidate": str(candidate),
        "checks": static,
        "failures": failures,
        "verdict": "P0_FAIL" if failures else "PASS",
        "p0": "ABF2-M-008 / CL-PROV-06: withdrawn Phase-B v1 receipt remains the sole Phase-C authorization binding",
        "scope_note": "Static P0 proof only. No actual-Tauri run, real Provider, credential, network, Pilot, or product-model access occurred.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "failure_count": len(failures)}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
