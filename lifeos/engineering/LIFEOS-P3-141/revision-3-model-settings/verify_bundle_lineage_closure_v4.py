#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

workspace = Path(__file__).resolve().parents[4]
manifest_path = workspace / 'lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/BUNDLE_LINEAGE_CLOSURE_V4_FINAL_MANIFEST.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
errors = []
if manifest.get('schema') != 'lifeos.p3-141.v4.prebuild-blocked-manifest.v1':
    errors.append('schema')
if manifest.get('status') != 'BLOCKED_ROOT_GATE_INCOMPATIBILITY':
    errors.append('status')
for relative, expected in manifest.get('evidence_files', {}).items():
    path = workspace / relative
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(f'evidence:{relative}')
if os.path.lexists(manifest['temporary_root']):
    errors.append('temporary_root_not_absent')
print(json.dumps({
    'schema': 'lifeos.p3-141.v4.prebuild-blocked-verifier-result.v1',
    'pass': not errors,
    'errors': errors,
    'archive_status': manifest.get('status'),
    'message': 'PASS validates only the v4 blocked archive; it is not an engineering or review conclusion.'
}, ensure_ascii=False, sort_keys=True))
raise SystemExit(1 if errors else 0)
