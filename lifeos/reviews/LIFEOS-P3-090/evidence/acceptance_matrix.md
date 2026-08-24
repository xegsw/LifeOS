# P3-090 验收标准 → 独立步骤 → Evidence

| 标准 | 独立核查 | Evidence | 结果 |
|---|---|---|---|
| 当前五项源 hash 与三项历史 hash | 独立 SHA-256 | `independent_static_results.json` | PASS |
| 合成／真实能力边界、禁止能力关闭 | 新写静态 runner | `independent_static_results.json` | PASS |
| 默认拒绝、grant、CONFIRM、撤回 | Chrome task-local 动态步骤 | `dynamic_results.json`、`operation_log.md` | PASS |
| 三页与无可靠建议关闭态 | Chrome 导航 + 静态检查 | `dynamic_results.json`、`independent_static_results.json` | PASS |
| 可访问性、缩放、刷新／关闭重开、失败清理 | 独立源代码静态路径核查；执行侧动态 Evidence 仅作交叉参照 | `independent_static_results.json`、P3-089 `dynamic_results.json` | PASS（任务限定的纯本地 UI） |
