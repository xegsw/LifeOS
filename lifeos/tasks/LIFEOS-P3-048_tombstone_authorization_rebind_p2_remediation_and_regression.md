# LIFEOS-P3-048｜Tombstone 向 Authorization 改绑旁路 P2 整改及回归

## 任务信息

- 任务 ID：LIFEOS-P3-048
- 任务名称：Tombstone 向 Authorization 改绑旁路 P2 整改及回归
- 优先级：P0（P3-047 P0 整改链收口；本次已知缺口为 PM-CE-06 / P2）
- 任务类型：P0 工程整改链窄补丁 / 候选 SQL 安全约束 / PM 反例迁移 / Evidence 生成
- 建议篇幅：1500-3000 字；只报告根因、补丁、反例矩阵、回归统计、剩余风险和 evidence 路径
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在现有候选 SQLite trigger 与合成合同测试中窄修 Tombstone 身份／控制包络改绑旁路，并迁移 PM-CE-06 八配置反例；Codex 更适合可运行 SQL 补丁、测试复跑和 evidence 整理。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：虽然已知缺口为 P2，但它属于 P0 整改链，涉及权限撤回、删除历史、cleanup 身份与证据链；补丁若过宽可能破坏 generic Tombstone 合法语义，若过窄可能继续留下 UPDATE/REPLACE/状态组合旁路，因此质量优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务涉及权限、撤回、删除和证据链核心边界，且直接处理 PM Rework；不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置，不得因仅一条 P2 反例而降级。
- 必须升级条件：若 `xhigh` 无法证明 OLD/NEW subject 类型、身份字段、cleanup 状态与时间组合均 fail closed，或发现 REPLACE／重建、合法 cleanup 状态机、generic Tombstone 既有语义与补丁发生冲突，先升级为 `gpt-5.6-sol` + `max`；若发现新增 P0/P1、真实能力触达、核心领域模型／技术架构／AI 权限边界必须变化、不可恢复数据风险或 evidence 冲突，立即停止并回报 PM。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选不可用时使用 `gpt-5.5` + `xhigh`，并在报告中记录原因、实际配置和影响；无法满足禁止降级条件时停止，不得静默换模。
- 是否需要后续独立评审：Yes；整改通过并经 PM 复跑后，仍须由与执行会话隔离的评审会话复核，才能讨论 R-0048/R-0049 关闭、Schema/API/migration/工程基线冻结或真实能力启用。
- 是否允许修改工程文件：Yes，仅限本任务授权边界
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 数据完整性工程负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程整改 / SQLite 权限与证据链会话
- 推荐复用的会话：优先复用执行 P3-047 的 Codex 工程会话；若该会话仍有未完成修改、发生上下文压缩后无法可靠恢复授权边界、工作区状态不明或已混入其他活动任务，则新建 Codex 工程整改会话。
- 会话判断理由：P3-048 是 P3-047 同一候选 SQL、同一 Tombstone trigger 的单根因窄整改，不要求执行会话独立评审自身成果；复用能保留工程上下文，但必须把本任务作为新的独立任务并重新建立修改授权。
- 是否需要独立性隔离：执行阶段 No；后续独立复评、风险关闭、冻结或阶段判断 Yes
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅复用短报告结构，不代表进入快车道）
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-047_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-047/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-047/evidence/counterexample_results.json`
  - `lifeos/deliverables/LIFEOS-P3-047_outbox_cas_and_lifecycle_control_envelope_p0_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-047/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0048、R-0049
  - `lifeos/DECISION_LOG.md` 中 D-0230、D-0231
- 可复用既有读取结果：同一会话中已完整读取、之后未修改、未截断、未压缩且读取状态可靠的 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- 必须因变化或不确定性重读：最新状态、本任务卡、P3-047 PM Review/PM Evidence、当前候选 SQL/tests、相关风险与决策；若上下文压缩或规则版本不明，重读根 `AGENTS.md` 和相关稳定规则文件
- 任务完成后是否建议保留会话：Yes，供同一候选 SQL 工程线后续测试复跑或 evidence 整理；不得用该会话独立复评自身结果

## 背景

P3-047 原专项回归为 297 PASS / 0 FAIL，P3-031 当前全量为 69 PASS / 0 FAIL，上一 PM 会话隔离复跑统计一致且 P3-046 只读失败基线保持不变。但 PM 静态核查发现 `authorization_tombstone_control_envelope_immutable` 只在 `OLD.subject_type='authorization'` 时保护控制包络。

PM-CE-06 证明：可先插入普通 `artifact` Tombstone，再通过 UPDATE 将其改绑为 `authorization/auth1`，并同时伪造 `generation`、`command_id`、`reason_code` 和 `blocked_at_ms`。该旁路在 memory/file、FK ON/OFF、recursive triggers ON/OFF 共 8 个配置中全部复现，0 PASS / 8 BYPASS，P2=8，入口退出码 1。

用户已采纳 P3-047 的 `Accepted / PM Adjusted to Rework` 结论并授权继续。本任务只关闭 PM-CE-06 及直接相邻写语义，不重做 P3-047 已通过的 Outbox CAS、Submission/hash 或 retention 主体。

## 授权边界

本任务允许：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限 Tombstone subject 身份、Authorization 控制包络、cleanup 状态／时间相邻不变量的窄修。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限迁移 PM-CE-06、补充直接相邻 UPDATE/REPLACE/复合字段/状态组合反例，以及调整因约束补强而失效的合法合成夹具。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限统一复跑、结构化结果、日志和非零退出合同。
- 更新 P3-031 当前 evidence，使当前 SQL/tests/runner hash、统计与日志一致。
- 在 `lifeos/engineering/LIFEOS-P3-048/` 新建候选 SQL 输入快照、专项 runner、合成文件库和 evidence。
- 输出报告到 `lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`。

本任务禁止：

- 不修改 P3-047 任务卡、交付物、runner、执行 evidence、PM Review、PM-CE-06 脚本与结果；这些全部是只读 Rework 基线。
- 不修改 P3-046 原报告、runner、原失败 evidence、PM Review 或 PM 原反例；这些继续严格只读。
- 不重写 P3-047 已通过的 Outbox runtime command、CAS、Submission/hash 或 retention 主体；若补丁意外影响这些部分，只允许为回归兼容作最小必要调整并必须在报告中说明。
- 不降低 PM-CE-06 严重级别、不改测试预期、不让反例跳过、不关闭 trigger/PRAGMA，不只测试 helper 的正确用法。
- 不新增核心领域实体、生产 worker、真实 IPC/API、真实身份认证、事件溯源、跨进程多 writer、同步或多设备。
- 不写或执行真实用户 DB migration，不连接、迁移或写入真实 DB/Vault/文件/导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri/IPC，不启用网络、云／第三方模型、向量、L3 或外部用户。
- 不修改 PM 账本，不关闭 R-0048/R-0049 或其他风险，不冻结 Schema/API/SQL migration/工程基线，不进入下一阶段。
- 不自行创建或启动独立复评、风险关闭或其他后续任务。

## 必须整改的合同

### PM-CE-06 / P2：Tombstone 身份与 Authorization 控制包络自 INSERT 起不可改绑

- 普通 Tombstone 不得通过 UPDATE、复合 UPDATE 或等价替换语义改绑为 Authorization Tombstone。
- Authorization Tombstone 不得改绑为普通类型、另一 Authorization、另一 `subject_id` 或另一 generation。
- `subject_type`、`subject_id` 的不可变责任必须覆盖 OLD/NEW 两侧，不能只在 OLD 已为 Authorization 时生效。
- 当 OLD 或 NEW 涉及 Authorization 时，`generation`、`command_id`、`reason_code`、`blocked_at_ms` 不得被同时或单独伪造。
- 不得通过在同一 UPDATE 中同时改写 `cleanup_status`、`updated_at_ms` 与身份字段绕过 insert contract 或 cleanup 状态机。
- `accepted`、`active_blocked`、`cleanup_pending`、`cleanup_failed`、`vendor_limited`、`cleaned` 各状态的身份／包络攻击必须 fail closed。
- 合法 cleanup_status 单向前进和 `updated_at_ms` 合法单调更新必须保留；不得因过宽 trigger 阻断任务卡已确认的合法状态变化。
- generic Tombstone 的既有合法语义不得在无证据情况下被扩大或收窄；若选择全局冻结 subject identity，必须通过回归证明不会破坏当前合同并明确这是实现不变量而非核心领域模型冻结。

## 必测矩阵

- 原 PM-CE-06 必须原样迁移并在新候选上覆盖 memory/file、FK ON/OFF、recursive triggers ON/OFF 共 8 个配置，全部 PASS。
- 覆盖至少以下路径：
  - generic→Authorization 改绑；
  - Authorization→generic 改绑；
  - Authorization A→Authorization B 改绑；
  - subject_type、subject_id、generation、command_id、reason_code、blocked_at_ms 单字段与复合字段更新；
  - 身份／包络字段与 cleanup_status、updated_at_ms 同语句组合更新；
  - 六个 cleanup 状态；
  - `INSERT OR REPLACE`、冲突 INSERT、DELETE/reinsert 或任务当前 Schema 允许触达的等价替换／重建相邻路径；
  - 多行 UPDATE 原子失败，不得出现部分改绑；
  - 合法 cleanup 状态推进、合法重试和时间单调更新。
- 复跑 P3-047 专项 297 条现有回归或其不弱于原断言的当前等价入口；0 FAIL / 0 Not Implemented / 0 Unknown。
- 复跑 P3-031 当前全量；不得出现 P0/P1/P2 回退。
- 核对 P3-047 PM-CE-06 原脚本／结果和 P3-046 原失败基线 hash 均未改变。
- 文件型 SQLite 必须执行 integrity/quick/FK 检查。

## Evidence 要求

`lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md` 至少包含：

- 授权范围、实际模型、不可外推声明。
- 环境、Python/SQLite、准确命令、退出码、memory/file 与 PRAGMA 矩阵。
- P3-047 任务卡／报告／runner／执行 evidence、P3-047 PM Review／PM-CE-06 脚本／结果的 before/after hash 保留证明。
- P3-046 原失败基线 hash 保留证明。
- P3-031 当前输入/输出 hash、P3-048 SQL 快照与 runner hash。
- PM-CE-06 根因→补丁→原攻击→相邻攻击→合法路径→剩余边界矩阵。
- 六 cleanup 状态、单字段／复合字段、同语句状态组合、替换／重建、多行原子性和合法状态推进的逐项统计。
- P3-047 专项等价回归、P3-031 全量、P3-048 专项的 PASS/FAIL/P0/P1/P2/Not Implemented/Unknown 与退出码。
- 文件库 integrity/quick/FK 检查和关键 before/after 快照。
- 完整日志写入 evidence；聊天与报告只提供摘要。

## 验收标准

- 报告与 evidence manifest 保存到指定路径；本地预检完成或按规则说明跳过原因。
- PM-CE-06 在 8 个配置中全部 PASS，0 BYPASS / 0 Not Implemented / 0 Unknown。
- generic→Authorization、Authorization→generic、Authorization A→B、单字段／复合字段／状态组合／多行更新和可触达替换语义均 fail closed。
- 合法 cleanup 状态机与 updated time 单调更新无回退。
- P3-047 专项等价回归与 P3-031 当前全量无失败；不得通过弱化原断言制造通过。
- P3-047 Rework 基线、PM-CE-06 原 Evidence 和 P3-046 原失败基线 hash 未变化。
- 未修改非授权工程范围或 PM 账本，未触达真实能力，未关闭风险，未冻结资产，未进入下一阶段。
- 新增 P0/P1、不可恢复损坏、合法 lifecycle 严重回退、核心合同变化或 evidence 冲突时必须标记 Rework/Blocked 并停止扩大范围。
- 任务结论只可作为整改候选和后续隔离复评输入，不得宣布 R-0048/R-0049 关闭、Schema/API/migration/工程基线冻结或生产适用。

## 交付物

完整报告：

`lifeos/deliverables/LIFEOS-P3-048_tombstone_authorization_rebind_p2_remediation_and_regression.md`

Evidence manifest：

`lifeos/engineering/LIFEOS-P3-048/evidence/MANIFEST.md`

报告必须包含：实际模型、修改文件、PM-CE-06 根因与补丁、受保护反例及相邻攻击、合法 cleanup 状态机回归、测试统计、只读基线保留、剩余风险、evidence 路径与不可外推边界。

## 限制与停止条件

- 不修改 P3-047/P3-046 原资产或 PM 反例 evidence，不修改 PM 账本。
- 不处理真实用户数据、真实数据库、Vault、文件能力、Tauri/IPC、网络、云／第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭风险、不冻结资产、不恢复工程基线、不进入下一阶段。
- 不把 Tombstone、Submission、Outbox、AuditEntry 或 command 升格为新的核心领域模型或认证系统。
- 命中新增 P0/P1、合法状态机严重回退、不可恢复损坏、真实能力触达或 evidence 冲突时立即停止并回报 PM。
- 不自行创建或启动后续独立复评、风险关闭或其他任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中只输出任务状态、3-8 条摘要、报告路径、evidence manifest 路径、本地预检路径、实际模型配置和是否需要 PM 决策；不要粘贴完整日志或报告正文。
