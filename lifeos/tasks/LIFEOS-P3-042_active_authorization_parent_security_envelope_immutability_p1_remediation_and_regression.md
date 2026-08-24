# LIFEOS-P3-042｜Active Authorization 父表安全包络字段不可变 P1 整改与回归

## 任务信息

- 任务 ID：LIFEOS-P3-042
- 任务名称：Active Authorization 父表安全包络字段不可变 P1 整改与回归
- 优先级：P0
- 任务类型：工程整改任务 / 候选 SQL 补丁 / 权限边界回归 / Evidence 生成
- 建议篇幅：1500-3000 字；完整日志、结构化测试结果和 hash 写入 evidence，报告只保留整改映射、测试摘要、证据路径、剩余风险和不可外推边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在候选 SQLite Schema 中补齐 active Authorization 父表安全包络不可变约束，扩展合同测试、复跑既有高风险回归并生成可复核 evidence；Codex 更适合窄范围 SQL trigger 整改、测试与证据整理。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：这是 P0 优先级权限边界整改，错误可能造成授权用途、处理器、位置、来源、有效期或策略版本被静默改写；需要同时保持合法生命周期、既有 42/128 项回归和证据链一致，质量优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务整体涉及 P0 权限边界与后续风险关闭输入，不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置；不得因补丁看似机械而降低配置。
- 必须升级条件：发现新增 P0、真实能力触达、候选 SQL与 evidence hash 冲突、合法退休/新版本路径回退、需要同时改动 R-0048/R-0049 设计边界、或无法稳定复现 P3-041 七个 P1 时，立即停止扩大范围并回到 PM；不得自行扩展任务。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选模型不可用时使用 `gpt-5.5` + `xhigh`，并在交付物中记录触发原因和是否影响验收范围
- 是否需要后续独立评审：Yes；整改通过后必须创建 P3-043，并由未参与 P3-042 执行的隔离独立评审会话复核
- 是否允许修改工程文件：Yes，仅限本任务授权范围
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 工程整改负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程整改 / SQLite 权限边界会话
- 推荐复用的会话：优先复用完成 P3-040 的 Codex 工程整改会话；若该会话已发生上下文压缩、仍有未完成任务、无法确认工作区状态或边界已经混淆，则改为新建 Codex 工程整改会话
- 会话判断理由：P3-042 与 P3-040 修改同一 P3-031 候选 SQL、合同测试和受控 SQLite 回归，属于同一工程线的后续 P0 窄整改；P3-041 独立评审会话不得用于执行本任务。
- 是否需要独立性隔离：执行阶段 No；P3-043 复评阶段 Yes，且不得由本执行会话评审自己的整改
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅复用短报告字段，不代表本任务进入快车道）
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-041_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-041/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/counter_example_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/counter_example_results.json`
  - `lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0044、R-0046、R-0047、R-0048、R-0049 相关行
- 可复用既有读取结果：若同一 Codex 工程会话已完整读取、之后未修改、未截断、未发生上下文压缩且能可靠确认读取状态，可复用 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解
- 必须因变化或不确定性重读：`lifeos/CURRENT_STATUS.md`、本任务卡、P3-041 独立评审/PM Review/反例 evidence、P3-031 当前候选 SQL与测试、P3-040 当前 runner/manifest、相关风险行；发生上下文压缩时还必须重读根 `AGENTS.md` 和相关基础规则
- 任务完成后是否建议保留会话：Yes，作为候选 SQL 权限边界整改线保留；不得用于 P3-043 独立复评

## 背景

P3-041 独立复评确认 P3-040 已真实关闭已知 11 个 active Authorization 子表 P1，但新增反例稳定发现 7 个父表字段旁路：active Authorization 的 `processor`、`purpose`、`location`、`grantor_ref`、`expires_mode`、`policy_version` 及复合字段可在 generation 不变、无 audit 追加时被静默修改。PM 在隔离临时副本复跑得到 19 PASS / 19 bypass，其中 P1=7、P2=12，并根据任务卡将评审结论校正为 Rework。用户已确认采纳 Rework 并授权启动本任务。

本任务只关闭父 Authorization 安全包络字段的 P1 根因。R-0048 的 audit/outbox 可变、预置证据与 generation 独立升高，以及 R-0049 的 terminal 子表历史语义可变，必须继续记录但不得混入本次补丁。P3-042 通过也不等于风险关闭、Schema/API 冻结、工程基线恢复或真实能力准入。

## 授权边界

本任务明确授权：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限增加 active Authorization 父表安全包络字段不可变约束及必要注释。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限新增本任务负测、合法路径测试和必要夹具调整。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限保持单一复跑入口、统计和非零退出合同。
- 更新 P3-031 evidence manifest、结构化结果和日志，记录最新稳定源文件 hash 与回归统计。
- 在 `lifeos/engineering/LIFEOS-P3-042/` 创建本任务专属 runner、合成 fixture、候选 SQL 快照和 evidence。
- 从 P3-041 反例复制或等价重建七个 P1 测试，并补齐 `expires_at_ms`、`valid_from_ms`、NULL 安全比较、复合更新、无操作更新和合法生命周期测试；不得修改 P3-041 原始 evidence。
- 复跑 P3-031 全量合同测试、P3-040 全量回归和 P3-042 专属回归。
- 输出交付物到 `lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`。
- 调用本地预检脚本检查交付物覆盖、模型路由记录和越界措辞。

本任务不授权：

- 不修改 P3-039、P3-040、P3-041 原始交付物、评审、PM Review 或 evidence。
- 不修复 audit_entry/outbox_job 的预置、UPDATE、DELETE，不改变 generation 独立升高规则；这些属于 R-0048。
- 不修复 terminal Authorization 子表 INSERT/UPDATE/DELETE；这些属于 R-0049。
- 不重写 Authorization 生命周期、核心领域模型、AI 权限模型或技术架构冻结合同。
- 不执行真实用户 DB migration或非空真实旧库 upgrade。
- 不访问真实 Vault、用户文件、真实导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049，不关闭或重新打开 R-0045。
- 不冻结 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不修改 PM 账本，不启动 P3-043 或其他后续任务，不进入下一阶段。

## 目标

本任务完成后，PM 应能判断：

- active Authorization 的父表安全包络字段是否无法被静默修改。
- `grantor_ref`、`processor`、`purpose`、`location`、`valid_from_ms`、`expires_mode`、`expires_at_ms`、`policy_version` 是否均采用 NULL 安全比较并被同一明确合同保护。
- 单字段、复合字段、配对有效期字段和多行 UPDATE 是否全部 fail closed，错误码是否稳定。
- active→active 的无操作更新与仅 `updated_at_ms` 更新是否仍合法；generation 独立升高不得被误写成安全白名单，它仍属于 R-0048 已知风险。
- proposed/granted 阶段的合法配置、active→revoked/expired/superseded 退休、新版本 supersede 与激活是否未被破坏。
- P3-031、P3-040 与 P3-042 三套回归是否达到 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown。
- P3-041 原始 evidence 是否保持不变，七个 P1 是否被定向重放并关闭，12 个 P2 是否仍被诚实保留为非范围。
- 是否足以进入 P3-043 隔离独立工程复评。

## 范围

### 1. 父表字段安全矩阵

- 列出 `authorization` 全部字段，并区分：本任务保护的安全包络字段、已有独立 trigger 保护的身份/状态字段、允许的非安全维护字段、R-0048/R-0049 非范围字段。
- 本任务至少保护：`grantor_ref`、`processor`、`purpose`、`location`、`valid_from_ms`、`expires_mode`、`expires_at_ms`、`policy_version`。
- 使用 SQLite NULL 安全语义（例如 `IS NOT`）比较 nullable 字段，不得因 NULL 比较漏过 `expires_at_ms`。
- 只允许明确且有测试的维护路径；不得用宽泛“除 status 外都可改”或“由应用层保证”替代 DB 约束。

### 2. Active 父表变异阻断

- 覆盖 P3-041 七个 P1 名称及等价攻击。
- 覆盖 `valid_from_ms`、`expires_at_ms`，包括 `at→indefinite`、`indefinite→at`、仅时间变更和配对字段复合变更。
- 覆盖单字段、同一语句多字段、多行 UPDATE、重复同值/no-op UPDATE。
- 统一、稳定地返回可断言错误，例如 `active_authorization_security_envelope_immutable`；不得只依赖 CHECK 或外键偶然失败。

### 3. 合法路径非回退

- proposed/granted 状态下在激活前配置安全包络仍合法。
- proposed→active、proposed→granted→active 仍合法。
- active→revoked/expired/superseded 的 generation+1、audit/outbox 合法路径仍通过。
- 旧版本 superseded 后创建并激活完整新版本仍通过；需要改变安全包络时必须通过新版本，而不是改写旧 active 版本。
- active 状态下 no-op 更新和仅 `updated_at_ms` 更新仍通过；不得在本任务中把 generation 独立升高宣布为合法安全维护。

### 4. 相邻字段处理

- 对 `id`、`created_at_ms`、`revoked_at_ms`、`updated_at_ms`、`status`、`generation`、`logical_key`、`version_no`、`supersedes_id` 给出明确归类和测试依据。
- 若发现其中任一字段形成新的 active 权限扩大、来源伪造或生命周期旁路，保留最小复现并回报 PM；只有与同一安全包络根因完全一致且不改变生命周期合同时，才允许纳入同一窄 trigger。
- 不得借此修改 R-0048 的 generation/evidence 合同或 R-0049 的 terminal 子表合同。

### 5. 回归与 Evidence

- P3-031 全量合同测试不得回退。
- P3-040 128 项回归或其当前完整集合不得回退。
- P3-041 七个 P1 必须在 P3-042 专属测试中逐项关闭；P3-041 原始反例 evidence 不得修改。
- P3-041 的 12 个 P2 可以继续复现，不得删除、降级或伪造成全绿；报告必须明确它们仍由 R-0048/R-0049 跟踪。
- 记录环境、准确命令、退出码、测试统计、修改前后 hash、原始 evidence 保留证明和候选 SQL 快照。

## 非范围

- R-0048：audit/outbox 预置、修改、删除以及 generation 独立升高。
- R-0049：terminal Authorization 子表历史语义不可变。
- 真实用户 DB、非空真实旧库、真实 Vault、真实文件、真实导出、真实 Tauri/IPC、云/第三方模型、向量、同步、多设备、L3、外部用户。
- 风险关闭、Schema/API 冻结、工程基线恢复、阶段切换。

## 输入材料

只读取“会话路由”中列出的文件和完成本任务所必需的直接工程依赖。不要读取完整 `PROJECT_CONTEXT.md`、全量 `DECISION_LOG.md`、无关 Review、Deliverable 或 Evidence。

执行规则：

- 先读取最新 `lifeos/CURRENT_STATUS.md` 和本任务卡。
- P3-041 独立评审、PM Review、反例脚本、结构化结果与 manifest 必须完整读取。
- P3-031 当前候选 SQL、合同测试、runner、manifest 和 P3-040 runner/manifest 必须完整读取。
- `RISK_LOG.md` 只定向读取 R-0044、R-0046、R-0047、R-0048、R-0049；`DECISION_LOG.md` 如需读取，只读 D-0216 至 D-0219。
- 不主动读取无关历史；上下文不足时先列出缺少文件和原因。
- 测试日志不粘贴到聊天或报告正文，完整内容写入 evidence。

## 角色检查点

主责角色必须重点回答：

- 安全包络不可变是否由真实 SQLite trigger/约束实现，而不是只改变测试期望。
- 八个必需字段、NULL 语义、复合/多行 UPDATE 和稳定错误码是否完整覆盖。
- 合法配置、退休和新版本路径是否不回退。
- 三套回归、hash、退出码和 evidence 是否可由 PM/P3-043 独立复跑。

协审角色必须重点检查：

- active 授权的处理器、用途、位置、授权来源、有效期和策略版本不能被静默扩大或改写。
- 用户可追溯的授权含义没有因 trigger 补丁而变得模糊。
- R-0048/R-0049 仍被诚实记录，未因本任务越界“顺手修复”或宣称已解决。
- 未触碰真实数据、真实 Vault、真实文件或真实 Tauri/IPC。

## 核心问题

- P3-041 的七个父表 P1 是否全部关闭？
- `valid_from_ms`、`expires_at_ms` 和 NULL/配对更新是否同样 fail closed？
- 是否存在复合、多行或 no-op 语义旁路？
- 合法激活、退休和新版本路径是否仍通过？
- P3-031、P3-040、P3-042 的统计、退出码和 hash 是什么？
- 是否存在任何新增 P0/P1、Not Implemented、Unknown 或证据冲突？
- R-0048/R-0049 是否被保持为明确非范围和开放风险？
- 是否建议进入 P3-043 隔离独立复评？

## 交付物

完整报告路径：

`lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`

Evidence manifest 路径：

`lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`

交付物必须包括：

- 任务信息、实际模型配置和授权边界
- 实际修改文件
- authorization 全字段安全矩阵
- 八个必需安全包络字段逐项整改映射
- P3-041 七个 P1 逐项重放结果
- NULL、复合、多行、no-op 与合法路径结果
- P3-031/P3-040/P3-042 测试统计、退出码、P0/P1/P2/Not Implemented/Unknown
- 修改前后稳定 hash、运行输出 hash 和 P3-041 原始 evidence 保留证明
- R-0048/R-0049 非范围与剩余风险
- 不可外推声明和是否建议 P3-043

Evidence manifest 至少包括：授权范围、环境、准确复跑命令、文件清单、输入/输出 hash、候选 SQL 快照、三套测试统计和退出码、八字段测试映射、P3-041 七个 P1 重放映射、原始 evidence 保留证明、R-0048/R-0049 非范围声明和不可外推声明。

## 验收标准

- 报告和 evidence manifest 已保存到指定路径。
- 八个必需安全包络字段均有真实 DB trigger/约束和可复核负测。
- P3-041 七个 P1 全部 fail closed；`valid_from_ms`/`expires_at_ms`、NULL、复合、多行更新无旁路。
- active no-op 与仅 `updated_at_ms` 更新、合法激活、退休和新版本路径未回退。
- P3-031、P3-040、P3-042 均为 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown；任何失败必须诚实保留并标记 Rework/Blocked。
- P3-041 原始 evidence 未修改，12 个 P2 仍清楚归入 R-0048/R-0049 非范围。
- 未触碰真实 DB/Vault/Tauri/IPC/真实文件或 PM 账本。
- 已完成本地预检并提供路径，或说明允许跳过原因。
- 聊天回复只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-039/P3-040/P3-041 原始交付物、评审、PM Review 或 evidence。
- 不修改 PM 账本。
- 不处理真实用户 DB、Vault、文件、敏感数据或 Tauri/IPC。
- 不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭任何风险，不冻结任何资产，不恢复工程基线，不进入下一阶段。
- 不自行启动 P3-043 或其他后续任务。
- 无法使用推荐模型或后备模型时不得静默换模；应停止并回报 PM。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天回复不要粘贴完整报告或测试日志，只输出任务状态、3-8 条摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
