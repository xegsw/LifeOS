# LIFEOS-P3-050｜Tombstone 向 Authorization 改绑整改全新隔离独立工程复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-050
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`
- 独立评审角色：独立 QA / Evidence Reviewer、技术架构负责人
- 协审视角：AI 信任与安全负责人、数据 / 领域模型负责人、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-050/independent_review.md`
- 评审结论：**Pass**
- 实际模型配置：`gpt-5.6-sol` + `xhigh`；派发证明记录首选可用、未降级、无后备模型。
- 更新时间：2026-08-21

## 评审摘要

- PM 派发证明与本会话记录一致：P3-050 为全新 Codex 任务 `01a02001-a5f2-7681-a2b8-e42f44a08efd`；首轮仅做隔离握手，正式启动后才读取项目材料。未继承其他 LifeOS 任务的范围、读取状态或工程执行上下文。
- P3-050 在读取 P3-049 独立 Review、脚本、结构化结果、日志和快照前，已独立写入攻击计划并封存 SHA-256；首轮自建脚本结果为 832 PASS、0 BYPASS、0 FAIL、0 Not Implemented、0 Unknown，退出码 0。
- 自建脚本只用 Python 标准库和候选 SQL，自行建立合成夹具；未 import、调用、复制或机械改写 P3-048/P3-049 的攻击函数、场景表或 runner helper。
- 直接攻击确认 generic→Authorization、Authorization→generic、Authorization A→B，六控制字段、六 cleanup 状态、NULL、状态/时间复合、冲突算法、DELETE/reinsert、多行和调用方 rollback 边界均 fail closed；合法 generic、no-op、cleanup retry、cleaned 终态路径未回退。
- 另一隔离副本复跑 P3-048 总入口为 552 PASS、P3-047 等价回归为 297 PASS、P3-031 为 70 PASS，均退出 0；原 P3-047 PM-CE-06 对当前候选 SQL 为 8 PASS / 0 BYPASS。
- P3-048 声明的 40 个 P3-046/P3-047 历史只读资产全部仍匹配 expected hash；历史 `0 PASS / 8 BYPASS` PM-CE-06 结果未被覆盖。
- P3-049 延迟资产只在本轮首轮计划与结果封存后才读取。其 488 PASS/0 bypass 与本轮结论一致，但不作为 P3-050 的独立性证明或主证据。

## 已通过内容

### 会话、证据与程序独立性

已验证事实：派发 Manifest 明确记录本任务通过新建 Codex 任务创建、并在 PM 完成派发证明后才获得正式启动指令。首轮计划、hash、独立脚本、首轮结构化结果、环境与封存记录均位于 P3-050 专属 Evidence；没有写入工程、历史 Review/Evidence 或 PM 账本。

已验证事实：首轮独立计划先于延迟 P3-049 攻击资产。`first_run_seal.md` 固化了计划、脚本、结果和环境 hash，记录首轮 832 个八配置实例全部通过。该顺序满足任务卡的核心反自证要求。

### Tombstone -> Authorization 合同

已验证事实：当前候选的 `authorization_tombstone_control_envelope_immutable` 对 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 使用 `UPDATE OF`，并在 OLD 或 NEW 任一侧属于 Authorization 时以 NULL 安全 `IS NOT` 比较拒绝变更。

已验证事实：三个 namespace/identity 方向、六字段单项和复合变异、六 cleanup 状态、NULL 变异、状态/时间组合、UPSERT/INSERT OR REPLACE/UPDATE OR REPLACE/冲突 INSERT/DELETE-reinsert 均没有形成可提交的改绑或控制包络伪造。每个拒绝路径均检查目标 Tombstone 行保持 before 快照。

已验证事实：多行攻击的非法行会使整个失败语句回滚；没有观察到 Authorization、AuditEntry、OutboxJob、Submission 或 Tombstone 半状态。文件 SQLite 配置的 `integrity_check`、`quick_check` 与 `foreign_key_check` 均通过。

### 回归与合法路径

已验证事实：generic Tombstone 的既有 generation/control/status 正向更新仍可用；Authorization protected-field no-op 仍可用；cleanup_failed/vendor_limited 到 cleanup_pending 的合法 retry 仍可用；满足受控清理条件后的 cleaned 路径可用，cleaned 后不能倒退。

已验证事实：隔离复跑 P3-048 为 552 PASS、P3-047 等价为 297 PASS、P3-031 为 70 PASS，所有入口无 FAIL/Not Implemented/Unknown。原 PM-CE-06 八配置攻击均被拒绝。

## 关键问题

未发现 P0、P1 或违反 Tombstone 自 INSERT 起不得改绑合同的 P2 bypass；未发现新增 P2 清洁项、Evidence/hash 冲突、只读资产覆盖或程序独立性缺口。

P3 观察：SQLite `RAISE(ABORT)` 只回滚失败语句。显式事务中更早的合法 generic 更新会保持待提交，调用方若需要撤销整个业务单元必须显式 `ROLLBACK`。本轮已验证拒绝语句本身没有修改 Authorization 或证据表，调用方 rollback 后完整恢复基线；此为已记录的事务语义，不构成当前合同 bypass。

## 必须整改项

无。

## 条件通过项

不适用。本结论为 Pass；候选 SQLite 受控边界和不可外推说明不是待整改条件。

## P0/P1/P2/P3 与退出码

| 项目 | 数量 / 状态 |
|---|---:|
| P0 bypass | 0 |
| P1 bypass | 0 |
| P2 bypass | 0 |
| 新增 P2 | 0 |
| P3 Observation | 1（显式事务调用方 rollback 边界） |
| Not Implemented | 0 |
| Unknown | 0 |
| P3-050 独立矩阵退出码 | 0 |
| P3-048 总入口退出码 | 0 |
| 原 PM-CE-06 退出码 | 0 |

## 关卡检查

- Gate 1 产品一致性评审：不适用；本任务未改变产品定位、V1 范围或产品资产。
- Gate 2 数据与来源评审：**Pass in Controlled Boundary**。Authorization cleanup Tombstone 的身份、generation、command、reason 与 blocked time 不能由 generic 历史改绑伪造；用户清理所需的历史与合法 cleanup 路径仍保留。
- Gate 3 AI 权限与信任评审：**Pass in Controlled Boundary**。已知撤回/清理证据包络的改绑路径 fail closed；未观察到控制包络或相关审计/队列/Submission 半状态。
- Gate 4 技术可行性评审：**Pass in Controlled Boundary**。候选 SQLite 的 OLD/NEW、UPDATE OF、NULL 安全比较、冲突算法、多行与事务边界均有独立可复现 Evidence。
- Gate 5 用户价值验证评审：不适用。

## 风险

- R-0048、R-0049 仍保持 Open / Remediation Candidate。本任务的 Pass 仅作为 PM 后续评估输入，不能自行关闭风险。
- P3-050 不构成真实 migration、生产并发、真实操作者认证、真实 DB/Vault/Tauri/IPC、备份恢复、外部模型或生产删除 SLA 的验证。
- P3-049 的程序独立性缺口不延续至 P3-050；但其历史结论不应被用于替代本轮自建 Evidence。

## 需要 PM 决策

1. 是否验收 P3-050 的 Pass 结论，并将其作为 P3-048/R-0049 后续决策输入。
2. 是否另行发起风险关闭、资产冻结、工程基线恢复或下一阶段任务；这些均不在本任务授权内，且本评审不提出自动推进。

## 最终建议

建议 PM 将 P3-050 评审结论按 **Pass** 验收：全新会话与延迟读取顺序可审计，独立攻击和隔离回归均通过，且历史 Evidence 未被覆盖。P3-048 资产仍应保持 Not Frozen，R-0048/R-0049 仍保持 Open，除非 PM 与用户在本任务之外作出明确决定。
