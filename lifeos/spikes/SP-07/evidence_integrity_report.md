# 证据完整性报告

## 搜索结果

重点结果的机器检查完整性为 `1.0`。每条结果均含：

- Source ID；
- ArtifactVersion ID；
- Derivation ID 与 Link ID；
- 用户确认状态；
- 生成时间；
- 证据状态与冲突状态；
- 当前权限状态与 Authorization ID。

## 恢复包

四个恢复包均按 Project 边界组装上次停点、近期变化、确认 Decision、开放 Action、未处理材料与冲突/缺口。每个条目携带可打开的合成证据引用；证据失效项只进入缺口区。Alpha 包因冲突与唯一证据失效标记为 `degraded_review_required`。

## 候选下一步

每个 Project 生成不超过 3 条 deterministic 候选。每条均为 `ai_candidate_suggestion / unconfirmed`，包含 1-3 条证据、理由、时效、置信边界、冲突状态、权限缺口和 `accept / edit_accept / reject` 反馈入口；没有自动创建或确认 Action、Decision、Link。

机器样例见 `recovery_package_samples.json`，断言见 `test_matrix.csv` T05、T13-T16。

