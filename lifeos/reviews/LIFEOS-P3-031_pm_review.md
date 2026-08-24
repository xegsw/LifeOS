# LIFEOS-P3-031｜PM Review：候选 SQL migration 编写 + 合成空库合同测试实现

## 验收信息

- 任务 ID：LIFEOS-P3-031
- 任务名称：候选 SQL migration 编写 + 合成空库合同测试实现
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-031_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional，允许在用户确认后启动 P3-032 独立工程评审
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-031 按任务卡在授权目录 `lifeos/engineering/LIFEOS-P3-031/` 内创建候选 SQLite migration、合同测试、复跑脚本和 evidence manifest，未发现越权修改 PM 账本、既有工程基线、Stitch 或真实能力相关文件。
- PM 复跑 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` 通过：33 PASS / 0 FAIL / 0 Not Implemented，其中 P0 18/18、P1 7/7、P2 8/8。
- P3-030 的两个 P1 条件已形成候选实现层证据：`authorization_activation_complete` trigger 与 CT-P1-07 覆盖授权激活完整性；`tombstone_generation_monotonic` trigger 与 DB-P0-15 / CT-P2-07 覆盖 tombstone generation 不得降低与 stale upgrade。
- P3-030 的三个 P2 清洁项已纳入候选 SQL / 测试 / 报告：DerivationInput `input_type` enum CHECK、并发 / stale tombstone 负测、Tombstone status 转换矩阵与强制层级。
- 交付物清楚声明本任务只验证合成空库，不连接真实 DB / Vault / Tauri / IPC，不冻结 Schema / API / SQL migration，不关闭 R-0040 / R-0043 / R-0044。
- 本地预检因本地模型连接重置跳过，符合 AGENTS 降级规则；PM 未把本地预检作为验收依据。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：P3-031 是首次授权候选 `.sql` migration 编写与合成空库合同测试，且涉及 R-0043 / R-0044 风险关闭候选证据，必须经过 PM 验收与后续独立工程评审，不适用快车道直接推进。

## 角色与关卡验收

- 主责角色覆盖情况：通过。候选 SQL 覆盖核心表、CHECK、FK、unique / partial index、trigger 与 migration meta；同时区分 DB 强制与应用事务 guard。
- 协审角色覆盖情况：通过但需独立复核。报告和 evidence 保持用户原文、外部来源、AI 派生、反馈、授权、tombstone、DTO 合同的边界分离；但 Authorization / Feedback / DTO 仍需独立反例攻击。
- 已通过关卡：
  - Gate 2 数据与来源评审：PM 验收通过，后续需独立复核 DB 约束旁路。
  - Gate 3 AI 权限与信任评审：PM 验收通过，后续需独立复核授权激活、撤回、删除、DTO fail closed。
  - Gate 4 技术可行性评审：PM 复跑通过，后续需独立复核 migration / rollback / test harness 是否过拟合。
- 未通过或需后续确认关卡：真实 Tauri / IPC、真实 DB 升级、真实 Vault、真实数据、导出、性能、WAL / backup、跨平台均未验证。
- 是否属于关键冻结事项：No。本任务不冻结 Schema / API 或工程基线。
- 是否需要独立评审：Yes，建议启动 P3-032。
- 独立评审路径：待创建。
- 独立评审结论：待完成。
- 是否允许进入下一任务或下一阶段：允许进入 P3-032 独立工程评审；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA、工程基线、R-0040 / R-0043 / R-0044 风险状态。
- 是否允许进入下一任务：Conditional。用户确认后可启动 P3-032 独立工程评审。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes，作为 P3-032 独立工程评审输入。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-031 的 PM 验收结论，并启动 P3-032 独立工程评审？
   - PM 建议：采纳，并启动 P3-032。
   - 可选方向：A. 采纳并启动 P3-032；B. 要求 P3-031 返工；C. 暂停 SQL migration 线。
   - 不确认的影响：P3-031 只能停留在 PM Accepted 候选输入，不能进入独立反例攻击，也不能作为后续真实 DB / Tauri 验证前置依据。

2. 问题：是否允许把 R-0043 / R-0044 标记为“候选关闭证据已进入独立评审输入”？
   - PM 建议：允许，但保持风险 Open，等待 P3-032 独立评审和后续用户确认后再考虑关闭。
   - 可选方向：A. 保持 Open 并进入 P3-032；B. 要求补充更多候选测试后再评审。
   - 不确认的影响：R-0043 / R-0044 仍仅保留 P3-031 执行 Agent 自证，不足以关闭风险。

## 整改建议

- 不要求 P3-031 返工。
- P3-032 独立评审必须重点攻击：
  - 候选 SQL trigger 是否存在 bypass 或 UPDATE / INSERT 未覆盖路径。
  - Authorization activation completeness 是否覆盖旧版本、scope/action/policy 组合边界。
  - Tombstone generation monotonicity 与 status transition 是否能抵御 stale / concurrent / rollback 反例。
  - DTO parser 测试是否过窄，是否可能误导为真实 IPC 证据。
  - `schema_checksum` 仍为候选标识，是否需要进入后续构建期 checksum 设计任务。

## 可接受内容

- 候选 `.sql` migration 文件可作为后续独立评审输入。
- 合成空库合同测试可作为后续 SQL / DB 验证基线候选。
- P3-030 两个 P1 条件已有候选实现层关闭证据。
- P3-030 三个 P2 清洁项已纳入候选 SQL / 测试口径。
- Evidence manifest 可作为 P3-032 的首要入口。

## 不接受或需谨慎内容

- 不接受将 P3-031 视为 Schema / API 冻结。
- 不接受将 P3-031 视为真实 DB migration 通过。
- 不接受将 DTO parser 测试视为真实 Tauri / IPC 通过。
- 不接受关闭 R-0040、R-0043 或 R-0044。
- 不接受进入下一阶段或启用真实能力。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：将 P3-031 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将 P3-031 更新为 Accepted but Not Frozen / Pass with Conditions。
- `lifeos/DECISION_LOG.md`：新增 PM 验收决策 D-0196。
- `lifeos/RISK_LOG.md`：更新 R-0043 / R-0044 缓解说明为已有候选关闭证据，但保持 Open。
- `lifeos/OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：能在受控目录中落地候选 SQL、测试脚本和 evidence，边界声明清楚，复跑入口单一。
- 主要问题：本任务仍是执行 Agent 自证，必须由独立评审会话攻击，不能自行得出冻结或风险关闭结论。
- 以后更适合分派给该 Agent 的任务类型：候选 SQL / 合同测试实现、合成测试 harness、evidence 整理、低风险工程补丁。
- 不建议分派给该 Agent 的任务类型：评审自己刚完成的候选 SQL / 风险关闭证明。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No。

## 下一步任务建议

- 建议用户确认采纳 P3-031 后，启动 P3-032：候选 SQL migration 与合成空库合同测试独立工程评审。
- P3-032 推荐交给 WorkBuddy 独立评审会话或新的隔离评审会话执行。
- P3-032 前不得冻结 Schema / API，不得关闭 R-0040 / R-0043 / R-0044，不得启动真实 Tauri / IPC 或真实 DB 验证。

## 聊天回复边界

PM 主会话只输出验收结论、资产状态、是否允许下一步 / 下一阶段、修改文件和需要用户确认的问题，不复述完整 Review。
