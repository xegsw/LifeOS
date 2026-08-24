# LIFEOS-P3-044｜Active Authorization 替换／重建旁路 P1 整改与回归

## 1. 任务信息与边界

- 当前状态：工程整改与回归完成，等待 PM 验收；不是 Accepted、风险关闭或冻结结论。
- 实际模型：`gpt-5.6-sol` + `xhigh`；首选配置可用，未触发 `gpt-5.5` 后备或降级。
- 主责角色：技术架构/工程整改负责人。协审视角：AI 信任与安全、数据/领域模型、QA/Evidence、PM。
- 授权范围：仅修改 P3-031 候选 SQL、合同测试/evidence，并新建 P3-044 runner/evidence。P3-039 至 P3-043 原始资产和 PM 账本只读；未创建或启动 P3-045。
- 能力范围：只使用合成空库/数据、内存与任务目录文件 SQLite；未连接真实 DB/Vault/文件/导出/Tauri/IPC，未执行真实 migration，未启用网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。

## 2. 实际修改与真实 DB 约束

修改文件：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`、结果与日志
- 新建 `lifeos/engineering/LIFEOS-P3-044/` runner、SQL 快照与 evidence

候选 SQL 新增两个窄 trigger：

1. `authorization_no_replace_while_active`：`BEFORE INSERT` 查询是否已有 active 行与 `NEW.id` 冲突，或与 `NEW.(logical_key,version_no)` 冲突；在 SQLite 执行 REPLACE 隐式删除前统一返回 `active_authorization_replace_forbidden`。
2. `authorization_no_delete_while_active`：`BEFORE DELETE` 在 `OLD.status='active'` 时返回 `active_authorization_delete_forbidden`，阻止 FK OFF 下 DELETE+INSERT 重建。

既有 direct-active INSERT trigger 做了必要的条件分流：active 冲突由 replacement trigger 稳定报告，无冲突 direct-active 仍返回 `authorization_must_start_inactive`。此设计不依赖 FK、recursive delete trigger、CHECK/UNIQUE 偶然报错或应用层约定；P3-042 UPDATE trigger 与生命周期 trigger 保持独立，没有被宽泛替换。

## 3. 冲突与执行矩阵

| 维度 | 已验证事实 |
|---|---|
| 冲突身份 | 同 id、同版本唯一键不同 id、两者同时、仅 id、无冲突均覆盖 |
| SQL 形态 | `INSERT OR REPLACE`、`REPLACE INTO`、两类 UPSERT DO UPDATE、DO NOTHING、普通重复 INSERT、DELETE、DELETE+INSERT |
| 目标状态 | proposed/granted/active/revoked 替换均拒绝 |
| 安全字段 | processor、purpose、location、policy_version、nullable/配对 expires 字段组合均未改变 |
| PRAGMA | FK ON/OFF × recursive ON/OFF，均在 migration 后设置并读回确认 |
| 后端 | memory/file |
| 事务 | autocommit、显式事务预期 commit、失败 rollback |

P3-043 原 P1 `insert_or_replace_granted_fk_on` 在 2 后端 × 2 FK × 2 recursive × 3 事务模式共 24 个实例全部稳定拒绝。DELETE+INSERT 同样覆盖这 24 个组合。替换失败后对完整父行、scope/action/policy、generation、audit/outbox 做快照比较，全部原子保持；显式事务中先插入 fake audit 再尝试 REPLACE 的 16 个实例也全部整事务回滚。

## 4. 合法路径与非回退

- 唯一 id/版本身份的新 proposed 或 granted 记录，配置三类子表后激活：16/16 PASS。
- active 合法 supersede（generation+1、audit、outbox）后，同事务创建正确 v2 successor、使用不同安全包络并激活：8/8 PASS。
- active no-op 包络 UPDATE 与仅 `updated_at_ms` 更新：8/8 PASS。
- P3-031 当前合同、P3-040 active 子表、P3-042 八字段/NULL/复合/多行回归全部针对当前 SQL hash `0b7f...d376` 运行并退出 0。

终态父/子记录不可变没有被本次 trigger 扩展；这仍属于 R-0049。generation/evidence/时间元数据也没有被声明为合法白名单或顺手修复。

## 5. 四组回归统计

| 测试集 | 结果 | FAIL / Not Implemented / Unknown | 退出码 |
|---|---|---|---:|
| P3-031 current | P0 18、P1 20、P2 8；46/46 PASS | 0 / 0 / 0 | 0 |
| P3-040 current | P1 126、P2 2；128/128 PASS | 0 / 0 / 0 | 0 |
| P3-042 current | 52 PASS + 26 P2 Known Limitation | 0 / 0 / 0 | 0 |
| P3-044 | P1 160 PASS；P2 40 PASS + 18 Known Limitation；P3 2 Observation | 0 / 0 / 0 | 0 |

P3-044 共 220 个执行实例；110 个文件库 integrity/quick/FK 检查全部通过。新增 P0=0、新增 P1=0。

## 6. P3-043 反例迁移与非范围保留

- 原 P1：`INSERT OR REPLACE(granted)` 改写 processor/policy_version 并重新激活，当前在 replacement 第一步即稳定失败；三类子表、generation、audit/outbox 不变。
- 原 10 个 P2：全部保留映射。`fk_off_replace_rebuild_then_activate` 与本任务同根且任务明确要求 FK OFF fail closed，当前 8/8 PASS；其余 9 个仍以双后端共 18 个 Known Limitation 实例保留。
- 原 1 个 P3：granted 激活前包络可配置仍以 2 个 Observation 实例保留。
- P3-043 原始 PM Review、独立评审、manifest、candidate、脚本和 JSON/TXT 结果共 7 文件 hash 前后完全一致；历史 34 PASS/12 BYPASS 未被删除、降级或改写。

这里区分“原始 P2 证据保留”和“当前行为”：FK OFF replace P2 因任务要求覆盖同根因而被关闭，不伪装为仍可复现；其余 R-0048/R-0049 P2 继续开放。

## 7. Hash 与 Evidence

- 候选 SQL：`ceedad2ba731b0406c28fb5cf503130cfeda74f7fdf4ccf4db1e7809bffa5a6b` → `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376`
- P3-031 tests：`e934dff9b9502d5e5c4f46c96a1471e9d581e08a7fe448e8a6754e86b7ecd275` → `58a4cb9781c88dc899e647ff9f95b851aba67c863dc1ddd48c6d8c7e20760ba9`
- P3-044 runner：`1e297a9eaf031776b33ee978656e9aa62e477d1b05875a6c1aa9627b532774c3`
- P3-044 results/log：`857c86c8212a09f35f5fdd129acda82ca4b532269158c0c4b5c9e08a8dbe439f` / `b0e4f76ce3af1cd447e1dfac53823fb73894f6959dd14f1afe8bdf949adc6848`
- P3-043 preservation：7/7 unchanged；明细见 `evidence/input/p3_043_preservation.json`。

完整命令、逐文件 hash、当前 SQL 快照、PRAGMA/事务逐项结果与原始保留证明见 `lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`。

## 8. 剩余风险、不可外推与关卡

- R-0048：audit/outbox 可预置/修改/删除、generation 独立升高、active created/revoked 时间元数据可变，未修复。
- R-0049：terminal Authorization 父表/子表历史语义可变，未修复。
- R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049、R-0050 均未关闭；R-0045 未改变。
- Gate 2：候选数据身份与原子状态证据已覆盖，R-0048/R-0049 条件仍开放。
- Gate 3：替换/重建 P1 在执行自检范围内关闭，仍须 P3-045 隔离复评确认。
- Gate 4：当前 Python/SQLite 双后端与 PRAGMA/事务矩阵通过；真实 migration、跨平台、并发/WAL/崩溃恢复未验证。

这些结果只适用于合成 SQLite。不得外推到真实非空旧库、真实用户 DB/Vault/文件/导出/Tauri/IPC、性能/生产 SLA；不构成风险关闭、Schema/API/SQL migration/工程基线冻结、真实能力准入或阶段切换。

## 9. 建议与 PM 决策

建议 PM 验收本任务，并在 PM 明确创建后交由未参与本整改的隔离会话执行 P3-045。本会话不创建、不启动，也不承担 P3-045。是否采纳整改候选、是否创建 P3-045、任何风险状态变化均需 PM 决策。

## 10. Local Precheck / 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`
- 实际路径：`lifeos/local_prechecks/LIFEOS-P3-044_LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression_local_precheck.md`
- 结果：`Skipped / Local Model Unavailable`；局域网本地模型连接超时（`Errno 60`），依允许跳过规则继续，PM 须按原流程人工复核。
- 本地预检仅作覆盖/措辞辅助，不是 PM Review、Independent Review、Accepted、风险关闭或准入结论。
