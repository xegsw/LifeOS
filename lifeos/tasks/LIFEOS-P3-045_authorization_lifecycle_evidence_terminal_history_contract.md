# LIFEOS-P3-045｜Authorization 生命周期证据与终态历史边界合同

## 任务信息

- 任务 ID：LIFEOS-P3-045
- 任务名称：Authorization 生命周期证据与终态历史边界合同
- 优先级：P1
- 任务类型：决策型任务 / 权限证据合同设计 / Schema 责任边界
- 建议篇幅：1500-2500 字；正文聚焦明确决策、责任矩阵、可执行验收合同与后续工程输入，扩展方案放入后续任务建议
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要结合当前候选 SQLite Schema、P3-041/P3-043 反例和 P3-044 整改结果，区分 audit append-only、outbox 合法状态变化、Authorization generation/时间元数据与终态历史清理责任，并形成可直接转为工程测试的合同；Codex 更适合跨 SQL/测试/证据结构做有界技术决策整理。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：任务涉及权限、删除、撤回、审计证据链和数据主权核心边界；错误设计可能把合法 outbox 处理全部锁死，或继续允许伪造退休证据与历史语义改写，需要高强度推理和跨文件一致性核对。
- 允许降级模型：`None`
- 禁止降级条件：涉及 Authorization、AuditEntry、OutboxJob、generation、终态历史、删除/清理和 Schema 冻结前责任边界，不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置；不得因本任务不写代码而降低配置。
- 必须升级条件：发现需要改变冻结的核心领域模型或 AI 权限边界、需要新增核心实体、现有产品/技术合同互相冲突、无法在数据主权与历史不可变之间形成可执行边界、或结论将触发真实数据/真实 migration/风险关闭时，停止并回报 PM，不自行扩大范围。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选模型不可用时使用 `gpt-5.5` + `xhigh`，并在交付物记录触发原因、实际配置和影响
- 是否需要后续独立评审：No for this task；本任务只形成后续工程合同，不冻结 Schema/API、不关闭风险。未来若据此关闭风险、冻结 Schema/API、启用真实能力或阶段切换，仍须重新满足相应独立评审或用户明确批准的例外条件
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：数据 / 领域模型负责人、技术架构负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程设计 / SQLite 权限边界会话
- 推荐复用的会话：优先复用完成 P3-044 的 Codex 工程整改会话；若该会话仍有活动任务、发生上下文压缩后无法恢复可靠边界、工作区状态不明或任务授权混淆，则新建 Codex 工程设计会话
- 会话判断理由：P3-045 直接使用 P3-044 已建立的 Authorization/trigger/反例/evidence 上下文，但它是新的独立任务，不继承 P3-044 的工程修改授权；本任务只设计合同，不写 SQL 或测试。
- 是否需要独立性隔离：No；本任务不是 P3-044 独立复评，也不作风险关闭/冻结判断
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-044_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-043/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-041/independent_review.md`
  - `lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
  - `lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
  - `lifeos/deliverables/LIFEOS-P3-029_sql_migration_design_and_contract_tests.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049、R-0050 相关行
- 可复用既有读取结果：若同一会话已完整读取、之后未修改、未截断、未发生上下文压缩且读取状态可靠，可复用 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解
- 必须因变化或不确定性重读：最新 `CURRENT_STATUS.md`、本任务卡、P3-044 PM Review/交付物/manifest、当前 P3-031 candidate SQL、相关风险行；若发生上下文压缩或读取状态不可靠，重读根 `AGENTS.md` 和相关基础规则
- 任务完成后是否建议保留会话：Yes，作为 Authorization/SQLite 权限合同线后续工程输入会话；不得把本会话输出当作独立评审

## 背景

P3-044 已在执行与 PM 复跑范围内关闭 active Authorization 父记录 REPLACE/直接删除重建 P1。用户因 WorkBuddy 当前额度不足，明确批准不执行原计划中的 P3-045 隔离独立复评并继续下一任务。PM 将该决定记录为一次性流程例外：P3-044 可继续作为后续输入，但不记为“已独立通过”，不关闭 R-0044/R-0047/R-0050，不冻结 Schema/API，也不启用真实能力。

目前剩余最接近 Schema 责任边界的已知问题是：

- R-0048：退休只检查 audit/outbox 记录存在性，记录可预置、修改或删除；active generation 可独立升高；`created_at_ms`/`revoked_at_ms` 可被改写。
- R-0049：Authorization 进入 revoked/expired/superseded 后，父表安全包络和 scope/action/policy 子表仍可被事后改写。

这些问题不能直接通过“所有表禁止 UPDATE/DELETE”解决，因为 outbox 的状态、租约和重试计数存在合法变化，删除/清理还必须服从用户数据主权。本任务先形成一份窄范围、可实施、可验证的 V1 合同，再由后续工程任务决定如何实现。

## 目标

本任务完成后，PM 应能判断：

- AuditEntry 哪些字段必须 append-only，如何防止预置、回放、修改和删除伪造退休证据。
- OutboxJob 哪些字段属于不可变业务载荷，哪些属于可变运行态，合法状态转换、租约、重试和清理如何表达。
- Authorization generation 是否只能绑定明确生命周期转换，如何禁止 active 状态下无事件独立升高。
- `created_at_ms`、`revoked_at_ms` 及 expired/superseded 对应时间字段的状态约束与不可变规则是什么。
- terminal Authorization 父表、scope/action/policy 应采用完全不可变、受控清理、历史快照还是事件/投影分离；用户删除请求如何避免与历史可信度冲突。
- DB trigger、应用事务守卫、生命周期事件/意图记录和清理作业之间如何分责。
- R-0048/R-0049 哪些项必须在下一工程补丁关闭，哪些可有条件保留为 P2 Known Limitation，失效条件是什么。
- 后续工程任务的最小修改边界、测试矩阵、evidence 和停止条件是什么。

## 范围

### 1. 不变量与字段责任矩阵

- 对 `authorization`、`authorization_scope`、`authorization_action`、`authorization_policy`、`audit_entry`、`outbox_job` 与相关 correlation/idempotency 字段建立责任矩阵。
- 每类字段标记：权威业务事实、不可变证据、可变运行态、可清理派生、敏感引用或受控删除对象。
- 明确 INSERT/UPDATE/DELETE 允许性、允许主体、前置状态、必须追加的证据和失败错误。

### 2. AuditEntry 合同

- 决定 audit 是否 append-only，以及哪些字段从首次写入后禁止修改/删除。
- 处理预置 retirement audit、重复 correlation、错误 generation/version、事后删除/改写和事务回滚。
- 明确仅检查“存在”为什么不足，以及 V1 最小可行的防预置/防回放机制。
- 不得把日志文件、聊天记录或应用层口头约定当作权威 DB 证据。

### 3. OutboxJob 合同

- 分离不可变业务载荷字段与可变执行字段。
- 定义 pending/leased/succeeded/failed/retry/abandoned 等最小状态机，若现有枚举不同则给出兼容映射而不是擅自改代码。
- 明确 lease owner/expiry、attempt count、last error、available time 等字段的合法变化范围和审计要求。
- 明确 outbox 清理/归档条件，不能用全表 append-only 阻断正常处理，也不能允许改写 subject/generation/payload/idempotency。

### 4. Authorization generation 与时间元数据

- generation 变化必须绑定哪些合法事件；是否允许 active→active 维护、重试或补偿改变 generation。
- 禁止无事件 generation climb 的 DB/应用责任和测试合同。
- 定义 `created_at_ms` 永久不可变、`revoked_at_ms` 的 NULL/状态配对及 revoked/expired/superseded 时间表达；若需新增字段，只能作为待 PM 确认方案，不得直接改核心模型。
- 定义同一事务中 Authorization 状态、generation、audit 和 outbox 的原子顺序与失败回滚。

### 5. Terminal 历史与用户清理

- 明确 revoked/expired/superseded 父表安全包络及子表是否不可变。
- 区分业务历史保真、敏感引用最小化、用户删除权和物理清理。
- 比较至少三种方案：原行完全不可变；终态快照/事件权威 + 可清理投影；受控 redaction/tombstone 并保留最小审计摘要。
- 推荐 V1 方案并说明选择理由、最小字段、隐私代价、实现成本、导出/恢复影响与未来迁移路径。

### 6. 方案比较与推荐

- 至少比较：A. 纯 DB trigger；B. DB 不变量 + 应用事务守卫；C. 生命周期事件权威 + Authorization 投影。
- 对安全性、可实现性、V1 复杂度、崩溃恢复、测试难度、未来扩展和数据主权做对比。
- 给出单一推荐方案、明确不采用方案和触发重新评估的条件。
- 推荐不得改变技术架构 V0.1、核心领域模型 V0.1 或 AI 权限与信任模型 V0.1；若必须改变，标记 Blocked/需 PM 决策。

### 7. 后续工程验收合同

- 把推荐方案转成 10-20 条可执行测试，不编写测试代码。
- 覆盖预置/修改/删除 audit，修改 outbox 业务载荷，合法 lease/retry，generation climb，时间元数据伪造，terminal 父/子变异，合法退休/新版本，删除/清理和事务失败回滚。
- 对每条测试标注严重级别、预期结果、证据和是否阻塞 Schema/API 后续判断。
- 给出下一工程任务的允许修改范围、非范围、evidence manifest 要求和停止条件。

## 非范围

- 不修改 SQL、测试、runner、代码、Stitch 或任何已有工程 evidence。
- 不修改 P3-041/P3-043/P3-044 原始交付物、评审、PM Review 或 evidence。
- 不重新执行 P3-044 独立评审，不把用户流程例外写成独立评审 Pass。
- 不关闭 R-0040/R-0043/R-0044/R-0046/R-0047/R-0048/R-0049/R-0050，不改变 R-0045。
- 不冻结 Schema/API、SQL migration、工程基线或任何核心资产。
- 不执行真实 migration，不连接真实 DB/Vault/用户文件，不运行真实 Tauri/IPC，不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不修改核心领域模型、AI 权限边界或技术架构冻结合同；如确需变化，只提出 PM 阻塞问题。
- 不创建或启动后续工程任务。

## 输入与读取规则

- 先读取最新 `lifeos/CURRENT_STATUS.md` 和本任务卡，再读取会话路由列出的直接材料。
- 当前 P3-031 candidate SQL必须完整读取；历史评审优先定向读取 R-0048/R-0049 相关发现和证据，不读取无关完整历史。
- P3-025/P3-027/P3-029 只读取 Authorization/AuditEntry/OutboxJob/transaction guard/cleanup 相关章节；不要重写生产 Schema/API 全文。
- `RISK_LOG.md` 只读取任务卡指定风险；`DECISION_LOG.md` 如需读取，只读 D-0222 至 D-0225。
- 如果材料冲突，列出冲突、影响和需 PM 选择，不自行改动冻结合同。
- 交付物完成后调用本地预检；日志和长引用不粘贴到聊天。

## 角色检查点

主责角色必须重点回答：

- 权威业务事实、证据、运行态和可清理数据是否明确分层。
- 合同是否能在当前 SQLite + 本地优先架构落地，不依赖未冻结的云服务或事件平台。
- 是否避免把 outbox 的合法运行态误锁成不可变，也避免将其业务载荷暴露为可任意改写。
- 是否形成可直接转为工程任务和测试的单一推荐，而不是只罗列可能性。

协审角色必须重点检查：

- 用户撤回、过期、替代和删除后的授权历史是否可信且可解释。
- 用户数据主权与历史证据保真是否有明确冲突解决规则。
- AI/消费入口所依赖的 authorization generation、policy 和 evidence 不会被伪造或静默改写。
- 未把用户批准的独立评审例外扩大为风险关闭、Schema 冻结或真实能力准入。

## 核心问题

- V1 应采用 DB-only、DB + 应用事务守卫，还是事件权威/投影分离？
- audit 如何防预置、回放、UPDATE 和 DELETE？
- outbox 哪些字段不可变、哪些字段必须可变？
- generation 和时间元数据怎样与状态转换原子绑定？
- terminal 父/子历史怎样兼顾不可篡改与用户删除/清理？
- R-0048/R-0049 分别需要哪些工程整改和测试才能进入关闭候选？
- 下一任务应实现什么、明确不实现什么、遇到什么必须停止？

## 交付物

完整交付物路径：

`lifeos/deliverables/LIFEOS-P3-045_authorization_lifecycle_evidence_terminal_history_contract.md`

交付物必须包括：

- 执行摘要与适用边界
- 已验证事实、推断、建议和需 PM 决策事项
- 表/字段/操作责任矩阵
- AuditEntry append-only 与防预置/防回放合同
- OutboxJob 不可变载荷与可变运行态合同
- generation/时间元数据/状态/evidence 原子合同
- terminal 历史与用户清理三方案比较及单一推荐
- DB trigger、应用事务守卫、事件/投影责任比较和 V1 推荐
- R-0048/R-0049 条目级处置矩阵
- 10-20 条后续工程验收测试
- 后续工程任务允许范围、非范围、evidence 与停止条件
- 不可外推声明、剩余风险和 PM 必须确认的问题

## 验收标准

- 报告已保存到指定路径，正文在建议篇幅附近且没有扩写成完整 Schema 重设计。
- 对 AuditEntry、OutboxJob、Authorization generation/时间、terminal 父/子和清理责任均给出明确合同。
- outbox 合法状态变化与不可变业务载荷清楚分离。
- 至少三种方案完成比较并给出单一 V1 推荐及重新评估条件。
- R-0048/R-0049 每个已知问题都有处理方式、后续测试和风险状态建议，但没有自行关闭风险。
- 形成 10-20 条可执行验收测试和下一工程任务边界。
- 未修改代码、SQL、测试、工程 evidence、Stitch、PM 账本或冻结资产。
- 已完成本地预检并提供路径，或说明允许跳过原因。
- 聊天回复严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径和是否需要 PM 决策。

## 限制条件

- 不修改工程文件或 PM 账本。
- 不处理真实数据、真实 DB/Vault/文件或真实 Tauri/IPC。
- 不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭风险，不冻结资产，不恢复工程基线，不进入下一阶段。
- 不把本任务称为 P3-044 独立复评或替代独立评审 Pass。
- 不自行创建或启动后续任务。
- 无法使用推荐模型或后备模型时不得静默换模；停止并回报 PM。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天回复不要粘贴完整报告，只输出任务状态、3-8 条摘要、交付物路径、本地预检路径和是否需要 PM 决策。
