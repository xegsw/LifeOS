#!/usr/bin/env python3
"""Offline negative controls for the Phase C independent-review receipt gate.

This harness never creates an accepting receipt.  Every review-shaped fixture
binds deliberately wrong candidate data; the only positive compilation is the
separate synthetic-review mode.  All generated material stays under the one
authorized temporary root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = TASK_ROOT / "candidate"
TEMP_ROOT = Path("/private/tmp/lifeos-p3-141-controlled-pilot-v1")
RECEIPT_NAME = "phase_b_pass_receipt.json"
TASK_SHA = "88b0dbcafd525604b08ebb0dffc07dc360635666612c87a2cdc94e661e72ac5a"
ABF_SHA = "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2"
RECEIPT_SCHEMA = "lifeos.p3-141.phase-b-independent-pass-receipt.v1"
MANIFEST_SCHEMA = "lifeos.p3-141.phase-b-independent-manifest.v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_binding() -> tuple[str, str]:
    commit = subprocess.check_output(["git", "-C", str(CANDIDATE), "rev-parse", "HEAD"], text=True).strip()
    tree = hashlib.sha256()
    for path in sorted(item for item in CANDIDATE.rglob("*") if item.is_file()):
        relative = path.relative_to(CANDIDATE).as_posix().encode("utf-8")
        content = path.read_bytes()
        tree.update(len(relative).to_bytes(8, "big"))
        tree.update(relative)
        tree.update(len(content).to_bytes(8, "big"))
        tree.update(content)
    return commit, tree.hexdigest()

def run_git(root: Path, *args: str) -> None:
    completed = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr}")


def cargo(case: str, extra: dict[str, str], expected: str) -> dict[str, object]:
    env = os.environ.copy()
    env.update(
        {
            "LIFEOS_INPUT_MODE": "real_self_use",
            "LIFEOS_P3_141_BUILD_MODE": "phase_c_real",
            # A relative path proves the receipt gate runs before root parsing.
            "LIFEOS_RUNTIME_ROOT": "must-not-be-parsed-before-receipt-gate",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TEMP_ROOT / "cargo-target"),
        }
    )
    env.pop("LIFEOS_P3_141_PHASE_B_RECEIPT", None)
    env.pop("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH", None)
    env.update(extra)
    completed = subprocess.run(
        ["/Users/xxe/.cargo/bin/cargo", "check", "--locked", "--offline"],
        cwd=CANDIDATE,
        text=True,
        capture_output=True,
        env=env,
    )
    combined = completed.stdout + completed.stderr
    if completed.returncode == 0 or expected not in combined:
        raise AssertionError(f"{case}: exit={completed.returncode}, expected={expected!r}, output={combined[-1600:]}")
    return {"case": case, "exit": completed.returncode, "expected_rejection": expected, "passed": True}


def synthetic_positive() -> dict[str, object]:
    runtime = TEMP_ROOT / "gate-synthetic-runtime"
    runtime.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(
        {
            "LIFEOS_INPUT_MODE": "synthetic",
            "LIFEOS_P3_141_BUILD_MODE": "synthetic_review",
            "LIFEOS_RUNTIME_ROOT": str(runtime),
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TARGET_DIR": str(TEMP_ROOT / "cargo-target"),
        }
    )
    env.pop("LIFEOS_P3_141_PHASE_B_RECEIPT", None)
    env.pop("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH", None)
    completed = subprocess.run(
        ["/Users/xxe/.cargo/bin/cargo", "check", "--locked", "--offline"],
        cwd=CANDIDATE,
        text=True,
        capture_output=True,
        env=env,
    )
    if completed.returncode:
        raise AssertionError(f"synthetic positive failed: {completed.stdout[-800:]}{completed.stderr[-800:]}")
    return {"case": "synthetic_review_without_receipt", "exit": 0, "passed": True}


def review_fixture(label: str, receipt_mutate=None, manifest_mutate=None, raw_receipt=None) -> tuple[Path, Path, Path]:
    root = TEMP_ROOT / "phase-b-gate-fixtures" / f"independent-review-worktree-{label}"
    attempt = root / "lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-negative"
    attempt.mkdir(parents=True, exist_ok=False)
    manifest = attempt / "FINAL_MANIFEST.json"
    receipt = attempt / RECEIPT_NAME
    manifest_payload = {
        "schema": MANIFEST_SCHEMA,
        "task_id": "LIFEOS-P3-141",
        "review_identity": {"role": "independent_review", "attempt_id": "attempt-negative"},
        "review_conclusion": "PASS",
        # Deliberately wrong: this harness can never form a valid receipt.
        "candidate_commit": "0" * 40,
        "candidate_tree_sha256": "0" * 64,
        "file_count_excluding_manifest": 1,
        "tree_sha256_excluding_manifest": "1" * 64,
        "files": {"independent_review.md": {"sha256": "2" * 64}},
    }
    if manifest_mutate is not None:
        manifest_mutate(manifest_payload)
    manifest.write_text(json.dumps(manifest_payload, sort_keys=True) + "\n", encoding="utf-8")
    receipt_payload = {
        "schema": RECEIPT_SCHEMA,
        "task_id": "LIFEOS-P3-141",
        "task_sha256": TASK_SHA,
        "abf_id": "ABF-P3-141-v1",
        "abf_sha256": ABF_SHA,
        "candidate_commit": "0" * 40,
        "candidate_tree_sha256": "0" * 64,
        "verdict": "PASS",
        "review_identity": {"role": "independent_review", "attempt_id": "attempt-negative"},
        "review_manifest": {"file": "FINAL_MANIFEST.json", "sha256": sha256(manifest), "schema": MANIFEST_SCHEMA},
        "issued_at_utc": "2026-08-30T00:00:00Z",
    }
    if receipt_mutate is not None:
        receipt_mutate(receipt_payload)
    receipt.write_text(raw_receipt if raw_receipt is not None else json.dumps(receipt_payload, sort_keys=True) + "\n", encoding="utf-8")
    for path in (receipt, manifest):
        path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    run_git(root, "init", "--quiet")
    run_git(root, "config", "user.email", "p3-141-negative@example.invalid")
    run_git(root, "config", "user.name", "P3-141 negative fixture")
    run_git(root, "add", "lifeos")
    run_git(root, "commit", "--quiet", "-m", "negative receipt fixture")
    return root, attempt, receipt


def rewrite_receipt(path: Path, mutate) -> None:
    path.chmod(stat.S_IWUSR | stat.S_IRUSR)
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.output.is_absolute() or TASK_ROOT not in args.output.parents:
        parser.error("--output must be an absolute file beneath this task root")
    if TEMP_ROOT.exists():
        # The caller's explicit cleanup normally removes this root. Refuse to
        # merge with unknown remnants rather than replacing them.
        raise SystemExit("authorized temp root must be absent before receipt-gate regression")
    TEMP_ROOT.mkdir(mode=0o700)
    results: list[dict[str, object]] = []
    try:
        results.append(synthetic_positive())
        results.append(cargo("missing_receipt", {}, "requires an explicit independent receipt path"))
        results.append(cargo("legacy_string", {"LIFEOS_P3_141_PHASE_B_RECEIPT": "LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS"}, "legacy receipt string is prohibited"))

        loose = TEMP_ROOT / "loose"
        loose.mkdir()
        directory = loose / RECEIPT_NAME
        directory.mkdir()
        results.append(cargo("directory", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(directory)}, "must be one read-only regular"))
        directory.rmdir()
        target = loose / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = loose / RECEIPT_NAME
        link.symlink_to(target)
        results.append(cargo("symlink", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(link)}, "must be one read-only regular"))
        link.unlink()
        outside = loose / RECEIPT_NAME
        outside.write_text("{}", encoding="utf-8")
        outside.chmod(stat.S_IRUSR)
        linked_parent = TEMP_ROOT / "linked-parent"
        linked_parent.symlink_to(loose, target_is_directory=True)
        results.append(cargo("ancestor_link", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(linked_parent / RECEIPT_NAME)}, "has a linked or non-directory ancestor"))
        results.append(cargo("unauthorized_root", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(outside)}, "authorized review-owned hierarchy"))

        root, attempt, receipt = review_fixture("wrong-candidate")
        results.append(cargo("wrong_candidate", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "stale or bound to a different candidate commit"))

        _, _, receipt = review_fixture("wrong-abf", receipt_mutate=lambda value: value.update({"abf_sha256": "f" * 64}))
        results.append(cargo("wrong_abf", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "receipt task, ABF, schema, or Pass verdict binding rejected"))
        _, _, receipt = review_fixture("rework", receipt_mutate=lambda value: value.update({"verdict": "REWORK"}))
        results.append(cargo("rework_verdict", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "receipt task, ABF, schema, or Pass verdict binding rejected"))
        _, _, receipt = review_fixture("blocked", receipt_mutate=lambda value: value.update({"verdict": "BLOCKED"}))
        results.append(cargo("blocked_verdict", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "receipt task, ABF, schema, or Pass verdict binding rejected"))
        _, _, receipt = review_fixture("extra", receipt_mutate=lambda value: value.update({"unexpected": True}))
        results.append(cargo("extra_field", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "fails the exact schema"))
        duplicate = '{"schema":"' + RECEIPT_SCHEMA + '","schema":"' + RECEIPT_SCHEMA + '"}\n'
        _, _, receipt = review_fixture("duplicate", raw_receipt=duplicate)
        results.append(cargo("duplicate_field", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "malformed or contains duplicate fields"))
        _, _, receipt = review_fixture("malformed", raw_receipt="{not-json}\n")
        results.append(cargo("malformed", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "malformed or contains duplicate fields"))
        _, _, receipt = review_fixture("manifest-hash", receipt_mutate=lambda value: value["review_manifest"].update({"sha256": "e" * 64}))
        results.append(cargo("wrong_manifest_hash", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "review-manifest hash binding rejected"))

        head, _ = candidate_binding()
        def stale_receipt(value):
            value.update({"candidate_commit": head, "candidate_tree_sha256": "0" * 64})
        def stale_manifest(value):
            value.update({"candidate_commit": head, "candidate_tree_sha256": "0" * 64})
        _, _, receipt = review_fixture("stale-tree", receipt_mutate=stale_receipt, manifest_mutate=stale_manifest)
        results.append(cargo("stale_tree", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "stale or bound to a different candidate tree"))

        # A valid-looking file becomes unusable as soon as its review-owned
        # history is changed after commit.
        rewrite_receipt(receipt, lambda value: value.update({"issued_at_utc": "2026-08-30T00:00:01Z"}))
        results.append(cargo("mutable_history", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "review ownership worktree is mutable or dirty"))

        # Even a clean, exact task/ABF/candidate-shaped receipt is rejected
        # when it lives in an unrelated Git repository rather than a declared
        # peer review worktree. It is never an accepting receipt.
        current_commit, current_tree = candidate_binding()
        def matching_receipt(value):
            value.update({"candidate_commit": current_commit, "candidate_tree_sha256": current_tree})
        def matching_manifest(value):
            value.update({"candidate_commit": current_commit, "candidate_tree_sha256": current_tree})
        _, _, receipt = review_fixture("unrelated-authority", receipt_mutate=matching_receipt, manifest_mutate=matching_manifest)
        results.append(cargo("unrelated_git_root", {"LIFEOS_P3_141_PHASE_B_RECEIPT_PATH": str(receipt)}, "not independently owned outside the candidate tree"))

        result = {
            "schema": "lifeos.p3-141.phase-b-receipt-gate-regression.v1",
            "scope": "offline synthetic only; no accepting independent receipt was created",
            "positive": results[0],
            "negative_count": len(results) - 1,
            "negative": results[1:],
        }
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    finally:
        shutil.rmtree(TEMP_ROOT)


if __name__ == "__main__":
    main()
