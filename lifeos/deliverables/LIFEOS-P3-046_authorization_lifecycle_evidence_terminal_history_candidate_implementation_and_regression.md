# LIFEOS-P3-046｜Authorization 生命周期证据与终态历史合同候选实现及回归

## 任务信息

- 任务 ID：LIFEOS-P3-046
- 执行 Agent：Codex 工程执行 Agent
- 实际模型配置：`gpt-5.6-sol` + `xhigh`；未降级、未切换后备模型
- 当前状态：Completed（候选实现与合成回归完成，待 PM 验收）
- 任务类型：P0 工程整改 / 候选 SQL 安全补丁 / Evidence 生成；不适用 P3 Engineering Fast Lane
- 数据边界：仅合成内存 SQLite 与 `lifeos/engineering/LIFEOS-P3-046/work/` 下合成文件库

## 实现结论

已在 P3-031 当前候选 SQL 中落实 P3-045 经 PM 条件验收的完整条件包。新增非核心、append-only 的 `authorization_lifecycle_command`：一次 INSERT 校验 active 状态、expected generation、目标终态和 scoped actor claim，并由数据库在同一语句/事务内完成父记录终态转换、generation 恰好 +1、DB 时间、唯一 correlation AuditEntry 与 pending OutboxJob。预置 correlation、重复 command/idempotency、错误 generation/target/subject、audit/outbox 冲突及外层事务 rollback 均不能留下半状态。

AuditEntry 现以 trigger 禁止 UPDATE、DELETE、主键/correlation REPLACE；生命周期 audit 只保存 action、scoped actor claim、Authorization reference/version、result、DB time 与 correlation，不写正文、路径、URL 或自由错误文本。OutboxJob 的 job/type/subject/generation/payload/idempotency 载荷不可变，运行态只允许 pending、leased、completed、cancelled、dead_letter 的列举转换，并约束 owner/generation/expiry CAS、retry、terminal 不回流及当前 Authorization generation 完成条件。

Authorization 的 active→revoked/expired/superseded 仅可由匹配 command 驱动；created time 不可改，revoked time 只在 revoke 时与 updated/audit 采用同一 DB 时间，expired/superseded 以 immutable audit occurred time 为权威终态时间。terminal 父行及 scope/action/policy 默认禁止 INSERT/UPDATE/DELETE/REPLACE/改绑。受控清理采用“保留 terminal 父身份，删除三类敏感子投影”的窄策略：Authorization tombstone 必须绑定终态与当前 generation，先有最小 cleanup audit，再单向进入 `active_blocked`、`cleanup_pending`、`cleaned`；只有 cleanup_pending 可删除子投影，cleaned 前必须确认投影已空。父行、tombstone 和两类最小 audit 长期保留，相同 id 的 REPLACE/重建及旧包恢复候选均不能复活。

## 实际修改文件

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-046/` 下候选快照、runner、合成库与 evidence
- 本交付物

P3-039 至 P3-045 的交付物、评审、PM Review、任务卡和 evidence 未修改；P3-044 四个受保护文件的执行前后 SHA-256 均与既有 manifest 基线一致。

## P3-045 AC 逐项实现映射

| AC | 级别 | 候选实现与测试结论 |
|---|---|---|
| AC-01 | P2 | 预置 correlation 触发唯一冲突，parent/command/audit/outbox 全回滚；8/8 PASS |
| AC-02 | P2 | audit UPDATE/DELETE/REPLACE 全拒绝且原行不变；8/8 PASS |
| AC-03 | P2 | 伪造 generation/version/action evidence 不放行直接退休；8/8 PASS |
| AC-04 | P2 | command/idempotency 重放不生成第二份 evidence；8/8 PASS |
| AC-05 | P2 | outbox subject/payload/idempotency mutation 与 REPLACE 拒绝；8/8 PASS |
| AC-06 | P1 | 合法 claim→complete 使用 owner/generation CAS；8/8 PASS |
| AC-07 | P1 | 旧 lease generation 与旧 subject generation 不形成完成假象；8/8 PASS |
| AC-08 | P2 | retry 只改运行态并递增 attempts，载荷保持；8/8 PASS |
| AC-09 | P2 | active generation 单独 +1/+N 均拒绝；8/8 PASS |
| AC-10 | P2 | created time 改写及 active revoked time 预写均拒绝；8/8 PASS |
| AC-11 | P2 | 手工时间配对旁路拒绝；合法转换 parent/audit 时间相等；8/8 PASS |
| AC-12 | P2 | terminal 父 UPDATE/REPLACE/DELETE 拒绝；8/8 PASS |
| AC-13 | P2 | terminal 子 INSERT/UPDATE/普通 DELETE/改绑拒绝；8/8 PASS |
| AC-14 | P1 | 三终态 × 8 后端/PRAGMA × autocommit/commit/rollback；72/72 PASS |
| AC-15 | P1 | supersede 后 successor 可完整配置并激活，旧历史不变；8/8 PASS |
| AC-16 | P1 | audit/outbox 两类故障 × 8 配置均整体回滚；16/16 PASS |
| AC-17 | P2 | active、错误 generation、缺 cleanup audit/gate 的清理拒绝；8/8 PASS |
| AC-18 | P2 | 合法单向清理保留父/tombstone/audit，重复与复活拒绝；8/8 PASS |

## 测试与 Evidence 摘要

- 复跑命令：`sh lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.sh`
- P3-046 AC：216 PASS，0 FAIL，0 Not Implemented，0 Unknown；其中 P1 112、P2 104。
- 附加 command/outbox/cleanup 状态机与 P3-044 当前候选直接相关回归：32 PASS；P3-046 总计 248 PASS，0 FAIL。
- P3-031 全量：P0 18、P1 25、P2 21，共 64 PASS；0 FAIL、0 Not Implemented、0 Unknown，退出码 0。CT-P1-13/14、17/18、19/20 分别承接 P3-040/P3-042/P3-044 当前直接相关 active parent/children 与替换/重建防线。
- 文件型数据库的 `integrity_check`/`quick_check` 均为 `ok`，`foreign_key_check` 均为空；FK ON/OFF、recursive triggers ON/OFF 均真实执行。
- Evidence manifest：`lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md`
- 结构化结果与日志：`evidence/test_results.json`、`evidence/test_run.log`；原子快照、状态机轨迹、完整性结果及源 hash 由 manifest 索引。
- 本地预检：Completed；`lifeos/local_prechecks/LIFEOS-P3-046_LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression_local_precheck.md`。本地预检仅为覆盖/措辞辅助，不是 PM Review 或独立评审。

## 威胁边界、剩余风险与关卡

`scoped_actor_claim` 是应用提交的未认证 claim。持有本地数据库直接写权限者可以请求“终态拒绝”，但 command 不能 grant、activate/reactivate、改写安全包络或证明操作者真实身份；本任务不提供 OS 身份认证、密码学不可否认性或生产 outbox worker。受控清理也只是候选 DB 合同，真实用户确认和业务编排仍属于应用层。

Gate 2 的数据来源/最小证据与清理口径、Gate 3 的 fail-closed 权限边界、Gate 4 的 SQLite 可执行性已由实现和合成证据覆盖，最终通过仍由 PM 判断。在关闭 R-0048/R-0049、冻结 Schema/API 或启用任何真实能力前，仍需与本执行会话隔离的独立工程复评；P3-044 的一次性豁免不延续。本任务不关闭 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049、R-0050，不改变 R-0045，不冻结任何资产、不恢复工程基线、不启动后续任务。

本结论只证明当前候选 SQL 在合成 SQLite 矩阵下满足合同，不可外推为真实 migration、真实 DB/Vault/文件/Tauri/IPC、云/第三方模型、向量、同步、多设备、L3、外部用户、生产安全或性能结论。

## PM 决策

需要。PM 需验收本候选实现与 Gate 2/3/4 evidence，并决定是否另行分派隔离复评；风险关闭、Schema/API 冻结及真实能力启用均不在本任务授权内。
