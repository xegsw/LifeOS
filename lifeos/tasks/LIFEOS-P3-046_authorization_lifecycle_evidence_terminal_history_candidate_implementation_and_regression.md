# LIFEOS-P3-046｜Authorization 生命周期证据与终态历史合同候选实现及回归

## 任务信息

- 任务 ID：LIFEOS-P3-046
- 任务名称：Authorization 生命周期证据与终态历史合同候选实现及回归
- 优先级：P0
- 任务类型：工程整改任务 / 候选 SQL 安全补丁 / 权限与删除边界回归 / Evidence 生成
- 建议篇幅：1500-3000 字；报告只保留合同映射、修改摘要、测试统计、剩余风险与证据路径，完整日志、逐例结果、环境、快照和 hash 写入 evidence
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在候选 SQLite Schema 中实现跨 Authorization、AuditEntry、OutboxJob、Submission、Tombstone 的原子不变量，迁移 18 项合同测试并生成可复核 evidence；Codex 更适合高风险 SQL trigger、状态机、故障注入与回归执行。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：任务同时涉及权限生命周期、撤回／过期／替代、审计可信度、用户清理和防复活；错误可能造成权限状态与证据分裂、历史被静默改写或清理后复活，且需兼顾 SQLite trigger 递归、冲突回滚、合法 outbox 运行态与既有回归，质量优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务整体属于权限、撤回、删除、证据链核心边界，不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置；不得因 R-0048/R-0049 当前为 P2、合同已有详细 AC 或改动仅限候选 SQL而降低配置。
- 必须升级条件：若 `xhigh` 无法稳定处理 trigger 顺序／递归、事务半状态、cleanup 与 append-only 冲突，先升级为 `gpt-5.6-sol` + `max`；若发现新增 P0/P1 active 权限旁路、清理后复活、数据不可恢复、真实能力触达、核心实体／技术架构／AI 权限边界必须变化、候选与 evidence 冲突或同一失败两次仍无法解释，立即停止并回报 PM，不得扩大范围。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选模型不可用时使用 `gpt-5.5` + `xhigh`；执行前确认全部授权边界可保持，并在报告中记录触发原因、实际配置和影响。若无法满足禁止降级条件则停止，不得静默换模。
- 是否需要后续独立评审：Conditional；本任务可先由 PM 复跑验收，但在关闭 R-0048/R-0049、冻结 Schema/API 或据此启用真实能力前，必须另行完成与执行会话隔离的独立工程复评。用户此前对 P3-044 的一次性复评豁免不自动延续到本任务。
- 是否允许修改工程文件：Yes，仅限“授权边界”列出的候选工程文件和本任务目录
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 数据完整性工程负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程执行 / SQLite 权限与证据链会话
- 推荐复用的会话：优先复用已完成 P3-044、P3-045 的 Codex 权限边界任务线会话。若该会话仍有活动任务、已发生上下文压缩且无法可靠恢复规则／授权、工作区状态不明或上下文已混淆，则改为新建 Codex 工程执行会话。
- 会话判断理由：P3-046 直接把 P3-045 合同落到 P3-031 当前候选 SQL/tests/runner，并继承 P3-044 的权限写入防线与回归矩阵；属于同一工程线，不要求执行者独立评审自己的结果。
- 是否需要独立性隔离：执行阶段 No；未来独立复评、风险关闭或 Schema/API 冻结判断阶段 Yes
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅复用短报告结构，不代表进入快车道）
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract.md`
  - `lifeos/reviews/LIFEOS-P3-045_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-044/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0044、R-0046、R-0047、R-0048、R-0049、R-0050 相关行
  - `lifeos/DECISION_LOG.md` 中 D-0225 至 D-0227
- 可复用既有读取结果：同一会话中已完整读取、之后未修改、未截断、未压缩且读取状态可靠的 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- 必须因变化或不确定性重读：最新 `CURRENT_STATUS.md`、本任务卡、P3-045 合同与 PM Review、P3-031 当前 SQL/tests/runner/manifest、P3-044 当前 runner/manifest、相关风险与决策；若发生上下文压缩或基础规则版本不明，必须重读根 `AGENTS.md` 及相关基础规则文件
- 任务完成后是否建议保留会话：Yes，保留为候选 SQL 权限／证据链工程线；不得用该会话完成自身独立复评或风险关闭判断

## 背景与已确认决策

P3-041/P3-043 已证明当前候选 SQL 的 Authorization retirement evidence、generation／时间元数据和 terminal 历史仍存在 R-0048/R-0049 P2 缺口。P3-045 已形成并通过 PM 条件验收，用户现已明确采纳完整条件包：

1. 采用方案 B：数据库负责不可绕过的不变量与同事务 evidence，应用层负责真实用户确认、操作者真实性和业务编排。
2. 允许候选 Schema 新增非核心、append-only、一次性内部控制记录 `authorization_lifecycle_command`。
3. 允许 `authorization` 成为 tombstone／受控清理 subject。
4. 采用“最小非敏感 AuditEntry 长期只追加；敏感载荷可经显式确认单向清理”的口径。

该确认只授权候选工程实现，不是核心领域实体变更、AI 权限边界变化、Schema/API 冻结、风险关闭、真实能力准入或阶段切换。R-0048/R-0049 仍为 Open / Contract Candidate。

## 授权边界

本任务明确授权：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限实现 P3-045/P3-045 PM Review 已确认的 lifecycle command、retirement 原子 evidence、AuditEntry append-only、OutboxJob 载荷／运行态、generation／时间、terminal 不可变和 Authorization 受控清理合同。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限新增或调整 AC-01 至 AC-18、直接相关合法路径、故障注入和必要夹具。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限保持统一复跑入口、结构化统计、日志落盘和非零退出合同。
- 更新 P3-031 的当前 evidence manifest、结构化结果与日志，使其 hash、测试统计和当前候选文件一致；不得删除或改写历史任务 evidence。
- 在 `lifeos/engineering/LIFEOS-P3-046/` 创建本任务专属 SQL 快照、runner、合成 fixture、受控文件库、测试结果和 evidence；`work/` 下测试数据库必须是合成临时资产。
- 复用或迁移 P3-044 直接相关回归逻辑，对 P3-031 当前候选 SQL 验证 active Authorization 防线未回退；P3-044 原始报告/evidence 只读。
- 输出报告到 `lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md`。
- 调用本地预检脚本检查交付物覆盖、风险措辞、模型配置、测试统计和不可外推声明。

本任务不授权：

- 不修改 P3-039 至 P3-045 的原始交付物、评审、PM Review、任务卡或 evidence。
- 不修改 PM 账本、冻结看板、决策、风险或开放问题。
- 不把 `authorization_lifecycle_command` 升级为核心领域实体、事件权威源、安全主体或真实身份凭证。
- 不引入事件溯源、跨进程多 writer、同步／多设备或新的核心服务边界。
- 不实现真实 UI 确认、操作系统身份认证、密码学不可否认审计或生产 outbox worker；只验证 DB 合同和合成应用事务守卫。
- 不写或执行真实用户 DB migration，不连接、迁移或写入真实 DB/Vault/文件/导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri/IPC，不启用云／第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040/R-0043/R-0044/R-0046/R-0047/R-0048/R-0049/R-0050，不改变 R-0045 Closed 状态。
- 不冻结 Schema/API、SQL migration、工程基线、导出格式或生产 SLA，不进入下一阶段。
- 不自行创建或启动后续独立评审、风险关闭或其他任务。

## 目标

本任务完成后，PM 应能判断：

- active→revoked/expired/superseded 是否只能通过一次性 lifecycle command 发生，并由 DB 在同一事务内完成 generation +1、DB 时间、AuditEntry 与 OutboxJob；任何一步失败是否整体回滚。
- 预置 audit/outbox、重复或跨 Authorization command、错误 expected generation、错误状态、直接 terminal UPDATE 是否均不能伪造合法 retirement。
- AuditEntry 是否正常运行下严格 append-only；普通 cleanup 是否不能 UPDATE/DELETE/REPLACE 最小审计记录。
- OutboxJob 的 job/subject/generation/payload/idempotency 是否不可变，status/attempt/available/lease/error 是否只按明确状态机和 CAS 变化，旧租约／旧 subject generation 是否不能发布。
- Authorization generation、created/revoked/terminal 时间和 terminal parent/children 是否满足 P3-045 原子与不可变合同。
- Authorization tombstone／受控清理是否只能向前、不得作用于 active 授权、不得复活已清理身份、保留最小 audit 并诚实标记历史已清理。
- 直接 SQL lifecycle command 的威胁边界是否被诚实记录：它可在本地文件控制者模型下请求终态拒绝，但不能 grant/reactivate、改写包络或证明操作者真实身份。
- P3-031 全量合同测试和 P3-044 直接相关权限回归是否对当前候选 SQL 无 P0/P1 回退，evidence 是否可复跑。

## 工程合同范围

### 1. Lifecycle command 与 retirement 原子性

- 新增非核心 `authorization_lifecycle_command`，至少稳定绑定 command/idempotency、authorization、expected generation、target terminal status、scoped actor claim、canonical request hash 和必要时间／消费结果；字段及最终消费语义必须明确。
- 只允许目标 `revoked`、`expired`、`superseded`；不得通过 command 创建、grant、activate、reactivate、改写 scope/action/policy 或安全包络。
- command 必须 append-only，禁止 UPDATE/DELETE/REPLACE；重复 command/idempotency、跨 subject 复用和错误 hash 必须 fail closed 或返回同一幂等结果，不得生成第二份 evidence。
- DB trigger 必须在同一语句／事务内校验旧状态与 expected generation，使用 DB 时间完成 status、generation、updated/revoked time，并生成 audit/outbox。不得继续依赖预先存在的 audit/outbox 放行。
- audit/outbox 插入冲突、故障注入或应用事务后续失败时，Authorization、command/submission、audit/outbox 必须无半状态。

### 2. AuditEntry 最小只追加合同

- `correlation_id` 必须具备可验证唯一性并稳定绑定 Authorization id、新 generation 与 terminal status。
- AuditEntry 正常运行下禁止 UPDATE、DELETE、REPLACE；预置相同 correlation 只能令 retirement 整体冲突回滚，不能充当已有证据。
- 生命周期 AuditEntry 只保存最小 scoped reference、版本、终态 action/result、generation/correlation 与 DB 时间；不得在新增字段或测试 fixture 中写正文、路径、URL、自由错误文本或可猜内容 hash。
- `scoped_actor_ref` 只是应用提交的 actor claim，不得在报告中宣称已由 DB、操作系统或密码学认证。

### 3. OutboxJob 载荷与运行态合同

- job id/type、subject type/id/generation、payload reference、idempotency key 为不可变业务载荷；UPDATE/REPLACE/改绑必须拒绝。
- status、attempts、available time、lease owner/generation/expiry、last error 仅允许 P3-045 指定的状态机和 CAS；terminal job 不得回 pending。
- 旧 lease owner/generation、过期 lease 或旧 Authorization generation 的完成尝试必须拒绝或取消，不得形成“已发布”假象。
- OutboxJob 始终是非权威运行态；其缺失、清理或重试不得改变 Authorization/AuditEntry 业务事实。

### 4. Generation、时间与 terminal 历史

- 新 Authorization generation 从 1 起；active→terminal 恰好 +1；active→active、outbox 重试、租约、cleanup 不得升高 Authorization generation。
- `created_at_ms` 自 INSERT 起不可变；非 revoked 状态 `revoked_at_ms` 必须 NULL；revoke 时由同一 DB 时间写入 revoked/updated/audit，之后不可变。expired/superseded 的权威时间为 immutable audit occurred time并与转换时 updated time一致。
- terminal Authorization 父身份、安全包络、status/generation/time 及 scope/action/policy 默认拒绝 INSERT/UPDATE/DELETE/REPLACE/改绑；合法受控清理是唯一窄例外。

### 5. Tombstone 与受控清理

- 将 `authorization` 加入 tombstone subject type；只允许 terminal Authorization 进入清理流程，active/proposed/granted 必须拒绝或保持 active_blocked 前不可清理。
- 清理状态只能向前；无 tombstone、未达到 `active_blocked`/明确 cleanup gate、generation 不匹配或缺少最小 cleanup audit 时，不得删除／单向清理任何 Authorization 敏感投影。
- 允许的最小实现可以选择：删除 terminal scope/action/policy 敏感投影并保留父行，或在引用完整性允许时删除 terminal parent/children 投影；必须在报告中说明所选策略、无法清理的引用情况和诚实降级表现。
- AuditEntry 最小行不得随普通对象清理被改写或删除；若候选结构无法在不改变核心模型的前提下满足此条件，应停止并报告 Blocked，不得引入未授权审计 redaction 例外。
- 清理后必须保留 Authorization tombstone 与最小 cleanup audit，禁止相同 Authorization id 被 REPLACE/重建，旧 restore/import 包不得恢复 active 或历史敏感投影。
- 整库由用户销毁本地库不属于本任务的行级 cleanup，不需要在候选 SQL 中模拟。

## 必测矩阵

P3-045 AC-01 至 AC-18 必须逐项映射为可运行测试，不得合并后遗漏。至少额外覆盖：

- lifecycle command：直接 SQL actor claim、重复 command、重复 idempotency、错误 hash、错误 expected generation、错误 target status、跨 Authorization 重放、同事务 rollback。
- retirement：revoke/expire/supersede 三状态；内存／文件；FK ON/OFF；recursive triggers ON/OFF；autocommit／显式 commit／rollback；audit/outbox 故障注入。
- AuditEntry：UPDATE/DELETE/REPLACE、预置 correlation、普通重复 INSERT、合法 append。
- OutboxJob：全部合法／非法状态转换，immutable payload mutation，lease owner/generation CAS，旧 subject generation 完成，terminal 回流和受控 terminal 清理。
- Authorization：active generation 单独升高、created/revoked 预写／改写、terminal parent/children 三种写操作和 REPLACE/改绑。
- Cleanup：无 tombstone、错误状态、generation 不匹配、active subject、合法 terminal cleanup、重复 cleanup、清理失败重试、同 id 重建、旧包恢复候选不复活。
- 回归：P3-031 当前全量测试；P3-040/P3-042/P3-044 中对当前候选 SQL直接相关的 active parent/children、替换／重建和合法生命周期集合。

如果某矩阵维度无法由当前运行时控制，必须标记 Not Implemented/Blocked 并使任务不能宣称通过；不得把未执行写成 PASS。

## Evidence 要求

`lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md` 至少包含：

- 任务授权边界与不可外推声明。
- 环境、Python/SQLite 版本、OS、PRAGMA、准确复跑命令和退出码。
- P3-031 当前候选 SQL/tests/runner 的输入 hash，P3-046 输出 hash，以及 P3-044 原 evidence 未修改证明。
- AC-01 至 AC-18 的逐项 ID、级别、预期、实际、后端／PRAGMA／事务组合和 evidence 文件映射。
- P3-031 全量回归、P3-044 直接相关回归、P3-046 专项测试的 PASS/FAIL/P0/P1/P2/Not Implemented/Unknown 统计。
- lifecycle command、Authorization、AuditEntry、OutboxJob、Submission、Tombstone 的失败前后快照与原子性结论。
- Outbox 状态机轨迹、lease CAS、cleanup 状态机、重放／预置／故障注入结果。
- 受控文件库 `integrity_check`、`foreign_key_check` 及测试数据库仅含合成数据的声明。
- 报告、manifest、结构化结果与原始日志之间的可核对关系；完整日志不得粘贴进聊天。

## 验收标准

- 报告与 evidence manifest 已保存到指定路径，本地预检已完成或按规则说明允许跳过原因。
- P3-045 AC-01 至 AC-18 全部有真实可运行测试和独立结果，不存在遗漏、Not Implemented 或 Unknown。
- 三种 terminal transition 的 parent/generation/DB time/audit/outbox 在同一事务内原子提交；直接 UPDATE、预置 evidence、重复／跨 subject command 与任一故障均不能形成半状态。
- AuditEntry append-only、OutboxJob immutable payload + legal runtime state machine、Authorization generation/time/terminal 历史合同均由真实 DB 约束或可验证的应用事务守卫实现，而非只修改测试期望。
- 受控清理不得作用于 active Authorization，不得删除最小 AuditEntry，不得重建相同已清理身份或通过旧包复活。
- 直接 SQL actor claim 的有限可信度被明确记录，不得宣称强身份、密码学不可否认或生产安全已完成。
- P3-031 当前全量回归及 P3-044 直接相关权限回归为 0 P0 / 0 P1 / 0 FAIL / 0 Not Implemented / 0 Unknown；P3-046 专项 AC 也必须为 0 FAIL / 0 Not Implemented / 0 Unknown。
- 任何新增 P0/P1、数据不可恢复、cleanup 复活、核心合同冲突或 evidence/hash 不一致必须诚实标记 Rework/Blocked，停止扩大范围。
- 未触碰真实 DB/Vault/文件/Tauri/IPC、PM 账本、冻结资产或非授权目录。
- 任务结论只能是候选实现和后续评审输入；不得宣布 R-0048/R-0049 关闭、Schema/API 冻结、工程基线恢复或进入下一阶段。

## 交付物

完整工程报告：

`lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md`

Evidence manifest：

`lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md`

报告必须包含：任务与实际模型配置、实际修改文件、P3-045 条件逐项实现映射、AC-01 至 AC-18 统计、回归摘要、直接 SQL actor 边界、cleanup 策略、剩余风险、证据路径和不可外推声明。

## 限制与停止条件

- 不修改历史交付物、评审、PM Review、任务卡或 evidence；不修改 PM 账本。
- 不处理任何真实数据、真实用户数据库、Vault、文件、Tauri/IPC、云／第三方模型、同步、多设备、L3 或外部用户。
- 不关闭风险、不冻结资产、不恢复工程基线、不进入下一阶段。
- 不把内部 command、audit 或 tombstone 升格为核心领域模型或已认证身份。
- 发现新增 P0/P1、清理后复活、不可恢复损坏、合法生命周期严重回退、合同必须改变、真实能力触达或 evidence 冲突时，立即停止并回报 PM。
- 不自行创建或启动独立复评、风险关闭或其他后续任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中只输出任务状态、3-8 条摘要、报告路径、evidence manifest 路径、本地预检路径、实际模型配置和是否需要 PM 决策；不要粘贴完整日志或报告正文。
