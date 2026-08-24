# LIFEOS-P3-064｜可真实使用 MVP 最小闭环全新隔离独立工程／体验复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、P3-063 只读工程资产和非敏感合成测试记录，用于防御性代码审查、独立反例验证与本地回归复评；不涉及外部目标、真实用户数据或真实凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“权限、攻击、反例、旁路、风险”等术语只指本地合成环境中的防御性负向验证，不授权扩大操作范围。所有真实能力、冻结、风险、工程基线、外部写入和阶段切换仍须遵守既有用户确认与安全关卡。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-064`；优先级：P0；类型：全新隔离独立工程／体验复评；建议篇幅：2500–4000 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离独立评审会话；推荐模型／推理强度：`gpt-5.6-terra` + `xhigh`。
- 推荐理由：P3-063 为 P0 MVP 闭环实现，且刚完成执行侧 Rework；必须避免执行会话自证。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：耐久保存、回执、输入／确认、来源／AI 身份、恢复、路径边界、R-0019、R-0040、P0/P1 或任何阶段结论。
- 必须升级条件：无法独立运行反例矩阵、工程资产不是只读、Evidence 冲突，或出现真实能力／Tauri/IPC／路径／个人数据要求时，停止并回报 PM；不得静默换模。
- 是否需要后续独立评审：本任务本身为独立复评；任何真实能力或阶段决定仍须另行独立评审与用户确认。
- 是否允许修改工程文件：No。可仅在新建临时副本和 `lifeos/reviews/LIFEOS-P3-064/` 下创建本任务 Evidence。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／工程安全；协审：产品／体验、数据／领域模型、AI 信任与安全、技术架构。
- 必须通过的关卡：Gate 1–4 的本任务受控闭环适用项；不得判定 Stage 4 Gate 通过。
- 状态：Ready。

## 会话与读取

- 必须使用全新隔离 Codex 独立评审会话；不得复用 P3-063 的任何工程执行或 Rework 会话，也不得复用将被评审的 PM 复跑会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的 P0、独立评审、用户确认与冻结规则；`ROLE_MATRIX.md` 的五类检查点；`STAGE_GATES.md` 的 Stage 3→4 与 Gate 1–5；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入：`lifeos/reviews/LIFEOS-P3-063_pm_review.md`、`lifeos/reviews/LIFEOS-P3-063/pm_evidence/MANIFEST.md`、P3-063 任务卡、交付物和 `lifeos/engineering/LIFEOS-P3-063/`（只读），以及 `RISK_LOG.md` 的 R-0019、R-0040。

## 独立目标与反例矩阵

必须自行建立独立 runner／断言，不得直接调用或复制 P3-063 的 `tests/test_mvp.py` 作为主要证据；可在临时副本运行被评审 CLI，但不得覆盖工程 Evidence。

1. 用独立合成参数运行正路径，核对操作者输入、来源／内容身份、`user_confirmed`、`external_action=none`、AI 关闭与输出只在隔离 runtime。
2. 独立验证空输入、缺少 `--synthetic-only`、非法 `--run-id`、同幂等键不同文本、提交前注入失败；均必须可见失败、非零退出、无“已保存”成功回执，且不得留下错误记录。
3. 独立验证同幂等键相同文本不重复写入、重启后仅已提交记录可读、未知 Project 被拒绝。
4. 检查 CLI／依赖／文件操作，确认无网络、Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、外部用户、L3 或真实个人数据通道；不得将静态检查或合成 CLI 外推为真实能力。
5. 核对 P3-063 执行侧及 PM Evidence hash；确认 P3-009、P3-031 和历史 Evidence 没有被本任务覆盖。

## 非范围与停止条件

- 不修改 P3-063 或任何其他工程／历史 Evidence，不修改账本、风险、冻结、工程基线或任务卡。
- 不输入真实个人数据，不使用真实路径／Vault，不启用或模拟 Tauri/IPC、导出、云、同步、多设备、外部用户或 L3。
- 不关闭 R-0019、R-0040 或任何风险；不冻结、不恢复工程基线、不进入 Stage 4，不创建后续任务。
- 任何 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、工程资产可写或独立性不足，结论必须为 Rework 或 Blocked；不得因执行侧测试数量多而放宽。

## 交付物与验收

- 独立 Review：`lifeos/reviews/LIFEOS-P3-064/independent_review.md`；结论只可为 Pass / Pass with Conditions / Rework / Blocked。
- Evidence：`lifeos/reviews/LIFEOS-P3-064/evidence/MANIFEST.md`，含隔离说明、独立 runner、命令、退出码、结构化结果、日志、快照、输入／输出 hash 与只读保留证明。
- 交付物：`lifeos/deliverables/LIFEOS-P3-064_usable_mvp_minimum_closed_loop_fresh_isolated_independent_re_review.md`，明确事实、反例统计、P0/P1/P2/Unknown/Not Implemented、范围与未验证项。
- 默认运行本地预检；不可用时记录允许跳过原因。会话回复使用 `SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和需要 PM 决策。
- Pass 仅表示 P3-063 受控合成闭环可作为 PM／用户下一步决定输入；不代表风险关闭、资产冻结、工程基线恢复、真实能力启用、Alpha 或 Stage 4。
