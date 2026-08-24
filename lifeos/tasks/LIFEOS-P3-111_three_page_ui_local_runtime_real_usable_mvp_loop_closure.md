# LIFEOS-P3-111｜三页 UI 与本地 Runtime 可真实使用 MVP 闭环收口

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。用户已明确确认：只在全新 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2`、其中全新 `capture.sqlite`、最多 3 条用户主动手工输入的低敏感短文本和本地 unsigned Tauri app 内，完成三页 UI 与本地 runtime 的有限本人真实使用闭环；仅允许 `capture_record`、`get_today`、`runtime_status` 及 UI 导航、刷新、关闭重开；禁止 clear、export、权限设置、恢复和网络能力；首轮保留目录与 DB，任何清理另行确认。禁止读取或修改 `LifeOS-Self-Use-Pilot-1`、既有个人文件／DB、Vault、云、第三方、凭据或外部目标。

## 任务信息

- 任务 ID：`LIFEOS-P3-111`
- 优先级：P0
- 任务类型：Stage 4 第一硬门“可真实使用 MVP”的受控实现与有限本人真实使用能力包。
- 单一结果：在不新增 Schema/API／IPC 的前提下，以三页 UI 完成“手工记录 → 本地提交成功 → Today 权威恢复 → 状态／来源可辨 → 导航、刷新、关闭重开后仍成立”的有限真实桌面闭环。
- 是否为受控能力包：Yes。
- 唯一风险边界：固定 P3-106 UI/Tauri candidate、P3-104 runtime 合同与 P3-102/103 有限真实使用边界的后继整合；只允许一个全新候选目录和一个待确认的全新真实使用目录。
- 包内允许工作：启动前产品走查、正向 allowlist 候选副本、同范围实现／回归／必要补测、固定非敏感自检、经确认后的少量低敏感真实使用、Evidence／Manifest／文案对齐。
- 包内整改授权：仅本任务工程目录、交付物、Evidence 和最终确认的精确真实目录；不得修改历史候选、ABF、账本、风险或冻结。
- 必须拆分：P3-111 完成后必须新建 P3-112 全新隔离独立复评。基础导出、基础权限设置、错误／数据恢复、Alpha/Gate 5、风险关闭／重开、基线恢复、冻结和 Stage 4 准入均是后续独立任务。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐 Agent：Codex 新建工程／真实能力执行会话。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型理由：真实本地路径、SQLite、Tauri/IPC、生命周期、内容隐私和失败关闭属于 P0 联合边界。
- 允许降级模型：None。
- 禁止降级条件：全部范围。
- 必须升级条件：正确配置、离线构建、真实 app 或原生窗口工具不可用时 Blocked；不得换模绕过。
- 后备模型：None。
- 是否需要后续独立评审：Yes；执行会话不得自评最终通过。
- 是否允许修改工程文件：Yes，仅 `lifeos/engineering/LIFEOS-P3-111/`。
- 是否允许修改项目账本：No。
- 主责角色：本地 MVP 工程与数据生命周期。
- 协审角色：产品／体验、数据与来源、AI 信任安全、可访问性、独立 QA。
- 关卡：Gate 1、Gate 3、Gate 4；Gate 5 只收集本人使用观察，不作通过。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`。
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-111-v1`
- ABF SHA-256：`24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395`
- 正式 Rework：0/2。
- 执行授权：用户将本任务卡绝对路径投递至合格新会话即启动 Frozen 边界；专项仍须由用户在该会话主动手工输入低敏感文本，不得自行生成或读取既有文本。

## 已确认的真实使用边界

- 新专用目录：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2`，不得复用或读取 Pilot-1。PM 冻结前只读确认目标不存在，`/Users`、`/Users/xxe`、`/Users/xxe/Documents` 均为真实目录而非链接。
- 新 DB：仅 `<专用目录>/capture.sqlite`；执行前必须不存在。
- 用户输入：最多 3 条用户主动手工输入的低敏感短文本；不得进入 Evidence 原文。
- 允许入口：当前三项 IPC `capture_record`、`get_today`、`runtime_status`，以及 UI 导航、刷新、关闭／重开。
- 禁止入口：`clear`、export、权限设置写入、恢复、raw SQL／shell／process、新 IPC、网络及任何外部能力。
- 保留：首轮完成后保留专用目录和 DB；任何清理另行逐次确认。
- app：本任务新候选的 unsigned debug Tauri app；不读取 P3-102 retained DB／页面。

## 会话、隔离与启动前走查

- 必须新建未参与 P3-104 至 P3-110 工程／评审的 Codex 执行会话。
- P3-110 保持暂停和只读；不得把其独立 Pass 声明当作候选基线。P3-110 PM finding 只作为新 Evidence verifier 的反例输入。
- 在复制或修改代码前，先只读对照冻结 Stitch、P3-106 当前截图与 P3-101 gap matrix，生成本任务内 `product_gap_matrix.md`；只允许映射到本 ABF，不能新增用户结果。
- 候选只能从 P3-106 正向 allowlist 复制到 `lifeos/engineering/LIFEOS-P3-111/candidate/`；禁止复制历史 Evidence、runner、tests、target 或工具。
- 不得修改 P3-104、P3-106、P3-102/103、P3-110 或其他历史资产。

## 最小启动包与定向补读

执行会话必须完整读取：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、Frozen ABF、`lifeos/ACCEPTANCE_GOVERNANCE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`、`lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`。

定向补读：

- `PM_OPERATING_MODEL.md`：真实能力、Tauri/IPC、用户确认、独立评审、两层验收。
- `ROLE_MATRIX.md`：产品、工程、数据、AI 信任、体验与独立 QA 职责。
- `STAGE_GATES.md`：Stage 3→4、Gate 1/3/4/5。
- `RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- `DECISION_LOG.md`：D-0401、D-0414 至 D-0424、D-0427 至 D-0448。
- P3-101 resume-1 PM Review；P3-102/103 任务、PM Review 与 Manifest；P3-104 PM Review/Manifest；P3-106 rework-1 任务、PM Review/Manifest；P3-110 PM Review/PM Evidence。
- 三张冻结 Stitch 与 P3-106 固定高保真截图。

## 验收范围

1. 产品走查只回答核心闭环中已有、缺失和占位项；不得扩展 V1 或重做视觉方向。
2. candidate provenance 与 UI/runtime hash 可追溯；IPC 仍严格三项，capability、网络和外部能力保持关闭。
3. 固定非敏感全量自检：首次、重复、冲突、失败、刷新、导航、关闭重开、窄屏、键盘、内容身份、路径／类型／sidecar／tamper、清理和 semantic verifier。
4. 经确认后的有限真实使用：用户在 app 内手工输入低敏感短文本；Evidence 只记长度区间、hash、计数和状态，不记原文或 key。
5. 成功只能在 DB commit 后显示；失败在任何错误文件／DB 变更前关闭；Today 必须从 backend 权威状态恢复。
6. 完成后候选工程 Evidence 稳定、临时夹具清零；真实专用目录／DB 按用户确认保留。

## 非范围与停止条件

- 不实现基础导出、权限设置、备份／恢复或 Alpha 说明；这些分别进入后续任务。
- 不新增 IPC、Schema、依赖、领域实体或 AI 能力；如核心闭环需要上述变化，停止并回 PM 新建任务。
- 不读取、迁移、复制、hash、覆盖或删除 Pilot-1 及任何既有个人 DB／页面。
- 不使用真实敏感文本、第三方内容、Vault、网络、云、同步、多设备、L3 或外部用户。
- 不关闭／重开风险，不冻结候选，不恢复基线，不进入 Stage 4。
- 目标路径已存在、祖先链含链接、Evidence 无法脱敏、需清理 retained 资产、用户结果变化或 ABF 有歧义时，在任何变更前停止。

## 交付物

- `lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure.md`
- `lifeos/engineering/LIFEOS-P3-111/`
- `lifeos/engineering/LIFEOS-P3-111/evidence/MANIFEST.md`
- 用户确认后的精确专用目录；不在 Evidence 中复制真实原文或 DB。

提交 PM 前必须完成包内自检，明确 P0/P1/P2/Unknown/Not Implemented；即使 PM Pass，也须用户采纳后另建 P3-112 全新隔离独立复评，且仍不自动满足其余四项硬门或 Stage 4。
