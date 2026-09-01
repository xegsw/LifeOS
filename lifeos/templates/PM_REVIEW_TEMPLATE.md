# LifeOS PM Review Template V2

## 验收信息

- 任务 ID：
- 风险等级：L0 / L1 / L2 / L3 / Gate
- Task Contract／ABF：
- 候选／交付物：
- Evidence 等级与路径：
- 任务状态：
- PM 结论：Pass / Closure Cycle / Evidence Closure / Paused — Resumable / Blocked / Invalidated Attempt / Closed — Acceptance Not Met / Superseded

## 结论摘要

- 唯一用户结果是否实现：Yes / No / Unknown
- 范围与授权是否一致：Yes / No
- 历史是否保全：Yes / No / N/A
- 测试与 Evidence 摘要：

## Task Contract 核对

| ID | 冻结／约定结果 | 实际 Evidence | 结论 |
|---|---|---|---|
| AC-01 |  |  | PASS / FAIL / UNKNOWN / NOT_IMPLEMENTED |

PM 不得增加无法映射到长期质量原则或 Task Contract 的新阻断标准。普通改进进入 Backlog。

## 五类计数

- P0：
- P1：
- P2：
- Unknown：
- Not Implemented：

## 风险分级与独立评审

- 当前风险等级是否准确：Yes / No；理由：
- 是否强制独立评审：Yes / No
- 是否条件触发独立评审：Yes / No；具体触发事实：
- 独立评审路径／结论：

不得仅因 P0 标签、Tauri/IPC、任务编号或历史惯例自动要求独立评审。

## Closure Cycle（仅未通过时）

首次 PM 未通过时，一次性列出全部当前合同内缺口：

| ID | 缺口 | 映射条款 | 所需修正／Evidence |
|---|---|---|---|
| CL-01 |  |  |  |

- 是否保持同一结果、范围、数据、入口、权限、风险和架构：Yes / No
- Yes：原任务进入 Closure Cycle，无需用户重复授权。
- No：关闭或 Superseded，并说明必须变化的合同边界。

## 暂停／恢复判断（仅适用时）

- 失败类别：Candidate Failure / Evidence Gap / Recoverable Environment / Recoverable Procedure / External Blocker / Irrecoverable Invalidation / Contract Change
- 检查点路径：
- Task Contract／候选／基线摘要是否仍一致：Yes / No
- 是否触及禁止边界：Yes / No
- 已完成且可复用阶段：
- 最早受影响阶段：
- `resume_from`：
- 错误 Evidence 是否已列入 excluded artifacts：Yes / No / N/A
- PM 结论：Paused — Resumable / Evidence Closure / Blocked / Invalidated Attempt

锁屏、AXWindow暂不可得、截图服务不可用或一次无敏感内容的截图错误，不得单独构成候选P0或整个任务失效。

## 用户确认判断

普通 L0/L1/L2 PM Pass 后自动 `Accepted / Complete`，无需逐任务采纳。

只有以下事项等待用户确认：

- L3/Gate 最终关卡；
- 产品方向或范围；
- 关键冻结；
- 风险关闭／重开；
- 真实能力／外部用户启用；
- Stage 切换；
- 新增高风险或不可逆边界。

本任务是否需要用户确认：Yes / No；理由：

## 账本与下一步

- CURRENT_STATUS：
- TASK_REGISTRY：
- DECISION_LOG：
- RISK_LOG／FREEZE_STATUS 是否有事实变化：
- 下一步：继续原任务 / 自动 Complete / 独立评审 / 用户关卡确认 / 新任务 / Backlog / None

## 聊天摘要

仅输出：结论、测试/Evidence 摘要、五类计数、风险/冻结/阶段状态、路径和确需用户决定的事项。
