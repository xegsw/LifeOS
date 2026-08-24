import { readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';

const root = new URL('../', import.meta.url);
const files = ['index.html', 'styles.css', 'app.js'];
const source = Object.fromEntries(files.map((file) => [file, readFileSync(new URL(file, root), 'utf8')]));
const joined = Object.values(source).join('\n');
const required = ['默认恢复态', '暂无可靠建议', '权限受限 · 离线', 'AI 未启用', '你的记录／原文', '今日安排', '选择 Project', '先记录当前停点', '刷新或关闭后'];
const forbidden = [/https?:\/\//i, /fetch\s*\(/i, /XMLHttpRequest/i, /WebSocket/i, /Tauri/i, /\bipc\b/i, /FileReader/i, /showOpenFilePicker/i, /localStorage/i, /indexedDB/i, /document\.cookie/i, /export/i, /sync/i, /model\s*call/i];
const results = [];
const check = (name, pass, detail) => results.push({ name, pass, detail });
required.forEach((term) => check(`required:${term}`, joined.includes(term), 'required UI boundary text'));
forbidden.forEach((pattern) => check(`forbidden:${pattern}`, !pattern.test(joined), 'static closed boundary'));
check('no-dependencies', !existsSync(new URL('package.json', root)), 'runs with browser file: open only');
const hashes = Object.fromEntries(files.map((file) => [file, createHash('sha256').update(source[file]).digest('hex')]));
console.log(JSON.stringify({ passed: results.filter((r) => r.pass).length, failed: results.filter((r) => !r.pass).length, results, hashes }, null, 2));
if (results.some((r) => !r.pass)) process.exit(1);
