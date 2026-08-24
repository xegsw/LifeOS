# P3-082 验收标准 → 测试 → Evidence

| 任务卡验收标准 | 测试／演练 | Evidence | 状态 |
|---|---|---|---|
| 三态可见切换且不混淆 | 源码检查状态 ID、切换按钮与标签；浏览器点击待复跑 | `tests/static_check.mjs`、`static_check_results.json` | Partial |
| 显式确认后才显示原文；空／失败不虚报保存 | 源码检查 `confirm-save`、空文本、模拟失败分支；浏览器交互待复跑 | `app.js`、`static_check_results.json` | Partial |
| 今日安排仅用户已确认；AI 关闭 | 静态必需文案检查 | `static_check_results.json` | Pass（静态） |
| 无可靠建议态缺口与两条受控路径 | 静态必需文案检查；浏览器点击待复跑 | `index.html`、`static_check_results.json` | Partial |
| 权限／离线分别说明并保留用户确认内容 | 静态必需文案检查；浏览器切换待复跑 | `index.html`、`static_check_results.json` | Partial |
| 干净浏览器首次、重复、关闭重启、刷新清除、截图／日志 | 受控 `file:` 浏览器演练 | `browser_blocker.md` | Not Implemented（浏览器策略阻断） |
| 禁止能力静态关闭 | 13 个禁止标记的静态扫描 | `static_check_results.json` | Pass |

未适用：原子持久化、半成品清理与审计追溯。本包不持久化、不写文件／DB；失败时只显示失败且不展示记录。该不适用结论仍需在可执行浏览器演练中确认。
