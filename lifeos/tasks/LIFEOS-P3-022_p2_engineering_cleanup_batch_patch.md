# LIFEOS-P3-022 P2 工程清洁项 Batch Patch 任务卡

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- 本任务需要的相关模板

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-022
- 任务名称：P2 工程清洁项 Batch Patch：feedback 覆盖语义、validate 分级统计、Derivation 主证据字段去混淆
- 优先级：P2
- 任务类型：P3 Engineering Fast Lane / P2 工程补丁 / Batch Patch
- 建议篇幅：800-1500 字
- 是否适用 P3 Engineering Fast Lane：Yes
- 推荐执行 Agent：Codex
- 推荐理由：本任务是 P3-009 受控工程目录内的窄范围代码、测试与 evidence 清洁项，适合由 Codex 快速实现、复跑并整理证据。
- 是否需要后续独立评审：No；若发现 P0、改变权限 / 删除 / 导出 / AI 建议可信度核心边界，或需要恢复 / 冻结工程基线，则退出快车道并回到 PM。
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-009/`。
- 是否允许修改项目账本：No。
- 主责角色：Technical Architect / QA Engineer
- 协审角色：Data Trust Reviewer / AI Trust Reviewer
- 必须通过的评审关卡：
  - Gate 2 数据与来源评审（受控工程层）
  - Gate 3 AI 权限与信任评审（受控反馈 / 建议身份层）
  - Gate 4 技术可行性评审（受控工程实现层）
- 状态：Ready

## 背景

`LIFEOS-P3-020` 已确认 P3-009 的 P1-3 至 P1-8 在合成、单进程、受控测试包边界内完成迁移，并记录 34 PASS / 0 FAIL 与 63 条独立反例攻击通过。PM Review 同时留下 3 个不阻塞 R-0040 关闭条件评估的 P2 清洁项：

1. `feedback()` 使用 `INSERT OR REPLACE`，存在静默覆盖用户反馈内容或状态的表达风险。
2. `scripts/validate.mjs` 当前将所有失败计入 `p0_fail`，P0 统计粒度过粗。
3. `derivation.evidence_version_id` 作为历史兼容 / 主证据字段，容易与完整 `derivation_input` 输入集合混淆。

P3-021 已由 PM 验收，用户已确认采纳其建议：`R-0040` 继续保持 Open / Conditional，当前不关闭、不拆分。本任务只处理受控 P2 工程清洁项，不改变该风险状态。

## 目标

本任务完成后，需要让 P3-009 受控工程包在以下三点上更干净、更不易误读：

- 用户反馈不会被同 ID 的后续写入静默覆盖或复活。
- 验证脚本能区分总失败与 P0 / P1 / P2 失败统计。
- Derivation 的“主证据 / 兼容字段”与“完整输入集合”在代码、返回结构、导出投影或 evidence 文档中表达清楚。

## Batch Patch 问题清单

| 问题 ID | 严重级别 | 修复边界 | 对应测试 | 是否触发独立复评 | 是否触发用户确认 |
|---|---|---|---|---|---|
| P2-CLEAN-1 | P2 | `feedback()` 不得使用静默覆盖语义；重复反馈必须保留原记录或 fail closed，不得覆盖 user_text / status，不得复活 retracted feedback | 新增重复 feedback / 冲突 feedback / retracted feedback 不复活测试 | No，除非发现 P0 | No |
| P2-CLEAN-2 | P2 | `validate.mjs` 分离 total_fail 与 p0_fail / p1_fail / p2_fail；保留任意失败时非零退出；更新 evidence summary / MANIFEST | 复跑验证脚本，检查 `test_results.json` 与 `MANIFEST.md` 字段清楚 | No，除非统计异常掩盖 P0 | No |
| P2-CLEAN-3 | P2 | 降低 `derivation.evidence_version_id` 与完整 `derivation_input` 的语义混淆；可保留 DB 兼容字段，但对外 / evidence 应明确其为 primary / legacy，而完整输入集合才是授权与恢复依据 | 新增或调整测试，确认多输入 Derivation 的完整 inputs 仍是消费 / 导出 / restore 判断依据 | No，除非改变核心消费门语义 | No |

## 范围

本任务必须覆盖：

- 仅在 `lifeos/engineering/LIFEOS-P3-009/` 内做最小必要修改。
- 修改 `feedback()` 写入语义，避免 `INSERT OR REPLACE` 静默覆盖用户反馈。
- 补充测试证明：
  - 同 ID 重复 feedback 不覆盖原 user_text。
  - 同 ID 冲突 feedback 不静默替换原记录。
  - 已撤回 feedback 不会因重复 feedback 写入而恢复为 active。
- 修改 `scripts/validate.mjs`：
  - `fail` / `total_fail` 表示全部失败。
  - `p0_fail` 只统计失败标题以 `P0` 开头的测试。
  - 如可行，补充 `p1_fail`、`p2_fail`。
  - 任意测试失败时仍必须让验证命令退出非零。
  - `summary.task` 更新为 `LIFEOS-P3-022`。
- 降低 `derivation.evidence_version_id` 语义混淆：
  - 若保留数据库字段，必须在代码返回结构、authority projection 或 evidence 中明确它是 primary / legacy / compatibility field。
  - 完整 `derivation_input` / `inputs` 必须继续作为消费门、导出、恢复候选和证据链判断的权威依据。
  - 不得把多证据 Derivation 退化为单主证据判断。
- 复跑：
  - `cd lifeos/engineering/LIFEOS-P3-009 && node scripts/validate.mjs`
  - 如需要，也可直接复跑 `node --experimental-strip-types --test tests/invariants.test.ts`
- 更新 `lifeos/engineering/LIFEOS-P3-009/evidence/` 下相关 evidence 文件。
- 输出短报告到指定交付物路径。

## 非范围

本任务暂时不要做：

- 不修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 不修改 PM 账本、风险账本、冻结看板或开放问题。
- 不关闭 `R-0040`，不拆分 `R-0040`。
- 不恢复或冻结工程基线扩展。
- 不进入下一阶段。
- 不启用真实 Tauri / IPC、真实 Vault、真实数据、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不改变产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界。
- 不重构生产 Schema、API、真实导出格式、真实 Tauri capability 或平台打包配置。
- 不把本任务结果写成正式工程基线冻结、真实能力准入或生产 SLA 通过。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/reviews/LIFEOS-P3-020_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-021_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/README.md`
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/store.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0173 至 D-0176 附近相关内容。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 若发现上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 交付物正文按 P3 快车道短报告控制；详细日志写入 evidence，不粘贴到报告正文。
- 聊天回复只输出摘要、交付物路径、evidence 路径、是否需要 PM 决策。
- 交付物完成后，默认调用本地预检：`python3 lifeos/tools/local_precheck.py <交付物路径>`。

## 角色检查点

主责角色必须重点回答：

- 本任务是否只修复 P2 清洁项，没有改变核心权限 / 删除 / 导出 / AI 建议可信度边界。
- 新增测试是否能证明三项清洁目标成立。
- evidence 是否能让 PM 快速复跑和核对。

协审角色必须重点检查：

- Data Trust Reviewer：反馈历史是否被保留，用户反馈不会被静默改写或复活。
- AI Trust Reviewer：Derivation 主证据字段不会误导 AI 建议的证据身份；完整输入集合仍是权威。
- QA Reviewer：验证脚本失败分级不会掩盖 P0，也不会把所有失败误计为 P0。

## 核心问题

请重点回答：

- P2-CLEAN-1 / 2 / 3 是否全部完成？
- 新增 / 修改了哪些测试？
- 验证命令结果是什么？PASS / FAIL / P0 失败数分别是多少？
- evidence manifest 路径是什么？
- 是否触发任何 P0、风险关闭、工程基线恢复、真实能力启用或用户确认事项？
- 是否建议后续独立复评？

## 交付物

请将完整短报告保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P3-022_p2_engineering_cleanup_batch_patch.md`

请使用：

`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`

Evidence manifest 路径应为：

`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`

篇幅控制：

- P3 快车道短报告建议 800-1500 字。
- 不粘贴完整测试日志；完整日志写入 evidence。
- 超出任务范围的分析、方案或问题，放入“后续任务建议”，不要展开。

## 验收标准

只有满足以下条件，任务才算完成：

- P2-CLEAN-1 / 2 / 3 均有明确处理结论。
- `feedback()` 不再静默覆盖用户反馈内容或状态。
- 验证脚本能区分总失败与 P0 / P1 / P2 失败统计，且任意失败仍非零退出。
- Derivation 主证据 / 兼容字段与完整输入集合的语义被清楚表达，完整输入集合仍是授权与恢复依据。
- 新增或调整的测试覆盖三项清洁目标。
- `node scripts/validate.mjs` 已复跑并刷新 evidence。
- 完整短报告已保存为指定路径。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过原因。
- 会话回复中提供交付物路径与 evidence manifest 路径。
- 明确说明未关闭 R-0040、未恢复 / 冻结工程基线、未启用真实能力、未进入下一阶段。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改 Stitch。
- 不修改 PM 账本或风险账本。
- 不关闭、拆分或降级 `R-0040`。
- 不启用真实 Tauri / IPC、真实 Vault、真实数据、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不自行启动后续任务。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整报告或测试日志，只输出摘要、交付物路径、evidence 路径、预检路径和是否需要 PM 决策。
