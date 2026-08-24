# LIFEOS-P3-047｜Outbox CAS 与生命周期控制包络 P0 整改及回归

## 1. 任务状态

- 状态：专项执行完成，等待 PM 验收与隔离独立复评。
- 实际模型：`gpt-5.6-sol` + `xhigh`；未降级、未触发后备模型。
- 执行角色：LifeOS 工程专项执行 Agent；不作为 PM 主会话或独立评审 Agent。
- 数据与能力边界：仅使用合成内存 SQLite、任务目录内合成文件 SQLite 和代码内合成夹具；未连接真实 DB、真实 Vault、真实用户文件、真实 Tauri / IPC、网络、云、第三方模型、向量、同步、多设备、L3 或外部用户，未执行真实 migration。
- 结论边界：本任务只形成候选 SQL、合成合同测试和 evidence，不代表 Accepted、风险关闭、Schema/API/migration/工程基线冻结或生产可用。

## 2. 授权范围内的修改

1. `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
   - 增加 Submission 与 lifecycle command 的 canonical hash/语义绑定。
   - 增加 append-only `outbox_runtime_command`，由数据库验证并应用 Outbox 运行态 CAS。
   - 增加 Authorization tombstone 控制包络不可变约束。
   - 增加参数化 retention policy、每任务不可变 retention binding 与作用域化 cleanup gate。
2. `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
   - 将合法夹具迁移到 Submission + lifecycle command、runtime command 协议。
   - 固化 PM-CE-01 至 PM-CE-05 及直接相关边界回归。
3. `lifeos/engineering/LIFEOS-P3-031/evidence/`
   - 复跑并更新当前候选的结果、日志及 MANIFEST。
4. `lifeos/engineering/LIFEOS-P3-047/`
   - 新建候选 SQL 输入快照、专项 runner、合成文件库、原子快照、状态机 traces、完整结果及 Evidence MANIFEST。
5. 本交付物。

P3-046 原报告、runner、shell、全部 evidence、PM Review、PM 反例脚本与反例结果均只读。专项 runner 对 18 个只读文件执行运行前/运行后 SHA-256 核对，全部 `unchanged=true`；未通过修改旧失败证据制造通过。

## 3. 五条 PM 反例整改映射

| 反例 | 原根因 | 候选补丁 | 新候选上的攻击结果 | 合法路径与剩余边界 |
|---|---|---|---|---|
| PM-CE-01 / P2 | lifecycle command 的 hash 可畸形且未绑定 Submission | hash 强制为小写 `sha256:` + 64 hex；command 必须匹配 append-only Submission 的 namespace、idempotency key、hash、command、subject 与空 result version | 8 个 memory/file、FK on/off、recursive trigger on/off 实例全部拒绝原攻击 | 合法 Submission 与 command 在同一 savepoint/事务提交；SQL 只验证结构和绑定，不把调用者升格为已认证身份 |
| PM-CE-02 / P1 | 未来 `available_at` 仍可 claim，且缺旧 generation CAS | claim command 必须匹配预期 status、availability、owner、generation，并由 DB 当前时间判断 `available_at <= now` | 8/8 拒绝未来任务领取与 stale generation | 合法 claim 由同一 runtime command 协议完成；应用仍负责生成可信 command intent |
| PM-CE-03 / P1 | 可直接把 processing 标成 completed，缺 owner/generation/lease 条件 | 禁止裸运行态 UPDATE；complete command 必须匹配 processing、lease owner、generation、未过期 lease，并核对 Authorization 当前 generation | 正常与 expired lease 共 16/16 实例拒绝无 owner/gen 或过期完成 | claim、renew、retry、cancel、dead-letter、complete 使用同一责任模型；DB 不声称识别 OS 进程身份 |
| PM-CE-04 / P2 | terminal Authorization 的 subject/command/reason/time 等控制字段可改写 | terminal/tombstone 行冻结 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at`/终态时间 | 8/8 配置中，对六类状态及全部控制字段的直接更新均拒绝 | 合法生命周期仍只允许 active→terminal；不会借此开放 terminal→active 或重建 |
| PM-CE-05 / P2 | generic terminal Outbox 被一刀切禁删，同时 Authorization 历史缺明确 retention | 普通非 Authorization 终态、无 lease 任务可清理；Authorization 生命周期任务仅在预配置 policy、任务创建时固化 binding、匹配 audit/terminal command 且 DB 时间满足 retention 后可删；缺配置/缺 binding 默认拒绝 | generic/before-retention/at-retention/unconfigured 共 33/33 通过 | retention 为非负毫秒参数；binding append-only 且普通 runtime mutation 不可倒退；生产策略值、运维入口与权限仍待后续正式设计 |

## 4. 受控协议说明

### 4.1 Outbox runtime command

候选表 `outbox_runtime_command` 是非核心、append-only 的数据库控制意图。每条命令包含目标 job、操作、旧 status/availability/owner/generation/lease 预期值，以及必要的新 owner、lease、availability 或 error。BEFORE trigger 对数据库当前行和 DB 时间做完整比较；AFTER trigger 执行唯一对应变更。裸 `outbox_job` 运行态 UPDATE 没有匹配命令即拒绝。

六类运行态操作使用统一模型：claim 校验到期可用；renew/complete 校验 owner、generation 与未过期 lease；retry/cancel/dead-letter 校验各自允许的旧状态和所有权条件。该设计把“旧值是否匹配、时间是否有效”放在 DB 强制层，但不宣称 SQLite 能认证命令提交者、进程身份或业务权限。

### 4.2 Submission 与 lifecycle command

Submission 和 lifecycle command 均为 append-only；同一主键不能通过 reinsert/REPLACE 重放。lifecycle command 的 canonical hash 必须精确匹配 Submission，并绑定 `destruct@1` namespace、idempotency key、终态命令、Authorization subject 与空 result version。合法退休 helper 使用 savepoint 保证两条插入要么共同成功、要么共同回滚。

### 4.3 Tombstone 与 retention

Authorization 进入 terminal 后，身份、generation、命令来源、reason 与终态时间构成不可变安全包络；任何单字段、复合字段或 subject 改绑均拒绝。Authorization 生命周期 Outbox 的 retention policy 必须在任务生成前配置，并在生成时形成每任务不可变 binding；之后修改 policy 不能追溯改变该任务的清理依据。未配置、未绑定、未到期、仍有 lease、audit 不匹配或终态 command 不匹配均默认拒绝。普通非 Authorization 终态 Outbox 不受此历史保留 gate 误伤。

## 5. 测试与 Evidence 结果

执行入口：

```bash
lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.sh
```

专项矩阵在 Python 3.9.6 / SQLite 3.51.0 上执行，覆盖内存与任务目录文件 SQLite、`foreign_keys` ON/OFF、`recursive_triggers` ON/OFF：

| 范围 | PASS | FAIL | Not Implemented / Unknown |
|---|---:|---:|---:|
| P3-045 AC-01 至 AC-18 等价迁移 | 216 | 0 | 0 |
| PM-CE-01 至 PM-CE-05 | 73 | 0 | 0 |
| P3-044 当前直接相关回归 | 8 | 0 | 0 |
| **P3-047 专项合计** | **297** | **0** | **0** |

专项严重度统计为 P1 144 PASS、P2 153 PASS。AC-14 另覆盖 revoked/expired/superseded × autocommit/commit/rollback × 8 配置，共 72 个实例；AC-16 覆盖 audit/outbox 故障注入 × 8 配置，共 16 个实例。生成 120 份原子快照、56 条状态机 trace；148 个文件库检查全部满足 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

P3-031 当前全量合同复跑：P0 18、P1 27、P2 24，合计 69 PASS，0 FAIL/Not Implemented，退出码 0。候选源与 P3-047 输入快照 SHA-256 均为 `7000ca397db8c737681bee1edff05caefcebffb1555f30697b61feb4a0df2854`。全部 runner 遇 FAIL、Not Implemented、Unknown、只读 hash 变化、快照不一致或回归非零都会返回非零。

## 6. 剩余风险与不可外推

- 这是空库候选 migration，不是已批准或已执行的真实迁移；未验证已有数据升级、WAL/backup、崩溃恢复、进程并发、性能容量或跨平台差异。
- SQLite trigger 能约束 command 与当前数据库事实，却不能认证真实调用者或证明应用层权限；Submission/runtime command 不升格为新的核心领域模型或认证系统。
- retention policy/binding 只是候选 SQL 控制包络；正式保留期限、运维权限、删除审计、导出与恢复 SLA 均未冻结。
- P3-046 的原失败与 PM Rework 记录保持原样；本结果只证明新候选在本合成矩阵中的行为。
- 不关闭 R-0048、R-0049 或任何其他风险；不修改 PM 账本，不冻结 Schema/API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。

## 7. 角色检查点与评审关卡

- 工程执行检查点：通过；授权目录内候选补丁、测试和 evidence 已生成。
- QA / Evidence 检查点：执行侧自检通过；结果、完整日志、hash、矩阵、原子快照、trace、integrity/FK 与只读保留证明齐备。
- AI 信任与安全、数据 / 领域模型检查点：等待隔离独立复评；本执行会话不自证通过。
- PM 关卡：需要 PM 对范围、反例迁移、剩余边界与 evidence 进行验收；P0 修复按项目规则还需要独立评审。未启动后续任务。

## 8. Evidence 与本地预检

- Evidence MANIFEST：`lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-047/evidence/test_results.json`
- 完整日志：`lifeos/engineering/LIFEOS-P3-047/evidence/test_run.log`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-047_LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression_local_precheck.md`。已按规则调用，局域网本地模型请求超时，报告状态为 `Skipped / Local Model Unavailable`；未阻塞原项目流程，也不作为 PM Review 或独立评审结论。

## 9. PM 决策

需要。请 PM 决定是否接受本次整改进入隔离独立复评；是否关闭风险、冻结任何资产或启动后续任务均不在本会话权限内。
