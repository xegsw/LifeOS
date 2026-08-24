import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';

const root = resolve(process.argv[2] || '.');
const files = Object.fromEntries(['index.html', 'app.js', 'styles.css'].map((name) => [name, readFileSync(resolve(root, name), 'utf8')]));
const joined = Object.values(files).join('\n');
const hash = (name) => createHash('sha256').update(files[name]).digest('hex');
const checks = [
  ['hash-index', hash('index.html') === 'eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722'],
  ['hash-app', hash('app.js') === '784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d'],
  ['hash-styles', hash('styles.css') === '7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2'],
  ['three-state-controls', ['默认恢复态', '暂无可靠建议', '权限受限 · 离线'].every((text) => files['index.html'].includes(text))],
  ['state-switching-handler', /selectState\(button\.dataset\.state\)/.test(files['app.js'])],
  ['explicit-confirmation', files['index.html'].includes('确认保留在本次会话') && files['app.js'].includes('已确认：')],
  ['empty-text-denied', files['app.js'].includes('未保存：请输入原文后再显式确认。')],
  ['failure-hides-record', /record\.hidden = true;\s*status\.textContent = '保存失败/.test(files['app.js'])],
  ['no-suggestion-two-paths', ['选择 Project', '先记录当前停点'].every((text) => files['index.html'].includes(text))],
  ['restricted-offline-ai-disabled', ['本页不联网、不同步。', 'AI 未启用'].every((text) => files['index.html'].includes(text))],
  ['session-only-boundary', files['index.html'].includes('刷新或关闭后手动内容会丢弃')],
  ['no-remote-url', !/https?:\/\//i.test(joined)],
  ['no-network-api', !/\b(fetch|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon)\b/.test(joined)],
  ['no-browser-persistence', !/\b(localStorage|sessionStorage|indexedDB|caches\.)\b/.test(joined)],
  ['no-file-tauri-ipc', !/\b(FileReader|showOpenFilePicker|showSaveFilePicker|__TAURI__|invoke\()\b/.test(joined)],
  ['no-export-sync-model', !/\b(export|synchroniz|model call|OpenAI|Anthropic)\b/i.test(joined)],
];
const results = checks.map(([id, pass]) => ({ id, status: pass ? 'PASS' : 'FAIL' }));
const summary = { passed: results.filter((result) => result.status === 'PASS').length, failed: results.filter((result) => result.status === 'FAIL').length };
console.log(JSON.stringify({ runner: 'LIFEOS-P3-084 independent static runner', root, sourceHashes: Object.fromEntries(Object.keys(files).map((name) => [name, hash(name)])), summary, results }, null, 2));
process.exitCode = summary.failed ? 1 : 0;
