# P3-084 验收标准 → 独立步骤／反例 → Evidence

| 任务卡验收标准 | 独立步骤／反例 | Evidence | 状态 |
|---|---|---|---|
| 当前 `index.html`、`app.js`、`styles.css` hash 与 P3-082 一致 | 原目录与干净副本逐项 SHA-256 比对 | `temp_copy_path.txt`、`independent_static_results.json` | Pass |
| 新写的独立静态验证实现 | 本任务 runner 仅读取三个副本源码；不导入、调用或复制 P3-082／083 runner | `independent_static_runner.mjs`、`independent_static_results.json` | Pass |
| 三态、确认、空文本、失败、无建议两路径、权限／离线的可执行动态验证 | 新图形浏览器 `file:` 导航后执行；导航在页面加载前被策略拒绝 | `browser_blocker.md`、`operation_log.md` | Not Implemented |
| 刷新、关闭重开后文本／记录／状态清除 | 依赖已加载页面的动态步骤；未尝试替代路径 | `browser_blocker.md` | Not Implemented |
| 视觉层级与三态截图 | 依赖已加载页面；无页面截图可诚实生成 | `browser_blocker.md` | Not Implemented |
| 无网络、持久化、文件 API、Tauri/IPC、Vault、导出、同步、模型调用 | 独立静态扫描负面标记，且浏览器阻断后未执行任何替代 | `independent_static_results.json`、`operation_log.md` | Pass（静态） |

未适用：持久化原子失败、半成品清理与审计耐久性；本 UI 能力包没有持久化、文件或 DB 写入。模拟失败隐藏记录的动态行为因浏览器阻断未验证，计入同一 Not Implemented 项。
