# LIFEOS-P3-001 合成数据最小纵向闭环实现与验证

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。本任务明确授权你在本地工作区创建 / 修改完成本任务所需的最小工程代码、测试、合成夹具、证据包和交付报告；但不得处理真实数据、不得启用真实外部能力、不得修改 Stitch、不得冻结 Schema / API / UI / SLA。

## 任务信息

- 任务 ID：LIFEOS-P3-001
- 任务名称：合成数据最小纵向闭环实现与验证
- 优先级：P0
- 任务类型：工程实现型任务 / 条件准入验证任务
- 建议交付报告篇幅：1500-3000 字；完整日志、测试输出和证据写入 evidence，不要塞进聊天回复
- 主责角色：工程负责人 / 技术架构负责人
- 协审角色：PM、产品架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、体验设计负责人、质量 / 测试负责人
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅继承自用有限例外，不宣称结果层通过
- 状态：Ready

## 背景

用户已采纳 `LIFEOS-P2-020`，允许启动 `LIFEOS-P3-001`。P2-020 已把 P2-019 的共同验收基线转成首个工程任务候选：只用合成数据证明一个最小纵向闭环。

当前项目还没有正式应用脚手架。因此本任务的工程实现应优先采用受控、可复跑、可审查、可迁移的最小本地实现，默认落在：

- 工程代码 / 脚本建议目录：`lifeos/engineering/LIFEOS-P3-001/`
- 证据根目录：`lifeos/engineering/LIFEOS-P3-001/evidence/`
- 工程交付报告：`lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`

如果你发现已有更合适的 LifeOS 应用代码目录，可以在不大范围重构的前提下使用，但必须在报告中说明依据、影响和未冻结内容。

## 目标

用确定性合成数据可复跑地证明以下最小纵向闭环：

捕获用户原文 → 权威保存 → 用户选择 Project 后恢复当前合法上下文 → 零或一个未确认候选下一步 → 用户确认 / 编辑后确认 / 拒绝 / 纠正 / 忽略 → 删除或撤回后的活跃阻断 → 基础导出 / 恢复候选与不复活验证。

## 范围

本任务必须覆盖：

- 创建一个最小可运行工程实现，优先使用本地 SQLite + FTS-first + 确定性规则 / stub；不得依赖真实云、真实模型或外部服务。
- 创建确定性合成夹具，且夹具不得包含真实身份、真实路径、真实凭据、真实秘密或真实 Vault 内容。
- 实现语义层最低身份区分：Source、Artifact / ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry，以及重要 Link 的来源与确认状态。
- 实现“权威提交后才已保存”；FTS、派生或队列故障不得伪造保存成功。
- 实现 Project 上下文恢复包：停点、变化、决定、未处理材料、证据缺口；所有条目必须能回到当前合法 Source / Artifact / 版本或诚实显示缺口。
- 实现零或一个候选下一步；候选必须标记为“规则 / AI 建议·未确认”，证据不足时返回“暂无可靠建议”。
- 实现用户反馈：确认、编辑后确认、拒绝、纠正、忽略；Feedback 追加留痕，不静默覆盖用户原文。
- 实现四类控制命令的最小语义：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback`；撤回 / 删除后活跃读取、搜索、建议、队列、导出 / 恢复候选必须零命中或诚实排除。
- 实现基础导出 / 恢复候选验证：仅受控测试包；必须验证身份、来源、版本、确认状态、排除项、部分失败和 tombstone / generation 不复活。
- 实现并运行 P2-020 指定的最小测试集：`T-SCOPE`、`T-ID`、`T-SAVE`、`T-GATE`、`T-DEL`、`T-IPC-OFF`、`T-DATA`、`T-OFF`、`T-UX`、`T-EXPORT`、`T-ARCH`。
- 生成 evidence manifest，记录夹具版本、环境 / 平台、提交或变更标识、命令 / 人工步骤、预期断言、机器可读结果或必要截图 / 原始日志、已知限制、责任人和复跑时间。
- 生成工程交付报告，并在聊天中只输出简短摘要、交付物路径、证据路径和是否需要 PM 决策。

## 非范围

本任务暂时不要做：

- 不处理真实数据、低敏真实副本、真实敏感数据或唯一数据。
- 不连接真实 Obsidian Vault，不读取用户真实 Vault，不做 Obsidian 写回、插件或双向同步。
- 不启用真实 Tauri 文件能力 / IPC / capability，不做真实文件系统广泛授权，不做打包发布。
- 不启用云 / 第三方模型、真实模型网关、向量、同步 / 多设备、L3 自动动作、外部用户、Beta、商业化。
- 不冻结 Schema、API、UI、Tauri 配置、正式导出格式、生产 SLA 或最终工程目录结构。
- 不修改 Stitch、首页 / 今日页 PRD 或冻结原型。
- 不做宽泛技术选型重开，不把工程便利性反向改写冻结产品规则。
- 不创建外部账号、部署服务、调用付费资源或上传任何数据。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/deliverables/LIFEOS-P2-020_min_vertical_slice_engineering_task_card.md`
- `lifeos/reviews/LIFEOS-P2-020_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/reviews/LIFEOS-P2-019_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/FREEZE_STATUS.md` 中“技术架构”“MVP 开发准入”“最小纵向切片验收合同”“最小纵向切片工程任务卡”相关行
- `lifeos/STAGE_GATES.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取 P2-020 的任务建议、P2-019 的 H1-H9 / `T-ARCH` / 能力启用门 / 第 6 节共同验收格式。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取最近 5-10 条或任务卡指定相关决策。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 技术测试可以产生大量日志，但聊天中只报告 PASS / FAIL 数量、P0 失败数、关键失败、报告路径和 evidence manifest 路径。

## 推荐工程目录与证据文件

建议创建：

- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/src/` 或等效最小实现目录
- `lifeos/engineering/LIFEOS-P3-001/fixtures/`
- `lifeos/engineering/LIFEOS-P3-001/tests/`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/scope_matrix.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/identity_trace.*`
- `lifeos/engineering/LIFEOS-P3-001/evidence/durability_report.*`
- `lifeos/engineering/LIFEOS-P3-001/evidence/consumption_gate.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/revocation_delete_e2e.*`
- `lifeos/engineering/LIFEOS-P3-001/evidence/tauri_ipc_matrix.*`
- `lifeos/engineering/LIFEOS-P3-001/evidence/data_gate_manifest.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/default_off_matrix.*`
- `lifeos/engineering/LIFEOS-P3-001/evidence/ux_export_report.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/architecture_conformance.md`

以上路径是建议，不是冻结的生产目录结构。若调整路径，必须在报告中说明。

## 角色检查点

主责角色必须重点回答：

- 最小实现是否真正跑通了一个端到端闭环，而不是只写文档或分散功能点？
- 权威保存、身份区分、授权重检、撤回 / 删除阻断、不复活、默认关闭能力是否有可复跑证据？
- 代码、夹具、测试和证据是否足够小、确定性、可审查、可迁移？

协审角色必须重点检查：

- PM：是否严格在 P3-001 范围内，不把有限自用准入外推成无条件正式开发。
- 产品架构：是否仍服务个人外脑第一场景，不扩成企业后台、IT 运维、全局任务系统或自主 Agent。
- AI 信任与安全：是否区分用户原文、AI / 规则候选、用户确认、外部来源；重大动作是否仍需确认；关闭能力是否不可达。
- 数据 / 领域模型：Source、Artifact、Derivation、Feedback、Authorization、AuditEntry 等语义身份是否可追踪、可失效、不混淆。
- 体验设计：正常、空、失败、受限、证据缺口、确认 / 拒绝 / 纠正、撤回 / 删除状态是否进入测试或走查。
- 质量 / 测试：P0 是否零失败；P1 是否有降级 / 关闭能力 / 责任人 / 期限；证据是否可复跑。

## 核心问题

请重点回答：

- 实际创建 / 修改了哪些工程文件？
- 最小闭环如何运行？复跑命令是什么？
- `T-SCOPE`、`T-ID`、`T-SAVE`、`T-GATE`、`T-DEL`、`T-IPC-OFF`、`T-DATA`、`T-OFF`、`T-UX`、`T-EXPORT`、`T-ARCH` 各自结果是什么？
- 是否存在 P0 失败？若有，必须结论为 Fail 或 Paused，不得判 Pass with Conditions。
- 是否存在任何能力启用请求、范围偏离、架构偏离、核心语义偏离或 AI 权限边界变化？
- 下一步是否可以进入 PM 验收？还是需要工程返工？

## 交付物

请将完整工程交付报告保存为：

`lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`

请输出的文件内容包括：

- 结论摘要
- 实现范围与非范围
- 创建 / 修改文件清单
- 运行方式与复跑命令
- 合成夹具说明与隐私扫描结果
- 端到端闭环说明
- H1-H9 与 `T-ARCH` 覆盖结果
- 测试结果摘要：PASS / FAIL 数量、P0 失败数、P1 遗留
- Evidence manifest 路径
- DoD 对照
- 失败、降级、回退或暂停说明
- 能力启用请求：如无，写“无”
- 需 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 已创建 / 修改最小工程代码、合成夹具、测试和证据包。
- 已生成指定交付报告。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 已运行可复跑测试，并在报告与聊天中给出 PASS / FAIL 数量、P0 失败数和关键失败。
- 适用 P0 测试若有任何失败，任务结论必须是 Fail 或 Paused，不得写 Accepted、Pass 或 Pass with Conditions。
- 证明合成数据不含真实身份、真实路径、凭据、秘密或真实 Vault 内容。
- 证明默认关闭能力不可达：真实 Vault、真实 Tauri 文件能力、真实导出扩权、云 / 第三方模型、向量、L3、外部用户。
- 证明删除 / 撤回后活跃读取、搜索、建议、队列、导出 / 恢复候选零命中或诚实排除。
- 明确说明未冻结 Schema、API、UI、Tauri 配置、正式导出格式、生产 SLA 或最终工程目录结构。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径、证据路径和是否需要 PM 决策。

## 限制条件

- 只允许使用合成数据。
- 不允许处理真实敏感数据、真实 Vault、真实文件系统广泛路径或真实外部服务。
- 不允许调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不允许启用向量、同步 / 多设备、L3 自动动作、外部用户 / Beta / 商业化。
- 不允许修改 Stitch、冻结原型、重写 PRD 或改变产品方向。
- 不允许冻结新的 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 如果实现发现必须偏离 V1 范围、技术架构、核心领域语义或 AI 权限边界，必须暂停并在报告中标记“需 PM 决策”，不得在代码中既成事实。
