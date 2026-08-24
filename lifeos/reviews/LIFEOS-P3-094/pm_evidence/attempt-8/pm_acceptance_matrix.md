# Attempt-8 PM 验收追溯矩阵

| 验收项 | PM 证据 | 结论 |
|---|---|---|
| 提交 Manifest／源码／历史只读 hash | 工程 Manifest、`source_hashes.json`、`historical_read_only_hashes.json`、`pm_post_update_integrity.json` | 提交前 16/16、5/5、155/155；PM 更新后仅 PM Review 为授权差异 |
| 全新隔离复跑 | `results.json`、`attempt6_regression_results.json`、`test_run.log` | attempt-8 18 PASS；attempt-6 19 PASS |
| DB 缺失／零字节／缺表缺列只读失败 | `results.json`、`read_only_db_states.json` | PASS；旧页面失效，DB 不创建／不改写 |
| 完整路径链、文件类型、render／clear 生命周期回归 | `attempt6_regression_results.json` | 19 PASS |
| 同列同类型但缺全部约束，且 source 非本地 | `pm_schema_constraint_counterexamples.json` | FAIL；成功发布并误标本地捕获 |
| 仅缺 idem_key UNIQUE 约束 | `pm_schema_constraint_counterexamples.json` | FAIL；成功发布，未按不完整 Schema 拒绝 |
| 临时夹具与禁止能力 | `pm_schema_constraint_counterexamples.json`、`pm_conclusion.json` | 仅固定非敏感 `/private/tmp` 夹具；零残留、未联网、未用真实数据 |

PM 计数：P0=0、P1=1、P2=0、Unknown=0、Not Implemented=0。两个失败夹具属于同一 Schema／来源完整性根因，只计一个 P1。
