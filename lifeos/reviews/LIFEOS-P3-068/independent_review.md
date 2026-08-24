# LIFEOS-P3-068｜合成恢复与失败披露全新隔离独立复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-068`
- 是否为受控能力包：No（P3-067 为 D-0287 前创建的历史任务，不追溯能力包规则）
- 能力包边界／被评审最终 hash：P3-067 当前 `src/recovery.py`=`b0a15c08…e78bc`，`scripts/recovery_cli.py`=`02b7f516…8b537`
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-067_synthetic_recovery_and_failure_disclosure_controlled_implementation.md`
- 独立评审角色：独立 QA
- 协审视角：技术架构、数据／领域模型、AI 信任与安全、产品／体验
- 评审关卡：Gate 1–4 合成恢复适用项
- 独立评审路径：全新隔离会话；新写 runner；仅复制候选源与 CLI 到一次性临时副本；未导入、调用或复制 P3-067 测试文件
- 评审结论：**Rework**

## 评审摘要

- 事实：候选主 Evidence hash 与 Manifest 一致；历史 P1 Evidence 未被覆盖，P3-067 Rework 的 13 PASS 主链仍可对账。
- 事实：独立 runner 在清空的临时 SQLite 中验证 34 项通过，包括 `saved` 回执、故障与非法输入、重启、来源／版本／未知计划、tombstone、缺少确认及黑盒 CLI 三段链。
- 事实：同一干净 run 的 CLI 链成立：`ready / not_executed` → `recovered / idempotent=false` → `recovered / idempotent=true`。
- P1：缺少确认时写入的 `recovery_not_confirmed` 审计事件没有在事务中提交；关闭并重启后该事件不在 audit 中。blocked 路径也使用相同的事务外 `_audit()` 写法。
- 推断：拒绝／阻断本身继续 fail-closed，未发现复活或外部动作；但审计顺序与失败披露不能在重启后完整核验，未满足本任务明确的审计检查要求。
- 因 P1，当前 hash 不可作为 Pass 输入；不关闭／重开风险，不冻结、不恢复工程基线、不启用真实能力或进入 Stage 4。

## 已通过内容

- 捕获仅在 SQLite 事务完成后报告 `saved`；提交前故障与非法输入返回可见失败且无记录。
- 已提交记录在重启后可预览；unknown、来源错配、版本错配、tombstone 及缺少 `CONFIRM` 都拒绝恢复。
- CLI 不接收任意 DB／路径参数，并要求 `LIFEOS_SYNTHETIC_ONLY=1`；候选代码的外部能力维持关闭态。
- 已解决 P3-067 的历史 P1：独立黑盒链真实包含首次恢复，而不是用已恢复 runtime 的幂等回执替代。

## 关键问题

### P1｜拒绝确认／阻断审计未耐久保存

`SyntheticRecovery.recover()` 在 preview 不 ready（第 96–98 行）及 confirmation 非 `CONFIRM`（第 99–101 行）时调用 `_audit()`，但不进入 `with self.conn:` 事务或显式 commit。独立 runner 先调用 `recover(plan, "NO")`，关闭连接并重新经 CLI 打开同一数据库；最终 audit 仅保留 `capture_pending`、`recovery_completed` 与 `recovery_idempotent`，不保留 `recovery_not_confirmed`。这不是把失败当作成功的 bypass，但使拒绝／阻断的可追溯性在重启后消失，不能满足恢复失败披露的审计核验。

## 必须整改项

1. 在 P3-067 原受控工程目录内，仅修复 recover 的 blocked／未确认审计写入耐久性：使记录与成功恢复路径一样位于明确事务或提交中，且不改变 fail-closed 返回、来源／版本／tombstone 语义或关闭态边界。
2. 在原任务的回归中加入“缺少确认／blocked 后关闭并重启，审计事件仍存在且顺序可核验”的独立断言；更新结构化结果、日志与 Manifest。
3. 整改完成后，PM 必须先在新临时副本复跑；若验收通过，仍需重新进行全新隔离独立复评。

## 条件通过项

不适用。任务卡规定发现 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突、hash 不一致或独立性不足时，必须 Rework 或 Blocked。

## 关卡检查

- Gate 1 产品一致性评审：适用项通过；仍是个人本地合成恢复演练，非范围与真实能力边界清晰。
- Gate 2 数据与来源评审：未通过；来源、版本、状态可见，但拒绝／阻断审计未跨重启保留。
- Gate 3 AI 权限与信任评审：未通过；明确确认与 fail-closed 存在，但拒绝确认的审计证据不耐久，无法完整支撑确认边界追溯。
- Gate 4 技术可行性评审：未通过；核心合成链可复跑，审计事务边界存在 P1。
- Gate 5 用户价值验证评审：不适用；本任务不判定 Stage 4 或外部用户验证。

## 风险

- R-0019、R-0021 的状态不变。该 P1 是当前合成恢复包的审计持久性缺口；不在本任务中更新或重开风险账本。
- R-0013、R-0040 未触发；未发现网络、真实路径、Vault、Tauri/IPC、导出、云、同步、多设备、L3、外部用户或外部动作。

## 需要 PM 决策

- 请 PM 采纳本独立复评 Rework，并在用户授权后将整改严格限制在 P3-067 原目录的 blocked／未确认审计耐久化、对应回归与 Evidence；不得扩大到真实恢复、备份、路径或任何真实能力。

## 最终建议

不建议冻结、风险关闭、恢复工程基线或进入下一阶段。建议原任务 P3-067 在既有隔离工程目录中完成上述窄 Rework；完成 PM 验收后，创建新的隔离独立复评。
