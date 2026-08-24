# LIFEOS-P3-047｜Outbox CAS 与生命周期控制包络 P0 整改及回归

## 任务信息

- 任务 ID：LIFEOS-P3-047
- 任务名称：Outbox CAS 与生命周期控制包络 P0 整改及回归
- 优先级：P0
- 任务类型：P0 工程整改 / 候选 SQL 安全补丁 / PM 反例迁移 / Evidence 生成
- 建议篇幅：1500-3000 字；报告仅保留整改映射、测试摘要、剩余风险与证据路径，完整日志、结构化结果、快照、环境和 hash 写入 evidence
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在当前候选 SQLite Schema 与合成应用事务守卫之间补齐 Outbox availability/lease CAS、Submission/hash 绑定、Tombstone 控制包络和 retention/cleanup 合同，并把 PM 反例固化为可执行回归；Codex 更适合窄范围高风险 SQL trigger、命令入口和 evidence 整改。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：任务包含 2 个 P1 和 3 个 P2，涉及权限撤回后的 Outbox 执行时序、租约所有权、幂等命令、删除历史和证据可信度；错误可能造成任务提前执行、假完成、清理身份被篡改或证据失配，质量优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务整体涉及权限、撤回、删除、证据链及 P1 Rework，不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置；不得因只有 5 个 PM 反例、候选代码局部或原回归已大量通过而降低配置。
- 必须升级条件：若 `xhigh` 无法稳定处理“DB 无法感知 UPDATE WHERE/CAS 调用者”的责任边界、需要新增内部运行态命令但无法证明不扩权、retention 参数化与默认拒绝冲突、并发领取产生不一致、或同一核心反例两次仍未关闭，先升级为 `gpt-5.6-sol` + `max`；若发现新增 P0/P1、真实能力触达、核心领域模型／技术架构／AI 权限边界必须变化、数据不可恢复或 evidence 冲突，立即停止并回报 PM。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选不可用时使用 `gpt-5.5` + `xhigh`，并在报告中记录触发原因、实际配置和影响；若无法满足禁止降级条件则停止，不得静默换模。
- 是否需要后续独立评审：Yes；整改通过并经 PM 复跑后，在关闭 R-0048/R-0049、冻结 Schema/API 或启用真实能力前，必须由与本执行会话隔离的评审会话进行独立工程复评。P3-044 的一次性豁免不延续。
- 是否允许修改工程文件：Yes，仅限授权边界列出的当前候选文件与 P3-047 目录
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 数据完整性工程负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程整改 / SQLite 权限与证据链会话
- 推荐复用的会话：优先复用执行 P3-046 的 Codex 会话。若该会话仍有活动任务、工作区状态不明、发生上下文压缩后无法可靠恢复授权边界或已经混淆任务，则改为新建 Codex 工程整改会话。
- 会话判断理由：P3-047 是对 P3-046 当前候选 SQL 的同根因窄整改，必须理解原 trigger、runner 和 PM 反例；复用可降低重复读取，但新任务的修改目录、非范围和验收要求必须重新建立。
- 是否需要独立性隔离：执行阶段 No；后续独立复评、风险关闭或冻结判断阶段 Yes
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅复用短报告字段，不代表进入快车道）
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-046_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-046/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-046/evidence/pm_counterexample_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-046/evidence/counterexample_results.json`
  - `lifeos/deliverables/LIFEOS-P3-046_authorization_lifecycle_evidence_terminal_history_candidate_implementation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-046/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-046/scripts/run_validation.py`
  - `lifeos/deliverables/LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract.md`
  - `lifeos/reviews/LIFEOS-P3-045_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0048、R-0049 相关行
  - `lifeos/DECISION_LOG.md` 中 D-0227 至 D-0229
- 可复用既有读取结果：同一会话中已完整读取、之后未修改、未截断、未压缩且读取状态可靠的 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- 必须因变化或不确定性重读：最新状态、本任务卡、P3-046 PM Review/反例代码/结果、P3-031 当前候选文件、相关风险和决策；若发生上下文压缩或规则版本不明，必须重读根 `AGENTS.md` 及相关稳定规则文件
- 任务完成后是否建议保留会话：Yes，作为候选 SQL 权限／证据链整改会话；不得用该会话独立复评自身结果

## 背景

P3-046 原入口及 PM 隔离复跑均得到 P3-046 248 PASS、P3-031 64 PASS、0 FAIL，但 PM 额外攻击发现 5 条未覆盖路径：

- PM-CE-02 / P1：未来 `available_at_ms` job 可提前领取。
- PM-CE-03 / P1：不带当前 owner/generation CAS 也可完成有效租约。
- PM-CE-01 / P2：任意 canonical hash 且无 Submission 仍可执行 lifecycle command。
- PM-CE-04 / P2：cleanup_pending Authorization tombstone 的身份和控制包络可改写。
- PM-CE-05 / P2：Authorization 专用 delete trigger 永久阻断其他 terminal outbox，且 Authorization outbox retention 未实现。

用户已采纳 PM Rework 并授权启动本任务。P3-045 的方案 B 与核心合同继续有效；P3-047 只补齐工程实现和反例，不重做架构设计，不关闭风险、不冻结 Schema/API、不触达真实能力。

## 授权边界

本任务允许：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限 PM-CE-01 至 PM-CE-05 的 DB 不变量、必要内部控制记录与注释。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限迁移 5 条 PM 反例、补充直接相关边界和调整因受控协议变化而失效的合法夹具。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限统一复跑、结构化结果、日志和非零退出合同。
- 更新 P3-031 当前 evidence，使当前 SQL/tests/runner hash、统计和日志一致。
- 在 `lifeos/engineering/LIFEOS-P3-047/` 新建当前候选 SQL 快照、runner、合成 fixture、工作库和 evidence。
- 将 P3-046 AC-01 至 AC-18 迁移为 P3-047 对当前协议的等价回归；如果 Submission/Outbox 受控命令使旧 helper 不再合法，应在新 runner 中诚实更新合法入口并保留相同安全断言。
- 可在候选 Schema 中新增一个非核心、append-only、一次性 `outbox_runtime_command` 或等价受控运行态入口，前提是它只表达 expected owner/generation/status/availability 的 worker 意图，不成为业务权威、权限主体、事件源或通用任务系统。
- 可为 lifecycle command 增加对现有 `submission` 的复合引用／一致性校验，并为相关 Submission 身份字段增加 append-only 约束；不得新造核心领域实体。
- 可增加候选 retention 参数／时间字段或受控清理门，但生产保留时长不得在本任务中冻结；未配置时必须默认拒绝 Authorization outbox 物理删除。
- 输出报告到 `lifeos/deliverables/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md`。

本任务禁止：

- 不修改或删除 P3-046 原报告、runner、evidence、任务卡、PM Review 和 PM 反例 evidence；这些全部是只读失败基线。
- 不通过降低 PM-CE 严重级别、改测试预期、让反例不执行、关闭 trigger/PRAGMA 或只测试 helper 的“正确用法”制造通过。
- 不新增生产 worker、真实 IPC/API、真实身份认证、密码学审计、事件溯源、跨进程多 writer、同步或多设备。
- 不写／执行真实用户 DB migration，不连接、迁移或写入真实 DB/Vault/文件/导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri/IPC，不启用网络、云／第三方模型、向量、L3 或外部用户。
- 不关闭 R-0048/R-0049 或其他风险，不冻结 Schema/API/SQL migration/工程基线，不进入下一阶段。
- 不修改 PM 账本，不自行创建或启动独立复评、风险关闭或其他后续任务。

## 必须整改的合同

### 1. PM-CE-02 / P1：Claim availability 与旧 generation CAS

- pending→leased 必须验证 `OLD.available_at_ms <= DB now`。
- Claim 必须绑定 expected old status、expected old lease generation 和 job id；并发竞争最多一个成功。
- 提前 1 ms、远未来、错误 old generation、已 leased、terminal 和重复 claim 必须 fail closed；`available_at_ms == DB now` 的边界应有明确结果。
- 不能只依赖调用者自愿写正确 WHERE。若 SQLite trigger 无法证明调用者携带 CAS，必须使用受控 runtime command 或等价、可直接攻击验证的 DB guard。

### 2. PM-CE-03 / P1：Completion owner/generation CAS

- leased→completed 必须绑定 expected current owner、lease generation、未过期 lease 和 current subject generation。
- 缺少 owner/generation、错误 owner、旧 generation、过期 lease、已取消／dead-letter、旧 subject generation 均不得完成或产生发布成功假象。
- 直接对 `outbox_job` 发起不带受控 guard 的 runtime UPDATE 必须拒绝；合法 worker 入口必须留下可审计的合成状态轨迹，但不得把 Outbox 提升为业务权威。
- Claim、renew、retry、cancel、dead-letter、complete 的合法/非法路径应使用同一明确责任模型，不能只特判 complete。

### 3. PM-CE-01 / P2：Submission、hash 与 lifecycle command 绑定

- `canonical_request_hash` 必须具有稳定格式，至少为可校验的 `sha256:` 值；非空但格式错误不得通过。
- 成功 lifecycle command 必须引用同一事务中已存在的 Submission 或等价幂等回执；namespace/idempotency、canonical hash、command、result subject 必须一致。
- Submission 的 namespace/idempotency/hash/command/result subject 绑定后不得 UPDATE/DELETE/REPLACE；不得在 command 完成后改写为另一请求。
- 缺 Submission、hash 不同、namespace/key 不同、result subject 不同、同 key 不同 hash、跨 Authorization 复用和外层 rollback 均须覆盖。
- 重放相同请求可以由合成应用 guard 返回既有结果或稳定冲突，但不得生成第二份 command/audit/outbox。

### 4. PM-CE-04 / P2：Authorization tombstone 控制包络不可变

- `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 自 INSERT 起不可变；禁止 UPDATE/REPLACE/改绑。
- 只允许 cleanup_status 按已确认状态机前进，并允许 `updated_at_ms` 随合法状态变化单调更新；无状态变化不得任意改历史时间。
- accepted、active_blocked、cleanup_pending、cleanup_failed/vendor_limited、cleaned 各阶段都必须攻击身份、generation 和控制字段改写。
- 合法重试不应放松最小 audit、terminal generation 和防复活约束。

### 5. PM-CE-05 / P2：Outbox cleanup 作用域与 retention

- Authorization 专用 delete guard 不得把所有其他 job type 永久锁死。若通用 Outbox cleanup 尚未冻结，本任务至少要把 Authorization 约束准确限定到自身，不改变其他类型既有行为。
- Authorization lifecycle job 只有 terminal、无活跃 lease、匹配 immutable audit 且 retention gate 满足时才可物理删除。
- 生产 retention 时长不在本任务冻结。应参数化并在未配置时默认拒绝；合成测试可使用明确 fixture 验证 before/at/after gate。
- retention 依据必须不可被普通 runtime mutation 倒退或伪造；删除 Outbox 不得改变 Authorization、AuditEntry、Submission、Tombstone 事实。

## 必测矩阵

- PM-CE-01 至 PM-CE-05 必须原样或更强地迁移到 P3-047 runner；P1/P2 级别不得降低。
- PM 原反例脚本与结果严格只读。P3-047 应记录同一攻击在新候选上的实际 PASS 证据，而不是覆盖旧 BYPASS 文件。
- Outbox：memory/file、FK ON/OFF、recursive triggers ON/OFF；claim/complete 至少覆盖 availability、owner、generation、expiry、subject generation 和双竞争。
- Submission/hash：格式、缺失、不匹配、重放、跨 subject、事务 rollback、append-only。
- Tombstone：所有控制字段在各 cleanup 状态的 UPDATE/REPLACE/改绑攻击。
- Retention：未配置默认拒绝、未到期拒绝、边界时刻、到期后合法删除、generic job 不受 Authorization 专用 guard 误伤。
- P3-045 AC-01 至 AC-18 必须在新受控协议下全部执行；不允许 Not Implemented/Unknown。
- P3-031 当前全量与 P3-044 active parent/children/replace/rebuild 直接相关回归必须无 P0/P1 回退。
- P3-046 原 runner 允许因协议升级不再作为当前通过入口，但其原文件/evidence 必须保持不变；P3-047 必须在 manifest 中逐项说明旧 helper 的替代入口和安全断言等价性。

## Evidence 要求

`lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md` 至少包含：

- 授权范围、实际模型、不可外推声明。
- 环境、Python/SQLite、准确命令、退出码、memory/file、PRAGMA 与事务矩阵。
- P3-046 原报告/runner/evidence、P3-046 PM Review/反例 evidence 的 before/after hash 保留证明。
- P3-031 当前输入/输出 hash，P3-047 SQL 快照与 runner hash。
- PM-CE-01 至 PM-CE-05 每项预期、实际、严重级别、所有配置实例和证据映射。
- 2 个 P1 与 3 个 P2 的根因→补丁→反例→合法路径→剩余边界矩阵。
- P3-045 AC-01 至 AC-18 在新协议下的逐项统计和证据路径。
- P3-031 全量、P3-044 直接相关、P3-047 专项的 PASS/FAIL/P0/P1/P2/Not Implemented/Unknown 与退出码。
- Outbox command/CAS 状态轨迹、Submission/command/audit/outbox 原子快照、Tombstone 包络快照、retention before/at/after 结果、文件库 integrity/FK 检查。
- 完整日志写入 evidence，聊天和报告不粘贴大段日志。

## 验收标准

- 报告与 evidence manifest 已保存到指定路径，本地预检完成或按规则说明跳过原因。
- PM-CE-01 至 PM-CE-05 在当前候选上全部 PASS；0 FAIL / 0 Not Implemented / 0 Unknown。
- future job、缺／错 owner/generation、过期 lease、旧 subject generation 和无受控 guard 的直接 runtime UPDATE 均不能 claim/complete。
- 合法 claim/renew/retry/cancel/dead-letter/complete 通过明确受控入口完成，并保留 DB fail-closed 与应用 CAS 的责任说明。
- lifecycle command 成功路径必须具有匹配、不可变的 Submission/hash 绑定；失败／重放无半状态或重复 evidence。
- Authorization tombstone 身份、generation 与控制包络不可变；cleanup 状态和 updated time 只合法前进。
- Authorization outbox retention 未配置默认拒绝，配置后 before/at/after 可验证；generic job 不再被 Authorization 专用 guard 误伤。
- P3-045 AC-01 至 AC-18 在新协议下全部真实执行并通过；P3-031 全量和 P3-044 直接相关回归无 P0/P1 回退。
- P3-046 原资产与 PM 反例 evidence hash 未改变；不得通过修改失败基线制造通过。
- 任何新增 P0/P1、数据不可恢复、清理／授权复活、核心合同变化或 evidence 冲突必须标记 Rework/Blocked 并停止扩大范围。
- 未触碰真实 DB/Vault/文件/Tauri/IPC、PM 账本、冻结资产或非授权目录。
- 任务结论只可作为整改候选和后续隔离复评输入，不得宣布风险关闭、Schema/API 冻结、工程基线恢复或阶段推进。

## 交付物

完整报告：

`lifeos/deliverables/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md`

Evidence manifest：

`lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md`

报告必须包含：实际模型、修改文件、5 条 PM 反例整改映射、受控 runtime command／等价方案说明、Submission/hash 绑定、Tombstone 不可变、retention 参数化、测试统计、剩余风险、evidence 路径和不可外推边界。

## 限制与停止条件

- 不修改 P3-046 原资产或 PM 反例 evidence，不修改 PM 账本。
- 不处理真实用户数据、真实数据库、Vault、文件能力、Tauri/IPC、网络、云／第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭风险、不冻结资产、不恢复工程基线、不进入下一阶段。
- 不把内部 command、Submission、Outbox、AuditEntry 或 Tombstone 升格为新的核心领域模型或已认证身份。
- 命中新增 P0/P1、合法生命周期严重回退、不可恢复损坏、真实能力触达或 evidence 冲突时立即停止并回报 PM。
- 不自行创建或启动后续独立复评、风险关闭或其他任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中只输出任务状态、3-8 条摘要、报告路径、evidence manifest 路径、本地预检路径、实际模型配置和是否需要 PM 决策；不要粘贴完整日志或报告正文。
