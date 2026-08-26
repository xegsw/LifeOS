# LifeOS 风险触发独立评审模板 V2

仅用于 L3/Gate，或 PM 已记录具体触发事实的 L1/L2。普通任务不得仅因 P0、Tauri/IPC、任务编号或历史惯例自动使用本模板。

## 评审信息

- 对应任务 ID：
- 是否为受控能力包：Yes / No
- 能力包边界／被评审最终 hash：
- 对应交付物路径：
- 独立评审角色：
- 协审视角：
- 评审关卡：
- 独立评审路径：
- 评审结论：Pass / Pass with Conditions / Rework / Blocked
- 风险等级：L1 / L2 / L3 / Gate
- 独立评审触发事实：强制关卡 / Evidence不可复算 / 污染或越权 / 长期冻结基线 / Closure后争议 / 用户要求

## 独立性与回流规则

- 执行侧与评审侧是否隔离：
- 是否只评审能力包的最终 Evidence／hash：
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：
- 是否可验证 runner 未导入、调用或复制执行侧测试：
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：
- 若需整改：不得创建微型整改任务；回到同一能力包后必须重新独立复评。
- 更新时间：

P3-074 起，独立 Review 的 Evidence 必须保留 task-local runner 源码、逐项结构化结果、hash／Manifest 与复跑说明；仅保存 runner hash 或汇总 PASS 数不足以证明独立性或覆盖。

## 本地 `file:` 动态 Evidence 预检（仅适用时）

- 指定浏览器与 bundle id：Google Chrome（`com.google.Chrome`），通过 Computer Use 的 `@oai/sky` 正常控制。
- task-local `file:` 入口／副本 hash：
- 新 Chrome 标签页首次预检：Pass / Fail；时间与 Evidence：
- 若首次失败，新 Chrome 标签页第二次预检：Pass / Fail；时间与 Evidence：
- In-app Browser 结果（如有）：仅工具限制记录，不作为 Blocked 依据。
- 动态矩阵是否只在 Chrome 预检通过后开始：Yes / No。
- 若候选 Blocked：两次 Chrome 正常加载失败是否均有记录，且未使用 HTTP／网络／CDP／命令行浏览器／策略绕过：Yes / No / N/A。

若本任务来自 Closure Cycle：原 Review 与 Evidence 是否只读保留：Yes / No；本轮目录：。

## 评审摘要

用 3-8 条概括最重要判断。

## 已通过内容

列出交付物中可以接受、可进入项目共识或后续输入的内容。

## 关键问题

列出影响冻结、进入下一阶段或开发实现的问题。

## Closure List

列出冻结前必须修改或补充的内容。

同一 Task Contract 内的问题回到原任务 Closure Cycle；只有合同或边界必须变化时才建议新任务。

## 条件通过项

若结论为 Pass with Conditions，列出条件、适用范围和失效条件。

## 关卡检查

逐项说明本次涉及的 Gate 是否通过：

- Gate 1 产品一致性评审：
- Gate 2 数据与来源评审：
- Gate 3 AI 权限与信任评审：
- Gate 4 技术可行性评审：
- Gate 5 用户价值验证评审：

## 风险

列出应进入 `lifeos/RISK_LOG.md` 或需要 PM 关注的风险。

## 需要 PM 决策

列出必须由 PM 主会话或用户确认的问题。

## 最终建议

说明是否建议冻结、返工、补充验证，或允许进入下一任务/下一阶段。
