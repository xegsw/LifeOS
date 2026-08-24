# P3-092 动态 Evidence 闭环表（attempt-2）

| 验收项 ID | 实际操作与前置状态 | 可观察结果 | 结构化结果 ID | 视觉 Evidence | SHA-256 | 状态 |
|---|---|---|---|---|---|---|
| D-01 | 新 Chrome 标签页打开 task-local `file:` 入口 | 默认恢复页、身份边界与 AI 未启用可见 | D-01 | `01-preflight.jpeg` | `ad7bb860324db8f30093130e2b62631400856e39d7a7d4e33f7da68d44bc5be6` | PASS |
| D-02 | 空输入点击“明确确认本次显示” | 页面保持默认拒绝，不显示记录 | D-02 | `02-empty-deny.jpeg` | `2b17bb1289ba91a86b5ab8bd5dccf231799881446e9af8f61e9e661b4bd78c3a` | PASS |
| D-03 | 填入固定非敏感文本后确认 | 仅当前页面会话显示已确认文本 | D-03 | `03-confirmed.jpeg` | `ed2a336b643a90b5557165eaf82fd0c6901cf8a9ce9ade2c52de8f4355ffbd6b` | PASS |
| D-04 | 重复确认 | 幂等回执、无新增记录 | D-04 | `04-repeat.jpeg` | 见 `all_hashes.txt` | PASS |
| D-05 | 明确 grant 后准备预览 | 仅页面内存 grant 与合成预览 | D-05 | `05-grant.jpeg`、`06-preview.jpeg` | 见 `all_hashes.txt` | PASS |
| D-06 | 小写 `confirm` 后提交 | 被精确 CONFIRM 门阻断 | D-06 | `07-invalid-confirm.jpeg` | 见 `all_hashes.txt` | PASS |
| D-07 | 精确 `CONFIRM` 后提交 | 合成回执、未发生真实恢复 | D-07 | `08-confirmed-restore.jpeg` | 见 `all_hashes.txt` | PASS |
| D-08 | 模拟失败 | 半成品状态清理 | D-08 | `09-failure-cleanup.jpeg` | 见 `all_hashes.txt` | PASS |
| D-09 | 撤回／拒绝 | 恢复立即阻断 | D-09 | `10-revoke.jpeg` | 见 `all_hashes.txt` | PASS |
| D-10 | 刷新 | 返回默认拒绝与空输入 | D-10 | `11-refresh.jpeg` | 见 `all_hashes.txt` | PASS |
| D-11 | 关闭已操作标签并新标签页重开同一副本 | 默认拒绝、输入与回执清除 | D-11 | `12-reopened.jpeg` | 见 `all_hashes.txt` | PASS |
| D-12 | 实际 Tab 至 skip link 并 Enter | 焦点进入主内容（`#main-content`） | D-12 | `13-tab.jpeg`、`14-enter.jpeg` | 见 `all_hashes.txt` | PASS |
| D-13 | 点击三页导航；从标准窗口切换为窄窗口 | 无建议与离线页均显示关闭态；窄屏布局可见 | D-13 | `15-empty-page.jpeg`、`16-restricted-page.jpeg`、`17-narrow-responsive.jpeg` | 见 `all_hashes.txt` | PASS |

结论：13 项必填动态动作均有实际操作、结构化结果 ID、视觉 Evidence 和 SHA-256 索引；闭环通过。
