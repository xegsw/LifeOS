# LIFEOS-P2-015 evidence entry

## Scope and conclusion

This directory contains a disposable, executable **equivalent harness** for the
renderer/backend IPC boundary. It is not a packaged Tauri application and does
not freeze a capability name, IPC signature, API, schema, file layout, or
desktop architecture.

Latest deterministic run: **42/42 PASS, 0 FAIL, 0 P0 failures**. The result is
therefore suitable only for a project-level **Pass with Conditions**: the
backend contract is executable and passes, while the actual Tauri capability,
plugin, webview, packaging, and release configuration must repeat the same
matrix when introduced.

## Reproduce

From the repository root:

```sh
python3 lifeos/spikes/P2-015-tauri-ipc-boundary/run_harness.py
```

Expected stdout:

```json
{"failed": 0, "p0_failed_count": 0, "passed": 42, "total": 42}
```

The script deletes and recreates only its own `work/` child directory. It uses
fixed synthetic sentinels and performs no network, shell, process-spawn, model,
cloud, third-party, account, or paid-resource operation.

## Environment

- Run date: 2026-08-09 (Asia/Shanghai)
- OS: macOS arm64 host
- Python: 3.9.6, standard library only
- Rust/Tauri toolchain: unavailable and not installed for this spike
- Harness SHA-256: `a92a547a346a7d6ead724d6fc2001ae415d97f5b8800b39426ef3ee617591410`
- Capability contract SHA-256: `ce5d918fa5afc7cc016d1df7b2f5c863aade3b1d6eba2b5372bf6466763ff36b`

## Evidence map

- `run_harness.py`: executable dispatcher, authorization/path gate, synthetic
  fixture builder, and 42 deterministic assertions.
- `equivalent_capability_contract.json`: renderer direct-capability and command
  allowlist declaration; unknown IPC defaults to deny.
- `fixture_manifest.md`: allowed root, synthetic Vault, authorized export root,
  outside root, hidden/excluded/attachment and symlink probes.
- `evidence/results.json`: machine-readable full result and zero-event counters.
- `evidence/test_matrix.csv`: one row per assertion.
- `evidence/audit_log.jsonl`: minimized reason-code-only audit events.
- `evidence/privacy_scan.json`: privacy scan result, 0 hits across 13 forbidden
  path/content/log categories.

## Security boundary proved by this harness

- Renderer direct file, directory, raw database, shell, process, network, and
  generic path capabilities are absent.
- Only three narrow IPC commands exist; unknown commands fail closed.
- Source paths are decoded, validated, canonicalized, checked against the real
  allowed root, and reject traversal, absolute paths, malformed/double encoding,
  NUL, alternate separators, hidden/excluded items, unauthorized attachments,
  and symlinks.
- Vault mutation commands are absent; generic write IPC is unknown; the Vault
  tree and hashes remain unchanged.
- Export is restricted to the authorized export root, rejects traversal,
  absolute and symlink escapes, rejects silent overwrite/merge, and never
  executes output.
- Reads/exports recheck authorization, source/artifact version, tombstone and
  restriction generation, source activity, and lease immediately before use.
- Responses retain user-original, external-source, AI-derivation, AI-inference/
  suggestion, and user-confirmed identities with source/version/Derivation/
  Feedback/Authorization metadata.

## Condition and retest trigger

Before any real Tauri shell or Obsidian/exports capability is enabled, port this
matrix to the actual application and run it against debug and release bundles on
every target platform. The real configuration must prove plugin/capability
allowlists, CSP/webview/network restrictions, invoke registration, filesystem
scope, symlink behavior, updater/release packaging, and OS-specific path rules.
Any unauthorized success, Vault mutation command, export escape, default allow,
identity loss, or privacy leak changes the result to Fail and keeps the affected
capability disabled.
