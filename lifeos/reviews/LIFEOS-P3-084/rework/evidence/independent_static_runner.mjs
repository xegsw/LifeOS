import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = process.argv[2];
if (!root) throw new Error('usage: node independent_static_runner.mjs <clean-copy-dir>');

const [html, js, css] = await Promise.all([
  readFile(resolve(root, 'index.html'), 'utf8'),
  readFile(resolve(root, 'app.js'), 'utf8'),
  readFile(resolve(root, 'styles.css'), 'utf8'),
]);

const cases = [
  ['three-state buttons exist', ['data-state="recovery"', 'data-state="no-suggestion"', 'data-state="restricted"'].every((s) => html.includes(s))],
  ['state switcher updates visibility and aria state', js.includes('function selectState') && js.includes("state.hidden = state.id !== id") && js.includes("button.setAttribute('aria-pressed'" )],
  ['nonempty capture needs explicit confirmation', html.includes('id="confirm-save"') && js.includes("document.querySelector('#confirm-save').addEventListener")],
  ['empty capture is rejected', js.includes('未保存：请输入原文后再显式确认。')],
  ['confirmed capture identifies user original text', html.includes('你的记录／原文') && js.includes('savedText.textContent = value')],
  ['simulated failure hides record', js.includes("document.querySelector('#simulate-failure')") && js.includes('record.hidden = true') && js.includes('保存失败：本次会话未保留原文')],
  ['no-suggestion has choose-project path', html.includes('id="choose-project"') && js.includes('选择 Project 是受控路径')],
  ['no-suggestion has record-stop path', html.includes('id="record-stop"') && js.includes('先记录当前停点是受控路径')],
  ['restricted state discloses offline boundary', html.includes('权限受限 · 离线') && html.includes('网络未使用；本页不联网、不同步')],
  ['AI is explicitly disabled in every state', (html.match(/AI 未启用/g) || []).length >= 3],
  ['session-only and refresh-close clearing are disclosed', html.includes('仅当前浏览器页面会话') && html.includes('刷新或关闭后手动内容会丢弃')],
  ['no remote URLs', !/https?:\/\//i.test(html + js + css)],
  ['no network APIs', !/\b(fetch|XMLHttpRequest|WebSocket|EventSource)\b/.test(js)],
  ['no browser persistence APIs', !/\b(localStorage|sessionStorage|indexedDB|document\.cookie)\b/.test(html + js)],
  ['no file or native bridge APIs', !/\b(FileReader|showOpenFilePicker|showSaveFilePicker|window\.open|__TAURI__|invoke)\b/.test(html + js)],
  ['no export, sync, vault, or model call markers', !/\b(export|sync|vault|model|OpenAI|Anthropic)\b/i.test(html + js)],
];

const results = cases.map(([name, pass], index) => ({ id: `STATIC-${String(index + 1).padStart(2, '0')}`, name, status: pass ? 'PASS' : 'FAIL' }));
console.log(JSON.stringify({ runner: 'P3-084 rework independent static runner', summary: { pass: results.filter((r) => r.status === 'PASS').length, fail: results.filter((r) => r.status === 'FAIL').length }, results }, null, 2));
process.exitCode = results.some((r) => r.status === 'FAIL') ? 1 : 0;
