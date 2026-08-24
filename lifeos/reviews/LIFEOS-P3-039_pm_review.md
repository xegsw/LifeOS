# LIFEOS-P3-039 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-039
- 任务名称：候选 SQL 残留 P1 整改隔离独立工程复评
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`
- Evidence 路径：`lifeos/reviews/LIFEOS-P3-039/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-039_LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-039_pm_review.md`
- 任务验收状态：Accepted
- 独立评审结论：Pass with Conditions
- 被评审资产状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional；仅允许用户确认后进入 P3-040 窄范围整改
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High
- 更新时间：2026-08-18

## PM 总结

1. P3-039 按任务卡完成了与 P3-038 执行会话隔离的独立复评，复跑、反例、hash 与不可外推边界完整，评审任务本身验收通过。
2. P3-038 对已知 P2-2、P2-3、P2-4 的三项整改真实有效：Tombstone DELETE / REPLACE / DELETE+INSERT、非法初始状态与 active Authorization 子表 DELETE 均在候选 DB 层被拒绝。
3. PM 在临时副本 `/tmp/lifeos-p3-039-pm-xwcy8B` 复跑：P3-031 为 38 PASS / 0 FAIL、退出码 0；P3-038 为 12 PASS / 0 FAIL、退出码 0；独立反例为 29 个场景、18 PASS / 11 FAIL、P1 bypass=11、退出码 1，与 P3-039 报告一致。
4. 11 个新 P1 可在父 Authorization 保持 active、generation 不变、audit 不追加时新增或改写 scope/action/policy，包括 INSERT、UPDATE、authorization_id 改绑和 `INSERT OR REPLACE`。其中新增 allow scope、增加 export action、开启 external send / training 等路径可直接扩大权限。
5. 因这些问题属于 Authorization 核心权限边界，P3-038 只能维持 Pass with Conditions；R-0046 不得进入关闭候选，覆盖范围扩展为 active Authorization 子表的 DELETE / INSERT / UPDATE / REPLACE / 改绑完整性与 generation/audit fencing。
6. R-0044 的既有关闭失效条件已触发：候选 SQL 变更后的独立 DB 验证发现 active Authorization 完整性新旁路，因此 PM 将 R-0044 防御性重新打开。R-0043 的 Tombstone 面已具备独立关闭候选证据，但本轮不关闭；R-0045 保持 Closed，R-0040 保持 Open / Conditional。

## P3 快车道 Review

不适用。本任务是 P0 安全整改后的隔离独立复评，且涉及删除 / 撤回与 Authorization 权限核心边界。

## 角色与关卡验收

- 主责角色覆盖情况：通过。独立复跑、29 个反例、结构化 evidence 和严重级别判断完整。
- 协审角色覆盖情况：通过。覆盖 Tombstone 不复活、Authorization 权限静默扩大、generation/audit 缺口和不可外推边界。
- Gate 2：Pass with Conditions。Tombstone 面通过，Authorization 子表非 DELETE 变异仍有 P1。
- Gate 3：Pass with Conditions。active Authorization 可被静默扩大或改写，必须整改。
- Gate 4：Pass with Conditions。两套既有回归可信，但测试集未覆盖 11 条相邻变异旁路。
- 是否属于关键冻结事项：No；但属于风险关闭和真实 DB 路线的前置安全关卡。
- 是否需要后续独立评审：Yes；P3-040 整改后必须由隔离会话再次复评。
- 是否允许进入下一任务或下一阶段：用户确认后仅允许进入 P3-040；不允许进入下一阶段。

## 验收与冻结区分

- P3-039 任务是否验收通过：Yes。
- P3-038 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：候选 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA、工程基线及真实 DB 能力。
- 是否允许进入下一任务：Conditional；仅限 P3-040 active Authorization 子表变异旁路整改。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

- 问题：是否采纳 P3-039 的 Pass with Conditions 结论、PM 对 R-0044 的防御性重新打开，以及启动 P3-040 窄范围整改。
- PM 建议：采纳并启动 P3-040。
- 不确认的影响：Authorization 子表 11 条 P1 旁路继续存在；R-0044 / R-0046 继续开启，真实 DB、Schema / API 冻结和后续风险关闭路线保持阻塞。

## 整改建议

P3-040 最小范围应包括：

- active 父 Authorization 下，阻断 scope/action/policy 的直接 INSERT、UPDATE、`INSERT OR REPLACE` 和 `authorization_id` 改绑；或实现等价的受控父状态退出、generation 递增与 audit/outbox 合同。
- 明确允许的非 active 清理 / 维护路径，避免把生命周期维护永久锁死。
- 将 11 个 P3-039 反例迁入 P3-031 合同测试和文件型 SQLite 回归，并保持非零退出合同。
- 更新 P3-031 / 新任务 evidence，但不得改写 P3-039 原始 failure evidence。
- 整改完成后再次安排隔离独立工程复评。

## 可接受内容

- P2-2、P2-3 的 Tombstone 已知旁路在当前候选层通过独立复核。
- P2-4 的 active Authorization 子表 DELETE 已知旁路通过独立复核，非 active 清理仍可用。
- P3-031 38 项与 P3-038 12 项既有回归可复现，hash 和 P3-037 failure evidence 保留可信。
- P3-039 发现的 11 个 P1 有最小可复现证据，足以作为 P3-040 输入。

## 不接受或需谨慎内容

- 不接受把 P3-039 的 Pass with Conditions 解读为 P3-038 已无条件通过。
- 不接受 R-0046 进入关闭候选；其风险面必须扩展到 DELETE / INSERT / UPDATE / REPLACE / 改绑。
- 不接受维持 R-0044 Closed，因为其关闭失效条件已经被新的 active Authorization 完整性旁路触发。
- 不接受关闭 R-0043；本轮只确认其 Tombstone 面可进入后续关闭候选判断。
- 不接受把候选 SQL、合成空库或单进程 SQLite 结果外推到真实 DB、Tauri / IPC、生产 migration 或下一阶段准入。

## 对项目文件的更新

- 更新 `lifeos/CURRENT_STATUS.md`。
- 更新 `lifeos/TASK_REGISTRY.md`。
- 更新 `lifeos/FREEZE_STATUS.md`。
- 更新 `lifeos/DECISION_LOG.md`。
- 更新 `lifeos/RISK_LOG.md`：R-0044 重新打开；扩展 R-0046；R-0043 保持开启但记录关闭候选证据。
- 更新 `lifeos/AGENT_ROUTING_SCORECARD.md`。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy。
- 本任务实际执行 Agent：WorkBuddy。
- 是否符合推荐：Yes。
- Agent 与任务类型匹配度：High。
- 主要优势：独立性清楚，既复跑已知回归，又主动扩展相邻变异反例，准确发现 11 条核心权限 P1。
- 主要问题：报告将存在 11 条 P1 的结果表述为 Pass with Conditions，边界可接受但容易被误读；PM 已明确其只允许进入整改任务，不允许风险关闭或冻结。
- 更适合的后续任务：权限 / 删除边界独立复评、反例攻击、evidence 复核。
- 不建议任务：直接修改本次被评审的候选 SQL或自行关闭风险。
- 是否更新 Scorecard：Yes。

## 下一步任务建议

用户采纳本 PM Review 后，创建 `LIFEOS-P3-040`：active Authorization 子表 INSERT / UPDATE / REPLACE / 改绑旁路整改与回归任务。推荐交给 Codex 工程整改会话；可复用 P3-038 工程线会话，但必须读取新任务卡并重置授权边界。整改完成后仍须创建隔离独立复评任务。
