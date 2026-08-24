# LIFEOS-P3-045 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-045
- 任务名称：Authorization 生命周期证据与终态历史边界合同
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-045_pm_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-045_LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract_local_precheck.md`（本地模型超时，按规则跳过）
- 任务验收状态：Accepted / Pass with Conditions
- 资产冻结状态：Accepted but Not Frozen / Engineering Contract Candidate
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-20

## PM 总结

- 交付物完整覆盖 AuditEntry 只追加、防预置／防重放、OutboxJob 业务载荷与运行态分离、Authorization generation／时间原子性、终态历史与用户清理边界，以及 DB／应用／事件投影职责分工。
- 三种实现方向比较成立；采用“数据库不变量 + 应用事务守卫”的方案 B，符合当前 SQLite 单机、非事件溯源的 V1 技术边界。
- `authorization_lifecycle_command` 被限定为非核心、只追加、单次消费的内部控制记录，用于让状态转换与 audit/outbox 在同一事务内生成，方向可接受，但新增前必须获得用户明确确认。
- AC-01 至 AC-18 可直接转化为后续候选 SQL 与合成空库合同测试；本任务没有把设计结论误写为已实现、风险关闭或 Schema/API 冻结。
- R-0048、R-0049 已由 Known Limitation 推进为 Contract Candidate，但仍保持开启。

## P3 快车道 Review

不适用。该任务涉及权限生命周期与证据可信度核心边界的设计判断，必须退出快车道采用完整 PM Review。

## 角色与关卡验收

- 主责角色覆盖情况：工程设计、数据完整性、安全边界与证据链职责均已覆盖。
- 协审角色覆盖情况：任务内完成方案反例、失败模式和边界自检；未进行独立评审。
- 已通过关卡：任务范围、交付物结构、方案比较、可测试性、风险映射、非范围声明。
- 未通过或需后续确认关卡：新增内部控制记录、tombstone 主题扩展、审计与清理最终口径；工程实现与独立风险关闭均未发生。
- 是否属于关键冻结事项：否；但它是 Schema/API 冻结前的高风险合同输入。
- 是否需要独立评审：本决策任务当前不强制；未来若据此关闭 R-0048/R-0049 或冻结 Schema/API，仍需相应独立证据与用户确认。
- 独立评审路径：无。
- 独立评审结论：N/A。
- 是否允许进入下一任务或下一阶段：用户确认条件包后允许创建窄范围工程实现任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：是，Pass with Conditions。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：生产 Schema/API、生命周期命令表、Authorization tombstone/cleanup 主题、AuditEntry/OutboxJob 最终实现、R-0048/R-0049。
- 是否允许进入下一任务：条件允许，须先取得用户确认。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：否，冻结状态没有变化。

## 必须保留的实施条件

1. `authorization_lifecycle_command` 只是一条数据库事务意图，不是安全主体，也不能单凭数据库字段证明“哪位真实用户完成了确认”。AuditEntry 最多证明候选数据库发生了某次状态转换；操作者真实性与 UI 确认仍由应用层负责。
2. 后续工程必须加入直接 SQL 伪造 command、重复 command、重放 idempotency key、跨 Authorization 复用、事务回滚、trigger 递归／顺序等负测，并验证 command 不可成为扩权入口。
3. “AuditEntry 严格只追加”与“用户清理”不得并存为相互矛盾的规则。优先方案是 AuditEntry 从创建时只保存最小、非敏感、可长期保留的 scoped reference；普通清理不得 UPDATE/DELETE 既有 AuditEntry。若未来确需审计脱敏，必须另立受控、可追踪且明确标记的例外流程。
4. terminal Authorization 及其 scope/action/policy 默认不可修改；用户清理采用确认后的 tombstone／单向清理，不得恢复 active，不得抹除最小终态事实，也不得把 OutboxJob 当成业务真相。

## 需要用户确认的事项

1. 是否采纳方案 B：数据库负责结构不变量与同事务生成证据，应用层负责真实用户确认、身份真实性和业务编排。PM 建议采纳。
2. 是否允许下一工程任务在候选 Schema 中新增非核心内部表 `authorization_lifecycle_command`。PM 建议允许，但严格受上述身份声明和防重放条件约束。
3. 是否允许把 `authorization` 加入 tombstone／受控清理 subject type。PM 建议允许，并采用“最小审计记录长期只追加、敏感载荷单向清理”的口径。
4. 是否同意上述三项作为一个条件包，确认后创建 P3-046 窄范围候选 SQL 与合同测试任务。未确认前不得创建或实施。

## 整改建议

本交付物无需返工。上述四项作为下一工程任务的强制输入，不要求在本任务内继续扩写。

## 可接受内容

- 方案 B 及 DB／应用／投影三层职责。
- active→terminal 单次合法转换、generation 恰好递增 1、DB 时间同事务落证。
- AuditEntry 作为只追加证据，OutboxJob 作为可重试投递运行态而非权威历史。
- terminal parent/children 默认不可变；清理为显式确认、单向且不复活。
- AC-01 至 AC-18 作为后续工程验收输入。

## 不接受或需谨慎内容

- 不得把 lifecycle command 中的 actor/confirmed 字段解释为已完成强身份认证。
- 不得一边宣称 AuditEntry 严格只追加，一边允许普通清理直接改写或删除审计行。
- 不得因合同已验收而关闭 R-0048/R-0049、冻结 Schema/API、启用真实 DB/Tauri/IPC 或进入下一阶段。

## 对项目文件的更新

- `lifeos/TASK_REGISTRY.md`：P3-045 更新为 Accepted / Pass with Conditions。
- `lifeos/DECISION_LOG.md`：新增 D-0226。
- `lifeos/RISK_LOG.md`：R-0048/R-0049 更新为 Open / Contract Candidate。
- `lifeos/CURRENT_STATUS.md`：切换为等待用户确认条件包。
- `lifeos/AGENT_ROUTING_SCORECARD.md`：记录 Codex 在本类高风险合同任务上的适配度。
- `lifeos/FREEZE_STATUS.md`：不更新。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex。
- 是否符合推荐：是。
- Agent 与任务类型匹配度：High。
- 主要优势：能把 SQLite 约束、应用确认、证据链、outbox 运行态和可执行测试合同连成闭环，且范围控制清楚。
- 主要问题：身份真实性声明与审计清理冲突需要 PM 增加强制护栏。
- 以后更适合分派给该 Agent 的任务类型：候选 Schema 合同、数据库不变量、权限生命周期、受控回归设计。
- 不建议分派给该 Agent 的任务类型：对自身后续高风险工程整改进行独立风险关闭评审。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：是。

## 下一步任务建议

用户确认四项条件包后，创建 P3-046：仅在候选 SQL、合成空库合同测试和本地 evidence 范围实现生命周期命令、原子 retirement evidence、terminal 不可变与受控清理约束。不得接入真实数据／真实数据库／真实 Tauri，不得自动关闭风险或冻结 Schema/API。
