# LIFEOS-P3-037｜受控文件型 SQLite migration / 残留 P2 验证执行任务

## 任务信息

- 任务 ID：LIFEOS-P3-037
- 任务名称：受控文件型 SQLite migration / 残留 P2 验证执行任务
- 优先级：P0
- 任务类型：工程验证任务 / 受控执行 / Evidence 生成
- 建议篇幅：1500-3000 字；完整日志写入 evidence，报告只写摘要、结论、证据路径和失败处理
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在隔离目录内创建合成文件型 SQLite 验证包、运行脚本、生成 evidence manifest，并验证 P2-2 / P2-3 / P2-4；Codex 更适合工程执行、脚本、测试和 evidence 整理。
- 是否需要后续独立评审：Yes；若本任务通过，后续必须由隔离独立工程评审会话复核 P2-2 / P2-3 / P2-4 结果、路径隔离、hash、rollback、evidence 和不可外推边界，才能作为更高层真实 DB / Schema / API 后续输入。
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-037/` 和本任务交付物路径
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 工程验证负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程执行 / SQLite 验证会话
- 推荐复用的会话：可复用此前 P3 SQL migration / DB 合同测试工程线 Codex 会话，前提是上一任务已结束、没有未完成修改、上下文未混淆，并且能重新读取本任务卡；否则新建 Codex 工程执行会话。
- 会话判断理由：本任务与 P3-031 至 P3-036 属于同一 SQL migration / DB 验证线，且是受控工程执行；复用同一工程线会话可降低上下文成本。
- 是否需要独立性隔离：执行阶段 No；后续独立评审 Yes，且不得由本执行会话评审自己的结果。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅用于短报告结构参考；本任务不适用快车道）
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
  - `lifeos/deliverables/LIFEOS-P3-036_real_db_migration_preflight_checklist.md`
  - `lifeos/reviews/LIFEOS-P3-036_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- 可复用既有读取结果：
  - 若同一 Codex 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-036 交付物与 PM Review
  - P3-031 evidence manifest 和三个稳定源文件 hash
  - R-0040 / R-0043 / R-0044 / R-0045 风险行
- 任务完成后是否建议保留会话：Yes，作为受控 SQLite 验证执行线保留；但不得用于后续独立评审本任务结果。

## 背景

P3-036 已由 PM 验收为 Accepted / Planning Input，明确下一步建议是“受控文件型 SQLite migration / 残留 P2 验证执行任务”。本任务承接 P3-036，不验证非空旧版本 upgrade，不触碰真实用户 DB，而是在新建隔离目录中使用合成无敏感 fixture 和文件型 SQLite 工作副本，攻击 P2-2 / P2-3 / P2-4。

三个残留项来自 P3-035：

- P2-2：Tombstone DELETE+INSERT 旁路。
- P2-3：Tombstone status INSERT 旁路。
- P2-4：Authorization 激活后子表 DELETE 审计完整性。

本任务目标不是“上线真实 DB migration”，而是验证候选 SQL 和未来执行边界在文件型 SQLite 场景中是否仍能 fail closed，并产出可复核 evidence。

## 授权边界

本任务明确授权：

- 在 `lifeos/engineering/LIFEOS-P3-037/` 下创建受控验证包，包括脚本、合成 fixture、临时 SQLite 工作副本、测试结果和 evidence。
- 只读引用 P3-031 的候选 SQL、测试脚本、复跑脚本和 evidence manifest。
- 可复制 P3-031 候选 SQL 到 P3-037 隔离目录作为验证输入快照，但不得修改 P3-031 原始文件。
- 可使用 Python 标准库 `sqlite3` 或系统 / bundled SQLite，在新建隔离目录内创建和写入合成 SQLite 文件。
- 可编写并运行 P2-2 / P2-3 / P2-4 的受控验证脚本。
- 可执行 backup / restore、integrity_check、foreign_key_check、hash 计算、rollback / commit 反例、消费门模拟断言和 evidence manifest 生成。
- 可输出完整报告到 `lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`。
- 可输出 evidence 到 `lifeos/engineering/LIFEOS-P3-037/evidence/`。
- 可调用本地预检脚本检查交付物完整性。

本任务不授权：

- 不修改 P3-031 原始候选 SQL、测试脚本、复跑脚本或 evidence。
- 不修改 P3-009 / P3-031 以外任何既有工程基线或生产代码。
- 不创建、连接、迁移或写入真实用户数据库。
- 不读取或写入真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不重新打开或关闭 R-0043 / R-0044 / R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不修改 `lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md`、`lifeos/RISK_LOG.md` 或其他 PM 账本。
- 不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P2-2 / P2-3 / P2-4 在文件型 SQLite + 合成 fixture 场景下是否被阻断或 fail closed。
- P3-031 候选 SQL 快照、测试脚本和验证脚本 hash 是否可追溯。
- 验证是否严格限制在隔离目录和合成数据中。
- backup / restore、rollback、integrity_check、foreign_key_check 和 evidence manifest 是否足以支撑后续独立评审。
- 结果是否足以进入后续独立工程评审，还是需要先返工。

## 范围

本任务必须覆盖：

1. **隔离执行环境**
   - 创建 `lifeos/engineering/LIFEOS-P3-037/`。
   - 明确 `input/`、`work/`、`scripts/`、`evidence/` 等目录。
   - 拒绝真实路径、`~`、宽泛目录、symlink 到目录外、网络路径或用户 DB / Vault 路径。
2. **稳定输入核对**
   - 核对 P3-031 manifest 中的稳定源文件 hash。
   - 将候选 SQL 复制为 P3-037 输入快照并记录 hash。
   - 区分稳定输入 hash 与运行输出 hash。
3. **文件型 SQLite 合成 fixture**
   - 创建只读 source fixture 和可丢弃 working copy。
   - fixture 必须无真实用户正文、真实路径、URL、密钥、真实 Project 名或可反识别 ID。
   - 记录 SQLite 版本、编译选项、PRAGMA `foreign_keys` 状态、journal mode 和操作系统。
4. **P2-2 验证**
   - Tombstone DELETE+INSERT 旁路。
   - 覆盖普通 DELETE、`INSERT OR REPLACE`、commit / rollback。
   - 验证消费门 / 恢复候选 / outbox / export 相关模拟断言仍拒绝。
5. **P2-3 验证**
   - Tombstone status INSERT 旁路。
   - 覆盖直接 INSERT `active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited`。
   - 覆盖合法 `accepted` 起点和合法 / 非法状态转换矩阵。
6. **P2-4 验证**
   - Authorization active 后 scope/action/policy 子表 DELETE。
   - 覆盖直接 DELETE、事务内先删后查、提交后查、rollback、缓存 / 队列重检模拟。
   - 验证 `strict_intersection` 或等价消费门在不完整授权时 DENY / AMBIGUOUS。
7. **Evidence 与报告**
   - 生成 `MANIFEST.md`。
   - 输出 `test_results.json` 和简短 `summary.md`。
   - 聊天中只输出摘要、交付物路径、evidence manifest 路径和是否需要 PM 决策。

## 非范围

本任务暂时不要做：

- 不做非空旧版本 upgrade migration。
- 不执行真实用户 DB migration。
- 不触碰真实 Vault、真实文件、真实导出路径或真实敏感数据。
- 不运行真实 Tauri / IPC。
- 不修改 P3-031 原始候选 SQL、测试、脚本或 evidence。
- 不修改 P3-009 工程基线、生产代码或其他工程目录。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不重新打开或关闭 R-0043 / R-0044 / R-0045。
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
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
- `lifeos/deliverables/LIFEOS-P3-036_real_db_migration_preflight_checklist.md`
- `lifeos/reviews/LIFEOS-P3-036_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- `RISK_LOG.md` 只需定向读取 R-0040、R-0043、R-0044、R-0045。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0205 至 D-0208 或任务卡指定决策。
- 不主动读取无关 Review、Deliverable 或 Evidence。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 文件型 SQLite 验证是否严格隔离、可复跑、可审计。
- P2-2 / P2-3 / P2-4 是否都有实际运行结果、PASS / FAIL 和证据。
- 验证脚本是否有非零退出合同，任何 P0/P1 / Unknown / Not Implemented 都会失败。
- 结果是否可支持后续独立工程评审。

协审角色必须重点检查：

- 删除 / 撤回、授权、AI 派生、来源身份和证据链是否仍 fail closed。
- 是否绝对没有触碰真实用户 DB、真实 Vault、真实文件、真实 Tauri / IPC。
- evidence 是否足以让 PM 和独立评审复核。
- 是否清楚区分事实、推断、建议和需 PM / 用户确认事项。

## 核心问题

请重点回答：

- P2-2 在受控文件型 SQLite 验证中是 PASS、FAIL 还是 Blocked？依据是什么？
- P2-3 在受控文件型 SQLite 验证中是 PASS、FAIL 还是 Blocked？依据是什么？
- P2-4 在受控文件型 SQLite 验证中是 PASS、FAIL 还是 Blocked？依据是什么？
- 是否发生任何 P0 / P1 / Not Implemented / Unknown？
- 是否完整证明未触碰真实 DB / Vault / Tauri / IPC / 真实文件？
- evidence 包是否包含足以复核的 hash、环境、命令、退出码、rollback、restore、integrity / FK、测试结果和 summary？
- 是否建议进入后续独立工程评审？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB migration 通过、真实 Tauri / IPC 通过、R-0040 关闭、正式 MVP 准入或下一阶段准入？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-037_controlled_file_sqlite_residual_p2_validation.md`

请将 evidence 保存到：

`lifeos/engineering/LIFEOS-P3-037/evidence/MANIFEST.md`

交付物内容必须包括：

- 任务信息
- 执行摘要
- 授权边界与实际修改范围
- 输入 hash 与环境
- 目录 / 路径隔离证明
- P2-2 验证结果
- P2-3 验证结果
- P2-4 验证结果
- PASS / FAIL / P0 / P1 / P2 / Not Implemented 统计
- backup / restore / rollback / integrity / FK 结果
- evidence manifest 路径
- 不可外推声明
- 风险与待确认事项
- 后续独立评审建议

Evidence manifest 至少包括：

- 授权范围
- 创建 / 修改文件清单
- 稳定输入 hash
- 运行输出 hash
- 环境信息
- 准确命令
- 退出码
- 测试统计
- P2-2 / P2-3 / P2-4 逐项证据路径
- 恢复演练和 rollback 证据
- 不可外推声明

## 验收标准

只有满足以下条件，任务才算完成：

- 完整交付物已保存到指定路径。
- evidence manifest 已保存到指定路径。
- 只修改 `lifeos/engineering/LIFEOS-P3-037/` 和本任务交付物 / 本地预检路径。
- 已覆盖 P2-2 / P2-3 / P2-4。
- 已证明未触碰真实用户 DB、真实 Vault、真实 Tauri / IPC、真实文件或真实敏感数据。
- 已明确是否存在 P0 / P1 / Not Implemented / Unknown。
- 已明确是否建议进入后续独立工程评审。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-031 原始候选 SQL、测试、脚本或 evidence。
- 不修改 P3-009 工程基线、生产代码或其他工程目录。
- 不创建、连接、迁移或写入真实用户数据库。
- 不读取或写入真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不重新打开或关闭 R-0043 / R-0044 / R-0045。
- 不修改 PM 账本或风险状态。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整交付物或完整日志，只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
