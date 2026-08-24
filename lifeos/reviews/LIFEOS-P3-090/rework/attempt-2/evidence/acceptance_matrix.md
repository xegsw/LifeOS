# P3-090 attempt-2 验收标准 → 独立步骤 → Evidence

| 任务卡标准 | 独立反例／步骤 | Evidence | 结果 |
|---|---|---|---|
| 五项工程与三项历史只读 hash | SHA-256 before／after 与指定历史复算 | `independent_static_results.json` | PASS |
| 合成／真实能力边界与关闭态 | 新写 runner 扫描资源、状态文案及禁止能力 | `independent_static_results.json` | PASS |
| Chrome file: 预检 | 新 Chrome 标签页直开 task-local 入口 | `01-preflight-wide.jpeg`、`dynamic_results.json` | PASS |
| 默认拒绝、确认、grant、精确 CONFIRM、重复回执、撤回 | Chrome 实操 | `03-confirmed-recovery.jpeg`、`04-revoked-cleared.jpeg`、`11-repeat-confirmation.jpeg` | PASS |
| 失败清理与披露 | Chrome 模拟失败 | `05-failure-cleared.jpeg` | PASS |
| 三页关闭态与本地导航 | Chrome 本地链接导航 | `06-no-suggestion.jpeg`、`07-restricted-offline.jpeg` | PASS |
| skip link／焦点／缩放 | Tab、Chrome 缩放和独立 CSS 检查 | `02-keyboard-focus.jpeg`、`09-zoom-responsive.jpeg`、`independent_static_results.json` | PASS |
| 刷新／关闭重开清除 | Chrome refresh、关闭 task-local 标签后新标签重开 | `08-refresh-cleared.jpeg`、`10-close-reopen-cleared.jpeg` | PASS |
| 逐文件 hash、runner、结果、日志与 Manifest | task-local Evidence 完整性核验 | `MANIFEST.md` | PASS |
