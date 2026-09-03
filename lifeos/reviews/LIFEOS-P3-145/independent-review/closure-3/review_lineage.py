#!/usr/bin/env python3
"""Read-only immutable-blob lineage audit for Closure-3."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

P145_COMMIT = "579914d06923db65db8c3b421b2da663a1950354"
P144_BASE = "lifeos/engineering/LIFEOS-P3-144/candidate/"
P145_BASE = "lifeos/engineering/LIFEOS-P3-145/candidate/"


def blob(commit: str, path: str) -> Optional[bytes]:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text(commit: str, path: str) -> str:
    data = blob(commit, path)
    if data is None:
        raise RuntimeError(f"missing immutable blob: {path}")
    return data.decode("utf-8")


def ipc_values(source: str) -> list[str]:
    match = re.search(r"const IPC: \[&str; 20\] = \[(.*?)\];", source, re.S)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def table_names(source: str) -> set[str]:
    return set(re.findall(r"CREATE TABLE IF NOT EXISTS ([a-z_]+)", source))


def main() -> None:
    p144_manifest = json.loads(Path(sys.argv[1]).read_text())
    p145_manifest = json.loads(Path(sys.argv[2]).read_text())
    p144_commit = sys.argv[3]
    p144 = {
        item["path"].removeprefix("candidate/"): item["sha256"]
        for item in p144_manifest["files"]
        if item["path"].startswith("candidate/")
    }
    p145 = {
        item["path"].removeprefix("candidate/"): item["sha256"]
        for item in p145_manifest["files"]
        if item["path"].startswith("candidate/")
    }
    entries = []
    for relative, expected in sorted(p144.items()):
        old = blob(p144_commit, P144_BASE + relative)
        new = blob(P145_COMMIT, P145_BASE + relative)
        old_actual = sha(old) if old is not None else None
        new_actual = sha(new) if new is not None else None
        status = "missing" if new is None else ("unchanged" if old_actual == new_actual else "modified")
        entries.append(
            {
                "path": relative,
                "p144_manifest_sha256": expected,
                "p144_immutable_sha256": old_actual,
                "p145_immutable_sha256": new_actual,
                "status": status,
                "p144_hash_matches_manifest": old_actual == expected,
                "p145_hash_matches_manifest": new_actual == p145.get(relative),
            }
        )
    old_runtime, new_runtime = text(p144_commit, P144_BASE + "src/runtime.rs"), text(P145_COMMIT, P145_BASE + "src/runtime.rs")
    old_deepseek, new_deepseek = text(p144_commit, P144_BASE + "src/deepseek.rs"), text(P145_COMMIT, P145_BASE + "src/deepseek.rs")
    old_tables, new_tables = table_names(old_runtime), table_names(new_runtime)
    semantic = {
        "ipc_exact_20_and_order_preserved": len(ipc_values(old_runtime)) == 20
        and ipc_values(old_runtime) == ipc_values(new_runtime),
        "all_p144_ui_assets_present": all(blob(P145_COMMIT, P145_BASE + path) is not None for path in p144 if path.startswith("ui/")),
        "all_p144_schema_tables_retained": old_tables.issubset(new_tables),
        "deepseek_authority_literal_retained": "https://api.deepseek.com" in old_deepseek and "https://api.deepseek.com" in new_deepseek,
        "p145_retains_credential_module": blob(P145_COMMIT, P145_BASE + "src/secure_credentials.rs") is not None,
        "p145_retains_runtime_memory_today_modules": all(
            blob(P145_COMMIT, P145_BASE + path) is not None
            for path in ["src/runtime/memory_context.rs", "src/runtime/today_intelligence.rs"]
        ),
    }
    result = {
        "schema_version": "lifeos.p3-145.closure-3.lineage.v1",
        "p144_commit": p144_commit,
        "p145_commit": P145_COMMIT,
        "baseline_entries": len(entries),
        "unchanged": sum(item["status"] == "unchanged" for item in entries),
        "modified": sum(item["status"] == "modified" for item in entries),
        "missing": sum(item["status"] == "missing" for item in entries),
        "p144_manifest_mismatches": [item["path"] for item in entries if not item["p144_hash_matches_manifest"]],
        "p145_manifest_mismatches": [item["path"] for item in entries if item["p145_immutable_sha256"] is not None and not item["p145_hash_matches_manifest"]],
        "semantic": semantic,
        "pass": not any(item["status"] == "missing" for item in entries)
        and not any(not item["p144_hash_matches_manifest"] for item in entries)
        and all(semantic.values()),
        "entries": entries,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
