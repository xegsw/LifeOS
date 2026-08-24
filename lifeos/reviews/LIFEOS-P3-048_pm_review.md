# LIFEOS-P3-048 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-048
- 任务名称：Tombstone 向 Authorization 改绑旁路 P2 整改及回归
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`
- 执行 Evidence：`lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-048/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-048_LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression_local_precheck.md`；`Skipped / Local Model Unavailable`，不影响 PM 人工验收
- PM Review：`lifeos/reviews/LIFEOS-P3-048_pm_review.md`
- 任务验收状态：Accepted / Remediation Regression Passed
- 资产冻结状态：Accepted but Not Frozen / Pending Independent Re-review
- 是否允许进入下一任务：Conditional；用户确认后只允许创建隔离独立复评任务
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-20

## PM 总结

- P3-048 按授权范围只修改 Tombstone trigger、P3-031 直接相关合同测试／evidence，并创建自身 runner/evidence；未重写 P3-047 已通过的 Outbox CAS、Submission/hash 或 retention 主体。
- 修复把控制包络保护从仅 `OLD.subject_type='authorization'` 扩展为 OLD 或 NEW 任一侧涉及 Authorization，关闭 generic→Authorization、Authorization→generic 和 Authorization A→B 改绑根因，同时保留 generic Tombstone 既有合法语义。
- PM 隔离复跑总入口：P3-048 552 PASS、P3-047 等价 297 PASS、P3-031 70 PASS，均无 FAIL/Not Implemented/Unknown，总入口退出码 0。
- PM 在隔离副本直接运行 P3-047 原 PM-CE-06 脚本攻击新 SQL，得到 8 PASS / 0 BYPASS、退出码 0；八配置均被目标 trigger 拒绝。
- 40/40 个 P3-047/P3-046 只读文件 hash 保持一致；旧 `0 PASS / 8 BYPASS` 与 P3-046 原失败 Evidence 未被改写。
- 未发现新增 P0/P1/P2 旁路。P3-048 可在合成 SQLite 边界内验收通过，但仍需用户确认与隔离独立复评；R-0048/R-0049 不关闭，资产不冻结。

## P3 快车道 Review

不适用。本任务属于 P0 整改链，涉及权限撤回、删除历史与证据链，任务卡明确标记不适用快车道。

## PM 独立复跑

- 隔离目录：`/tmp/lifeos-p3048-pm.eOuqsz`。
- 总入口：`sh lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.sh`。
- P3-048：P2 552 PASS，0 FAIL/Not Implemented/Unknown。
- P3-047 当前协议等价回归：P1 144 + P2 153 = 297 PASS，0 FAIL/Not Implemented/Unknown。
- P3-031：P0 18 + P1 27 + P2 25 = 70 PASS，0 FAIL/Not Implemented，退出码 0。
- 只读保留：40/40 unchanged。
- 原 PM-CE-06 直接攻击：8 PASS / 0 BYPASS，退出码 0。

## 角色与关卡验收

- 主责角色覆盖：根因、最小 trigger 补丁、OLD/NEW 双侧责任、替换／重建、多行原子性和合法路径均有可运行证据。
- 协审角色覆盖：AI 信任与安全、数据／领域语义、QA/Evidence 的关键检查点均在合成边界内覆盖；报告明确 SQLite 不认证真实操作者。
- Gate 2 数据与来源评审：Pass in Controlled Boundary；Authorization cleanup 历史身份与控制包络的已知改绑旁路关闭。
- Gate 3 AI 权限与信任评审：Pass in Controlled Boundary；撤回／清理证据不再可通过已知 generic 改绑路径伪造。
- Gate 4 技术可行性评审：Pass in Controlled Boundary；专项、等价回归、全量回归与文件完整性均可复现。
- 是否属于关键冻结事项：否；但属于风险关闭、Schema/API/migration/工程基线冻结前置高风险候选。
- 是否需要独立评审：是；必须由与 P3-048 执行会话隔离的评审会话复核。
- 是否允许进入下一任务：用户确认后，仅允许创建隔离独立复评任务。
- 是否允许进入下一阶段：No。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted / Remediation Regression Passed。
- 工程结论是否通过：在所列合成 SQLite 受控边界内通过。
- 对应资产是否冻结：否，Accepted but Not Frozen / Pending Independent Re-review。
- 是否允许关闭 R-0048：否，保持 Open / Remediation Candidate。
- 是否允许关闭 R-0049：否；可进入 Open / Remediation Candidate。
- 是否允许恢复／扩展工程基线：否。
- 是否允许启用真实能力：否。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：否，冻结状态没有变化。

## 需要用户确认的事项

- 是否采纳 P3-048 的 `Accepted / Remediation Regression Passed` 结论。PM 建议采纳。
- 采纳后是否创建隔离独立复评任务。PM 建议创建，并由不同于 P3-048 执行会话的独立评审会话承担。
- 不确认前的影响：P3-048 保持等待用户确认；不得关闭 R-0048/R-0049、冻结资产、恢复工程基线、启用真实能力或进入下一阶段。

## 整改建议

无本轮阻断整改项。后续隔离独立复评应重点重跑原 PM-CE-06，并独立攻击 OLD/NEW 类型组合、六状态、复合 UPDATE、UPSERT/REPLACE、多行原子性和 generic 合法语义，避免仅复述执行侧 runner。

## 可接受内容

- OLD 或 NEW 任一侧涉及 Authorization 时冻结六字段控制包络的候选 SQL 不变量。
- generic Tombstone 不被全局冻结的最小补丁边界。
- P3-048 552、P3-047 等价 297、P3-031 70 条通过结果和 40 文件只读保留证据，作为隔离独立复评输入。

## 不接受或需谨慎内容

- 不得把合成 SQLite 结果外推为真实 migration、生产并发、真实调用者认证、真实 DB/Vault/Tauri/IPC 或生产删除 SLA 通过。
- 不得把任务 Accepted 自动解释为 R-0048/R-0049 关闭、Schema/API/migration/工程基线冻结或阶段推进。
- 执行会话不得独立评审自己的结果。

## 对项目文件的更新

- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认 P3-048 验收结论。
- `lifeos/TASK_REGISTRY.md`：P3-048 更新为 Accepted but Not Frozen / Pending Independent Re-review。
- `lifeos/DECISION_LOG.md`：新增 D-0232，记录 PM 验收与用户确认边界。
- `lifeos/RISK_LOG.md`：R-0048 保持 Open / Remediation Candidate；R-0049 更新为 Open / Remediation Candidate。
- `lifeos/FREEZE_STATUS.md`：不更新。
- `lifeos/OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex；符合推荐。
- 匹配度：High。
- 主要优势：补丁保持单根因范围，攻击矩阵覆盖 OLD/NEW、状态、字段、替换、多行和合法路径，Evidence 可复现且旧失败基线保护完整。
- 主要问题：无阻断问题；最终独立性仍不能由执行侧自证。
- 后续独立复评应交给隔离评审会话，不建议继续由本 Codex 执行会话承担。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No；当前表现符合既有 Codex 工程整改路由。

## 下一步任务建议

等待用户确认，不在本轮创建后续任务。若用户采纳并授权继续，再创建 P3-049 隔离独立工程复评；该复评仍不得自动关闭风险、冻结资产、恢复工程基线或进入下一阶段。
