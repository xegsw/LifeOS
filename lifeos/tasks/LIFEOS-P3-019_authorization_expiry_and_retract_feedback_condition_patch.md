# LIFEOS-P3-019 P1-7 条件补丁：授权 expires_at 与 retract_feedback

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程补丁会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-019
- 任务名称：P1-7 条件补丁：授权 `expires_at` 与 `retract_feedback`
- 优先级：P1
- 任务类型：P3 Engineering Fast Lane / 补丁 / 条件整改型任务 / 工程硬化 / 回归测试
- 建议篇幅：800-1500 字；详细日志写入 evidence，不粘贴到报告正文
- 是否适用 P3 Engineering Fast Lane：Yes
- 推荐执行 Agent：Codex
- 推荐理由：本任务是 P3-009 受控工程目录内的窄范围工程补丁，需要修改 TypeScript 代码、补测试、复跑验证并更新 evidence，更适合工程执行型 Agent
- 是否需要后续独立评审：No；若 PM 验收发现 P0、范围扩张、真实时间/调度能力、真实数据能力或权限 / 撤回边界被改写，再退出快车道并另行安排
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-7 授权过期、P1-7 反馈撤回、P1-6 restore candidates 回归、P1-8 suggestion ID 回归、P1-4 staling 回归、P3-015 suggest 旧候选消费门回归、P1-3 / P1-5 回归、H1-H9 / T-ARCH 回归、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

P3-014 独立工程复评记录了 P1-7 未迁移：授权 `expires_at` 与 `retract_feedback`。经过 P3-015 至 P3-018，P3-009 已在合成、单进程、受控测试包边界内补齐：

- `suggest()` 旧候选返回前的完整输入消费门重检。
- Artifact / Source generation mismatch 主动 staling。
- suggestion ID 对完整可消费输入集合与双级 generation 的稳定绑定。
- 受控内存导出包的最小权威投影、restore candidates 与旧包不复活。

当前剩余 P1-7 关注两个用户掌控感问题：

1. 授权不是永久空白支票。若授权存在有效期，过期后所有消费入口必须 fail closed。
2. 用户对 AI 派生的确认 / 纠正不是不可撤回背书。用户应能显式撤回反馈，撤回后该反馈不得继续支撑“已确认”状态或后续 AI 建议。

本任务只做合成、单进程、受控测试包内的 P1-7 最小补丁。它不实现真实时间服务、后台调度、真实审计系统或真实 UI；不关闭 R-0040，不恢复 / 冻结新的工程基线，不启用真实能力。

## 目标

本任务完成后，需要回答：

- Authorization 是否支持最小 `expires_at` 或等价字段，并在所有消费入口中被一致检查？
- 已过期授权是否会阻断 `read`、`search`、`recovery`、`suggest`、`feedback`、`exportMemory`、`restoreCandidates`、`createImportantLink` 等已实现入口？
- 未设置过期时间的既有授权是否保持当前非过期行为？
- 未来过期时间的授权是否在确定性测试时间内仍可放行？
- 用户是否可以显式撤回已存在的 feedback？
- 被撤回的 feedback 是否不再作为有效确认 / 纠正依据，不会复活或支撑旧 Derivation？
- 撤回 feedback 是否保留记录 / 状态，而不是静默删除用户历史？
- 原有 30 项 P3-009 测试是否继续通过，并新增 P1-7 回归测试？
- evidence manifest、test_results、test_run.log、矩阵文件是否更新且一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/store.ts` 中与 Authorization、Feedback schema / 写入 / 查询相关的最小必要代码。
- 修改 `lifeos/engineering/LIFEOS-P3-009/src/consumption-gate.ts` 中与授权过期判断相关的最小必要代码。
- 修改 `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` 中与已实现消费入口、feedback 撤回或测试辅助 API 相关的最小必要代码。
- 如确有必要，可修改 `lifeos/engineering/LIFEOS-P3-009/src/types.ts`，但必须说明原因，并保持最小改动。
- 可以新增受控、显式的方法，例如 `retractFeedback(...)` 或等价命名；该方法必须代表用户显式撤回，不得由 AI 自动触发。
- 可以为消费门引入确定性测试时钟或可注入 `now` 参数；测试不得依赖真实系统时间造成 flaky 结果。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`，新增 P1-7 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限同步新增测试统计、snapshot 和 evidence 内容。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程快车道短报告：`lifeos/deliverables/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 实现真实时间服务、后台调度器、系统通知、定时扫描、真实审计系统或真实 UI。
- 把 `expires_at` 设计成生产 SLA、同步协议、真实多设备一致性或正式权限策略语言。
- 让 AI 自动撤回用户 feedback，或用撤回替代用户明确确认。
- 静默删除原 feedback 记录；不得破坏用户原文或用户历史。
- 顺手处理 `INSERT OR REPLACE`、自引用 Link、夹具多样性、真实 IPC、真实 Vault、P2 清洁项或其它非 P1-7 问题，除非为 feedback 撤回语义直接必要且必须在报告中说明。
- 接入真实 Tauri / IPC、真实 Obsidian Vault、真实文件路径、真实用户数据、真实云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 自行关闭 R-0040 或新增 / 关闭风险。
- 自行启动后续任务。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- `lifeos/deliverables/LIFEOS-P3-018_restore_candidates_authority_projection_non_revival_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-018_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 对 P3-014 只需定向读取 P1-7 未迁移项和 P1-3 至 P1-8 状态清单。
- 对 P3-018 只需定向读取当前已通过的 30 项回归边界、P1-6 非范围与后续 P1-7 建议。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0163 至 D-0170 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 授权过期字段：
   - Authorization 必须支持最小 `expires_at`、`expires_at_ms` 或等价字段。
   - 未设置过期时间的既有授权应保持非过期行为。
   - 已过期授权必须 fail closed；不得被解释成 allow。
   - 测试必须使用确定性时间；不得依赖真实系统当前时间。
2. 消费入口一致性：
   - 已过期授权必须阻断 `read`。
   - 已过期授权必须阻断 `search`。
   - 已过期授权必须阻断 `recovery`。
   - 已过期授权必须阻断 `suggest`。
   - 已过期授权必须阻断 `feedback`。
   - 已过期授权必须阻断 `exportMemory`。
   - 已过期授权必须阻断 `restoreCandidates` 或等价恢复候选评估。
   - 已过期授权必须阻断 `createImportantLink`。
3. Feedback 显式撤回：
   - 新增或补齐 `retract_feedback` / `retractFeedback` 语义。
   - 撤回必须是用户显式动作，不得由 AI 自动触发。
   - 撤回后 feedback 状态应变为 `retracted` 或等价状态；不得静默删除。
   - 重复撤回应幂等。
   - 被撤回的确认 / 纠正不得继续作为有效确认 / 纠正依据。
   - 若当前实现通过 Derivation status 表达用户确认，撤回必须同步处理该状态，避免只有已撤回 feedback 却仍把 Derivation 当作用户确认事实。
4. 不复活与不越权：
   - 撤回 feedback 不得复活 stale / invalid / 权限失效的 Derivation。
   - 权限过期后不得写入新的 active feedback。
   - 权限过期后旧 Derivation 不得通过 `suggest`、`exportMemory` 或 `restoreCandidates` 回到可用候选。
5. 原有回归：
   - P1-6 restore candidates、权威投影与旧包不复活测试继续通过。
   - P1-8 suggestion ID 完整 generation 绑定测试继续通过。
   - P1-4 generation mismatch staling 测试继续通过。
   - P3-015 direct-deny 测试继续通过。
   - P1-3 / P1-5 测试继续通过。
   - P3-011 P0 消费门测试继续通过。
   - H1-H9 / T-ARCH 继续通过。
6. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
7. 输出工程快车道短报告：
   - `lifeos/deliverables/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`

## 非范围

本任务暂时不要做：

- 不实现真实时间服务、后台调度、过期扫描任务、系统通知或自动清理任务。
- 不实现真实 UI、真实撤回按钮、真实审计页面或用户设置页。
- 不实现正式权限策略语言、多设备授权同步、生产级过期 SLA 或服务端权威时间。
- 不实现正式导出 / 导入 / 备份恢复、真实文件写入或路径权限。
- 不改变 P1-6 restore candidates 的只读候选性质。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码补上授权过期与 feedback 撤回？
- 过期判断是否进入统一消费门，而不是只在单个入口临时判断？
- feedback 撤回是否幂等、显式、不会删除用户历史？
- 原有 30 项测试和新增 P1-7 测试是否全部可复跑？

数据与权限负责人必须重点检查：

- `expires_at` 是否被视为 Authorization 当前有效性的组成部分？
- 过期授权是否在所有已实现消费入口 fail closed？
- 撤回 feedback 是否保留来源与状态，不混淆用户原文、AI 派生和用户确认？

AI 信任与安全负责人必须重点检查：

- 撤回后 AI 不得继续把该 feedback 当作用户背书。
- 过期授权下 AI suggestion、export、restore candidates 不得返回旧可用建议。
- AI 不得自动撤回用户反馈或静默改写用户原文。

QA / 测试负责人必须重点检查：

- 测试是否覆盖过期前、过期后、未设置过期时间三类授权状态？
- 测试是否覆盖所有已实现消费入口？
- 测试是否覆盖 feedback 撤回、重复撤回、撤回后不复活和过期后不能写 feedback？
- evidence 是否与实际测试结果一致？

技术架构负责人必须重点检查：

- 是否没有新增外部依赖或真实时间 / 调度系统？
- 是否没有冻结正式权限策略、Schema / API 或生产 SLA？
- 是否没有启用真实 Tauri / IPC、真实 Vault、真实文件导出或其它关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程快车道短报告保存为：

`lifeos/deliverables/LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch.md`

报告建议使用：

`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P1-7 条件关闭说明
- 授权 `expires_at` 设计说明
- `retract_feedback` 设计说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- R-0040 未关闭声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- Authorization 支持最小过期字段，且未设置过期时间时保持原有行为。
- 已过期授权在所有已实现消费入口 fail closed。
- 过期前授权在确定性测试时间下仍可正常放行。
- feedback 可由用户显式撤回，撤回不删除历史。
- feedback 撤回幂等。
- 被撤回 feedback 不再作为有效用户确认 / 纠正依据。
- 撤回 feedback 不复活 stale / invalid / 权限失效 Derivation。
- 权限过期后不能写入新的 active feedback。
- 原有 30 项 P3-009 测试继续通过。
- 新增 P1-7 回归测试通过。
- P0 失败数为 0。
- Evidence manifest 与测试结果一致。
- 未修改 P3-001。
- 未修改项目账本。
- 未启用真实能力。
- 已生成指定工程快车道短报告。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 交付物路径
- evidence manifest 路径
- 测试摘要
- 是否需要 PM 决策

不要修改项目账本，不要自行宣布工程基线扩展完成，不要关闭 R-0040，不要自行启动后续任务。
