# LIFEOS-P3-024 PM Review：真实 Tauri / IPC 集成前置验证任务规划

## 验收信息

- 任务 ID：LIFEOS-P3-024
- 任务名称：真实 Tauri / IPC 集成前置验证任务规划
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-024_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Planning Input
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy / Unknown
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

- P3-024 按任务卡完成真实 Tauri / IPC 集成前置验证规划，覆盖 R-0040 真实集成层风险、P2-015 已验证 / 未验证边界、最小验证矩阵、P0/P1/P2 判定、evidence 包结构、失败降级和后续任务建议。
- 交付物没有安装、配置或运行真实 Tauri，没有修改工程代码、Stitch、evidence 或 PM 账本，没有关闭 R-0040，也没有启用真实能力。
- PM 接受其核心结论：P2-015 后端合同不能外推为真实 Tauri / IPC 安全；未来真实验证必须覆盖 capability / permission、plugin / invoke、Renderer / CSP、debug / release、目标平台路径、IPC 参数、Project / auth / tombstone / generation / evidence 重检和禁用能力负测。
- PM 对下一步顺序做一处约束：不建议直接启动实际验证任务；应先启动生产 Schema / API 设计任务，明确 IPC 命令签名、参数结构、错误码和 SQLite Schema 面向生产的边界，再进入最小 Tauri 壳搭建和矩阵迁移验证。
- 本地预检因本地模型连接重置跳过，不作为验收依据。

## P3 快车道 Review（适用时）

- 是否适用 P3 快车道：No
- 原因：本任务涉及 R-0040 真实能力启用前置规划，不属于 P3 快车道工程补丁；不得用快车道跳过 PM / 用户确认或真实能力启用门。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖。交付物给出 9 类攻击面、26 项矩阵、P0/P1/P2 判定与 P2-015 迁移路径。
- 协审角色覆盖情况：已覆盖。交付物检查了 IPC、path scope、Renderer、debug / release 差异对用户授权、证据链、tombstone、generation 和 Project 边界的绕过风险。
- 已通过关卡：Gate 3 AI 权限与信任评审 Pass with Conditions；Gate 4 技术可行性评审 Pass with Conditions。
- 未通过或需后续确认关卡：真实 Tauri / IPC 尚未验证；R-0040 不关闭；真实能力不启用。
- 是否属于关键冻结事项：No，本任务为规划输入，不冻结 Tauri 配置、Schema / API、工程基线或阶段状态。
- 是否需要独立评审：本任务自身为独立规划；未来实际验证和 R-0040 关闭仍需独立复评与用户确认。
- 独立评审路径：`lifeos/deliverables/LIFEOS-P3-024_true_tauri_ipc_preflight_validation_plan.md`
- 独立评审结论：建议规划后进入“生产 Schema/API → 最小 Tauri 壳 → 矩阵迁移验证 → R-0040 关闭评估”的顺序。
- 是否允许进入下一任务或下一阶段：允许进入下一规划任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：真实 Tauri / IPC 配置、capability / permission、plugin / invoke、Renderer / CSP、debug / release 包、目标平台范围、生产 Schema / API、导出格式、R-0040 状态、工程基线冻结、下一阶段。
- 是否允许进入下一任务：Conditional。PM 建议下一任务为生产 Schema / API 设计，而不是实际 Tauri 验证。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，更新为 Accepted / Planning Input。

## 需要用户确认的事项

### 问题：是否采纳 PM 的下一步顺序

- PM 建议：采纳 P3-024 作为规划输入，并启动 `LIFEOS-P3-025` 生产 Schema / API 设计任务；暂不安装、配置或运行真实 Tauri。
- 可选方向：
  - A：按 PM 建议，先做生产 Schema / API 设计。（推荐）
  - B：先做 UI 壳规划，再做 Schema / API。
  - C：直接启动最小 Tauri 壳搭建与验证准备；PM 不推荐，因为命令签名和 Schema 边界尚未定清。
- 不确认的影响：P3-024 可以作为规划输入，但 PM 暂不应启动依赖其建议的后续真实验证链路。

## 整改建议

无强制返工。若后续进入实际验证任务，需要在任务卡中进一步明确目标平台范围（macOS-only 或 macOS + Windows + Linux）、工具链版本、是否允许安装 Tauri、是否允许创建一次性 Tauri 壳目录。

## 可接受内容

- 接受 M-01 至 M-26 作为未来真实 Tauri / IPC 验证矩阵候选。
- 接受 P0/P1/P2 判定标准，尤其是 capability 越权、未知 IPC 未拒绝、路径攻击成功、跨 Project 泄漏、撤回 / 删除复活、禁用能力可调用均为 P0。
- 接受 evidence 包结构建议：MANIFEST、test_results、test_run、test_matrix、debug / release 结果、platform_results、audit_log、privacy_scan、capability_snapshot。
- 接受失败时必须关闭 / 降级 / 回滚，不得放宽 H1-H9 / T-ARCH 合同。

## 不接受或需谨慎内容

- 不接受把“规划完成”解释为“真实 Tauri / IPC 可启用”。
- 不接受在生产 Schema / API 和 IPC 命令签名未定义前直接启动真实验证执行。
- 不接受关闭 R-0040、冻结 Tauri 配置或进入下一阶段。
- 不接受使用真实 Vault、真实用户文件或真实敏感数据作为下一步验证输入。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：将 P3-024 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将 P3-024 更新为 Accepted / Planning Input。
- `lifeos/CURRENT_STATUS.md`：更新当前等待用户确认事项为是否启动 P3-025 生产 Schema / API 设计。
- `lifeos/DECISION_LOG.md`：新增 D-0182，记录 PM 接受 P3-024 和下一步建议。
- `lifeos/RISK_LOG.md`：不更新，R-0040 保持 Open / Conditional。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy / Unknown
- 是否符合推荐：基本符合
- Agent 与任务类型匹配度：High
- 主要优势：矩阵完整、边界克制、没有把规划写成能力启用。
- 主要问题：对“建议立即创建实际验证任务”的措辞需要 PM 加一层顺序约束：先 Schema / API，再壳与验证。
- 以后更适合分派给该 Agent 的任务类型：独立规划、风险矩阵、反例清单、能力启用前置评估。
- 不建议分派给该 Agent 的任务类型：直接工程实现与 evidence 写入。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要。

## 下一步任务建议

建议用户确认后启动 `LIFEOS-P3-025` 生产 Schema / API 设计任务。该任务仍不安装、配置或运行真实 Tauri，不启用真实能力，不关闭 R-0040。

