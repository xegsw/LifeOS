# Attempt-8 验收追溯矩阵

| 任务卡标准 | 测试 ID | Evidence |
|---|---|---|
| DB 缺失先失效旧页且不创建 DB／副文件 | A8-01 | results.json, read_only_db_states.json |
| 零字节 DB 只读失败且 bytes／对象不变 | A8-02 | results.json, read_only_db_states.json |
| 无 Schema／部分 Schema／双表缺列不初始化或补写 | A8-03..05 | results.json, read_only_db_states.json |
| attempt-7 空／损坏／不可读／查询失败合同 | A8-06..09 | results.json, read_only_db_states.json |
| 页面失效失败、合法 render、原子发布、clear | A8-10..13 | results.json |
| attempt-6 全边界回归 | A8-14 | attempt6_regression_results.json |
| 干净单元、缓存、零残留、历史只读 | A8-15..18 | results.json, historical_read_only_hashes.json |
