# P3-084 Rework 验收矩阵

| 任务卡验收标准 | 独立验证 | Evidence | 结果 |
|---|---|---|---|
| hash 与干净副本 | SHA-256 比对原 P3-082、临时副本 | `MANIFEST.md` | PASS |
| 新 Chrome `file:` 动态页面 | 新标签页加载临时副本 | `operation_log.md`、`visual_default.png` | PASS |
| 三态与视觉层级 | 逐一切换恢复／无建议／受限离线 | `operation_log.md`、四张状态截图 | PASS |
| 非空确认、空值拒绝、失败清理 | 固定文本确认、空确认、模拟失败 | `operation_log.md`、`visual_confirmed.png` | PASS |
| 无建议两条路径 | 点击两条路径且核对提示 | `operation_log.md`、`visual_no_suggestion.png` | PASS |
| 权限受限／离线、AI 未启用 | 切换受限态并核对边界文案 | `operation_log.md`、`visual_restricted.png` | PASS |
| 重复／幂等 | 连续两次确认后仅一个记录显示区 | `operation_log.md`、`independent_results.json` | PASS |
| 刷新／关闭重开清除 | Chrome 刷新、关闭临时页后新标签页重新打开 | `operation_log.md`、`visual_after_refresh.png`、`visual_reopened.png` | PASS |
| 禁止能力关闭态 | 独立静态扫描远程／网络／持久化／文件／native／导出等 | `independent_static_runner.mjs`、`independent_results.json` | PASS |
