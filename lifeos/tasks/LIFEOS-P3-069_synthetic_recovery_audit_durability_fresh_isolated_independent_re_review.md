# LIFEOS-P3-069｜合成恢复审计耐久性全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** 本任务仅限用户授权维护的 LifeOS 本地项目、P3-067 只读工程资产和非敏感合成 SQLite 数据，用于防御性独立复评与回归验证；不涉及外部目标、真实数据／凭据、网络扫描、真实攻击、持久化、数据获取或安全控制规避。真实 DB、路径／Vault、Tauri/IPC、网络、云、导出、同步、多设备、L3、外部用户和 Stage 4 均未获授权。

## 任务

- `LIFEOS-P3-069`，P0，全新隔离独立复评；新 Codex 会话，`gpt-5.6-terra` + `xhigh`，不得降级。
- P3-067 工程和历史 Evidence 严格只读；仅可在临时副本及 `lifeos/reviews/LIFEOS-P3-069/` 写入。
- 新会话最小启动包：`AGENTS.md`、`CURRENT_STATUS.md`、本任务卡、`INDEPENDENT_REVIEW_TEMPLATE.md`、`SESSION_REPORT_TEMPLATE.md`；定向补读 P0／独立评审规则、Gate 1–4、冻结状态和 P3-067/P3-068 PM Review/Evidence。
- 新写独立 runner；不得导入、调用或复制 P3-067 测试文件。

## 必须验证

1. 清空 runtime 的临时副本中，`saved` 仅在提交后返回，故障／非法输入不伪称已保存。
2. CLI 链为 ready preview → 首次 CONFIRM recovered（非幂等）→ 二次 CONFIRM recovered（幂等）。
3. `recovery_not_confirmed` 与 `recovery_blocked` 均在关闭并重启后持久保留且顺序可核验；来源／版本不匹配、撤回、tombstone 均 fail-closed。
4. 核对当前 hash、P3-067 Rework Evidence 和 P3-068 历史 Rework Evidence 未覆盖；静态检查所有外部能力关闭。

任何 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、hash 不一致或独立性不足均为 Rework／Blocked。不得关闭风险、冻结、恢复基线、启用真实能力、进入 Stage 4 或创建后续任务。

输出独立 Review、Evidence Manifest、结构化结果和交付物；Pass 仅作当前合成 hash 的 PM／用户判断输入。
