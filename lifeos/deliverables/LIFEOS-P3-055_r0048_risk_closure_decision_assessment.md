# LIFEOS-P3-055｜R-0048 风险关闭决策评估

## 1. 结论与授权边界

**建议：在严格限定的受控边界内建议关闭 R-0048；本文件不执行关闭。**

建议只覆盖当前候选 SQL（SHA-256：`bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`）、合成 memory/file SQLite、`foreign_keys` 与 `recursive_triggers` 各 ON/OFF 的八配置、P3-045 至 P3-054 当前 Evidence，以及有限 Stage 3 的单用户、单设备、本地受控边界。

此建议的依据是：P3-052 曾以全新隔离复评稳定发现两条 Outbox P1 与两条 lifecycle 初始值 P2；P3-053 只整改这四项；P3-054 又在全新隔离、先封存计划、后读取历史资产的条件下，以自建 runner 得到 80 PASS / 0 FAIL / 0 Unknown / 0 Not Implemented、P0/P1/明确 P2 bypass 均为 0。PM 隔离复跑同为 80 PASS，P3-031 回归 74 PASS、八配置矩阵 88 PASS，且 37 个历史只读资产的 before/after 散列一致。

本结论不是 R-0048 已关闭、Schema/API 或工程基线已冻结、真实能力可启用、或可进入下一阶段的陈述。最终关闭仍须 PM 验收与用户明确授权；本会话不修改风险账本，也不改变 R-0049。

## 2. 已验证事实

1. P3-045 已把 DB 不变量与应用事务守卫分责：数据库负责生命周期状态、generation、DB 时间、证据原子生成和不可变性；应用负责真实用户确认、身份与编排。P3-046、P3-047 的 PM 反例曾分别发现 Outbox CAS 与 Tombstone 包络缺口，说明本建议不把早期执行侧通过当作充分证据。
2. 当前 SQL 的 `authorization_lifecycle_command` 与 `submission` 具备 hash、idempotency、目标命令、Authorization 与 expected generation 绑定，且均不可更新或删除；命令触发器只接受 active Authorization 的预期 generation。
3. 当前 SQL 的同一 lifecycle command INSERT 依次完成 terminal Authorization、不可改写的 AuditEntry、canonical lifecycle Outbox 与 retention binding；其中任一 audit/outbox/binding 冲突会使该语句失败并回滚，不留下已终态而无对应证据的半状态。
4. P3-053 将 `authorization_state_change` Outbox 的直接伪造/替换改为必须匹配 command、Submission、terminal Authorization、AuditEntry、generation、payload、canonical ID/idempotency/correlation；retention 删除后保留不可重用的 correlation fence。P3-054 的 A/B 组独立攻击及 PM 复跑均通过。
5. P3-053 还把新 Authorization 的初始 generation 固定为 1，并禁止 non-revoked 初始/activation 携带 `revoked_at_ms`；P3-054 的 C 组覆盖 INSERT、REPLACE、activation 与 revoked/expired/superseded 配对，全部通过。
6. P3-054 的 D 组覆盖事务、多行语句与外层 rollback；文件型合成库的 close/reopen、`integrity_check`、`quick_check` 和 `foreign_key_check` 均无异常。

## 3. R-0048 条目级判断

| 判断项 | 受控边界判断 | 关键证据与限制 |
|---|---|---|
| lifecycle command / Submission | 通过 | append-only、canonical hash/idempotency/command/subject 绑定与 active+expected-generation 前置条件成立；P3-054 覆盖三终态完整链路、冲突/REPLACE 与 activation。它不认证提交者的真实身份。 |
| AuditEntry | 条件通过（仅作为生命周期组合证据） | lifecycle trigger 同语句生成固定 correlation 的最小 audit，UPDATE/DELETE/reinsert 被拒绝，预置冲突会回滚 lifecycle 命令。当前 SQL 并未把单独的首次 audit INSERT 认证为真实用户动作；因此任何消费端都必须同时核验 matching terminal Authorization、lifecycle command、Submission 与 correlation，而不得单独信任 audit 行。 |
| Outbox provenance、CAS、replay 与 retention | 通过 | P3-052 的 P1-01/P1-02 已被 P3-053 窄整改；P3-054 覆盖伪造 INSERT/REPLACE、错误 identity/payload/generation、CAS、合法三终态、retention 后 ID/correlation/idempotency/payload 重放及 generic job 合法清理。 |
| generation / 时间 | 通过 | 初始值、active→terminal 恰好 +1、created time 不可改、revoked time 配对与三终态均由 SQL 约束；P3-054 C 组和 P3-031 八配置回归通过。 |
| 事务原子性 | 通过 | command apply 中 parent、audit、outbox 与 binding 的冲突会终止同一 SQLite 语句；独立多行和 rollback 用例无 orphan/半状态。SQLite `RAISE(ABORT)` 后，应用若要撤销此前已成功的语句仍须显式 `ROLLBACK`，这是已知调用方边界而非本候选 SQL 的通过外推。 |
| 真实 actor / 用户确认 / 进程身份 | **不在通过范围内，必须显式排除** | `scoped_actor_claim` 是应用声明，Outbox owner 也是受控 SQL 字段；两者均不提供 OS、密码学或真实用户身份认证。本建议不得被解释为该边界已验证或风险已消失。 |

## 4. 推断与决策理由

在限定边界中，R-0048 所描述的已知结构性问题——预置/伪造 lifecycle Outbox、retention 后重放、错误 lifecycle 初始值、generation/time 不配对、无 CAS 的运行态改变与证据冲突产生半状态——已先被独立发现、再被最小范围整改、最后被新的隔离独立攻击与 PM 复跑验证。最新候选散列与 P3-053/P3-054 Manifest 一致，历史失败证据未被覆盖。因此，**没有充分依据仅因候选 SQL + 合成 SQLite 的已知结构完整性缺口而继续维持 R-0048 为 Open**。

这是一项有限推断：它不将数据库中的 actor claim 视为真实授权证明，也不把 append-only 记录单独抬升为脱离 Authorization/command/correlation 组合的权威事实。任何消费、审计展示或后续实现若把孤立 AuditEntry、孤立 runtime command 或无应用确认的 claim 当作真实用户动作，都超出本建议范围并应触发新的风险判断。

## 5. 建议关闭范围、非范围与重开条件

### 若 PM 与用户采纳，建议关闭的精确范围

- 当前 hash 的候选 SQL及其 P3-031 直接合同测试；
- Python/SQLite 合成 memory/file SQLite 与上述八配置；
- P3-045 合同、P3-046/P3-047 历史失败、P3-052 失败、P3-053 整改、P3-054 独立复评和当前 Evidence；
- 有限 Stage 3 的本地受控技术验证，不包含真实用户或外部服务。

### 明确非范围

真实 DB/migration/非空升级、WAL 或多 writer 并发、崩溃/断电/备份恢复、跨平台、真实 actor/用户确认 UX、进程身份、真实 worker 与 retention 运维权限、真实 Vault/Tauri/IPC/文件、云或第三方模型、同步/多设备、L3、外部用户和生产 SLA，均不在本建议内。R-0049 继续 Closed / Limited Controlled Boundary；本任务未触发其重开条件。

### 任一项发生即应重新打开 R-0048 或建立等价风险

1. 候选 SQL、lifecycle/Submission/Audit/Outbox/retention trigger、P3-031 合同或 P3-054 主 Evidence 出现实质变更、散列不一致或独立性失效；
2. 发现可提交的伪造/预置/重放 lifecycle 组合，或可绕过 provenance、lease CAS、retention fence、generation/time 或原子回滚；
3. 任何 AuditEntry、Outbox 或 lifecycle command 被新的消费路径单独作为真实用户授权或真实操作证明；
4. 适用范围扩展到任一明确非范围，特别是真实 actor/确认、真实数据库、并发、恢复或真实能力；
5. 新的 P0/P1、明确 P2 bypass、Not Implemented、Unknown 或历史 Evidence 保留失败出现。

## 6. 角色、关卡与待 PM 确认

任务卡没有逐项列出角色和关卡；为保持与 P3-052/P3-054 的连续性，本评估按“风险关闭评估 / 独立 QA 与 Evidence Reviewer”为主责，AI 信任与安全、数据/领域模型与技术架构为协审进行检查。这是本报告的覆盖口径，不是对任务卡或项目角色的修改。

- Gate 2（数据与来源）：**Pass in Controlled Boundary**；组合证据的来源、绑定、重放围栏与历史保留可核对。
- Gate 3（AI 权限与信任）：**Pass in Controlled Boundary**；已知撤回/失效生命周期证据路径 fail closed；真实 actor/确认仍为非范围。
- Gate 4（技术可行性）：**Pass in Controlled Boundary**；八配置、文件完整性、独立性与 PM 复跑成立。
- Gate 1、Gate 5：不适用；本任务不改产品范围或用户价值假设。

**需 PM 决策：** 是否接受本“建议关闭”的有限范围与重开条件，并提请用户作最终关闭授权。即使接受，也不得冻结资产、恢复基线、启用真实能力或推进阶段。

## 7. 本地预检

本任务是高风险风险关闭判断，本地模型不得提供或影响最终判断；为避免造成误导，按项目允许跳过规则未调用本地预检。PM 仍须按正常流程独立复核本任务卡、交付物、最新 Evidence、主账本与用户授权。
