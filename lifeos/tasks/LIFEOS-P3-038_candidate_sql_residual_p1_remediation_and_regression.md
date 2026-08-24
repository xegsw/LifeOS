# LIFEOS-P3-038｜候选 SQL 残留 P1 整改与回归任务

## 任务信息

- 任务 ID：LIFEOS-P3-038
- 任务名称：候选 SQL 残留 P1 整改与回归任务
- 优先级：P0
- 任务类型：工程整改任务 / 候选 SQL 补丁 / 回归验证 / Evidence 生成
- 建议篇幅：1500-3000 字；完整日志写入 evidence，报告只写摘要、变更、测试结果、证据路径和风险边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要修改候选 SQL、补充合同测试、复跑合成空库与受控文件型 SQLite 回归，并产出 evidence；Codex 更适合工程整改、脚本、测试和证据整理。
- 是否需要后续独立评审：Yes；若本任务整改通过，后续必须由隔离独立工程评审会话复核 SQL 约束、P2-2 / P2-3 / P2-4 回归、hash、路径隔离、rollback、evidence 和不可外推边界。
- 是否允许修改工程文件：Yes，仅限本任务授权范围
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 工程整改负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程整改 / SQLite 验证会话
- 推荐复用的会话：可复用此前 P3 SQL migration / DB 合同测试工程线 Codex 会话，前提是上一任务已结束、没有未完成修改、上下文未混淆，并且能重新读取本任务卡；否则新建 Codex 工程整改会话。
- 会话判断理由：本任务承接 P3-037 失败结果，属于同一 SQL migration / DB 验证线的窄范围整改。
- 是否需要独立性隔离：执行阶段 No；后续独立复评 Yes，且不得由本执行会话评审自己的整改结果。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046 相关行
  - `lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`
  - `lifeos/reviews/LIFEOS-P3-037_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json`
  - `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- 可复用既有读取结果：
  - 若同一 Codex 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-037 交付物、PM Review 和三个失败 JSON
  - P3-031 当前候选 SQL、测试脚本、runner 和 MANIFEST
  - R-0043 / R-0046 风险行
- 任务完成后是否建议保留会话：Yes，作为候选 SQL 整改线保留；但不得用于后续独立复评本任务结果。

## 背景

P3-037 已由 PM 验收为 Accepted / Validation Failed。它在受控文件型 SQLite + 合成 fixture 中稳定复现 3 个 P1 失败：

- P2-2：tombstone 可通过普通 DELETE、`INSERT OR REPLACE`、DELETE+INSERT commit 删除或降代，六类合成消费门由 DENY 变 ALLOW。
- P2-3：tombstone 可直接 INSERT 为 `active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited` 等非 `accepted` 初始状态。
- P2-4：active Authorization 的 scope/action/policy 子表可直接 DELETE；运行时重检仍 DENY / AMBIGUOUS，但父授权仍 active、generation 不变、audit 未追加。

PM 因 P2-2 / P2-3 重新打开 R-0043，并新增 R-0046 跟踪 P2-4 的 audit / generation fencing 缺口。P3-038 用于对候选 SQL 和合同测试做窄范围整改，重新跑合成空库和文件型 SQLite 回归。

## 授权边界

本任务明确授权：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限修复 P2-2 / P2-3 / P2-4 对应的候选 SQL 约束、trigger 或必要索引。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限补充或调整 P2-2 / P2-3 / P2-4 的合成空库合同测试和回归断言。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限保持单一复跑入口和退出码合同，不得扩大到真实能力。
- 更新 `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`、`test_results.json`、`test_run.log`，记录 P3-038 后的最新候选 SQL / 测试 / runner hash 与复跑结果。
- 在 `lifeos/engineering/LIFEOS-P3-038/` 下创建本任务专属回归包、脚本、合成 fixture、测试结果和 evidence。
- 可复制 P3-037 的验证思路或脚本到 P3-038 隔离目录，但不得覆盖或改写 P3-037 原始 failure evidence。
- 可运行 P3-031 合成空库合同测试与 P3-038 受控文件型 SQLite 回归。
- 可输出完整报告到 `lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`。
- 可输出 evidence 到 `lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`。
- 可调用本地预检脚本检查交付物完整性。

本任务不授权：

- 不修改 P3-037 原始 failure evidence、P3-037 交付物或 P3-037 PM Review。
- 不修改 P3-009 工程基线、生产代码或其他工程目录。
- 不做非空旧版本 upgrade migration。
- 不创建、连接、迁移或写入真实用户数据库。
- 不读取或写入真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0046。
- 不重新打开或关闭 R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不修改 `lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md`、`lifeos/RISK_LOG.md` 或其他 PM 账本。
- 不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P2-2 是否已由候选 SQL / 合同测试阻断：tombstone 不能被直接 DELETE、`INSERT OR REPLACE` 或 DELETE+INSERT commit 删除 / 降代 / 复活。
- P2-3 是否已由候选 SQL / 合同测试阻断：tombstone 初始 INSERT 只能为 `accepted`，非 `accepted` 状态必须经合法状态转换和证明进入。
- P2-4 是否已由候选 SQL / 合同测试修复：active Authorization 子表 DELETE 被 DB 直接拒绝，或受控事务内父授权降级 / 撤销、generation 递增、audit / outbox 追加且消费门 fail-closed。
- P3-031 合成空库合同测试是否重新通过，且 P3-037 类文件型 SQLite 回归是否从 3 个 P1 FAIL 变成 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown。
- 结果是否足以进入后续隔离独立工程复评。

## 范围

本任务必须覆盖：

1. **候选 SQL 整改**
   - P2-2：阻断 tombstone 直接 DELETE、`INSERT OR REPLACE`、DELETE+INSERT 降代 / 复活。
   - P2-3：阻断 tombstone 非 `accepted` 初始 INSERT。
   - P2-4：阻断 active Authorization 子表直接 DELETE，或实现等价的受控降级 / generation / audit / outbox 合同。
2. **合成空库合同测试**
   - 在 P3-031 合同测试中补齐对应负测。
   - 确保旧有 P0 / P1 / P2 合同测试不回退。
3. **受控文件型 SQLite 回归**
   - 在 P3-038 隔离目录内复现 P3-037 三个攻击面。
   - 输出结构化 JSON 和 MANIFEST。
4. **证据链**
   - 记录 P3-031 修改前后稳定源文件 hash。
   - 区分稳定输入 hash 与运行输出 hash。
   - 明确 P3-037 failure evidence 保持不变。
5. **不可外推边界**
   - 明确本整改只在候选 SQL、合成空库和受控文件型 SQLite 范围内成立。
   - 不代表真实用户 DB、非空旧库 upgrade、真实 Tauri / IPC、Schema / API 冻结或下一阶段准入。

## 非范围

本任务暂时不要做：

- 不执行真实用户 DB migration。
- 不做非空旧版本 upgrade migration。
- 不触碰真实 Vault、真实文件、真实导出路径或真实敏感数据。
- 不运行真实 Tauri / IPC。
- 不修改 P3-037 原始 failure evidence。
- 不修改 P3-009 工程基线、生产代码或无关工程目录。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0046。
- 不重新打开或关闭 R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046 相关行
- `lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`
- `lifeos/reviews/LIFEOS-P3-037_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-037/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_2_tombstone_delete_insert.json`
- `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_3_tombstone_status_insert.json`
- `lifeos/engineering/LIFEOS-P3-037/evidence/checks/p2_4_authorization_child_delete.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- `RISK_LOG.md` 只需定向读取 R-0040、R-0043、R-0044、R-0045、R-0046。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0208 至 D-0210 或任务卡指定决策。
- 不主动读取无关 Review、Deliverable 或 Evidence。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 三个 P1 失败是否被实际修复，而不是只修改测试口径。
- SQL 约束是否足够靠近 DB 层，不能只依赖“正常代码不会这么写”。
- P3-031 合成空库测试和 P3-038 文件型回归是否都通过。
- 变更是否保持候选 SQL 可追溯、可复跑、可审计。

协审角色必须重点检查：

- 删除 / 撤回、授权、AI 派生、来源身份和证据链是否仍 fail closed。
- 是否绝对没有触碰真实用户 DB、真实 Vault、真实文件、真实 Tauri / IPC。
- P3-037 failure evidence 是否被保留而非覆盖。
- evidence 是否足以让 PM 和独立评审复核。

## 核心问题

请重点回答：

- P2-2 的失败原因如何被修复？对应测试结果是什么？
- P2-3 的失败原因如何被修复？对应测试结果是什么？
- P2-4 的失败原因如何被修复？对应测试结果是什么？
- P3-031 合成空库合同测试是否全部通过？统计是什么？
- P3-038 受控文件型 SQLite 回归是否全部通过？统计是什么？
- 是否发生任何 P0 / P1 / Not Implemented / Unknown？
- 是否完整证明未触碰真实 DB / Vault / Tauri / IPC / 真实文件？
- 是否建议进入后续独立工程复评？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB migration 通过、真实 Tauri / IPC 通过、R-0040 关闭、正式 MVP 准入或下一阶段准入？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`

请将 evidence 保存到：

`lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`

交付物内容必须包括：

- 任务信息
- 执行摘要
- 授权边界与实际修改范围
- 修改文件清单
- P2-2 整改说明与回归结果
- P2-3 整改说明与回归结果
- P2-4 整改说明与回归结果
- P3-031 合成空库合同测试结果
- P3-038 文件型 SQLite 回归结果
- PASS / FAIL / P0 / P1 / P2 / Not Implemented / Unknown 统计
- 输入 / 输出 hash
- evidence manifest 路径
- 不可外推声明
- 风险与待确认事项
- 后续独立评审建议

Evidence manifest 至少包括：

- 授权范围
- 创建 / 修改文件清单
- 修改前 / 修改后稳定源文件 hash
- 运行输出 hash
- 环境信息
- 准确命令
- 退出码
- 测试统计
- P2-2 / P2-3 / P2-4 逐项证据路径
- P3-031 与 P3-038 两套回归入口
- P3-037 failure evidence 保留声明
- 不可外推声明

## 验收标准

只有满足以下条件，任务才算完成：

- 完整交付物已保存到指定路径。
- evidence manifest 已保存到指定路径。
- P2-2 / P2-3 / P2-4 均有整改说明、代码 / SQL 变更和回归证据。
- P3-031 合成空库合同测试无 P0 / P1 / Not Implemented / Unknown。
- P3-038 文件型 SQLite 回归无 P0 / P1 / Not Implemented / Unknown。
- P3-037 failure evidence 未被覆盖或改写。
- 已证明未触碰真实用户 DB、真实 Vault、真实 Tauri / IPC、真实文件或真实敏感数据。
- 已明确是否建议进入后续独立工程复评。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-037 原始 failure evidence、P3-037 交付物或 P3-037 PM Review。
- 不修改 P3-009 工程基线、生产代码或其他无关工程目录。
- 不创建、连接、迁移或写入真实用户数据库。
- 不读取或写入真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0046。
- 不重新打开或关闭 R-0044 / R-0045。
- 不修改 PM 账本或风险状态。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整交付物或完整日志，只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
