# LIFEOS-P3-053｜R-0048 Outbox 来源／重放与生命周期初始值整改

## 任务信息

- 任务 ID：LIFEOS-P3-053
- 类型：R-0048 窄范围候选 SQL 整改与回归
- 执行配置：Codex，`gpt-5.6-terra` + `xhigh`；未降级、未使用后备模型。
- 授权范围：仅 P3-031 候选 SQL、相关合同测试/runner 与 P3-053 deliverable/evidence；仅合成 SQLite。
- 未修改：任何 PM 主账本、P3-046 至 P3-052 历史任务/Review/Evidence、R-0049、冻结状态与工程基线。

## 已验证事实

### 1. Outbox provenance P1 已在候选合同中整改

`authorization_state_change` 的 INSERT trigger 现拒绝非 Authorization subject，并要求该行与同一 lifecycle correlation 的 canonical command、terminal Authorization、唯一 AuditEntry、Submission、generation、terminal payload、available time、canonical job id 和 idempotency 一致。正常 lifecycle command 的 trigger 顺序为：终态 Authorization → AuditEntry → canonical Outbox；任何人为直接 INSERT 无法提供 active 状态下的来源证据，终态时则与 canonical identity 冲突。

`P3-052-P1-01` 同时验证普通 INSERT 和 `INSERT OR REPLACE` 的伪造行均被拒绝；合法 lifecycle command 仍产生完整 command/audit/outbox 绑定。

### 2. retention 后 replay P1 已在候选合同中整改

`outbox_retention_binding` 新增不可重用的 lifecycle correlation fence。具备 retention 资格的 lifecycle job 删除后，binding 保留；任何复用原 job id 或 correlation/idempotency 的 lifecycle 或 generic Outbox INSERT 均被拒绝。普通 generic terminal job 仍可按原有合法路径完成并清理。

`P3-052-P1-02` 验证 retention=0 的合成清理可完成、fence 会保留、篡改 payload 的重插和 generic correlation 复用均被拒绝，且无关 generic terminal cleanup 未被收紧。

### 3. lifecycle 初始值 P2 已在候选合同中整改

Authorization 的 INSERT / `INSERT OR REPLACE` 必须从 `generation=1` 开始；每次 activation 再次校验 generation 仍为 1。所有非 revoked 初始状态不得预写 `revoked_at_ms`，activation 同样拒绝该值。既有 lifecycle transition 合同继续控制 terminal generation/time：合法 revoked 为 `generation=2` 且 `revoked_at_ms=updated_at_ms`；expired/superseded 的 revoked time 为 NULL。

`P3-052-P2-01` 覆盖 INSERT、REPLACE/conflict 与 activation 的 initial-generation 旁路。`P3-052-P2-02` 覆盖相同入口的 revoked-time 旁路及三类 terminal pairing。

### 4. 回归与八配置结果

- P3-031 全量合同回归：74 PASS / 0 FAIL / 0 Not Implemented（P0=18、P1=29、P2=27）。
- 八配置矩阵：11 个目标用例在 memory/file × FK OFF/ON × recursive triggers OFF/ON 的 88 次执行中均 PASS。
- 矩阵包含四条 P3-052 反例、PM-CE-01 至 PM-CE-05、`AC-14` 原子 lifecycle 与 `AC-16` evidence-conflict rollback。
- 文件模式共验证 72 个持久化合成 DB；每个 close/reopen 后 `integrity_check` 与 `quick_check` 为 `ok`，`foreign_key_check` 为空。

完整证据入口：[MANIFEST.md](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-053/evidence/MANIFEST.md)。

## 合理推断

在候选 SQL 与合成 SQLite 的限定边界内，P3-052 识别的两项 Outbox P1 和两项 lifecycle initial-value P2 已获得可重复的整改证据。provenance 与 retention fence 均通过证据表约束、canonical identity 与 append-only binding 形成 fail-closed 路径，而非依赖测试 runner 的单独判断。

这项推断不外推到真实 migration、非空旧库、真实用户数据、并发、多进程、备份/恢复、Vault、Tauri/IPC、云端或生产 SLA。

## 角色与关卡自检

- 技术架构负责人：候选 trigger/表约束、原子回滚和八配置/文件可行性已覆盖；Gate 4 在本地候选自检范围内通过，仍待独立复评确认。
- AI 信任与安全负责人：Authorization terminal evidence、Outbox 来源和重放均被 fail-closed 约束；Gate 3 在本地候选自检范围内通过，未改变 AI 权限边界。
- QA / Evidence Reviewer：四条新反例、PM-CE-01 至 PM-CE-05、P3-031 全量回归、事务原子性与文件完整性均有可读证据；Gate 2 在本地候选自检范围内通过，仍待隔离独立验证。

## 风险与限制

- R-0048 必须保持 **Open**；本任务不关闭风险。
- R-0049 保持 **Closed / Limited Controlled Boundary**，本任务没有重新打开或改变其结论。
- 候选 SQL、Schema/API、工程基线均保持 Not Frozen；本任务不进入下一阶段。
- P3-052 及此前历史 Review/Evidence 是只读输入；当前读取 hash 已记录在本任务 evidence，不替代历史资产的原始 hash manifest。

## 建议与需要 PM 确认

建议 PM 仅将本结果作为下一次全新隔离独立复评的工程输入。该复评必须不复用本执行会话、不得由本执行 Agent 自评，并独立构造 provenance/replay/initial-value 反例，复跑八配置、P3-031 回归和文件完整性。PM 在读取该复评后再判断任务验收与 R-0048 的后续处理；本报告不提出风险关闭或冻结建议。

## Evidence

- [P3-053 evidence manifest](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-053/evidence/MANIFEST.md)
- [P3-031 full regression results](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-053/evidence/p3_031_regression_results.json)
- [P3-053 lifecycle matrix results](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-053/evidence/lifecycle_matrix_results.json)
