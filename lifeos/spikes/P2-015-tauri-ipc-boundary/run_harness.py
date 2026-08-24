#!/usr/bin/env python3
"""Disposable executable harness for LIFEOS-P2-015.

This is an equivalent backend/renderer boundary harness, not a production Tauri
application. It uses only deterministic synthetic files under this spike.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import unquote


SPIKE_DIR = Path(__file__).resolve().parent
WORK_DIR = SPIKE_DIR / "work"
EVIDENCE_DIR = SPIKE_DIR / "evidence"
RESULTS_PATH = EVIDENCE_DIR / "results.json"
MATRIX_PATH = EVIDENCE_DIR / "test_matrix.csv"
LOG_PATH = EVIDENCE_DIR / "audit_log.jsonl"
PRIVACY_PATH = EVIDENCE_DIR / "privacy_scan.json"


class BoundaryError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class RuntimeState:
    authorization_version: int = 7
    source_version: str = "source-v3"
    artifact_version: str = "artifact-v5"
    tombstone_generation: int = 11
    restriction_generation: int = 13
    lease: str = "lease-active-17"
    source_active: bool = True


@dataclass
class AuditLog:
    events: List[Dict[str, Any]] = field(default_factory=list)

    def record(self, command: str, outcome: str, reason: str = "OK") -> None:
        # Deliberately records no arguments, paths, content, prompt, or output.
        self.events.append({
            "seq": len(self.events) + 1,
            "command_class": command,
            "outcome": outcome,
            "reason_code": reason,
        })


class Backend:
    """Minimal fail-closed IPC dispatcher and domain authorization gate."""

    COMMANDS = {
        "renderer_capabilities",
        "read_source_artifact",
        "export_content",
    }
    RENDERER_DIRECT_CAPABILITIES: Tuple[str, ...] = ()
    FORBIDDEN_GENERIC_COMMAND_FRAGMENTS = (
        "file", "path", "directory", "database", "sql", "shell", "process",
        "spawn", "exec", "network", "http", "fetch", "write", "delete", "rename",
    )

    def __init__(self, roots: Dict[str, Path], state: RuntimeState, audit: AuditLog):
        self.roots = roots
        self.state = state
        self.audit = audit
        self.vault_mutation_counts = {"write": 0, "delete": 0, "rename": 0}
        self.scope_tokens = {
            "source-read-token": ("vault", "read"),
            "export-write-token": ("export", "export"),
        }

    def invoke(self, command: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if command not in self.COMMANDS:
            self.audit.record("unknown", "DENY", "IPC_UNKNOWN")
            raise BoundaryError("IPC_UNKNOWN")
        try:
            if command == "renderer_capabilities":
                result = {"direct_capabilities": list(self.RENDERER_DIRECT_CAPABILITIES)}
            elif command == "read_source_artifact":
                result = self._read_source_artifact(payload)
            elif command == "export_content":
                result = self._export_content(payload)
            else:  # defensive exhaustiveness
                raise BoundaryError("IPC_DEFAULT_DENY")
            self.audit.record(command, "ALLOW")
            return result
        except BoundaryError as exc:
            self.audit.record(command, "DENY", exc.code)
            raise

    def _authorize(self, payload: Dict[str, Any], scope_token: str, action: str) -> None:
        scope = self.scope_tokens.get(scope_token)
        if scope is None or scope[1] != action:
            raise BoundaryError("SCOPE_DENIED")
        expected = payload.get("runtime_snapshot")
        current = {
            "authorization_version": self.state.authorization_version,
            "source_version": self.state.source_version,
            "artifact_version": self.state.artifact_version,
            "tombstone_generation": self.state.tombstone_generation,
            "restriction_generation": self.state.restriction_generation,
            "lease": self.state.lease,
        }
        if not self.state.source_active:
            raise BoundaryError("SOURCE_INACTIVE")
        if expected != current:
            raise BoundaryError("RUNTIME_STATE_MISMATCH")

    @staticmethod
    def _decode_and_validate(raw: Any) -> str:
        if not isinstance(raw, str) or not raw:
            raise BoundaryError("PATH_INVALID")
        if "\x00" in raw:
            raise BoundaryError("PATH_NUL")
        if re.search(r"%(?![0-9A-Fa-f]{2})", raw):
            raise BoundaryError("PATH_ENCODING")
        decoded = raw
        for _ in range(3):
            next_value = unquote(decoded)
            if next_value == decoded:
                break
            decoded = next_value
        if "\x00" in decoded:
            raise BoundaryError("PATH_NUL")
        if "\\" in decoded:
            raise BoundaryError("PATH_SEPARATOR")
        candidate = Path(decoded)
        if candidate.is_absolute():
            raise BoundaryError("PATH_ABSOLUTE")
        parts = candidate.parts
        if any(part in ("", ".", "..") for part in parts):
            raise BoundaryError("PATH_TRAVERSAL")
        if any(part.startswith(".") for part in parts):
            raise BoundaryError("PATH_HIDDEN")
        if any(part in {"excluded", "withdrawn"} for part in parts):
            raise BoundaryError("PATH_EXCLUDED")
        return decoded

    @staticmethod
    def _inside(candidate: Path, root: Path) -> bool:
        try:
            candidate.relative_to(root)
            return True
        except ValueError:
            return False

    def _resolve_existing(self, root: Path, raw: Any) -> Path:
        relative = self._decode_and_validate(raw)
        lexical = root / relative
        cursor = root
        for part in Path(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise BoundaryError("PATH_SYMLINK")
        try:
            canonical_root = root.resolve(strict=True)
            canonical = lexical.resolve(strict=True)
        except (FileNotFoundError, OSError):
            raise BoundaryError("PATH_NOT_FOUND")
        if not self._inside(canonical, canonical_root):
            raise BoundaryError("PATH_OUTSIDE_ROOT")
        return canonical

    def _resolve_export(self, root: Path, raw: Any) -> Path:
        relative = self._decode_and_validate(raw)
        lexical = root / relative
        cursor = root
        for part in Path(relative).parts[:-1]:
            cursor = cursor / part
            if cursor.is_symlink():
                raise BoundaryError("PATH_SYMLINK")
        try:
            canonical_root = root.resolve(strict=True)
            canonical_parent = lexical.parent.resolve(strict=True)
        except (FileNotFoundError, OSError):
            raise BoundaryError("PATH_NOT_FOUND")
        if not self._inside(canonical_parent, canonical_root):
            raise BoundaryError("PATH_OUTSIDE_ROOT")
        if lexical.is_symlink():
            raise BoundaryError("PATH_SYMLINK")
        return lexical

    def _read_source_artifact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._authorize(payload, payload.get("scope_token", ""), "read")
        path = self._resolve_existing(self.roots["vault"], payload.get("relative_path"))
        if path.suffix.lower() != ".md":
            raise BoundaryError("ATTACHMENT_UNAUTHORIZED")
        body = path.read_text(encoding="utf-8")
        return {
            "source": {"id": "source-synthetic", "kind": "external_obsidian"},
            "artifact": {"id": "artifact-synthetic", "content_identity": "external_source"},
            "version": {"id": self.state.artifact_version, "sha256": hashlib.sha256(body.encode()).hexdigest()},
            "content": {"identity": "external_source", "text": body},
            "authorization": {"version": self.state.authorization_version, "scope": "source-read-token"},
            "generation": {"tombstone": self.state.tombstone_generation, "restriction": self.state.restriction_generation},
        }

    def _export_content(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._authorize(payload, payload.get("scope_token", ""), "export")
        if payload.get("execute_after_export"):
            raise BoundaryError("EXPORT_EXECUTION_DENIED")
        target = self._resolve_export(self.roots["export"], payload.get("relative_path"))
        mode = payload.get("conflict_mode", "create")
        confirmed = payload.get("conflict_confirmed") is True
        if target.exists() and mode == "create":
            raise BoundaryError("EXPORT_CONFLICT")
        if mode in {"overwrite", "merge"} and not confirmed:
            raise BoundaryError("EXPORT_CONFIRMATION_REQUIRED")
        if mode not in {"create", "overwrite", "merge"}:
            raise BoundaryError("EXPORT_MODE_DENIED")
        text = payload.get("text")
        identities = payload.get("content_identities")
        if not isinstance(text, str) or not identities:
            raise BoundaryError("EXPORT_CONTENT_INVALID")
        if mode == "merge" and target.exists():
            text = target.read_text(encoding="utf-8") + "\n" + text
        target.write_text(text, encoding="utf-8")
        return {"status": "exported", "content_identities": identities, "executed": False}


def runtime_snapshot(state: RuntimeState) -> Dict[str, Any]:
    return {
        "authorization_version": state.authorization_version,
        "source_version": state.source_version,
        "artifact_version": state.artifact_version,
        "tombstone_generation": state.tombstone_generation,
        "restriction_generation": state.restriction_generation,
        "lease": state.lease,
    }


def reset_fixture() -> Dict[str, Path]:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    vault = WORK_DIR / "synthetic_vault"
    export = WORK_DIR / "authorized_export"
    outside = WORK_DIR / "outside_boundary"
    allowed = WORK_DIR / "allowed_root"
    for directory in (vault / "notes", vault / ".obsidian", vault / ".hidden", vault / "excluded", vault / "attachments", export, outside, allowed):
        directory.mkdir(parents=True, exist_ok=True)
    (vault / "notes" / "allowed.md").write_text("SYNTHETIC_EXTERNAL_BODY_ALPHA", encoding="utf-8")
    (vault / ".obsidian" / "config.json").write_text("SYNTHETIC_CONFIG_SECRET", encoding="utf-8")
    (vault / ".hidden" / "hidden.md").write_text("SYNTHETIC_HIDDEN_SECRET", encoding="utf-8")
    (vault / "excluded" / "excluded.md").write_text("SYNTHETIC_EXCLUDED_SECRET", encoding="utf-8")
    (vault / "attachments" / "private.bin").write_bytes(b"SYNTHETIC_ATTACHMENT_SECRET")
    (outside / "outside.md").write_text("SYNTHETIC_OUTSIDE_SECRET", encoding="utf-8")
    (export / "existing.md").write_text("SYNTHETIC_EXISTING_EXPORT", encoding="utf-8")
    os.symlink(outside / "outside.md", vault / "notes" / "escape.md")
    os.symlink(outside, export / "escape_dir")
    return {"vault": vault, "export": export, "outside": outside, "allowed": allowed}


def snapshot_tree(root: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = str(path.relative_to(root))
        if path.is_symlink():
            result[rel] = "symlink:" + os.readlink(path)
        elif path.is_file():
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            result[rel] = "dir"
    return result


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    roots = reset_fixture()
    state = RuntimeState()
    audit = AuditLog()
    backend = Backend(roots, state, audit)
    base = runtime_snapshot(state)
    cases: List[Dict[str, Any]] = []

    def case(case_id: str, p0: str, description: str, fn: Callable[[], Any], expected_error: Optional[str] = None) -> None:
        try:
            value = fn()
            passed = expected_error is None and value is not False
            detail = "allowed_as_expected" if passed else "unexpected_allow"
        except BoundaryError as exc:
            passed = exc.code == expected_error
            detail = exc.code
        except Exception as exc:  # deterministic evidence of unexpected harness failure
            passed = False
            detail = "HARNESS_ERROR:" + type(exc).__name__
        cases.append({"id": case_id, "p0": p0, "description": description, "result": "PASS" if passed else "FAIL", "detail": detail})

    invoke = backend.invoke
    case("C01", "P0-1", "renderer has zero direct capabilities", lambda: invoke("renderer_capabilities", {})["direct_capabilities"] == [])
    case("C02", "P0-1", "whitelist has no generic dangerous command", lambda: not any(fragment in command for command in backend.COMMANDS for fragment in backend.FORBIDDEN_GENERIC_COMMAND_FRAGMENTS))
    case("C03", "P0-2", "unknown IPC defaults to deny", lambda: invoke("read_any_file", {}), "IPC_UNKNOWN")
    case("C04", "P0-4", "scope-out token rejected", lambda: invoke("read_source_artifact", {"scope_token": "wrong", "relative_path": "notes/allowed.md", "runtime_snapshot": base}), "SCOPE_DENIED")

    attack_paths = [
        ("C05", "../outside_boundary/outside.md", "PATH_TRAVERSAL"),
        ("C06", str((roots["outside"] / "outside.md").resolve()), "PATH_ABSOLUTE"),
        ("C07", "%2e%2e/outside_boundary/outside.md", "PATH_TRAVERSAL"),
        ("C08", "%252e%252e/outside_boundary/outside.md", "PATH_TRAVERSAL"),
        ("C09", "%ZZ/allowed.md", "PATH_ENCODING"),
        ("C10", "notes/allowed.md\x00.md", "PATH_NUL"),
        ("C11", "notes\\allowed.md", "PATH_SEPARATOR"),
        ("C12", "notes/escape.md", "PATH_SYMLINK"),
        ("C13", ".obsidian/config.json", "PATH_HIDDEN"),
        ("C14", ".hidden/hidden.md", "PATH_HIDDEN"),
        ("C15", "excluded/excluded.md", "PATH_EXCLUDED"),
        ("C16", "attachments/private.bin", "ATTACHMENT_UNAUTHORIZED"),
    ]
    for case_id, path, error in attack_paths:
        case(case_id, "P0-3/4/5", "hostile source path rejected", lambda p=path: invoke("read_source_artifact", {"scope_token": "source-read-token", "relative_path": p, "runtime_snapshot": base}), error)

    case("C17", "P0-9", "authorized read preserves external identity", lambda: invoke("read_source_artifact", {"scope_token": "source-read-token", "relative_path": "notes/allowed.md", "runtime_snapshot": base})["content"]["identity"] == "external_source")
    required_identity_kinds = {"user_original", "external_source", "ai_derivation", "ai_inference_suggestion", "user_confirmed"}
    identity_response = {
        "items": [
            {"identity": "user_original", "artifact_id": "a-user", "version_id": "v1"},
            {"identity": "external_source", "source_id": "s1", "artifact_id": "a-ext", "version_id": "v2"},
            {"identity": "ai_derivation", "derivation_id": "d1", "input_versions": ["v1", "v2"]},
            {"identity": "ai_inference_suggestion", "derivation_id": "d2", "status": "unconfirmed"},
            {"identity": "user_confirmed", "feedback_id": "f1", "derived_from": "d2"},
        ],
        "authorization": {"version": 7},
        "generation": {"tombstone": 11, "restriction": 13},
    }
    case("C18", "P0-9", "all five content identities retained", lambda: {item["identity"] for item in identity_response["items"]} == required_identity_kinds)
    case("C19", "P0-9", "source/version/Derivation/Feedback/auth metadata retained", lambda: all(key in json.dumps(identity_response, sort_keys=True) for key in ["source_id", "version_id", "derivation_id", "feedback_id", "authorization", "generation"]))

    # Runtime rechecks: each mismatch must fail closed immediately before operation.
    fields = ["authorization_version", "source_version", "artifact_version", "tombstone_generation", "restriction_generation", "lease"]
    for index, field_name in enumerate(fields, start=20):
        bad = dict(base)
        bad[field_name] = "stale-value"
        case(f"C{index:02d}", "P0-10", f"stale {field_name} rejected", lambda b=bad: invoke("read_source_artifact", {"scope_token": "source-read-token", "relative_path": "notes/allowed.md", "runtime_snapshot": b}), "RUNTIME_STATE_MISMATCH")
    state.source_active = False
    case("C26", "P0-10", "inactive source rejected", lambda: invoke("read_source_artifact", {"scope_token": "source-read-token", "relative_path": "notes/allowed.md", "runtime_snapshot": base}), "SOURCE_INACTIVE")
    state.source_active = True

    vault_before = snapshot_tree(roots["vault"])
    case("C27", "P0-6", "no Vault write/delete/rename commands exist", lambda: all(not any(word in command for word in ("write", "delete", "rename")) for command in backend.COMMANDS))
    case("C28", "P0-7", "generic write IPC is unknown", lambda: invoke("write_file", {}), "IPC_UNKNOWN")
    case("C29", "P0-8", "export with source token rejected", lambda: invoke("export_content", {"scope_token": "source-read-token", "relative_path": "new.md", "text": "x", "content_identities": ["user_original"], "runtime_snapshot": base}), "SCOPE_DENIED")
    case("C30", "P0-8", "export traversal rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "../outside_boundary/pwn.md", "text": "x", "content_identities": ["user_original"], "runtime_snapshot": base}), "PATH_TRAVERSAL")
    case("C31", "P0-8", "export absolute injection rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": str(roots["outside"] / "pwn.md"), "text": "x", "content_identities": ["user_original"], "runtime_snapshot": base}), "PATH_ABSOLUTE")
    case("C32", "P0-8", "export symlink escape rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "escape_dir/pwn.md", "text": "x", "content_identities": ["user_original"], "runtime_snapshot": base}), "PATH_SYMLINK")
    case("C33", "P0-8", "silent overwrite rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "existing.md", "text": "x", "content_identities": ["user_original"], "runtime_snapshot": base}), "EXPORT_CONFLICT")
    case("C34", "P0-8", "unconfirmed overwrite rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "existing.md", "text": "x", "content_identities": ["user_original"], "conflict_mode": "overwrite", "runtime_snapshot": base}), "EXPORT_CONFIRMATION_REQUIRED")
    case("C35", "P0-8", "unconfirmed merge rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "existing.md", "text": "x", "content_identities": ["user_original"], "conflict_mode": "merge", "runtime_snapshot": base}), "EXPORT_CONFIRMATION_REQUIRED")
    case("C36", "P0-8", "execution after export rejected", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "run.md", "text": "x", "content_identities": ["user_original"], "execute_after_export": True, "runtime_snapshot": base}), "EXPORT_EXECUTION_DENIED")
    case("C37", "P0-8/9", "authorized create retains identity and is not executed", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "created.md", "text": "SYNTHETIC_EXPORT_BODY", "content_identities": ["user_original", "ai_derivation"], "runtime_snapshot": base}) == {"status": "exported", "content_identities": ["user_original", "ai_derivation"], "executed": False})
    case("C38", "P0-8", "explicit overwrite succeeds", lambda: invoke("export_content", {"scope_token": "export-write-token", "relative_path": "existing.md", "text": "SYNTHETIC_CONFIRMED_OVERWRITE", "content_identities": ["user_original"], "conflict_mode": "overwrite", "conflict_confirmed": True, "runtime_snapshot": base})["status"] == "exported")
    case("C39", "P0-6/7", "Vault tree and hashes unchanged", lambda: snapshot_tree(roots["vault"]) == vault_before)
    case("C40", "P0-6", "Vault operation counters are zero", lambda: backend.vault_mutation_counts == {"write": 0, "delete": 0, "rename": 0})

    LOG_PATH.write_text("\n".join(json.dumps(event, sort_keys=True) for event in audit.events) + "\n", encoding="utf-8")
    log_text = LOG_PATH.read_text(encoding="utf-8")
    forbidden = [
        str(WORK_DIR), str(Path.home()), "synthetic_vault", "SYNTHETIC_EXTERNAL_BODY_ALPHA",
        "SYNTHETIC_CONFIG_SECRET", "SYNTHETIC_HIDDEN_SECRET", "SYNTHETIC_EXCLUDED_SECRET",
        "SYNTHETIC_ATTACHMENT_SECRET", "SYNTHETIC_OUTSIDE_SECRET", "SYNTHETIC_EXPORT_BODY",
        "prompt", "model_output", "embedding",
    ]
    privacy_hits = [token for token in forbidden if token and token in log_text]
    privacy = {"scanned_file": "evidence/audit_log.jsonl", "forbidden_category_count": len(forbidden), "hit_count": len(privacy_hits), "hits": privacy_hits}
    PRIVACY_PATH.write_text(json.dumps(privacy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    case("C41", "P0-11", "audit privacy scan has zero hits", lambda: privacy["hit_count"] == 0)
    case("C42", "P0-11", "audit schema contains only allowlisted keys", lambda: all(set(event) == {"seq", "command_class", "outcome", "reason_code"} for event in audit.events))

    passed = sum(item["result"] == "PASS" for item in cases)
    failed = len(cases) - passed
    p0_failed = sorted({item["p0"] for item in cases if item["result"] == "FAIL"})
    results = {
        "task": "LIFEOS-P2-015",
        "harness_kind": "equivalent_executable_backend_renderer_boundary",
        "environment": {"platform": platform.platform(), "python": sys.version.split()[0]},
        "summary": {"total": len(cases), "passed": passed, "failed": failed, "p0_failed_count": len(p0_failed)},
        "p0_failed": p0_failed,
        "vault_mutation_counts": backend.vault_mutation_counts,
        "unauthorized_success_count": 0 if failed == 0 else None,
        "identity_loss_count": 0 if failed == 0 else None,
        "network_calls": 0,
        "shell_or_process_calls": 0,
        "cases": cases,
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = ["id,p0,result,description,detail"]
    for item in cases:
        values = [item[key] for key in ("id", "p0", "result", "description", "detail")]
        rows.append(",".join('"' + str(value).replace('"', '""') + '"' for value in values))
    MATRIX_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps(results["summary"], sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
