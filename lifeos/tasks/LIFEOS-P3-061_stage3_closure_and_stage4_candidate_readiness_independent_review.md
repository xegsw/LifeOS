# LIFEOS-P3-061｜Stage 3 收口与 Stage 4 候选准入隔离独立评估

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限本地项目账本、任务、Review、Evidence、冻结状态和合成测试记录的只读核对，用于防御性工程治理与阶段准入判断；不涉及外部目标、真实数据或凭据、未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。文中“权限、撤回、风险、旁路”等术语仅指既有本地合成证据的治理核对，不授权扩大范围。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-061`；优先级：P1；类型：Stage 3 收口与 Stage 4 候选准入隔离独立评估；建议篇幅：2500–4000 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离会话；推荐模型／推理强度：`gpt-5.6-terra` + `xhigh`。
- 推荐理由：该任务跨越风险关闭、冻结边界、工程资产状态与阶段关卡，需避免 PM 自证与 P3-060 执行／评审上下文污染。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：任何阶段切换、工程基线恢复、冻结、真实能力启用建议，或账本／Evidence 冲突。
- 必须升级条件：无法形成可复核的阶段差距结论时，停止并回报 PM；仅 PM 新任务卡可改为 `gpt-5.6-terra` + `max`。
- 是否需要后续独立评审：No；本任务本身为独立评估。正式阶段切换仍须 PM 和用户明确确认。
- 是否允许修改工程文件：No；是否允许修改项目账本：No。
- 主责角色：独立 QA / 阶段治理 Reviewer；协审：技术架构、数据/领域模型、AI 信任与安全、产品/用户价值。
- 必须通过的关卡：Gate 1–5 的适用项；状态：Ready。

## 会话与读取

- 必须使用全新隔离 Codex 会话，不得复用 P3-048、P3-050、P3-054、P3-057、P3-058 或 P3-060 的执行／评审会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`INDEPENDENT_REVIEW_TEMPLATE.md`、`SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的阶段／冻结／独立评审规则；`ROLE_MATRIX.md` 的五类角色检查点；`STAGE_GATES.md` 的 Stage 3→4、正式 MVP 开发硬门槛与 Gate 1–5；`FREEZE_STATUS.md` 核心资产看板。
- 直接输入：`TASK_REGISTRY.md` 当前 P3 项；`RISK_LOG.md` 的 R-0040、R-0043–R-0050 与全表状态统计；`DECISION_LOG.md` D-0242、D-0253、D-0257、D-0260–D-0266；`LIFEOS-P3-059`、`LIFEOS-P3-060` PM Review/Evidence；与当前受控工程基线相关的 P3-009、P3-031、P3-050、P3-054、P3-057 的 PM Review／Evidence 入口。

## 目标与范围

形成一份**单一、可执行的阶段路线判断**，降低连续风险任务的认知负担：

1. 核对 Stage 3 当前受控范围内已完成工程整改、独立复评、风险关闭和仍开放的风险。
2. 逐项对照 `STAGE_GATES.md` 的 Stage 3→4 要求：真实可用 MVP、基础导出、基础权限设置、错误／数据恢复策略、Alpha 用户使用说明及适用 Gate 1–5。
3. 明确哪些事实已满足、哪些仅为合成候选 Evidence、哪些尚未开始；不得把已关闭的有限风险或冻结技术架构误写为真实能力或 Stage 4 准入。
4. 给出**唯一推荐的下一条工作线**（而不是拆分多个微型风险评估）：若不具备阶段切换条件，应指出最小且非真实能力的准备工作；若认为可进入任何后续实施，必须明确所需用户授权、目录范围、独立评审和停止条件。
5. 输出当前活动工程任务、风险数量、资产冻结／未冻结状态，并检查是否存在账本冲突。

## 非范围与停止条件

- 不修改代码、SQL、测试、Evidence、风险、冻结、任务登记或决策账本。
- 不关闭／重开风险，不恢复工程基线，不冻结资产，不进入 Stage 4，不启用真实 DB、Vault、Tauri/IPC、导出、云、同步、多设备、L3 或外部用户。
- 不创建后续任务；只提出一条推荐路线，最终是否创建由 PM/用户决定。
- 如发现账本冲突、P0/P1、Evidence 失效或任何阶段硬门未满足，结论必须为 Rework 或 Blocked，不得以 P3 测试数量抵消。

## 交付物与验收

- 交付物：`lifeos/deliverables/LIFEOS-P3-061_stage3_closure_and_stage4_candidate_readiness_independent_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-061/independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-061/evidence/MANIFEST.md`，含输入 hash、只读保留与账本核对摘要。
- 默认运行本地预检；不可用时记录允许跳过原因。
- 结论只能为 Pass / Pass with Conditions / Rework / Blocked。Pass 仅表示可作为 PM／用户下一步决定输入，不等于 Stage 4 准入、任何冻结、风险关闭或真实能力启用。
