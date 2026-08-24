import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const root = process.argv[2] || new URL('..', import.meta.url).pathname;
const attempt = join(root, 'evidence/rework/attempt-2');
const closure = await readFile(join(attempt, 'dynamic_evidence_closure.md'), 'utf8');
const required = [
  ['D-REOPEN', [['01-confirmed-before-close.jpeg', 'c19cbb26e0477f11cf7b03226915272fa4d864baccf2a85b34b3d64af78c3559'], ['02-reopened-cleared.jpeg', 'ad7bb860324db8f30093130e2b62631400856e39d7a7d4e33f7da68d44bc5be6']]],
  ['D-TAB-ENTER', [['03-tab-skip-link-focus.jpeg', '848f2b056488b74e65c05d22f676ccbd591875b52214379e63ac9b1074761282'], ['04-enter-skip-link.jpeg', '8194ae6a9b6de108d14f3f95a651b79d8b8380bbf6a95eaf774f9255ac01b47c']]]
];
const results = [];
for (const [id, evidence] of required) {
  const row = closure.split('\n').find(line => line.includes(`| ${id} |`)) || '';
  const verified = await Promise.all(evidence.map(async ([file, expectedHash]) => {
    const actualHash = createHash('sha256').update(await readFile(join(attempt, file))).digest('hex');
    return { file, expectedHash, actualHash, pass: row.includes(file) && row.includes(expectedHash) && actualHash === expectedHash };
  }));
  results.push({ id, pass: row.includes('| PASS |') && verified.every(item => item.pass), verified });
}
const payload = { pass: results.filter(r => r.pass).length, fail: results.filter(r => !r.pass).length, results };
console.log(JSON.stringify(payload, null, 2));
process.exitCode = payload.fail ? 1 : 0;
