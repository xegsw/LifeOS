#!/usr/bin/env python3
"""Review-owned, offline SHA-256 and Git-lineage verifier for P3-143 manifests."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Optional


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def resolve_repo_path(repo: Path, manifest: Path, declared: str) -> Path:
    if Path(declared).is_absolute():
        raise ValueError("absolute_declared_path")
    result = (manifest.parent / declared).resolve()
    if result != repo and repo not in result.parents:
        raise ValueError("declared_path_escapes_repo")
    return result


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def verify_manifest(repo: Path, manifest_path: Path, commit: Optional[str], candidate_prefix: Optional[str], snapshot_commit: Optional[str]) -> dict:
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = document.get("files")
    result = {
        "manifest": str(manifest_path.relative_to(repo)),
        "basis": f"git:{snapshot_commit}" if snapshot_commit else "current_worktree",
        "schema": document.get("schema"),
        "self_referential": document.get("self_referential"),
        "declared_file_count": len(rows) if isinstance(rows, list) else None,
        "checked": 0,
        "mismatches": [],
        "candidate_git_checked": 0,
        "candidate_git_mismatches": [],
    }
    if document.get("self_referential") is not False and document.get("self_exclusion") is not True:
        result["mismatches"].append({"kind": "self_reference_not_false"})
    if not isinstance(rows, list):
        result["mismatches"].append({"kind": "files_not_list"})
        return result
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            result["mismatches"].append({"index": index, "kind": "entry_not_object"})
            continue
        declared = row.get("path")
        expected_hash = row.get("sha256")
        expected_bytes = row.get("bytes")
        if not isinstance(declared, str) or not isinstance(expected_hash, str):
            result["mismatches"].append({"index": index, "kind": "missing_path_or_sha256"})
            continue
        try:
            on_disk = resolve_repo_path(repo, manifest_path, declared)
        except ValueError as error:
            result["mismatches"].append({"index": index, "path": declared, "kind": str(error)})
            continue
        if snapshot_commit:
            relative = on_disk.relative_to(repo).as_posix()
            try:
                content = git_blob(repo, snapshot_commit, relative)
            except subprocess.CalledProcessError:
                result["mismatches"].append({"index": index, "path": declared, "kind": "missing_snapshot_blob"})
                continue
        else:
            if not on_disk.is_file() or on_disk.is_symlink():
                result["mismatches"].append({"index": index, "path": declared, "kind": "missing_or_nonregular"})
                continue
            content = on_disk.read_bytes()
        actual_hash = sha256_bytes(content)
        actual_bytes = len(content)
        result["checked"] += 1
        if actual_hash != expected_hash or (isinstance(expected_bytes, int) and actual_bytes != expected_bytes):
            result["mismatches"].append({
                "index": index,
                "path": declared,
                "kind": "disk_hash_or_size_mismatch",
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
                "expected_bytes": expected_bytes,
                "actual_bytes": actual_bytes,
            })
        if not snapshot_commit and commit and candidate_prefix and row.get("category") == "candidate":
            relative = on_disk.relative_to(repo).as_posix()
            if not relative.startswith(candidate_prefix.rstrip("/") + "/"):
                result["candidate_git_mismatches"].append({"index": index, "path": declared, "kind": "candidate_outside_prefix"})
                continue
            try:
                blob = git_blob(repo, commit, relative)
            except subprocess.CalledProcessError:
                result["candidate_git_mismatches"].append({"index": index, "path": declared, "kind": "missing_git_blob"})
                continue
            result["candidate_git_checked"] += 1
            if sha256_bytes(blob) != actual_hash or len(blob) != actual_bytes:
                result["candidate_git_mismatches"].append({"index": index, "path": declared, "kind": "git_blob_mismatch"})
    result["status"] = "PASS" if not result["mismatches"] and not result["candidate_git_mismatches"] else "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--manifest", action="append", required=True)
    parser.add_argument("--candidate-commit")
    parser.add_argument("--candidate-prefix")
    parser.add_argument("--snapshot-commit")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    reports = [verify_manifest(repo, (repo / value).resolve(), args.candidate_commit, args.candidate_prefix, args.snapshot_commit) for value in args.manifest]
    output = {
        "schema": "lifeos.p3-143.independent-rereview-3.manifest-verification.v1",
        "network": "disabled_by_runner_contract",
        "manifests": reports,
        "error_count": sum(len(item["mismatches"]) + len(item["candidate_git_mismatches"]) for item in reports),
        "status": "PASS" if all(item["status"] == "PASS" for item in reports) else "FAIL",
    }
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "error_count": output["error_count"], "manifest_count": len(reports)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
