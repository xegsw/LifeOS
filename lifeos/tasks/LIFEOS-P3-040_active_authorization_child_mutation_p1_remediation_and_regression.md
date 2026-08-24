# LIFEOS-P3-040｜Active Authorization 子表变异 P1 整改与回归

## 任务信息

- 任务 ID：LIFEOS-P3-040
- 任务名称：Active Authorization 子表变异 P1 整改与回归
- 优先级：P0
- 任务类型：工程整改任务 / 候选 SQL 补丁 / 权限边界回归 / Evidence 生成
- 建议篇幅：1500-3000 字；完整日志、结构化测试结果和 hash 写入 evidence，报告仅保留变更、统计、关键结论、证据路径和风险边界
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要修改候选 SQL、扩展合同测试、迁移 P3-039 的 11 条反例、补充状态翻转绕过验证，并产出可复跑 evidence；Codex 更适合工程整改、SQLite trigger、回归测试和证据整理。
- 是否需要后续独立评审：Yes；整改通过后必须由未参与 P3-040 执行的隔离独立评审会话复核，不得由执行 Agent 自评风险关闭。
- 是否允许修改工程文件：Yes，仅限本任务授权范围
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 工程整改负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：No
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：Codex 工程整改 / SQLite 合同测试会话
- 推荐复用的会话：优先复用完成 P3-038 的 Codex 候选 SQL整改会话，前提是上一任务已结束、无未完成修改、上下文未混淆，并能重新读取最新状态和本任务卡；否则新建 Codex 工程整改会话。
- 会话判断理由：本任务直接承接 P3-038 / P3-039，继续修改同一 P3-031 候选 SQL、合同测试和受控 SQLite 回归，属于同一工程线的窄范围整改。
- 是否需要独立性隔离：执行阶段 No；后续复评 Yes，且不得由本执行会话评审自己的整改。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
  - `lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`
  - `lifeos/reviews/LIFEOS-P3-039_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/MANIFEST.md`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_attacks.py`
  - `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_results.json`
  - `lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
  - `lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
  - `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
  - `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
  - `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
  - `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046 相关行
- 可复用既有读取结果：
  - 若同一 Codex 工程会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - P3-039 独立评审、PM Review、反例脚本和结构化结果
  - P3-031 当前候选 SQL、合同测试、runner 和 MANIFEST
  - R-0044 / R-0046 当前风险行
- 任务完成后是否建议保留会话：Yes，作为候选 SQL 权限边界整改线保留；不得用于后续独立复评本任务。

## 背景

P3-039 隔离独立复评确认 P3-038 已真实关闭三个已知攻击面，但发现 active Authorization 的 scope/action/policy 子表仍可通过 11 条 INSERT、UPDATE、`INSERT OR REPLACE` 和 `authorization_id` 改绑路径被静默新增或改写。父授权保持 active，generation 不变，audit 不追加，部分路径可直接新增 allow scope、增加 export action、开启 training 或 external send。

PM 已复现 29 个反例中的 18 PASS / 11 FAIL，并防御性重新打开 R-0044、扩展 R-0046。用户已采纳 P3-039 与上述风险处理，授权启动本窄范围整改。

本任务不能只针对 11 条 SQL 文本逐条打补丁，还必须验证是否可通过“active → 非 active → 修改子表 → 重新 active”绕过新 trigger。若候选 schema 无法在不破坏合法 revoke / expire / supersede 和非 active 清理路径的情况下封住该逃逸路径，必须明确报告 Blocked 或提出后续最小设计条件，不得伪造全绿结果。

## 授权边界

本任务明确授权：

- 修改 `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`，仅限 active Authorization 子表变异保护及为防止状态翻转绕过所必需的最小 Authorization 状态 / generation 约束。
- 修改 `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`，仅限新增本任务相关负测、合法维护路径测试和必要夹具调整。
- 必要时修改 `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`，仅限保持单一复跑入口和非零退出合同。
- 更新 P3-031 evidence manifest、测试结果和日志，记录最新稳定源文件 hash 与回归统计。
- 在 `lifeos/engineering/LIFEOS-P3-040/` 创建本任务专属回归包、候选 SQL 快照、合成 fixture、脚本和 evidence。
- 将 P3-039 的 11 条反例复制到 P3-040 隔离回归包并扩展状态翻转绕过；不得修改 P3-039 原始评审 evidence。
- 运行 P3-031 合成空库合同测试与 P3-040 受控文件型 / 内存 SQLite 回归。
- 输出交付物到 `lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`。
- 输出 evidence manifest 到 `lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`。
- 调用本地预检脚本检查交付物覆盖和越界措辞。

本任务不授权：

- 不修改 P3-037、P3-038、P3-039 原始 failure / review evidence、交付物或 PM Review。
- 不修改 P3-009 工程基线、生产代码或其他无关工程目录。
- 不重写完整 Authorization 领域模型、AI 权限模型或技术架构冻结合同。
- 不执行真实用户 DB migration，不做非空真实旧库 upgrade。
- 不访问真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不安装、配置或运行真实 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040、R-0043、R-0044、R-0046，不关闭或重新打开 R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不修改任何 PM 账本，不启动后续任务或下一阶段。

## 目标

本任务完成后，PM 应能判断：

- P3-039 的 11 个 active Authorization 子表 INSERT / UPDATE / REPLACE / 改绑 P1 是否全部被候选 DB 层阻断。
- trigger 是否同时检查 OLD 与 NEW 父 Authorization 状态，避免从 active 改绑到 inactive 或从 inactive 改绑到 active 的旁路。
- `INSERT OR REPLACE` 是否在 SQLite 冲突处理前被保护，scope/action/policy 是否均无遗漏。
- 是否存在“active → 非 active → 改子表 → 重新 active”的状态翻转逃逸路径；若存在，是否由最小状态 / generation 约束阻断或明确判定 Blocked。
- 合法 revoked / expired / superseded 清理和受控维护路径是否仍可用，没有把生命周期永久锁死。
- P3-031 全量合同测试与 P3-040 文件型 / 内存回归是否达到 0 P0 / 0 P1 / 0 Not Implemented / 0 Unknown。
- 结果是否足以进入后续隔离独立工程复评。

## 范围

本任务必须覆盖：

1. **Scope 保护**
   - active 父下新增 allow / deny scope。
   - UPDATE effect、project_id、source_id、artifact_id。
   - UPDATE authorization_id：OLD 父 active、NEW 父 active、两端状态不同的改绑。
   - `INSERT OR REPLACE` 同 id scope 整体替换。
2. **Action 保护**
   - active 父下新增 action。
   - UPDATE action 值，例如 read → export_candidate。
   - UPDATE authorization_id 改绑。
   - `INSERT OR REPLACE` 同 id action 替换。
3. **Policy 保护**
   - active 父下直接 INSERT / 替换 policy。
   - UPDATE retention、sensitivity、training、external send、recipients、regions、disclosure、license、quantity、frequency 等字段。
   - `INSERT OR REPLACE` policy 整体替换。
4. **状态翻转逃逸测试**
   - active → proposed / granted 等非法回退后修改再激活。
   - active → revoked / expired / superseded 后修改并尝试重新 active。
   - 检查 generation、version、supersedes、audit / outbox 约束是否足以防止静默复用旧授权。
   - 若现有候选 schema 无法安全表达合法状态转换与审计顺序，必须报告 Blocked / 需设计条件，不能跳过此项。
5. **合法维护与清理路径**
   - 非 active Authorization 的 scope/action/policy 清理在明确允许状态下仍可用。
   - 合法新版本 Authorization 的 proposed → complete → active 流程仍通过。
   - 不允许通过修改旧 active 版本代替创建新版本 / supersede 流程。
6. **回归与 Evidence**
   - P3-031 全量测试不回退。
   - P3-039 29 个反例全部迁入或由等价更强测试覆盖；不得删除失败证据来制造全绿。
   - P3-040 增加状态翻转、双向改绑、合法清理与新版本流程测试。
   - 记录修改前后稳定 hash、运行结果、退出码、环境和原始 P3-039 evidence 保留证明。

## 非范围

- 不执行真实用户 DB migration或非空真实旧库 upgrade。
- 不修改真实 Vault、真实用户文件、真实导出路径或真实敏感数据。
- 不运行真实 Tauri / IPC，不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不改写核心领域模型或 AI 权限模型。
- 不修改 P3-039 原始反例结果、独立评审或 PM Review。
- 不关闭或改变风险状态，不冻结资产，不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-039_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-039/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_attacks.py`
- `lifeos/reviews/LIFEOS-P3-039/evidence/counter_example_results.json`
- `lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
- `lifeos/engineering/LIFEOS-P3-038/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/RISK_LOG.md` 中 R-0040、R-0043、R-0044、R-0045、R-0046

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡和直接依赖材料。
- P3-039 独立评审、PM Review、反例脚本与结构化结果必须完整读取。
- P3-031 当前 SQL、测试、runner 和 manifest 必须完整读取。
- `RISK_LOG.md` 只定向读取相关风险行；`DECISION_LOG.md` 如需读取，只读 D-0211 至 D-0214。
- 不主动读取完整 `PROJECT_CONTEXT.md` 或无关历史交付物。
- 若上下文不足，先列出缺少文件和原因，不自行全量翻历史。
- 测试日志只在聊天报告摘要，完整结果写入 evidence。

## 角色检查点

主责角色必须重点回答：

- 11 个 P1 是否由真实 DB trigger / 约束关闭，而不是只修改测试期望。
- INSERT、UPDATE、REPLACE、双向改绑和状态翻转是否全部 fail closed。
- 合法撤回、过期、替代、清理和新版本激活是否未被破坏。
- 两套回归、hash、退出码和 evidence 是否可由 PM / 独立评审复跑。

协审角色必须重点检查：

- 权限范围、动作、训练许可、外部发送和敏感等级不能被静默扩大或改写。
- 父 authorization generation、version、audit / outbox 的语义没有被绕开。
- R-0044 / R-0046 仍不得由执行会话关闭。
- 未触碰真实数据、真实 Vault、真实文件或真实 Tauri / IPC。

## 核心问题

- 11 个 P3-039 P1 是否全部关闭？
- 状态翻转绕过是否关闭；如未关闭，是否正确报告 Blocked？
- OLD / NEW 父状态双向改绑是否均受保护？
- 合法非 active 清理与新版本激活是否仍通过？
- P3-031 与 P3-040 回归统计、退出码是什么？
- 是否存在任何 P0 / P1 / Not Implemented / Unknown？
- 是否建议进入后续隔离独立复评？
- 哪些内容仍不得外推为风险关闭、Schema / API 冻结、真实 DB / Tauri 验证或下一阶段准入？

## 交付物

完整报告路径：

`lifeos/deliverables/LIFEOS-P3-040_active_authorization_child_mutation_p1_remediation_and_regression.md`

Evidence manifest 路径：

`lifeos/engineering/LIFEOS-P3-040/evidence/MANIFEST.md`

交付物必须包括：

- 任务信息和授权边界
- 实际修改文件
- 11 个 P1 逐项整改映射
- 状态翻转与双向改绑处理
- 合法维护 / 清理 / 新版本路径
- P3-031 与 P3-040 回归统计及退出码
- P0 / P1 / P2 / Not Implemented / Unknown
- 修改前后稳定 hash 与运行输出 hash
- P3-039 原始 evidence 保留证明
- 风险、阻塞与不可外推声明
- 是否建议进入独立复评

Evidence manifest 至少包括：授权范围、文件清单、稳定输入 hash、修改前后 hash、准确命令、环境、退出码、测试统计、11 个 P1 与新增状态翻转测试路径、P3-039 evidence 保留声明和不可外推声明。

## 验收标准

- 报告和 evidence manifest 已保存到指定路径。
- 11 个 P1 均有 SQL / trigger 整改与可复核回归，不得只改测试口径。
- 已覆盖 OLD / NEW 父状态双向改绑、INSERT OR REPLACE 和状态翻转逃逸。
- 合法非 active 清理与新版本激活路径未回退。
- P3-031 与 P3-040 均无 P0 / P1 / Not Implemented / Unknown。
- P3-039 原始 evidence 未被修改。
- 未触碰真实 DB / Vault / Tauri / IPC / 真实文件。
- 若状态翻转无法安全解决，已明确标记 Blocked 并保留失败 evidence，而不是宣称通过。
- 已完成本地预检并提供路径，或说明允许跳过原因。
- 聊天回复只输出摘要、交付物路径、evidence 路径、本地预检路径和是否需要 PM 决策。

## 限制条件

- 不修改 P3-037 / P3-038 / P3-039 原始交付物、评审、PM Review 或 evidence。
- 不修改 PM 账本。
- 不处理真实用户 DB、Vault、文件、敏感数据或 Tauri / IPC。
- 不启用云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040 / R-0043 / R-0044 / R-0046，不关闭或重新打开 R-0045。
- 不冻结 Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线。
- 不启动后续任务，不进入下一阶段。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

聊天回复不要粘贴完整报告或测试日志，只输出摘要、交付物路径、evidence manifest 路径、本地预检路径和是否需要 PM 决策。
