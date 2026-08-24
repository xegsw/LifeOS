# LIFEOS-P3-046 Evidence Manifest

## 1. 任务边界与结论口径

- 任务：Authorization 生命周期证据与终态历史合同候选实现及回归。
- 实际路由：`gpt-5.6-sol` + `xhigh`；未降级。
- 修改范围仅为任务卡授权的 P3-031 当前候选 SQL/tests/evidence、P3-046 工程目录和指定交付物。
- 所有数据库均为新建合成内存库或 `lifeos/engineering/LIFEOS-P3-046/work/` 下合成文件库；无真实用户数据。
- 未连接或迁移真实 DB/Vault/文件能力，未启用 Tauri/IPC、网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 本 evidence 只是候选实现的 PM 验收/后续隔离复评输入；不关闭任何风险，不改变 R-0045，不冻结 Schema/API、SQL migration 或工程基线，不构成真实能力准入。

## 2. 环境与复跑

- 工作目录：`/Users/xxe/Documents/No.2`
- 命令：`sh lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.sh`
- 最终退出码：`0`
- Python：`3.9.6`
- SQLite：`3.51.0`
- OS：`macOS-26.6.2-arm64-arm-64bit`
- 后端矩阵：`:memory:` / task-local file SQLite
- PRAGMA 矩阵：`foreign_keys=ON/OFF` × `recursive_triggers=ON/OFF`
- 事务矩阵：autocommit / explicit commit / explicit rollback；AC-14 对三种 terminal 状态完整展开。
- 文件库检查：全部 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`；见 `checks/integrity_and_fk.json`。
- Runner 任一 FAIL、Not Implemented、Unknown、P3-031 非零退出、完整性失败或 P3-044 hash 变化均返回非零。

## 3. 统计

### 3.1 P3-046 专项与直接回归

| 集合 | P0 PASS | P1 PASS | P2 PASS | FAIL | Not Implemented | Unknown |
|---|---:|---:|---:|---:|---:|---:|
| AC-01～AC-18 | 0 | 112 | 104 | 0 | 0 | 0 |
| 附加 command/outbox/cleanup | 0 | 8 | 16 | 0 | 0 | 0 |
| P3-044 当前候选直接回归 | 0 | 16 | 0 | 0 | 0 | 0 |
| **P3-046 总计** | **0** | **136** | **112** | **0** | **0** | **0** |

P3-046 共 248 个真实执行实例。AC-14 为 3 terminal × 8 后端/PRAGMA × 3 事务 = 72；AC-16 为 2 故障点 × 8 配置 = 16；其余每项 8 配置。结构化逐例结果为 `test_results.json`。

### 3.2 P3-031 当前全量

| P0 PASS | P1 PASS | P2 PASS | Total PASS | FAIL | Not Implemented | Unknown | Exit |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 18 | 25 | 21 | 64 | 0 | 0 | 0 | 0 |

P3-040/P3-042/P3-044 当前直接相关防线分别由 P3-031 的 CT-P1-13/14、CT-P1-17/18、CT-P1-19/20 承接；另由本 runner 的 `P3-044-CURRENT` 八配置复核。历史 runner 未改写、未以旧退休前置证据合同冒充当前回归。

## 4. AC-01～AC-18 可执行映射

所有实际状态均为 PASS；逐实例的 backend、FK、recursive triggers、terminal、transaction/fault 维度和 detail 在 `test_results.json`，失败前后快照在 `atomic_snapshots.json`，状态序列在 `state_machine_traces.json`。

| ID | 级别 | 预期/实际 | 实例 | Evidence |
|---|---|---|---:|---|
| AC-01 | P2 | 预置 correlation 冲突并全回滚 / PASS | 8 | results + atomic snapshots |
| AC-02 | P2 | audit UPDATE/DELETE/REPLACE 拒绝 / PASS | 8 | results |
| AC-03 | P2 | 不匹配 evidence 不可退休 / PASS | 8 | results |
| AC-04 | P2 | 重放不增 evidence / PASS | 8 | results |
| AC-05 | P2 | outbox immutable payload / PASS | 8 | results |
| AC-06 | P1 | lease owner/generation CAS 完成 / PASS | 8 | results + traces |
| AC-07 | P1 | stale lease/subject generation 不发布 / PASS | 8 | results |
| AC-08 | P2 | retry 只改运行态 / PASS | 8 | results + traces |
| AC-09 | P2 | active generation 单独爬升拒绝 / PASS | 8 | results |
| AC-10 | P2 | created/revoked time 预写改写拒绝 / PASS | 8 | results |
| AC-11 | P2 | 错误时间配对拒绝，合法 DB 时间一致 / PASS | 8 | results |
| AC-12 | P2 | terminal parent UPDATE/REPLACE/DELETE 拒绝 / PASS | 8 | results |
| AC-13 | P2 | terminal children 普通写删改绑拒绝 / PASS | 8 | results |
| AC-14 | P1 | 三终态同事务 parent+1/audit/outbox；rollback 无半态 / PASS | 72 | results + atomic snapshots |
| AC-15 | P1 | successor 激活且旧历史不变 / PASS | 8 | results |
| AC-16 | P1 | audit/outbox 故障全部回滚 / PASS | 16 | results + atomic snapshots |
| AC-17 | P2 | 无/错误 tombstone、gate、generation 清理拒绝 / PASS | 8 | results |
| AC-18 | P2 | 单向清理、最小历史保留、旧包不复活 / PASS | 8 | results + atomic snapshots |

## 5. 合同实现与证据边界

- `authorization_lifecycle_command` 是非核心一次性控制记录：command/idempotency 唯一，append-only，绑定 authorization、expected generation、终态、actor claim、canonical request hash、DB processed time、result generation/correlation。
- active→terminal 的 parent、generation +1、DB time、AuditEntry、OutboxJob 由同一 AFTER INSERT trigger 生成；任何约束冲突或外层 rollback 会撤销 command 和全部副作用。
- AuditEntry 最小行 append-only 且 correlation 唯一；cleanup 不允许修改或删除它。
- OutboxJob 业务载荷不可变，运行态由显式状态机与 CAS 约束；它不是 Authorization/AuditEntry 的权威源。
- cleanup 选择保留 terminal parent，受 tombstone + 最小 cleanup audit + forward-only gate 控制，只删除 scope/action/policy；cleaned 后同 id REPLACE/重建被 terminal parent 与 tombstone 双重阻断。
- `scoped_actor_claim` 未由 DB、操作系统或密码学认证。直接 SQL 持有者可以提交终态拒绝请求，但不能 grant/reactivate 或改写安全包络；真实用户确认与身份真实性仍在应用层非范围。

快照覆盖 Authorization、lifecycle command、AuditEntry、OutboxJob、Submission、Tombstone 及三类子投影；`atomic_snapshots.json` 共 104 个前后/提交/回滚或清理快照，`state_machine_traces.json` 共 32 条 outbox/cleanup 轨迹。

## 6. Hash 与文件关系

### 6.1 当前输入

| 文件 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | `1d8ea2f5d8095bd254291c6e0e54aa14ca921175da6757ae6c66e6e06769fe` |
| `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py` | `ec492449e29d7d19d801ea36218dd866e4ce6cd4b46d805c2dbede24e88e5967` |
| `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |
| `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md` | `c55f7eb4b1198a181df6bc824f9627330c7ba403083733bb6d6619d2015c10df` |
| `input/001_candidate_schema.sql` | `1d8ea2f5d8095bd254291c6e0e54aa14ca921175da6757ae6c66e6e06769fe` |
| `scripts/run_validation.py` | `106a959cb9dedd49d8b2866e80aef3f4ee7010bf26800d7b3da9d83a4d851e4a` |
| `scripts/run_validation.sh` | `268c4c0a6a04017222cc1d1838fd9c1c3baa0d930f66087ef4767eaf142bd028` |

候选 SQL 与任务快照 hash 相同；`input/source_hashes.json` 是 runner 运行时采集值。

### 6.2 输出快照

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `test_results.json` | 248 项结构化结果/AC 覆盖 | `6e918b089196077bbca7e6ac0ee24b122ab2c9fb4eeb2ab358d514a622b332bb` |
| `test_run.log` | 原始完整日志 | `152ef9022c18ed3bfd0c566bb50f4e9564a3f461e2fff737038666914427dce9` |
| `atomic_snapshots.json` | 原子/回滚/清理前后快照 | `6acd7d65c92752b61b96174d04a28c3320314cff260bf6d280e0267c6bca38dd` |
| `state_machine_traces.json` | outbox/cleanup 状态轨迹 | `9484580f4ff676081fb128cc935709510baa02244333fc45ce72f7d95e2fa56f` |
| `checks/integrity_and_fk.json` | 文件库完整性/FK | `ffb7557407eb113d269e5042f1758ddf6f95457260f8d13420932d825279ef3c` |
| `environment.json` | 环境、能力与合成库声明 | `98e16eae0c263606cb92e71916b70b62b5a69437e4b46371967cf8842817f805` |
| `regressions/p3_031_test_results.json` | P3-031 全量结构化结果 | `7fb8bbc1f688267efc84c17674f2f527f6c2c6fe54f0a81e393c20340b0319a5` |
| `regressions/p3_031_test_run.log` | P3-031 全量日志 | `fe20e2f76225199e647c892f78c6fe365a0b2ebb77ff433190083b6c447b5600` |
| 指定交付报告 | 结果摘要/边界 | `94dac087ee1dfacbdf9b448b7fef08a90109ee7282a89293739342b9dbb800b9` |
| 指定本地预检 | 只读覆盖/措辞辅助 | `5cdde9112ebc3dad75ceadec2a24c32b5b90d9cdccbf36092384baa06b191351` |

报告引用本 manifest；manifest 索引结构化结果与原始日志；结构化结果保存逐例实际值，日志保存同一轮人类可读输出。生成文件含运行快照，复跑覆盖后 hash 会变化，须以新一轮整套文件重新核对。

### 6.3 P3-044 原 evidence 未修改

`input/p3_044_preservation.json` 记录执行前/后 hash；以下四项均 `unchanged=true`：P3-044 `evidence/MANIFEST.md`、runner、`test_results.json`、`test_run.log`。其基线 SHA-256 分别为 `8e0575…3b26`、`1e297a…40c3`、`857c86…439f`、`b0e4f7…6848`。

## 7. 剩余关卡

Gate 2/3/4 的工程证据已形成，但通过结论由 PM 验收。关闭 R-0048/R-0049、冻结 Schema/API 或启用真实能力前必须另行进行与执行会话隔离的独立工程复评；本任务未启动该后续工作。
