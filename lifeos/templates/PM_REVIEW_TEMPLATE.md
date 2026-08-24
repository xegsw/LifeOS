# LifeOS PM Review Template

## 验收信息

- 任务 ID：
- Acceptance Basis Freeze 路径：
- ABF ID／版本／PM 记录 SHA-256：
- ABF 是否在专项会话开始前 Frozen：Yes / No
- 本次反例是否全部映射到既有 L1/L2：Yes / No；映射：
- 正式 Rework 次数／上限：
- 是否为受控能力包：Yes / No
- 能力包边界与包内整改记录：
- 任务名称：
- 专项交付物路径：
- PM Review 路径：
- 执行授权证据核验：用户投递的任务卡路径、专项会话类型、接收时间，以及任务卡要求的投递前单独确认（如适用）。
- 任务验收状态：Accepted / Rework / Blocked
- 资产冻结状态：Frozen / Accepted but Not Frozen / Pass with Conditions / Not Applicable
- 是否允许进入下一任务：Yes / No / Conditional
- 是否允许进入下一阶段：Yes / No / Conditional
- 是否只是后续任务输入：Yes / No
- 实际执行 Agent：Codex / WorkBuddy / Other / Unknown
- Agent 与任务匹配度：High / Medium / Low / Unknown
- 更新时间：

## PM 总结

用 3-8 条概括 PM 对交付物的判断。

## 两层验收治理核对（D-0401 起）

- 违反或满足的 L1 条款：
- 冻结 L2／ABF 条款与矩阵行：
- PM 是否在提交后新增了无法映射到 L1/L2 的标准：Yes / No
- 新发现问题分类：当前任务失败 / 不阻断的 Backlog 候选 / 必须新建任务 / Blocked
- 是否需要实质修改 ABF：Yes / No
- 是否仍满足同任务 Rework 全部条件：Yes / No
- 是否达到两轮正式 Rework 上限：Yes / No
- 终止状态：N/A / Closed — Acceptance Not Met / Superseded
- 新任务触发理由（如适用）：

## P3 快车道 Review（适用时）

仅当任务满足 P3 Engineering Fast Lane 条件时填写；否则写“不适用”。

- 是否适用 P3 快车道：
- 验收结论：
- 测试复跑摘要：
- 是否存在 P0：
- P1 / P2 是否可留在快车道：
- 风险状态是否变化：
- 是否触发用户确认：
- 是否允许继续下一工程补丁：
- 修改文件：
- evidence 路径：
- Agent 适配度记录：
- 是否必须退出快车道：

退出快车道条件：发现 P0、需要关闭风险、需要恢复工程基线、涉及真实数据 / 权限 / 删除 / 导出 / AI 建议可信度核心边界最终判断、涉及技术架构 / 领域模型 / AI 权限边界变化、需要进入下一阶段。

## 角色与关卡验收

- 主责角色覆盖情况：
- 协审角色覆盖情况：
- 已通过关卡：
- 未通过或需后续确认关卡：
- 是否属于关键冻结事项：
- 是否需要独立评审：
- 独立评审路径：
- 独立评审结论：
- 是否允许进入下一任务或下一阶段：

## 验收与冻结区分

- 任务是否验收通过：
- 对应资产是否冻结：
- 冻结范围：
- 未冻结内容：
- 是否允许进入下一任务：
- 是否允许进入下一阶段：
- 是否只是后续任务输入：
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：

## 受控能力包关卡（适用时）

- 是否完成交付前包内自检关卡：
- 干净副本首次／幂等／重启演练结果：
- 原子失败／清理／拒绝与审计追溯结果：
- 验收标准→测试→Evidence 矩阵是否完整：
- 测试／runner、逐项结果、日志／快照、hash／Manifest 与复跑入口是否可复核：
- 历史只读资产及禁止能力关闭态是否已核对：
- 执行侧自检数量与未覆盖项是否如实报告：
- 是否完成包内实现、回归、必要补测、Evidence 与文案对齐：
- 是否首次正式 PM 验收：
- 是否需要／已经进入全新隔离独立复评：
- 是否因 P0/P1、Evidence 冲突、hash 实质变化或独立性不足而必须回包内整改：
- 是否触发新的用户确认：

正式 Rework 口径：仅当 PM 或全新隔离独立复评发现实质 P0/P1、明确合同违反、Evidence 冲突／不可复核、独立性不足、越权／范围扩大、真实能力默认关闭失效，或影响完成定义的 Unknown／Not Implemented 时记录；其他同范围问题应在 PM 提交前由执行侧留在原能力包内修正。

D-0401 起，正式 Rework 还必须能映射到 L1 或冻结 L2，且 ABF 不变、未达到两轮上限。无法映射的普通改进不阻断本轮；需要修改 ABF 或扩大边界时关闭当前任务并新建任务。

## 需要用户确认的事项

列出需要项目负责人确认的问题。每个问题应说明：

- 问题
- PM 建议
- 可选方向
- 不确认的影响

## 整改建议

列出需要专项会话返工或补充的内容。

## 可接受内容

列出已经可以沉淀为项目共识、决策、规则或后续任务输入的内容。

## 不接受或需谨慎内容

列出不应直接采用、表达不准确、范围过大或证据不足的内容。

## 对项目文件的更新建议

说明是否需要更新：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/OPEN_QUESTIONS.md`

## Agent 分派与适配度评估

- 本任务推荐 Agent：
- 本任务实际执行 Agent：
- 是否符合推荐：
- Agent 与任务类型匹配度：High / Medium / Low / Unknown
- 主要优势：
- 主要问题：
- 以后更适合分派给该 Agent 的任务类型：
- 不建议分派给该 Agent 的任务类型：
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：

## 下一步任务建议

列出建议启动、暂停、返工或调整的任务。

## 聊天回复边界

PM Review 文件可以完整，但 PM 主会话在聊天中只输出：

- 验收结论
- 资产状态
- 是否允许下一步 / 下一阶段
- 修改文件
- 需要用户确认的问题

聊天中不复述完整 Review，不重复粘贴任务卡全文，不重复粘贴大段历史决策。若用户需要细节，提供本 Review 路径和关键摘要。
