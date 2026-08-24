# LIFEOS-P3-067｜合成恢复与失败披露受控实现及验证

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限新建的任务目录、只读输入和非敏感合成记录，用于防御性软件工程、故障注入、恢复边界验证和本地回归测试；不涉及外部目标、真实用户数据／凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“故障、恢复、撤回、墓碑、旁路”等术语只指本地合成环境中的负向验证，不授权扩大操作范围。真实 DB、路径／Vault、Tauri/IPC、网络、云／第三方、导出、同步、多设备、L3、外部用户和 Stage 4 均未获授权。

## 任务信息

- 任务 ID：`LIFEOS-P3-067`；优先级：P0；类型：受控工程实现与验证；P3 Engineering Fast Lane：No。
- 推荐 Agent／配置：新建隔离 Codex 工程会话，`gpt-5.6-terra` + `xhigh`；允许降级：None；后备：None。
- 路由理由：恢复、已保存语义与撤回／墓碑恢复禁止属于 P0；必须避免复用 P3-063/P3-065 的执行上下文或把候选资产当作真实能力。
- 禁止降级／必须升级条件：涉及 R-0013、R-0019、R-0021、R-0040、任何真实数据／能力、Evidence 冲突或无法维持隔离时，不得换模或扩大范围，停止回报 PM。
- 允许修改：仅 `lifeos/engineering/LIFEOS-P3-067/` 与本任务自身 Evidence／交付物。不得修改项目账本、P3-031、P3-063、P3-065 或其历史 Evidence。
- 主责：技术架构；协审：数据／领域模型、AI 信任与安全、产品／体验、独立 QA。
- 评审关卡：Gate 1–4 的合成恢复适用项；本任务不判定任何 Stage 4 Gate。
- 状态：Ready；完成后必须经过 PM 验收与全新隔离独立复评。

## 会话与读取

- 必须新建会话，不能复用 P3-063、P3-065 或 P3-066 会话；本任务完成后不自动继续其他任务。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向补读：`PM_OPERATING_MODEL.md` 的 P0／用户确认规则；`ROLE_MATRIX.md` 的数据、AI 信任、技术与体验检查点；`STAGE_GATES.md` 的 Gate 1–4 与 Stage 3→4；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入（只读）：P3-062 交付物、P3-063 PM Review、P3-065 PM Review、P3-066 PM Review，以及 `RISK_LOG.md` 的 R-0013、R-0019、R-0021、R-0040。

## 目标与必须覆盖范围

在全新目录内交付一个仅使用标准库与合成 SQLite 的最小恢复演练包，证明下列**受控语义**，而不是声称真实恢复能力：

1. 合成捕获只有在本地事务成功提交后才返回 `saved`；故障注入、非法输入或提交前中断必须返回可见失败，绝不伪称已保存。
2. 重启／重新打开同一合成数据库后，已提交记录可被核验；未提交或失败记录不可被伪造为已保存。
3. 恢复候选必须带来源、记录身份、保存／失败状态与版本；撤回或 tombstone 标记的合成对象不可通过恢复入口复活或消费。
4. 提供操作者 CLI：预览合成恢复计划 → 明确 `CONFIRM` 执行受控恢复 → 显示成功、失败和受阻原因；不得使用任何真实路径或目录扫描。
5. 以独立的 fault／recovery 测试覆盖：提交前故障、提交后重启、损坏／未知输入的可见失败、重复恢复幂等、撤回／tombstone 阻断、来源／版本不匹配阻断、审计与无外部动作。
6. 生成结构化结果、日志、快照和 hash Manifest；静态检查网络、Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、L3 与外部用户能力均处于关闭态。

## 非范围与停止条件

- 不读取或写入任务目录以外的真实文件；不操作真实 DB、备份、用户数据、身份、Vault 或文件导出；不做并发／WAL、真实崩溃恢复、迁移、网络、云、同步、多设备或 Tauri/IPC。
- 不接入或修改 P3-031/P3-063/P3-065；它们只能作为只读语义输入。不得把合成 SQLite Evidence 表述为正式恢复、正式备份、真实权限或 Stage 4 准入。
- 任何 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、越权访问或真实能力需求：停止并报告 PM；不得以条件通过掩盖。
- 不关闭／重开任何风险，不冻结资产、不恢复工程基线、不进入 Stage 4、不创建后续任务。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-067/`，含 README、CLI、实现、测试与 `evidence/MANIFEST.md`。
- 交付物：`lifeos/deliverables/LIFEOS-P3-067_synthetic_recovery_and_failure_disclosure_controlled_implementation.md`，区分事实、推断、未验证项与 PM 决策。
- 本地预检：默认运行 `python3 lifeos/tools/local_precheck.py <交付物>`；不可用／超时才记录并继续。
- 通过仅表示受控合成演练满足上述六项；P0/P1/P2/Unknown/Not Implemented 必须为 0，所有测试 exit 0，历史只读资产 hash 不变，且无外部动作。通过后仍须 PM 验收、全新隔离独立复评和用户决定。
