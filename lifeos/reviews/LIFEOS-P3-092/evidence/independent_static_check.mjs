import { readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join, resolve } from 'node:path';

const root = resolve(process.argv[2] || '/private/tmp/lifeos-p3-092-XpxwaB/app');
const output = resolve(process.argv[3] || join(process.cwd(), 'lifeos/reviews/LIFEOS-P3-092/evidence/independent_static_results.json'));
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];
const sourceFiles = [...pages, 'styles.css', 'app.js'];
const contents = Object.fromEntries(await Promise.all(sourceFiles.map(async (file) => [file, await readFile(join(root, file), 'utf8')])));
const tests = [];
const check = (id, condition, detail) => tests.push({ id, pass: Boolean(condition), detail });

for (const page of pages) {
  const html = contents[page];
  check(`${page}:identity-boundary`, html.includes('内容身份与处理边界'), 'visible identity/boundary heading');
  check(`${page}:synthetic-demo`, html.includes('固定非敏感演示文本'), 'fixed non-sensitive demo content is labelled');
  check(`${page}:explicit-confirmation`, html.includes('用户明确确认动作'), 'explicit user-confirmation label');
  check(`${page}:synthetic-state`, html.includes('合成系统状态'), 'synthetic-state label');
  check(`${page}:ai-disabled`, html.includes('AI 未启用'), 'AI disabled disclosure');
  check(`${page}:no-real-processing`, html.includes('未发生真实保存、授权、恢复或处理') || html.includes('不读取资料、不保存输入、不生成建议'), 'real processing is not claimed');
  check(`${page}:accessible-navigation`, html.includes('aria-label="今日状态导航"') && html.includes('href="#main-content"'), 'labelled navigation and skip link');
  check(`${page}:local-assets`, !/https?:\/\//i.test(html) && html.includes('styles.css') && html.includes('app.js'), 'no remote URL; only relative local assets');
}

const allSource = Object.values(contents).join('\n');
for (const forbidden of ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'FileReader', 'showOpenFilePicker', 'tauri', 'ipc', 'WebSocket', 'sqlite', 'FileSystem', 'navigator.sendBeacon', 'export ', 'sync(']) {
  check(`closed:${forbidden}`, !allSource.includes(forbidden), 'forbidden real capability absent');
}
check('css:responsive', contents['styles.css'].includes('@media (max-width:600px)'), 'narrow-screen rule exists');
check('css:reduced-motion', contents['styles.css'].includes('prefers-reduced-motion:reduce'), 'reduced-motion rule exists');
check('css:visible-focus', contents['styles.css'].includes(':focus-visible') && contents['styles.css'].includes('outline:3px'), 'visible focus rule exists');
check('js:default-deny', contents['app.js'].includes("permission: '默认拒绝'"), 'default permission is deny');
check('js:exact-confirm', contents['app.js'].includes("!== 'CONFIRM'"), 'restore requires exact CONFIRM');
check('js:clear-display', contents['app.js'].includes('clearDisplay') && contents['app.js'].includes('半成品显示状态已清理'), 'failure cleanup clears display state');

const hashes = Object.fromEntries(await Promise.all(sourceFiles.map(async (file) => {
  const data = await readFile(join(root, file));
  return [file, createHash('sha256').update(data).digest('hex')];
})));
const unexpected = (await readdir(root)).filter((name) => !['README.md', 'app.js', 'default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html', 'styles.css', 'evidence', 'tests'].includes(name));
check('no-unexpected-root-files', unexpected.length === 0, `unexpected root entries: ${unexpected.join(', ') || 'none'}`);

const result = { generatedAt: new Date().toISOString(), runner: 'P3-092 independent static runner', root, pass: tests.filter((item) => item.pass).length, fail: tests.filter((item) => !item.pass).length, tests, hashes };
await writeFile(output, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.fail ? 1 : 0;
