# P3-132 Closure Cycle｜actual Tauri 动态 Evidence 闭环

本表只补足 PM Review 指定的 CL-01／CL-02。所有动作均在本任务唯一临时根的直接子目录完成，使用本任务候选构建的 native Tauri bundle；SQLite/audit 快照在清理前以只读方式保留到工程 Evidence。

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| CL-01-a | 新鲜 `closure-cl01-insufficient`；实际窗口点击“记录证据不足原文” | 当前 Capture 标题为不足原文；实际 receipt 为 `unlinked_insufficient`；Capture identity 为 `user_original` | `closure-cl01-before-second-reopen.json` | `actual-runs/screenshots/closure-cl01-insufficient-reopen.jpeg`；`actual-runs/closure-ui-observations.json` | `bd86a50dc221b017792d5e710b0c4963ebe8050f754844de52da0a73af86273c` | PASS |  |
| CL-01-b | 关闭并重开同一 actual App | 仍显示同一不足 Capture，`Project link: none · evidence insufficient`；没有 `typed link: candidate`；零 Link／Derivation／Understanding／Feedback／Action | `closure-cl01-after-second-reopen.json` | `actual-runs/screenshots/closure-cl01-insufficient-reopen-verified.jpeg`；`actual-runs/closure-ui-observations.json` | `b095ef6751daaa3aecd45167d50226982939405361bd101439b1b45f112fbe01` | PASS |  |
| CL-02-a | 新鲜 `closure-cl02-multi`；固定夹具逆序插入 3 条开放已确认 Action，其中 `tie-a`／`tie-z` 均为 `confirmed_at=7000` | actual UI 显示 3 条开放 Action，按 `confirmed_at / action_id` 排为 `tie-a`、`tie-z`、`newer`，Focus 为 `tie-a` | `closure-cl02-multi-start.json`；`closure-cl02-fixture.json` | `actual-runs/screenshots/closure-cl02-multi-start.jpeg`；`actual-runs/closure-ui-observations.json` | `a31d11441e37d687976b4a3327eeb99607c363380f4f65a9e04d93b4dd78fc98` | PASS |  |
| CL-02-b | 在同一 actual App 点击“刷新” | Focus 与 3 条稳定顺序不变；SQLite/audit SHA-256 不变 | `closure-cl02-multi-refresh.json` | `actual-runs/screenshots/closure-cl02-multi-refresh.jpeg`；`actual-runs/closure-ui-observations.json` | `ea37c022293225b15759551fcd46d14adac1407227229c1cd4bf342513d9c3f2` | PASS |  |
| CL-02-c | 关闭并重开同一 actual App | Focus 仍为 `action:p3-131:fixture-tie-a`，显示顺序不变，SQLite/audit SHA-256 仍为 `17c3fe…4257` | `closure-cl02-multi-reopen.json` | `actual-runs/screenshots/closure-cl02-multi-reopen.jpeg`；`actual-runs/closure-ui-observations.json` | `8586844a3e6152782f60d9570eeaa2c94d0eee1377ee91a1fc318b531ef6537d` | PASS |  |

`closure-ui-observations.json` 绑定每张实际截图、同 run SQLite/audit JSON、Bundle identity 与可见状态；`verification.json` 对这些路径、哈希、行数、逆序插入、稳定排序和清理结果做结构化检查，不从本 Markdown 的 `PASS` 文字推导结论。
