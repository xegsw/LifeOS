import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const root = process.argv[2];
if (!root) throw new Error('usage: node independent_static_runner.mjs <copied-ui-directory>');
const files = Object.fromEntries(['index.html', 'app.js', 'styles.css'].map((name) => [name, readFileSync(`${root}/${name}`, 'utf8')]));
const all = Object.values(files).join('\n');
const cases = [
  ['three state controls', /data-state="recovery"[\s\S]*data-state="no-suggestion"[\s\S]*data-state="restricted"/],
  ['recovery marks AI off and confirmed action', /AI 未启用[\s\S]*你已确认 · 行动/],
  ['no suggestion states evidence gap and two paths', /暂无可靠建议[\s\S]*选择 Project[\s\S]*先记录当前停点/],
  ['restricted state separately explains offline and source handling', /权限受限 · 离线[\s\S]*离线状态[\s\S]*来源／处理边界/],
  ['capture requires explicit confirmation and rejects empty input', /value\.trim\(\)[\s\S]*未保存：请输入原文后再显式确认/],
  ['failure hides record and discloses failure', /record\.hidden = true[\s\S]*保存失败：本次会话未保留原文/],
  ['refresh-safe implementation has no storage API', !/localStorage|sessionStorage|indexedDB|document\.cookie/.test(files['app.js'])],
  ['forbidden remote or runtime capabilities absent', !/https?:\/\/|fetch\(|XMLHttpRequest|WebSocket|navigator\.serviceWorker|__TAURI__|invoke\(|showOpenFilePicker|FileReader|download=|\bexport\b|\bsync\b|model/.test(`${files['index.html']}\n${files['app.js']}`)],
];
const results = cases.map(([name, rule]) => ({ name, pass: typeof rule === 'boolean' ? rule : rule.test(all) }));
const output = {
  runner: 'independent_static_runner.mjs',
  sourceHashes: Object.fromEntries(Object.entries(files).map(([name, value]) => [name, createHash('sha256').update(value).digest('hex')])),
  results,
  summary: { passed: results.filter((x) => x.pass).length, failed: results.filter((x) => !x.pass).length },
};
console.log(JSON.stringify(output, null, 2));
process.exitCode = output.summary.failed ? 1 : 0;
