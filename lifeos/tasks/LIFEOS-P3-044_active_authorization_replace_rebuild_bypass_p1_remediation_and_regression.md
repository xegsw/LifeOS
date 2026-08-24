# LIFEOS-P3-044｜Active Authorization 替换／重建旁路 P1 整改与回归

## 任务信息

- 任务 ID：LIFEOS-P3-044
- 任务名称：Active Authorization 替换／重建旁路 P1 整改与回归
- 优先级：P0
- 任务类型：工程整改任务 / 候选 SQL 安全补丁 / 权限边界回归 / Evidence 生成
- 建议篇幅：1500-3000 字；完整日志、结构化测试结果、环境与 hash 写入 evidence，报告只保留整改映射、测试摘要、证据路径、剩余风险和不可外推边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要修改候选 SQLite Schema、合同测试和回归 runner，封堵 `INSERT OR REPLACE`、直接 DELETE 后重建等 active Authorization 父记录旁路，并维护可复核 evidence；Codex 更适合高风险 SQL trigger 整改、反例迁移和自动回归。
- 推荐模型：`gpt-5.6-sol`
- 推荐推理强度：`xhigh`
- 模型选择理由：这是权限边界 P1 的 P0 优先级整改；错误可能允许已有 active 授权的处理器、策略版本等安全字段被静默替换并无审计重新激活，且需要同时覆盖 SQLite conflict resolution、FK/recursive trigger 组合、合法生命周期和多套历史回归，质量优先于 Token 成本。
- 允许降级模型：`None`
- 禁止降级条件：本任务整体涉及权限、证据链和后续风险关闭输入，不得使用 `gpt-5.6-luna`、`gpt-5.4` 或其他较低配置；不得因补丁行数少、trigger 写法看似机械或已有反例而降低配置。
- 必须升级条件：发现新增 P0、直接 active 消费门绕过、数据不可恢复、真实能力触达、候选 SQL与 evidence/hash 冲突、合法退休/新版本路径回退、必须改变 Authorization 生命周期或 AI 权限边界、或无法在 FK/recursive trigger 组合下稳定重现和关闭 P3-043 P1 时，立即停止扩大范围并回到 PM。
- 后备模型：`gpt-5.5`
- 后备模型执行要求：仅在首选模型不可用时使用 `gpt-5.5` + `xhigh`，并在交付物中记录触发原因、实际配置和是否影响验收范围
- 是否需要后续独立评审：Yes；整改通过后必须由未参与本任务执行的新建隔离独立评审会话执行 P3-045
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
- 推荐复用的会话：优先复用完成 P3-042 的 Codex 工程整改会话；不得使用 P3-043 WorkBuddy 独立评审会话执行整改。若 P3-042 会话仍有活动任务、已发生上下文压缩且无法恢复可靠边界、工作区状态不明或上下文已经混淆，则改为新建 Codex 工程整改会话。
- 会话判断理由：P3-044 与 P3-042 修改同一 P3-031 候选 SQL、合同测试和受控 SQLite 回归，属于同一工程线的后续窄整改；复用可以保留工程上下文，但新任务的范围和授权必须重新建立。
- 是否需要独立性隔离：执行阶段 No；P3-045 复评阶段 Yes，且不得由本执行会话独立评审自己的整改
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅复用短报告字段，不代表本任务进入快车道）
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-043_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-043/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-043/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-043/evidence/counter_example_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-043/evidence/counter_example_results.json`
  - `lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-042/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0044、R-0046、R-0047、R-0048、R-0049、R-0050 相关行
- 可复用既有读取结果：若同一 Codex 工程会话已完整读取、之后未修改、未截断、未发生上下文压缩且能可靠确认读取状态，可复用 `lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解
- 必须因变化或不确定性重读：最新 `CURRENT_STATUS.md`、本任务卡、P3-043 独立评审/PM Review/反例 evidence、P3-031 当前候选 SQL/tests/runner/manifest、P3-042 与 P3-040 当前 runner/manifest、相关风险行；若发生上下文压缩或读取状态不可靠，还必须重读根 `AGENTS.md` 和相关基础规则
- 任务完成后是否建议保留会话：Yes，作为候选 SQL 权限边界整改线保留；不得用于 P3-045 独立复评

## 背景

P3-042 已通过 UPDATE trigger 关闭 active Authorization 八个父表安全包络字段的直接 UPDATE 旁路。P3-043 隔离独立复评随后构造 46 个反例，得到 34 PASS、12 BYPASS，其中 1 个为 P1：在 FK ON、当前 trigger 生效时，`INSERT OR REPLACE` 可将既有 active Authorization 替换为 `granted`，改写 `processor`、`policy_version` 等安全字段，同时保留既有 scope/action/policy，之后可在无 audit/outbox 的情况下重新激活。PM 已独立复现该行为，并依据任务卡将 P3-043 结论校正为 Rework。

用户已确认采纳 Rework 并授权启动本任务。P3-044 只封堵 active Authorization 父记录的替换／重建写旁路；R-0048 的 evidence/generation/时间元数据问题和 R-0049 的 terminal 历史语义问题继续保持 P2 非范围。本任务通过不等于风险关闭、Schema/API 冻结、工程基线恢复、真实能力准入或阶段切换。

## 授权边界

本任务明确授权：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限增加 active Authorization 父记录替换、冲突写入和直接删除/重建的 fail-closed 约束及必要注释。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限新增本任务负测、合法路径测试和必要夹具调整。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限保持单一复跑入口、统计和非零退出合同。
- 更新 P3-031 evidence manifest、结构化结果和日志，记录当前候选 SQL/tests/runner 的稳定 hash 与回归统计。
- 在 `lifeos/engineering/LIFEOS-P3-044/` 创建本任务专属候选 SQL 快照、runner、合成 fixture、测试结果和 evidence。
- 复制或等价迁移 P3-043 的 P1 反例到 P3-044 测试包；原 P3-043 review/evidence 必须只读。
- 使用当前 P3-031 候选 SQL 运行 P3-040、P3-042 的直接相关回归逻辑；不得只复跑它们各自目录中的旧 SQL 快照后宣称当前候选未回退。
- 输出报告到 `lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`。
- 调用本地预检脚本检查交付物覆盖、模型路由记录、风险措辞和不可外推声明。

本任务不授权：

- 不修改 P3-039、P3-040、P3-041、P3-042、P3-043 的原始交付物、评审、PM Review 或 evidence。
- 不通过修改或删除 P3-043 反例、降低严重级别、关闭 foreign_keys 或只依赖 `recursive_triggers=ON` 来制造通过。
- 不修复 R-0048 的 audit/outbox 预置、UPDATE、DELETE、generation 独立升高、`created_at_ms`/`revoked_at_ms` 可变问题。
- 不修复 R-0049 的 terminal Authorization 父表/子表历史语义可变问题。
- 不关闭 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049、R-0050；不关闭或重新打开 R-0045。
- 不重写 Authorization 生命周期、核心领域模型、AI 权限模型或技术架构冻结合同。
- 不执行真实用户 DB migration、非空真实旧库 upgrade，不连接真实 DB/Vault/文件/导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri/IPC，不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema/API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线，不进入下一阶段。
- 不修改 PM 账本，不自行创建或启动 P3-045 或其他后续任务。

## 目标

本任务完成后，PM 应能判断：

- 已有 active Authorization 是否无法被 `INSERT OR REPLACE`、`REPLACE INTO`、冲突 INSERT/UPSERT、直接 DELETE 后 INSERT 或父记录重建改写/降级后重新激活。
- 防护是否同时覆盖主键 `id` 冲突、`UNIQUE(logical_key, version_no)` 冲突及其组合，而不只覆盖 P3-043 的单一 SQL 文本。
- 防护是否不依赖 SQLite REPLACE 的隐式 DELETE trigger、`recursive_triggers=ON` 或 FK cascade 偶然行为。
- FK ON/OFF、recursive_triggers ON/OFF、内存/文件库和事务 commit/rollback 组合是否均 fail closed，失败后原 active 父表、三类子表、generation 和 evidence 状态是否原子保持。
- 合法的新 proposed/granted 授权、激活前配置、active 退休、创建完整 successor version 并激活是否未被过度阻断。
- P3-043 的 P1 是否被定向关闭，同时其 10 个 P2 与 1 个 P3 观察仍被诚实保留为非范围。
- P3-031 全量合同测试及 P3-040/P3-042 直接相关回归是否对当前候选 SQL 达到 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown。
- 是否足以进入 P3-045 隔离独立工程复评。

## 范围

### 1. 冲突键与写语义矩阵

- 至少覆盖相同 `id`、相同 `(logical_key, version_no)` 但不同 id、两者同时冲突，以及无冲突的新记录。
- 覆盖 `INSERT OR REPLACE`、`REPLACE INTO`、`INSERT ... ON CONFLICT DO UPDATE`、普通重复 INSERT、直接 DELETE+INSERT、同事务多语句重建。
- 覆盖把 active 替换为 proposed/granted/active/terminal 的尝试，以及改写 `processor`、`policy_version` 和至少一个 nullable/配对安全字段的组合。
- 使用稳定、可断言的错误码区分父记录替换与 active 直接删除；不得只依赖 UNIQUE、FK 或 CHECK 偶然失败。

### 2. Fail-closed trigger 合同

- 对 INSERT/REPLACE 必须在冲突解析删除旧 active 行之前检查并拒绝，不得只依赖 `BEFORE DELETE` 或 recursive delete trigger。
- 对直接 DELETE active 父记录必须拒绝，防止 DELETE+INSERT 重建旁路；终态记录的历史不可变和受控清理仍归 R-0049，不在本任务扩大处理。
- 对 UPDATE/UPSERT 仍必须保留 P3-042 八字段和状态机保护，不得用新的宽泛 trigger 替代后造成合法/非法路径模糊。
- 失败必须回滚整条语句/事务，不得留下父记录丢失、子表孤儿、部分更新、generation 变化或伪 evidence。

### 3. PRAGMA、后端与事务组合

- 内存库与受控文件库均测试 `foreign_keys=ON/OFF` 和 `recursive_triggers=ON/OFF`。
- 明确区分每个组合的预期行为、实际结果、退出码和 integrity/FK 检查；不得只测试默认连接。
- 覆盖 autocommit、显式事务 commit、失败后 rollback、同事务先退休再新建 successor 的合法路径。
- 如某组合无法由当前运行时控制，标记 Not Implemented/Blocked，不得写成通过。

### 4. 合法路径非回退

- 新的 proposed/granted Authorization 使用唯一 id 与版本身份创建，配置 scope/action/policy 后激活仍通过。
- active→revoked/expired/superseded 的 generation+1、audit/outbox 合法退休仍通过。
- 旧版本 superseded 后，以新 id、`version_no+1`、正确 `supersedes_id` 和不同安全包络创建完整 successor 并激活仍通过。
- active no-op、只改 `updated_at_ms` 及 P3-042 八字段直接 UPDATE 阻断仍维持既有合同。
- 不把 terminal REPLACE、历史父/子变异或 evidence append-only 问题误写成已解决。

### 5. 回归与 Evidence

- P3-031 当前全量合同测试不得回退。
- P3-040 active 子表 128 项或其当前完整等价集合必须针对当前候选 SQL 验证。
- P3-042 八字段、NULL/配对、复合/多行、合法生命周期测试必须针对当前候选 SQL 验证。
- P3-043 的父 REPLACE P1 必须在 P3-044 专属测试中稳定 fail closed；原 P3-043 evidence 不得修改。
- 记录环境、SQLite/Python 版本、准确命令、退出码、测试统计、候选 SQL与测试 hash、原始 evidence 保留证明、内存/文件库与 PRAGMA 矩阵。

## 非范围

- R-0048：audit/outbox 预置、修改、删除，generation 独立升高，active `created_at_ms`/`revoked_at_ms` 可变。
- R-0049：terminal Authorization 父表/子表历史语义不可变和受控清理设计。
- R-0043/R-0046 风险关闭、R-0050 风险关闭决策。
- 真实用户 DB、非空真实旧库、真实 Vault、真实文件/导出、真实 Tauri/IPC、云/第三方模型、向量、同步、多设备、L3、外部用户。
- Schema/API/SQL migration/工程基线冻结或恢复、阶段切换。

## 输入与执行规则

- 先读取最新 `lifeos/CURRENT_STATUS.md` 和本任务卡，再读取“会话路由”列出的直接输入。
- P3-043 独立评审、PM Review、manifest、反例脚本和结构化结果必须完整读取；原文件严格只读。
- P3-031 当前候选 SQL/tests/runner/manifest、P3-040 与 P3-042 当前 runner/manifest 必须完整读取。
- `RISK_LOG.md` 只定向读取 R-0044、R-0046、R-0047、R-0048、R-0049、R-0050；`DECISION_LOG.md` 如需读取，只读 D-0218 至 D-0223。
- 不主动读取完整 `PROJECT_CONTEXT.md`、全量 `DECISION_LOG.md` 或无关 Review/Deliverable/Evidence；上下文不足时先列出缺少文件和原因。
- 旧 runner 若固定加载旧 SQL 快照，只能作为历史复现；本任务必须另建 P3-044 runner 把相关测试逻辑施加到当前 P3-031 候选 SQL。
- 测试日志不粘贴到聊天或报告正文，完整内容写入 evidence。

## 角色检查点

主责角色必须重点回答：

- 防护是否由真实 SQLite trigger/constraint 实现，而不是只修改测试期望或攻击脚本。
- 是否覆盖两个唯一身份维度、REPLACE/UPSERT/DELETE+INSERT 和 PRAGMA 组合，并且不依赖隐式 DELETE trigger。
- 失败是否原子保持父/子/evidence 状态，合法退休与 successor version 是否不回退。
- 当前候选 SQL、多套回归、hash、退出码和 evidence 是否可由 PM/P3-045 独立复跑。

协审角色必须重点检查：

- active 授权的处理器、用途、位置、授权来源、有效期和策略版本不能通过替换/重建被静默扩大。
- 用户可追溯的授权语义、generation 和 audit/outbox 没有因失败写入形成半状态。
- R-0048/R-0049 仍被诚实记录，未被越界修复或宣称关闭。
- 未触碰真实数据、真实 Vault/文件、真实 Tauri/IPC 或 PM 账本。

## 核心问题

- P3-043 的 `INSERT OR REPLACE(granted)` P1 是否稳定关闭？
- 主键冲突、版本唯一键冲突、不同状态、不同 PRAGMA 和直接 DELETE+INSERT 是否存在等价旁路？
- 防护是否不依赖 recursive delete trigger 或 FK 偶然行为？
- 失败后父表、三类子表、generation、audit/outbox 是否保持原子一致？
- 合法激活、退休和 successor version 路径是否仍通过？
- P3-031、P3-040、P3-042、P3-044 的当前候选回归统计、退出码和 hash 是什么？
- 是否存在任何新增 P0/P1、Not Implemented、Unknown 或证据冲突？
- 是否建议进入 P3-045 隔离独立复评？

## 交付物

完整报告路径：

`lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`

Evidence manifest 路径：

`lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`

交付物必须包括：

- 任务信息、实际模型配置和授权边界
- 实际修改文件与 trigger/constraint 设计说明
- 冲突键、SQL 写法、状态、PRAGMA、后端和事务测试矩阵
- P3-043 P1 迁移与关闭证据，P2/P3 非范围保留说明
- 合法路径与失败原子性结果
- P3-031/P3-040/P3-042/P3-044 当前候选测试统计、退出码、P0/P1/P2/Not Implemented/Unknown
- 输入/输出 hash、当前候选 SQL 快照和 P3-043 原始 evidence 保留证明
- R-0048/R-0049 非范围、剩余风险、不可外推声明和是否建议 P3-045

Evidence manifest 至少包括：授权范围、环境、准确复跑命令、文件清单、输入/输出 hash、当前候选 SQL 快照、四组测试统计和退出码、冲突键/SQL/PRAGMA/后端矩阵、失败原子性检查、P3-043 P1 重放映射、原始 evidence 保留证明、R-0048/R-0049 非范围声明和不可外推声明。

## 验收标准

- 报告和 evidence manifest 已保存到指定路径。
- P3-043 父 REPLACE P1 及同根因的主键/版本键/DELETE+INSERT 旁路均有真实 DB 约束和可复核负测。
- 防护在内存/文件、FK ON/OFF、recursive triggers ON/OFF 下不依赖隐式 DELETE trigger，失败状态原子一致。
- active 直接 UPDATE/子表变异保护、合法激活、退休和 successor version 路径未回退。
- P3-031、P3-040、P3-042、P3-044 对当前候选 SQL均为 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown；任何失败必须诚实保留并标记 Rework/Blocked。
- P3-043 原始 review/evidence 未修改；10 个 P2 和 1 个 P3 观察未被删除、降级或伪造成已关闭。
- 未触碰真实 DB/Vault/文件/Tauri/IPC 或 PM 账本。
- 已完成本地预检并提供路径，或说明允许跳过原因。
- 聊天回复只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-039/P3-040/P3-041/P3-042/P3-043 原始交付物、评审、PM Review 或 evidence。
- 不修改 PM 账本。
- 不处理真实用户 DB、Vault、文件、敏感数据或 Tauri/IPC。
- 不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭任何风险，不冻结任何资产，不恢复工程基线，不进入下一阶段。
- 不自行创建或启动 P3-045 或其他后续任务。
- 无法使用推荐模型或后备模型时不得静默换模；应停止并回报 PM。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天回复不要粘贴完整报告或测试日志，只输出任务状态、3-8 条摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
