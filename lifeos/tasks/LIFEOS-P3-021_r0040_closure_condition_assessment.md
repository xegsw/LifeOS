# LIFEOS-P3-021 R-0040 关闭条件评估任务卡

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- 本任务需要的相关模板

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-021
- 任务名称：R-0040 关闭条件评估
- 优先级：P0
- 任务类型：评审型 / 决策输入型 / 风险关闭条件评估
- 建议篇幅：2000-4000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务涉及高风险项 R-0040 是否可关闭，必须保持只读、独立、反例优先的评估视角，不应由刚完成工程补丁链路的执行会话自证。
- 是否需要后续独立评审：本任务自身为独立风险评估；若建议关闭 R-0040，仍需 PM 主会话验收与用户确认。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：Security Reviewer / Risk Owner
- 协审角色：Technical Architect / Data Trust Reviewer / QA Reviewer
- 必须通过的评审关卡：
  - Gate 2 数据与来源评审
  - Gate 3 AI 权限与信任评审
  - Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P3-020` 已独立复评 P3-009 的 P1-3 至 P1-8 迁移完成候选，结论为 Pass with Conditions：在合成数据、单进程、受控测试包边界内，P1 迁移已完成，未发现 P0 / P1。

但 `R-0040` 的原始风险不是普通单进程领域逻辑漏洞，而是 Tauri capability / IPC command / path scope / Renderer 调用链路配置不当时，可能绕过领域授权、读写非授权文件或写回 Vault 的高风险项。P2-015 已验证“后端等价安全合同”，P3-009 至 P3-020 已验证“受控工程包内的领域门禁与不变量”，二者仍不等同于真实 Tauri / IPC 集成已安全。

因此本任务用于评估：在当前有限 Stage 3 边界下，`R-0040` 是否具备关闭条件、是否只能窄范围关闭、是否应继续保持 Open / Conditional，或是否需要拆分为“受控后端门禁已验证”和“真实 Tauri 集成仍待验证”两个风险条目。

## 目标

本任务完成后，需要为 PM 主会话提供一个明确、可执行的风险判断输入：

- `R-0040` 当前是否可以关闭？
- 如果可以，只能关闭到什么边界？
- 如果不能关闭，阻塞证据是什么？
- 是否建议拆分风险？
- 关闭、保持、拆分三种选择各自对后续 P3 工程推进意味着什么？

## 范围

本任务必须覆盖：

- 核对 `R-0040` 在 `lifeos/RISK_LOG.md` 中的原始定义、当前状态、关闭条件和触发条件。
- 区分三类证据边界：
  - P2-015：Tauri / IPC 后端等价安全合同与窄测结果。
  - P2-016 / P2-018 / P2-019：技术架构冻结合同、有限 Stage 3 准入与最小纵向切片能力启用门。
  - P3-009 至 P3-020：合成、单进程、受控测试包内的领域门禁、消费门、证据链和 P1 迁移覆盖。
- 评估当前 Stage 3 是否仍满足以下安全边界：
  - 不启用真实 Tauri / IPC。
  - 不连接真实 Vault。
  - 不处理真实数据。
  - 不执行真实文件导出或路径扩权。
  - 不调用云 / 第三方模型、同步、多设备、L3 或外部用户能力。
- 判断 P3-020 的 Pass with Conditions 能否支持：
  - 关闭 `R-0040`；
  - 保持 `R-0040` Open / Conditional；
  - 或拆分 `R-0040`。
- 如建议关闭或拆分，必须给出：
  - 精确适用范围；
  - 失效条件；
  - 未来重新打开或新建风险的触发器；
  - 必须回到 PM / 用户确认的事项。
- 如建议继续保持 Open / Conditional，必须给出：
  - 当前缺口；
  - 进入真实 Tauri / IPC 前必须补充的验证任务；
  - 允许继续做哪些受控工程任务。

## 非范围

本任务暂时不要做：

- 不关闭 `R-0040`。
- 不修改 `lifeos/RISK_LOG.md`、`lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md` 或任何项目账本。
- 不恢复或冻结新的工程基线。
- 不修改任何工程代码、测试代码、脚本或 evidence 文件。
- 不启用真实 Tauri / IPC、真实 Vault、真实数据、真实文件导出、云 / 第三方模型、同步、多设备、L3 或外部用户能力。
- 不重新评审产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界。
- 不把当前评估结论写成“已关闭风险”“已准入真实能力”或“已进入下一阶段”。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/RISK_LOG.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/tasks/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike.md`
- `lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/reviews/LIFEOS-P2-016_pm_review.md`
- `lifeos/reviews/LIFEOS-P2-018_mvp_development_entry_independent_review.md`
- `lifeos/reviews/LIFEOS-P2-018_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/reviews/LIFEOS-P2-019_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-020_p1_migration_completion_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-020_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品方向或阶段判断冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0120、D-0121、D-0123、D-0127、D-0131、D-0149、D-0157、D-0173、D-0174 附近相关内容。
- 若发现上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 交付物正文按评审型任务篇幅控制；超出范围的内容放入“后续任务建议”。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。
- 交付物完成后，默认调用本地预检：`python3 lifeos/tools/local_precheck.py <交付物路径>`。
- 本地预检只用于摘要、覆盖检查、风险抽取和模板完整性检查；不得替代独立评估结论、PM 验收或用户确认。

## 角色检查点

主责角色必须重点回答：

- `R-0040` 的原始风险是否已经被当前证据真正覆盖，还是只被受控后端 / 领域逻辑证据部分覆盖。
- 若关闭，关闭范围是否足够窄，不会被误读为真实 Tauri / IPC 安全通过。
- 若不关闭，必须补什么证据，而不是泛泛说“以后再测”。

协审角色必须重点检查：

- Technical Architect：技术架构 V0.1 合同中“不冻结真实 Tauri capability / IPC 签名 / 平台配置”的边界是否被严格继承。
- Data Trust Reviewer：用户数据、Vault、导出、写回、来源和证据链是否仍处于默认关闭或受控合成边界。
- QA Reviewer：P3-020 的 PASS 证据是否能支撑受控范围判断，是否存在被外推到真实能力的误用风险。

## 核心问题

请重点回答：

- `R-0040` 是否建议关闭？结论必须在以下选项中选择一个：
  - A. 建议关闭；
  - B. 建议保持 Open / Conditional；
  - C. 建议拆分为“受控后端 / 领域门禁风险”和“真实 Tauri / IPC 集成风险”。
- 如果选择 A，必须给出为什么真实 Tauri / IPC 风险也已被足够覆盖；如无法证明，不得选择 A。
- 如果选择 B，必须说明当前 P2-015 / P3-020 已经覆盖了什么、还缺什么、后续工程是否可以继续。
- 如果选择 C，必须给出拆分后的风险名称、边界、关闭条件和触发器建议。
- 当前是否允许继续做 P3 受控工程任务？
- 进入真实 Tauri / IPC、真实 Vault 或真实文件能力前，最低还需要哪些验证？

## 交付物

请将完整评估报告保存为 Markdown 文件，路径：

`lifeos/reviews/LIFEOS-P3-021_r0040_closure_condition_assessment.md`

请输出的文件内容包括：

- 评审信息
- 评估摘要
- 事实依据
- 证据边界拆分
- R-0040 原始风险覆盖判断
- 关闭 / 保持 / 拆分选项评估
- 推荐结论
- 适用范围与失效条件
- 后续验证建议
- 需要 PM / 用户决策
- 风险
- 最终建议

篇幅控制：

- 评审型任务建议 2000-4000 字。
- 超出当前任务范围的分析、方案或问题，放入“后续任务建议”，不要在当前任务正文无限展开。
- 交付物必须完整，但聊天回复必须简短。

## 验收标准

只有满足以下条件，任务才算完成：

- 明确选择 A / B / C 中一个结论。
- 准确区分 P2-015、P2-016 / P2-018 / P2-019、P3-009 至 P3-020 三类证据边界。
- 明确说明当前是否允许关闭 `R-0040`，且不把任务结论自行写成项目账本状态。
- 明确说明是否允许继续 P3 受控工程任务。
- 明确说明真实 Tauri / IPC、真实 Vault、真实文件能力启用前的最低验证要求。
- 完整评估报告已保存为指定文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供评估报告路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确区分事实、推断、建议。
- 列出风险和待确认问题。
- 标记哪些结论需要 PM 主会话确认。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不改变 V1 范围。
- 不改变技术架构 V0.1 冻结合同。
- 不修改核心领域模型或 AI 权限边界。
- 不修改任何项目账本或风险账本。
- 不关闭 `R-0040`。
- 不恢复或冻结工程基线扩展。
- 不进入下一阶段。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、同步、多设备、L3 或外部用户。
- 不自行启动后续任务；如认为需要新任务，只写入“后续任务建议”。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整评估报告正文，只输出摘要和交付物路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入评估报告文件。
