#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/xxe/Documents/No.2")
EVIDENCE = ROOT / "lifeos/engineering/LIFEOS-P3-102/evidence"
CLI = ROOT / "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py"
TARGET = Path("/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1")
DB = TARGET / "capture.sqlite"
PAGE = TARGET / "today.html"
OUT = ROOT / "lifeos/reviews/LIFEOS-P3-102/pm_evidence/initial/verification_results.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cli(db: Path, command: str, *args: str) -> tuple[int, dict]:
    cp = subprocess.run(
        [sys.executable, str(CLI), "--db", str(db), command, *args],
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(cp.stdout) if cp.stdout.strip() else {}
    return cp.returncode, payload


def metadata(path: Path) -> dict:
    s = os.lstat(path)
    return {
        "path": str(path),
        "inode": s.st_ino,
        "device": s.st_dev,
        "size": s.st_size,
        "mode": stat.S_IMODE(s.st_mode),
        "nlink": s.st_nlink,
        "is_dir": stat.S_ISDIR(s.st_mode),
        "is_file": stat.S_ISREG(s.st_mode),
        "is_symlink": stat.S_ISLNK(s.st_mode),
    }


def main() -> int:
    manifest_rows = []
    for line in (EVIDENCE / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `") or "SHA-256" in line:
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        rel, expected = cells
        path = (EVIDENCE / rel).resolve()
        actual = sha(path)
        manifest_rows.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})

    acceptance = json.loads((EVIDENCE / "acceptance_matrix.json").read_text(encoding="utf-8"))
    results = json.loads((EVIDENCE / "results.json").read_text(encoding="utf-8"))
    integrity = json.loads((EVIDENCE / "input_integrity.json").read_text(encoding="utf-8"))
    retained_before = {"directory": metadata(TARGET), "db": metadata(DB), "page": metadata(PAGE), "names": sorted(os.listdir(TARGET))}

    tmp = Path(tempfile.mkdtemp(prefix="lifeos-p3-102-pm-", dir="/private/tmp"))
    fixture_db = tmp / "capture.sqlite"
    fixture_page = tmp / "today.html"
    fixture = {"status": "FAIL"}
    try:
        text = "fixed non-sensitive PM verification text"
        key = "pm-fixed-key"
        c1, p1 = run_cli(fixture_db, "capture", "--text", text, "--key", key)
        c2, p2 = run_cli(fixture_db, "capture", "--text", text, "--key", key)
        before_conflict = sha(fixture_db)
        c3, p3 = run_cli(fixture_db, "capture", "--text", "fixed conflict", "--key", key)
        after_conflict = sha(fixture_db)
        c4, p4 = run_cli(fixture_db, "today")
        c5, p5 = run_cli(fixture_db, "render")
        before_failure_db = sha(fixture_db)
        before_failure_page = sha(fixture_page)
        c6, p6 = run_cli(fixture_db, "capture", "--text", "fixed failure", "--key", "pm-failure", "--inject-failure")
        names = sorted(os.listdir(tmp))
        fixture_pass = all([
            c1 == 0 and p1.get("status") == "saved",
            c2 == 0 and p2.get("status") == "idempotent_repeat",
            c3 == 2 and p3.get("status") == "blocked" and before_conflict == after_conflict,
            c4 == 0 and len(p4.get("records", [])) == 1,
            c5 == 0 and p5.get("status") == "rendered" and fixture_page.is_file(),
            c6 == 2 and p6.get("status") == "blocked",
            before_failure_db == sha(fixture_db),
            before_failure_page == sha(fixture_page),
            names == ["capture.sqlite", "today.html"],
        ])
        fixture = {
            "status": "PASS" if fixture_pass else "FAIL",
            "steps": {"first": p1.get("status"), "repeat": p2.get("status"), "conflict": p3.get("status"), "today_count": len(p4.get("records", [])), "render": p5.get("status"), "failure": p6.get("status")},
            "allowed_names": names,
            "clear_invoked": False,
            "contains_user_input": False,
        }
    finally:
        shutil.rmtree(tmp)

    retained_after = {"directory": metadata(TARGET), "db": metadata(DB), "page": metadata(PAGE), "names": sorted(os.listdir(TARGET))}
    retained_unchanged = retained_before == retained_after
    report = {
        "task_id": "LIFEOS-P3-102",
        "submitted_manifest": {"verified": sum(r["match"] for r in manifest_rows), "total": len(manifest_rows), "mismatches": [r for r in manifest_rows if not r["match"]]},
        "acceptance_matrix": {"pass": sum(r.get("status") == "PASS" for r in acceptance), "total": len(acceptance), "unique_test_ids": len({r.get("test_id") for r in acceptance}), "unique_fixture_ids": len({r.get("fixture_id") for r in acceptance}), "unique_execution_ids": len({r.get("execution_id") for r in acceptance})},
        "submitted_counts": results.get("counts"),
        "submitted_status": results.get("status"),
        "candidate_hashes": {"verified": sum(r.get("match") for r in integrity.get("after_candidate_hashes", [])), "total": len(integrity.get("after_candidate_hashes", []))},
        "evidence_redaction_scan": integrity.get("evidence_redaction_scan"),
        "retained_metadata": {"before": retained_before, "after": retained_after, "unchanged_during_pm": retained_unchanged, "content_read": False, "content_hashed_by_pm": False},
        "fresh_fixed_fixture": fixture,
        "pm_temp_residue": os.path.lexists(tmp),
    }
    report["status"] = "PASS" if all([
        report["submitted_manifest"]["verified"] == 17,
        report["submitted_manifest"]["total"] == 17,
        report["acceptance_matrix"]["pass"] == 12,
        report["acceptance_matrix"]["total"] == 12,
        report["acceptance_matrix"]["unique_test_ids"] == 12,
        report["acceptance_matrix"]["unique_fixture_ids"] == 12,
        report["acceptance_matrix"]["unique_execution_ids"] == 12,
        report["candidate_hashes"]["verified"] == 7,
        report["candidate_hashes"]["total"] == 7,
        report["evidence_redaction_scan"].get("hit_count") == 0,
        retained_unchanged,
        fixture["status"] == "PASS",
        not report["pm_temp_residue"],
    ]) else "FAIL"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "manifest": report["submitted_manifest"], "matrix": report["acceptance_matrix"], "candidate_hashes": report["candidate_hashes"], "fresh_fixed_fixture": fixture["status"], "retained_unchanged": retained_unchanged, "pm_temp_residue": report["pm_temp_residue"]}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
