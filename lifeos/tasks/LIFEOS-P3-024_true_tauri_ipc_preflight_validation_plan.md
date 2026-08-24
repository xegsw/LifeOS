# LIFEOS-P3-024｜真实 Tauri / IPC 集成前置验证任务规划

## 任务信息

- 任务 ID：LIFEOS-P3-024
- 任务名称：真实 Tauri / IPC 集成前置验证任务规划
- 优先级：P0
- 任务类型：技术验证规划 / 决策型任务
- 建议篇幅：1500-2500 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：WorkBuddy
- 推荐理由：本任务涉及 R-0040 的真实集成层风险、能力启用门、debug / release 差异、Renderer / CSP / IPC / capability / path scope 等反例规划，适合独立评审视角先做验证设计，不适合直接由工程实现会话跳进真实集成。
- 是否需要后续独立评审：Conditional（本任务本身只做规划；未来若执行真实 Tauri / IPC 验证并拟关闭 R-0040，必须另行独立复评与用户确认）
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 安全验证规划
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer
- 必须通过的评审关卡：Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session
- 推荐会话类型：WorkBuddy 独立评审 / 风险评估会话
- 推荐复用的会话：若已有执行 `LIFEOS-P3-021` 或 `LIFEOS-P3-023` 的 WorkBuddy 独立风险评估线会话，优先复用；否则新建 WorkBuddy 独立规划会话。
- 会话判断理由：本任务延续 R-0040 与工程基线恢复后的真实能力启用前置验证线，需要保持独立风险视角；不得让工程实现会话直接把规划误写成执行许可。
- 是否需要独立性隔离：Yes，与后续可能执行真实 Tauri / IPC 验证的工程会话隔离。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - 本任务卡明确列出的输入材料
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 可复用既有读取结果：
  - 若同一 WorkBuddy 会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/reviews/LIFEOS-P3-023_pm_review.md`
  - `lifeos/reviews/LIFEOS-P3-021_r0040_closure_condition_assessment.md`
  - `lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- 任务完成后是否建议保留会话：Yes，作为后续 R-0040 / 真实能力启用前置验证线会话保留。

## 背景

用户已确认采纳 P3-023 推荐 B：P3-009 恢复为受控工程基线扩展，但不冻结、不关闭 R-0040、不启用真实能力、不进入下一阶段。当前可以继续受控 Stage 3 工程规划，但真实 Tauri / IPC、真实 Vault、真实文件导出、真实数据等能力仍默认关闭。

R-0040 的核心风险不是 P3-009 单进程领域门，而是真实 Tauri capability、IPC、Renderer / WebView、CSP、plugin、invoke 注册、路径 scope、debug / release 打包与 OS 路径行为可能绕过领域授权门。P2-015 已用等价 harness 验证后端安全合同，但未验证真实 Tauri 集成层。P3-021 明确 R-0040 保持 Open / Conditional，未来真实能力启用前必须单列验证任务。

因此，本任务只规划“未来真实 Tauri / IPC 验证应该怎么做”，不执行真实集成，不写代码，不启用真实能力。

## 目标

本任务完成后，PM 应能清楚判断：

- 未来真实 Tauri / IPC 验证任务应覆盖哪些攻击面。
- P2-015 后端安全合同应如何迁移到真实 Tauri debug / release 与目标平台验证。
- 该验证任务需要哪些夹具、矩阵、证据文件、退出条件和失败处理。
- 哪些内容必须继续默认关闭，不能因规划完成而启用。
- 下一步是否应该创建实际验证任务，还是先补充 Schema / API / UI 壳规划。

## 范围

本任务必须覆盖：

- R-0040 当前风险边界复述：真实 Tauri capability / IPC / path scope 绕过领域授权门。
- P2-015 已验证内容与未验证内容拆分。
- 未来真实 Tauri / IPC 验证任务的最小矩阵设计，至少覆盖：
  - capability / permission 白名单
  - plugin / invoke 注册面
  - Renderer / WebView / CSP
  - debug / release 包差异
  - 目标平台路径行为
  - 合成临时目录 / 模拟 Vault
  - path scope 与文件能力默认关闭
  - IPC 参数校验、项目边界、授权、tombstone、generation、证据重检
  - 禁用能力的负测
- 未来验证任务的 evidence 包结构建议。
- P0 / P1 / P2 判定标准。
- 失败时的关闭 / 降级 / 回滚处理。
- 明确说明本任务是否建议立即创建实际验证任务。

## 非范围

本任务暂时不要做：

- 不安装、配置或运行真实 Tauri。
- 不写工程代码、不修改 `lifeos/engineering/`。
- 不连接真实 Vault。
- 不处理真实数据、低敏真实数据或真实用户文件。
- 不启用真实文件导出、路径扩权、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不冻结 Tauri 配置、Schema、API、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/reviews/LIFEOS-P3-021_r0040_closure_condition_assessment.md`
- `lifeos/reviews/LIFEOS-P3-021_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-023_engineering_baseline_extension_decision_assessment.md`
- `lifeos/reviews/LIFEOS-P3-023_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`，只读任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 真实 Tauri / IPC 验证任务的最小安全矩阵是什么。
- P2-015 后端合同如何迁移到真实集成层。
- 哪些条件满足前，不得关闭 R-0040 或启用真实能力。

协审角色必须重点检查：

- IPC、path scope、Renderer、debug / release 差异是否可能绕过用户授权、证据链、tombstone、generation 和 Project 边界。
- 规划是否误把“验证计划完成”写成“真实能力可启用”。
- evidence 设计是否足以让 PM 判断 P0 / P1 / P2。

## 核心问题

请重点回答：

- 未来真实 Tauri / IPC 验证任务最小应该测什么？
- 哪些测试失败必须视为 P0？
- 是否建议立即进入实际验证任务？如果建议，前置条件是什么？
- 如果暂不建议，下一步更应该先做什么？
- 本任务完成后 R-0040 状态是否变化？为什么？

## 交付物

请将完整交付物保存为 Markdown 文件，路径建议：

`lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`

请输出的文件内容包括：

- 结论摘要
- 已验证 / 未验证边界
- 最小验证矩阵
- P0 / P1 / P2 判定标准
- Evidence 包结构
- 失败处理与降级策略
- 是否建议启动实际验证任务
- 角色检查点结果
- 需要 PM / 用户确认的问题
- 后续任务建议

篇幅控制：

- 决策 / 技术规划型任务建议 1500-2500 字。
- 超出范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确声明本任务不关闭 R-0040、不启用真实能力、不冻结任何配置或工程基线。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改项目账本。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不恢复或冻结新的工程基线。
- 不进入下一阶段。
- 不自行启动后续任务。

## 给专项会话的可复制启动提示词

请先读取当前项目根目录的 `AGENTS.md`，并按其中规则执行 LifeOS 专项任务。

任务文件：

`lifeos/tasks/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`

请注意：你是专项独立规划会话，不是 PM 主会话。只做真实 Tauri / IPC 集成前置验证规划，不安装、不配置、不运行真实 Tauri，不修改工程文件、Stitch 或项目账本；不得关闭 R-0040，不得启用真实能力，不得冻结工程基线，不得进入下一阶段。完整交付物写入任务卡指定路径，聊天回复只输出摘要、交付物路径、预检路径和是否需要 PM 决策。

