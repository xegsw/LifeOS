# P3-094 Final Invariant Closure PM 验收矩阵

| 验收项 | Evidence | PM 结论 |
|---|---|---|
| 提交 Manifest／源码／历史只读 hash | 工程 Manifest、`source_hashes.json`、`historical_read_only_hashes.json`、`pm_post_update_integrity.json` | 提交前 24/24、6/6、185/185；PM 更新后仅 PM Review 为授权差异 |
| 全新隔离复跑 | `results.json`、`summary.json`、`unit_test.log` | runner 107 PASS；unit 41 PASS；历史回归 19/13/18 PASS |
| attempt-8 已知 Schema／来源反例 | `results.json` | 2 PASS，既有 P1 已关闭 |
| 既有 DB post-commit cleanup | `pm_final_invariant_counterexamples.json#PM-A9-01` | FAIL；返回失败但 DB 1→2、audit 1→2、页面消失并残留 staging |
| 新 DB post-publish cleanup | `pm_final_invariant_counterexamples.json#PM-A9-02` | FAIL；返回失败但新 DB 已提交 1 条记录 |
| saved／repeat／clear 审计语义 | `pm_final_invariant_counterexamples.json#PM-A9-03..05` | FAIL；伪造时间、顺序和 count 被接受 |
| 强制矩阵逐行实际执行 | `pm_final_invariant_counterexamples.json#PM-A9-06` | FAIL；至少五类必测项无独立 fixture，runner 仍批量标 PASS |
| 临时夹具与禁止能力 | `pm_conclusion.json`、PM 反例结果 | 仅固定非敏感 `/private/tmp` 夹具；零残留、未联网、未用真实数据 |

PM 计数：P0=0、P1=3、P2=0、Unknown=0、Not Implemented=1。
