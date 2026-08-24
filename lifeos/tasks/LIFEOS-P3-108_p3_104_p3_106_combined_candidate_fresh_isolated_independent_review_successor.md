# LIFEOS-P3-108｜P3-104 + P3-106 组合候选全新隔离独立复评后继

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-107 关闭结论并授权创建本后继任务与新 ABF。本任务只读评估项目工作区内的固定候选，并仅在 `/private/tmp` 使用全新固定非敏感夹具，防御性验证 Tauri UI/runtime 的视觉、生命周期、路径、IPC、失败关闭和 Evidence；不访问 retained pilot、真实个人文件／DB、网络、云、第三方、凭据或外部目标，不授权扩大文件、数据库、shell、process 或网络能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-108`
- 任务名称：P3-104 + P3-106 组合候选全新隔离独立复评后继
- 优先级：P0
- 任务类型：全新隔离独立工程／安全／视觉／可访问性复评
- 是否为受控能力包：Yes。
- 能力包边界：只读评估固定 P3-106 高保真 Tauri candidate 与 P3-104 runtime 安全底座；不修复候选。
- 包内允许工作：独立测试设计、正向 allowlist 构建副本、离线 clean build、实际 app 动态复跑、视觉／响应式／a11y、生命周期／路径反例、Evidence／Manifest 与独立 Review。
- 包内整改授权：仅限 P3-108 自身 runner、Evidence、Review 和交付文案；不得修改候选、ABF、账本或风险。
- 必须拆分：候选修复、runtime／IPC／Cargo／capability／Schema/API 变化、路径扩大、真实数据／路径、系统显示设置、风险／冻结／基线／Stage 4。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 独立评审。
- 推荐理由：需要真实 Tauri 离线构建、GUI app 动态动作、P0 路径／生命周期反例及 P1 视觉／响应式判断，同时彻底隔离提交 Evidence／runner。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 独立性、历史时间语义、路径、IPC、失败关闭与动态 Evidence 必须联合判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选配置不可用时停止。
- 后备模型：None。
- 是否需要后续独立评审：No；本任务自身即独立复评，之后仍须 PM 验收和用户采纳。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／安全与数据生命周期评审。
- 协审角色：体验设计、可访问性、技术架构、数据／领域、AI 信任安全。
- 必须通过关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查固定非敏感内部理解，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-108-v1`
- ABF SHA-256：`54cbb4a8d302a1dd4007bcdbd7c7844f0d98588f54c51d941e197a8176c1ae10`
- ABF 状态：Frozen。
- 正式 Rework：0/2。
- 生效决策：D-0438。
- 执行授权：用户将本任务卡绝对路径投递至符合隔离条件的全新 Codex 独立评审会话，即启动 Frozen ABF 范围；仅在 PM 主会话查看路径不执行。
- 会话隔离：必须全新，不得复用 P3-104、P3-106、P3-107 工程／评审会话或本 PM 会话。
- 动态 Evidence：必须操作实际 Tauri app；不得以浏览器、file、HTTP、DOM mock、静态扫描或旧截图替代。正常本地 GUI app 控制连续两次不可用时 Blocked。
- 动态闭环：采用 `UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或结构等价 JSON；每个动作分别记录前置、操作、可观察结果、结果 ID、视觉／日志和 SHA-256。
- 投递前额外用户确认：None。当前固定非敏感独立复评已获授权；任何真实数据／路径、显示设置、runtime／IPC／依赖、风险／冻结／阶段变化仍需新确认。
- 授权记录：首份报告记录任务卡与 ABF 路径／ID／hash、接收时间、会话类型、实际模型／推理强度、独立性声明和歧义检查。

## 会话路由

- 建议新建会话：Yes。
- 推荐方式：Create New Session。
- 推荐会话类型：Codex 独立评审。
- 推荐复用会话：None。
- 隔离理由：P3-108 必须避免 P3-104/P3-106 实现与 P3-107 评审判断的自证循环；P3-107 的 runner、Evidence 和结论均仅作为错误历史只读输入。
- 任务完成后建议保留：Yes，仅用于 P3-108 自身 ABF 内修正；不得修复候选或执行后续任务。

## 最小启动包与高风险定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. Frozen ABF
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
7. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
8. `lifeos/ACCEPTANCE_GOVERNANCE.md`
9. `lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
10. `lifeos/reviews/LIFEOS-P3-104_pm_review.md`
11. `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md`
12. `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md`
13. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`
14. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md`
15. `lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_rework_1.md`
16. `lifeos/reviews/LIFEOS-P3-106_pm_review.md`
17. `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md`
18. `lifeos/reviews/LIFEOS-P3-106/pm_evidence/rework-1/MANIFEST.md`
19. `lifeos/reviews/LIFEOS-P3-107_pm_review.md`
20. `lifeos/reviews/LIFEOS-P3-107/pm_evidence/resume-1/MANIFEST.md`
21. 三张冻结 Stitch 权威参考图及 `lifeos/deliverables/LIFEOS-P1-011_home_today_stitch_freeze_condition_patch.md`

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：任务投递、模型路由、独立评审、两层验收、动态 Evidence、验收状态章节。
- `lifeos/ROLE_MATRIX.md`：PM、独立 QA、体验、架构、数据、AI 信任安全职责。
- `lifeos/STAGE_GATES.md`：Gate 1–5 与 Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0424 至 D-0438。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- P1-004/P1-006 信息层级与内容身份；P1-009/P1-010/P1-011 三态视觉意图。

只在发现冲突时定向补读，不全文重读无关历史。P3-104/P3-106/P3-107 runner、tests、tools 和结构化结论必须等新独立测试设计落盘并固定 SHA-256 后才可读取；始终不得复制、导入或执行。

## 背景与治理修正

P3-107 未确认候选工程缺陷，但因两项评审治理问题关闭：其工作副本复制了提交 Evidence／runner 而材料声明未复制；Frozen M-003 又把一个 Manifest 生成后更新的 PM Review 当作当前逐项匹配项，形成不可满足终点。

P3-108 不降低质量底线。新 ABF 将构建副本改为正向 allowlist，并对 P3-104 Manifest 唯一已知差异采用精确时间限定语义；任何第二项差异仍为失败。这样本轮有明确且可达的终点。

## 独立性执行顺序

1. 仅依据任务卡、ABF、L1 与用户结果设计新测试。
2. 在 `lifeos/reviews/LIFEOS-P3-108/evidence/` 落盘测试设计、夹具、断言、时间并固定 hash。
3. 之后才可只读反查提交源码／runner；不得复制、导入、执行或改写。
4. 从空目录按 ABF 正向 allowlist 创建构建副本，并先执行禁项 inventory 负门。
5. 独立 runner、ID 与结果结构不得沿用 P3-107；旧 PASS／Blocked 仅是待核历史。

## 目标与范围

独立回答固定 P3-106 candidate 是否同时保留 P3-104 runtime 安全边界、实现三张冻结 Stitch 高保真结果、适应原屏与窄屏，并在固定非敏感 actual-app 生命周期和失败反例下完整 fail-closed。

必须覆盖：当前快照与时间限定 Manifest；allowlist clean copy/build；三项 IPC／capability／runtime provenance；三张视觉与响应式；saved/repeat/conflict/failure/refresh/navigation/close-reopen；unknown IPC／额外字段；路径、链接、hardlink、类型、dangling、tamper；实际 a11y；Evidence 负门、隐私／网络、历史保全和精确清理。

非范围：候选修改；retained pilot 或真实数据；联网／安装依赖；显示设置修改；新增 IPC／capability／依赖／文件／shell／process／network；风险／冻结／基线／Stage 4。

## 允许修改与交付物

只允许：

- `lifeos/deliverables/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md`
- `lifeos/reviews/LIFEOS-P3-108/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-108/evidence/`
- Frozen ABF 精确临时路径，结束时按台账清理

不得创建 `lifeos/engineering/LIFEOS-P3-108/`，不得修改项目账本。

Evidence 必须包含 16 行矩阵、独立 runner、copy inventory、时间限定 Manifest 结果、clean build、actual-app 动态／负向／视觉／a11y、hash、before/after、scan、cleanup、final verifier、复跑说明和非自指 Manifest。

本地模型预检可因 P0 独立性、真实 Tauri/IPC 与本地文件边界最终判断跳过；须在 Review 写明理由。

## 验收结论与回退

- 结论只可为 Pass / Rework / Blocked。
- Pass：ABF 14 项不变量、16 行矩阵及全部子动作通过；P0/P1/P2/Unknown/Not Implemented 全零；历史不变；P3-108 残留 0；P3-107 旧路径仍缺失。
- P3-108 自身 Evidence／runner 缺陷可在 ABF 与边界不变时 Rework，最多两轮。
- 发现候选 P0/P1：结论 Rework，评审不得修复；PM 决定新任务边界。
- 独立性不成立、固定输入来源不明漂移、正常 actual-app 控制或锁定离线工具不可用：Blocked。
- 即使 Pass，也不改变 R-0040/R-0051/R-0052，不冻结、不恢复基线、不进入 Stage 4；等待 PM 验收和用户采纳。

## 聊天回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出：独立结论；ABF/hash；测试与 Evidence 摘要；P0/P1/P2/Unknown/Not Implemented；资产与风险状态；下一步许可；Review／Evidence 路径；需 PM 确认事项。
