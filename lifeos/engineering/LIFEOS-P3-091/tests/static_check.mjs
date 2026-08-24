import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

const root = process.argv[2] || new URL('..', import.meta.url).pathname;
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];
const required = [...pages, 'styles.css', 'app.js'];
const results = [];
const check = (id, pass, detail) => results.push({ id, pass, detail });
const files = Object.fromEntries(await Promise.all(required.map(async file => [file, await readFile(join(root, file), 'utf8')])));
const all = Object.values(files).join('\n');
for (const page of pages) {
  const html = files[page];
  for (const [id, pattern, detail] of [
    ['doctype', /<!doctype html>/i, 'HTML document'], ['language', /<html lang="zh-CN">/, 'Chinese language'], ['viewport', /name="viewport"/, 'responsive viewport'], ['skip-link', /class="skip-link" href="#main-content"/, 'skip link'], ['main', /<main id="main-content"/, 'main landmark'], ['navigation', /<nav class="page-nav" aria-label=/, 'labelled navigation'], ['synthetic-label', /合成生命周期演示/, 'synthetic label'], ['identity-boundary', /内容身份与处理边界/, 'identity boundary'], ['demo-text', /固定非敏感演示文本/, 'demo text identity'], ['confirm-action', /用户明确确认动作/, 'confirmation identity'], ['synthetic-state', /合成系统状态/, 'state identity'], ['ai-off', /AI 未启用/, 'AI disabled'], ['no-real-processing', /未发生真实保存、授权、恢复或处理|未发生任何真实处理/, 'real processing disclosure'], ['relative-assets', /href="styles.css"/.test(html) && /src="app.js"/.test(html), 'relative local assets'], ['no-remote-url', !/https?:\/\//i.test(html), 'no remote URL']
  ]) check(`${page}:${id}`, pattern instanceof RegExp ? pattern.test(html) : pattern, detail);
  for (const target of pages) check(`${page}:nav:${target}`, html.includes(`href="${target}"`), 'relative navigation target');
}
check('one-current-page', pages.every(page => (files[page].match(/aria-current="page"/g) || []).length === 1), 'exactly one current page');
const primary = files['default-recovery.html'];
for (const marker of ['confirm-capture', 'simulate-failure', 'grant', 'revoke', 'prepare-restore', 'confirm-restore', 'restore-confirmation']) check(`default:${marker}`, primary.includes(marker), 'lifecycle control');
check('default:live-status', (primary.match(/role="status" aria-live="polite"/g) || []).length >= 2, 'live status disclosures');
check('empty:no-fabricated-suggestion', /暂无可靠建议/.test(files[pages[1]]) && /不会据最近痕迹生成恢复或建议/.test(files[pages[1]]), 'no fabricated suggestion');
check('restricted:fail-closed', /默认拒绝且离线/.test(files[pages[2]]) && /不读取来源、不处理内容，也不生成建议/.test(files[pages[2]]), 'restricted closed state');
const js = files['app.js'];
for (const marker of ['if (!value)', '重复确认：幂等回执', '明确 grant', '已撤回／拒绝', 'if (!state.restorePreview)', "!== 'CONFIRM'", '重复 CONFIRM：幂等回执', '半成品显示状态已清理', '未保存、未授权、未恢复或处理任何真实内容']) check(`js:${marker}`, js.includes(marker), 'lifecycle behaviour');
for (const forbidden of ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'FileReader', 'showOpenFilePicker', 'tauri', 'ipc', 'WebSocket', 'sqlite', 'FileSystem', 'navigator.sendBeacon', 'export ', 'sync(']) check(`closed:${forbidden}`, !all.toLowerCase().includes(forbidden.toLowerCase()), 'forbidden capability absent');
const css = files['styles.css'];
for (const marker of [':focus-visible', 'outline:3px', '@media (max-width:600px)', 'prefers-reduced-motion:reduce', 'width:min(100% - 40px', 'identity-boundary']) check(`css:${marker}`, css.includes(marker), 'accessibility or responsive styling');
const entries = await readdir(root);
check('no-third-party-dependency', !entries.includes('node_modules') && !entries.includes('package.json'), 'no third-party dependency');
const hashes = Object.fromEntries(Object.entries(files).map(([file, content]) => [file, createHash('sha256').update(content).digest('hex')]));
const payload = { generatedAt: new Date().toISOString(), root, pass:results.filter(r=>r.pass).length, fail:results.filter(r=>!r.pass).length, results, hashes };
console.log(JSON.stringify(payload, null, 2));
process.exitCode = payload.fail ? 1 : 0;
