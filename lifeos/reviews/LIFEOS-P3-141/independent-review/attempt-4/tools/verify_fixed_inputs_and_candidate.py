#!/usr/bin/env python3
"""Attempt-4 owned fixed-input, lineage, and static-contract verifier."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import sys


WORKTREE = pathlib.Path('/Users/xxe/.codex/worktrees/3a75/No.2')
PM = pathlib.Path('/Users/xxe/Documents/No.2')
INVENTORY = PM / 'lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json'
P139_CANDIDATE = pathlib.Path('/Users/xxe/.codex/worktrees/b381/No.2/lifeos/engineering/LIFEOS-P3-139/closure-4/candidate')
P140_CANDIDATE = pathlib.Path('/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/candidate')
CANDIDATE = WORKTREE / 'lifeos/engineering/LIFEOS-P3-141/candidate'
OUT = WORKTREE / 'lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-4/evidence/matrices/fixed_inputs_and_lineage.json'


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def tree(root: pathlib.Path) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for path in sorted((item for item in root.rglob('*') if item.is_file()), key=lambda item: item.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        entries.append({'path': rel, 'bytes': path.stat().st_size, 'sha256': digest(path)})
    framed = hashlib.sha256()
    for entry in entries:
        raw = json.dumps(entry, sort_keys=True, separators=(',', ':')).encode('utf-8')
        framed.update(len(raw).to_bytes(8, 'big'))
        framed.update(raw)
    return {'file_count': len(entries), 'length_framed_tree_sha256': framed.hexdigest(), 'entries': entries}


def entry_map(entries: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(entry['path']): {'bytes': entry['bytes'], 'sha256': entry['sha256']} for entry in entries}


def p139_manifest_entries() -> dict[str, dict[str, object]]:
    path = pathlib.Path('/Users/xxe/.codex/worktrees/b381/No.2/lifeos/engineering/LIFEOS-P3-139/evidence/FINAL_MANIFEST.json')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    output: dict[str, dict[str, object]] = {}
    for entry in manifest['entries']:
        if entry.get('role') == 'candidate_source':
            rel = str(entry['path']).split('/candidate/', 1)[1]
            output[rel] = {'bytes': entry['bytes'], 'sha256': entry['sha256']}
    return output


def p140_manifest_entries() -> dict[str, dict[str, object]]:
    path = pathlib.Path('/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/evidence/FINAL_MANIFEST.json')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    return manifest['candidate']['entries']


def main() -> int:
    inventory = json.loads(INVENTORY.read_text(encoding='utf-8'))
    input_results = []
    errors: list[str] = []
    for entry in inventory['entries']:
        raw = entry['path']
        path = pathlib.Path(raw) if raw.startswith('/') else PM / raw
        observed = {'role': entry['role'], 'path': raw, 'expected_bytes': entry['bytes'], 'expected_sha256': entry['sha256']}
        try:
            observed.update({'observed_bytes': path.stat().st_size, 'observed_sha256': digest(path)})
            observed['pass'] = observed['observed_bytes'] == entry['bytes'] and observed['observed_sha256'] == entry['sha256']
        except OSError as exc:
            observed.update({'pass': False, 'error': type(exc).__name__})
        if not observed['pass']:
            errors.append(f"fixed_input:{entry['role']}")
        input_results.append(observed)

    p139 = tree(P139_CANDIDATE)
    p140 = tree(P140_CANDIDATE)
    candidate = tree(CANDIDATE)
    expected = inventory['tree_lineage']
    p139_expected_entries = p139_manifest_entries()
    p140_expected_entries = p140_manifest_entries()
    p139_pass = p139['file_count'] == expected['p3_139_candidate_file_count'] and entry_map(p139['entries']) == p139_expected_entries
    p140_pass = p140['file_count'] == expected['p3_140_candidate_file_count'] and entry_map(p140['entries']) == p140_expected_entries
    if not p139_pass:
        errors.append('p3_139_lineage')
    if not p140_pass:
        errors.append('p3_140_lineage')

    runtime = (CANDIDATE / 'src/runtime.rs').read_text(encoding='utf-8')
    ui_files = '\n'.join(path.read_text(encoding='utf-8', errors='replace') for path in sorted((CANDIDATE / 'ui').glob('*')) if path.is_file())
    ipc_declared = re.search(r'const IPC: \[&str; (\d+)\] = \[(.*?)\];', runtime, re.S)
    ipc = re.findall(r'"([a-z_]+)"', ipc_declared.group(2)) if ipc_declared else []
    provider_profiles = re.findall(r'"(openai|anthropic|ollama|lm_studio)"', runtime)
    old_identity_hits = {
        'p3_133': len(re.findall(r'P3-133|p3-133', runtime + ui_files)),
        'p3_131': len(re.findall(r'P3-131|p3-131', runtime + ui_files)),
    }
    static = {
        'ipc_declared_length': int(ipc_declared.group(1)) if ipc_declared else None,
        'ipc_unique_count': len(set(ipc)),
        'ipc': ipc,
        'provider_profiles_found': sorted(set(provider_profiles)),
        'custom_profile_token_present': 'custom_openai_compatible' in runtime + ui_files,
        'old_real_flow_identity_hits': old_identity_hits,
        'p3_141_identity_present': 'P3-141' in runtime + ui_files,
    }
    static['provider_profile_enum_has_custom_variant'] = 'enum ProviderProfile { Openai, Anthropic, Ollama, LmStudio, Custom' in runtime or 'enum ProviderProfile { Openai, Anthropic, Ollama, LmStudio , Custom' in runtime
    static['pass'] = static['ipc_declared_length'] == 20 and static['ipc_unique_count'] == 20 and static['provider_profiles_found'] == ['anthropic', 'lm_studio', 'ollama', 'openai'] and not static['provider_profile_enum_has_custom_variant'] and all(value == 0 for value in old_identity_hits.values()) and static['p3_141_identity_present']
    if not static['pass']:
        errors.append('static_contract')

    payload = {
        'schema': 'lifeos.p3_141.attempt_4.fixed_input_and_lineage.v1',
        'inventory_path': str(INVENTORY),
        'fixed_inputs': input_results,
        'fixed_input_pass_count': sum(1 for item in input_results if item['pass']),
        'p3_139_lineage': {**p139, 'expected_file_count': expected['p3_139_candidate_file_count'], 'manifest_asserted_tree_sha256': expected['p3_139_candidate_tree_sha256'], 'manifest_entry_count': len(p139_expected_entries), 'entry_by_entry_pass': p139_pass},
        'p3_140_lineage': {**p140, 'expected_file_count': expected['p3_140_candidate_file_count'], 'manifest_asserted_tree_sha256': expected['p3_140_candidate_tree_sha256'], 'manifest_entry_count': len(p140_expected_entries), 'entry_by_entry_pass': p140_pass},
        'candidate_before': candidate,
        'static_contract': static,
        'errors': errors,
        'pass': not errors,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pass': payload['pass'], 'fixed_inputs': payload['fixed_input_pass_count'], 'p139': p139_pass, 'p140': p140_pass, 'candidate_files': candidate['file_count'], 'static': static['pass'], 'errors': errors}, ensure_ascii=False))
    return 0 if payload['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
