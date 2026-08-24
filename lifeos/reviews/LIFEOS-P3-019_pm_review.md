# LIFEOS-P3-019 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-019
- 任务名称：P1-7 条件补丁：授权 `expires_at` 与 `retract_feedback`
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-019_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-11

## PM 总结

- P3-019 按任务卡完成 P1-7：Authorization 新增可空 `expires_at_ms`，并由统一消费门 `canConsume()` 通过确定性 `nowMs` 进行过期判断。
- PM 使用 Codex bundled Node v24.14.0 复跑 `node scripts/validate.mjs`，结果为 **34 PASS / 0 FAIL / P0=0**，与交付报告和 evidence manifest 一致。
- 已验证新增 P1-7 覆盖为 **4/4 PASS**：无期限 / 未过期授权放行、过期授权阻断所有已实现消费和写入口、feedback 显式幂等撤回、撤回后不复活 stale / invalid / 过期 Derivation。
- 原有回归 **30/30 PASS**；P1-6、P1-8、P1-4、P3-015、P1-3 / P1-5 回归均保持通过。
- 本任务没有启用真实时间服务、后台调度、真实 UI、真实审计、真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 本任务不关闭 R-0040，不恢复或冻结新的工程基线，不进入下一阶段。

## P3 快车道 Review

- 是否适用 P3 快车道：Yes
- 验收结论：Accepted
- 测试复跑摘要：PM 复跑 `cd lifeos/engineering/LIFEOS-P3-009 && /Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs`，结果 34 PASS / 0 FAIL / P0=0。
- 是否存在 P0：No
- P1 / P2 是否可留在快车道：Yes，本任务是受控 P1 窄补丁，未触发退出条件。
- 风险状态是否变化：R-0040 保持 Open / Conditional；R-0041 / R-0042 保持 Closed。
- 是否触发用户确认：No。未涉及 P0 采纳、风险关闭、工程基线恢复、真实能力启用、阶段切换或关键边界变更。
- 是否允许继续下一工程补丁：Conditional。若只是继续低风险 P1/P2 清洁补丁可留在快车道；但当前 P1-3 至 P1-8 已形成一组迁移完成候选，下一步更建议做独立覆盖复评，而不是继续散补。
- 修改文件：专项会话修改 `lifeos/engineering/LIFEOS-P3-009/src/store.ts`、`src/consumption-gate.ts`、`src/lifeos.ts`、`tests/invariants.test.ts`、`scripts/validate.mjs`、`evidence/`；未修改 `src/types.ts`、`lifeos/engineering/LIFEOS-P3-001/` 或 PM 账本。
- evidence 路径：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- Agent 适配度记录：Codex 与 P3 快车道工程补丁匹配度 High；范围纪律、工程执行、测试复跑、evidence 整理均符合要求。
- 是否必须退出快车道：No。但后续如要关闭 R-0040、恢复/冻结工程基线扩展，必须退出快车道并走独立复评 + 用户确认。

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人覆盖。补丁集中在统一消费门、授权 schema、feedback 撤回语义、测试和 evidence 更新；未引入真实时间服务或调度器。
- 协审角色覆盖情况：数据与权限、AI 信任与安全、QA / 测试、技术架构均有覆盖。
- 已通过关卡：P1-7 授权过期；P1-7 feedback 撤回；P1-6 restore candidates 回归；P1-8 suggestion ID 回归；P1-4 staling 回归；P3-015 suggest 旧候选消费门回归；P1-3 / P1-5 回归；H1-H9 / T-ARCH 回归；evidence manifest 更新；默认关闭能力回归。
- 未通过或需后续确认关卡：真实时间权威、正式权限策略、多设备同步、真实 UI / 审计、真实 Tauri / IPC、真实数据均未验证；R-0040 未关闭。
- 是否属于关键冻结事项：No，本任务不是技术架构冻结、MVP 准入、风险关闭或工程基线恢复。
- 是否需要独立评审：当前任务本身 No；若要以 P1-3 至 P1-8 迁移完成作为 R-0040 关闭或工程基线扩展依据，则需要独立工程覆盖复评。
- 独立评审路径：Not Applicable
- 独立评审结论：Not Applicable
- 是否允许进入下一任务或下一阶段：允许进入下一任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No，Accepted but Not Frozen。
- 冻结范围：无。
- 未冻结内容：生产 Schema / API、正式权限策略、真实时间权威、真实 UI / 审计、真实 Tauri / IPC、真实 Vault、真实数据、真实导出 / 恢复格式、工程基线扩展、R-0040 关闭。
- 是否允许进入下一任务：Conditional，建议启动 P1 迁移完成后的独立覆盖复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，更新 P1-7 为 Accepted。

## 需要用户确认的事项

- 问题：是否启动 P1-3 至 P1-8 迁移完成后的独立工程覆盖复评。
  - PM 建议：启动，推荐 WorkBuddy 执行，只读复核 P3-009 当前 34 项测试、evidence 一致性和 P1-3 至 P1-8 是否仍存在覆盖差距。
  - 可选方向：A. 启动独立覆盖复评；B. 继续在快车道内找 P2 清洁项；C. 暂停工程补丁，转向 UI / PRD / IA。
  - 不确认的影响：R-0040 不能关闭，P3-009 工程基线扩展不能恢复或冻结。

## 整改建议

无必须返工项。

## 可接受内容

- `expires_at_ms` 作为当前 P3-009 受控 Authorization 的最小过期字段。
- `canConsume()` 将未过期 allow 作为唯一可消费授权；过期、deny、缺失、重复、generation mismatch 均 fail closed。
- `retractFeedback(feedbackId, "user")` 作为受控显式撤回入口；撤回保留 feedback 记录并将 confirmed / edited_confirmed Derivation 移出可消费状态。
- `feedback_retracted` 作为当前受控测试包内的非可消费 Derivation 状态。

## 不接受或需谨慎内容

- 不得把 P3-019 解释为真实时间权威、后台调度、正式审计 UI 或多设备授权同步已完成。
- 不得把 34/34 合成测试通过外推为真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型或生产 SLA 通过。
- 不得关闭 R-0040，不得恢复或冻结新的工程基线扩展。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：更新 P3-019 为 Accepted。
- `lifeos/FREEZE_STATUS.md`：更新 P1-7 授权过期与 feedback 撤回为 Accepted but Not Frozen。
- `lifeos/CURRENT_STATUS.md`：更新当前任务状态与下一步建议。
- `lifeos/DECISION_LOG.md`：新增 PM 接受 P3-019 的决策。
- `lifeos/RISK_LOG.md`：不更新；R-0040 仍保持 Open / Conditional。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：窄范围工程实现、确定性测试、evidence 更新、非范围声明清楚。
- 主要问题：本地预检依赖的局域网模型不可用，但专项会话已记录跳过原因；不影响 PM 验收。
- 以后更适合分派给该 Agent 的任务类型：P3 快车道工程补丁、测试回归、evidence 整理。
- 不建议分派给该 Agent 的任务类型：独立复评自己刚完成的工程、风险关闭最终判断。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No，本次观察与既有分派规则一致。

## 下一步任务建议

建议启动 `LIFEOS-P3-020`：P3-009 P1 迁移完成独立工程覆盖复评。

目的不是继续写代码，而是让独立评审确认 P1-3 / P1-4 / P1-5 / P1-6 / P1-7 / P1-8 是否在当前 P3-009 受控边界内真实闭合，并判断是否仍存在阻止 R-0040 后续关闭或工程基线扩展恢复的 P0 / P1。

## 聊天回复边界

PM 主会话在聊天中只输出验收结论、资产状态、是否允许下一步 / 下一阶段、修改文件和需要用户确认的问题；不复述完整 Review。
