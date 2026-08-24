# LIFEOS-P3-041｜Active Authorization 子表变异整改隔离独立工程复评

## 任务信息

- 任务 ID：LIFEOS-P3-041
- 任务名称：Active Authorization 子表变异整改隔离独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务 / 权限边界反例攻击 / Evidence 复核
- 建议篇幅：2000-4000 字；完整日志、反例结果和 hash 写入独立 evidence，评审正文只保留结论、问题、统计、证据路径和风险边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务必须独立复评 Codex 完成的 P3-040 高风险权限边界整改，重点是反例攻击、证据链核对和避免执行者自证；WorkBuddy 更适合作为隔离外部评审视角。
- 推荐模型：N/A
- 推荐推理强度：N/A
- 模型选择理由：外部 Agent，Codex 模型路由不适用
- 允许降级模型：N/A
- 禁止降级条件：N/A
- 必须升级条件：N/A
- 后备模型：N/A
- 是否需要后续独立评审：No；本任务本身就是强制隔离独立复评，但最终采纳、风险处理和下一步仍由 PM 决定
- 是否允许修改工程文件：No；仅允许只读原始工程与 evidence，可在临时副本复跑，并可在 `lifeos/reviews/LIFEOS-P3-041/` 下创建独立评审 evidence
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人 / QA 与 Evidence Reviewer
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、技术架构负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 隔离独立工程复评会话
- 推荐复用的会话：不复用 P3-040 Codex 执行会话；默认新建 WorkBuddy 独立复评会话
- 会话判断理由：这是 P0 优先级权限整改后的强制独立复评，必须与 P3-040 执行上下文隔离，避免自证循环、旧授权继承和证据污染。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `AGENTS.md`
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/AGENT_BRIEFING_PACK.md`
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-040_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/input/source_hashes.json`
  - `lifeos/engineering/LIFEOS-P3-040/evidence/input/p3_039_evidence_preservation.json`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-040/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_results.json`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046 相关行
- 可复用既有读取结果：无；新建独立会话应按任务卡重新建立证据理解
- 必须因变化或不确定性重读：P3-031 当前候选 SQL / runner / tests / MANIFEST，P3-040 全部直接 evidence，P3-039 原始反例 evidence，相关风险行
- 任务完成后是否建议保留会话：Yes，可作为后续同一候选 SQL 风险关闭前的独立复核会话；不得修改原始工程文件

## 背景

P3-039 独立评审在 P3-038 已知整改之外发现 11 个 active Authorization 子表 INSERT、UPDATE、`INSERT OR REPLACE` 和 `authorization_id` 改绑 P1。P3-040 随后在候选 SQL 中增加 scope、action、policy 的 active 父变异 trigger，并补充 forward-only 状态转换、retirement generation / audit / outbox fence、版本身份不可变和新版本 supersedes 约束。

P3-040 执行会话报告 P3-031 为 42 PASS，P3-040 内存 / 文件双模式为 128 PASS。PM 已在隔离临时副本复跑得到相同统计，并核对 manifest hash 与 P3-039 evidence 保留证明，因此接受任务为 `Accepted / Remediation Regression Passed`。用户已确认采纳，但这不等于风险关闭或资产冻结。

本任务必须站在执行者之外重新判断：已知 11 个 P1 是否真实关闭；新增状态 / 版本 / audit / outbox 约束是否引入新的绕过、历史证据篡改或合法流程阻塞；当前证据是否足以让 R-0044 / R-0046 进入风险关闭候选评估。不得只复述 P3-040 报告或复跑现有测试后直接 Pass。

## 目标

本任务完成后，PM 应能判断：

- P3-040 的候选 SQL、测试、runner、结果与 manifest 是否一致且可隔离复现。
- P3-039 的 11 个 P1 及其相邻变异路径是否全部 fail closed。
- OLD / NEW 双向改绑、REPLACE / UPSERT、复合语句和 trigger 顺序是否存在遗漏。
- 状态翻转、generation、audit / outbox 与版本链约束能否被预置、重放、单独更新或组合操作绕过。
- terminal Authorization 子表允许维护是否会破坏历史授权证据，即使终态不能复活。
- 合法 revoke / expire / supersede、终态清理和新版本激活是否未被错误阻塞。
- 是否存在 P0 / P1；如果没有，R-0044 / R-0046 是否可进入后续风险关闭条件评估。

## 范围

### 1. Evidence 与复跑一致性

- 核对 P3-040 manifest 中所有稳定输入、运行输出和 P3-039 保留 hash。
- 在隔离临时副本复跑 P3-031 与 P3-040；不得让复跑覆盖原始 evidence。
- 核对退出码、P0 / P1 / P2 / Not Implemented / Unknown 统计。
- 确认 29 个 P3-039 反例逐名迁入或被可证明更强的等价测试覆盖。

### 2. Active 子表变异反例攻击

- scope / action / policy 的 INSERT、UPDATE、DELETE、`INSERT OR REPLACE`、UPSERT / `ON CONFLICT DO UPDATE`。
- OLD 父 active、NEW 父 active、两端状态不同、同父更新与跨父改绑。
- 多行 UPDATE、复合事务、冲突替换、字段组合更新和当前 runner 未直接覆盖的列。
- SQLite trigger 触发顺序、递归 trigger 设置和 foreign key 开关差异是否改变安全结论。

### 3. 状态、generation 与证据 fence

- active → proposed / granted 非法回退。
- active → revoked / expired / superseded 后对子表变异并尝试直接或间接复活。
- generation 脱离状态转换单独增加、跨步增加、重复使用或与旧 evidence 组合。
- audit / outbox 记录预置、重放、重复、修改或删除后，retirement contract 是否仍能形成可信证据。
- 同一事务内不同写入顺序、事务回滚以及失败后残留记录是否可能绕过约束。

### 4. 版本链与历史完整性

- version 跳号、并列版本、错误 logical key、错误 supersedes、非前一版本 supersedes、并发候选 active 唯一性。
- terminal Authorization 的 scope / action / policy INSERT / UPDATE / DELETE 是否会改写历史授权语义；如允许清理，必须判断最小可接受边界和证据要求。
- 旧版本 superseded 与新版本激活之间的中间状态是否可能形成双 active、无 active 或越权消费窗口。

### 5. 合法路径非回退

- proposed → granted → active 与 proposed → active 的既有合法路径。
- active → revoked / expired / superseded 的合法路径。
- 允许的终态清理与完整新版本激活路径。
- P3-031 既有 42 项不得回退。

## 非范围

- 不修改 P3-031、P3-037、P3-038、P3-039、P3-040 原始工程文件、评审、交付物或 evidence。
- 不修复发现的问题；只记录可复现反例、严重级别、证据和建议。
- 不修改 PM 账本、风险状态或冻结状态。
- 不执行真实用户 DB migration、非空真实旧库 upgrade 或真实生产数据测试。
- 不访问真实 Vault、用户文件、真实导出路径或敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044、R-0046，不关闭或重新打开 R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动后续整改、风险关闭或下一阶段任务。

## 输入材料

只读取“会话路由”中列出的文件及完成反例复跑所必需的直接依赖。不要读取完整 `PROJECT_CONTEXT.md`、全量 `DECISION_LOG.md`、无关 Review、Deliverable 或 Evidence。

如需运行脚本：

- 必须在临时副本或评审专属目录运行，不能覆盖 P3-031 / P3-040 原始 evidence。
- 聊天中只报告 PASS / FAIL 数量、P0 数量、关键失败和 evidence 路径，不粘贴完整日志。
- 详细独立日志、反例脚本、结构化结果和 hash 写入 `lifeos/reviews/LIFEOS-P3-041/evidence/`。
- Evidence 包必须包含 `MANIFEST.md`。

## 角色检查点

主责角色必须重点回答：

- 是否独立复现两套回归与 hash，而非信任执行报告。
- 是否设计了超出现有正向测试的反例，并保留失败证据。
- 每个 P0 / P1 是否有具体 SQL、前置状态、预期 / 实际结果和复跑入口。
- 评审结论是否与风险状态、冻结边界和不可外推范围一致。

协审角色必须重点检查：

- 权限范围、动作、训练许可、外部发送、敏感等级和接收方不能被静默扩大。
- audit / outbox / generation / version 是否真的构成可信且不可静默改写的证据链。
- terminal 历史授权语义是否会被清理或维护路径改写。
- 合法生命周期没有被过度约束永久锁死。

## 核心问题

- P3-039 的 11 个 P1 是否全部独立确认关闭？
- 是否发现任何新的 P0 / P1？
- audit / outbox 预置、重放或删除是否构成旁路或证据链缺口？
- terminal 子表维护是否会破坏历史完整性？
- version / supersedes / generation 组合是否存在旁路？
- P3-031 与 P3-040 的复跑统计、退出码和 hash 是否与报告一致？
- R-0044 / R-0046 是否可以进入风险关闭候选评估，还是必须 Rework？

## 交付物

独立评审文件：

`lifeos/reviews/LIFEOS-P3-041_active_authorization_child_mutation_remediation_independent_engineering_re_review.md`

独立 evidence manifest：

`lifeos/reviews/LIFEOS-P3-041/evidence/MANIFEST.md`

评审文件必须包括：

- 最终结论：Pass / Pass with Conditions / Rework / Blocked
- 任务范围与独立性声明
- P3-031 / P3-040 隔离复跑统计和退出码
- Manifest 与 P3-039 evidence hash 核对
- 已知 11 个 P1 逐项独立判断
- 新增反例清单与结果
- P0 / P1 / P2 分类
- Gate 2 / Gate 3 / Gate 4 判断
- 风险状态建议，但不得直接修改风险
- 不可外推声明
- PM 必须确认的问题

## 判定标准

- **Pass**：两套回归、hash 和保留证明一致；已知 11 个 P1 与新增高风险反例全部 fail closed；没有 P0 / P1；合法路径未回退。
- **Pass with Conditions**：没有 P0 / P1，仅存在明确可后置且不削弱当前权限边界的 P2 条件。
- **Rework**：发现任何可复现 P0 / P1、证据 hash 冲突、现有测试不能复现、已知旁路未关闭、合法核心路径被阻塞，或历史证据可被静默改写并影响信任结论。
- **Blocked**：缺少必要文件、无法建立隔离证据、关键脚本不可运行，或无法在不污染原 evidence 的情况下完成判断。

如发现 P0，立即停止扩大测试范围，保留最小复现 evidence 并回报 PM。WorkBuddy 不得自行要求 Codex 直接修复。

## 验收标准

- 独立评审和 evidence manifest 已保存到指定路径。
- 原始工程、交付物、PM Review 和 evidence 未被修改。
- 两套回归在隔离副本复跑，或对无法复跑给出 Blocked 证据。
- 已核对全部关键 hash 与 P3-039 evidence 保留证明。
- 不仅复跑现有测试，还完成任务卡指定的相邻反例攻击。
- 每个发现有严重级别、证据路径、复跑入口和影响判断。
- 未发现 P0 / P1 时才能建议 Pass / Pass with Conditions。
- 已调用本地预检检查评审覆盖与越界措辞；若本地模型不可用，记录允许跳过原因。
- 聊天回复只输出摘要、评审路径、evidence 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 严格只读原始 P3-031 / P3-039 / P3-040 资产。
- 不修改候选 SQL、测试、runner 或原始 evidence。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 不关闭风险、不冻结资产、不恢复工程基线、不进入下一阶段。
- 不处理真实数据、真实 Vault、真实文件或真实 Tauri / IPC。
- 不自行启动任何后续任务。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天回复不要粘贴完整评审或测试日志，只输出任务状态、3-8 条摘要、评审路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
