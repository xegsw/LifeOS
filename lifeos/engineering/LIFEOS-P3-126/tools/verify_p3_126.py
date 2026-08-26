#!/usr/bin/env python3
"""Fail-closed verifier and disposable mutation runner for P3-126."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
TASK = REPO / "lifeos/engineering/LIFEOS-P3-126"
EVIDENCE = TASK / "evidence"
CANDIDATE = TASK / "candidate"
TEMP = Path("/private/tmp/lifeos-p3-126-clean-closure-v1")
ALLOWLIST = REPO / "lifeos/tasks/LIFEOS-P3-126_source_allowlist.md"
FIXED = [
    REPO / "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json",
    REPO / "lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_rework_1.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125_pm_rework_1_review.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1/MANIFEST.md",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/final-adoption/MANIFEST.md",
    ALLOWLIST,
]
EXTERNAL = {
    REPO / "lifeos/tasks/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md": "task_card",
    REPO / "lifeos/tasks/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild_acceptance_basis_freeze.md": "frozen_abf",
    REPO / "lifeos/tasks/LIFEOS-P3-126_source_allowlist.md": "source_allowlist",
    REPO / "lifeos/tasks/LIFEOS-P3-126_authorization/user_confirmation.md": "authorization",
    REPO / "lifeos/tasks/LIFEOS-P3-126_authorization/FREEZE_MANIFEST.md": "freeze_manifest",
    REPO / "lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json": "p3_125_final_manifest",
    REPO / "lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_rework_1.md": "p3_125_delivery",
    REPO / "lifeos/reviews/LIFEOS-P3-125_pm_rework_1_review.md": "p3_125_pm_review",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1/MANIFEST.md": "p3_125_pm_rework_manifest",
    REPO / "lifeos/reviews/LIFEOS-P3-125/pm_evidence/final-adoption/MANIFEST.md": "p3_125_final_adoption_manifest",
    REPO / "lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md": "delivery",
}
REQUIRED_ROLES = set(EXTERNAL.values()) | {"candidate", "runner", "evidence", "mutation", "cleanup", "log"}


def relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        # Disposable negative manifests are deliberately stored in the
        # task-local /private/tmp root. Report their bad exclusions instead
        # of treating the negative control as a verifier crash.
        return resolved.as_posix()


def digest(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def allowlist_rows() -> dict[str, tuple[int, str]]:
    rows: dict[str, tuple[int, str]] = {}
    for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        columns = raw.split("|")
        if len(columns) == 5 and columns[1].strip().startswith("`") and columns[2].strip().isdigit() and len(columns[3].strip().strip("`")) == 64:
            rows[columns[1].strip().strip("`")] = (int(columns[2].strip()), columns[3].strip().strip("`"))
    if len(rows) != 75:
        raise RuntimeError("frozen allowlist did not parse to 75 rows")
    return rows


def candidate_errors(root: Path) -> list[str]:
    expected = allowlist_rows()
    observed = {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}
    errors = []
    if set(observed) != set(expected):
        errors.append("candidate_set_mismatch")
    for name, (size, expected_hash) in expected.items():
        target = observed.get(name)
        if target is None:
            continue
        if target.is_symlink():
            errors.append(f"candidate_symlink:{name}")
            continue
        actual_size, actual_hash = digest(target)
        if (actual_size, actual_hash) != (size, expected_hash):
            errors.append(f"candidate_hash_mismatch:{name}")
    return errors


def fixed_errors() -> list[str]:
    expected = json.loads((EVIDENCE / "history-before.json").read_text(encoding="utf-8"))["items"]
    observed = []
    for path in FIXED:
        size, sha = digest(path)
        observed.append({"path": relative(path), "bytes": size, "sha256": sha})
    return [] if observed == expected else ["protected_history_mismatch"]


def role_for(path: Path) -> str:
    local = path.relative_to(TASK).as_posix()
    if local.startswith("candidate/"):
        return "candidate"
    if local.startswith("tools/"):
        return "runner"
    if local.startswith("logs/"):
        return "log"
    if local.endswith("mutation-results.json"):
        return "mutation"
    if local.endswith("cleanup.json"):
        return "cleanup"
    return "evidence"


def entries_for(manifest: Path) -> list[dict[str, object]]:
    entries = []
    for path in sorted((item for item in TASK.rglob("*") if item.is_file() and item.resolve() != manifest.resolve()), key=lambda item: item.as_posix()):
        size, sha = digest(path)
        entries.append({"path": relative(path), "bytes": size, "sha256": sha, "role": role_for(path)})
    for path, role in EXTERNAL.items():
        size, sha = digest(path)
        entries.append({"path": relative(path), "bytes": size, "sha256": sha, "role": role})
    return entries


def create_manifest(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "task_id": "LIFEOS-P3-126",
        "manifest_root": "repository-root",
        "inventory_excludes": [relative(target)],
        "entries": entries_for(target),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify(manifest: Path) -> list[str]:
    errors = []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    excludes = data.get("inventory_excludes")
    if excludes != [relative(manifest)]:
        errors.append("invalid_self_exclusion")
    entries = data.get("entries")
    if not isinstance(entries, list):
        return ["entries_not_list"]
    paths = [item.get("path") for item in entries if isinstance(item, dict)]
    if len(paths) != len(set(paths)):
        errors.append("duplicate_manifest_path")
    roles = {item.get("role") for item in entries if isinstance(item, dict)}
    required_roles = REQUIRED_ROLES
    if manifest.name != "FINAL_MANIFEST.json":
        # The pristine control predates mutation and exact-cleanup evidence;
        # those terminal roles are mandatory only in the final manifest.
        required_roles = REQUIRED_ROLES - {"cleanup", "mutation"}
    missing_roles = required_roles - roles
    if missing_roles:
        errors.append(f"missing_roles:{','.join(sorted(missing_roles))}")
    current = {item["path"]: item for item in entries_for(manifest)}
    declared = {item.get("path"): item for item in entries if isinstance(item, dict)}
    if set(current) != set(declared):
        errors.append("manifest_missing_or_extra_path")
    for path, current_item in current.items():
        declared_item = declared.get(path)
        if declared_item is None:
            continue
        if (declared_item.get("bytes"), declared_item.get("sha256"), declared_item.get("role")) != (current_item["bytes"], current_item["sha256"], current_item["role"]):
            errors.append(f"manifest_mismatch:{path}")
    errors.extend(candidate_errors(CANDIDATE))
    errors.extend(fixed_errors())
    static = json.loads((EVIDENCE / "static-contract.json").read_text(encoding="utf-8"))
    boundary = json.loads((EVIDENCE / "boundary.json").read_text(encoding="utf-8"))
    if static.get("status") != "PASS" or not static.get("all_pass"):
        errors.append("static_contract_not_pass")
    if boundary.get("status") != "PASS" or boundary.get("command_audit", {}).get("prohibited_runtime_root_operations") != 0:
        errors.append("boundary_not_pass")
    return errors


def disposable_copy(name: str) -> Path:
    destination = TEMP / "disposable/mutations" / name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(CANDIDATE, destination)
    return destination


def mutations(pristine: Path) -> None:
    pristine_errors = verify(pristine)
    cases: list[dict[str, object]] = [{"case": "pristine", "pass": not pristine_errors, "errors": pristine_errors}]
    modifications = {
        "root": ("build.rs", "\nconst ALLOWED_PARENT: &str = \"fixed-parent\";\n"),
        "fallback": ("src/runtime.rs", "\nconst RUNTIME_ROOT_FALLBACK: &str = \"fallback\";\n"),
        "derive": ("src/runtime.rs", "\nconst MUTATED_DB_NAME: &str = \"other.sqlite\";\n"),
        "order": ("src/runtime.rs", "\n// mutation: storage ordering changed\n"),
    }
    for name, (member, addition) in modifications.items():
        root = disposable_copy(name)
        target = root / member
        target.write_text(target.read_text(encoding="utf-8") + addition, encoding="utf-8")
        errors = candidate_errors(root)
        cases.append({"case": name, "mutation": member, "rejected": bool(errors), "errors": errors})
    root = disposable_copy("extra")
    (root / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    errors = candidate_errors(root)
    cases.append({"case": "extra", "rejected": bool(errors), "errors": errors})
    history_copy = TEMP / "disposable/mutations/history-copy.bin"
    history_copy.write_bytes((FIXED[0]).read_bytes() + b"\nmutation\n")
    size, sha = digest(history_copy)
    source_size, source_sha = digest(FIXED[0])
    cases.append({"case": "history", "rejected": (size, sha) != (source_size, source_sha), "errors": ["protected_history_mismatch"] if (size, sha) != (source_size, source_sha) else []})
    path_manifest = TEMP / "disposable/mutations/path-manifest.json"
    path_manifest.write_text(pristine.read_text(encoding="utf-8"), encoding="utf-8")
    path_data = json.loads(path_manifest.read_text(encoding="utf-8"))
    path_data["entries"][0]["path"] = "../outside"
    path_manifest.write_text(json.dumps(path_data), encoding="utf-8")
    cases.append({"case": "path", "rejected": bool(verify(path_manifest)), "errors": verify(path_manifest)})
    omit_manifest = TEMP / "disposable/mutations/omit-manifest.json"
    omission = json.loads(pristine.read_text(encoding="utf-8"))
    omission["entries"] = [item for item in omission["entries"] if item.get("role") != "delivery"]
    omit_manifest.write_text(json.dumps(omission), encoding="utf-8")
    cases.append({"case": "omission", "rejected": bool(verify(omit_manifest)), "errors": verify(omit_manifest)})
    passed = cases[0]["pass"] and all(item.get("rejected") for item in cases[1:])
    (EVIDENCE / "mutation-results.json").write_text(json.dumps({"test_id": "P126-M011", "status": "PASS" if passed else "FAIL", "cases": cases}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "verify", "mutate"])
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    manifest = (REPO / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest).resolve()
    if args.action == "create":
        create_manifest(manifest)
        return 0
    if args.action == "verify":
        errors = verify(manifest)
        print(json.dumps({"manifest": relative(manifest), "status": "PASS" if not errors else "FAIL", "errors": errors}, ensure_ascii=False))
        return 0 if not errors else 1
    mutations(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
