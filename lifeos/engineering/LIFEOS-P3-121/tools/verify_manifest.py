#!/usr/bin/env python3
"""Build and fail-closed verify the P3-121 self-contained final manifest."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "manifest" / "final-manifest.json"
MUTATION = ROOT / "evidence" / "mutations" / "manifest-mutations.json"
INCLUDE = ("candidate", "tools", "evidence/actual_app", "evidence/static", "evidence/runtime")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for prefix in INCLUDE:
        base = root / prefix
        for path in sorted(base.rglob("*")) if base.exists() else []:
            if path.is_file() and not path.is_symlink():
                entries.append({"path": str(path.relative_to(root)), "sha256": digest(path)})
    return entries


def verify_document(document: dict, base: Path) -> tuple[bool, str]:
    entries = document.get("entries")
    if not isinstance(entries, list) or not entries:
        return False, "entries_missing"
    seen: set[str] = set()
    for entry in entries:
        path_text = entry.get("path") if isinstance(entry, dict) else None
        expected = entry.get("sha256") if isinstance(entry, dict) else None
        if not isinstance(path_text, str) or not isinstance(expected, str) or path_text in seen:
            return False, "entry_shape_or_duplicate"
        seen.add(path_text)
        path = base / path_text
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            return False, "entry_missing_or_hash_mismatch"
    actual = inventory(base)
    expected_paths = [entry["path"] for entry in entries]
    if [entry["path"] for entry in actual] != expected_paths:
        return False, "inventory_path_mismatch"
    if any(actual[index]["sha256"] != entries[index]["sha256"] for index in range(len(actual))):
        return False, "inventory_hash_mismatch"
    return True, "ok"


def main() -> int:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    entries = inventory(ROOT)
    document = {
        "task": "LIFEOS-P3-121",
        "kind": "self-check final manifest; not PM acceptance",
        "entries": entries,
        "entry_count": len(entries),
        "tree_sha256": hashlib.sha256("\n".join(f"{entry['path']}:{entry['sha256']}" for entry in entries).encode()).hexdigest(),
    }
    ok, reason = verify_document(document, ROOT)
    if not ok:
        raise SystemExit(f"manifest source validation failed: {reason}")
    MANIFEST.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # A pristine disposable copy must pass before precise mutations can prove rejection.
    MUTATION.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="p3-121-manifest-", dir=MUTATION.parent) as scratch:
        disposable = Path(scratch) / "candidate-root"
        disposable.mkdir()
        # Copy only the explicit inventory roots. Copying ROOT would recursively include this
        # task-local scratch directory and make a control invalid by construction.
        for prefix in INCLUDE:
            source = ROOT / prefix
            if source.exists():
                shutil.copytree(source, disposable / prefix, ignore=shutil.ignore_patterns("__pycache__"))
        copied_manifest = disposable / MANIFEST.relative_to(ROOT)
        copied_manifest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(MANIFEST, copied_manifest)
        pristine = json.loads(copied_manifest.read_text(encoding="utf-8"))
        control_ok, control_reason = verify_document(pristine, disposable)
        missing = json.loads(json.dumps(pristine))
        missing["entries"].pop()
        missing_ok, missing_reason = verify_document(missing, disposable)
        changed_file = disposable / "candidate" / "ui" / "app.js"
        original = changed_file.read_bytes()
        changed_file.write_bytes(original.replace(b"Global AI", b"Global ZI", 1))
        changed_ok, changed_reason = verify_document(pristine, disposable)
        changed_file.write_bytes(original)
        extra = disposable / "candidate" / "unexpected.txt"
        extra.write_text("P3-121 disposable mutation only\n", encoding="utf-8")
        extra_ok, extra_reason = verify_document(pristine, disposable)
    results = {
        "task": "LIFEOS-P3-121",
        "control": {"result": "PASS" if control_ok else "FAIL", "reason": control_reason},
        "missing_manifest_row": {"result": "PASS" if not missing_ok else "FAIL", "reason": missing_reason},
        "candidate_byte_change": {"result": "PASS" if not changed_ok else "FAIL", "reason": changed_reason},
        "unexpected_candidate_file": {"result": "PASS" if not extra_ok else "FAIL", "reason": extra_reason},
        "disposable_cleanup": "PASS",
    }
    MUTATION.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed = all(value.get("result") == "PASS" for key, value in results.items() if isinstance(value, dict))
    print(f"P3-121-MANIFEST: {'PASS' if passed else 'FAIL'} ({len(entries)} entries)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
