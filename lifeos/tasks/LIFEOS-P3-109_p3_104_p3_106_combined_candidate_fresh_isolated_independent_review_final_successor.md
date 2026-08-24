# LIFEOS-P3-109｜P3-104 + P3-106 组合候选全新隔离独立复评最终后继

## 授权与安全语境

> LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已采纳 P3-108 的 `Closed — Acceptance Not Met / Rework 2/2` 结论，并授权创建本全新后继独立复评任务。本任务只读评估固定 P3-106 Tauri candidate 与 P3-104 runtime 安全底座，只在项目工作区和 ABF 精确枚举的 `/private/tmp` 路径使用固定非敏感夹具；不访问 retained pilot、真实个人文件／DB、网络、云、第三方、凭据或外部目标，不扩展攻击或通用文件／数据库／进程能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-109`
- 任务名称：P3-104 + P3-106 组合候选全新隔离独立复评最终后继
- 优先级：P0
- 任务类型：全新隔离独立工程／安全／视觉／响应式／可访问性复评
- 是否为受控能力包：Yes；只读复评同一固定组合候选，不修复候选。
- 包内允许工作：独立测试设计、正向 allowlist 副本、离线 clean build、actual app 动态动作、固定视觉比较、native 窗口几何、生命周期／路径反例、语义 verifier、Evidence／Manifest／Review。
- 包内整改授权：仅 P3-109 自身 runner、Evidence、Review 和交付文案；不得修改候选、ABF、账本、风险或冻结状态。
- 必须拆分：候选修复、runtime／IPC／依赖／capability／Schema/API 变化、路径／数据／授权扩大、系统显示或偏好修改、风险／冻结／基线／Stage 4。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex 独立评审。
- 推荐理由：需要真实 Tauri 离线构建、native macOS 窗口几何、P0 生命周期／路径反例、P1 视觉／响应式判断和不信任汇总状态的语义级 Evidence 验证。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 独立性、固定身份、路径／IPC、失败关闭、native geometry 与 Evidence 语义需联合判断。
- 允许降级模型：None。
- 禁止降级条件：本任务全部范围。
- 必须升级条件：N/A；首选配置不可用时停止为 Blocked。
- 后备模型：None。
- 是否需要后续独立评审：No；本任务自身即独立复评，之后仍须 PM 验收和用户采纳。
- 是否允许修改工程文件：No。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／安全与数据生命周期评审。
- 协审角色：体验设计、可访问性、技术架构、数据／领域、AI 信任安全。
- 必须通过关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅核对固定非敏感内部理解，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-109-v1`
- ABF SHA-256：`212b66b320a4ad8cc55db0e9818407368d6ccb31104f6b12a130e06bdd20ac5d`
- ABF 状态：Frozen。
- 正式 Rework：0/2。
- 生效决策：D-0443。
- 执行授权：用户将本任务卡绝对路径投递至符合隔离条件的全新 Codex 独立评审会话，即启动 Frozen ABF 范围；仅在 PM 主会话查看路径不执行。
- 投递前额外用户确认：None。任何真实数据／路径、系统设置修改、候选修改、风险／冻结／阶段变化仍需新确认。

## 会话路由与独立性

- 必须新建会话：Yes。
- 推荐方式：Create New Session；不得复用 P3-104、P3-106、P3-107、P3-108 工程／评审会话或 PM 主会话。
- 隔离理由：P3-109 必须避免实现上下文和两代失败评审 runner／状态字段形成自证循环。
- 执行顺序：先只依据任务卡、Frozen ABF 与 L1 形成 `test_design.md` 并固定 SHA-256；之后才可只读反查 P3-107/P3-108 runner／结果。旧 runner／tools／Evidence 不得复制、导入、执行或作为当前 PASS 输入。
- 任务完成后：保留会话仅处理 P3-109 同 ABF 内、未达两轮上限的自身 Evidence／runner Rework；不得修复候选或自动执行下一任务。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. Frozen ABF
5. `lifeos/ACCEPTANCE_GOVERNANCE.md`
6. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
7. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
8. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
9. `lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration.md`
10. `lifeos/reviews/LIFEOS-P3-104_pm_review.md`
11. `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md`
12. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`
13. `lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md`
14. `lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_rework_1.md`
15. `lifeos/reviews/LIFEOS-P3-106_pm_review.md`
16. `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md`
17. `lifeos/reviews/LIFEOS-P3-108_pm_review.md`
18. `lifeos/reviews/LIFEOS-P3-108/pm_evidence/rework-1/MANIFEST.md`
19. ABF 固定的三张 Stitch 与三张 P3-106 1280×1024 Evidence

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：任务投递、模型路由、独立评审、动态 Evidence、两层验收章节。
- `lifeos/ROLE_MATRIX.md`：独立 QA、体验、架构、数据与 AI 信任职责。
- `lifeos/STAGE_GATES.md`：Gate 1–5 与 Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0433 至 D-0443。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。
- P1-004/P1-006 信息层级与身份；P1-009/P1-010/P1-011 三态视觉意图。

只在发现账本或 hash 冲突时再定向补读，不全文翻阅无关历史。

## 本任务吸收的 P3-108 治理修正

1. M-007 明确只比较 ABF 固定的 P3-106 三张 1280×1024 actual-app Evidence 与 Stitch，不重新捕获或量测 1280 窗口。
2. M-008 把 700×760 冻结为 macOS native outer window frame 的 point size，允许普通 GUI resize 和 AX／CGWindow／System Events 只读查询；禁止用 CUA 图片尺寸、屏幕坐标或显示缩放替代。
3. final verifier 不读取矩阵 `status/pass` 作为通过依据，而从 raw logs、DB／fixture snapshots、geometry、cleanup 和 hashes 重新计算。
4. 使用 payload manifest → semantic verifier → 顶层非自指 Manifest → PM 独立复算的非循环链，避免 verifier 声称验证包含自身 hash 的结构。
5. 冻结独立 Review 路径必须写入本轮结论；不得把专项执行回报写入 PM Review。

## 目标与验收范围

独立回答固定 P3-106 candidate 是否同时：

- 保留 P3-104 runtime／IPC／路径／原子发布安全边界；
- 实现三张冻结 Stitch 的共享骨架与独立状态锚点；
- 在当前原窗口和 native 700×760 下保持内容、滚动和关键动作可达；
- 对 saved／repeat／conflict／failure／refresh／navigation／close-reopen 保持真实一致；
- 对未知 IPC、多余字段、路径／链接／hardlink／类型／dangling／tamper 在变更前 fail-closed；
- 保持实际键盘／focus／reduced-motion 披露、隐私、离线、历史保全与精确清理；
- 提供不依赖自报状态的语义级可复核 Evidence。

完整 Pass 公式、矩阵、geometry 定义、mutation self-test 与退出条件以 Frozen ABF 为唯一 L2 依据。

## 允许修改与交付物

只允许创建／修改：

- `lifeos/deliverables/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor.md`
- `lifeos/reviews/LIFEOS-P3-109/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-109/evidence/`
- Frozen ABF 逐字枚举的 `/private/tmp` 路径，结束时精确清理

不得创建 `lifeos/engineering/LIFEOS-P3-109/`，不得修改候选、历史资产、ABF 或项目账本。

Evidence 至少包含：授权／固定输入、read order、新测试设计、allowlist inventory、离线 build、static results、固定视觉逐态比较、native geometry 原始输出、16 行结构化结果、actual app raw logs／AX／截图、DB／fixture before/after、boundary／negative／a11y／scan、六类 verifier mutation logs、payload manifest、cleanup、final verifier、顶层非自指 Manifest 和精确复跑命令。

## 结论、Rework 与停止规则

- 专项结论只可为 Pass / Rework / Blocked；PM 独立裁决并维护账本。
- Pass：Frozen ABF I-01–I-14、M-001–M-016 和全部子动作通过；语义 verifier 真 payload 退出 0、六类 mutation 全部非零；P0/P1/P2/Unknown/Not Implemented 全 0；历史不变、临时残留 0、PM 可复算 Manifest。
- P3-109 自身 runner／Evidence／Review 缺陷仅在 ABF 不变且正式 Rework 少于两轮时可原任务整改。
- 发现候选 P0/P1：独立评审不得修复，结论 Rework，交回 PM 判断候选修复的新任务边界。
- 正确模型、锁定离线工具、正常 actual app 或两种只读 native geometry 查询均不可用：Blocked；不得用旧动态 Evidence 替代。
- 即使 Pass，也不改变 R-0040／R-0051／R-0052，不冻结、不恢复基线、不连接 retained pilot、不进入 Stage 4；等待 PM 验收和用户采纳。

## 本地预检与聊天回复

- 本地模型预检可跳过：本任务涉及 P0 独立性、真实 Tauri/IPC、本地文件失败关闭、native geometry 和 Evidence 真实性最终判断；须在 Review 说明理由。
- 聊天严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出：独立结论；ABF/hash；测试与 Evidence 摘要；P0/P1/P2/Unknown/Not Implemented；资产与风险；下一步许可；Review／Evidence 路径；需 PM 确认事项。
