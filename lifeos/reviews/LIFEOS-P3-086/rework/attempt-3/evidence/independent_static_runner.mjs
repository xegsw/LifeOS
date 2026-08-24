import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(process.argv[2] || '.');
const pages = [
  'default-recovery.html',
  'no-reliable-suggestion.html',
  'restricted-offline.html',
];
const source = Object.fromEntries([...pages, 'app.js', 'styles.css'].map((name) => [
  name,
  readFileSync(join(root, name), 'utf8'),
]));
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const results = [];
const check = (id, condition, detail) => results.push({ id, status: condition ? 'PASS' : 'FAIL', detail });

for (const page of pages) {
  const text = source[page];
  check(`${page}/document`, /<!doctype html>/i.test(text) && /<main\b/.test(text), '独立 HTML 文档具有主内容容器。');
  check(`${page}/local-assets`, /href="styles\.css"/.test(text) && /src="app\.js"/.test(text), '仅引用相对本地 CSS 与 JavaScript。');
  check(`${page}/three-way-navigation`, pages.every((target) => text.includes(`href="${target}"`)), '页面包含通向三张本地页面的显式导航。');
  check(`${page}/ai-closed`, text.includes('AI 未启用'), '页面明确披露 AI 未启用。');
}

const recovery = source['default-recovery.html'];
const empty = source['no-reliable-suggestion.html'];
const restricted = source['restricted-offline.html'];
const app = source['app.js'];
check('recovery/context-first', recovery.includes('当前 Project') && recovery.includes('从这里继续') && recovery.includes('今日安排'), '默认页保留从项目恢复到今日安排的叙事。');
check('recovery/confirmed-action', recovery.includes('你已确认 · 行动') && recovery.includes('AI 未启用'), '默认页仅将已确认行动写为今日安排，并关闭 AI。');
check('capture/empty-rejected', app.includes("if (!value)") && app.includes('请先输入原文'), '空文本确认有显式拒绝与披露。');
check('capture/explicit-confirm', app.includes("savedText.textContent = value") && app.includes("savedRecord.hidden = false") && app.includes('已确认'), '非空文本仅在显式确认后显示。');
check('capture/repeated-confirm-idempotent', app.includes("savedText.textContent = value") && !/\.append(?:Child|\()/.test(app), '重复确认替换当前会话显示，不累加记录。');
check('capture/failure-clears', app.includes("clearRecord('模拟失败") && app.includes("savedText.textContent = ''"), '模拟失败清除显示记录并披露未保留。');
check('empty/no-invention', empty.includes('暂无可靠建议') && empty.includes('不会据最近痕迹生成恢复或建议'), '无建议页不虚构重点或建议。');
check('empty/two-human-paths', empty.includes('id="choose-project"') && empty.includes('id="record-stop"') && app.includes('选择 Project 是受控路径') && app.includes('先记录当前停点是受控路径'), '无建议页只提供两条人工受控路径和反馈。');
check('restricted/fail-closed', restricted.includes('网络未使用') && restricted.includes('不读取来源、不处理内容，也不生成建议'), '受限／离线页明确关闭来源处理与建议。');

const combined = Object.values(source).join('\n');
const forbidden = [
  ['closed/remote-url', /https?:\/\//i, '没有远程 URL。'],
  ['closed/network-api', /\b(fetch|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon)\b/, '没有网络 API。'],
  ['closed/browser-persistence', /\b(localStorage|sessionStorage|indexedDB|document\.cookie)\b/, '没有浏览器持久化。'],
  ['closed/file-api', /\b(FileReader|showOpenFilePicker|showSaveFilePicker|FileSystemHandle|input\s+type=["']file)/i, '没有文件 API。'],
  ['closed/tauri-ipc', /\b(Tauri|tauri|invoke\s*\(|ipcRenderer|postMessage\s*\()/i, '没有 Tauri／IPC。'],
  ['closed/export-sync', /\b(export|download|sync|synchroniz)/i, '没有导出或同步能力标识。'],
  ['closed/model-third-party', /\b(OpenAI|Anthropic|Gemini|model\s*invoke|api[_-]?key)\b/i, '没有模型调用或第三方凭据标识。'],
];
for (const [id, pattern, detail] of forbidden) check(id, !pattern.test(combined), detail);

const pass = results.filter((item) => item.status === 'PASS').length;
const fail = results.length - pass;
const report = {
  task: 'LIFEOS-P3-086',
  attempt: 'attempt-3',
  kind: 'fresh-independent-static',
  root,
  pass,
  fail,
  results,
  hashes: Object.fromEntries(Object.entries(source).map(([name, text]) => [name, sha256(text)])),
};
console.log(JSON.stringify(report, null, 2));
process.exitCode = fail ? 1 : 0;
