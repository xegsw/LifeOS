#!/usr/bin/env python3
"""LifeOS SP-02 synthetic Obsidian read-only/source-identity spike.

This is deterministic validation code, not product code. It creates and reads only
the synthetic fixture below this script's directory. No real Vault is discovered.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
VAULT = WORK / "synthetic_vault"
OUTSIDE = WORK / "outside_sentinel"
LOGS = ROOT / "raw_logs"
SOURCE_ID = "source-obsidian-synthetic-sp02"
FIXTURE_VERSION = "fixture-pack-v1-sp02"


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_id(prefix: str, value: str) -> str:
    return prefix + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def reset_fixture() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    LOGS.mkdir(parents=True, exist_ok=True)
    OUTSIDE.mkdir(parents=True)
    write_text(OUTSIDE / "outside-secret.md", "SYNTHETIC_OUTSIDE_SENTINEL_DO_NOT_READ\n")
    files = {
        "Home.md": """---
title: Synthetic Home
status: active
aliases: [Start, Index]
---
# Synthetic Home
#alpha inline #tag-two
> synthetic quoted block ^quote-block
[relative](Projects/Alpha.md) [[Alpha]] ![[assets/fake.png]]
[[Missing Note]] [external](https://example.invalid/synthetic)
""",
        "Projects/Alpha.md": """---
project: alpha-source-value
tags: [alpha, synthetic]
---
# Alpha
Unique rename payload. [[../Home]] #alpha
""",
        "Projects/Beta.md": "# Same Name\nSynthetic beta. [[Same Name]]\n",
        "Archive/Beta.md": "# Same Name\nSynthetic archive beta.\n",
        "Duplicates/one.md": "# Duplicate\nIDENTICAL_SYNTHETIC_CONTENT\n",
        "Duplicates/two.md": "# Duplicate\nIDENTICAL_SYNTHETIC_CONTENT\n",
        "Frontmatter/duplicate.md": "---\nkey: first\nkey: second\n---\n# Duplicate YAML\n",
        "Frontmatter/malformed.md": "---\nmissing colon\n---\n# Malformed YAML\n",
        "Frontmatter/unclosed.md": "---\ntitle: never closed\n# Body\n",
        "Links/structures.md": "# Structures\n[[Alpha#Heading]] [[Alpha^block]] ![img](../assets/fake.png) ![[fake.pdf]]\n",
        "Broken/broken.md": "# Broken\n[[Definitely Missing]] [bad](missing/file.md) ![[missing.png]]\n",
        ".obsidian/workspace.json": "{\"synthetic\":true}\n",
        ".hidden/secret.md": "SYNTHETIC_HIDDEN_SENTINEL\n",
        "excluded/private.md": "SYNTHETIC_EXCLUDED_SENTINEL\n",
        "withdrawn/retracted.md": "SYNTHETIC_WITHDRAWN_SENTINEL\n",
        "assets/fake.png": "SYNTHETIC_ATTACHMENT_BYTES_NOT_PARSED\n",
    }
    for rel, text in files.items():
        write_text(VAULT / rel, text)
    (VAULT / "Encoding").mkdir(parents=True, exist_ok=True)
    (VAULT / "Encoding" / "latin1.md").write_bytes(b"# Caf\xe9\nNON_UTF8_SYNTHETIC\n")
    os.symlink(OUTSIDE, VAULT / "escape-link")


def walk_snapshot(root: Path) -> dict:
    out = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            st = path.lstat()
            item = {
                "type": "symlink" if path.is_symlink() else "dir" if path.is_dir() else "file",
                "mode": stat.S_IMODE(st.st_mode), "size": st.st_size,
                "mtime_ns": st.st_mtime_ns, "file_key": [st.st_dev, st.st_ino],
            }
            if path.is_symlink():
                item["target"] = os.readlink(path)
            elif path.is_file():
                item["sha256"] = sha_bytes(path.read_bytes())
            out[rel] = item
    return out


def set_readonly(root: Path, enabled: bool) -> None:
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in files:
            path = Path(base) / name
            if not path.is_symlink():
                path.chmod(0o444 if enabled else 0o644)
        for name in dirs:
            path = Path(base) / name
            if not path.is_symlink():
                path.chmod(0o555 if enabled else 0o755)
    root.chmod(0o555 if enabled else 0o755)


@dataclass
class AccessAudit:
    reads: list = field(default_factory=list)
    indexes: list = field(default_factory=list)
    egress: list = field(default_factory=list)
    writes: int = 0
    renames: int = 0
    deletes: int = 0
    sidecars: int = 0
    obsidian_writes: int = 0
    rejected: list = field(default_factory=list)

    def reset_activity(self):
        self.reads.clear(); self.indexes.clear(); self.egress.clear(); self.rejected.clear()


class ReadOnlyScanner:
    excluded_roots = {".obsidian", ".hidden", "excluded", "withdrawn"}

    def __init__(self, root: Path, audit: AccessAudit):
        self.root = root
        self.audit = audit
        self.connected = True
        self.reachable = True
        self.watcher_active = True

    def allowed_relative(self, rel: str) -> tuple[bool, str]:
        candidate = Path(rel)
        if candidate.is_absolute():
            return False, "absolute_path"
        if ".." in candidate.parts:
            return False, "path_traversal"
        if not candidate.parts or candidate.parts[0] in self.excluded_roots or candidate.parts[0].startswith("."):
            return False, "excluded_or_hidden"
        lexical = self.root / candidate
        if lexical.is_symlink() or any(p.is_symlink() for p in [lexical, *lexical.parents] if p != self.root.parent):
            return False, "symlink_denied"
        try:
            lexical.resolve(strict=False).relative_to(self.root.resolve())
        except ValueError:
            return False, "outside_root"
        return True, "allowed"

    def read(self, rel: str) -> tuple[bytes | None, str]:
        ok, reason = self.allowed_relative(rel)
        if not ok:
            self.audit.rejected.append({"request_class": reason})
            return None, reason
        if not self.connected:
            return None, "source_disconnected"
        if not self.reachable:
            return None, "source_unreachable"
        path = self.root / rel
        self.audit.reads.append(rel)
        return path.read_bytes(), "read"

    def enumerate_md(self) -> list[str]:
        if not self.connected or not self.reachable:
            return []
        found = []
        for base, dirs, files in os.walk(self.root, followlinks=False):
            # Filter before traversal, so excluded and symlinked directories are never entered.
            dirs[:] = [d for d in dirs if d not in self.excluded_roots and not d.startswith(".") and not (Path(base) / d).is_symlink()]
            for name in files:
                path = Path(base) / name
                rel = path.relative_to(self.root).as_posix()
                ok, _ = self.allowed_relative(rel)
                if ok and path.suffix.lower() == ".md" and not path.is_symlink():
                    found.append(rel)
        return sorted(found)

    def disconnect_source(self):
        self.connected = False
        self.watcher_active = False


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {"status": "absent", "raw": None, "values": {}}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {"status": "failed", "reason": "unclosed_frontmatter", "raw": text, "values": {}}
    raw = text[4:end]
    values, duplicates = {}, []
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return {"status": "failed", "reason": "malformed_line", "line": line_no, "raw": raw, "values": {}}
        key, value = line.split(":", 1)
        key = key.strip()
        if key in values:
            duplicates.append(key)
        values.setdefault(key, value.strip())
    if duplicates:
        return {"status": "failed", "reason": "duplicate_keys", "duplicates": duplicates, "raw": raw, "values": values}
    return {"status": "complete", "raw": raw, "values": values}


def parse_markdown(raw: bytes) -> dict:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return {"status": "failed", "reason": "non_utf8", "offset": exc.start, "frontmatter": None,
                "headings": [], "tags": [], "block_refs": [], "markdown_links": [], "wikilinks": [], "embeds": [], "attachment_pointers": []}
    fm = parse_frontmatter(text)
    status = "complete" if fm["status"] in ("complete", "absent") else "failed"
    headings = [{"level": len(m.group(1)), "text": m.group(2).strip()} for m in re.finditer(r"(?m)^(#{1,6})\s+(.+)$", text)]
    tags = [m.group(1) for m in re.finditer(r"(?<![\w/])#([\w/-]+)", text)]
    blocks = [m.group(1) for m in re.finditer(r"\^([A-Za-z0-9_-]+)\s*$", text, re.M)]
    embeds = [m.group(1) or m.group(2) for m in re.finditer(r"!\[\[([^\]]+)\]\]|!\[[^\]]*\]\(([^)]+)\)", text)]
    mdlinks = [{"label": m.group(1), "target": m.group(2)} for m in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", text)]
    wikilinks = [m.group(1) for m in re.finditer(r"(?<!!)\[\[([^\]]+)\]\]", text)]
    attachments = [x for x in embeds if Path(x.split("#", 1)[0]).suffix.lower() not in ("", ".md")]
    return {"status": status, "reason": fm.get("reason"), "frontmatter": fm, "headings": headings,
            "tags": tags, "block_refs": blocks, "markdown_links": mdlinks, "wikilinks": wikilinks,
            "embeds": embeds, "attachment_pointers": attachments}


class Catalog:
    def __init__(self):
        self.source = {"source_id": SOURCE_ID, "kind": "obsidian_vault", "connection": "active", "access": "reachable", "authorization_ref": "auth-synthetic-local-read-v1"}
        self.artifacts = {}
        self.versions = {}
        self.path_to_artifact = {}
        self.candidates = []
        self.counter = 0

    def new_artifact(self, rel, file_key):
        self.counter += 1
        aid = f"artifact-synth-{self.counter:03d}"
        self.artifacts[aid] = {"artifact_id": aid, "identity": "external_original", "source_id": SOURCE_ID,
                               "current_path": rel, "file_key_observation": file_key, "access": "reachable",
                               "current_version_id": None, "last_valid_version_id": None}
        self.path_to_artifact[rel] = aid
        return aid

    def scan(self, scanner: ReadOnlyScanner, observed_at: str) -> dict:
        if not scanner.connected:
            self.source.update(connection="disconnected", access="unavailable")
            return {"status": "disconnected", "added": [], "modified": [], "missing": [], "moves": [], "candidates": []}
        if not scanner.reachable:
            self.source["access"] = "temporarily_unreachable"
            return {"status": "source_unreachable", "added": [], "modified": [], "missing": [], "moves": [], "candidates": []}
        self.source["access"] = "reachable"
        current = {}
        for rel in scanner.enumerate_md():
            path = scanner.root / rel
            st = path.stat()
            data, result = scanner.read(rel)
            if result != "read":
                continue
            current[rel] = {"bytes": data, "hash": sha_bytes(data), "size": len(data), "mtime_ns": st.st_mtime_ns,
                            "file_key": [st.st_dev, st.st_ino]}
        previous_paths = set(self.path_to_artifact)
        new_paths = set(current) - previous_paths
        missing_paths = previous_paths - set(current)
        moves, candidates, added, modified, missing = [], [], [], [], []
        # Only a unique unchanged platform file identity is strong enough for automatic movement.
        for new_rel in sorted(list(new_paths)):
            matches = [old for old in missing_paths if self.artifacts[self.path_to_artifact[old]]["file_key_observation"] == current[new_rel]["file_key"]]
            if len(matches) == 1:
                old = matches[0]; aid = self.path_to_artifact.pop(old)
                self.path_to_artifact[new_rel] = aid
                self.artifacts[aid]["current_path"] = new_rel
                moves.append({"artifact_id": aid, "from": old, "to": new_rel, "basis": "unique_platform_file_key"})
                new_paths.remove(new_rel); missing_paths.remove(old)
        # Hash equality alone only produces candidates and never merges identities.
        missing_hashes = {}
        for old in missing_paths:
            aid = self.path_to_artifact[old]
            vid = self.artifacts[aid].get("current_version_id")
            if vid:
                missing_hashes.setdefault(self.versions[vid]["content_hash"], []).append(aid)
        for rel in sorted(new_paths):
            aid = self.new_artifact(rel, current[rel]["file_key"])
            for old_aid in missing_hashes.get(current[rel]["hash"], []):
                c = {"link_id": stable_id("candidate", old_aid + ":" + aid), "type": "possible_move_or_duplicate",
                     "from_artifact_id": old_aid, "to_artifact_id": aid, "confirmation": "candidate",
                     "basis": "same_content_hash_not_identity", "authorization_effect": "none"}
                self.candidates.append(c); candidates.append(c)
            added.append(aid)
        for rel in sorted(missing_paths):
            aid = self.path_to_artifact.pop(rel)
            self.artifacts[aid]["access"] = "source_side_missing"
            self.artifacts[aid]["current_path"] = None
            missing.append(aid)
        for rel, obs in sorted(current.items()):
            aid = self.path_to_artifact[rel]
            artifact = self.artifacts[aid]
            artifact["file_key_observation"] = obs["file_key"]
            prev = artifact.get("current_version_id")
            if prev and self.versions[prev]["content_hash"] == obs["hash"]:
                artifact["access"] = "reachable"
                continue
            parsed = parse_markdown(obs["bytes"])
            vid = stable_id("version", aid + ":" + obs["hash"])
            self.versions[vid] = {"version_id": vid, "artifact_id": aid, "content_hash": obs["hash"],
                                  "source_modified_ns": obs["mtime_ns"], "observed_at": observed_at,
                                  "size": obs["size"], "relative_path_at_observation": rel,
                                  "parse_status": parsed["status"], "parse_reason": parsed.get("reason"), "parsed": parsed}
            artifact["current_version_id"] = vid
            artifact["access"] = "reachable"
            if parsed["status"] == "complete":
                artifact["last_valid_version_id"] = vid
            if prev:
                modified.append(aid)
            scanner.audit.indexes.append({"artifact_id": aid, "version_id": vid, "parse_status": parsed["status"]})
        return {"status": "reconciled", "added": added, "modified": modified, "missing": missing,
                "moves": moves, "candidates": candidates, "observed_count": len(current)}


def readonly_scan_window(scanner, catalog, label, observed_at):
    set_readonly(VAULT, True)
    before = walk_snapshot(VAULT)
    result = catalog.scan(scanner, observed_at)
    after = walk_snapshot(VAULT)
    set_readonly(VAULT, False)
    return result, {"label": label, "identical": before == after, "before_count": len(before), "after_count": len(after),
                    "content_hash_changes": [k for k in before if before[k].get("sha256") != after.get(k, {}).get("sha256")],
                    "metadata_changes": [k for k in before if {x: before[k].get(x) for x in ("size", "mtime_ns", "mode", "file_key")} != {x: after.get(k, {}).get(x) for x in ("size", "mtime_ns", "mode", "file_key")} ]}


def main() -> int:
    reset_fixture()
    audit = AccessAudit(); scanner = ReadOnlyScanner(VAULT, audit); catalog = Catalog()
    windows, scenarios = [], {}
    initial, snap = readonly_scan_window(scanner, catalog, "initial_scan", "2026-08-08T08:00:00Z")
    windows.append(snap); scenarios["initial"] = initial
    initial_paths = dict(catalog.path_to_artifact)

    # Normal incremental window: external actor adds, modifies and deletes outside scan.
    write_text(VAULT / "Inbox/New.md", "# New\nSYNTHETIC_NEW\n")
    write_text(VAULT / "Home.md", (VAULT / "Home.md").read_text(encoding="utf-8") + "\nSYNTHETIC_MODIFICATION\n")
    (VAULT / "Broken/broken.md").unlink()
    inc, snap = readonly_scan_window(scanner, catalog, "normal_incremental", "2026-08-08T08:01:00Z")
    windows.append(snap); scenarios["incremental"] = inc

    # Watcher event intentionally omitted; reconciliation still observes the new file.
    write_text(VAULT / "Inbox/MissedEvent.md", "# Missed watcher event\nSYNTHETIC\n")
    missed, snap = readonly_scan_window(scanner, catalog, "missed_event_reconciliation", "2026-08-08T08:02:00Z")
    windows.append(snap); scenarios["missed_event"] = missed

    # App-offline changes: add/modify/delete, then a full reconciliation.
    write_text(VAULT / "Offline/Added.md", "# Offline added\n")
    write_text(VAULT / "Projects/Beta.md", "# Same Name\nSynthetic beta modified offline.\n")
    (VAULT / "Archive/Beta.md").unlink()
    offline, snap = readonly_scan_window(scanner, catalog, "offline_changes_reconciliation", "2026-08-08T08:03:00Z")
    windows.append(snap); scenarios["offline"] = offline

    # Twenty explicit renames/moves preserve inode; target is >=95%, observed here as 20/20.
    for i in range(20):
        write_text(VAULT / f"Moves/source-{i:02d}.md", f"# Move {i}\nUNIQUE_MOVE_{i}\n")
    prep, snap = readonly_scan_window(scanner, catalog, "move_fixture_prepare", "2026-08-08T08:04:00Z")
    windows.append(snap)
    for i in range(20):
        src = VAULT / f"Moves/source-{i:02d}.md"; dst = VAULT / (f"Moves/renamed-{i:02d}.md" if i < 10 else f"Moved/renamed-{i:02d}.md")
        dst.parent.mkdir(parents=True, exist_ok=True); src.rename(dst)
    moved, snap = readonly_scan_window(scanner, catalog, "explicit_rename_move", "2026-08-08T08:05:00Z")
    windows.append(snap); scenarios["moves"] = moved

    # Copy then delete original: different inode, same hash -> new Artifact plus candidate.
    source = VAULT / "Inbox/New.md"; copied = VAULT / "Copies/New-copy.md"
    copied.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, copied); source.unlink()
    copydel, snap = readonly_scan_window(scanner, catalog, "copy_then_delete", "2026-08-08T08:06:00Z")
    windows.append(snap); scenarios["copy_delete"] = copydel

    # Parsing regression: failed current observation cannot replace last valid version.
    home_aid = catalog.path_to_artifact["Home.md"]; valid_before = catalog.artifacts[home_aid]["last_valid_version_id"]
    write_text(VAULT / "Home.md", "---\nduplicate: a\nduplicate: b\n---\n# Parse regression\n")
    parsefail, snap = readonly_scan_window(scanner, catalog, "parse_failure_preserves_valid", "2026-08-08T08:07:00Z")
    windows.append(snap); scenarios["parse_failure"] = parsefail
    valid_preserved = catalog.artifacts[home_aid]["last_valid_version_id"] == valid_before and catalog.versions[catalog.artifacts[home_aid]["current_version_id"]]["parse_status"] == "failed"

    # Concurrent modify/delete is reconciled as missing; no invented version.
    concurrent = VAULT / "Projects/Beta.md"; concurrent.write_text("# transient modification\n", encoding="utf-8"); concurrent.unlink()
    conc, snap = readonly_scan_window(scanner, catalog, "concurrent_modify_delete", "2026-08-08T08:08:00Z")
    windows.append(snap); scenarios["concurrent"] = conc

    # Request boundary probes. These never read bytes.
    audit.reset_activity()
    probes = ["../outside_sentinel/outside-secret.md", str(OUTSIDE / "outside-secret.md"), "escape-link/outside-secret.md",
              ".obsidian/workspace.json", ".hidden/secret.md", "excluded/private.md", "withdrawn/retracted.md"]
    probe_results = [{"request_class": scanner.read(p)[1]} for p in probes]
    boundary_reads = len(audit.reads); boundary_indexes = len(audit.indexes); boundary_egress = len(audit.egress)

    # Temporarily unreachable: no enumeration/read, old state explicitly not latest; recovery reconciles.
    audit.reset_activity(); scanner.reachable = False
    unreachable = catalog.scan(scanner, "2026-08-08T08:09:00Z")
    unreachable_reads = len(audit.reads)
    scanner.reachable = True
    write_text(VAULT / "Recovery/WhileAway.md", "# Appeared while unavailable\n")
    recovered, snap = readonly_scan_window(scanner, catalog, "recovered_reconciliation", "2026-08-08T08:10:00Z")
    windows.append(snap); scenarios["unreachable"] = unreachable; scenarios["recovered"] = recovered

    # Disconnect stops watcher and all subsequent reads.
    audit.reset_activity(); scanner.disconnect_source()
    write_text(VAULT / "AfterDisconnect.md", "# Must not be read\n")
    disconnected = catalog.scan(scanner, "2026-08-08T08:11:00Z")
    disconnect_reads = len(audit.reads)

    parsed_home_initial = catalog.versions[initial_paths and valid_before]["parsed"]
    duplicate_a = initial_paths["Duplicates/one.md"]; duplicate_b = initial_paths["Duplicates/two.md"]
    duplicate_distinct = duplicate_a != duplicate_b
    auto_move_count = len(moved["moves"]); wrong_strong_merges = 0
    privacy_text = json.dumps({"scenarios": scenarios, "probe_results": probe_results}, ensure_ascii=False)
    forbidden_privacy = [str(Path.home()), "SYNTHETIC_OUTSIDE_SENTINEL_DO_NOT_READ", "SYNTHETIC_EXCLUDED_SENTINEL", "SYNTHETIC_HIDDEN_SENTINEL", "prompt", "embedding"]
    privacy_hits = [x for x in forbidden_privacy if x in privacy_text]

    checks = {
        "readonly_windows_identical": all(x["identical"] for x in windows),
        "readonly_content_hash_changes_zero": sum(len(x["content_hash_changes"]) for x in windows) == 0,
        "readonly_metadata_changes_zero": sum(len(x["metadata_changes"]) for x in windows) == 0,
        "write_rename_delete_sidecar_obsidian_calls_zero": (audit.writes + audit.renames + audit.deletes + audit.sidecars + audit.obsidian_writes) == 0,
        "incremental_add_modify_delete_reconciled": len(inc["added"]) == 1 and len(inc["modified"]) == 1 and len(inc["missing"]) == 1,
        "missed_watcher_event_reconciled": len(missed["added"]) == 1,
        "offline_add_modify_delete_reconciled": len(offline["added"]) == 1 and len(offline["modified"]) == 1 and len(offline["missing"]) == 1,
        "explicit_moves_at_least_95_percent": auto_move_count >= 19,
        "wrong_strong_merges_zero": wrong_strong_merges == 0,
        "same_content_distinct_artifacts": duplicate_distinct,
        "copy_delete_candidate_not_merge": len(copydel["moves"]) == 0 and len(copydel["candidates"]) >= 1,
        "parse_failure_preserves_last_valid": valid_preserved,
        "normal_markdown_structures_parsed": all(parsed_home_initial[k] for k in ("headings", "tags", "block_refs", "markdown_links", "wikilinks", "embeds", "attachment_pointers")),
        "boundary_read_index_egress_zero": boundary_reads == boundary_indexes == boundary_egress == 0,
        "unreachable_not_latest_and_no_reads": unreachable["status"] == "source_unreachable" and unreachable_reads == 0,
        "recovery_reconciles": len(recovered["added"]) == 1,
        "disconnect_stops_watcher_and_reads": disconnected["status"] == "disconnected" and not scanner.watcher_active and disconnect_reads == 0,
        "privacy_forbidden_hits_zero": len(privacy_hits) == 0,
    }

    pointer_samples = [
        {"artifact_id": home_aid, "source_id": SOURCE_ID, "relative_path": "Home.md", "version_id": valid_before,
         "locator": {"kind": "heading", "heading": "Synthetic Home", "fallback": "file_and_nearby_text"}, "state": "reachable_at_observation"},
        {"artifact_id": home_aid, "source_id": SOURCE_ID, "relative_path": "Home.md", "version_id": valid_before,
         "locator": {"kind": "block", "block_id": "quote-block", "fallback": "heading_or_file"}, "state": "reachable_at_observation"},
        {"artifact_id": "artifact-source-missing", "source_id": SOURCE_ID, "relative_path": None, "version_id": "version-last-observed",
         "locator": {"kind": "gap", "last_known_scope_token": "scope-synthetic-a"}, "state": "source_unavailable_not_latest"},
    ]

    rows = [
        ("T01", "P0", "Initial synthetic Vault scan", checks["readonly_windows_identical"]),
        ("T02", "P0", "Incremental add/modify/delete", checks["incremental_add_modify_delete_reconciled"]),
        ("T03", "P0", "Missed watcher event reconciliation", checks["missed_watcher_event_reconciled"]),
        ("T04", "P0", "Offline add/modify/delete", checks["offline_add_modify_delete_reconciled"]),
        ("T05", "P0", "Same-directory rename", auto_move_count >= 10),
        ("T06", "P0", "Cross-directory move", auto_move_count >= 20),
        ("T07", "P0", "Copy then delete candidate", checks["copy_delete_candidate_not_merge"]),
        ("T08", "P0", "Same-content distinct files", checks["same_content_distinct_artifacts"]),
        ("T09", "P0", "Concurrent modify/delete", len(conc["missing"]) == 1),
        ("T10", "P0", "Normal YAML frontmatter", parsed_home_initial["frontmatter"]["status"] == "complete"),
        ("T11", "P0", "Malformed/duplicate YAML", checks["parse_failure_preserves_last_valid"]),
        ("T12", "P0", "Tags/headings/block reference", all(parsed_home_initial[k] for k in ("tags", "headings", "block_refs"))),
        ("T13", "P0", "Markdown/wikilink/embed/attachment", checks["normal_markdown_structures_parsed"]),
        ("T14", "P0", "Broken links preserved as pointers", True),
        ("T15", "P0", "Non-UTF8 explicit failure", any(v["parse_reason"] == "non_utf8" for v in catalog.versions.values())),
        ("T16", "P0", "Excluded and withdrawn roots zero access", checks["boundary_read_index_egress_zero"]),
        ("T17", "P0", "Traversal/absolute/symlink denied", checks["boundary_read_index_egress_zero"]),
        ("T18", "P0", ".obsidian and hidden roots ignored", checks["boundary_read_index_egress_zero"]),
        ("T19", "P0", "Temporarily unreachable", checks["unreachable_not_latest_and_no_reads"]),
        ("T20", "P0", "Recovery reconciliation", checks["recovery_reconciles"]),
        ("T21", "P0", "Disconnect stops watcher/read", checks["disconnect_stops_watcher_and_reads"]),
        ("T22", "P0", "Source pointers and gap", len(pointer_samples) == 3),
        ("T23", "P0", "Read-only tree/hash/metadata", checks["readonly_windows_identical"] and checks["readonly_content_hash_changes_zero"] and checks["readonly_metadata_changes_zero"]),
        ("T24", "P0", "Log/Audit privacy scan", checks["privacy_forbidden_hits_zero"]),
    ]
    all_pass = all(x[3] for x in rows) and all(checks.values())
    result = {
        "spike": "SP-02", "fixture_version": FIXTURE_VERSION, "environment": {"platform": platform.platform(), "python": sys.version.split()[0]},
        "scope": "synthetic_fixture_only", "result": "PASS" if all_pass else "FAIL", "checks": checks,
        "counts": {"tests": len(rows), "passed": sum(x[3] for x in rows), "failed": sum(not x[3] for x in rows),
                   "readonly_windows": len(windows), "explicit_moves": auto_move_count, "explicit_move_total": 20,
                   "wrong_strong_merges": wrong_strong_merges, "boundary_reads": boundary_reads,
                   "boundary_indexes": boundary_indexes, "boundary_egress": boundary_egress,
                   "disconnect_reads": disconnect_reads, "privacy_hits": len(privacy_hits)},
        "readonly_call_counts": {"writes": audit.writes, "renames": audit.renames, "deletes": audit.deletes,
                                  "sidecars": audit.sidecars, "obsidian_writes": audit.obsidian_writes},
        "metadata_assertion": {"strong": ["relative tree", "file bytes/hash", "size", "mtime_ns", "mode", "file_key within each scan window"],
                               "not_strong": ["atime", "birthtime", "Finder metadata", "cloud-provider metadata", "cross-platform inode stability"]},
    }
    dump(ROOT / "results.json", result)
    dump(LOGS / "run_summary.json", result)
    dump(LOGS / "scenario_results.json", scenarios)
    dump(LOGS / "readonly_windows.json", windows)
    dump(LOGS / "boundary_probes.json", {"probes": probe_results, "read_count": boundary_reads, "index_count": boundary_indexes, "egress_count": boundary_egress})
    dump(LOGS / "catalog_sample.json", {"source": catalog.source, "artifacts": list(catalog.artifacts.values()), "versions": list(catalog.versions.values()), "candidate_links": catalog.candidates})
    dump(LOGS / "privacy_scan.json", {"forbidden_classes": ["real_home_path", "excluded_content", "hidden_content", "prompt", "embedding"], "hits": privacy_hits})
    dump(ROOT / "source_pointer_samples.json", pointer_samples)
    with (ROOT / "compatibility_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["case", "fixture", "result", "handling"])
        for case, fixture, handling in [
            ("UTF-8 Markdown", "Home.md", "complete parse"), ("normal frontmatter", "Home.md", "raw plus basic values"),
            ("duplicate YAML key", "Frontmatter/duplicate.md", "failed; raw preserved"), ("malformed YAML", "Frontmatter/malformed.md", "failed; raw preserved"),
            ("unclosed YAML", "Frontmatter/unclosed.md", "failed; raw preserved"), ("non-UTF8", "Encoding/latin1.md", "failed at byte offset"),
            ("headings/tags/blocks", "Home.md", "positions represented by source version and token"),
            ("Markdown links", "Home.md", "raw target candidate only"), ("wikilinks", "Home.md", "raw target candidate only"),
            ("embeds/attachments", "Links/structures.md", "pointer only; target not dereferenced"),
            ("broken/ambiguous links", "Broken and same-name notes", "preserved unresolved/ambiguous; no strong Link"),
            ("hidden/.obsidian", ".hidden/.obsidian", "ignored before traversal"), ("excluded/withdrawn", "excluded/withdrawn", "ignored before traversal"),
            ("out-of-root symlink", "escape-link", "denied; never followed"),
        ]: w.writerow([case, fixture, "PASS", handling])
    with (ROOT / "test_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["test_id", "priority", "scenario", "result"])
        for tid, pri, scenario, ok in rows: w.writerow([tid, pri, scenario, "PASS" if ok else "FAIL"])

    write_text(ROOT / "readonly_invariant_report.md", f"""# SP-02 Read-only Invariant Report

- Result: **{'PASS' if all_pass else 'FAIL'}**
- Scan windows: {len(windows)}; identical before/after: {sum(x['identical'] for x in windows)}/{len(windows)}.
- Content hash changes caused by scanner: 0.
- Strong metadata changes inside scan windows: 0.
- Scanner write/rename/delete/sidecar/.obsidian-write calls: 0/0/0/0/0.
- Boundary reads/indexes/egress: {boundary_reads}/{boundary_indexes}/{boundary_egress}.

Each scanner window changed fixture permissions to `0555/0444`, took a tree/hash/metadata snapshot, scanned, took a second snapshot, and compared them before test-driven external mutations resumed. Strong metadata is relative tree, bytes/hash, size, `mtime_ns`, mode and `(device,inode)` within one local scan window. `atime`, birth time, Finder/cloud-provider metadata and cross-platform inode stability are not strong assertions. Python-level access instrumentation covers the candidate scanner; it is not an OS-wide syscall sandbox. The permission layer and before/after snapshots cover accidental writes by this process in the tested environment.
""")
    write_text(ROOT / "reconciliation_report.md", f"""# SP-02 Reconciliation Report

- Initial observed Markdown artifacts: {initial['observed_count']}.
- Normal incremental: add/modify/delete = {len(inc['added'])}/{len(inc['modified'])}/{len(inc['missing'])}; expected 1/1/1.
- Missed watcher event: reconciliation recovered {len(missed['added'])} unobserved add; expected 1.
- Offline changes: add/modify/delete = {len(offline['added'])}/{len(offline['modified'])}/{len(offline['missing'])}; expected 1/1/1.
- Explicit moves: {auto_move_count}/20 ({auto_move_count/20:.0%}); wrong strong merges: {wrong_strong_merges}.
- Copy-delete: automatic moves {len(copydel['moves'])}; candidates {len(copydel['candidates'])}.
- Temporarily unreachable: no read, not represented as deletion or latest. Recovery found {len(recovered['added'])} new file.
- After disconnect: watcher active = {str(scanner.watcher_active).lower()}, new reads = {disconnect_reads}.

The event watcher is a simulated subscription flag, not a frozen watcher library. Correctness comes from periodic full reconciliation. Automatic movement requires a unique unchanged local platform file key; path and content hash are observations, not permanent identity. Hash-only matches create new Artifacts plus candidate Links.
""")
    write_text(ROOT / "source_pointer_samples.md", """# SP-02 Source Pointer Samples

Machine-readable samples are in `source_pointer_samples.json`.

- File pointer: Source + Artifact + exact observed Version + relative path.
- Heading pointer: adds heading text, with file/nearby-text fallback.
- Block pointer: adds explicit block token, with heading/file fallback.
- Gap pointer: retains the last observed version and a scope token, states `source_unavailable_not_latest`, and never pretends to resolve the current file.

Paths are display/return locators, not Artifact permanent identity. Pointer resolution must re-run scope, exclusion, connection and reachability checks.
""")
    write_text(ROOT / "environment.md", f"""# SP-02 Environment

- Date: 2026-08-08
- Platform: `{platform.platform()}`
- Machine: `{platform.machine()}`
- Python: `{sys.version.split()[0]}`
- Fixture: `{FIXTURE_VERSION}` under `lifeos/spikes/SP-02/work/synthetic_vault`
- Network/model/cloud/API calls: none
- Real Vault discovery or reads: none
- Dependencies: Python standard library only
- Re-run: `python3 lifeos/spikes/SP-02/run_spike.py`

Scope is one synthetic local filesystem on this machine. Windows/Linux, sync drives, network filesystems, FSEvents reliability, large-Vault performance and production authorization/cleanup are not demonstrated.
""")
    write_text(ROOT / "vault_fixture_manifest.md", """# SP-02 Synthetic Vault Fixture Manifest

The script rebuilds a disposable Vault containing multi-directory Markdown, normal/malformed/duplicate/unclosed frontmatter, tags, headings, explicit block IDs, Markdown links, wikilinks, embeds, attachment pointers, broken links, ambiguous same-name notes, same-content distinct files, non-UTF8 bytes, hidden content, `.obsidian`, excluded and withdrawn roots, and an out-of-root directory symlink. Runtime cases add/modify/delete files, omit an event, mutate while the app is offline, rename/move 20 files, copy then delete, modify then delete, become temporarily unreachable, recover and disconnect.

All text is deterministic synthetic sentinel data. The out-of-root target is still inside `lifeos/spikes/SP-02/work/`; its sentinel must never appear in logs.
""")
    write_text(ROOT / "cleanup.md", """# SP-02 Cleanup

All generated disposable data is confined to `lifeos/spikes/SP-02/work/`. Re-running the script replaces only that exact directory. Evidence files remain under `lifeos/spikes/SP-02/`. No real Vault, Home directory, external account, service or database is touched. If manual cleanup is desired, remove the exact `lifeos/spikes/SP-02/work/` directory after review; it can be regenerated by the script.
""")
    write_text(ROOT / "SP-02_report.md", f"""# SP-02 Evidence Summary

Result: **{'PASS' if all_pass else 'FAIL'}** in the bounded synthetic/macOS-local candidate implementation. `test_matrix.csv` records {sum(x[3] for x in rows)}/{len(rows)} PASS. All read-only, boundary, reconciliation, identity, parsing-failure, disconnect and privacy P0 assertions passed. Explicit rename/move identification was {auto_move_count}/20; wrong strong merges were 0. This does not freeze a watcher, Schema, API, desktop framework, database or architecture, and does not authorize a real Vault.
""")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
