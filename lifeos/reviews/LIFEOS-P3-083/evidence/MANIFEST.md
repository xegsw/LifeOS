# LIFEOS-P3-083 独立 Evidence Manifest

## 范围与独立性

- 新建隔离独立评审会话；未复用 P3-082 工程执行、P3-082 PM 验收、P3-079／080 或 P3-081 会话。
- 只读核验 P3-082 工程与历史 Evidence；只在本目录和 task-local 临时副本写入。
- 独立 runner 是本任务新写的 `independent_static_runner.mjs`；未导入、调用或复制 P3-082 的 `tests/static_check.mjs`。两者 SHA-256 分别为 `1f2c7ab2b7069abd2df7378a8bb22ba167831fb310bd0dc946b3d8e705f08ae4` 与 `08b8b22aa3d6c9fc7397863fe1e4e5bf202793dd8f2f69c0ae084e153e019778`。

## 被评审 hash

| 文件 | SHA-256 | 结论 |
|---|---|---|
| `index.html` | `eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722` | 与 P3-082 Manifest 一致 |
| `app.js` | `784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d` | 与 P3-082 Manifest 一致 |
| `styles.css` | `7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2` | 与 P3-082 Manifest 一致 |

## Evidence 与复跑

| Evidence | 说明 |
|---|---|
| `independent_static_runner.mjs` | 新的独立静态 runner |
| `independent_static_results.json` | 8 PASS / 0 FAIL 的逐项结构化结果 |
| `browser_blocker.md` | `file:` 独立动态验证被安全策略阻断的失败披露 |

从工作区根目录复跑静态检查：

```sh
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node lifeos/reviews/LIFEOS-P3-083/evidence/independent_static_runner.mjs /private/tmp/lifeos-p3-083.JwJ6Fn
```

临时副本会随本机临时目录策略清理；重跑时须重新创建干净副本、核对上述 hash，不得改用 HTTP 服务或持久化浏览器状态。

## 验收标准 → 反例 → Evidence

| 验收标准 | 独立反例／检查 | Evidence | 状态 |
|---|---|---|---|
| 三态与身份层级 | 状态控件、AI 关闭、用户确认行动、无建议缺口的独立静态断言 | `independent_static_results.json` | Pass（静态） |
| 显式确认、空文本和失败不伪报 | 空值分支、失败隐藏记录的独立静态断言 | `independent_static_results.json` | Pass（静态） |
| 无建议两条受控路径；权限／离线分述 | 独立静态断言 | `independent_static_results.json` | Pass（静态） |
| 禁止能力关闭 | 存储、远程 URL、网络、Tauri/IPC、文件、导出标记独立扫描 | `independent_static_results.json` | Pass（静态） |
| 新会话 `file:` 动态三态、刷新与视觉 | 浏览器拒绝导航；不绕过 | `browser_blocker.md` | Not Implemented |
