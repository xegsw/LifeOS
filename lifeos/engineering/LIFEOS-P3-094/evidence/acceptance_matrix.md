# 验收矩阵

| 标准 | 测试 | Evidence |
|---|---|---|
| 捕获、重启、今日页 | AC-01..03 | self_check_results.json |
| 幂等与拒绝 | AC-04..06 | self_check_results.json |
| 原子失败、损坏 DB、清理 | AC-07..12 | self_check_results.json, operation_log.md |
| 禁止能力关闭 | AC-13 | self_check_results.json |
| 可运行回归 | AC-14 | self_check_results.json, test_run.log |
