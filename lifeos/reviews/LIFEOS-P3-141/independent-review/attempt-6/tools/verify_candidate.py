#!/usr/bin/env python3
"""Attempt-6 read-only lineage and manifest verifier.

This does not invoke candidate tests.  It independently recomputes the fixed
input hashes, candidate tree digest, exact IPC declaration and the engineering
Final Manifest file claims.  Output is a non-content JSON evidence record.
"""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree(root: Path):
    rows = []
    framed = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        rows.append((relative, hashlib.sha256(data).hexdigest()))
        encoded = relative.encode("utf-8")
        framed.update(len(encoded).to_bytes(8, "big"))
        framed.update(encoded)
        framed.update(len(data).to_bytes(8, "big"))
        framed.update(data)
    return rows, framed.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pm-root", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--p3-140-baseline", required=True, type=Path)
    parser.add_argument("--engineering-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    inventory = json.loads((args.pm_root / "lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json").read_text())
    fixed = []
    for item in inventory["entries"]:
        path = Path(item["path"])
        if not path.is_absolute():
            path = args.pm_root / path
        actual = digest(path)
        actual_bytes = path.stat().st_size
        fixed.append({"role": item["role"], "bytes_expected": item["bytes"], "bytes_actual": actual_bytes,
                      "sha256_expected": item["sha256"], "sha256_actual": actual,
                      "status": "PASS" if actual == item["sha256"] and actual_bytes == item["bytes"] else "FAIL"})

    candidate_rows, candidate_tree = tree(args.candidate)
    baseline_rows, baseline_tree = tree(args.p3_140_baseline)
    ipc_file = args.candidate / "src/runtime.rs"
    source = ipc_file.read_text()
    marker = "const IPC: [&str; 20] = ["
    ipc_fragment = source[source.index(marker):source.index("];", source.index(marker)) + 2]
    ipc = [entry.strip(' "') for entry in ipc_fragment.split("[")[2].split("]")[0].split(",")]

    manifest_path = args.engineering_root / "evidence/FINAL_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    problems = []
    for relative, expected in manifest["files"].items():
        target = args.engineering_root / relative
        if not target.is_file() or digest(target) != expected:
            problems.append(relative)
    result = {
        "schema": "lifeos.p3-141.attempt6.candidate-verification.v1",
        "fixed_inputs": fixed,
        "fixed_input_pass_count": sum(item["status"] == "PASS" for item in fixed),
        "candidate": {"path": str(args.candidate), "file_count": len(candidate_rows), "tree_sha256": candidate_tree,
                      "commit_bound": "e4eeb73395151955c0b833965979be1806406ce5"},
        "p3_140_baseline": {"path": str(args.p3_140_baseline), "file_count": len(baseline_rows), "tree_sha256": baseline_tree,
                             "expected_file_count": inventory["tree_lineage"]["p3_140_candidate_file_count"],
                             "expected_tree_sha256": inventory["tree_lineage"]["p3_140_candidate_tree_sha256"],
                             "status": "PASS" if len(baseline_rows) == inventory["tree_lineage"]["p3_140_candidate_file_count"] and baseline_tree == inventory["tree_lineage"]["p3_140_candidate_tree_sha256"] else "FAIL"},
        "ipc": {"count": len(ipc), "names": ipc, "status": "PASS" if len(ipc) == 20 else "FAIL"},
        "engineering_final_manifest": {"path": str(manifest_path), "declared_file_count": manifest["file_count_excluding_manifest"],
                                        "verified_file_count": len(manifest["files"]), "mismatches": problems,
                                        "self_reference": manifest.get("self_reference"), "status": "PASS" if not problems and manifest.get("self_reference") == "excluded: evidence/FINAL_MANIFEST.json" else "FAIL"},
    }
    result["status"] = "PASS" if result["fixed_input_pass_count"] == 12 and len(candidate_rows) == 79 and result["p3_140_baseline"]["status"] == "PASS" and result["ipc"]["status"] == "PASS" and result["engineering_final_manifest"]["status"] == "PASS" else "FAIL"
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(result["status"])
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
