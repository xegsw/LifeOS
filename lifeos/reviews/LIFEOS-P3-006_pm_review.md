# LIFEOS-P3-006 PM Review｜P3-001 第二轮 P0 返工独立工程复评

## 验收信息

- 任务 ID：LIFEOS-P3-006
- 任务名称：P3-001 第二轮 P0 返工独立工程复评
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-006_LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-006_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Unknown
- Agent 与任务匹配度：Unknown
- 更新时间：2026-08-11

## PM 总结

1. P3-006 已按任务卡完成独立工程复评，覆盖基础复跑、P3-004 三项新增 P0 反例、P3-002 四项历史 P0 回归、新绕路 / 过拟合检查、H1-H9 / T-ARCH / 能力启用门对照。
2. 复评结论为 `Rework`。该结论不是泛化质疑，而是明确指出 4 项 P0、2 项 P1、2 项 P2，并说明 P3-001 不应恢复为后续工程基线候选，R-0041 不应关闭。
3. 本地预检已尝试，但因本地模型连接重置而跳过；PM 未以本地预检作为验收依据。
4. PM 复跑 `py_compile` 与 `run_validation.py`，结果仍为 19 PASS / 0 FAIL / P0=0 / P1=0，说明 P3-006 的核心判断是“既有验证全绿，但仍有未覆盖 P0”。
5. PM 抽样重放 P3-006 的关键反例，确认恢复包重算 checksum 后的伪造原文会被返回为 restored；Authorization 已 deny 后仍可通过 `add_feedback()` 确认候选；公共 `add_important_link()` 可写入跨 Project Link。
6. P3-006 未修改源码、测试、夹具、README、Stitch、PRD 或项目账本；未启用真实数据、真实 Vault、真实 Tauri / IPC、云 / 第三方模型、向量、同步、多设备、L3、外部用户或商业化能力。
7. P3-006 可作为独立复评任务被接受；但 P3-001 继续保持 Rework，R-0041 继续保持 Open。

## PM 复核证据

- 基础复跑结果：`{"pass": 19, "fail": 0, "p0_fail": 0, "p1_open": 0}`。
- Evidence 快照：`3779cd5efe2d55a5bafe7e78cef4bd8eac230df52b394c14be69fe189965f3a3`。
- 本地预检：Skipped / Local Model Unavailable，错误为 `[Errno 54] Connection reset by peer`。
- PM 抽样反例：
  - `forged_artifact_payload_returned_as_restored = true`
  - `feedback_after_deny_bypasses_gate = true`
  - `cross_project_link_public_write_bypasses_gate = true`

## 角色与关卡验收

- 主责角色覆盖情况：独立工程评审负责人覆盖充分，复评没有停留在原有测试结果，而是构造了变形反例和新入口绕路检查。
- 协审角色覆盖情况：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、PM 边界均有对应检查。
- 已通过关卡：Gate 1 通过；Gate 5 仅确认未被错误外推。
- 未通过或需后续确认关卡：Gate 2 / Gate 3 / Gate 4 未通过，原因是恢复载荷身份、Feedback / Link 写入口授权、混合 Project 状态导出和 generation 证据绑定存在 P0。
- 是否属于关键冻结事项：否。本任务是独立工程复评，不冻结生产 Schema、API、UI、Tauri 配置、导出格式或 SLA。
- 是否需要独立评审：本任务本身即为独立复评。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`
- 独立评审结论：Rework
- 是否允许进入下一任务或下一阶段：允许在用户确认后进入窄范围 P0 返工任务；不允许进入下一阶段或散开开发。

## 验收与冻结区分

- 任务是否验收通过：是，P3-006 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-001 工程基线、生产 Schema、API、UI、真实 Tauri 配置、正式导出格式、生产 SLA、真实数据、真实 Vault、云 / 第三方模型、向量、同步、多设备、L3、外部用户。
- 是否允许进入下一任务：Conditional，需用户确认是否采纳 Rework 结论并启动后续窄范围 P0 返工。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-006 的 `Rework` 结论？
   - PM 建议：采纳。
   - 可选方向：A. 采纳 Rework 并启动后续 P0 返工；B. 要求 P3-006 补充证据；C. 暂停工程线。
   - 不确认的影响：P3-001 继续保持 Rework，后续工程不能以其作为基线。
2. 问题：是否允许 PM 创建并启动后续窄范围 P0 返工任务？
   - PM 建议：允许，建议任务聚焦四项 P0，不散开开发。
   - 可选方向：A. 启动 P3-007 窄范围 P0 返工；B. 先让另一个 Agent 复核 P3-006；C. 暂停。
   - 不确认的影响：R-0041 保持 Open，最小纵切片无法恢复工程基线。

## 整改建议

建议后续返工只覆盖 P3-006 指出的四项 P0：

1. 恢复候选只返回当前权威投影，且逐类验证包内 Artifact / Derivation / Feedback / Link 身份与内容，不信任重算 checksum 后的包内载荷。
2. `add_feedback()` 与 `add_important_link()` 增加对象级当前门、Project 闭包、授权上下文、证据、版本、tombstone、generation 检查。
3. 导出包内所有 `states` / `excluded` / `control_states` 字段也必须执行 Project 与最小披露闭包，不能只约束活跃列表。
4. 将 Artifact / Source generation 纳入 Derivation 依赖身份与消费重检，并把代际变化反例纳入统一自动回归。

## 可接受内容

- P3-006 的 Rework 结论可作为下一轮返工输入。
- 19 PASS / 0 FAIL 可继续作为“既有验证全绿”的事实背景，但不能作为恢复基线依据。
- P3-006 指出的四项 P0 可进入后续任务卡的必须关闭项。
- P3-006 未产生产品方向、技术架构合同、领域语义或 AI 权限边界变化。

## 不接受或需谨慎内容

- 不接受把 P3-005 / P3-006 前的 19 PASS 外推为 P3-001 可恢复工程基线。
- 不接受关闭 R-0041。
- 不接受把合成工程通过外推为真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、同步、多设备、L3 或外部用户能力可用。
- 不接受把当前实现细节外推为生产 Schema、API、导出格式、搜索 SLA 或同步方案冻结。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：P3-006 更新为 Accepted；P3-001 保持 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-006 更新为 Accepted / Rework 结论；P3-001 保持 Rework。
- `lifeos/DECISION_LOG.md`：新增 D-0143。
- `lifeos/RISK_LOG.md`：R-0041 保持 Open，补充 P3-006 发现四项 P0。
- `lifeos/OPEN_QUESTIONS.md`：不更新。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-006 Rework 并启动后续 P0 返工。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：Unknown
- 是否符合推荐：Unknown
- Agent 与任务类型匹配度：Unknown
- 主要优势：交付物具备较强反例攻击能力，能发现固定回归之外的写入口、混合 Project、generation 与恢复载荷问题。
- 主要问题：当前无法从交付物路径判断实际执行 Agent；不更新 Agent 分派评分。
- 以后更适合分派给该 Agent 的任务类型：Unknown
- 不建议分派给该 Agent 的任务类型：Unknown
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-007｜P3-001 第三轮 P0 窄范围返工与补测`

P3-007 应只做 P3-006 四项 P0 的窄范围修复与回归，不散开写新功能、不启用真实能力、不恢复工程基线；完成后仍需 PM 验收与再次独立复评。
