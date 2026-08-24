# LIFEOS-P3-043｜Active Authorization 父表安全包络整改隔离独立工程复评

## 任务信息

- 任务 ID：LIFEOS-P3-043
- 任务名称：Active Authorization 父表安全包络整改隔离独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务 / 权限边界反例攻击 / Evidence 复核
- 建议篇幅：2000-4000 字；完整日志、反例脚本、结构化结果和 hash 写入独立 evidence，评审正文只保留结论、关键发现、统计、证据路径和风险边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务必须独立复评 Codex 完成的 P3-042 P0 权限边界整改，并主动攻击既有测试未覆盖的 SQL 写法、trigger 顺序和证据组合；WorkBuddy 在 P3-039/P3-041 已证明适合隔离反例攻击，但最终严重级别和风险归属仍由 PM 裁定。
- 推荐模型：N/A
- 推荐推理强度：N/A
- 模型选择理由：外部 Agent，Codex 模型路由不适用
- 允许降级模型：N/A
- 禁止降级条件：N/A
- 必须升级条件：N/A
- 后备模型：N/A
- 是否需要后续独立评审：No；本任务本身是强制隔离独立复评，最终采纳、风险状态和后续任务仍由 PM/用户决定
- 是否允许修改工程文件：No；原始工程、交付物和 evidence 严格只读，只允许在临时副本复跑，并在 `lifeos/reviews/LIFEOS-P3-043/` 创建独立评审 evidence
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人 / QA 与 Evidence Reviewer
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、技术架构负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 隔离独立工程复评会话
- 推荐复用的会话：不复用 P3-042 Codex 执行会话，也不复用 P3-041 WorkBuddy 复评会话；默认新建 WorkBuddy 隔离会话
- 会话判断理由：P0 修复后的独立复评按项目规则默认必须新建会话，避免执行者自证、既有攻击结论锚定和旧任务授权/证据污染。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/AGENT_BRIEFING_PACK.md`
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-042_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-042/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-042/evidence/input/source_hashes.json`
  - `lifeos/engineering/LIFEOS-P3-042/evidence/input/p3_041_evidence_preservation.json`
  - `lifeos/engineering/LIFEOS-P3-042/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-042/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
  - `lifeos/reviews/LIFEOS-P3-041/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/counter_example_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-041/evidence/counter_example_results.json`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049 相关行
- 可复用既有读取结果：无；新建隔离会话必须重新建立当前候选 SQL、整改 evidence、历史反例和风险边界理解
- 必须因变化或不确定性重读：P3-031 当前 SQL/tests/runner/manifest、P3-042 全部直接 evidence、P3-041 原始反例 evidence、相关风险行
- 任务完成后是否建议保留会话：Yes，可作为后续候选 SQL 风险关闭前的独立复核会话；不得修改原始工程或自行启动后续任务

## 背景

P3-041 独立复评确认 P3-040 已关闭 active Authorization 子表 11 个 P1，但发现 active 父 Authorization 的 `processor`、`purpose`、`location`、`grantor_ref`、`expires_mode`、`policy_version` 和复合字段仍可静默改写。P3-042 随后增加八字段 NULL 安全不可变 trigger，并补齐 `valid_from_ms`、`expires_at_ms`、复合/多行/no-op 和合法生命周期测试。

P3-042 执行报告和 PM 隔离复跑均得到：P3-031 44/44、P3-040 128/128、P3-042 52 PASS + 26 个 P2 Known Limitation，三套退出码为 0，P3-041 原始 evidence 哈希保持不变。PM 接受整改任务，但资产仍未冻结，R-0044/R-0047 只进入 Remediation Candidate。

P3-042 同时记录 active `created_at_ms`/`revoked_at_ms` 可改写，PM 暂按 R-0048 的 P2 证据/生命周期元数据完整性问题处理。本任务必须独立判断：八字段 P1 是否真实关闭；是否能通过 REPLACE/UPSERT、状态组合、trigger 配置或同事务顺序绕过；相邻元数据与预置 evidence/generation 组合后是否会升级为 P0/P1。不得只复跑现有脚本后直接通过。

## 目标

本任务完成后，PM 应能判断：

- P3-042 报告、候选 SQL、测试、runner、结果、hash 和 manifest 是否一致且可隔离复现。
- P3-041 七个父表 P1 与 P3-042 八字段矩阵是否真实 fail closed。
- `expires_at_ms` NULL、配对有效期、复合/多行 UPDATE、active→terminal 同语句是否存在遗漏。
- UPSERT、`INSERT OR REPLACE`、DELETE+INSERT、状态翻转、连接 PRAGMA 和 trigger 顺序能否绕过父表不可变与既有 active INSERT/状态机约束。
- `created_at_ms`/`revoked_at_ms` 与 generation、预置/可变 audit/outbox、退休状态组合后是否仍只是 P2，或应升级为 P0/P1。
- 合法激活、退休、新版本、安全包络变化、no-op 和 `updated_at_ms` 维护是否未被错误阻塞。
- R-0044/R-0047 是否可进入后续风险关闭条件评估，还是必须再次 Rework。

## 范围

### 1. Evidence 与隔离复跑

- 核对 P3-042 manifest 中稳定输入、候选快照、运行输出、P3-041 preservation 和三套回归 hash。
- 在隔离临时副本复跑 P3-031、P3-040 和 P3-042；不得覆盖任何原始 evidence。
- 核对退出码、P0/P1/P2、Known Limitation、Not Implemented、Unknown 和文件库 integrity/FK 统计。
- 确认 P3-041 五个原始 evidence 文件及 P3-042 原始 evidence 在评审前后均未修改。

### 2. 八字段与 SQL 写法反例攻击

- 逐项攻击 `grantor_ref`、`processor`、`purpose`、`location`、`valid_from_ms`、`expires_mode`、`expires_at_ms`、`policy_version`。
- 覆盖 NULL↔值、at↔indefinite 配对、单字段、复合字段、多行 UPDATE、no-op、只改 `updated_at_ms`。
- 覆盖 `UPDATE ... FROM`（若当前 SQLite 支持）、子查询赋值、CASE、同值类型变化、UPSERT/`ON CONFLICT DO UPDATE`、`INSERT OR REPLACE`、DELETE+INSERT 和父记录重建。
- 覆盖 active→revoked/expired/superseded 同语句同时修改包络、generation 和时间元数据。
- 若某攻击只在明确违反候选连接合同（例如关闭 foreign_keys）后成立，必须记录前置条件并判断是配置 P2、启动 fail-open 还是实际 P1；不得无条件上调或降级。

### 3. Trigger 与连接状态

- 检查 `BEFORE UPDATE OF` 的列匹配、trigger 触发顺序、事务回滚、递归 trigger 开关与 foreign_keys ON/OFF 差异。
- 检查直接 active INSERT、REPLACE 为 proposed 后再激活、父 id/版本身份变更和子表保留组合。
- 不把“攻击者直接 DROP TRIGGER/修改 Schema”当作本候选运行时旁路；如认为 DDL 威胁属于当前模型，必须单独说明依据并交 PM 判断。

### 4. R-0048 相邻组合攻击

- active 时预写/改写 `revoked_at_ms`，再进行合法/伪造 retirement。
- active 时改写 `created_at_ms`，检查是否影响版本、审计、导出解释或后续消费判断。
- 与 generation 独立升高、预置 audit/outbox、audit/outbox UPDATE/DELETE、同事务顺序组合。
- 明确区分：只破坏历史解释的 P2、能改变 active 权限或绕过退休/消费门的 P1、会造成不可恢复数据/权限失控的 P0。
- 本任务只评审和分级，不修复 R-0048/R-0049。

### 5. 合法路径非回退

- proposed/granted 激活前配置并激活。
- active→revoked/expired/superseded 的 generation+1 + audit/outbox。
- 旧版本 superseded 后以不同安全包络创建并激活完整新版本。
- active no-op、只改 `updated_at_ms` 和既有合法查询/合同测试。

## 非范围

- 不修改 P3-031、P3-039、P3-040、P3-041、P3-042 原始工程、评审、交付物或 evidence。
- 不修复发现的问题；只保留最小反例、证据、严重级别和建议。
- 不修改 PM 账本、风险或冻结状态。
- 不执行真实用户 DB migration、非空真实旧库 upgrade 或真实生产数据测试。
- 不访问真实 Vault、用户文件、真实导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri/IPC。
- 不启用云/第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭风险、不冻结 Schema/API/SQL migration/工程基线、不进入下一阶段。

## 输入与执行规则

- 只读取“会话路由”列出的文件及反例复跑所必需的直接依赖；不要读取完整 `PROJECT_CONTEXT.md`、全量 `DECISION_LOG.md` 或无关历史。
- 原始工程和 evidence 必须只读；所有执行在临时副本或 `lifeos/reviews/LIFEOS-P3-043/evidence/` 的独立资产上完成。
- 详细日志、反例脚本、结构化结果、环境、命令、退出码与 hash 写入独立 evidence；聊天只报告摘要。
- Evidence 包必须包含 `MANIFEST.md`，并能让 PM 复跑每个 P0/P1 反例。
- 若上下文或文件不足，先列缺失项并返回 Blocked，不自行全量翻历史或修改原资产。

## 角色检查点

主责角色必须重点回答：

- 是否独立复现三套回归和所有关键 hash，而不是信任执行报告。
- 是否构造超出现有 runner 的 SQL 写法、trigger/PRAGMA、事务顺序和父记录重建反例。
- 每个 P0/P1 是否有最小 SQL、前置状态、预期/实际结果、环境和复跑入口。
- 是否把双后端实例数、逻辑问题数、历史证据数和当前可复现数区分清楚。

协审角色必须重点检查：

- 处理器、用途、位置、授权来源、有效期和策略版本不能被静默改写。
- `created_at_ms`/`revoked_at_ms` 与 evidence/generation 组合不会被过早降为无害 P2。
- 合法生命周期和用户可追溯授权语义没有被 trigger 过度锁死。
- 不修改原始 evidence、不启用真实能力、不自行关闭风险。

## 核心问题

- P3-042 三套回归和 hash 是否独立一致？
- P3-041 七个 P1及八字段扩展是否全部关闭？
- REPLACE/UPSERT/DELETE+INSERT/状态组合/PRAGMA 是否存在 P0/P1 绕过？
- `created_at_ms`/`revoked_at_ms` 与 R-0048 组合后应维持 P2 还是升级？
- 是否出现合法生命周期回退或过度阻断？
- R-0044/R-0047 可否进入后续风险关闭条件评估？
- 结论应为 Pass、Pass with Conditions、Rework 还是 Blocked？

## 交付物

独立评审文件：

`lifeos/reviews/LIFEOS-P3-043/independent_review.md`

独立 evidence manifest：

`lifeos/reviews/LIFEOS-P3-043/evidence/MANIFEST.md`

评审文件必须包括：

- 最终结论与独立性声明
- P3-031/P3-040/P3-042 隔离复跑统计和退出码
- Manifest、稳定输入和原 evidence hash 核对
- 八字段与 P3-041 七个 P1逐项判断
- 新增 SQL/trigger/PRAGMA/事务/父记录重建反例清单
- R-0048 相邻组合攻击与严重级别判断
- P0/P1/P2、Known Limitation、Not Implemented、Unknown 分类
- Gate 2/Gate 3/Gate 4 判断
- 风险状态建议、不可外推声明和 PM 必须确认的问题

## 判定标准

- **Pass**：三套回归、hash 和保留证明一致；八字段与全部新增高风险反例 fail closed；没有 P0/P1，且没有新的待处置 P2。
- **Pass with Conditions**：没有 P0/P1；只存在明确、可复现、未被误降级且不削弱当前 active 权限边界的 P2/Known Limitation，并给出冻结前条件。
- **Rework**：发现任何可复现 P0/P1、证据/hash 冲突、原 evidence 被修改、既有测试不可复现、八字段旁路未关闭、父记录重建可绕过安全包络，或合法核心生命周期被阻塞。
- **Blocked**：缺少必要文件、无法建立隔离证据、关键脚本不可运行，或无法在不污染原 evidence 的情况下完成判断。

如发现 P0，立即停止扩大测试范围，保留最小复现 evidence 并回报 PM。WorkBuddy 不得自行要求 Codex 直接修复。

## 验收标准

- 独立评审和 evidence manifest 已保存到指定路径。
- 原始工程、交付物、PM Review 和 evidence 未修改。
- 三套回归在隔离副本复跑，或对无法复跑给出 Blocked 证据。
- 不仅复跑现有测试，还完成任务卡指定的相邻反例攻击。
- 每个发现有严重级别、逻辑问题数、双后端实例数、证据路径和复跑入口。
- 未发现 P0/P1 时才能建议 Pass/Pass with Conditions。
- 已调用本地预检；若不可用，记录允许跳过原因。
- 聊天回复只输出摘要、评审路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 严格只读 P3-031/P3-039/P3-040/P3-041/P3-042 原始资产。
- 不修改候选 SQL、测试、runner、交付物或原 evidence。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 不关闭风险、不冻结资产、不恢复工程基线、不进入下一阶段。
- 不处理真实数据、真实 Vault、真实文件或真实 Tauri/IPC。
- 不自行启动任何后续任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天回复不要粘贴完整评审或测试日志，只输出任务状态、3-8 条摘要、评审路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
