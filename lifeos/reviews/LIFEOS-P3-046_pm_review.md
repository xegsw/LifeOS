# LIFEOS-P3-046 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-046
- 任务名称：Authorization 生命周期证据与终态历史合同候选实现及回归
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md`
- 原 Evidence：`lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md`
- PM 反例 Evidence：`lifeos/reviews/LIFEOS-P3-046/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-046_LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression_local_precheck.md`
- PM Review：`lifeos/reviews/LIFEOS-P3-046_pm_review.md`
- 任务验收状态：Accepted / PM Adjusted to Rework
- 资产冻结状态：Rework / Not Frozen
- 是否允许进入下一任务：Conditional；用户确认 Rework 后仅允许创建窄范围整改任务
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：Medium
- 更新时间：2026-08-20

## PM 总结

- 报告、原 manifest、hash 与原任务统计一致；PM 在隔离临时副本复跑 P3-046 为 248/248 PASS、P3-031 为 64/64 PASS，原入口退出码 0，P3-044 受保护 evidence 未变化。
- lifecycle command、同事务 retirement evidence、AuditEntry append-only、terminal parent/children 默认不可变和窄 cleanup 主体方向已经形成真实候选实现，不是纸面设计。
- 原测试存在自证盲区。PM 新增 5 条不修改工程代码的合成反例，得到 0 PASS / 5 BYPASS，P1=2、P2=3，入口退出码 1。
- 两个 P1 均位于任务卡明确要求的 Outbox CAS 边界：未来调度 job 可被提前领取；不带当前 owner/generation 条件也可完成有效租约。根据任务卡，出现任何 P0/P1 必须 Rework。
- R-0048/R-0049 保持开启并退回工程整改，不得进入风险关闭、Schema/API 冻结、真实能力准入或下一阶段。

## P3 快车道 Review

不适用。本任务涉及权限、撤回、删除与证据链核心边界，且 PM 已发现 P1，必须使用完整 Review。

## PM 独立复跑

- 隔离目录：`/tmp/lifeos-p3046-pm.Y3ZYFm`（临时复跑副本，不作为长期 evidence）。
- 原入口：`sh lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.sh`。
- 原入口结果：P3-046 248 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown；P1 136、P2 112；P3-031 64 PASS，退出码 0；P3-044 preservation True。
- PM 反例入口：`python3 lifeos/reviews/LIFEOS-P3-046/evidence/pm_counterexample_attacks.py`。
- PM 反例结果：5 BYPASS；P1=2、P2=3；退出码 1。

## 必须整改的问题

### PM-CE-02 / P1：Future Outbox 可提前领取

`outbox_job_runtime_state_machine` 的 pending→leased 分支没有验证 `OLD.available_at_ms <= DB now`；任务自带 claim helper 的 WHERE 也只有 `id + status`，未绑定 availability 或旧 lease generation。未来调度的 job 可立即进入 leased，违反 P3-045 的 available time + generation CAS 合同。

整改要求：候选 DB guard 与合成应用 claim 语句必须共同约束 available time、pending 状态和 expected old lease generation；新增提前 1 ms、远未来、边界相等和竞争领取反例。

### PM-CE-03 / P1：Completion 未强制 owner/generation CAS

当前 trigger 只确认 OLD 行存在有效未过期 lease，却无法证明执行 UPDATE 的调用者持有该 owner/generation。原 AC-06 的 stale 测试只是使用一个匹配不到行的 WHERE，未攻击“完全不带 CAS 条件”的更新。PM 复现该更新可直接 completed。

整改要求：明确 DB 与应用 guard 的责任；提供唯一受控 completion 入口或等价可验证 guard，保证缺少／错误 owner、lease generation 的完成尝试 fail closed。不得只在测试 helper 中“自觉写 WHERE”。

### PM-CE-01 / P2：Canonical hash 与 Submission 未绑定

`canonical_request_hash` 仅检查非空；值为 `x` 且数据库没有任何 Submission 时 retirement 仍成功。原回归只证明 fault rollback 会清除临时 Submission，没有证明成功路径的 Submission/idempotency/hash 绑定，也未执行任务卡列出的错误 hash 反例。

整改要求：定义并实现成功路径的 Submission/command 绑定或等价应用事务守卫；至少拒绝格式错误、同 idempotency 不同 hash、Submission 缺失／不匹配和跨 Authorization 复用。

### PM-CE-04 / P2：Tombstone 控制包络可改写

进入 cleanup_pending 后，`subject_type/subject_id`、`command_id`、`reason_code`、`blocked_at_ms` 等仍可直接 UPDATE；PM 已复现把 subject 改为 ghost 并改写清理意图。cleanup_status 单向不等于 tombstone 身份与证据包络不可变。

整改要求：Authorization tombstone 的身份、generation、command/reason、blocked time 自 INSERT 起不可变；只允许任务合同明确的 cleanup_status/updated time 合法前进。

### PM-CE-05 / P2：Outbox 删除合同过度收窄且缺 retention

当前 delete trigger 仅允许清理 `authorization_state_change`，导致其他 terminal 非权威 job 永久不可删除；同时 Authorization terminal job 达到 terminal 后可立即删除，没有 P3-045 所述保留窗口。

整改要求：限定本补丁不得破坏其他 Outbox 类型的受控清理；为 Authorization lifecycle job 定义可测试的最小 retention gate，或把未冻结保留策略显式参数化并保持默认拒绝。

## 角色与关卡验收

- 主责角色覆盖：候选 SQL、测试、evidence 和原子 retirement 主体覆盖充分。
- 协审角色覆盖：范围纪律和不可外推声明清楚，但反例攻击不足，未覆盖调用者绕过应用 CAS 与 tombstone 控制包络。
- Gate 2：Rework；Submission/hash 与 tombstone 历史身份仍不完整。
- Gate 3：Rework；Outbox claim/completion 的 P1 fail-closed 未成立。
- Gate 4：Rework；原回归可复现，但测试集合不足以支持合同通过。
- 是否属于关键冻结事项：否；但属于 Schema/API 冻结和风险关闭前置高风险候选。
- 是否需要独立评审：整改完成并通过 PM 复跑后，需要隔离独立工程复评，才能讨论风险关闭或冻结。
- 是否允许进入下一任务：用户确认 Rework 后，只允许进入 P3-047 窄范围整改。
- 是否允许进入下一阶段：No。

## 验收与冻结区分

- 任务是否完成交付：是。
- 工程结论是否通过：否，Rework。
- 对应资产是否冻结：否。
- 是否允许关闭 R-0048/R-0049：否。
- 是否允许恢复／扩展工程基线：否。
- 是否允许启用真实能力：否。
- 是否需要更新 `FREEZE_STATUS.md`：否，冻结状态未变化。

## 需要用户确认

- 是否采纳 PM 将 P3-046 校正为 Rework。PM 建议采纳。
- 采纳后是否创建 P3-047：只处理上述 2 个 P1 与 3 个 P2，不扩展真实 worker、真实 DB、Tauri/IPC、风险关闭或 Schema/API 冻结。PM 建议创建。

## Agent 分派与适配度

- 推荐 Agent：Codex；实际 Agent：Codex；基础工程能力匹配。
- 匹配度：Medium。本次能完成复杂 trigger 与大矩阵回归，但测试过度贴合自身实现，对“没有 CAS WHERE”“未来 available time”“控制包络改写”等反例覆盖不足。
- 后续整改仍可交给同一 Codex 工程会话；未来独立复评必须隔离，不能由该会话自评风险关闭。

## 下一步建议

用户确认后创建 P3-047 窄范围整改与回归任务。整改必须首先把本 Review 的 PM 反例迁移为受保护回归，再修改候选 SQL／合成应用 guard；PM-CE-01 至 PM-CE-05 必须全部 PASS，P3-031/P3-044/P3-046 当前回归不得回退。整改通过仍不自动关闭风险，之后再决定隔离独立复评安排。
