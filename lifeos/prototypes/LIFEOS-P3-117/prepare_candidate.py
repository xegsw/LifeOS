#!/usr/bin/env python3
"""Create the only permitted P3-117 disposable candidate and audit its probe."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TASK_ROOT.parents[2]
SOURCE_ROOT = PROJECT_ROOT / "lifeos/prototypes/LIFEOS-P3-116"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-117-native-capture-v1")
EVIDENCE_ROOT = TASK_ROOT / "evidence/preflight"

FIXED = {
    "lifeos/prototypes/LIFEOS-P3-116/index.html": "d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b",
    "lifeos/prototypes/LIFEOS-P3-116/app.js": "c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f",
    "lifeos/prototypes/LIFEOS-P3-116/styles.css": "cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3",
    "lifeos/prototypes/LIFEOS-P3-116/fixtures.js": "a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93",
    "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md": "584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393",
    "lifeos/prototypes/LIFEOS-P3-116/state_machine.json": "2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc",
    "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json": "c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49",
    "lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md": "bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467",
    "lifeos/reviews/LIFEOS-P3-116_pm_review.md": "f698ade8695fc966034031129d271f25fcb35f2dd714acd3ba85a04cb3acef0d",
    "lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/MANIFEST.md": "58e778aeeb3f8c7306d8981409a1a0aae234c7137fae9eb3b660355c1cdc969b",
    "lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/attempt-2/MANIFEST.md": "e41fe9514af6df1b6e272f92cf4c100f4b9f1bc1c3f4137c69a8a2a591aa3799",
    "lifeos/reviews/LIFEOS-P3-116/pm_evidence/rework-1/attempt_2_blocked_assessment.md": "4dde5d041f7d29875a5efb131c1568c425f2ff63d359eb90dd1f4a32a797fc2a",
    "lifeos/ACCEPTANCE_GOVERNANCE.md": "86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c",
}
COPY_NAMES = (
    "index.html",
    "app.js",
    "styles.css",
    "fixtures.js",
    "interaction_contract.md",
    "state_machine.json",
    "visual_contract.json",
    "ia_reconciliation.md",
)
PROBE_FORBIDDEN = ("fetch(", "XMLHttpRequest", "WebSocket", "localStorage", "sessionStorage", "indexedDB", "document.cookie", "navigator.sendBeacon")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if TEMP_ROOT.exists():
        raise RuntimeError(f"refusing non-empty/reused temporary root: {TEMP_ROOT}")

    actual = {}
    for relative, expected in FIXED.items():
        source = PROJECT_ROOT / relative
        found = digest(source)
        actual[relative] = {"sha256": found, "expected": expected, "match": found == expected}
    if not all(item["match"] for item in actual.values()):
        write_json(EVIDENCE_ROOT / "fixed_inputs.json", {
            "task": "LIFEOS-P3-117",
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "all_match": False,
            "result": "BLOCKED_ABF_FIXED_INPUT_MISMATCH",
            "inputs": actual,
            "read_only_source_root": str(SOURCE_ROOT),
            "statement": "No temporary root was created by this failed hash preflight.",
        })
        raise RuntimeError("fixed-input hash mismatch; no temporary root created")

    probe = TASK_ROOT / "evidence_probe.js"
    text = probe.read_text(encoding="utf-8")
    forbidden = [token for token in PROBE_FORBIDDEN if token in text]
    required = ("P117-PROBE-V1", "location.protocol", "window.innerWidth", "window.devicePixelRatio", "Alt+Shift+P", "data-action")
    missing = [token for token in required if token not in text]
    if forbidden or missing:
        raise RuntimeError(f"probe audit failed: forbidden={forbidden}; missing={missing}")

    TEMP_ROOT.mkdir(mode=0o700)
    candidate = TEMP_ROOT / "candidate"
    profile = TEMP_ROOT / "chrome-profile"
    candidate.mkdir()
    profile.mkdir()
    for name in COPY_NAMES:
        shutil.copy2(SOURCE_ROOT / name, candidate / name)
    for name in COPY_NAMES:
        source_hash = digest(SOURCE_ROOT / name)
        copy_hash = digest(candidate / name)
        if source_hash != copy_hash:
            raise RuntimeError(f"copy mismatch for {name}")

    shutil.copy2(probe, candidate / "evidence_probe.js")
    index = candidate / "index.html"
    index_text = index.read_text(encoding="utf-8")
    injection = '\n    <script src="evidence_probe.js"></script>\n'
    if index_text.count("</body>") != 1 or "evidence_probe.js" in index_text:
        raise RuntimeError("candidate index injection point is not unique")
    index.write_text(index_text.replace("</body>", injection + "  </body>"), encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    write_json(EVIDENCE_ROOT / "fixed_inputs.json", {
        "task": "LIFEOS-P3-117",
        "checked_at_utc": now,
        "all_match": True,
        "inputs": actual,
        "read_only_source_root": str(SOURCE_ROOT),
    })
    write_json(EVIDENCE_ROOT / "probe_audit.json", {
        "task": "LIFEOS-P3-117",
        "checked_at_utc": now,
        "probe": "evidence_probe.js",
        "probe_sha256": digest(probe),
        "candidate_probe_sha256": digest(candidate / "evidence_probe.js"),
        "required_tokens": list(required),
        "forbidden_tokens": list(PROBE_FORBIDDEN),
        "forbidden_hits": forbidden,
        "result": "PASS",
        "contract": "display-only; fixed overlay; no network, storage, browser-chrome reads, or product-state mutation",
    })
    write_json(EVIDENCE_ROOT / "prepare_result.json", {
        "task": "LIFEOS-P3-117",
        "checked_at_utc": now,
        "temporary_root": str(TEMP_ROOT),
        "candidate": str(candidate),
        "chrome_profile": str(profile),
        "candidate_source_hashes_before_probe": {name: digest(SOURCE_ROOT / name) for name in COPY_NAMES},
        "candidate_hashes_after_probe": {name: digest(candidate / name) for name in COPY_NAMES},
        "copy_result": "PASS",
        "index_has_task_local_probe": "evidence_probe.js" in index.read_text(encoding="utf-8"),
    })
    print(json.dumps({"result": "PASS", "candidate": str(candidate), "profile": str(profile)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
