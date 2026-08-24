# 验收标准 → 测试 → Evidence 矩阵

| 任务卡验收项 | 测试／演练 | 当前结果 | Evidence |
|---|---|---|---|
| 三个独立页面可 `file:` 打开并相互导航 | 三份独立 HTML 的相对链接静态核验；动态 `file:` 点击演练 | 静态 Pass；动态 Not Implemented | `static_check_results.json`；`browser_blocker.md` |
| 保留“今日从哪里继续”主叙事 | 默认恢复页文本和语义结构核验 | Pass | `static_check_results.json` |
| 无建议时不虚构建议，保留两条受控路径 | 无建议页文本、按钮与 AI 关闭态核验 | Pass | `static_check_results.json` |
| 受限／离线时 AI 未启用、网络未使用 | 受限页文字与禁止能力扫描 | Pass | `static_check_results.json` |
| 空文本拒绝、显式确认后显示、模拟失败不显示记录 | 脚本逻辑静态核验；浏览器交互演练 | 静态 Pass；动态 Not Implemented | `static_check_results.json`；`browser_blocker.md` |
| 重复确认、刷新和关闭重开清除 | 脚本不含持久化 API；浏览器交互演练 | 静态 Pass；动态 Not Implemented | `static_check_results.json`；`browser_blocker.md` |
| 禁止的真实能力保持关闭 | 远程 URL、网络、浏览器持久化、文件 API、Tauri/IPC、导出、同步、模型标识扫描 | Pass | `static_check_results.json` |
| P3-082／084 历史只读资产未覆盖 | SHA-256 复算 | Pass | `MANIFEST.md` |
| runner、结果、日志、hash、Manifest、复跑说明可复核 | 本工程独立 runner 与本 Evidence 链 | Partial：动态视觉记录缺失且已披露 | `tests/static_check.mjs`；本目录所有文件 |
