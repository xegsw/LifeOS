# LIFEOS-P3-038 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-038
- 任务名称：候选 SQL 残留 P1 整改与回归任务
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
- Evidence 路径：`lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-038_LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-038_pm_review.md`
- 任务验收状态：Accepted / Remediation Regression Passed
- 资产冻结状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional；仅允许进入隔离独立工程复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-17

## PM 总结

1. P3-038 按任务卡完成了 P2-2、P2-3、P2-4 三项候选 SQL 整改，没有把应用层约定冒充 DB 约束，也没有触碰真实用户 DB、Vault、Tauri / IPC 或其他禁止范围。
2. P2-2 通过 `tombstone_no_delete` 与 `tombstone_insert_contract` 阻断直接 DELETE、`INSERT OR REPLACE` 和 DELETE+INSERT 降代 / 复活；P2-3 强制 Tombstone 只能以 `accepted` 初始状态创建；P2-4 采用任务卡允许的 DB 直接拒绝分支，阻断 active Authorization 三类子表 DELETE。
3. PM 在临时副本 `/tmp/lifeos-p3-038-pm-vhf92y` 独立复跑：P3-031 为 38 PASS / 0 FAIL / 0 Not Implemented，P0=18、P1=12、P2=8；P3-038 为 12 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown，P0=2、P1=10；两套退出码均为 0。
4. Evidence manifest 提供稳定源文件 hash、运行输出 hash、P3-037 failure evidence 保留证明、路径隔离、完整性 / FK、backup / restore 和 rollback 证据。PM 复跑结果与报告一致。
5. 当前证据足以认定“整改任务完成并通过回归”，但执行会话不能独立确认自己修复的高风险边界。R-0043 继续保持 Reopened，R-0046 继续保持 Open，R-0040 继续保持 Open / Conditional。
6. 下一步必须由与本执行会话隔离的独立工程评审会话复核；在独立复评与后续用户决策前，不关闭风险、不冻结 Schema / API、不恢复或冻结工程基线、不启用真实能力、不进入下一阶段。

## P3 快车道 Review

不适用。本任务优先级为 P0，且涉及删除 / 撤回与 Authorization 权限完整性核心边界，必须使用完整 PM Review，并在整改通过后安排独立复评。

## 角色与关卡验收

- 主责角色覆盖情况：通过。候选 SQL、合同测试、文件型 SQLite 回归、runner 退出合同和 evidence 均已覆盖。
- 协审角色覆盖情况：通过但需独立复评。报告明确检查 Tombstone 不复活、授权子表完整性、P3-037 证据保留和真实能力隔离。
- 已通过关卡：Gate 2、Gate 3、Gate 4 在“执行整改 + PM 复跑”层面 Pass with Conditions。
- 未通过或需后续确认关卡：Gate 2 / 3 / 4 的独立性确认尚未完成。
- 是否属于关键冻结事项：No；但属于 P0 安全整改与风险关闭前置证据。
- 是否需要独立评审：Yes，必须使用与 P3-038 执行会话隔离的评审会话。
- 独立评审路径：待创建，建议任务 ID 为 `LIFEOS-P3-039`。
- 独立评审结论：待完成。
- 是否允许进入下一任务或下一阶段：允许在用户采纳本 PM 结论后进入 P3-039；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：候选 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA、工程基线，以及真实 DB / 非空旧库 upgrade 能力。
- 是否允许进入下一任务：Conditional；仅限 P3-039 隔离独立工程复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，更新为 Accepted but Not Frozen / Pending Independent Re-review。

## 需要用户确认的事项

- 问题：是否采纳 P3-038 的 `Accepted / Remediation Regression Passed` 结论并启动 P3-039 隔离独立工程复评。
- PM 建议：采纳并启动 P3-039。
- 不确认的影响：P3-038 保持已验收但未进入独立确认，R-0043 / R-0046 继续开启，Schema / API 与后续真实能力路线继续暂停。

## 整改建议

当前不要求 P3-038 执行会话返工。后续独立复评至少应：

- 复跑 P3-031 与 P3-038 两套入口，并核对非零退出合同。
- 独立攻击 Tombstone DELETE、REPLACE、DELETE+INSERT、非法初始状态和状态转换。
- 独立攻击 active Authorization scope/action/policy DELETE，并确认 inactive 清理仍可用。
- 额外检查 active Authorization 子表的 INSERT / UPDATE / 改绑等同类变异路径，避免只对 P3-037 已知 DELETE 用例过拟合；若发现新旁路，应由 PM 另行登记风险和整改任务。
- 核对 P3-037 failure evidence、稳定输入 hash、路径隔离、backup / restore、rollback 与不可外推声明。

## 可接受内容

- 三项 P1 失败已在当前候选 SQL、合成空库和受控文件型 SQLite 范围内形成可复跑的整改证据。
- P3-031 合同测试扩展为 38 项，P3-038 文件型回归为 12 项，当前 PM 复跑全部通过。
- P3-037 原始失败证据被保留，整改 evidence 与历史失败 evidence 没有被混写。
- 报告对真实 DB、非空旧库 upgrade、真实 Tauri / IPC、跨平台、并发 / WAL / 断电和生产 SLA 的不可外推边界表达清楚。

## 不接受或需谨慎内容

- 不接受把本任务通过解释为 R-0043 / R-0046 已关闭。
- 不接受把候选 SQL 回归通过解释为生产 migration、非空旧库 upgrade 或真实用户数据安全已通过。
- 不接受在独立复评前冻结 Schema / API、SQL migration 或工程基线。
- P2-4 当前只证明三类 active 子表 DELETE 被拒绝；其他直接 INSERT / UPDATE / 改绑路径必须由独立复评做反例检查，不能从 DELETE 测试自动外推。

## 对项目文件的更新

- 更新 `lifeos/CURRENT_STATUS.md`。
- 更新 `lifeos/TASK_REGISTRY.md`。
- 更新 `lifeos/FREEZE_STATUS.md`。
- 更新 `lifeos/DECISION_LOG.md`。
- 更新 `lifeos/RISK_LOG.md`，仅补充整改候选证据，不改变风险状态。
- 更新 `lifeos/AGENT_ROUTING_SCORECARD.md`。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex。
- 是否符合推荐：Yes。
- Agent 与任务类型匹配度：High。
- 主要优势：范围纪律、DB 层补丁、两套回归、hash / evidence、不可外推声明均清楚，PM 可稳定复跑。
- 主要问题：执行者不能独立评审自己的高风险整改；现有测试集中于任务卡已知攻击面，仍需独立评审扩展反例。
- 以后更适合分派给该 Agent 的任务类型：工程整改、SQLite 合同测试、回归入口和 evidence 整理。
- 不建议分派给该 Agent 的任务类型：对本次整改的独立复评、风险关闭最终判断。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：Yes。

## 下一步任务建议

用户采纳本 PM Review 后，创建并启动 `LIFEOS-P3-039`：候选 SQL 残留 P1 整改隔离独立工程复评。建议交给 WorkBuddy 独立评审会话，必要时由其在隔离临时副本只读复跑和做反例攻击；不得修改 P3-031 / P3-038 工程文件，不得关闭风险或启动后续任务。
