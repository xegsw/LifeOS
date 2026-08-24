# LIFEOS-P3-040｜Active Authorization 子表变异 P1 整改与回归报告

## 1. 任务信息与结论

- 任务 ID：LIFEOS-P3-040
- 执行 Agent：Codex 专项工程整改会话；不是 PM 或独立评审会话
- 主责角色：技术架构负责人 / 工程整改负责人
- 协审角色：AI 信任与安全、数据 / 领域模型、QA / Evidence Reviewer、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 执行状态：**Completed / Candidate Regression PASS**

**[已验证事实]** P3-039 的 11 个 active Authorization 子表 INSERT、UPDATE、`INSERT OR REPLACE`、改绑 P1 已由候选 SQLite trigger 在 DB 层阻断。P3-031 合成空库回归为 42 PASS；P3-040 在内存与任务专属文件库双模式下为 128 PASS，均无 P0/P1 FAIL、Not Implemented 或 Unknown。

**[判断]** 当前结果足以作为后续隔离独立工程复评输入，但不等于 PM 验收、风险关闭、Schema/API 或 SQL migration 冻结，也不是任何真实能力证明。

## 2. 授权边界与实际修改

修改：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`

创建：

- `lifeos/engineering/LIFEOS-P3-040/` 下候选快照、双模式 runner、合成文件库与 evidence
- 本交付物

P3-031 `scripts/run_validation.sh` 无需修改，其非零退出透传合同保持不变。未修改 P3-037、P3-038、P3-039 的原始交付物、评审、PM Review 或 evidence；未修改 P3-009、Stitch、生产代码或 PM 账本。

仅使用合成空库、内存 SQLite 和 P3-040 隔离目录内的合成文件库；未连接真实 DB/Vault，未访问真实用户文件，未启动真实 Tauri/IPC，未启用网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。

## 3. 候选 SQL 整改

### 3.1 Active 子表封闭

scope、action、policy 各新增 BEFORE INSERT 与 BEFORE UPDATE trigger，并保留 P3-038 的 BEFORE DELETE trigger：

- INSERT 在 NEW 父为 active 时拒绝；该前置检查同时覆盖 `INSERT OR REPLACE` 的冲突处理前路径。
- UPDATE 同时查询 OLD 与 NEW `authorization_id` 对应父状态；任一端 active 即拒绝，封住 active→inactive、inactive→active、active→active 改绑。
- DELETE 在 OLD 父 active 时拒绝；父处于终态时仍允许清理。

### 3.2 状态翻转与版本复用

新增最小候选生命周期合同：

- 只允许 proposed→granted/active、granted→active、active→revoked/expired/superseded。
- active→proposed/granted 拒绝；revoked/expired/superseded 为终态，不可重新 active。
- active 退出必须 generation 精确 `OLD+1`，并预先存在与 `id:generation:terminal-status` 绑定的 audit correlation 和 pending outbox idempotency；缺 generation、audit 或 outbox 均拒绝。
- `logical_key`、`version_no`、`supersedes_id` 插入后不可原地改写。
- version > 1 激活必须指向同 logical key、前一 version 且已 superseded 的授权；首版不得声明 supersedes。

该合同允许终态子表维护，但不允许通过“active→终态→改子表→复活”复用旧授权；合法变更必须创建 complete 的新版本并在旧版本 superseded 后激活。

## 4. P3-039 11 个 P1 整改映射

| P3-039 旁路 | DB 整改 | 回归入口 |
|---|---|---|
| active 新增 allow scope | scope BEFORE INSERT | `ADJ/insert_new_scope_active` |
| active 新增 action | action BEFORE INSERT | `ADJ/insert_new_action_active` |
| scope effect UPDATE | scope BEFORE UPDATE | `ADJ/update_scope_effect_active` |
| scope target UPDATE | scope BEFORE UPDATE | `ADJ/update_scope_target_active` |
| scope authorization_id 改绑 | OLD/NEW 双端 UPDATE | `ADJ/scope_rebind_active`、`EXT-REBIND` |
| policy training UPDATE | policy BEFORE UPDATE | `ADJ/update_policy_training_active` |
| policy sensitivity UPDATE | policy BEFORE UPDATE | `ADJ/update_policy_sensitivity_active` |
| policy external send UPDATE | policy BEFORE UPDATE | `ADJ/update_policy_external_send_active` |
| action read→export UPDATE | action BEFORE UPDATE | `ADJ/update_action_value_active` |
| scope REPLACE | scope BEFORE INSERT | `ADJ/insert_or_replace_scope_effect` |
| policy REPLACE | policy BEFORE INSERT | `ADJ/insert_or_replace_policy` |

更强覆盖还包括 deny scope、source/artifact target、action REPLACE、policy direct INSERT，以及 retention、recipients、regions、disclosure、license、quantity、frequency 字段。

## 5. 状态翻转、双向改绑与合法路径

**[已验证事实]** `EXT-REBIND` 对 scope/action/policy 分别覆盖 active→inactive、inactive→active、active→active，共 9 个逻辑场景、双模式 18 项，全部被指定 trigger 拒绝。

**[已验证事实]** `EXT-STATE` 证明：active→proposed/granted 拒绝；退出缺 generation/audit/outbox 分别拒绝；revoked/expired/superseded 后允许修改非 active 子表，但再次 active 被 forward-only trigger 拒绝；version identity 原地修改和无 supersedes 的 v2 激活被拒绝。

**[已验证事实]** `EXT-LEGAL` 证明 revoked、expired、superseded 三种终态下 scope/action/policy 均可删除；旧 v1 以 generation+1、audit/outbox 绑定进入 superseded 后，新 v2 以 proposed→complete→active 合法通过。P3-031 还验证 proposed→granted→active 路径。

**[限制]** SQLite trigger 能要求匹配证据在状态 UPDATE 执行时已可见；正式服务仍应在同一事务中写 audit/outbox 并更新状态。本任务没有验证真实事务 API、并发进程或崩溃恢复，因此不把候选顺序合同外推为生产实现通过。

## 6. 回归统计与退出码

### P3-031 合成空库

命令：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`；退出码 0。

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 16 | 0 | 0 |
| P2 | 8 | 0 | 0 |
| **Total** | **42** | **0** | **0** |

新增 CT-P1-13 至 CT-P1-16 分别覆盖全字段变异、OLD/NEW 改绑、状态翻转与 retirement fence、合法终态清理和新版本激活；既有 38 项未回退。

### P3-040 双模式

命令：`lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.sh`；退出码 0。

| 严重级别 | PASS | FAIL | Not Implemented | Unknown |
|---|---:|---:|---:|---:|
| P0 | 0 | 0 | 0 | 0 |
| P1 | 126 | 0 | 0 | 0 |
| P2 | 2 | 0 | 0 | 0 |
| **Total** | **128** | **0** | **0** | **0** |

64 个逻辑场景均在 memory 与 file 模式运行；P3-039 的 29 个攻击逐名迁入等价测试，另加 35 个场景。64 个文件库的 integrity、quick check、FK 全通过。P3-039 五个原始 evidence 文件 hash 均未变化。

## 7. Hash 与 evidence

| 稳定文件 | 整改前 | 整改后 |
|---|---|---|
| P3-031 候选 SQL | `008cd328...c4cf2` | `50d25371...3cf7c` |
| P3-031 合同测试 | `246f3675...39da` | `074e9388...4072e` |
| P3-031 runner | `611a2714...6230d` | 未变化 |

P3-040 快照与当前候选 SQL hash 完全一致。完整 64 位稳定/运行 hash、环境、访问路径和 P3-039 保留证明见：

`lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`

## 8. 角色关卡、风险与 PM 决策

- Gate 2：**执行自检 Pass with Conditions**。版本链、终态与子表完整性在当前候选层可追溯；仍待隔离独立复评。
- Gate 3：**执行自检 Pass with Conditions**。scope/action/training/external-send/sensitivity 等静默改写路径 fail closed；真实权限消费链未在本任务验证。
- Gate 4：**执行自检 Pass with Conditions**。两套回归、退出合同、hash、文件库 integrity/FK 可复跑；未验证真实 migration、跨平台、并发或崩溃恢复。
- R-0040、R-0043、R-0044、R-0046 保持当前开启状态；R-0045 保持 Closed。本会话不改变任何风险状态。
- 无工程阻塞；是否采纳本候选整改、是否进入后续隔离独立复评需 PM 决策。执行会话不启动后续任务，也不得独立评审自己的结果。
- 本地预检已按规则调用，但局域网模型超时不可用，状态为 `Skipped / Local Model Unavailable`；不阻塞原流程。报告路径：`lifeos/local_prechecks/LIFEOS-P3-040_LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression_local_precheck.md`。

## 9. 不可外推声明

本结果仅适用于当前候选 SQL、合成空库、单进程内存 SQLite 和任务专属文件型 SQLite。不得外推为非空真实旧库 upgrade、真实用户 DB/Vault/文件、真实 Tauri/IPC、云/第三方模型、向量、同步、多设备、L3、外部用户、跨平台、并发、WAL/断电、生产 backup SLA 或正式 migration 通过；不得冻结任何资产、关闭风险、恢复工程基线或构成下一阶段准入。
