# LIFEOS-P3-025｜生产 Schema / API 设计草案

## 任务信息

- 任务 ID：LIFEOS-P3-025
- 任务名称：生产 Schema / API 设计草案
- 优先级：P0
- 任务类型：技术 / 数据设计任务
- 建议篇幅：2500-4000 字
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要结构化产出 SQLite Schema 候选、Tauri IPC / 本地 API 命令签名、错误码、字段边界和后续实现输入；Codex 更适合生成严谨、可落地的工程合同草案。但本任务不写代码、不生成迁移、不执行真实 Tauri。
- 是否需要后续独立评审：Yes，建议后续由 WorkBuddy 对 Schema / API 草案做独立反例评审，再决定是否进入最小 Tauri 壳搭建。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：技术架构负责人 / 数据模型负责人
- 协审角色：AI 信任与安全负责人、QA / Evidence Reviewer、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 会话路由

- 是否建议新建会话：Conditional
- 推荐执行方式：Reuse Existing Session / Create New Session
- 推荐会话类型：Codex 技术 / 数据设计会话
- 推荐复用的会话：若已有 P3-009 / P3-024 相关 Codex 技术设计会话且上下文可靠，可复用；否则新建 Codex 专项设计会话。
- 会话判断理由：本任务需要继承 P3-009 受控工程基线扩展和 P3-024 真实 Tauri / IPC 前置验证规划，但不需要修改工程代码。
- 是否需要独立性隔离：Yes。执行本设计的会话不得承担后续独立评审。
- 必须重新读取：
  - `lifeos/CURRENT_STATUS.md`
  - 本任务卡
  - 本任务卡明确列出的输入材料
  - `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 可复用既有读取结果：
  - 若同一会话已完整读取且未压缩、未截断、文件未修改，可复用 `AGENTS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 的稳定规则理解。
- 必须因变化或不确定性重读：
  - `lifeos/CURRENT_STATUS.md`
  - `lifeos/reviews/LIFEOS-P3-024_pm_review.md`
  - `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
  - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 任务完成后是否建议保留会话：Yes，作为 Schema / API 设计线会话保留。

## 背景

P3-009 已恢复为受控工程基线扩展，但仍限于合成、单进程、受控测试包和本地 evidence。P3-024 已完成真实 Tauri / IPC 集成前置验证规划，并明确建议在实际 Tauri 壳搭建与矩阵迁移验证前，先完成生产 Schema / API 设计：明确 IPC 命令签名、参数结构、错误码、SQLite Schema 面向生产的边界。

当前 P3-009 中的 Schema 只是“不变量落点”和受控测试包实现，不代表生产 Schema、API、Tauri 配置、导出格式或 SLA 冻结。本任务要把后续最小 Tauri 壳、真实 IPC 验证和 UI 实现所需的 Schema / API 候选合同先设计清楚。

## 目标

本任务完成后，PM 应能获得一份可供评审的 Schema / API 设计草案，用于判断：

- V1 最小本地闭环需要哪些生产候选实体、表、字段、索引和状态。
- Tauri IPC / 本地 API 至少需要哪些命令、参数、返回、错误码和重检规则。
- P3-009 现有不变量如何映射到候选生产 Schema / API，而不是被简化丢失。
- 哪些设计可作为后续最小 Tauri 壳搭建输入。
- 哪些内容仍未冻结，必须经独立评审和后续验证。

## 范围

本任务必须覆盖：

- 生产候选 Schema 设计，至少覆盖：
  - Project
  - Source
  - Artifact
  - ArtifactVersion
  - ContentIdentity / 内容身份
  - Authorization / 权限
  - Derivation
  - DerivationInput
  - Feedback
  - ImportantLink / LinkEvidence
  - Tombstone / 删除与撤回状态
  - OutboxJob / 后续任务
  - FTS / SearchIndex 可重建派生
  - Export / Restore package projection（候选，不实现）
- 每类实体的字段、主键、外键、generation / version / status / content_hash / created_at / updated_at / source_id 等关键字段。
- 最小索引和约束建议，包括唯一约束、外键、状态约束、generation 约束、FTS 回连权威表。
- Tauri IPC / 本地 API 命令草案，至少覆盖：
  - capture / save user original
  - read artifact
  - search
  - suggest / create AI suggestion candidate
  - feedback / confirm / reject / correct / retract feedback
  - create important link
  - revoke authorization / delete artifact
  - export memory package candidate
  - restore candidates read-only evaluation
  - capability status / health check
- 每个 API 命令需说明：
  - 输入参数
  - 输出结构
  - 错误码
  - 必须重检的权限 / project / source / version / generation / tombstone / evidence / lease / purpose / location / processor
  - 是否允许写入
  - 是否触发 outbox / FTS / evidence 更新
- 错误码与 P0 / P1 / P2 风险映射。
- 与 P3-024 M-01 至 M-26 验证矩阵的映射。
- “冻结前硬条件”和“实现前注意事项”。

## 非范围

本任务暂时不要做：

- 不写 SQL migration 文件。
- 不修改 `lifeos/engineering/` 代码。
- 不安装、配置或运行真实 Tauri。
- 不创建真实 IPC handler。
- 不连接真实 Vault。
- 不处理真实数据、低敏真实数据或真实用户文件。
- 不启用真实文件导出、路径扩权、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不关闭 R-0040。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P1-004_home_today_prd.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-020_min_vertical_slice_engineering_task_card.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- `lifeos/reviews/LIFEOS-P3-024_pm_review.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 可按需要只读取输入材料中与 Schema/API 相关的章节；若文件较大，先用 `rg` 定位关键词再定向读取。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构冻结合同或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`，只读任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 角色检查点

主责角色必须重点回答：

- 生产候选 Schema 是否完整承接 P3-009 与 H1-H9 / T-ARCH 不变量。
- API 命令边界是否能支撑 P3-024 真实 Tauri / IPC 矩阵验证。
- 哪些字段、约束和索引是 Must，哪些是 Should / Later。

协审角色必须重点检查：

- 是否清楚区分用户原文、AI 生成、AI 推断、AI 建议、外部引用来源。
- 用户确认、纠正、撤回、删除、权限过期和反馈撤回是否有独立状态和证据。
- 是否避免把 FTS、导出包、恢复候选、summary、suggestion 等派生物变成不可重建权威。
- 是否没有借设计草案冻结 Schema / API 或启用真实能力。

## 核心问题

请重点回答：

- V1 最小本地闭环的生产候选 Schema 应包含哪些表 / 实体？
- 最小 Tauri IPC / 本地 API 应包含哪些命令？
- 每个命令如何 fail closed？
- 哪些错误必须视为 P0？
- 哪些设计是后续最小 Tauri 壳搭建前置条件？
- 本任务完成后是否允许实际安装 / 运行 Tauri？为什么？

## 交付物

请将完整交付物保存为 Markdown 文件，路径建议：

`lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`

请输出的文件内容包括：

- 结论摘要
- 设计边界与非冻结声明
- 生产候选 Schema 总览
- 表 / 实体设计
- 索引、约束和 generation / version 规则
- Tauri IPC / 本地 API 命令设计
- 错误码与 P0/P1/P2 映射
- 与 P3-024 验证矩阵映射
- 权限 / 删除 / 撤回 / 反馈 / 导出 / 恢复候选特殊规则
- Must / Should / Later 分层
- 角色检查点结果
- 需要 PM / 用户确认的问题
- 后续任务建议

篇幅控制：

- 技术 / 数据设计任务建议 2500-4000 字。
- 超出范围的内容放入“后续任务建议”，不要无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2 / Gate 3 / Gate 4 是否通过或条件通过。
- 明确区分事实、推断、建议和需 PM / 用户确认事项。
- 明确声明本任务不冻结 Schema / API、不运行 Tauri、不启用真实能力、不关闭 R-0040。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不修改项目账本。
- 不写 SQL migration。
- 不安装、配置或运行真实 Tauri。
- 不关闭 R-0040。
- 不启用真实数据、真实 Vault、真实 Tauri / IPC、真实文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 不冻结 Schema / API、Tauri 配置、导出格式、生产 SLA 或工程基线。
- 不进入下一阶段。
- 不自行启动后续任务。

## 给专项会话的可复制启动提示词

请先读取当前项目根目录的 `AGENTS.md`，并按其中规则执行 LifeOS 专项任务。

任务文件：

`lifeos/tasks/LIFEOS-P3-025_production_schema_api_design.md`

请注意：你是专项技术 / 数据设计会话，不是 PM 主会话。只产出生产 Schema / API 设计草案，不写代码、不写 SQL migration、不安装、不配置、不运行真实 Tauri，不修改工程文件、Stitch 或项目账本；不得关闭 R-0040，不得启用真实能力，不得冻结 Schema / API 或工程基线，不得进入下一阶段。完整交付物写入任务卡指定路径，聊天回复只输出摘要、交付物路径、预检路径和是否需要 PM 决策。

