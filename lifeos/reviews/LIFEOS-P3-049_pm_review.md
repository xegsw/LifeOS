# LIFEOS-P3-049 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-049
- 任务名称：Tombstone 向 Authorization 改绑整改隔离独立工程复评
- 独立评审：`lifeos/reviews/LIFEOS-P3-049/independent_review.md`
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-049/evidence/MANIFEST.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-049/pm_evidence/MANIFEST.md`
- 独立评审本地预检：`lifeos/local_prechecks/LIFEOS-P3-049_independent_review_local_precheck.md`；Completed
- PM Review 本地预检：`lifeos/local_prechecks/LIFEOS-P3-049_LIFEOS-P3-049_pm_review_local_precheck.md`；Skipped / Local Model Unavailable（`Operation not permitted`），不影响 PM 人工验收
- 任务验收状态：Accepted / PM Adjusted to Rework
- 独立工程结论：Rework；技术矩阵通过，但未满足“全新隔离 Codex 会话”硬性条件
- 资产冻结状态：Rework / Not Frozen
- 是否允许进入下一任务：No；等待用户确认，且本轮不创建或启动后续任务
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-21

## PM 总结

- P3-049 的技术证据可复现。PM 在新的隔离临时副本复跑 P3-048 总入口，得到 P3-048 552 PASS、P3-047 等价 297 PASS、P3-031 70 PASS，退出码 0；直接运行原 PM-CE-06 得到 8 PASS / 0 BYPASS。
- P3-049 独立脚本未 import 或调用 P3-048/P3-047 runner helper，自建合成 SQLite 夹具；PM 复跑得到 488 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown。
- 独立脚本覆盖 memory/file、FK ON/OFF、recursive triggers ON/OFF、OLD/NEW 三方向、六字段、六 cleanup 状态、NULL、状态/时间组合、UPSERT/REPLACE、DELETE/reinsert、多行与显式事务；合法 generic/no-op/cleanup 路径无回退。
- 在 PM 写入本轮 Review 与账本前，P3-049 的 18/18 artifact hash、55/55 直接输入 hash、14/14 P3-048 关键 Evidence hash 均匹配；P3-046/P3-047/P3-048 历史失败 Evidence 未被覆盖，P3-047 原 `0 PASS / 8 BYPASS` 结果 hash 仍为 `f09d3a...e7a5`。其后只有本次获授权的 PM Review、PM Evidence、本地预检与主账本发生预期更新。
- 但 Codex 应用任务记录证明 P3-049 复用了既有任务 `01a01dc5-4a0a-7820-b7fd-bb180be333e5`。该任务于 2026-08-20 14:04 创建并先执行 P3-043；P3-049 于 22:43 才在同一任务中下发。它没有参与 P3-046/P3-047/P3-048 工程执行，因此执行侧隔离仍在，但不满足任务卡、D-0233 和用户提示中“全新 Codex 会话 / Create New Session / 不复用既有读取结果”的明确要求。
- PM 复跑不能替代独立评审会话隔离。故不接受独立报告的 Pass，校正为 Rework；技术结果可保留为后续真正隔离复评的输入。

## PM 独立核查

### 会话与独立性

- 应用任务记录：同一 thread ID 同时包含 P3-043 与 P3-049；P3-049 不是全新任务。
- 执行侧隔离：通过。该 thread 未参与 P3-046/P3-047/P3-048 工程实现或 PM 验收；工程与历史资产的当前 hash 与 P3-049 before/after 证明一致。
- 攻击集合独立性：通过。`independent_counterexample_attacks.py` 只导入 Python 标准库，直接读取候选 SQL，自建 fixture 与场景；未导入执行侧 runner。
- 最终判定：程序独立性不完整，违反硬性会话路由要求；不能判 Pass。

### PM 隔离复跑

- 临时副本：`/private/tmp/lifeos-p3049-pm.2vPenD`。
- P3-048 总入口：退出码 0。
- P3-048：P2 552 PASS，0 FAIL/Not Implemented/Unknown。
- P3-047 等价：P1 144 + P2 153 = 297 PASS，0 FAIL/Not Implemented/Unknown。
- P3-031：P0 18 + P1 27 + P2 25 = 70 PASS，0 FAIL/Not Implemented。
- 原 PM-CE-06：8 PASS / 0 BYPASS，退出码 0。
- P3-049 独立攻击：488 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown，退出码 0。

### 技术分类

- 技术 P0：0。
- 技术 P1：0。
- 技术 P2 bypass：0。
- 新增技术 P2：0。
- 程序性 Rework：1；未使用全新隔离 Codex 会话。
- P3 Observation：2；cross-trigger 首错误不稳定、显式事务中 `RAISE(ABORT)` 后调用方需显式 rollback。
- Not Implemented：0。
- Unknown：0。

## 角色与关卡验收

- 独立 QA / Evidence Reviewer：技术 evidence、hash、退出码与攻击集合可复现；会话隔离证明未通过。
- 技术架构负责人：OLD/NEW、`UPDATE OF`、NULL 安全比较、替换语义与事务原子性在候选 SQLite 边界内通过。
- AI 信任与安全负责人：已知 PM-CE-06 与相邻改绑路径在本轮矩阵内 fail closed；但程序独立性缺口阻止最终独立 Pass。
- 数据 / 领域模型负责人：generic Tombstone 合法语义未被全局冻结；本任务不改变核心模型。
- Gate 2：Technical Pass in Controlled Boundary / Process Rework。
- Gate 3：Technical Pass in Controlled Boundary / Process Rework。
- Gate 4：Technical Pass in Controlled Boundary / Process Rework。
- 是否需要再次独立评审：Yes；如用户授权，必须在真正新建且未承载其他 LifeOS 任务的隔离 Codex 会话中重新执行或至少重新形成独立验证链。

## 验收、风险、冻结与阶段区分

- P3-049 交付是否完成：是；因此任务层记录 Accepted。
- P3-049 最终工程独立结论是否通过：否；PM Adjusted to Rework。
- P3-048 技术整改证据是否可保留：是，作为后续复评输入。
- P3-048 资产是否冻结：否，Rework / Not Frozen。
- R-0048 是否关闭：否，保持 Open / Remediation Candidate。
- R-0049 是否关闭：否，保持 Open / Remediation Candidate。
- 是否允许恢复工程基线：否。
- 是否允许启用真实能力：否。
- 是否允许进入下一阶段：否。
- 是否更新 `FREEZE_STATUS.md`：否；冻结状态未变化。其当前阶段叙述仍停留在 P3-040，属于既有运营索引滞后，不构成本轮冻结授权。

## 需要用户确认

1. 是否采纳 P3-049 的 `Accepted / PM Adjusted to Rework` 结论。
2. 是否另行授权创建一个真正全新的隔离 Codex 复评任务；本轮不创建、不启动。
3. 在用户确认前，R-0048/R-0049 保持开启，资产不冻结，不恢复工程基线，不进入下一阶段。

## 对项目文件的更新

- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认 P3-049 Rework。
- `lifeos/TASK_REGISTRY.md`：P3-048 更新为 Independent Re-review Rework；P3-049 更新为 Accepted / PM Adjusted to Rework。
- `lifeos/DECISION_LOG.md`：新增 D-0234。
- `lifeos/RISK_LOG.md`：R-0049 补充 P3-049 技术证据通过但程序独立性不足，状态保持 Open / Remediation Candidate；R-0048 不变。
- `lifeos/FREEZE_STATUS.md`：不更新。
