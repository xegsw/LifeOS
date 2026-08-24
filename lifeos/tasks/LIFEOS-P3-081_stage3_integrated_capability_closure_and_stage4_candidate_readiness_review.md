# LIFEOS-P3-081｜Stage 3 整合能力收口与 Stage 4 候选就绪复核

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、已采纳的只读任务卡、Review、Evidence 与项目账本中进行阶段治理、证据核对和防御性范围审查。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。本任务不实施任何真实能力，不授权访问真实个人数据、真实 DB、真实路径／文件、Vault、Tauri/IPC、网络、云／第三方、同步、多设备、L3 或外部用户。

## 状态、模型与隔离

- 状态：`Ready / Task-card Delivery Authorizes Execution`。用户将本任务卡路径发送至新建隔离 Codex 阶段治理／独立评审会话，即授权本卡范围内执行。
- 主责：新建隔离 Codex 阶段治理评审会话；不得复用 P3-079 工程执行、P3-080 独立评审或其 PM 验收会话。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`high`。
- 允许降级：`gpt-5.6-luna` + `high`；后备：`gpt-5.5` + `xhigh`，须记录原因。
- 禁止降级／必须回报：账本冲突、Evidence 冲突、任何 P0/P1、风险／冻结／基线／Stage 4 结论不明确，或发现真实能力已被启用。

## 目标

用**一份合并报告**更新 P3-062 的 Stage 3→4 五项硬门槛事实矩阵，纳入 P3-063 至 P3-080 已采纳的受控能力包。明确：

1. 哪些受控能力已经形成整合、可复查的有限边界 Evidence；
2. 哪些 Stage 4 硬门槛仍因真实运行、真实文件／路径、真实数据或外部／Alpha 用户 Evidence 而未满足；
3. 是否存在当前账本冲突、P0/P1 或需要先回包内整改的问题；
4. 下一次需要用户作出的**唯一重大选择**是什么。

本任务只形成阶段收口与用户决策输入，不作 Stage 4 准入、风险关闭／重开、基线恢复、资产冻结或真实能力启用决定。

## 范围与输入

- 必读最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`。
- 定向输入：P3-062 交付物与 PM Review；P3-063／064、P3-065／066、P3-067／069、P3-070／071、P3-072／073、P3-074、P3-075／076、P3-077／078、P3-079／080 的最终 PM Review／独立 Review／Evidence Manifest；`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`RISK_LOG.md` 的 R-0013／R-0014／R-0015／R-0019／R-0021／R-0040；D-0325 至 D-0332；以及 `STAGE_GATES.md` 的 Stage 3→4 与 Gate 1／3／4／5 章节。
- 允许写入：仅本任务交付物、`lifeos/reviews/LIFEOS-P3-081/`、task-local 临时摘要与本地预检报告。
- 禁止：修改工程代码、历史任务／Review／Evidence、风险、冻结、工程基线、Schema/API 或项目账本；不得创建后续工程任务。

## 验收标准

1. 将五项 Stage 4 硬门槛逐项标注为：`有限受控 Evidence 已具备`、`真实能力 Evidence 缺失`、`Blocked` 或 `Unknown`；不得把合成 SQLite／CLI／沙盒结果表述为真实能力通过。
2. 对 P3-079／080 的整合闭环、P3-070–073 的导出沙盒、P3-074 的使用说明、P3-067／069 的恢复和 P3-077／078 的权限运行时，分别说明已证明的严格范围与不可外推部分。
3. 核对当前主账本与指定 Evidence 的任务状态、hash／Manifest、风险和冻结叙述是否一致；发现冲突时只报告并建议修正。
4. 覆盖 Gate 1／3／4／5：已具备的定义或受控输入、仍缺的真实／用户 Evidence、以及禁止自动推进的原因。
5. 输出单一路线图，不拆分微型风险评估；只提出一个需要用户选择的后续方向：维持有限 Stage 3，或单独授权首项真实能力前置验证范围。
6. 明确 P0、P1、P2、Unknown、Not Implemented 数量；如发现 P0/P1、Evidence 冲突或阶段边界不清，结论必须为 Rework 或 Blocked。

## 交付与关卡

- 交付物：`lifeos/deliverables/LIFEOS-P3-081_stage3_integrated_capability_closure_and_stage4_candidate_readiness_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-081/independent_review.md`；Evidence Manifest：`lifeos/reviews/LIFEOS-P3-081/evidence/MANIFEST.md`。
- 首份会话报告必须记录收到的任务卡路径、会话类型与接收时间，作为 D-0319 执行授权证据。
- Gate 1／3／4／5 只做证据就绪度判断；即使结论为 Pass with Conditions，也不得进入 Stage 4，仍须 PM 验收与用户决定。

## D-0335 授权窄 Rework

用户已授权在原 P3-081 隔离阶段治理会话与原只读范围内执行以下整改；不新建任务号：

1. 更正 P3-080 PM Evidence Manifest 中 `4114715…` 的引用对象：它是 `lifeos/reviews/LIFEOS-P3-080/evidence/MANIFEST.md` 的 hash，不是 PM Manifest 的自指 hash；不得再声称存在 P3-080 Evidence 冲突。
2. 基于更正后的事实重新给出 P3-081 的 Stage 3 收口／Stage 4 候选就绪结论；五项真实能力 Evidence 缺口、风险、冻结与 Stage 4 边界必须保持准确，且不得把更正外推为准入。
3. 保留当前提交为只读历史；新的交付物、Review、复查命令、hash 与 Manifest 仅写入 P3-081 新 Rework 子目录。

不得修改 P3-080 或任何历史资产、项目账本、风险、冻结、基线、工程代码、Schema/API 或阶段状态；不得创建后续工程任务、启用真实能力或进入 Stage 4。完成后重新提交 PM 验收。
