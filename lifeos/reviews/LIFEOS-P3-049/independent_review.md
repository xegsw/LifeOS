# LIFEOS-P3-049｜Tombstone 向 Authorization 改绑整改隔离独立工程复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-049
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`
- 独立评审角色：独立 QA / Evidence Reviewer、技术架构负责人
- 协审视角：AI 信任与安全负责人、数据 / 领域模型负责人、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-049/independent_review.md`
- 评审结论：**Pass**
- 实际模型：`gpt-5.6-sol` + `xhigh`；首选可用，未降级
- 更新时间：2026-08-20

## 最终结论与独立性声明

本轮结论为 **Pass**。在候选 SQLite、合成数据、单进程、隔离临时副本边界内，P3-048 已关闭 P3-047 的 PM-CE-06：普通 Tombstone 不能经 UPDATE 改绑为 Authorization Tombstone；Authorization Tombstone 也不能离开 Authorization namespace、改绑另一 Authorization 或改写六字段控制包络。独立反例未发现 P0、P1 或违反明确合同的 P2 bypass，合法 generic 与 Authorization cleanup 路径未回退。

本评审会话未参与 P3-046、P3-047 或 P3-048 工程实现，也未导入或调用 P3-048/P3-047 runner 的 helper。历史 runner 仅在 `/tmp/lifeos-p3049-review.2M82rP/workspace` 隔离副本复跑；独立攻击由本任务新建的 `independent_counterexample_attacks.py` 实现。源工作区候选 SQL、测试、runner、工程 Evidence、历史 PM Evidence 和项目账本均只读。

本结论只证明任务卡列明的受控候选边界，不代表 R-0048/R-0049 已关闭，不代表 Schema/API/migration/工程基线冻结，也不代表真实 migration、真实数据库、真实操作者认证、Tauri/IPC、生产并发或删除 SLA 已验证。

## 评审摘要

- 隔离总入口复现 P3-048 552 PASS、P3-047 当前协议等价 297 PASS、P3-031 70 PASS；三组均无 FAIL/Not Implemented/Unknown，总入口退出码 0，`READ_ONLY_PRESERVED=True`。
- 原 P3-047 PM-CE-06 脚本直接攻击新候选 SQL得到 8 PASS / 0 BYPASS，八配置均由 `authorization_tombstone_control_envelope_immutable` 拒绝。
- 独立攻击共 61 个逻辑场景、八配置 488 个实例：488 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown。
- 六控制字段 × 六 cleanup 状态形成 36 个逻辑场景、288 个实例，全部由目标包络 guard fail closed；OLD/NEW 三类改绑方向 24/24 PASS。
- UPSERT、INSERT OR REPLACE、冲突 INSERT、UPDATE OR REPLACE、DELETE/reinsert、多行 UPDATE 与显式事务回滚共 72 个实例全部通过；未出现 Authorization、AuditEntry、OutboxJob、Submission 或 Tombstone 半状态。
- 244 个独立文件型 SQLite 实例全部 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。
- 40/40 个 P3-048 声明只读文件与 expected hash 一致；14 个关键 P3-048 Evidence 文件与 manifest 声明 hash 一致；未发现 evidence/统计冲突。

## 方法、统计与证据

### 隔离回归

| 入口 | P0 PASS | P1 PASS | P2 PASS | Total PASS | FAIL / NI / Unknown | 退出码 |
|---|---:|---:|---:|---:|---:|---:|
| P3-048 专项 | 0 | 0 | 552 | 552 | 0 | 0 |
| P3-047 当前协议等价 | 0 | 144 | 153 | 297 | 0 | 0 |
| P3-031 当前全量 | 18 | 27 | 25 | 70 | 0 | 0 |
| 原 PM-CE-06 攻击新候选 | 0 | 0 | 8 | 8 | 0 BYPASS | 0 |

详细日志与结构化结果位于 `evidence/regressions/`。复跑未在源工作区执行，因而没有覆盖 P3-031、P3-047 或 P3-048 原 Evidence。

### 独立反例

| 类别 | 逻辑场景 | 八配置实例 | PASS | BYPASS / FAIL / NI / Unknown |
|---|---:|---:|---:|---:|
| OLD/NEW：generic→Authorization、Authorization→generic、A→B | 3 | 24 | 24 | 0 |
| 六字段 × 六 cleanup 状态 | 36 | 288 | 288 | 0 |
| 六字段 NULL 写入（Schema 全部 NOT NULL） | 6 | 48 | 48 | 0 |
| 身份/包络 + cleanup_status + updated_at 同语句 | 6 | 48 | 48 | 0 |
| UPSERT/REPLACE/冲突/DELETE/reinsert | 7 | 56 | 56 | 0 |
| 多行与显式事务原子性 | 2 | 16 | 16 | 0 |
| 合法 generic/no-op/cleanup trace | 1 | 8 | 8 | 0 |
| **合计** | **61** | **488** | **488** | **0** |

配置为 memory/file × foreign_keys ON/OFF × recursive_triggers ON/OFF。六控制字段是 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms`；六状态是 accepted、active_blocked、cleanup_pending、cleanup_failed、vendor_limited、cleaned。

独立脚本没有把“被任一 trigger 拒绝”等同于目标 guard 已验证：六字段直接攻击明确要求错误包含 `authorization_tombstone_control_envelope_immutable`。多行复合语句在当前创建顺序下先由 `authorization_tombstone_time_requires_status_change` 拒绝；快照证明整句回滚，而直接字段矩阵另行证明目标 guard 自身生效。这是 cross-trigger 首错误观察，不是 bypass，也不依赖 SQLite 未承诺的 trigger 执行顺序。

显式事务探针同时记录 SQLite `RAISE(ABORT)` 的语义：失败只终止当前语句，事务中更早的合法 generic 更新仍保持 pending；应用显式 rollback 后整个事务恢复基线。被拒绝语句本身从未改动 Authorization 或证据表。这是标准事务边界观察，不削弱当前安全合同。

## 已通过内容

1. 目标 trigger 的 `UPDATE OF` 列表完整包含六控制字段，WHEN 同时覆盖 `OLD.subject_type='authorization'` 与 `NEW.subject_type='authorization'`，六字段使用 NULL 安全 `IS NOT` 比较。
2. generic→Authorization、Authorization→generic、Authorization A→B 均在八配置下 fail closed；没有依赖 FK 或 recursive trigger 设置。
3. accepted 至 cleaned 六状态上的单字段、复合字段、状态/时间组合均 fail closed。
4. UPSERT/REPLACE/冲突 INSERT 由 INSERT contract 或目标 UPDATE guard 拒绝；DELETE 在 reinsert 前被 `tombstone_no_delete` 拒绝。
5. 多行 UPDATE 失败时整句原子回滚；Authorization、AuditEntry、OutboxJob、Submission 与 Tombstone 快照无半状态。
6. generic Tombstone 现有身份/控制字段更新语义、Authorization no-op、合法 cleanup retry 和 cleaned 路径仍可用。
7. P3-048 报告、manifest、关键 Evidence hash、统计和隔离复跑相互一致。

## 关键问题

未发现阻断 P3-048 受控候选结论的 P0/P1/P2 问题。

需保留两项边界说明：SQLite 不保证多个同类 trigger 的跨 trigger 执行顺序；应用层若在显式事务中捕获 ABORT 后希望撤销先前语句，必须显式 rollback。两项均未形成 Authorization 改绑或证据半状态，不构成本任务的新风险项。

## 必须整改项

无。

## 条件通过项

不适用；本轮为 Pass。不可外推边界不是待整改条件。

## P0/P1/P2 分类

- P0：0。
- P1：0。
- P2 bypass：0。
- 新增 P2 清洁项：0。
- P3 观察：2（cross-trigger 首错误不稳定；显式事务 ABORT 需调用方 rollback）。
- Not Implemented：0。
- Unknown：0。

## 关卡检查

- Gate 1 产品一致性评审：不适用，本任务不改变产品定位或 V1 范围。
- Gate 2 数据与来源评审：**Pass in Controlled Boundary**。Authorization cleanup Tombstone 的 subject 身份、generation、command、reason 与 blocked time 不能由 generic 历史改绑伪造；合法 cleanup 历史保留。
- Gate 3 AI 权限与信任评审：**Pass in Controlled Boundary**。已知撤回/清理证据改绑路径关闭，未观察到 Authorization、AuditEntry、OutboxJob 或 Submission 半状态。
- Gate 4 技术可行性评审：**Pass in Controlled Boundary**。隔离回归、独立八配置攻击、替换语义、事务原子性及文件完整性全部可复现。
- Gate 5 用户价值验证评审：不适用。

## 风险

- R-0049：本评审支持将 P3-048 候选整改作为后续风险关闭条件评估输入；风险仍须保持 Open / Remediation Candidate，是否关闭只能由 PM/用户另行决定。
- R-0048：P3-047 等价回归虽复现通过，但本任务独立攻击重点是 Tombstone 改绑，不构成 Outbox CAS、Submission/hash 与 retention 全主题的独立风险关闭评审；继续保持 Open / Remediation Candidate。
- R-0040、R-0043、R-0044、R-0046、R-0047、R-0050 及 R-0045 状态均不由本任务改变。

## 需要 PM 决策

1. 是否采纳 P3-049 的 Pass 结论。
2. 是否将本评审作为 R-0049 后续风险关闭条件评估输入；本会话不关闭风险。
3. 是否保留两项 P3 事务/trigger 顺序观察为工程说明；不建议将其上调为 P2。

## 最终建议

建议 PM 接受 P3-049 为 **Pass**，并保持资产 **Not Frozen**、R-0048/R-0049 **Open**。是否进行风险关闭、Schema/API/migration/工程基线冻结或任何后续任务，必须由 PM/用户另行决策。本会话不恢复工程基线、不启用真实能力、不进入下一阶段，也不自行启动后续任务。
