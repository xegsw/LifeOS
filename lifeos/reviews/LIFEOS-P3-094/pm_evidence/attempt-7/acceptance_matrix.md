# Attempt-7 验收追溯矩阵

| 任务卡标准 | 测试 ID | Evidence |
|---|---|---|
| 空 DB + 旧页面 fail closed，DB 不变 | A7-01 | results.json, stale_page_states.json |
| 损坏／不可读 DB + 旧页面 fail closed | A7-02..03 | results.json, stale_page_states.json |
| 查询失败 + 旧页面 fail closed | A7-04 | results.json, stale_page_states.json |
| 旧页面失效失败明确披露、DB 不变 | A7-05 | results.json, stale_page_states.json |
| 合法 render、原子发布、clear 语义保持 | A7-06..08 | results.json |
| attempt-6 完整边界／生命周期回归 | A7-09 | attempt6_regression_results.json |
| 干净副本单元、缓存卫生、零残留、历史只读 | A7-10..13 | results.json, historical_read_only_hashes.json |
