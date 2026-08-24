# LIFEOS-P3-039｜候选 SQL 残留 P1 整改隔离独立工程复评

## 任务信息

- 任务 ID：LIFEOS-P3-039
- 任务名称：候选 SQL 残留 P1 整改隔离独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务 / P0 整改复评 / 反例攻击 / Evidence 复核
- 建议篇幅：2000-4000 字；完整复跑日志与结构化反例结果写入评审 evidence，不粘贴到聊天
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务需要与 P3-038 Codex 执行上下文隔离，独立攻击 Tombstone 删除后复活与 Authorization 权限子表完整性边界，并复核两套 SQLite 回归和 evidence；WorkBuddy 更适合作为独立评审、反例攻击和证据链挑错者。
- 是否需要后续独立评审：No，本任务自身即独立复评；如发现 P0 / P1，必须回到 PM 主会话决定 Rework 与后续整改任务。
- 是否允许修改工程文件：No；只允许在系统临时目录或 `lifeos/reviews/LIFEOS-P3-039/evidence/` 创建评审副本、日志与证据
- 是否允许修改项目账本：No
- 主责角色：独立工程评审负责人、QA / Evidence Reviewer
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：WorkBuddy 独立评审
- 推荐复用的会话：可复用此前专门承担 P3 SQL migration / SQLite 合同测试独立评审的 WorkBuddy 会话，但必须确认该会话未参与 P3-038 工程整改、上一任务已结束、没有未完成修改、上下文未混淆，并能重新读取本任务卡；否则新建 WorkBuddy 独立评审会话。
- 会话判断理由：P3-038 属于 P0 安全整改，执行 Agent 不得独立评审自己的候选 SQL、测试和风险关闭前置证据；本任务必须隔离以避免自证循环和已知测试过拟合。
- 是否需要独立性隔离：Yes
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
  - `lifeos/reviews/LIFEOS-P3-038_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_2_tombstone_delete_insert.json`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_3_tombstone_status_insert.json`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_4_authorization_child_delete.json`
  - `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.py`
  - `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
  - `lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`
  - `lifeos/reviews/LIFEOS-P3-037_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046 相关行
- 可复用既有读取结果：
  - 若同一 WorkBuddy 独立评审会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-038 交付物、PM Review、候选 SQL、测试、runner、evidence manifest 与三项整改 JSON
  - P3-037 失败报告、PM Review 与 failure evidence manifest
  - R-0043 / R-0046 风险行，以及 R-0044 / R-0045 既有 Closed 边界
- 任务完成后是否建议保留会话：Yes，作为 P3 SQL migration / SQLite 权限与删除边界独立评审会话保留；不得转为工程整改会话修改被评审目录。

## 背景

P3-037 在受控文件型 SQLite 中发现三项 P1：Tombstone 可被 DELETE / REPLACE / DELETE+INSERT 删除或降代、Tombstone 可伪造非 `accepted` 初始状态、active Authorization 的 scope/action/policy 子表可直接 DELETE 且父授权 generation 与 audit 不变。该结果导致 R-0043 重新打开并新增 R-0046。

P3-038 已按任务卡增加 Tombstone 初始 INSERT / DELETE 保护和 active Authorization 三类子表 DELETE 保护，并扩展 P3-031 合同测试与 P3-038 文件型回归。PM 在隔离临时副本复跑：P3-031 为 38 PASS / 0 FAIL，P3-038 为 12 PASS / 0 FAIL，两套退出码均为 0。用户已采纳 P3-038 PM 结论，但风险仍未关闭，Schema / API 仍未冻结。

本任务用于独立判断整改是否真实、是否存在 trigger order、REPLACE、事务、残留行或相邻 Authorization 子表变异旁路，以及 evidence 是否可信。它不是风险关闭任务，也不允许把受控候选结果外推到真实用户数据库或真实 Tauri / IPC。

## 授权边界

本任务明确授权：

- 只读审查 P3-037、P3-038、P3-031 的任务直接依赖文件、相关风险行和 PM Review。
- 可使用 `rg`、`sed`、hash 校验、SQLite 静态分析等只读命令。
- 可将 P3-031、P3-037、P3-038 复制到系统临时目录后复跑；不得在原目录运行会改写 evidence 的脚本。
- 可在临时副本增加评审专用反例脚本或 SQL 探针；这些改动不得回写工程目录。
- 可将详细评审 evidence 写入 `lifeos/reviews/LIFEOS-P3-039/evidence/`，其中必须提供 `MANIFEST.md`；若不产生额外 evidence，应在评审中说明。
- 可将完整独立评审写入 `lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`。
- 可调用本地预检脚本检查评审文件覆盖与措辞。

本任务不授权：

- 不修改 `lifeos/engineering/LIFEOS-P3-031/`、`LIFEOS-P3-037/`、`LIFEOS-P3-038/` 的任何原始 SQL、测试、脚本、fixture 或 evidence。
- 不修改 P3-037 / P3-038 交付物或 PM Review。
- 不修改 `CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md` 或其他 PM 账本。
- 不执行工程修复；发现问题只记录反例、严重级别、证据路径和整改边界。
- 不创建、连接、迁移或写入真实用户数据库，不做非空真实旧库 upgrade。
- 不读取或写入真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC，不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0046，不重新打开或关闭 R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动整改任务、风险关闭任务、后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P3-038 是否真实关闭 P3-037 的 P2-2、P2-3、P2-4 三项已知 P1，而不是只调整测试口径。
- Tombstone DELETE、`INSERT OR REPLACE`、DELETE+INSERT、非法初始状态、状态转换和事务回滚是否在候选 DB 层 fail closed。
- active Authorization scope/action/policy DELETE 是否确实被拒绝，inactive 清理是否仍可用。
- active Authorization 子表是否仍存在直接 INSERT、UPDATE、effect / target 改写、authorization_id 改绑、policy 直接改写等相邻旁路；若存在，严重级别和影响是什么。
- P3-031 与 P3-038 两套结果、退出码、hash、P3-037 failure evidence 保留、backup / restore、rollback 和路径隔离是否可信。
- P3-038 应判定 Pass、Pass with Conditions、Rework 还是 Blocked。
- R-0043 / R-0046 是否可进入后续风险关闭决策输入，还是必须继续整改；评审本身不得关闭风险。

## 范围

本任务必须覆盖：

1. **P2-2 Tombstone 删除 / 重插独立攻击**
   - 普通 DELETE。
   - `INSERT OR REPLACE` 同主键低 generation / 相同 generation / 高 generation。
   - 显式 DELETE+INSERT 在单事务 commit 与 rollback 下的行为。
   - trigger 顺序、冲突处理、异常后行内容与六类合成消费门是否保持 DENY。
2. **P2-3 Tombstone 初始状态与转换独立攻击**
   - 非 `accepted` 初始 INSERT。
   - 合法 `accepted` 起点与合法状态转换。
   - 非法跳转、generation 降低及失败后零残留 / 原行不变。
3. **P2-4 Authorization 子表独立攻击**
   - active 父授权下 scope/action/policy DELETE。
   - inactive / revoked / expired 等非 active 状态下合法清理边界。
   - 父状态、generation、子行和 audit 是否保持一致。
4. **相邻变异反例**
   - active Authorization 下直接 INSERT 新 allow scope / action 或额外 policy 语义。
   - UPDATE scope `effect`、project/source/artifact target、action 值或 `authorization_id` 改绑。
   - UPDATE policy 的 retention、sensitivity、external send、recipient / region 等字段。
   - 判断这些路径是否会绕过 generation / audit / outbox 或扩大权限；发现问题时给出最小可复现证据，但不得在原目录修复。
5. **两套回归与退出合同**
   - 在临时副本复跑 P3-031 和 P3-038。
   - 核对 PASS / FAIL / P0 / P1 / P2 / Not Implemented / Unknown 与退出码一致。
6. **Evidence 与隔离复核**
   - 核对稳定源文件 hash、运行输出 hash、P3-037 failure evidence 保留声明。
   - 核对固定入口、路径隔离、只读 source fixture、integrity / FK、backup / restore 与 rollback。
7. **风险与不可外推边界**
   - 分别判断 R-0043、R-0046；确认 R-0040 仍 Open / Conditional。
   - 若相邻变异影响 R-0044 的既有关闭条件，只能提出“建议 PM 重新评估”，不得自行改状态。
   - 明确当前结论不得外推到真实 DB、非空旧库 upgrade、真实 Tauri / IPC、跨平台、并发 / WAL / 断电或生产 SLA。

## 非范围

本任务暂时不要做：

- 不修改或修复候选 SQL、合同测试、runner、fixture 或原始 evidence。
- 不在 P3-031 / P3-037 / P3-038 原目录运行会改写 evidence 的命令。
- 不执行真实用户 DB migration或非空真实旧库 upgrade。
- 不触碰真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不运行真实 Tauri / IPC，不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭或改变 R-0040、R-0043、R-0044、R-0045、R-0046 状态。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段，不创建或启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
- `lifeos/reviews/LIFEOS-P3-038_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-038/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_2_tombstone_delete_insert.json`
- `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_3_tombstone_status_insert.json`
- `lifeos/engineering/LIFEOS-P3-038/evidence/checks/p2_4_authorization_child_delete.json`
- `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-038/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`
- `lifeos/reviews/LIFEOS-P3-037_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- P3-038 交付物、PM Review、evidence manifest、候选 SQL、测试脚本和 P3-038 runner 必须完整读取。
- P3-037 只需读取失败摘要、PM Review、manifest 与 P2-2 / P2-3 / P2-4 直接相关 evidence，不读取无关历史。
- `RISK_LOG.md` 只定向读取 R-0040、R-0043、R-0044、R-0045、R-0046。
- `DECISION_LOG.md` 如需读取，只读 D-0209 至 D-0212。
- 不主动读取完整 `PROJECT_CONTEXT.md` 或无关 Deliverable、Review、Evidence。
- 若上下文不足，先列出缺少的文件和原因，不自行全量翻历史。
- 复跑必须在临时副本进行，聊天中只报告统计、关键失败和 evidence 路径。

## 角色检查点

主责角色必须重点回答：

- 三项已知 P1 是否在 DB 层真实关闭，测试是否可复核、未过拟合。
- 是否存在 trigger 顺序、REPLACE、事务或残留行反例。
- active Authorization 子表相邻 INSERT / UPDATE / 改绑路径是否造成新的 P0 / P1。
- Evidence、hash、退出码和路径隔离是否足以支持独立结论。

协审角色必须重点检查：

- 删除 / 撤回对象是否仍不可复活，用户数据主权边界是否 fail closed。
- Authorization 权限是否能被静默扩大或在 generation / audit / outbox 不变时改写。
- R-0043 / R-0046 是否只能进入关闭候选，而不能由评审会话直接关闭。
- 是否绝对没有触碰真实用户 DB、真实 Vault、真实文件或真实 Tauri / IPC。

## 核心问题

请重点回答：

- P3-038 最终结论应为 Pass、Pass with Conditions、Rework 还是 Blocked？
- P2-2、P2-3、P2-4 是否分别通过独立反例攻击？
- P3-031 38 PASS 与 P3-038 12 PASS 是否可独立复现，退出合同是否可信？
- 是否发现新的 P0、P1 或关键 P2？
- Authorization 子表 INSERT / UPDATE / 改绑是否存在与 DELETE 同级的完整性旁路？
- R-0043、R-0046 是否可进入后续风险关闭决策输入？
- R-0044 是否需要建议 PM 重新评估？R-0045 是否保持 Closed？
- 哪些内容仍不得外推为生产 migration、真实 DB、真实 Tauri / IPC、Schema / API 冻结或下一阶段准入？

## 交付物

请将完整独立评审保存为：

`lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`

如产生评审复跑日志、反例脚本或结构化结果，请保存到：

`lifeos/reviews/LIFEOS-P3-039/evidence/`

并创建：

`lifeos/reviews/LIFEOS-P3-039/evidence/MANIFEST.md`

独立评审必须包含：

- 评审信息与独立性声明
- 评审摘要
- 已通过内容
- P2-2 / P2-3 / P2-4 独立攻击结果
- Authorization 相邻 INSERT / UPDATE / 改绑反例结果
- 两套回归统计与退出码
- Evidence / hash / 路径隔离复核
- P0 / P1 / P2 分类
- R-0040 / R-0043 / R-0044 / R-0045 / R-0046 独立建议
- Gate 2 / Gate 3 / Gate 4 判断
- 必须整改项或条件通过项
- 需要 PM 决策
- 不可外推声明
- 最终建议

## 验收标准

只有满足以下条件，任务才算完成：

- 完整独立评审已保存到指定路径。
- 明确声明评审会话未参与 P3-038 工程整改，并与执行上下文隔离。
- 在临时副本复跑 P3-031 与 P3-038，或明确说明无法复跑的客观原因及其对结论的影响。
- 已独立攻击 P2-2、P2-3、P2-4，并提供可复核结果。
- 已检查 active Authorization 子表 INSERT、UPDATE、effect / target 改写、authorization_id 改绑和 policy 直接改写。
- 已核对 P3-037 failure evidence 保留、稳定输入 hash、结果统计、退出码和不可外推边界。
- 已明确是否存在 P0 / P1 / P2。
- 已明确 P3-038 的 Pass / Pass with Conditions / Rework / Blocked 结论。
- 已分别给出 R-0043、R-0046 是否可进入关闭候选的建议，并判断 R-0044 是否需 PM 重新评估。
- 未修改任何原始工程文件或 PM 账本。
- 已完成本地预检并提供路径，或说明允许跳过的原因。
- 聊天回复只输出摘要、评审路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-031 / P3-037 / P3-038 原始工程文件、交付物、PM Review 或 evidence。
- 不修改项目账本。
- 不执行工程修复。
- 不创建、连接、迁移或写入真实用户数据库，不处理真实 Vault、真实文件或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭或改变 R-0040、R-0043、R-0044、R-0045、R-0046。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动后续任务，不进入下一阶段。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整评审或测试日志，只输出摘要、评审文件路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
