# LIFEOS-P3-007 PM Review｜P3-001 第三轮 P0 窄范围返工与补测

## 验收信息

- 任务 ID：LIFEOS-P3-007
- 任务名称：P3-001 第三轮 P0 窄范围返工与补测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-007_third_p0_narrow_remediation_and_regression_report.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-007_LIFEOS-P3-007_third_p0_narrow_remediation_and_regression_report_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-007_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Unknown
- Agent 与任务匹配度：Unknown
- 更新时间：2026-08-11

## PM 总结

1. P3-007 已按任务卡完成第三轮 P0 窄范围返工，覆盖 P3-006 指出的四项 P0：恢复包载荷自证、Feedback / Link 写入口绕过、混合 Project state 泄漏、Derivation generation 漏绑。
2. 本地预检已尝试，但因本地模型连接重置而跳过；PM 未以本地预检作为验收依据。
3. PM 复跑 `py_compile` 与 `run_validation.py`，结果为 23 PASS / 0 FAIL / P0=0 / P1=0；evidence 显示 136 / 136 记录断言通过，P3-007 新增四组 51 / 51 断言通过。
4. PM 独立抽样重放 P3-006 的关键失败路径，均已关闭：伪造恢复包载荷不再 returned as restored；Authorization deny 后 `add_feedback()` fail closed 且不改状态；公共写入跨 Project Link fail closed；混合 Project Derivation 不泄漏；generation 变化后旧候选 stale 且生成新身份。
5. 交付物未修改 Stitch、PRD、产品定义、项目账本或冻结资产；未启用真实数据、真实 Vault、真实 Tauri / IPC、云 / 第三方模型、向量、同步、多设备、L3、外部用户或商业化能力。
6. P3-007 可作为第三轮 P0 返工完成证据被接受；但 P3-001 仍不得恢复为工程基线，必须等待后续独立工程复评。

## PM 复核证据

- 基础复跑结果：`{"pass": 23, "fail": 0, "p0_fail": 0, "p1_open": 0}`。
- Evidence 快照：`ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`。
- 机器记录断言：136 / 136 PASS。
- P3-007 新增断言：51 / 51 PASS。
- 本地预检：Skipped / Local Model Unavailable，错误为 `[Errno 54] Connection reset by peer`。
- PM 抽样反例结果：
  - `forged_payload_not_returned = true`
  - `feedback_after_deny_fail_closed = true`
  - `cross_project_link_fail_closed = true`
  - `mixed_derivation_no_state_leak = true`
  - `generation_new_identity_old_stale = true`

## 角色与关卡验收

- 主责角色覆盖情况：工程返工负责人 / 技术架构负责人覆盖充分，四项 P0 均有代码层修复、自动回归和 evidence。
- 协审角色覆盖情况：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM 范围边界均有对应证据。
- 已通过关卡：Gate 1 通过；Gate 2 / Gate 3 / Gate 4 在本次返工 PM 验收层面通过；Gate 5 仅确认未被错误外推。
- 未通过或需后续确认关卡：P3-001 工程基线恢复仍需独立工程复评；Gate 5 结果层不在本任务范围。
- 是否属于关键冻结事项：否。本任务是工程返工验收，不冻结生产 Schema、API、UI、Tauri 配置、导出格式或 SLA。
- 是否需要独立评审：Yes，建议启动 P3-008。
- 独立评审路径：待后续创建 `LIFEOS-P3-008` 独立工程复评。
- 独立评审结论：待后续任务。
- 是否允许进入下一任务或下一阶段：允许在用户确认后进入 P3-008；不允许进入下一阶段或散开开发。

## 验收与冻结区分

- 任务是否验收通过：是，P3-007 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-001 工程基线、生产 Schema、API、UI、真实 Tauri 配置、正式导出格式、生产 SLA、真实数据、真实 Vault、云 / 第三方模型、向量、同步、多设备、L3、外部用户。
- 是否允许进入下一任务：Conditional，需用户确认后启动 P3-008 独立工程复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-007 PM 验收结论，并启动 P3-008 独立工程复评？
   - PM 建议：采纳并启动。
   - 可选方向：A. 采纳并启动 P3-008；B. 要求 P3-007 补充证据；C. 暂停工程线。
   - 不确认的影响：P3-001 继续保持 Rework，后续工程不能以其作为基线。
2. 问题：是否确认 P3-008 通过前，P3-001 仍不得作为工程基线？
   - PM 建议：确认。
   - 可选方向：A. 维持 Rework，等待复评；B. 降低标准提前使用。
   - 不确认的影响：若提前使用，可能把未经独立复验的恢复、导出、写入口和证据 generation 边界带入后续实现。

## 整改建议

本任务暂无必须返工项。后续独立复评应重点检查：

1. 重新构造分字段重签载荷，验证恢复结果只来自当前权威投影。
2. 对 Feedback / Link 写入口逐项构造缺失、deny、revoked、expired、冲突、purpose / location / processor 错配、跨 Project、删除、断源、generation 错配。
3. 构造多种混合 Project Derivation / Feedback / Link 排列，检查所有 state / excluded / control 字段是否零泄漏。
4. 对 Artifact / Source generation 做多次滚动、旧上下文组合和旧恢复包组合，确认旧候选 stale / fail closed，新候选身份清楚。

## 可接受内容

- P3-007 的四项 P0 修复与新增 51 条回归断言可作为 P3-008 输入。
- 23 PASS / 0 FAIL / P0=0 / P1=0 可作为本次返工 PM 复跑结果。
- `MANIFEST.md`、`test_results.json`、`regression_assertions.json` 与 `snapshot_manifest.json` 可作为后续复评优先证据。
- 本次返工未产生能力启用请求、产品方向变化、技术架构变化或 AI 权限边界变化。

## 不接受或需谨慎内容

- 不接受把 P3-007 验收通过等同于 P3-001 恢复工程基线。
- 不接受关闭 R-0041。
- 不接受把合成工程通过外推为真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、同步、多设备、L3 或外部用户能力可用。
- 不接受把当前实现细节外推为生产 Schema、API、导出格式、搜索 SLA 或同步方案冻结。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：P3-007 更新为 Accepted；P3-001 保持 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-007 更新为 Accepted；P3-001 保持 Rework，注明待 P3-008 独立复评。
- `lifeos/DECISION_LOG.md`：新增 D-0145。
- `lifeos/RISK_LOG.md`：R-0041 保持 Open，补充 P3-007 已通过 PM 验收但仍待独立复评。
- `lifeos/OPEN_QUESTIONS.md`：不更新。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-007 并启动 P3-008。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Unknown
- 是否符合推荐：Unknown
- Agent 与任务类型匹配度：Unknown
- 主要优势：交付物与 evidence 质量高，工程修复、回归测试、manifest 更新和边界声明完整。
- 主要问题：当前无法从交付路径确认实际执行 Agent；不更新 Agent 分派评分。
- 以后更适合分派给该 Agent 的任务类型：Unknown
- 不建议分派给该 Agent 的任务类型：Unknown
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-008｜P3-001 第三轮 P0 返工独立工程复评`

P3-008 应只做独立复评，不写新功能、不启用真实能力、不直接恢复工程基线；复评通过后再由 PM 决定是否恢复 P3-001 为后续工程基线候选、是否关闭 R-0041。
