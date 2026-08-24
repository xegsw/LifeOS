# LIFEOS-P3-033｜候选 SQL activation INSERT 旁路条件整改

## 任务信息

- 任务 ID：LIFEOS-P3-033
- 任务名称：候选 SQL activation INSERT 旁路条件整改
- 优先级：P1
- 任务类型：补丁 / 条件整改型任务 / 受控工程整改
- 建议篇幅：1500-3000 字；详细测试日志写入 evidence，不粘贴到聊天
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要在既有候选 SQLite migration 与合成空库合同测试中补齐明确的 P1 INSERT active 旁路，Codex 更适合受控 SQL trigger、测试脚本、复跑和 evidence manifest 更新。
- 是否需要后续独立评审：Conditional。若 P3-033 只补齐 P3-032 指定 P1/P2 且 PM 复跑通过，可先由 PM 验收；是否需要 P3-034 轻量独立复评由 PM 在验收后决定。若出现 P0、新 P1 或范围扩展，必须独立复评。
- 是否允许修改工程文件：Yes，仅限本任务授权范围
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人、数据 / 领域模型负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：Codex 工程执行
- 推荐复用的会话：可复用此前承担 P3-031 候选 SQL / 合同测试实现的 Codex 工程执行会话，前提是该会话上一任务已结束、没有未完成修改、上下文未混淆、能重新读取本任务卡，且未参与 P3-032 独立评审；否则新建 Codex 工程执行会话。
- 会话判断理由：P3-033 是 P3-031 的明确条件整改，适合原工程执行线继续补丁；但不得复用 P3-032 独立评审会话，避免评审者直接修改自己刚评审的成果。
- 是否需要独立性隔离：Yes，P3-032 独立评审会话不得执行本任务；P3-033 执行会话不得自行承担后续独立复评。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅参考短报告结构；本任务不适用快车道）
  - `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
  - `lifeos/reviews/LIFEOS-P3-032_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
  - `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045 相关行
- 可复用既有读取结果：
  - 若同一 Codex 工程执行会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-032 独立评审与 PM Review
  - P3-031 候选 SQL、测试脚本、复跑脚本和 evidence manifest
  - R-0044 / R-0045 风险行
- 任务完成后是否建议保留会话：Yes，作为候选 SQL / 合同测试条件整改线保留。

## 背景

P3-032 独立工程评审已由 PM 验收为 Accepted / Pass with Conditions。评审未发现 P0，但发现 2 项 P1：

1. `authorization_activation_complete` 仅覆盖 `BEFORE UPDATE OF status`，直接 `INSERT status='active'` 可绕过 scope/action/policy 完整性检查，R-0044 不能进入关闭候选。
2. `derivation_activation_complete` 仅覆盖 `BEFORE UPDATE OF status`，直接 `INSERT status='active'` 可绕过 inputs / constraints 完整性检查，已登记为 R-0045。

本任务用于在候选 SQL 与合成空库合同测试层补齐上述 INSERT active 旁路，并同步修复 P3-032 指出的 MANIFEST 生成文件 hash 不一致问题。

## 授权边界

本任务明确授权修改：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`（仅在复跑入口确有必要时）
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
- `lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`

本任务不授权：

- 不修改 PM 账本。
- 不修改 P3-032 独立评审文件或 PM Review。
- 不连接真实数据库、真实 Vault、真实用户文件、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不创建真实生产 SQL migration，不执行真实数据库 migration。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不关闭 R-0040、R-0043、R-0044 或 R-0045。
- 不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- Authorization 直接 `INSERT status='active'` 是否已被候选 SQL fail closed。
- Derivation 直接 `INSERT status='active'` 是否已被候选 SQL fail closed。
- 对应负测是否进入合成空库合同测试，且任一失败会导致验证命令非零退出。
- P3-032 的 P2-1 MANIFEST 生成文件 hash 不一致是否已修复。
- 是否允许将 R-0044 / R-0045 标记为“待 PM 验收的关闭候选”，或仍需返工。
- 是否允许后续启动 P3-034 轻量独立复评或风险关闭决策包。

## 范围

本任务必须覆盖：

1. **Authorization INSERT active 旁路整改**
   - 增加候选 SQL 保护，优先方案为 `BEFORE INSERT` trigger 拒绝直接插入 `status='active'` 的 Authorization，强制走 propose / grant / activate 更新流程。
   - 若选择同等完整性校验方案，必须解释为什么比拒绝直接 active insert 更安全。
   - 增加合同测试：直接 `INSERT INTO authorization (... status='active' ...)` 必须被拒绝。
2. **Derivation INSERT active 旁路整改**
   - 增加候选 SQL 保护，优先方案为 `BEFORE INSERT` trigger 拒绝直接插入 `status='active'` 的 Derivation，强制先创建非 active，再补齐 inputs / constraints 后激活。
   - 增加合同测试：直接 `INSERT INTO derivation (... status='active' ...)` 必须被拒绝。
3. **测试统计与退出合同**
   - 更新测试列表与结果统计。
   - 任一 P0 / P1 / P2 FAIL 均必须导致验证命令非零退出。
   - 报告 total / P0 / P1 / P2 PASS / FAIL / Not Implemented。
4. **Evidence 修复**
   - 复跑 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`。
   - 更新 `test_results.json`、`test_run.log` 和 `MANIFEST.md` 中对应 hash。
   - MANIFEST 必须清楚说明哪些 hash 是源文件 hash，哪些是本次生成文件 hash。
5. **短工程报告**
   - 输出 P3-033 交付物，说明修改范围、测试摘要、P3-032 条件处理、R-0044 / R-0045 候选关闭状态、剩余风险和下一步建议。

## 非范围

本任务暂时不要做：

- 不处理真实数据库 migration。
- 不引入真实 SQLite 生产库升级、WAL / backup、跨平台、性能或容量验证。
- 不连接真实 Vault、真实用户数据、真实 Tauri / IPC 或真实文件能力。
- 不实现真实 Tauri handler、capability 或 IPC。
- 不修改 P3-032 独立评审结论。
- 不修改项目账本。
- 不关闭 R-0040、R-0043、R-0044、R-0045。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动 P3-034 或任何后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-032_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- `lifeos/reviews/LIFEOS-P3-031_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- P3-032 独立评审与 PM Review 必须完整读取。
- P3-031 候选 SQL、测试脚本、复跑脚本、evidence manifest 必须完整读取。
- `RISK_LOG.md` 可定向读取 R-0040、R-0043、R-0044、R-0045。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同、核心领域模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需要只读 D-0196 至 D-0199。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- Authorization / Derivation 的直接 INSERT active 旁路是否已被 DB 层 fail closed。
- 修改是否足够窄，是否只影响候选 SQL 与合成空库合同测试。
- 测试是否证明 P3-032 指出的两个 P1 已被补齐。
- evidence manifest 是否与最新源文件和生成文件一致。

协审角色必须重点检查：

- Authorization、Derivation、AI 派生内容身份、证据链和消费门没有被放宽。
- 整改没有被外推为真实 DB / Tauri / IPC 通过。
- 报告没有宣布风险关闭、Schema/API 冻结或工程基线冻结。
- P2 项是否被处理或明确保留。

## 核心问题

请重点回答：

- P3-032 的 P1-1 Authorization INSERT active 旁路是否已关闭？
- P3-032 的 P1-2 Derivation INSERT active 旁路是否已关闭？
- 是否新增 P0 / P1 / P2？
- 最新复跑结果是多少？
- R-0044 / R-0045 是否可进入“待 PM 验收的关闭候选”？
- R-0043 是否受到本次整改影响？
- 哪些内容仍不得外推为 Schema / API 冻结、真实 DB 验证、真实 Tauri / IPC 通过或 R-0040 关闭？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`

同时更新：

- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`

交付物内容必须包括：

- 任务摘要
- 修改范围
- 候选 SQL 修改说明
- 测试脚本修改说明
- 复跑命令
- 测试摘要：total / P0 / P1 / P2 PASS / FAIL / Not Implemented
- P3-032 P1 / P2 条件处理情况
- R-0044 / R-0045 处理情况
- R-0043 是否受影响
- evidence manifest 路径
- 剩余风险
- 是否建议 PM 启动 P3-034 轻量独立复评或风险关闭决策包
- 非冻结 / 非真实能力声明

## 验收标准

只有满足以下条件，任务才算完成：

- Authorization 直接 INSERT active 负测存在且通过。
- Derivation 直接 INSERT active 负测存在且通过。
- 合成空库验证命令可复跑。
- 任一 FAIL 会导致命令非零退出。
- `MANIFEST.md` 与最新源文件和生成文件一致，或清楚说明生成文件 hash 口径。
- 完整报告已保存到 `lifeos/deliverables/`。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复只输出摘要、交付物路径、evidence 路径、预检路径和是否需要 PM 决策。
- 明确声明本任务不冻结 Schema / API、不关闭 R-0040 / R-0043 / R-0044 / R-0045、不启用真实能力、不进入下一阶段。

## 限制条件

- 只允许修改任务卡授权的 P3-031 候选 SQL / 测试 / evidence 文件和本任务交付物。
- 不修改项目账本。
- 不连接真实数据库、真实 Vault 或真实用户数据。
- 不运行真实 Tauri，不创建真实 IPC handler。
- 不启用真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044、R-0045。
- 不冻结 Schema / API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整报告或测试日志，只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
