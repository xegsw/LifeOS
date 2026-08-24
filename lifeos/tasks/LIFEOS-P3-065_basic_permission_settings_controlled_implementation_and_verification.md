# LIFEOS-P3-065｜基础权限设置受控实现与验证

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、新隔离工程目录和非敏感合成测试记录，用于防御性软件工程、权限设置的缺陷修复与本地回归验证；不涉及外部目标、真实用户数据或真实凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“权限、撤回、攻击、反例、旁路、风险”等术语只用于本地合成环境中的防御性验证，不授权扩大操作范围。真实 Tauri/IPC、真实路径／Vault、云／第三方处理者、导出、同步、多设备、L3、外部用户和 Stage 4 均未获授权。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-065`；优先级：P0；类型：受控基础权限设置实现与验证；建议篇幅：2500–4000 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离工程执行会话；推荐模型／推理强度：`gpt-5.6-terra` + `xhigh`。
- 推荐理由：基础权限设置涉及授予、拒绝、撤回、处理目的／位置／处理者、有效期及 fail-closed 消费门，必须与 P3-063／P3-064 会话隔离。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：授权授予／拒绝／撤回、消费门、审计、有效期、身份、P0/P1、R-0040 或任何真实能力边界。
- 必须升级条件：需要真实身份、真实个人数据、Tauri/IPC、真实路径、Vault、云／第三方处理、导出、网络或无法以合成受控环境验证撤回后 fail-closed 时，立即停止并回报 PM；不得静默换模。
- 是否需要后续独立评审：Yes。执行会话不得评审自身成果；PM 验收后须新建隔离独立安全／体验复评。
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-065/` 与本任务交付物／Evidence／本地预检路径。
- 是否允许修改项目账本：No。
- 主责角色：AI 信任与安全／工程实现；协审：产品／体验、数据／领域模型、技术架构、独立 QA。
- 必须通过的关卡：Gate 2、3、4 的本任务受控设置适用项；不得判定任一 Stage 4 Gate 通过。
- 状态：Ready。

## 会话与读取

- 使用全新隔离 Codex 工程执行会话；不得复用 P3-063、P3-064 或后续独立复评会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的 P0、用户确认、独立评审与冻结规则；`ROLE_MATRIX.md` 的 AI 信任、数据、产品、技术与体验检查点；`STAGE_GATES.md` 的 Stage 3→4 与 Gate 2–4；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入：`lifeos/reviews/LIFEOS-P3-062_pm_review.md`、`lifeos/reviews/LIFEOS-P3-064_pm_review.md`、`lifeos/engineering/LIFEOS-P3-009/` 与 `lifeos/engineering/LIFEOS-P3-031/` 的只读授权约束输入、`lifeos/engineering/LIFEOS-P3-063/` 的只读闭环输入，以及 `RISK_LOG.md` 的 R-0013、R-0014、R-0015、R-0021、R-0040。

## 授权范围与目标

仅在新建 `lifeos/engineering/LIFEOS-P3-065/` 内使用 Python 标准库、SQLite 和非敏感合成记录，提供操作者可用的本地 CLI：

1. 操作者显式输入合成数据类别、处理目的、处理位置、处理者、有效期与受控 Project，先查看设置摘要，再明确授予或拒绝；默认必须拒绝。
2. 对已授予的合成授权，操作者可显式撤回；撤回后受控“消费尝试”必须 fail-closed，且不产生外部动作、网络、导出或 AI 消费。
3. 设置、授予／拒绝／撤回、消费判定、时间／版本和操作者确认均应可观察、可审计、可复跑；原文、授权事实、AI 状态和确认状态不得混淆。
4. 至少验证：默认拒绝、有效授权允许受控本地消费、拒绝阻断、撤回后阻断、过期阻断、处理目的／位置／处理者不匹配阻断、空／非法输入拒绝、幂等操作与失败不报成功。
5. 生成独立目录内的运行脚本、测试、结构化结果、日志、快照、hash 与 Evidence Manifest；不得覆盖 P3-009、P3-031、P3-063 或历史失败 Evidence。

“允许受控本地消费”只表示在合成 SQLite 中返回一个不会读取／发送真实内容、不会产生外部动作的 allow 决定；不代表真实 AI、云、第三方处理者、Tauri/IPC 或文件能力获得授权。

## 非范围与硬停止条件

- 不修改 P3-009、P3-031、P3-063、P3-064 或项目账本；它们只读。
- 不使用真实个人数据、真实用户身份、真实数据库、真实路径／Vault、真实 Tauri/IPC、网络、云／第三方处理、导出、同步、多设备、L3、外部用户或自动外部动作。
- 不冻结或恢复 Schema/API、工程基线、运行时配置或 Stage 4；不关闭／重开风险。
- 若授权模型不能保持默认拒绝、撤回后 fail-closed、目的／位置／处理者／时效绑定，或需扩大到真实能力，必须停止并报告 Rework／Blocked；不得以 mock／静态文档冒充真实 Tauri/IPC 或外部处理验证。
- 若出现 P0/P1、明确 P2 bypass、Unknown、Not Implemented、Evidence 不可复跑或范围越界，必须停止并如实报告。

## 必须交付与验收

- 工程资产：仅在 `lifeos/engineering/LIFEOS-P3-065/`，包含操作者 CLI、SQLite 适配层、合成夹具、测试、复跑脚本和 `evidence/MANIFEST.md`。
- 交付物：`lifeos/deliverables/LIFEOS-P3-065_basic_permission_settings_controlled_implementation_and_verification.md`，明确测试统计、退出码、P0/P1/P2/Unknown/Not Implemented、范围、授权矩阵、失败路径、未实现能力和输入 hash。
- 默认运行本地预检；不可用时记录允许跳过原因。会话回复使用 `SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和需要 PM 决策。
- 通过最低条件：所有上述授权场景均可重复验证；默认拒绝、撤回／过期／不匹配全部 fail-closed；成功／失败回执与审计可观察；无 P0/P1、Unknown、Not Implemented 或范围越界。即使通过，也只可进入 PM 验收与全新隔离独立安全／体验复评，绝不等于真实权限、风险关闭、冻结或 Stage 4。

## Rework 授权（D-0280）

PM 新增反例发现：同一精确绑定先 `grant`、再 `deny` 时，初版消费门仍返回 allow。用户已授权仅在 `lifeos/engineering/LIFEOS-P3-065/` 内执行窄 Rework。

- 必须在授权选择与消费门中建立**确定性、fail-closed 的冲突语义**：任一同一精确绑定下当前有效的明确 `deny` 均不得被历史或并列 `grant` 绕过；如存在多个候选且无法明确选择，也必须 deny。
- 必须新增并独立列出顺序／冲突矩阵：grant→deny、deny→grant、grant→revoke、grant→expiry、重复 grant、重复 deny、撤回幂等与撤回幂等键冲突；每项均核对返回、审计、版本、持久化与后续 consume。
- 必须修正交付物中回归数量与结构化结果不一致的文案，并更新 Manifest、日志、快照和 hash；不得覆盖初版或 PM P1 Evidence。
- 不得改动原任务的模型路由、目录授权、禁止边界、独立复评要求或 Stage 4 限制。可复用原 P3-065 工程执行会话（若仍只处理本任务且无其他活动工作）；若不可用则新建隔离工程会话，执行会话不得承担后续独立复评。
