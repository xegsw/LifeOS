# LIFEOS-P3-040 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-040
- 任务名称：Active Authorization 子表变异 P1 整改与回归
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`
- Evidence 路径：`lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-040_pm_review.md`
- 任务验收状态：Accepted / Remediation Regression Passed
- 资产冻结状态：Accepted but Not Frozen / Pending Independent Re-review
- 是否允许进入下一任务：Conditional；仅允许在用户确认采纳后启动隔离独立工程复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-20

## PM 总结

- P3-040 按授权范围修改 P3-031 候选 SQL、合同测试与 evidence，并创建任务专属双模式回归包；未发现越权修改 PM 账本、历史评审 evidence、真实数据或真实能力。
- PM 在隔离临时副本复跑 P3-031：42 PASS / 0 FAIL / 0 Not Implemented，退出码 0；P0 18、P1 16、P2 8。
- PM 在同一隔离副本复跑 P3-040：128 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown，退出码 0；P1 126、P2 2。
- P3-039 的 29 个反例已按原分组迁入双模式回归，其中 11 个已知 active Authorization 子表 P1 均被候选 DB trigger 拒绝；新增覆盖 OLD / NEW 双向改绑、状态翻转、retirement fence、合法终态清理和新版本激活。
- Manifest 所列稳定文件与运行输出 SHA-256 均与当前文件一致；P3-040 快照与当前候选 SQL hash 一致；P3-039 五个原始 evidence 文件 hash 保持未变。
- 当前证据足以进入隔离独立工程复评，但不构成 R-0043 / R-0044 / R-0046 关闭、Schema / API 或 SQL migration 冻结、真实 DB / Tauri 验证、工程基线恢复或阶段准入。
- 本地预检再次调用但局域网模型超时，按规则跳过；PM 已完成人工核对和独立临时副本复跑。

## P3 快车道 Review

- 是否适用 P3 快车道：No。任务优先级为 P0，且直接涉及权限、证据链和风险关闭候选边界。
- 验收结论：退出快车道，使用完整 PM Review。
- 是否存在已知 P0 / P1 回归失败：当前两套回归中无。
- 风险状态是否变化：No；R-0040、R-0043、R-0044、R-0046 保持开启，R-0045 保持 Closed。
- 是否触发用户确认：Yes；P0 优先级整改结论采纳及启动隔离独立复评必须由用户确认。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖候选 SQL trigger、状态转换、generation fence、合同测试、双模式 runner 和 evidence。
- 协审角色覆盖情况：已覆盖权限静默扩大、训练 / 外发 / sensitivity 改写、OLD / NEW 改绑、合法终态清理、版本激活与不可外推边界。
- Gate 2：PM 条件通过；候选版本链和 hash 可追溯，仍需独立评审攻击历史证据与版本复用边界。
- Gate 3：PM 条件通过；已知 active 子表静默变异在当前候选层 fail closed，仍需隔离独立复评发现相邻旁路。
- Gate 4：PM 条件通过；两套回归可复现且退出合同有效，但未验证真实 migration、并发、崩溃恢复或跨平台。
- 是否属于关键冻结事项：No；本任务不冻结任何资产。
- 是否需要独立评审：Yes，强制。
- 独立评审路径：待用户确认后创建下一张新任务卡。
- 独立评审结论：Pending。

## 验收与冻结区分

- 任务是否验收通过：Yes。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：生产 Schema / API、候选 SQL migration、真实事务 API、Tauri capability、导出格式、生产 SLA、工程基线。
- 是否允许进入下一任务：Conditional；只允许进入隔离独立工程复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：No。

## 需要用户确认的事项

### 是否采纳 P3-040 PM 验收结论并启动隔离独立复评

- PM 建议：采纳 P3-040 为 `Accepted / Remediation Regression Passed`，但保持所有相关风险开启；随后创建 P3-041 隔离独立工程复评任务。
- 推荐 Agent：WorkBuddy；Codex 模型路由字段按 D-0215 填写 `N/A`。
- 不确认的影响：P3-040 保持 Accepted but Not Frozen，不能判断 R-0044 / R-0046 是否具备关闭候选资格，也不能继续任何风险关闭或冻结动作。

## 整改建议

当前不要求执行会话返工。独立复评必须至少攻击：

- scope / action / policy 未知相邻变异、复合语句和 trigger 顺序。
- audit / outbox 证据预置、重复或重放，以及 generation 可否脱离合法状态转换单独变化。
- terminal Authorization 子表可维护是否会破坏历史授权证据完整性，即使终态不可复活。
- version 链跳号、并列版本、supersedes 关系和 active 唯一性组合边界。
- P3-031 与 P3-040 退出码、hash、P3-039 保留证明和双模式结果能否在隔离副本复现。

如独立评审发现 P0 / P1，应回到 PM 主会话，不得由评审 Agent 直接要求执行会话修复。

## 可接受内容

- 已知 11 个 P3-039 子表变异 P1 已形成候选 DB trigger 与可复跑回归映射。
- OLD / NEW 父双向改绑和 `INSERT OR REPLACE` 已进入负测。
- active 状态回退、终态复活、retirement generation / audit / outbox 缺失、version identity 原地修改和无 supersedes 的新版本激活已进入回归。
- 合法终态清理和 supersede 后新版本激活在当前合成边界通过。
- Evidence manifest、结果文件、日志与 SHA-256 可用于独立复评输入。

## 不接受或需谨慎内容

- 不接受把当前全绿外推为风险关闭或生产权限边界已完成。
- 不接受把 audit / outbox “存在性”检查外推为真实事务原子性、时序正确性或防重放已经成立。
- 不接受把合成空库和单进程文件型 SQLite 外推为非空旧库 upgrade、并发、WAL / 断电、跨平台或真实 Tauri / IPC 通过。
- terminal 子表维护与历史证据完整性的取舍仍需独立攻击，不在本次 PM 验收中冻结。

## 对项目文件的更新

- `lifeos/TASK_REGISTRY.md`：P3-040 更新为 Accepted but Not Frozen / Pending Independent Re-review。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳并启动 P3-041。
- `lifeos/DECISION_LOG.md`：新增 PM 验收决策 D-0216。
- `lifeos/AGENT_ROUTING_SCORECARD.md`：记录 Codex 在本任务中的适配度。
- `lifeos/RISK_LOG.md`：不修改风险状态。
- `lifeos/FREEZE_STATUS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex。
- 是否符合推荐：Yes。
- Agent 与任务类型匹配度：High。
- 主要优势：SQLite trigger 补丁、合同测试扩展、双模式复跑、hash 与 evidence 组织完整，范围纪律清楚。
- 主要问题：不能独立复评自己完成的高风险权限整改；真实事务与历史证据语义仍需外部反例攻击。
- 更适合的后续任务：候选 SQL 工程整改、合同测试、受控回归和 evidence 整理。
- 不建议分派的任务：P3-040 的独立复评、风险关闭最终判断或资产冻结。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：Yes，保持默认路由不变。

## 下一步任务建议

用户确认采纳后，创建 P3-041：P3-040 Active Authorization 子表变异整改隔离独立工程复评。该任务必须使用独立评审会话；本轮不创建、不启动。
