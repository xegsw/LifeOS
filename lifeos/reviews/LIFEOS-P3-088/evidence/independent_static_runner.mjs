#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.argv[2];
const outputAt = process.argv[3] === '--output' ? process.argv[4] : undefined;
if (!root) throw new Error('Usage: node independent_static_runner.mjs <task-local-app-dir>');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const files = Object.fromEntries(['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html', 'app.js', 'styles.css'].map((name) => [name, read(name)]));
const checks = [];
const check = (id, condition, detail) => checks.push({ id, status: condition ? 'PASS' : 'FAIL', detail });
const pages = ['default-recovery.html', 'no-reliable-suggestion.html', 'restricted-offline.html'];

for (const page of pages) {
  const html = files[page];
  check(`${page}:language`, /<html lang="zh-CN">/i.test(html), 'declares Chinese document language');
  check(`${page}:viewport`, /name="viewport" content="width=device-width, initial-scale=1"/.test(html), 'declares responsive viewport');
  check(`${page}:skip-link`, /class="skip-link" href="#main-content"/.test(html), 'provides keyboard skip link');
  check(`${page}:main-landmark`, /<main id="main-content"/.test(html), 'has main landmark matching skip link');
  check(`${page}:navigation`, /<nav class="page-nav" aria-label="今日状态导航">/.test(html), 'labels state navigation');
  check(`${page}:three-local-pages`, /href="default-recovery.html"/.test(html) && /href="no-reliable-suggestion.html"/.test(html) && /href="restricted-offline.html"/.test(html), 'only relative local page navigation');
  check(`${page}:boundary-copy`, /AI 未启用/.test(html) && /网络未使用/.test(html), 'states AI and network closed');
  check(`${page}:local-assets`, /href="styles.css"/.test(html) && /src="app.js"/.test(html), 'uses only local CSS and JS');
  check(`${page}:no-remote-url`, !/(?:https?:|\/\/)/i.test(html), 'contains no remote URL');
}

const defaultPage = files['default-recovery.html'];
check('default:semantic-heading-order', /<h1>今日<\/h1>[\s\S]*<h2 id="project-title">[\s\S]*<h3>/.test(defaultPage), 'uses h1 then h2 then h3 in main recovery content');
check('default:original-label', /你的记录／原文/.test(defaultPage), 'labels user-origin text');
check('default:explicit-confirmation', /确认保留在本次会话/.test(defaultPage), 'requires explicit confirmation');
check('default:live-status', /id="capture-status" role="status" aria-live="polite"/.test(defaultPage), 'announces interaction state');
check('default:no-autosave-attribute', !/autofocus|oninput|localStorage|sessionStorage/i.test(defaultPage), 'does not imply automatic or persistent capture');

const emptyPage = files['no-reliable-suggestion.html'];
check('empty:no-fabricated-suggestion', /暂无可靠建议/.test(emptyPage) && /不会虚构重点或建议/.test(emptyPage), 'fails closed when evidence is insufficient');
check('empty:two-controlled-paths', /id="choose-project"/.test(emptyPage) && /id="record-stop"/.test(emptyPage), 'offers two manual controlled paths');
check('empty:live-status', /id="no-suggestion-status" role="status" aria-live="polite"/.test(emptyPage), 'announces chosen path');

const restrictedPage = files['restricted-offline.html'];
check('restricted:fail-closed-copy', /不读取来源、不处理内容，也不生成建议/.test(restrictedPage), 'states restricted/offline fail-closed behavior');
check('restricted:no-network-sync', /不联网、不同步/.test(restrictedPage), 'states network and sync closed');

const js = files['app.js'];
check('script:empty-input-rejected', /if \(!value\) return clear\('未显示记录：请先输入原文，再明确确认。'\)/.test(js), 'rejects empty input');
check('script:confirmation-is-explicit', /confirm-save/.test(js) && /addEventListener\('click'/.test(js), 'confirmation is click-triggered');
check('script:failure-clears-record', /simulate-failure[\s\S]*clear\('模拟失败：本次会话未保留或显示原文/.test(js), 'simulated failure clears displayed record');
check('script:no-storage-or-network', !/(localStorage|sessionStorage|indexedDB|fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|FileReader|showOpenFilePicker|tauri|invoke\()/i.test(js), 'does not access storage, network, file, or Tauri APIs');
check('script:manual-empty-state-paths', /选择 Project 是受控路径/.test(js) && /先记录当前停点是受控路径/.test(js), 'two empty-state paths do not read material');

const css = files['styles.css'];
check('css:visible-focus', /:focus-visible[^{]*\{[^}]*outline:3px solid var\(--focus\)/.test(css), 'uses high-contrast visible focus outline');
check('css:skip-link-focus', /\.skip-link:focus \{ top:12px; \}/.test(css), 'reveals skip link on focus');
check('css:narrow-layout', /@media \(max-width:600px\)[\s\S]*grid-template-columns:1fr/.test(css), 'switches action and navigation layout on narrow screens');
check('css:readable-container', /width:min\(100% - 40px, 900px\)/.test(css), 'uses constrained readable layout');
check('css:reduced-motion', /prefers-reduced-motion:reduce/.test(css), 'honors reduced-motion preference');
check('css:no-remote-import', !/@import|url\(/i.test(css), 'contains no remote stylesheet or asset import');

for (const [name, content] of Object.entries(files)) {
  check(`closed:${name}`, !/(?:https?:|wss?:|localStorage|sessionStorage|indexedDB|fetch\(|XMLHttpRequest|WebSocket|FileReader|showOpenFilePicker|tauri|ipc|supabase|firebase|openai)/i.test(content), 'does not contain prohibited real-capability token');
}

const result = {
  runner: 'LIFEOS-P3-088 independent static runner',
  target: root,
  generated_at: new Date().toISOString(),
  counts: { pass: checks.filter((item) => item.status === 'PASS').length, fail: checks.filter((item) => item.status === 'FAIL').length },
  hashes: Object.fromEntries(Object.entries(files).map(([name, content]) => [name, crypto.createHash('sha256').update(content).digest('hex')])),
  checks,
};
const serialized = JSON.stringify(result, null, 2);
if (outputAt) fs.writeFileSync(outputAt, `${serialized}\n`);
console.log(serialized);
process.exitCode = result.counts.fail ? 1 : 0;
