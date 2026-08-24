# LIFEOS-P3-048｜Tombstone 向 Authorization 改绑旁路 P2 整改及回归

## 任务信息

- 执行 Agent：Codex 专项工程执行会话，不是 PM 或独立评审会话。
- 实际配置：`gpt-5.6-sol` + `xhigh`；首选可用，未降级。
- 状态：Completed，等待 PM 验收与隔离独立复评。
- 边界：仅合成内存/任务目录文件 SQLite 与代码内合成夹具；未连接或执行任何真实能力。

## 已验证事实

PM-CE-06 的根因是 `authorization_tombstone_control_envelope_immutable` 只检查 `OLD.subject_type='authorization'`。普通 Tombstone 因 OLD 不属于 Authorization，可在一次 UPDATE 中把 subject、generation、command、reason 和 blocked time 改写为伪造的 Authorization cleanup 包络。

本次只把 trigger 条件改为：`OLD` 或 `NEW` 任一侧涉及 Authorization，且 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 任一变化即拒绝。由此同时封堵 generic→Authorization、Authorization→generic、Authorization A→B，以及控制字段单独/复合改写。未全局冻结 generic Tombstone，其 generation CAS、控制字段更新与 cleanup 正向状态语义保持可用。

实际修改限 P3-031 候选 SQL、合同测试、当前 evidence/MANIFEST，以及新建 P3-048 工程目录和本报告。

P3-047/P3-046 的任务、报告、runner、输入、执行 Evidence、PM Review 和 PM 反例 Evidence 均未修改；P3-047 的 Outbox CAS、Submission/hash、retention 主体未重写。

## 测试结果

| 范围 | PASS | FAIL / NI / Unknown |
|---|---:|---:|
| 原 PM-CE-06，8 配置 | 8 | 0 |
| 三类 OLD/NEW 改绑方向 | 24 | 0 |
| 六状态 × 六单字段/一复合字段 | 336 | 0 |
| 身份 + cleanup status + time 同语句 | 48 | 0 |
| REPLACE/冲突/重建/UPSERT 相邻语义 | 40 | 0 |
| 多行 UPDATE 原子失败 | 8 | 0 |
| 合法状态、retry、generic、no-op | 72 | 0 |
| 时间组合 | 16 | 0 |
| **P3-048 专项合计** | **552** | **0** |

六状态为 accepted、active_blocked、cleanup_pending、cleanup_failed、vendor_limited、cleaned。单字段覆盖 subject type/id、generation、command、reason、blocked time。多行攻击同时包含合法 generic 推进与非法改绑，结果整句回滚。

合法 trace 覆盖 accepted→active_blocked→cleanup_pending→cleanup_failed→cleanup_pending→vendor_limited→cleanup_pending→cleaned，时间逐步增加；无状态改时间及状态变化时倒退时间均拒绝。generic Tombstone 仍可按旧合同推进 generation/control/status。

回归结果：

- P3-047 当前协议等价回归：297 PASS（P1 144、P2 153），无失败/未实现/未知。
- P3-031 当前全量：70 PASS（P0 18、P1 27、P2 25），退出码 0。
- 文件 SQLite：P3-048 68 个、P3-047 等价回归 148 个，共 216 个；全部 integrity/quick/FK 检查通过。
- 候选 SQL 与 P3-048 输入快照 SHA-256 均为 `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d`。
- 40 个只读文件 expected/before/after hash 全部一致；旧 BYPASS/Rework Evidence 保持原样。

复跑：`lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.sh`。

## 推断、风险与非范围

合理推断：在所列 SQLite 合成矩阵内，OLD/NEW 双侧条件覆盖了 PM-CE-06 的结构根因，且不依赖 FK 或 recursive trigger 配置。此结论不能外推为真实身份认证、生产并发或真实迁移通过。

未连接真实 DB/Vault/用户文件，未执行真实 migration；未启用真实 Tauri/IPC、网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。SQLite trigger 不认证真实操作者。

本任务不关闭 R-0048/R-0049 或其他风险，不修改 PM 账本，不恢复工程基线，不冻结 Schema/API/migration/工程基线，不进入下一阶段，不启动后续任务。

## 角色、关卡与 Evidence

- 技术架构/数据完整性执行侧：通过；补丁限于 OLD/NEW 条件。
- Gate 2/3/4：执行侧候选证据通过；仍需 PM 复跑与隔离独立复评。
- Evidence：`lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`（含结果、日志、只读证明与完整 hash）。
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-048_LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression_local_precheck.md`

需要 PM 决策：是否在隔离副本复跑通过后送入隔离独立复评。风险关闭、冻结、基线恢复、真实能力或后续任务均需另行授权。
