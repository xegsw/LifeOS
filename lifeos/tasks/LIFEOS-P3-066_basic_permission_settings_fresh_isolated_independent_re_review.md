# LIFEOS-P3-066｜基础权限设置全新隔离独立安全／体验复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、P3-065 只读工程资产和非敏感合成测试记录，用于防御性代码审查、独立反例验证与本地回归复评；不涉及外部目标、真实用户数据或真实凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“权限、撤回、攻击、反例、旁路、风险”等术语只指本地合成环境中的防御性负向验证，不授权扩大操作范围。真实身份、Tauri/IPC、路径／Vault、云／第三方处理、导出、同步、多设备、L3、外部用户和 Stage 4 均未获授权。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-066`；优先级：P0；类型：全新隔离独立安全／体验复评；建议篇幅：2000–3500 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离独立评审会话；推荐模型／推理强度：`gpt-5.6-terra` + `xhigh`。
- 推荐理由：P3-065 为 P0 权限设置任务，且 D-0279 曾稳定复现 deny 被 grant 绕过；D-0281 修复后必须避免执行会话自证。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：deny 优先、撤回、有效期、幂等、审计、消费门、P0/P1、R-0013/R-0014/R-0021/R-0040 或任何真实能力边界。
- 必须升级条件：无法建立独立反例矩阵、工程资产不是只读、Evidence 冲突、独立性不足或出现真实能力要求时，停止并回报 PM；不得静默换模。
- 是否需要后续独立评审：本任务本身为独立复评；任何真实权限或阶段决定仍须另行独立评审与用户确认。
- 是否允许修改工程文件：No。只允许在隔离临时副本和 `lifeos/reviews/LIFEOS-P3-066/` 下创建本任务 Evidence。
- 是否允许修改项目账本：No。
- 主责角色：独立 QA／AI 信任与安全；协审：产品／体验、数据／领域模型、技术架构。
- 必须通过的关卡：Gate 2、3、4 的 P3-065 受控设置适用项；不得判定 Stage 4 Gate 通过。
- 状态：Ready。

## 会话与读取

- 必须使用全新隔离 Codex 独立评审会话；不得复用 P3-065 执行／Rework 会话、P3-064 评审会话或 PM 复跑会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的 P0、独立评审、用户确认与冻结规则；`ROLE_MATRIX.md` 的 AI 信任、数据、产品、技术与体验检查点；`STAGE_GATES.md` 的 Stage 3→4 与 Gate 2–4；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入：`lifeos/reviews/LIFEOS-P3-065_pm_review.md`、`lifeos/reviews/LIFEOS-P3-065/pm_evidence/MANIFEST.md`、P3-065 任务卡、交付物和 `lifeos/engineering/LIFEOS-P3-065/`（只读），以及 `RISK_LOG.md` 的 R-0013、R-0014、R-0015、R-0021、R-0040。

## 独立复评矩阵

必须自行编写独立 runner／断言，不得直接调用、导入或复制 P3-065 的测试文件作为主要证据；可在临时副本执行被评审 CLI，但不得覆盖工程 Evidence。

1. 独立复现历史 P1：同一精确绑定 grant→deny，必须 `allowed=false`、`explicit_deny_current`、无外部动作；同样验证 deny→grant。
2. 验证多个当前 grant 不确定时 deny；默认 deny、显式 deny、撤回、过期、四维绑定不匹配均必须 fail-closed。
3. 验证重复 grant／deny、重复撤回与撤回幂等键冲突的返回、版本、审计和持久化；冲突不得改变另一项授权。
4. 用操作者 CLI 完成 preview→CONFIRM grant→consume→CONFIRM deny→consume 的黑盒路径，验证确认、审计、来源／AI 状态和 `external_action=none`。
5. 静态检查无网络、Tauri/IPC、Vault、路径、导出、云、同步、多设备、外部用户或 L3 通道；只记录关闭态，不外推为真实能力。
6. 核对初版 14 PASS Evidence、Rework 23 PASS Evidence、PM P1 Evidence 和当前候选 hash 均被保留且未覆盖。

## 非范围与停止条件

- 不修改 P3-065 或任何历史工程／Evidence，不修改账本、风险、冻结、工程基线或任务卡。
- 不输入真实个人数据，不使用真实身份、路径／Vault，不启用或模拟 Tauri/IPC、网络、云／第三方、导出、同步、多设备、外部用户或 L3。
- 不关闭 R-0013、R-0014、R-0015、R-0021、R-0040 或其他风险；不冻结、不恢复工程基线、不进入 Stage 4，不创建后续任务。
- 任何 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、工程资产可写或独立性不足，结论必须为 Rework 或 Blocked；不得因执行侧测试数量多而放宽。

## 交付物与验收

- 独立 Review：`lifeos/reviews/LIFEOS-P3-066/independent_review.md`。
- Evidence：`lifeos/reviews/LIFEOS-P3-066/evidence/MANIFEST.md`，含隔离说明、独立 runner、命令、退出码、结构化结果、日志、快照、hash 与只读保留证明。
- 交付物：`lifeos/deliverables/LIFEOS-P3-066_basic_permission_settings_fresh_isolated_independent_re_review.md`，明确事实、反例统计、P0/P1/P2/Unknown/Not Implemented、范围与未验证项。
- 默认运行本地预检；不可用时记录允许跳过原因。会话回复使用 `SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和需要 PM 决策。
- Pass 仅表示 P3-065 当前 hash 的受控合成权限设置可作为 PM／用户后续判断输入；不代表真实权限、风险关闭、冻结、基线恢复、Alpha 或 Stage 4。
