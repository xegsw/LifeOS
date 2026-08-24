# LIFEOS-P3-080｜本地 MVP 整合能力包全新隔离独立安全／体验复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-079 当前 hash 的只读工程资产、只读 Evidence、非敏感测试文本与新建临时副本中进行防御性代码审查、独立反例验证和本地回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、撤回、恢复、失败、反例与边界术语仅用于核验本项目内部的防御性缺陷，不授权扩大范围。

## 状态、独立性与模型路由

- 状态：`Ready / Task-card Delivery Authorizes Execution`。用户将本任务卡路径发送到符合下方隔离要求的新专项会话，即授权本卡范围内执行。
- 主责：**新建隔离 Codex 独立评审会话**；不得复用 P3-079 工程执行会话、P3-079 PM 验收会话，或任何参与其实现、Rework 或复跑的会话。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`high`；理由：P0 整合闭环中的权限撤回与 Evidence 独立性须进行独立反例审阅。
- 允许降级模型：`gpt-5.6-luna` + `high`；后备模型：`gpt-5.5` + `xhigh`。使用时必须记录实际配置与原因。
- 禁止降级／必须回报：P0/P1、Evidence 冲突、独立性无法证明、越权、默认关闭失效、真实能力、风险／冻结／基线／Stage 4 或冻结合同问题。

## 目标、输入与边界

独立核验 P3-079 D-0328 Rework 当前 hash 是否在有限边界内满足：显式确认保存、来源／状态可见、精确 grant／deny／撤回、撤回幂等键绑定、恢复确认、原子失败无半成品、拒绝／阻断审计耐久、重启后 fail-closed，以及禁止通道继续关闭。

- 只读输入：`lifeos/engineering/LIFEOS-P3-079/`、P3-079 交付物、PM Review、PM Rework Evidence、`CURRENT_STATUS.md`、`FREEZE_STATUS.md`、`RISK_LOG.md` 的 R-0013／R-0014／R-0015／R-0019／R-0021／R-0040、D-0327 至 D-0329，以及独立评审模板。
- 允许写入：仅 `lifeos/reviews/LIFEOS-P3-080/`、本任务独立交付物、task-local 临时副本与本地预检报告。
- 禁止：修改 P3-079 或任何历史工程／Review／Evidence／账本；不得使用真实个人数据、真实 DB／路径／文件、Vault、Tauri/IPC、网络、云／第三方、AI 消费、导出、同步、多设备、L3、外部用户；不得关闭／重开风险、恢复基线、冻结资产或进入 Stage 4。

## 独立验证与 Evidence

1. 新建 task-local 黑盒反例 runner；不得导入、调用或复制 P3-079 的 `tests/`、`scripts/run_self_check.py` 或 `scripts/run_rework_self_check.py` 作为主要验证实现。
2. 在新建临时副本独立覆盖：保存确认／未确认、默认拒绝、精确 grant、deny 优先、过期／绑定不匹配、撤回后的 fail-closed、同 permission 同键重放、跨 permission 同键冲突、重启后冲突与审计、原子失败、恢复不复活撤回内容和 CLI preview。
3. 独立静态核对网络、云、Tauri/IPC、真实路径／文件、Vault、导出、同步、多设备、AI 消费、L3 和外部用户通道均未实现。
4. 保留 runner 源码、逐项结构化结果、日志、快照、hash、Manifest、复跑命令和“验收标准 → 反例 → Evidence”矩阵；核对 P3-079 当前 hash 与其指定历史只读输入未被覆盖。
5. 明确 P0、P1、P2、Unknown、Not Implemented 数量。发现 P0/P1、明确合同违反、Evidence 冲突、独立性不足、越权、默认关闭失效或影响完成定义的 Unknown／Not Implemented，必须判定 Rework 或 Blocked。

## 交付与关卡

- 独立交付物：`lifeos/deliverables/LIFEOS-P3-080_local_mvp_integrated_fresh_isolated_independent_re_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-080/independent_review.md`；Evidence Manifest：`lifeos/reviews/LIFEOS-P3-080/evidence/MANIFEST.md`。
- 首份会话报告必须记录本任务卡路径、会话类型与接收时间，作为 D-0319 执行授权证据。
- 新会话最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`；并定向读取本卡所列直接输入及 `PM_OPERATING_MODEL.md`、`ROLE_MATRIX.md`、`STAGE_GATES.md` 中的独立评审／P0 权限／Stage 3 边界章节。不得读取无关完整历史。
- 完成后提交 PM 验收。即使 Pass，也仅是 P3-079 当前 hash 在非敏感测试文本、task-local SQLite 与隔离本地目录内的独立复评输入；资产仍 Not Frozen，仍需用户采纳，不自动启用真实能力或进入 Stage 4。
