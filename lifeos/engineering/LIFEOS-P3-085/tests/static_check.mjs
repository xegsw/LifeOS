import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];
const assets = [...pages, 'app.js', 'styles.css'];
const results = [];
const check = (name, condition, detail) => results.push({ name, status: condition ? 'PASS' : 'FAIL', detail });
const read = async (file) => readFile(resolve(root, file), 'utf8');
const source = Object.fromEntries(await Promise.all(assets.map(async (file) => [file, await read(file)])));

for (const page of pages) {
  check(`${page}: standalone document`, /<!doctype html>/i.test(source[page]) && /<main class="shell">/.test(source[page]), '可单独作为 HTML 文档打开。');
  check(`${page}: local stylesheet`, /href="styles\.css"/.test(source[page]), '仅加载相对本地样式。');
  check(`${page}: local script`, /src="app\.js"/.test(source[page]), '仅加载相对本地脚本。');
  check(`${page}: three-page navigation`, pages.every((target) => source[page].includes(`href="${target}"`)), '可见且非自动的三页导航完整。');
  check(`${page}: AI closed`, source[page].includes('AI 未启用'), '每页显式呈现 AI 关闭态。');
}

check('default: recovery narrative', /从这里继续/.test(source['default-recovery.html']) && /当前 Project/.test(source['default-recovery.html']), '保留“今日从哪里继续”的主叙事。');
check('default: explicit confirmation capture', /确认保留在本次会话/.test(source['default-recovery.html']) && /你的记录／原文/.test(source['default-recovery.html']), '捕获需显式确认。');
check('empty: no invented suggestion', /暂无可靠建议/.test(source['no-reliable-suggestion.html']) && /不会据最近痕迹生成恢复或建议/.test(source['no-reliable-suggestion.html']), '无建议页披露缺口。');
check('empty: two controlled paths', /选择 Project/.test(source['no-reliable-suggestion.html']) && /先记录当前停点/.test(source['no-reliable-suggestion.html']), '无建议页有两条受控路径。');
check('restricted: offline boundary', /网络未使用/.test(source['restricted-offline.html']) && /不联网、不同步/.test(source['restricted-offline.html']), '离线页明确网络关闭。');
check('restricted: source boundary', /不读取来源、不处理内容，也不生成建议/.test(source['restricted-offline.html']), '受限页 fail-closed。');

const joined = Object.values(source).join('\n');
const forbidden = [
  /https?:\/\//i, /\bfetch\s*\(/i, /\bXMLHttpRequest\b/i, /\bWebSocket\b/i,
  /\blocalStorage\b/i, /\bsessionStorage\b/i, /\bindexedDB\b/i, /\bdocument\.cookie\b/i,
  /\bFileReader\b/i, /\bshowOpenFilePicker\b/i, /\bshowSaveFilePicker\b/i, /\bTauri\b/i,
  /\bipcRenderer\b/i, /\bexport\b/i, /\bsync\b/i, /\bmodel\b/i
];
for (const pattern of forbidden) check(`closed capability: ${pattern}`, !pattern.test(joined), '工程源码未出现禁止能力标识。');

const hashes = Object.fromEntries(await Promise.all(assets.map(async (file) => [file, createHash('sha256').update(source[file]).digest('hex')])));
const summary = { task: 'LIFEOS-P3-085', runner: basename(import.meta.url), pass: results.filter((item) => item.status === 'PASS').length, fail: results.filter((item) => item.status === 'FAIL').length, results, hashes };
console.log(JSON.stringify(summary, null, 2));
if (summary.fail) process.exitCode = 1;
