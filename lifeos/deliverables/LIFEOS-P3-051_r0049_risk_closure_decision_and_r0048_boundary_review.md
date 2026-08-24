# LIFEOS-P3-051｜R-0049 风险关闭建议与 R-0048 边界复核

## 1. 决策摘要

- **R-0049 结论：建议关闭 R-0049。** 建议关闭范围严格限定为当前候选 SQL（核验时 SHA-256：`56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d`）、合成 memory/file SQLite、当前 P3-045 至 P3-050 Evidence 与有限 Stage 3 受控边界。
- **R-0048 结论：保持 Open / Remediation Candidate。** P3-050 的全新隔离独立攻击只对 Tombstone→Authorization 改绑及直接相邻 cleanup 控制包络形成独立主证据；它没有对完整 lifecycle、AuditEntry、OutboxJob、generation/time、Submission/幂等命令合同形成新的独立攻击结论。
- 本结论只是风险决策建议，**不执行风险关闭**。只有 PM 验收且用户再次明确授权后，PM 才可更新 `RISK_LOG.md`；R-0048 不得连带关闭。
- 不冻结 Schema/API、候选 SQL migration 或工程基线；不恢复工程基线，不启用真实 DB/Vault/Tauri/IPC/文件/云/第三方模型/同步等真实能力，不进入下一阶段。
- 实际执行配置：全新 Codex 任务 `01a021d6-6ef6-7d22-baa6-7cd695befcd0`，`gpt-5.6-sol` + `xhigh`，未降级。

## 2. 已验证事实、推断、建议与待确认

### 已验证事实

1. P3-045 已把 terminal Authorization 父记录、scope/action/policy 子记录、Tombstone cleanup 控制包络、受控单向清理与最小审计保留写成明确合同，并由 AC-12、AC-13、AC-17、AC-18 承接。
2. 当前候选 SQL 对 terminal 父记录使用全行 UPDATE 拒绝、DELETE 拒绝和冲突 INSERT/REPLACE 拒绝；对三类 terminal 子记录分别拒绝 INSERT/UPDATE，并仅在匹配 terminal generation、Authorization Tombstone=`cleanup_pending`、最小 cleanup audit 存在时允许 DELETE。
3. P3-047 的等价回归在八配置中对 AC-12、AC-13、AC-17、AC-18 各记录 8/8 PASS；P3-031 当前合同入口相应 AC 也为 PASS。P3-050 隔离复跑记录 P3-047 等价 297 PASS、P3-031 70 PASS，退出码均为 0。
4. P3-047 原 PM-CE-06 曾在八配置稳定形成 0 PASS / 8 BYPASS；P3-048 将保护条件修正为 OLD 或 NEW 任一侧涉及 Authorization，并在执行与 PM 复跑中得到 552 PASS、原 PM-CE-06 8 PASS / 0 BYPASS。
5. P3-050 使用全新任务；独立计划及 hash 先于独立脚本、首轮结果和封存记录，且延迟读取 P3-049 攻击资产。自建独立矩阵为 832 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown，PM 复跑结果逐条一致。
6. P3-050 声明的 40 个历史只读文件全部匹配 expected hash；P3-047 原 `0 PASS / 8 BYPASS` 结果仍保持原 hash，未被新通过结果覆盖。

### 合理推断

- 在上述候选 SQL 与合成 SQLite 边界内，R-0049 所述“terminal 父/子历史或 cleanup 主体、generation、command、reason、time 被事后改写”的已知路径已有结构不变量、逐项合同测试和独立 Evidence 支撑，继续保持 R-0049 Open 不再对应一个已知未整改旁路。
- P3-050 的 832 条独立矩阵是 cleanup 控制包络改绑的主证据；terminal 父/子部分的独立支撑来自 P3-050 对 AC 回归的隔离复跑、P3-050 PM Evidence，以及本任务对 SQL/测试/结构化结果的独立逐项核验。不能把 832 总数误称为 terminal 父/子全部攻击数。
- R-0048 与 R-0049 可分离处置：R-0049 关闭只表示当前 terminal 历史与 cleanup 包络的事后变异路径在受控边界内已收口，不表示 lifecycle evidence 的产生、调度、租约、幂等或真实调用者可信度已完成关闭。

### 建议

- PM 验收后，请用户单独确认是否按本文件第 5 节的有限范围关闭 R-0049。
- R-0048 保持 Open / Remediation Candidate，后续若要关闭，必须对第 7 节完整边界另做隔离独立复评，不得复用本任务结论替代。

### 待 PM / 用户确认

- 是否采纳“建议关闭 R-0049”的有限范围结论。确认前 R-0049 仍保持 Open。
- 本任务不请求也不授权冻结、基线恢复、真实能力启用、风险连带关闭或阶段推进。

## 3. R-0049 条目级证据映射

| R-0049 子项 | 合同 | 候选实现 / 测试 | 独立证据 | 判断 |
|---|---|---|---|---|
| terminal 父记录身份、授权来源、用途、状态、generation 与时间不可事后改写 | P3-045 §3、§6、§7；AC-12 | `authorization_terminal_immutable`、terminal DELETE/REPLACE guard；P3-046 AC-12 8/8，P3-047 等价 AC-12 8/8，P3-031 AC-12 PASS | P3-050 隔离复跑 P3-047 等价与 P3-031；P3-051 静态核对 trigger 覆盖 revoked/expired/superseded | 通过受控边界 |
| terminal scope/action/policy 不可 INSERT、UPDATE、改绑或无门 DELETE | P3-045 §3、§7；AC-13 | 三子表分别具备 terminal INSERT/UPDATE guard，UPDATE 同查 OLD/NEW parent；DELETE 仅允许受控清理；P3-046/P3-047 AC-13 与 P3-031 AC-13 PASS | P3-050 隔离回归与 PM Evidence；P3-051 逐 trigger/逐 AC 核对 | 通过受控边界 |
| 无 terminal generation、无 Tombstone、无 cleanup audit 或门未到 `cleanup_pending` 时不得清理 | P3-045 §7；AC-17 | Tombstone INSERT 绑定 terminal generation；三子表 DELETE 要求 Tombstone + cleanup audit + pending；P3-046/P3-047 AC-17 与 P3-031 AC-17 PASS | P3-050 隔离回归；P3-051 对 SQL join 条件与测试断言核对 | 通过受控边界 |
| 合法清理只能单向删除敏感子投影，保留 terminal 父、Tombstone 与最小 audit，旧包不可复活 | P3-045 §7；AC-18 | cleanup 状态机、cleaned 前三子表为空检查；P3-046/P3-047 AC-18 与 P3-031 AC-18 PASS | P3-050 独立合法 retry/cleaned/rollback 控制 + 隔离 AC 回归 | 通过受控边界 |
| cleanup subject/type/generation/command/reason/blocked time 自 INSERT 起不可改绑 | P3-045 §3、§7；P3-047 PM-CE-04/06 | P3-048 OLD/NEW 双侧、六字段、六状态、NULL、复合 UPDATE、替换/重建与多行矩阵；552 PASS；原 PM-CE-06 8/8 PASS | P3-050 自建 832 PASS，覆盖三方向、六字段×六状态、NULL、冲突语义、多行、调用方 rollback；PM 复跑逐条一致 | 独立主证据通过 |
| cleanup status/time 正向性及合法 generic/no-op 路径不回退 | P3-045 §7、AC-18 | P3-048 status/time、time、legal 类别分别 48、16、72 PASS | P3-050 自建 status/time 48、legal/no-op 80、transaction 8 PASS；文件型 integrity/quick/FK 全通过 | 通过受控边界 |
| 历史失败与当前通过证据可追溯、不被覆盖 | P3-045 §11 Evidence 合同；P3-048 只读基线 | P3-048 声明 40 个保护文件；P3-047 原 BYPASS 证据保留 | P3-050 40/40 hash 匹配；P3-051 再核对关键 hash 与 Manifest 一致 | 通过 |

以上映射没有用“552”或“832”总数代替具体风险项；每项均列明合同、具体 AC/场景、Evidence 来源和独立性层级。

## 4. P3-050 独立性与 Evidence 可信度核查

- 新建会话证明：`pm_dispatch_evidence/MANIFEST.md` 记录 `create_thread`、全新 thread ID、首轮只做隔离握手、正式启动前无工具操作；与 P3-050 Review、PM Review 一致。
- 延迟读取证明：计划文件 hash 为 `3ac78f…1680dc`，计划 hash 文件、独立脚本、结果、首轮 seal 的文件时间顺序与封存声明一致。
- 程序独立性：自建脚本只导入 Python 标准库，未 import/call P3-048/P3-049 runner；场景结构与 P3-049 只作封存后的比较。
- 结果一致性：首轮与 PM 复跑完整 JSON hash 因 `schema` 和临时数据库路径不同而不同；删除这些运行路径元数据后，832 条 `.results` 的规范化 SHA-256 均为 `b22cee38a953ad4a15e370acc49b6d0bb5817f79437516c38f48717bf39f7f0e`，配置完整性检查规范化 SHA-256 均为 `7aad636a1545df93fc023830df128f3d2a7f21fd91534f5348e76fe318a2ae21`。这不是证据冲突。
- 关键输入 hash：候选 SQL、P3-050 计划/脚本/首轮结果/seal、P3-048/P3-047 结果、原 PM-CE-06 脚本/失败结果均与各 Manifest 一致。
- `FREEZE_STATUS.md` 的任务叙述停留在 P3-040，但其相关冻结边界仍明确“不冻结 Schema/API、不恢复工程基线、不进入下一阶段”；D-0232 至 D-0237 与最新 `CURRENT_STATUS.md` 也一致。该运营索引滞后不构成 R-0049 Evidence 或冻结授权冲突。

## 5. 关闭建议的适用范围

建议关闭只覆盖：

1. 当前 hash 的候选 SQL 与直接合同测试；
2. Python 3.9.6 / SQLite 3.51.0 下的合成 memory/file SQLite；
3. `foreign_keys` ON/OFF、`recursive_triggers` ON/OFF 八配置；
4. P3-045 合同、P3-046/P3-047/P3-048 回归、P3-050 全新隔离独立 Evidence 与本任务静态/结构化核验；
5. 有限 Stage 3、单用户、单设备、本地受控、非商用、无外部用户、外部能力默认关闭的边界。

明确不覆盖真实 migration、既有数据库升级、WAL/多 writer 并发、崩溃/断电/备份恢复、生产性能、跨平台差异、真实调用者认证、真实用户确认 UX、真实 cleanup worker/保留策略、真实 DB/Vault/Tauri/IPC/用户文件、云/第三方模型、向量、同步、多设备、L3、外部用户或生产删除 SLA。

## 6. R-0049 失效与重开条件

出现任一情况，应重新打开 R-0049 或创建等价新风险，不得继续引用本建议：

- 候选 SQL、相关 trigger、AC-12/13/17/18、PM-CE-06 或 cleanup 状态机发生实质修改；
- 新发现 terminal 父/子 INSERT、UPDATE、DELETE、REPLACE、UPSERT、改绑、重建、批量或事务路径可提交；
- 新发现 Tombstone 主体、generation、command、reason、blocked time 或 cleanup status/time 可伪造、倒退、删除或替换；
- cleanup 可在 generation/audit/state gate 不成立时删除子投影，或可删除 terminal 父/Tombstone/最小 audit、复活旧包；
- P3-050/P3-051 关键 Evidence/hash、历史 preservation 或会话独立性证明失效；
- R-0048 后续发现可伪造 cleanup audit、lifecycle command 或相关原子证据，进而绕过 R-0049 的清理门；
- 适用范围扩展到真实数据库、既有数据迁移、并发/恢复或任何真实能力而未完成对应独立验证。

## 7. R-0048 必须保持 Open 的边界

| 仍开放范围 | 当前已有候选证据 | 为什么 P3-050/P3-051 不足以关闭 |
|---|---|---|
| Submission、canonical hash、idempotency 与 lifecycle command 绑定/重放 | P3-047 PM-CE-01 8/8 PASS | P3-050 独立脚本未重新攻击该协议；当前仅有执行回归与隔离复跑 |
| AuditEntry 同事务生成、append-only、correlation 唯一、预置/冲突回滚 | P3-045 AC-01/02/03/04/14/16；P3-047 等价回归 PASS | 未形成覆盖完整 evidence 产生链的全新独立攻击与真实故障/恢复验证 |
| Outbox immutable payload、availability、owner/generation CAS、lease、retry、complete/cancel/dead-letter | P3-047 PM-CE-02 8/8、PM-CE-03 16/16 及 AC-05/06/07/08 PASS | P3-050 只针对 Tombstone；未独立证明调度/租约/伪完成全边界 |
| Outbox retention/binding 与 generic job cleanup 作用域 | P3-047 PM-CE-05 33/33 PASS | 正式 retention 值、运维权限、真实 worker 和删除/恢复 SLA 未冻结或验证 |
| active→terminal generation/time 配对与 audit/outbox/submission 全回滚 | AC-09/10/11/14/16 PASS | 当前为候选 SQL 合成回归，未完成完整隔离攻击、并发、崩溃和真实 migration 验证 |
| actor claim、真实用户确认、调用者/进程身份与应用事务编排 | P3-045 明确由应用层负责，SQLite 不认证真实主体 | 未实现/未验证，不能由 DB 合成矩阵外推 |

因此，R-0049 的有限关闭建议不削弱 R-0048；后者继续承接 lifecycle/audit/outbox/generation/time/幂等命令的完整原子性与真实能力风险。

## 8. 角色与关卡结论

- 主责：风险关闭评估负责人、独立 QA / Evidence Reviewer——通过；风险、合同、测试、独立性、hash 和失效条件已逐项映射。
- AI 信任与安全负责人——R-0049 受控边界通过；重大动作确认、真实 actor 与完整 lifecycle evidence 仍由 R-0048 保持 Open。
- 数据 / 领域模型负责人——terminal 权威历史、敏感子投影与受控清理分层清楚；未把候选表/trigger 误写为核心模型或 Schema 冻结。
- 技术架构负责人——SQLite 候选不变量在当前矩阵可复核；真实 migration、并发、恢复和能力启用未外推。
- Gate 2：**Pass in Controlled Boundary**（R-0049）；R-0048 相关完整证据链仍 Open。
- Gate 3：**Pass in Controlled Boundary**（R-0049）；真实确认/actor/处理能力未通过。
- Gate 4：**Pass in Controlled Boundary**（R-0049）；真实 DB/生产环境未通过。

## 9. 最终建议

**建议关闭 R-0049；R-0048 保持 Open。** PM 验收和用户明确授权前，两项风险账本状态均不得由本会话修改。本结论不冻结任何资产、不恢复工程基线、不启用真实能力、不进入下一阶段，也不自行创建后续任务。
