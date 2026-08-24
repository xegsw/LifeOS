# P3-087 验收标准 → 测试 → Evidence

| 验收标准 | 测试 | Evidence | 结果 |
|---|---|---|---|
| 三页可独立本地打开、无自动导航 | 静态相对链接检查；Chrome 新标签预检 | `static_results.json`、`01-preflight-wide.png` | PASS |
| 语义 landmark、标题、可见焦点、合理 Tab 顺序 | 静态检查；Chrome Tab 焦点与 Enter 导航 | `static_results.json`、`02-keyboard-no-suggestion.png` | PASS |
| 默认、无建议、受限离线三态和关闭态保留 | 静态文案检查；Chrome 状态导航 | `static_results.json`、`02-keyboard-no-suggestion.png`、`03-keyboard-controlled-path.png` | PASS |
| 确认、重复和原子失败清理 | Chrome 受控非敏感输入、两次确认与失败按钮 | `04-confirmed.png`、`05-failure-cleared.png`、`dynamic_results.json` | PASS |
| 刷新／关闭重开清除 | Chrome reload、关闭任务标签并新建标签重开 | `08-refresh-cleared.png`、`09-close-reopen-cleared.png` | PASS |
| 宽／窄屏可阅读且边界未丢失 | 宽屏与 150%/200% 缩放视觉记录 | `01-preflight-wide.png`、`06-narrow-responsive.png`、`07-extra-narrow-responsive.png` | PASS |
| 禁止能力与真实边界静态关闭 | runner 扫描网络、持久化、文件 API、DB、Tauri/IPC、导出、同步、模型、第三方依赖 | `static_results.json` | PASS |
| 历史 P3-085／086 未覆盖 | SHA-256 与 P3-086 attempt-3 Manifest 比对 | `MANIFEST.md` | PASS |
