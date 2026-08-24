import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(process.argv[2] ?? '.');
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];
const assets = [...pages, 'app.js', 'styles.css'];
const results = [];
const check = (id, condition, detail) => results.push({ id, status: condition ? 'PASS' : 'FAIL', detail });
const source = Object.fromEntries(await Promise.all(assets.map(async (file) => [file, await readFile(resolve(root, file), 'utf8')])));

for (const page of pages) {
  const text = source[page];
  check(`${page}:standalone`, /<!doctype html>/i.test(text) && /<main class="shell">/.test(text), '可独立作为本地 HTML 文档打开。');
  check(`${page}:relative-assets`, /href="styles\.css"/.test(text) && /src="app\.js"/.test(text), '仅引用相对本地 CSS 与 JavaScript。');
  check(`${page}:explicit-navigation`, pages.every((target) => text.includes(`href="${target}"`)), '三页均呈现通向另两页的显式本地导航。');
  check(`${page}:ai-closed`, text.includes('AI 未启用'), '每页显式披露 AI 未启用。');
}

const defaultPage = source['default-recovery.html'];
const emptyPage = source['no-reliable-suggestion.html'];
const restrictedPage = source['restricted-offline.html'];
const script = source['app.js'];
check('default:recovery-priority', /当前 Project/.test(defaultPage) && /从这里继续/.test(defaultPage) && /今日安排/.test(defaultPage), '默认页保留项目恢复到已确认行动的叙事。');
check('default:explicit-confirmation', /确认保留在本次会话/.test(defaultPage) && /你的记录／原文/.test(defaultPage), '手动文本以用户原文身份呈现且需明确确认。');
check('default:empty-rejected', /if \(!value\)/.test(script) && /请先输入原文，再明确确认/.test(script), '空文本确认被拒绝并有可见说明。');
check('default:failure-clears', /simulate-failure/.test(script) && /未保留或显示原文/.test(script) && /savedRecord\.hidden = true/.test(script), '模拟失败清除显示记录并披露未保留。');
check('empty:no-invention', /暂无可靠建议/.test(emptyPage) && /不会据最近痕迹生成恢复或建议/.test(emptyPage), '无建议页不虚构重点或建议。');
check('empty:two-controlled-paths', /选择 Project/.test(emptyPage) && /先记录当前停点/.test(emptyPage), '无建议页仅呈现两条人工受控路径。');
check('restricted:fail-closed', /网络未使用/.test(restrictedPage) && /不联网、不同步/.test(restrictedPage) && /不读取来源、不处理内容，也不生成建议/.test(restrictedPage), '受限／离线页明确关闭处理与建议。');

const joined = Object.values(source).join('\n');
const forbidden = [
  ['network-url', /https?:\/\//i], ['fetch', /\bfetch\s*\(/i], ['xhr', /\bXMLHttpRequest\b/i], ['websocket', /\bWebSocket\b/i],
  ['persistence', /\b(localStorage|sessionStorage|indexedDB|document\.cookie)\b/i], ['file-api', /\b(FileReader|showOpenFilePicker|showSaveFilePicker)\b/i],
  ['tauri-ipc', /\b(Tauri|ipcRenderer)\b/i], ['export', /\bexport\b/i], ['sync', /\bsync\b/i], ['model', /\bmodel\b/i]
];
for (const [id, pattern] of forbidden) check(`closed:${id}`, !pattern.test(joined), '受控工程源码未出现该禁止能力标识。');

const hashes = Object.fromEntries(assets.map((file) => [file, createHash('sha256').update(source[file]).digest('hex')]));
const output = { task: 'LIFEOS-P3-086', kind: 'independent-static', root, pass: results.filter((item) => item.status === 'PASS').length, fail: results.filter((item) => item.status === 'FAIL').length, results, hashes };
console.log(JSON.stringify(output, null, 2));
if (output.fail) process.exitCode = 1;
