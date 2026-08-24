# LIFEOS-P3-078｜本地受控权限设置运行时全新隔离独立安全／体验复评

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅在指定本地工作区、P3-077 当前 hash 的只读工程资产、只读 Evidence、非敏感测试文本与新建临时副本中进行防御性代码审查、独立反例验证和本地回归测试。

不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。权限、拒绝、撤回、反例与边界术语仅用于核验本项目内部防御性缺陷，不授权扩大范围。所有删除、权限、外部写入和重大行动仍须遵守既有安全关卡。

## 状态、独立性与模型路由

- 状态：`Ready / Task-card Delivery Authorizes Execution`。创建任务不执行；用户将本任务卡路径发送到符合下方隔离要求的新专项会话，即授权本卡范围内执行。
- 主责：**新建隔离 Codex 独立评审会话**；不得复用 P3-077 执行会话、P3-077 PM 验收会话或任何参与 P3-077 实现／复跑的会话。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`high`；理由：P0 权限语义须独立审阅与反例覆盖。
- 允许降级模型：`gpt-5.6-luna` + `high`；后备模型：`gpt-5.5` + `xhigh`，必须记录实际配置与原因。
- 禁止降级／必须回报：P0/P1、Evidence 冲突、独立性无法证明、越权、默认关闭失效、真实能力、风险／冻结／基线／Stage 4 或冻结合同问题。

## 目标、输入与边界

独立核验 P3-077 当前 hash 是否在有限边界内满足：默认拒绝、唯一精确 grant + `CONFIRM`、当前 deny 优先、歧义／过期／撤回／绑定不匹配 fail-closed、原子失败无半成品、拒绝／撤回审计可追溯、重启后仍 fail-closed、操作者 preview 可理解，以及禁止通道继续关闭。

- 只读输入：`lifeos/engineering/LIFEOS-P3-077/`、P3-077 交付物、PM Review、PM Evidence、`CURRENT_STATUS.md`、`FREEZE_STATUS.md`、`RISK_LOG.md` 的 R-0013／R-0014／R-0015／R-0021／R-0040、D-0319 至 D-0322，以及独立评审模板。
- 允许写入：仅 `lifeos/reviews/LIFEOS-P3-078/`、本任务独立交付物、task-local 临时副本与本地预检报告。
- 禁止：修改 P3-077 或任何历史工程／Review／Evidence／账本；不得使用真实个人数据、真实 DB／路径／文件、Vault、Tauri/IPC、网络、云／第三方、AI 消费、导出、同步、多设备、L3、外部用户；不得关闭／重开风险、恢复基线、冻结资产或进入 Stage 4。

## 独立验证与 Evidence

1. 新建 task-local 黑盒反例 runner；不得导入、调用、复制 P3-077 的 `tests/test_permission_runtime.py` 或 `scripts/run_self_check.py` 作为主要验证实现。
2. 在新建临时副本中覆盖 allow 正例、默认拒绝、deny 优先（含 deny 后 grant）、多个 grant 歧义、过期、撤回、错误确认、上下文不匹配、幂等／冲突、原子失败、重启后撤回和 CLI preview。
3. 独立静态核对网络、云、Tauri/IPC、真实路径／文件、Vault、导出、同步、多设备、AI 消费、L3 和外部用户通道均未实现。
4. 保留 runner 源码、逐项结构化结果、日志、快照、hash、Manifest、复跑命令和“验收标准 → 反例 → Evidence”矩阵；同时核对 P3-077 当前 hash 与历史只读输入未被覆盖。
5. 明确 P0、P1、P2、Unknown、Not Implemented 数量。发现 P0/P1、明确合同违反、Evidence 冲突、独立性不足、越权、默认关闭失效或影响完成定义的 Unknown／Not Implemented，必须判定 Rework 或 Blocked。

## 交付与关卡

- 独立交付物：`lifeos/deliverables/LIFEOS-P3-078_local_runtime_permission_settings_fresh_isolated_independent_re_review.md`。
- 独立 Review：`lifeos/reviews/LIFEOS-P3-078/independent_review.md`；Evidence Manifest：`lifeos/reviews/LIFEOS-P3-078/evidence/MANIFEST.md`。
- 首份会话报告必须记录本任务卡路径、会话类型与接收时间，作为 D-0319 执行授权证据。
- 完成后提交 PM 验收。即使 Pass，也仅是 P3-077 当前 hash 在非敏感测试文本、task-local SQLite 与隔离本地目录内的独立复评输入；资产仍 Not Frozen，仍需用户采纳，不自动启用真实能力或进入 Stage 4。
