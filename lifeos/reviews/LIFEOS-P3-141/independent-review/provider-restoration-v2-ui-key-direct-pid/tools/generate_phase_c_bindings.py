#!/usr/bin/env python3
"""Write and verify review-owned v2 manifest/receipt with strict regular files."""
import argparse
import hashlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "LIFEOS-P3-141"
TASK_SHA256 = "c97419a1818e0aa6fe6fc61c487e3ef97746e199b2c7d22435d8c05090374800"
INVENTORY_SHA256 = "3651e046da8211f06bf5144a155a0505b7ddfbaab67a249e51d94aeae09861a5"
ABF_ID = "ABF-P3-141-v2"
ABF_SHA256 = "096ad12beec63b78aaa3be92535b4a6ea632cdc4235c1d83f224db955d5dc9ea"
MANIFEST_SCHEMA = "lifeos.p3-141.independent-review-manifest.v2"
RECEIPT_SCHEMA = "lifeos.p3-141.phase-c-independent-pass-receipt.v2"
ATTEMPT_ID = "provider-restoration-v2-ui-key-direct-pid"
EXCLUDED = {"FINAL_MANIFEST.json", "phase_c_v2_independent_pass_receipt.json"}


def regular_files(root: Path, excluded: set[str] = set()):
    rows = []
    for current, directories, names in os.walk(root, topdown=True, followlinks=False):
        for directory in directories:
            if (Path(current) / directory).is_symlink():
                raise SystemExit(f"linked review entry rejected: {(Path(current) / directory).relative_to(root)}")
        directories[:] = sorted(directories)
        for name in sorted(names):
            item = Path(current) / name
            rel = item.relative_to(root).as_posix()
            if rel in excluded:
                continue
            meta = item.lstat()
            if stat.S_ISLNK(meta.st_mode) or not stat.S_ISREG(meta.st_mode):
                raise SystemExit(f"non-regular review entry rejected: {rel}")
            rows.append((rel, item))
    # Rust PathBuf::Ord is component-aware: src/runtime/* precedes
    # src/runtime.rs.  Do not replace this with lexical relative strings.
    return sorted(rows, key=lambda row: Path(row[0]))


def candidate_digest(root: Path):
    files = regular_files(root)
    digest = hashlib.sha256()
    for relative, item in files:
        path_bytes = relative.encode("utf-8")
        content = item.read_bytes()
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return len(files), digest.hexdigest()


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(root: Path, candidate: Path, commit: str):
    rows = regular_files(root, EXCLUDED)
    files = {relative: sha(item) for relative, item in rows}
    content = b"".join(
        len(relative.encode("utf-8")).to_bytes(8, "big") + relative.encode("utf-8") +
        len(item.read_bytes()).to_bytes(8, "big") + item.read_bytes()
        for relative, item in rows
    )
    _, candidate_tree = candidate_digest(candidate)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "task_id": TASK_ID,
        "task_sha256": TASK_SHA256,
        "fixed_input_inventory_sha256": INVENTORY_SHA256,
        "abf_id": ABF_ID,
        "abf_sha256": ABF_SHA256,
        "review_identity": {"role": "independent_review", "attempt_id": ATTEMPT_ID},
        "review_conclusion": "PASS",
        "candidate_commit": commit,
        "candidate_tree_sha256": candidate_tree,
        "file_count_excluding_manifest": len(rows),
        "tree_sha256_excluding_manifest": hashlib.sha256(content).hexdigest(),
        "files": files,
    }
    manifest_path = root / "FINAL_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "task_id": TASK_ID,
        "task_sha256": TASK_SHA256,
        "fixed_input_inventory_sha256": INVENTORY_SHA256,
        "abf_id": ABF_ID,
        "abf_sha256": ABF_SHA256,
        "candidate_commit": commit,
        "candidate_tree_sha256": candidate_tree,
        "verdict": "PASS",
        "review_identity": {"role": "independent_review", "attempt_id": ATTEMPT_ID},
        "review_manifest": {
            "file": "FINAL_MANIFEST.json",
            "sha256": sha(manifest_path),
            "schema": MANIFEST_SCHEMA,
        },
        "issued_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    receipt_path = root / "phase_c_v2_independent_pass_receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest_sha256": sha(manifest_path), "receipt_sha256": sha(receipt_path), "candidate_tree_sha256": candidate_tree, "review_files": len(rows)}, sort_keys=True))


def verify(root: Path, candidate: Path, commit: str):
    manifest_path = root / "FINAL_MANIFEST.json"
    receipt_path = root / "phase_c_v2_independent_pass_receipt.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    _, digest = candidate_digest(candidate)
    checks = {
        "manifest_schema": manifest.get("schema") == MANIFEST_SCHEMA,
        "receipt_schema": receipt.get("schema") == RECEIPT_SCHEMA,
        "candidate_commit": manifest.get("candidate_commit") == commit == receipt.get("candidate_commit"),
        "candidate_tree": manifest.get("candidate_tree_sha256") == digest == receipt.get("candidate_tree_sha256"),
        "manifest_binding": receipt.get("review_manifest") == {"file": "FINAL_MANIFEST.json", "sha256": sha(manifest_path), "schema": MANIFEST_SCHEMA},
        "review_identity": manifest.get("review_identity") == receipt.get("review_identity") == {"role": "independent_review", "attempt_id": ATTEMPT_ID},
        "pass": manifest.get("review_conclusion") == receipt.get("verdict") == "PASS",
    }
    print(json.dumps({"checks": checks, "pass": all(checks.values())}, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=("write", "verify"))
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--candidate", type=Path, required=True)
parser.add_argument("--commit", required=True)
args = parser.parse_args()
root = args.root.resolve()
candidate = args.candidate.resolve()
if root.name != ATTEMPT_ID or not (candidate / "build.rs").is_file():
    raise SystemExit("root shape rejected")
if args.mode == "write":
    write(root, candidate, args.commit)
else:
    verify(root, candidate, args.commit)
