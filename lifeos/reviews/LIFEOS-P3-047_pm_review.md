# LIFEOS-P3-047 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-047
- 任务名称：Outbox CAS 与生命周期控制包络 P0 整改及回归
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md`
- 执行 Evidence：`lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md`
- PM Evidence：`lifeos/reviews/LIFEOS-P3-047/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-047_LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression_local_precheck.md`；`Skipped / Local Model Unavailable`，不影响 PM 人工验收
- PM Review：`lifeos/reviews/LIFEOS-P3-047_pm_review.md`
- 任务验收状态：Accepted / PM Adjusted to Rework
- 资产冻结状态：Rework / Not Frozen
- 是否允许进入下一任务：No；等待用户确认本 PM 结论并另行授权
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：Medium
- 更新时间：2026-08-20

## PM 总结

- 专项报告与执行 Evidence 完整；既有统计为 P3-047 297 PASS / 0 FAIL、P3-031 当前全量 69 PASS / 0 FAIL，上一 PM 会话在隔离临时副本复跑得到相同统计、总入口退出码 0，且 P3-046 只读失败基线保持不变。
- PM-CE-01、PM-CE-02、PM-CE-03、PM-CE-05 的候选整改和现有回归可以保留，作为 R-0048 的候选整改证据，但不等于风险关闭、独立复评通过或资产冻结。
- 静态核查发现 `authorization_tombstone_control_envelope_immutable` 仅在 `OLD.subject_type='authorization'` 时保护包络，未覆盖普通 Tombstone 向 Authorization Tombstone 的 UPDATE 改绑。
- 新增 PM-CE-06 / P2 在 memory / file、FK ON/OFF、recursive triggers ON/OFF 共 8 个配置中稳定得到 0 PASS / 8 BYPASS，入口退出码 1；改绑后 generation、command、reason、blocked time 均可被伪造。
- PM-CE-06 与任务卡 PM-CE-04“控制包络自 INSERT 起不可变、禁止改绑”属于同类明确验收缺口。因此原 297 条测试全部通过仍不足以判定工程整改通过，P3-047 必须校正为 Rework。
- R-0048 保持 Open，可标记为 Remediation Candidate；R-0049 保持 Open / Rework。任何风险均不关闭，任何资产均不冻结，不恢复工程基线，不进入下一阶段。

## P3 快车道 Review

不适用。本任务是 P0 整改，涉及权限撤回、删除历史与证据链；任务卡明确标记不适用快车道，且 PM 新增反例发现 P2 合同旁路，必须使用完整 Review。

## PM 复核与反例

- 既有可复现统计：P3-047 297 PASS / 0 FAIL；P3-031 69 PASS / 0 FAIL；总入口退出码 0；`READ_ONLY_PRESERVED=True`。
- PM-CE-06 命令：`python3 lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py`。
- PM-CE-06 结果：0 PASS / 8 BYPASS；P2 bypass=8；退出码 1。
- 八个实例均满足：改绑成功、`integrity_check=ok`、`foreign_key_check=[]`。
- 结构化结果：`lifeos/reviews/LIFEOS-P3-047/evidence/counterexample_results.json`。

## 必须整改的问题

### PM-CE-06 / P2：普通 Tombstone 可改绑为 Authorization Tombstone

当前不可变 trigger 只检查旧行已经是 Authorization 的情况。攻击者可先插入合法普通 Tombstone，再通过一次 UPDATE 把 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code` 与 `blocked_at_ms` 同时改写成一份伪造的 Authorization cleanup 控制包络。

整改必须覆盖：

- Tombstone 的身份与控制包络从 INSERT 起对所有 subject 类型不可变，或至少禁止任何向／从 Authorization 的改绑；不得只检查 OLD 已是 Authorization。
- UPDATE、复合 UPDATE、REPLACE／重建相邻路径和 cleanup 各状态均需 fail closed。
- 合法 cleanup_status / updated_at_ms 单向状态机不得因修复而回退。
- PM-CE-06 必须迁移为当前候选的受保护回归，并覆盖现有 8 配置矩阵。

## 角色与关卡验收

- 主责角色覆盖：技术实现、CAS、Submission/hash、retention 与原有 PM-CE-01 至 PM-CE-05 回归主体覆盖充分，但 Tombstone 自 INSERT 起不可变的实现不完整。
- 协审角色覆盖：执行侧 Evidence 结构完整；QA / Evidence Reviewer 未攻击 OLD 为普通类型的改绑路径，存在自证盲区。
- Gate 2 数据与来源评审：Rework；Authorization cleanup 历史身份和控制来源可被事后伪造。
- Gate 3 AI 权限与信任评审：Rework；授权撤回后的清理证据包络未完整 fail closed。
- Gate 4 技术可行性评审：Rework；原回归稳定但攻击集合不足以支持合同通过。
- 是否属于关键冻结事项：否；但属于风险关闭、Schema/API/migration/工程基线冻结前置高风险候选。
- 是否需要独立评审：是；整改经 PM 复跑通过后，仍须由与执行会话隔离的独立评审复核，才能讨论风险关闭或冻结。
- 是否允许进入下一任务：否；本轮不得创建或启动 P3-048。
- 是否允许进入下一阶段：否。

## 验收与冻结区分

- 任务是否完成交付：是，故任务层记录为 Accepted。
- 工程结论是否通过：否，PM Adjusted to Rework。
- 对应资产是否冻结：否，Rework / Not Frozen。
- 是否允许关闭 R-0048：否；仅可进入 Open / Remediation Candidate。
- 是否允许关闭 R-0049：否；保持 Open / Rework。
- 是否允许恢复／扩展工程基线：否。
- 是否允许启用真实能力：否。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：否，冻结状态没有变化。

## 需要用户确认的事项

- 是否采纳 P3-047 的最终 PM 结论 `Accepted / PM Adjusted to Rework`。PM 建议采纳。
- 本轮不请求自动创建 P3-048。只有用户明确采纳 Rework 并另行授权继续后，PM 才可创建针对 PM-CE-06 的窄整改任务。
- 不确认前的影响：P3-047 保持等待用户确认；不得推进后续任务、独立复评、风险关闭、资产冻结或阶段切换。

## 整改建议

- 后续窄整改只处理 PM-CE-06 及直接相邻的 Tombstone 改绑／替换路径，不重做 P3-047 已通过的 Outbox CAS、Submission/hash 或 retention 主体。
- 保留 P3-047 原执行 Evidence 和本 PM 反例 Evidence；不得改写 BYPASS 历史。
- 整改后复跑 P3-047 专项、P3-031 当前全量、PM-CE-06 八配置矩阵，并再次核对 P3-046 原失败基线未变化。

## 可接受内容

- Outbox runtime command 的 availability、owner、generation、lease expiry 与 subject generation CAS 候选方向。
- Submission/hash/lifecycle command 的 append-only 绑定候选方向。
- Authorization Outbox retention 的参数化、未配置默认拒绝与 generic job 作用域修正候选方向。
- P3-047 297 PASS、P3-031 69 PASS 与只读基线保留证据，作为下一轮窄整改的回归基线。

## 不接受或需谨慎内容

- 不接受“PM-CE-01 至 PM-CE-05 全部通过”作为 PM-CE-04 已完整关闭的最终证明。
- 不接受因 PM-CE-06 为 P2 而使用 Pass with Conditions；任务验收标准明确要求 Tombstone 包络自 INSERT 起不可变且 PM-CE-01 至 PM-CE-05 全部成立。
- 不得把合成 SQLite 结果外推到真实 migration、真实 DB、Vault、Tauri/IPC、生产并发、备份恢复、云或第三方能力。

## 对项目文件的更新

- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认 P3-047 Rework。
- `lifeos/TASK_REGISTRY.md`：P3-047 更新为 Accepted / PM Adjusted to Rework。
- `lifeos/DECISION_LOG.md`：新增 D-0230，记录 PM-CE-06 与等待用户确认边界。
- `lifeos/RISK_LOG.md`：R-0048 更新为 Open / Remediation Candidate；R-0049 保持 Open / Rework 并纳入 PM-CE-06。
- `lifeos/FREEZE_STATUS.md`：不更新。
- `lifeos/OPEN_QUESTIONS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex；符合推荐。
- 匹配度：Medium。
- 主要优势：复杂 SQL trigger、运行态 command、合成矩阵与 Evidence 组织完整，原五条 PM 反例的主体整改可复现。
- 主要问题：测试仍贴合 trigger 的已知 OLD=authorization 路径，遗漏“普通类型先插入、再改绑”的同合同反例。
- 后续工程窄整改仍可交给 Codex；独立复评不得由原执行会话自评。
- 本轮无需更新 `lifeos/AGENT_ROUTING_SCORECARD.md`；既有 Codex 工程执行强、反例独立性需外部隔离的路由结论不变。

## 下一步任务建议

等待用户确认，不创建或启动 P3-048。若用户明确采纳并授权继续，再由 PM 创建只处理 PM-CE-06 的窄整改任务；该任务完成并经 PM 复跑后，仍需隔离独立复评才能讨论 R-0048/R-0049 关闭或任何冻结。
