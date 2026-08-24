import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

const root = process.argv[2] || new URL('..', import.meta.url).pathname;
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];
const required = ['styles.css', 'app.js'];
const results = [];
const check = (id, pass, detail) => results.push({ id, pass, detail });
const files = Object.fromEntries(await Promise.all([...pages, ...required].map(async f => [f, await readFile(join(root, f), 'utf8')])));
for (const page of pages) { const html = files[page]; check(`${page}:doctype`, /<!doctype html>/i.test(html), 'HTML document'); check(`${page}:lang`, /<html lang="zh-CN">/.test(html), 'Chinese language'); check(`${page}:viewport`, /name="viewport"/.test(html), 'responsive viewport'); check(`${page}:main`, /<main id="main-content"/.test(html), 'main landmark'); check(`${page}:skip`, /class="skip-link" href="#main-content"/.test(html), 'skip link'); check(`${page}:nav`, /<nav class="page-nav" aria-label=/.test(html), 'labelled navigation'); check(`${page}:local-assets`, !/https?:\/\//i.test(html), 'no remote URL'); }
for (const page of pages) { for (const target of pages) check(`${page}:nav:${target}`, files[page].includes(`href="${target}"`), 'relative local navigation'); }
check('one-current-page-per-page', pages.every(page => (files[page].match(/aria-current="page"/g) || []).length === 1), 'one current navigation state');
check('default:semantic-headings', /<h1>/.test(files[pages[0]]) && /<h2/.test(files[pages[0]]) && /<h3>/.test(files[pages[0]]), 'heading hierarchy');
check('default:keyboard-controls', /<textarea id="capture-text"/.test(files[pages[0]]) && /<button type="button" id="confirm-save"/.test(files[pages[0]]), 'native keyboard controls');
check('default:status-live', /role="status" aria-live="polite"/.test(files[pages[0]]), 'status announcement');
check('empty:controlled-paths', /id="choose-project"/.test(files[pages[1]]) && /id="record-stop"/.test(files[pages[1]]), 'two controlled paths');
check('restricted:fail-closed', /不联网、不同步/.test(files[pages[2]]) && /不读取来源、不处理内容，也不生成建议/.test(files[pages[2]]), 'offline restriction');
for (const phrase of ['AI 未启用', '网络未使用']) check(`state:${phrase}`, pages.every(p => files[p].includes(phrase)), 'closed state text');
for (const forbidden of ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'FileReader', 'showOpenFilePicker', 'tauri', 'ipc', 'WebSocket', 'export', 'sync', 'model']) check(`closed:${forbidden}`, !Object.values(files).join('\n').toLowerCase().includes(forbidden.toLowerCase()), 'forbidden capability absent');
const css = files['styles.css']; check('css:visible-focus', /:focus-visible/.test(css) && /outline:3px/.test(css), 'visible focus'); check('css:mobile-layout', /@media \(max-width:600px\)/.test(css), 'narrow layout'); check('css:reduced-motion', /prefers-reduced-motion:reduce/.test(css), 'motion reduction'); check('css:no-horizontal-overflow', /width:min\(100% - 40px/.test(css), 'fluid container');
const js = files['app.js']; check('js:no-persistence', !/localStorage|sessionStorage|indexedDB|cookie/i.test(js), 'no browser persistence'); check('js:empty-rejected', /if \(!value\)/.test(js), 'empty input rejected'); check('js:explicit-confirmation', /confirm-save/.test(js) && /已确认/.test(js), 'explicit confirmation'); check('js:failure-clears', /record\.hidden = true/.test(js) && /模拟失败/.test(js), 'failure clears partial display');
const forbiddenPaths = ['node_modules', 'package.json']; const entries = await readdir(root); check('no-third-party-dependency', forbiddenPaths.every(x => !entries.includes(x)), 'no dependencies');
const hashes = Object.fromEntries(Object.entries(files).map(([name, content]) => [name, createHash('sha256').update(content).digest('hex')]));
const payload = { generatedAt: new Date().toISOString(), root, pass: results.filter(x => x.pass).length, fail: results.filter(x => !x.pass).length, results, hashes };
console.log(JSON.stringify(payload, null, 2)); process.exitCode = payload.fail ? 1 : 0;
