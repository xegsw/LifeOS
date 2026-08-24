# 权限与活跃阻断报告

## 机器结果

- 权限泄漏：`0`。
- 被删除、撤回、断源、证据失效或旧 generation 影响的内容进入搜索、恢复包或候选建议：`0`。
- 跨 Project 相似内容串扰：`0`。
- `local_search` 专用材料进入 `project_recovery` 或 `next_step`：`0`。

## 判定顺序

每条消费路径先检查当前 Authorization 与目的，再检查 tombstone / retract、Source 状态、证据状态和 queue generation，最后执行 Project 与元数据过滤。`DENY`、不可判定或用途不匹配均 fail closed。搜索命中不产生恢复包或建议用途授权。

冲突证据可以在搜索与恢复包的“待复核”区显示，但不能生成下一步候选。唯一证据失效的用户确认对象保留历史身份，只进入 `review_required` 缺口，不进入活跃恢复叙述与建议。拒绝的 AI 候选不进入建议。

详细逐查询排除计数见 `retrieval_results.json`，断言见 `test_matrix.csv` T04、T06-T17。

