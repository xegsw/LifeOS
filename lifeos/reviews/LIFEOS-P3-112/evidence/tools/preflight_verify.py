#!/usr/bin/env python3
"""P3-112 independent, read-only fixed-input and candidate identity verifier."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / "lifeos/reviews/LIFEOS-P3-112/evidence"
CANDIDATE = ROOT / "lifeos/engineering/LIFEOS-P3-111/candidate"

EXPECTED = {
    "p3_111_task": (
        "lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md",
        "5b5ed1211647747e34518e1b7de02b8693e01923e09dd76a7d212a9ff5dde59e",
    ),
    "p3_111_abf": (
        "lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_acceptance_basis_freeze.md",
        "24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395",
    ),
    "initial_deliverable": (
        "lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md",
        "a84a5778bf689f63c044e53aa3d6cf644289610b5bfb1ab607fdc603ceb8ddfe",
    ),
    "rework_1_deliverable": (
        "lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_rework_1.md",
        "6f6bb1dcf5aed2b4e9e660fb30971af1f9b6e5adbccd9a75519b70c80bac9e75",
    ),
    "candidate_provenance": (
        "lifeos/engineering/LIFEOS-P3-111/candidate_provenance.md",
        "f97f1e0f5edbbe8f562b4287e5544ffd17560a4ac5da736b95e990a232f0d6cc",
    ),
    "product_gap_matrix": (
        "lifeos/engineering/LIFEOS-P3-111/product_gap_matrix.md",
        "e1451c258ec18cc57895580f4a02c04747d62b476a225cec632272d024254ff6",
    ),
    "initial_engineering_manifest": (
        "lifeos/engineering/LIFEOS-P3-111/evidence/MANIFEST.md",
        "e70f70b96e4aa1bfce2158d3e81f708b7fbc457b0348a632ade1ff4b0f4b835b",
    ),
    "rework_1_engineering_manifest": (
        "lifeos/engineering/LIFEOS-P3-111/evidence/rework-1/MANIFEST.md",
        "3f677fd533ce4ca902552e7aad661ba343070d517b9c03f9e3b4dcc89dc62ed4",
    ),
    "pm_review": (
        "lifeos/reviews/LIFEOS-P3-111_pm_review.md",
        "e8fc44bcd79b7a2d6fb0ec29f3ff23b22ece0c08fdc260236fb8113f60bb0c10",
    ),
    "rework_1_pm_evidence_manifest": (
        "lifeos/reviews/LIFEOS-P3-111/pm_evidence/rework-1/MANIFEST.md",
        "38c868b2d901af11092f8bcbb05bf2d3f3d7f58f73838fe7b31febde9796ee85",
    ),
    "submitted_semantic_verifier": (
        "lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py",
        "1537c9daa9730cb35618c71af443fafbef2a4ef1d3f6fa3457406e932873db73",
    ),
    "submitted_mutation_runner": (
        "lifeos/engineering/LIFEOS-P3-111/tools/run_disposable_mutations.py",
        "8576247e54ba2fb46994e9cd55a4d77550762020ca80a78a32d10a4bdc7f7e27",
    ),
}
EXPECTED_TREE = "cc1ff0f05d5d3993c8b113dae80a043b3d7f535a05a8236771b980a4892718a3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    fixed = []
    for name, (relative, expected) in EXPECTED.items():
        path = ROOT / relative
        actual = sha256(path) if path.is_file() else None
        fixed.append({
            "id": name,
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "pass": actual == expected,
        })

    files = []
    for path in sorted(CANDIDATE.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(CANDIDATE).as_posix()
            files.append({"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest_text = "".join(f"{item['path']}\t{item['sha256']}\n" for item in files)
    actual_tree = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
    candidate = {
        "candidate_root": "lifeos/engineering/LIFEOS-P3-111/candidate",
        "ordinary_file_count": len(files),
        "expected_ordinary_file_count": 72,
        "expected_tree_sha256": EXPECTED_TREE,
        "actual_tree_sha256": actual_tree,
        "pass": len(files) == 72 and actual_tree == EXPECTED_TREE,
        "files": files,
    }
    report = {
        "task": "LIFEOS-P3-112",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "operation": "read-only fixed input and candidate identity verification",
        "fixed_inputs": fixed,
        "fixed_input_pass_count": sum(item["pass"] for item in fixed),
        "fixed_input_total": len(fixed),
        "candidate": candidate,
        "overall_pass": all(item["pass"] for item in fixed) and candidate["pass"],
    }
    (OUT / "fixed-inputs.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (OUT / "candidate-manifest.tsv").write_text(manifest_text, encoding="utf-8")
    (OUT / "candidate-manifest.json").write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "fixed_input_pass_count": report["fixed_input_pass_count"],
        "fixed_input_total": report["fixed_input_total"],
        "candidate_file_count": candidate["ordinary_file_count"],
        "candidate_tree_sha256": actual_tree,
        "overall_pass": report["overall_pass"],
    }, sort_keys=True))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
