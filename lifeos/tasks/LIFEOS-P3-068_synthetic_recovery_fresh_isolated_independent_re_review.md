# LIFEOS-P3-068｜合成恢复与失败披露全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限 P3-067 只读工程资产、任务卡指定的本地工作区和非敏感合成测试数据，用于防御性独立代码审查、故障／恢复反例验证和本地回归复评；不涉及外部目标、真实用户数据或凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“恢复、撤回、墓碑、反例”等术语只指本地合成环境，不授权扩大操作范围。真实 DB、备份、路径／Vault、Tauri/IPC、网络、云／第三方、导出、同步、多设备、L3、外部用户和 Stage 4 均未获授权。

## 任务信息

- 任务 ID：`LIFEOS-P3-068`；优先级：P0；类型：全新隔离独立复评；P3 Engineering Fast Lane：No。
- 推荐 Agent／配置：新建隔离 Codex 独立评审会话，`gpt-5.6-terra` + `xhigh`；允许降级／后备：None。
- 允许修改：仅 `lifeos/reviews/LIFEOS-P3-068/`、本任务交付物与临时副本；P3-067 工程及其 Evidence 严格只读。
- 主责：独立 QA；协审：技术架构、数据／领域模型、AI 信任与安全、产品／体验。
- 状态：Ready。

## 会话、输入与独立性

- 必须使用全新会话；不得复用 P3-067 执行／Rework 会话、P3-064/P3-066 评审会话或 PM 复跑会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向补读：`PM_OPERATING_MODEL.md` 的 P0、独立评审与用户确认规则；`ROLE_MATRIX.md` 的适用检查点；`STAGE_GATES.md` 的 Gate 1–4；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入（只读）：P3-067 任务卡、交付物、PM Review、PM Evidence、`lifeos/engineering/LIFEOS-P3-067/`，以及 `RISK_LOG.md` 的 R-0013、R-0019、R-0021、R-0040。
- 独立 runner 必须新写，不得导入、调用或复制 P3-067 测试文件；可在临时副本执行候选 CLI，不能覆盖原 Evidence。

## 必须验证

1. 在新临时副本清空 runtime 后，独立验证 capture 仅在提交后报告 saved；提交前故障／非法输入不伪称已保存。
2. 独立黑盒 CLI 链：同一干净 task-local run 必须是 `ready preview → first CONFIRM recovered (idempotent=false) → second CONFIRM recovered (idempotent=true)`。
3. 重启、未知计划、来源／版本不匹配、缺少确认、撤回与 tombstone 必须 fail-closed；不得复活或消费。
4. 检查审计顺序、来源／版本／状态可见性、hash 与 P3-067 Rework Evidence；确认历史 P1 Evidence 未覆盖。
5. 静态检查关闭态：网络、Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、L3、外部用户与外部动作均未实现。

## 停止条件与交付

- P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、hash 不一致、工程可写或独立性不足，结论必须 Rework 或 Blocked。
- 不关闭／重开风险，不冻结、不恢复工程基线、不启用真实能力、不进入 Stage 4、不创建后续任务。
- 输出：`lifeos/reviews/LIFEOS-P3-068/independent_review.md`、`lifeos/reviews/LIFEOS-P3-068/evidence/MANIFEST.md`、`lifeos/deliverables/LIFEOS-P3-068_synthetic_recovery_fresh_isolated_independent_re_review.md`；默认运行本地预检。
- Pass 仅表示 P3-067 当前 hash 的受控合成恢复包可供 PM／用户判断；不代表真实恢复、备份、风险关闭、冻结、基线恢复或 Stage 4。
