#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const manifestPath = process.argv[2] ?? 'lifeos/reviews/LIFEOS-P3-144/independent-review/FINAL_MANIFEST.json';
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const sha256 = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
const errors = [];
if (manifest.selfExclusion !== true) errors.push('self_exclusion_required');
if (manifest.entries.some((entry) => entry.path === manifestPath || entry.path.endsWith('/FINAL_MANIFEST.json'))) {
  errors.push('manifest_is_self_referential');
}
for (const entry of manifest.entries) {
  try {
    const actual = sha256(entry.path);
    if (actual !== entry.sha256) errors.push(`hash_mismatch:${entry.path}`);
  } catch {
    errors.push(`missing:${entry.path}`);
  }
}
console.log(JSON.stringify({
  schema: 'lifeos.p3-144.independent-review.failure-manifest-verification.v1',
  manifestPath,
  entryCount: manifest.entries.length,
  result: errors.length === 0 ? 'PASS' : 'FAIL',
  errors
}, null, 2));
process.exitCode = errors.length === 0 ? 0 : 1;
