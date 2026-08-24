# LIFEOS-P2-019 最小纵向切片验收合同 + 风险—测试追踪矩阵 + 能力启用门

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。本任务是工程实现前的验收合同任务，不写代码、不创建工程脚手架、不修改 Stitch、不处理真实数据。

## 任务信息

- 任务 ID：LIFEOS-P2-019
- 任务名称：最小纵向切片验收合同 + 风险—测试追踪矩阵 + 能力启用门
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字；如表格较长可略超，但不要扩展为完整开发计划
- 主责角色：PM / 技术架构负责人
- 协审角色：产品架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、体验设计负责人、质量 / 测试负责人
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 只承接自用有限例外，不宣称结果层通过
- 状态：Ready

## 背景

用户已采纳 `LIFEOS-P2-018` 的 Pass with Conditions，接受 Gate 5 自用 MVP 有限例外和九条工程硬约束，并允许进入“有限 Stage 3 / 自用 MVP 最小切片条件准入”。

但这不是无条件正式开发，不允许直接散开写代码。P2-018 明确要求：首个后续任务应先形成“最小纵向切片验收合同 + 风险—测试追踪矩阵 + 能力启用门”，再据此拆分工程任务。

本任务就是把 P2-018 的条件准入转成可执行、可验收、可追踪的工程共同合同。

## 目标

完成后需要回答：

- 自用 MVP 最小纵向切片到底包含哪些端到端能力？
- 哪些冻结资产和不变量必须被每个工程任务继承？
- P2-018 的九条工程硬约束如何转成验收项、测试项和证据路径？
- 哪些能力默认关闭，满足什么条件才能启用？
- 后续工程任务如何判断完成、失败、降级或不得上线？

## 范围

本任务必须覆盖：

- 定义“最小纵向切片”的验收合同：
  - 捕获用户原文；
  - 权威保存与“已保存”语义；
  - Source / Artifact / Derivation / Authorization / Feedback / AuditEntry 的最低追踪；
  - Project 上下文恢复；
  - 可核对证据；
  - 一个或零个 AI / 规则候选下一步；
  - 用户确认 / 拒绝 / 纠正 / 反馈；
  - 删除 / 撤回后的活跃阻断和不复活；
  - 基础导出 / 恢复候选边界。
- 建立风险—测试追踪矩阵：
  - 每条冻结不变量；
  - P2-018 九条工程硬约束；
  - R-0040；
  - 与真实数据、真实 Vault、真实 Tauri / IPC、导出、云 / 第三方模型、L3 自动动作相关的启用风险。
- 建立能力启用门：
  - 合成数据；
  - 低敏非唯一真实副本；
  - 真实 Obsidian Vault；
  - 真实 Tauri 文件能力 / IPC / capability；
  - 导出路径扩权；
  - 云 / 第三方模型；
  - 向量能力；
  - L3 内部自动动作；
  - 外部用户 / Beta / 商业化。
- 明确工程任务拆分前必须继承的共同验收格式。
- 明确失败、降级和暂停规则。

## 非范围

本任务暂时不要做：

- 不写代码。
- 不创建工程脚手架、数据库 Schema、API、Tauri 配置、测试脚本或具体实现任务。
- 不修改 Stitch 或任何原型。
- 不冻结新的 Schema、API、UI、真实 Tauri capability、真实导出格式、真实云 / 第三方模型或生产 SLA。
- 不处理真实敏感数据，不连接真实 Obsidian Vault。
- 不联系真实用户，不启动 Beta，不形成商业化或市场验证结论。
- 不重新打开宽泛技术选型，不推翻技术架构 V0.1 合同。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/RISK_LOG.md` 中 R-0013、R-0014、R-0017、R-0019 至 R-0040
- `lifeos/DECISION_LOG.md` 中 D-0123 至 D-0127，必要时读取 D-0081、D-0035、D-0050、D-0055、D-0062、D-0068、D-0078
- `lifeos/reviews/LIFEOS-P2-018_mvp_development_entry_independent_review.md`
- `lifeos/reviews/LIFEOS-P2-018_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-017_mvp_development_entry_review_package.md`
- `lifeos/reviews/LIFEOS-P2-017_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/reviews/LIFEOS-P2-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取冻结状态、PM Review、独立评审、风险行和准入相关决策；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界存在冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；只读取任务卡指定决策或最近 5-10 条相关决策。
- 如上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 交付物正文按补丁 / 条件整改型任务篇幅控制；超出范围的内容放入“后续任务建议”。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。
- 交付物完成后，默认调用本地预检：`python3 lifeos/tools/local_precheck.py <交付物路径>`。
- 会话回复应引用本地预检报告路径；若本地模型不可用、超时、输出为空、任务无明确交付物路径，或用户明确要求不调用本地模型，可跳过并说明原因。

## 角色检查点

主责角色必须重点回答：

- 最小纵向切片边界是否足够小、足够端到端、足够可验收？
- 风险—测试追踪矩阵是否能阻止工程任务绕过冻结资产？
- 能力启用门是否足够硬，不会让真实数据、真实 Vault、Tauri 文件能力或第三方模型被提前打开？

协审角色必须重点检查：

- 产品架构：切片仍服务 V1 第一场景，不扩成全知全能、企业后台或开发者工具。
- AI 信任与安全：AI 输出身份、用户确认、授权、撤回、删除、外发和高风险边界没有被简化掉。
- 数据 / 领域模型：用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认事实可区分、可追溯、可失效。
- 体验设计：最小切片必须覆盖关键交互状态，而不只写后端合同。
- 质量 / 测试：每条硬约束应有可复跑测试或证据路径。

## 核心问题

请重点回答：

- 自用 MVP 最小纵向切片的 Must / Should / Not Now 是什么？
- “完成”的判定标准是什么？哪些失败必须阻塞？
- P2-018 九条工程硬约束如何映射到测试和证据？
- 哪些能力必须默认关闭？每个能力启用前需要哪些证据、PM 决策或复测？
- 后续第一个真正工程任务应该具备什么任务卡结构和验收标准？

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

请输出的文件内容包括：

- 结论摘要
- 最小纵向切片范围合同
- Must / Should / Not Now
- 完成定义、失败定义、降级规则
- 风险—测试追踪矩阵
- 能力启用门表
- 后续工程任务共同验收格式
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为指定文件。
- 已完成本地预检并提供预检报告路径，或明确说明允许跳过的原因。
- 会话回复中提供交付物路径。
- 明确说明本任务不写代码、不创建工程实现任务。
- 明确区分事实、推断、建议和需 PM 确认事项。
- 明确列出哪些能力默认关闭、哪些证据通过前不得启用。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 不修改代码。
- 不修改 Stitch。
- 不创建工程实现任务。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不冻结新的产品、技术、Schema、API 或交互资产。
- 不处理真实敏感数据。
