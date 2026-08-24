# LIFEOS-P3-088 验收标准 → 独立步骤 → Evidence

| 验收标准 | 独立步骤／反例 | Evidence | 结果 |
|---|---|---|---|
| 当前 hash 与副本、P3-085 历史只读 hash 一致 | SHA-256 before／after 复算 | `hashes.txt`、`MANIFEST.md` | Pass |
| 三页语义、相对资源、响应式与可见焦点 | 独立静态 runner 53 项 | `independent_static_runner.mjs`、`independent_static_results.json` | Pass |
| Chrome `file:` 预检后才做动态矩阵 | 新标签页打开 default page | `01-preflight-wide.jpeg`、操作日志 | Pass |
| 键盘 skip／Tab／Enter 三页导航 | 从文档起点 Tab、Enter | `02-keyboard-focus.jpeg`、`dynamic_results.json` DYN-02..04 | Pass |
| 空输入拒绝、显式／重复确认 | 空输入与两次确认 | `04-confirmed.jpeg`、DYN-05..07 | Pass |
| 原子失败、半成品清理与失败披露 | 模拟失败后检查显示记录与状态 | `05-failure-disclosure.jpeg`、DYN-08 | Pass |
| 刷新与关闭重开清除 | reload，关闭标签后新标签重开 | `08-close-reopen-cleared.jpeg`、DYN-09..10 | Pass |
| 窄屏／缩放可读性 | Chrome 增加缩放并作视觉检查 | `06-zoom-responsive.jpeg`、DYN-11 | Pass |
| 无可靠建议与受限离线 fail-closed | 两条人工路径、第三页 | `03-no-suggestion.jpeg`、`07-restricted-offline.jpeg`、DYN-03..04/12 | Pass |
| 禁止能力维持关闭 | 静态 token 扫描、动态 task-local URL 核对 | 静态结果关闭态项、DYN-13 | Pass |
