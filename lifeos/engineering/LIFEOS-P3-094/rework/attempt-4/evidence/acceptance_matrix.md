# Attempt-4 验收追溯矩阵

| 任务卡标准 | 测试 ID | Evidence |
|---|---|---|
| 捕获、幂等、跨进程复读 | A4-01..04 | results.json, test_run.log |
| 清理后 DB 为零、旧页面不存在、重渲染失败 | A4-05..06 | results.json, operation_log.md |
| 页面失效失败时 DB 不清空、操作失败 | A4-07 | results.json |
| 原子失败、损坏 DB fail-closed | A4-08..09 | results.json |
| 禁止能力关闭态 | A4-10 | results.json, source_hashes.json |
| 干净副本回归、残留为零、历史只读 | A4-11..13 | results.json, historical_read_only_hashes.json |
