# LIFEOS-P2-016｜技术架构冻结补充 / 决策准备

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-016
- 任务名称：技术架构冻结补充 / 决策准备
- 优先级：P0
- 任务类型：决策型任务
- 建议篇幅：1500-2500 字；正文只做冻结决策准备，不重写完整技术架构大论文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-010` 至 `LIFEOS-P2-013` 已形成技术架构冻结候选、非冻结范围和两项冻结前硬窄测合同。随后：

- `LIFEOS-P2-014` FTS 维护隔离窄测已通过 PM 验收，结论为 `Accepted / Pass`，用户已确认采纳，R-0039 已关闭。
- `LIFEOS-P2-015` Tauri / IPC 最小安全边界窄测已通过 PM 验收，结论为 `Accepted / Pass with Conditions`，用户已确认采纳；R-0040 保持 `Open / Conditional`，真实 Tauri 集成或能力变更前必须迁移矩阵复测。

当前仍未冻结技术架构，也未进入正式 MVP 开发。本任务用于准备一次清晰、可审计的技术架构冻结决策输入，避免把 Spike 通过、条件通过、风险关闭、架构冻结和 Stage 3 准入混为一谈。

## 目标

本任务完成后，需要回答：

1. 当前技术架构是否已经具备“可冻结为 V0.1 架构合同”的条件？
2. 如果可以冻结，冻结范围到底是什么？
3. 哪些内容必须明确不冻结？
4. P2-015 的条件通过如何进入冻结边界：是可接受的冻结条件，还是必须先做真实 Tauri 包复测？
5. R-0039 / R-0040 / 其他未关闭风险如何影响冻结判断？
6. 技术架构冻结后，是否仍不得进入正式 MVP 开发？
7. PM / 用户下一步应做哪个明确决策？

## 范围

本任务必须覆盖：

### 1. 冻结条件核对

请逐项核对 P2-013 第 8 节冻结前置条件是否满足：

- P2-013 通过 PM 验收并由用户采纳。
- FTS 窄测通过或条件通过且条件被 PM 接受。
- Tauri / IPC 窄测通过或条件通过且条件被 PM 接受。
- 最终冻结包需引用两项窄测结果或形成补充附件。
- PM / 用户仍需另行作出技术架构冻结决定。

### 2. 冻结候选范围

请整理可冻结候选，但不要扩展或重写架构。至少覆盖：

- V1 默认单设备、本地优先。
- 本地权威原文与控制账本优先。
- SQLite + FTS-first 作为本地检索主路径候选。
- FTS 为可重建派生，长维护不得阻塞权威捕获。
- 派生可重建，向量后置。
- 权威事实 / 可重建派生 / outbox 与 job 职责分离。
- 发布、展示、索引、再派生、导出、恢复、外发前重检授权、来源、版本、tombstone / restriction generation、证据与租约。
- Obsidian 仅作为默认关闭、只读、条件适配器与降级合同，不承诺正式启用。
- Tauri / IPC 仅冻结后端安全合同和复测触发器，不冻结真实 Tauri capability 或打包配置。
- 同步 / 服务端具体栈后置，不进入当前冻结默认范围。

### 3. 明确不冻结范围

必须明确不得冻结：

- 正式 MVP / Stage 3 准入。
- SQLite Schema、API、Tauri capability 名称 / 配置、IPC 命令签名。
- FTS 表结构、PRAGMA、worker、调度策略、性能 SLA。
- 真实 Tauri 插件、WebView / CSP、debug / release bundle、updater / sidecar、跨平台路径行为。
- 同步 / 服务端具体栈、设备数、云端权威范围、冲突 UI、生产同步 SLA。
- Obsidian 正式启用承诺、写回、插件、双向同步、真实 Vault 接入许可。
- 真实云 / 第三方模型上线许可、模型供应商、供应商政策合格性。
- 正式导出格式、加密 / 签名、灾备和生产容量承诺。

### 4. 条件与风险处置

请明确：

- R-0039 是否可作为已关闭风险进入冻结输入。
- R-0040 是否可作为 `Open / Conditional` 被技术架构冻结接受。
- 若接受 R-0040 条件冻结，必须写明复测触发器、关闭能力和失败降级。
- 哪些遗留风险不阻止“架构合同冻结”，但会阻止真实能力启用或 Stage 3 准入。

### 5. 决策选项

请给 PM / 用户提供明确选项：

- 选项 A：冻结技术架构 V0.1 合同，但带 R-0040 真实 Tauri 集成复测条件。
- 选项 B：暂不冻结技术架构，先启动真实 Tauri 包复测任务。
- 选项 C：仅接受当前架构候选，不冻结，继续补充其他验证。

每个选项必须说明收益、代价、风险和推荐程度。

## 非范围

本任务暂时不要做：

- 不直接冻结技术架构。
- 不进入正式 MVP 工程开发。
- 不编写、修改或运行新技术 Spike 代码。
- 不运行真实 Tauri 集成或打包测试。
- 不修改 Stitch、PRD、V1 范围、核心领域模型或 AI 权限模型。
- 不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不调用真实模型、真实云服务、真实第三方 API 或付费资源。
- 不重新比较所有技术栈、云平台、数据库或向量库。
- 不把技术架构冻结等同于 Stage 3 / MVP 开发准入。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md` 中“技术架构”“P2-014”“P2-015”“MVP 开发准入”相关行
- `lifeos/RISK_LOG.md` 中 R-0039、R-0040
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P2-010_technical_architecture_candidate_review.md`
- `lifeos/deliverables/LIFEOS-P2-011_technical_architecture_freeze_condition_remediation.md`
- `lifeos/reviews/LIFEOS-P2-012_technical_architecture_independent_review.md`
- `lifeos/deliverables/LIFEOS-P2-013_technical_architecture_freeze_condition_final_patch.md`
- `lifeos/reviews/LIFEOS-P2-013_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-014_fts_maintenance_isolation_narrow_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-014_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-015_pm_review.md`
- `lifeos/DECISION_LOG.md` 中 D-0110 至 D-0121

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 evidence 日志；本任务只需要引用 P2-014 / P2-015 报告与 PM Review 的结论。
- 不主动读取完整 `PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `DECISION_LOG.md`；只读取 D-0110 至 D-0121 或最近相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。

## 角色检查点

主责角色必须重点回答：

- 当前是否足以冻结“架构合同”，而不是冻结实现细节？
- P2-014 / P2-015 是否已足够关闭 P2-012 的 Gate 4 条件？
- R-0040 的条件状态是否可以被冻结决策接受，还是必须先实测真实 Tauri 包？

协审角色必须重点检查：

- 数据 / 领域模型负责人：冻结候选是否保护用户原文、Source、ArtifactVersion、Derivation、Feedback、Authorization、tombstone 与 generation。
- AI 信任与安全负责人：授权、来源、AI 输出身份、外发前重检、重大动作确认和真实处理者关闭是否清楚。
- 产品架构负责人：方案是否仍服务 V1 自用闭环，不扩展成企业后台、云平台或 IT 运维平台。
- 体验设计负责人：已保存、索引中、索引失败、权限拒绝、只读限制、导出确认和复测条件是否能转化为诚实用户状态。
- PM：冻结 / 不冻结 / 条件冻结 / Stage 3 准入四类状态是否清楚。

## 核心问题

请重点回答：

1. 是否建议冻结技术架构 V0.1 合同？
2. 如果建议冻结，冻结范围是什么？
3. 哪些内容明确不冻结？
4. R-0039 / R-0040 如何进入最终冻结判断？
5. 是否需要先做真实 Tauri 包复测？
6. 技术架构冻结后是否仍禁止正式 MVP 开发？
7. PM / 用户应选择哪个选项？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`

交付物至少包括：

1. 执行摘要
2. 冻结前置条件核对
3. 建议冻结范围
4. 明确不冻结范围
5. R-0039 / R-0040 与条件处置
6. 决策选项 A / B / C
7. PM 推荐方案
8. 对 Stage 3 / MVP 开发准入的影响
9. 风险、例外与后续触发器
10. 需要 PM / 用户确认的问题

## 验收标准

只有满足以下条件，任务才算完成：

- 明确回答是否建议冻结技术架构 V0.1 合同。
- 清楚区分冻结范围、不冻结范围、条件冻结和开发准入。
- 明确处理 P2-014、P2-015、R-0039、R-0040。
- 提供至少 3 个决策选项并给出 PM 推荐。
- 明确正式 MVP 开发是否仍未准入。
- 未修改代码、Stitch、PRD、V1 范围、核心领域模型或 AI 权限模型。
- 完整交付物已保存到指定路径。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，且不粘贴完整交付物正文。

## 限制条件

- 不修改代码。
- 不运行新的技术 Spike。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结技术架构、Schema、API、Tauri capability 或数据模型。
- 不进入正式 MVP 开发。
- 不处理真实敏感数据、真实 Vault 或真实第三方数据。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入交付物文件。
