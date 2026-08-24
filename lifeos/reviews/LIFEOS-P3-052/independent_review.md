# LIFEOS-P3-052｜R-0048 生命周期证据全范围隔离独立复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-052
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review.md`
- 独立评审角色：独立 QA / Evidence Reviewer、AI 信任与安全负责人
- 协审视角：技术架构负责人、数据 / 领域模型负责人、风险关闭评估负责人
- 评审关卡：Gate 2、Gate 3、Gate 4
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-052/independent_review.md`
- 评审结论：**Rework**
- 更新时间：2026-08-21

## 评审摘要

- 本会话与任务卡的全新派发 ID 一致；未复用 P3-046 至 P3-051 或 PM 会话。先封存独立攻击计划及 SHA-256，再延迟读取历史攻击资产。
- 自建 runner 直接加载 P3-048 candidate SQL，未 import/call P3-047 runner 或历史 attack helper；23 逻辑用例在 memory/file × FK ON/OFF × recursive triggers ON/OFF 共 184 个实例中获得 152 PASS、32 BYPASS、0 FAIL、0 Unknown。
- P3-031 在隔离临时副本复跑为 70 PASS（P0 18、P1 27、P2 25），退出 0；这证明既有合同回归仍通过，但不覆盖本轮新发现的 provenance/replay 和初始值缺口。
- 在所有八配置中稳定复现两个 P1：可伪造并完成 lifecycle Outbox 投递；retention 删除后可重插相同 lifecycle job identity/idempotency 并改变 payload。
- 在所有八配置中稳定复现两个 P2：Authorization 可跳过初始 generation=1；可带预写 `revoked_at_ms` 进入 active。
- 所有文件型临时数据库的 `integrity_check`、`quick_check` 为 `ok`，`foreign_key_check` 为空；这不抵消上述业务/证据合同 bypass。
- P3-046/P3-047 历史失败 Evidence、当前 P3-048 输入与 Manifest 共 14 个只读文件 before/after SHA-256 一致；没有修改工程、历史 Evidence 或项目账本。

## 已通过内容

- Submission/hash 的格式与 Submission—lifecycle command 基本绑定、直接 retirement/generation/time 改写阻断、Audit/Submission/lifecycle command append-only、预置 audit/outbox 同 correlation 的失败语句回滚均在独立矩阵通过。
- future availability 领取、错误 owner/generation 的完成、过期租约的 complete/renew、payload/subject/idempotency 原位改写、retry 与 completed/cancelled/dead-letter 的单向状态机均按测试预期 fail closed 或保持合法运行态。
- 当前 PM-CE-01 至 PM-CE-05 的语义分别获得独立验证；P3-031 隔离回归也通过 PM-CE-01 至 PM-CE-06。Tombstone CE-04 仅作为回归确认，不构成对已关闭 R-0049 的重新判断。
- 显式事务、外层后续失败回滚、savepoint 回滚和多行失败语句均未留下 Authorization/Audit/Outbox/Submission 半状态。

## 关键问题

### P1-01：Outbox lifecycle provenance 可被直接伪造

已验证事实：`outbox_job_insert_contract` 只校验新 job 为 pending 初态，并不要求 `authorization_state_change` job 由匹配 lifecycle command 与 AuditEntry 同一事务派生。独立用例可在 active Authorization（generation=1）上直接插入 `authorization_state_change` job，随后用合法 runtime command claim 与 complete；`complete` 仅核对 Authorization generation，因此完成后 parent 仍为 active、无 lifecycle command、无 AuditEntry。

影响推断：非权威 Outbox 虽不直接改变 Authorization 权威状态，却能生成与权威状态不一致的“已完成状态变更投递”，破坏 R-0048 的 lifecycle evidence / delivery 可信度，并可能驱动下游错误的 fail-closed 行为。按任务卡 Outbox payload、审计和事务证据边界评为 P1。

### P1-02：retention 清理后 lifecycle Outbox 可复活并改写 payload

已验证事实：完成 lifecycle job 后，在 retention=0 的合成策略下受控 DELETE 可通过；但删除后 `outbox_job_insert_contract` 只查询仍存在的 outbox 行。即使 append-only `outbox_retention_binding` 和 runtime command 历史仍在，也可用同一 deleted job ID/idempotency key 重插 payload 已改变的 lifecycle job。

影响推断：保留期后的队列清理不应解除 lifecycle identity/replay 防线。该路径允许重复或篡改状态变更投递，因而仍是 P1 Outbox evidence / idempotency bypass。

### P2-01：Authorization 初始 generation 未锁定为 1

已验证事实：表约束仅为 `generation >= 1`，且 proposed→active 触发器不校验初始值。`generation=7` 的新 Authorization 可完成 scope/action/policy 配置并激活；八配置均复现。

影响推断：这违反 P3-045 “新 Authorization 从 generation=1 开始”的 lifecycle fencing 合同，削弱 generation 的可解释性与回放/证据一致性，评为明确 P2 bypass。

### P2-02：非 revoked 状态可携带预写 revoked_at_ms

已验证事实：Authorization 在 proposed INSERT 时可填入 `revoked_at_ms`，并在不改该字段的情况下激活。现有触发器只在该字段发生 UPDATE 时检查，不在 INSERT 或 active 转换时强制非 revoked 状态为 NULL；八配置均复现。

影响推断：这违反 P3-045 的 NULL/状态/转换时间配对合同，形成生命周期时间证据歧义，评为明确 P2 bypass。

## 必须整改项

1. 为 `authorization_state_change` Outbox 建立不可绕过的 provenance gate：其 INSERT 必须与对应 lifecycle command、terminal Authorization、唯一 AuditEntry、correlation/idempotency、subject generation 和 payload 在同一事务中可验证绑定；直接伪造行不得可 claim/complete。
2. 为 retention 删除后的 lifecycle job 保留 replay fence。删除后不得重用 lifecycle job ID/idempotency/correlation 或以新 payload 重建；同时保持 generic terminal job 的合法清理范围。
3. 在 Authorization INSERT/activation 合同中强制首次 generation=1，并拒绝非 revoked 状态的预写 `revoked_at_ms`；增加三终态、INSERT、activation、REPLACE/冲突及八配置负测。
4. 修复后必须由新的工程任务在合成边界回归 P3-031、PM-CE-01 至 PM-CE-05、上述四条 P3-052 反例与文件完整性；修复执行会话不得承担其独立复评。

## 条件通过项

不适用。任务卡规定任一 P0/P1、明确 P2 bypass 或 Evidence 冲突即为 Rework；本轮有 2 个 P1 与 2 个 P2。

## 关卡检查

- Gate 1 产品一致性评审：不适用；本任务没有改变产品定位、范围或体验资产。
- Gate 2 数据与来源评审：**Rework**。Audit/Outbox/Submission 的生命周期证据仍可出现未经 command/audit 派生的 Outbox，以及已清理 job 的重放；generation/time 初始语义也不完整。
- Gate 3 AI 权限与信任评审：**Rework**。状态变更投递可与 Authorization 权威状态不一致，影响撤回、失效和下游行为可解释性；不满足风险关闭前的 fail-closed 证据要求。
- Gate 4 技术可行性评审：**Rework**。SQLite 八配置与文件完整性可复现，但候选实现尚不能满足完整 lifecycle / idempotency / retention 合同。
- Gate 5 用户价值验证评审：不适用。

## 风险

- R-0048 必须保持 **Open / Remediation Candidate**；本文件不执行风险关闭。
- 已关闭 R-0049 不在本轮结论范围内，未被关闭、重开或改变。对 Tombstone 的回归验证不能取代任何 R-0049 决策。
- 当前结论仅适用于候选 SQL 与合成 SQLite；不外推到真实 migration、真实 DB/Vault/Tauri/IPC、真实身份认证、并发、备份恢复、云/第三方模型或生产 SLA。

## 需要 PM 决策

1. 是否采纳本独立结论 **Rework**，并将 P1-01/P1-02/P2-01/P2-02 作为 R-0048 后续窄整改的输入。
2. 后续若创建整改任务，需 PM 重新限定工程目录、独立复评隔离与模型路由；本会话不创建、不修改工程，也不建议在修复前进入风险关闭讨论。

## 最终建议

建议 PM 将 LIFEOS-P3-052 验收为“任务交付完成、独立评审结论 Rework”。候选资产继续 Not Frozen；不允许关闭 R-0048、恢复基线、启用真实能力或进入下一阶段。优先修复两条 P1 Outbox provenance/replay 缺口，再处理两条 P2 初始 lifecycle 约束，并在新的隔离独立复评中重新判断。
