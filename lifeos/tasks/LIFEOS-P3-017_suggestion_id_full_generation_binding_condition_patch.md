# LIFEOS-P3-017 P1-8 条件补丁：suggestion ID 完整 generation 绑定

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程补丁会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-017
- 任务名称：P1-8 条件补丁：suggestion ID 完整 generation 绑定
- 优先级：P1
- 任务类型：P3 Engineering Fast Lane / 补丁 / 条件整改型任务 / 工程硬化 / 回归测试
- 建议篇幅：800-1500 字；详细日志写入 evidence，不粘贴到报告正文
- 是否适用 P3 Engineering Fast Lane：Yes
- 推荐执行 Agent：Codex
- 推荐理由：本任务是 P3-009 受控工程目录内的窄范围工程补丁，需要修改 TypeScript 代码、补充回归测试、复跑验证并更新 evidence，更适合工程执行型 Agent
- 是否需要后续独立评审：No；若 PM 验收发现 P0、范围扩张或触及真实能力，再退出快车道并另行安排
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：数据与权限负责人、AI 信任与安全负责人、QA / 测试负责人、技术架构负责人
- 必须通过的评审关卡：P1-8 suggestion ID 完整 generation 绑定、P1-4 staling 回归、P3-015 suggest 旧候选消费门回归、P1-3 / P1-5 回归、H1-H9 / T-ARCH 回归、evidence manifest 更新、默认关闭能力回归
- 状态：Ready

## 背景

`LIFEOS-P3-014` 独立工程复评记录了 P1-8 未迁移：当前 `suggest()` 的 suggestion ID 仍存在基于单一主证据生成的倾向。P3-013 已经让 Derivation 记录完整多证据输入集合，P3-015 已补强旧 suggestion 返回前的输入消费门重检，P3-016 已补上 generation mismatch 主动 staling。

但如果 suggestion ID 本身仍主要绑定首个输入，就可能出现语义不清：同一个 Project 下，多证据集合、非主证据 generation、source generation 或输入集合变化时，系统可能复用一个看起来“相同”的 suggestion ID。长期外脑里，这会削弱 AI 建议的可追溯性：用户看到的是一个 AI 建议，但它究竟依据哪一组原文、哪一代来源、哪一组证据生成，不应只靠后续消费门兜底。

本任务只补 P1-8：让 suggestion ID 与完整可消费输入集合及其 generation 快照绑定。不迁移 P1-6 / P1-7，不关闭 R-0040，不启用真实能力。

## 目标

本任务完成后，需要回答：

- `suggest()` 新建候选时，suggestion ID 是否由完整可消费输入集合决定，而不是只由首个 / 主证据决定？
- ID 是否包含或等价绑定 Project、每个输入的 evidence version、artifact、source、artifact generation、source generation？
- 同一组可消费输入在不同 evidence 顺序下，是否得到同一个稳定 ID？
- 任一非主输入 artifact generation 或 source generation 变化后，是否不会继续复用旧 suggestion ID？
- 已存在旧 suggestion 是否仍被 P3-015 / P3-016 机制正确阻断或 stale？
- 原有 21 项 P3-009 测试是否继续通过，并新增 P1-8 回归测试？
- evidence manifest、test_results、test_run.log、矩阵文件是否更新且一致？

## 授权范围

允许：

- 修改 `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` 中与 suggestion ID 生成、稳定排序、完整 generation 绑定相关的最小必要代码。
- 如确有必要，可修改 `lifeos/engineering/LIFEOS-P3-009/src/store.ts`、`src/types.ts` 或新增极小工具函数，但必须说明原因，并保持最小改动。
- 可使用 Node.js 内置能力实现确定性 ID，例如稳定字符串或内置 hash；不得新增外部依赖。
- 修改 `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`，新增 P1-8 回归测试。
- 修改 `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`，仅限同步新增测试统计、snapshot 和 evidence 内容。
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 中由验证脚本生成或需要同步的 evidence 文件。
- 创建工程快车道短报告：`lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`。
- 运行 P3-009 测试和验证脚本。
- 调用本地预检检查交付报告。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、PRD、冻结资产或项目背景包。
- 迁移 P1-6 restore candidates、权威投影与旧包不复活。
- 迁移 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 顺手重构 `feedback()` 的 `INSERT OR REPLACE`、导出格式、恢复包格式、自引用 Link、夹具多样性或其它 P2 清洁项。
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
- `lifeos/deliverables/LIFEOS-P3-015_suggest_existing_derivation_consumption_gate_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-016_generation_mismatch_staling_condition_patch.md`
- `lifeos/reviews/LIFEOS-P3-016_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖材料；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0160 至 D-0166 及最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 完整 ID 绑定实现：
   - suggestion ID 必须由 Project 与完整可消费输入集合稳定生成。
   - 每个输入至少要等价绑定：`evidence_version_id` / `version_id`、`artifact_id`、`source_id`、`artifact_generation`、`source_generation`。
   - 输入集合必须稳定排序，避免同一组 evidence 因顺序不同生成不同 ID。
   - ID 生成不得只依赖首个输入、主证据、`artifact_generation ?? 1` fallback 或单一 version。
2. 与既有机制兼容：
   - P3-015 的旧 suggestion 返回前输入消费门重检继续有效。
   - P3-016 的 generation mismatch 主动 staling 继续有效。
   - 已确认 suggestion 的重复调用应继续保留确认和反馈追踪，不被静默重置为 candidate。
3. 新增回归测试：
   - 同一 Project、同一完整 evidence 集合，不同输入顺序下 ID 相同。
   - 非主输入 artifact generation 变化后，新 suggestion 不复用旧 ID，旧 Derivation 不可被继续消费。
   - 非主输入 source generation 变化后，新 suggestion 不复用旧 ID，旧 Derivation 不可被继续消费。
   - 多证据输入集合变化时，ID 变化或明确 fail closed；不得假装仍是同一个建议。
4. 原有回归：
   - P1-4 generation mismatch staling 测试继续通过。
   - P3-015 direct-deny 测试继续通过。
   - P1-3 / P1-5 测试继续通过。
   - P3-011 P0 消费门测试继续通过。
   - H1-H9 / T-ARCH 继续通过。
5. Evidence 更新：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - `test_results.json`
   - `test_run.log`
   - `invariant_migration_matrix.md`
   - `architecture_conformance.md`
   - 如默认关闭矩阵无变化，也需确认未被破坏。
6. 输出工程快车道短报告：
   - `lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`

## 非范围

本任务暂时不要做：

- 不迁移 P1-6 restore_candidates、权威投影与旧包不复活。
- 不迁移 P1-7 授权 `expires_at` 与 `retract_feedback`。
- 不把 P1-8 扩展成正式 AI 生成策略、真实模型调用、语义去重或推荐排序系统。
- 不改造导出格式、恢复包格式、真实文件导出或真实备份。
- 不迁移 P3-001 的全部 23 项测试 / 136 条断言。
- 不接入真实 Tauri / IPC。
- 不接入真实 Obsidian Vault。
- 不处理真实数据或真实系统路径。
- 不冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线扩展。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 是否用最小代码让 suggestion ID 绑定完整输入集合？
- 是否没有顺手迁移 P1-6 / P1-7 或其它清洁项？
- 原有 21 项测试和新增 P1-8 测试是否全部可复跑？

数据与权限负责人必须重点检查：

- suggestion ID 是否能追溯到完整 evidence version、artifact、source 与双级 generation？
- 是否覆盖非主输入 generation 变化，而不是只覆盖主证据？
- 是否仍以完整 `derivation_input` 语义为准，而不是绕过 P1-3 迁移成果？

AI 信任与安全负责人必须重点检查：

- 用户看到的 AI suggestion 是否不会在证据集合变化后被静默冒充为同一建议？
- 旧 AI suggestion 是否仍由 P3-015 / P3-016 阻断或 stale？
- 是否保持用户原文、AI 建议、用户反馈和外部来源身份分离？

QA / 测试负责人必须重点检查：

- 测试是否验证顺序稳定性、非主输入 generation 变化和输入集合变化？
- 测试是否能证明 ID 不再只绑定首个输入？
- evidence 是否与实际测试结果一致？

技术架构负责人必须重点检查：

- 是否没有新增外部依赖或引入重型架构？
- 是否没有冻结生产 Schema / API / 模块边界？
- 是否没有启用真实 Tauri / IPC 或其它关闭能力？
- R-0040 是否保持 Open / Conditional？

## 交付物格式

请将完整工程快车道短报告保存为：

`lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`

报告建议使用：

`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

报告必须包含：

- 任务摘要
- 修改文件清单
- P1-8 条件关闭说明
- 新增 / 修改测试清单
- 测试命令与结果摘要
- Evidence 更新清单
- 未启用真实能力声明
- P1-6 / P1-7 仍未迁移声明
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、测试摘要、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- suggestion ID 由完整可消费输入集合稳定生成。
- ID 等价绑定 Project、每个输入的 evidence version、artifact、source、artifact generation、source generation。
- 同一输入集合不同顺序下 ID 相同。
- 非主输入 artifact generation 变化后不复用旧 ID。
- 非主输入 source generation 变化后不复用旧 ID。
- 旧 suggestion 仍会被 P3-015 / P3-016 机制阻断或 stale。
- 已确认 suggestion 的重复调用不静默重置状态或反馈。
- 原有 21 项 P3-009 测试继续通过。
- 新增 P1-8 回归测试通过。
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
