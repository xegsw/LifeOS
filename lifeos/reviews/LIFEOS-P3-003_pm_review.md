# LIFEOS-P3-003 PM Review｜P3-001 四项 P0 返工与补测

## 验收信息

- 任务 ID：LIFEOS-P3-003
- 任务名称：P3-001 四项 P0 返工与补测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-003_p0_remediation_and_regression_report.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-003_LIFEOS-P3-003_p0_remediation_and_regression_report_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-003_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P3-003 已按任务卡完成四项 P0 窄范围返工：跨 Project 导出泄漏、撤回后旧包恢复复活、确认状态静默重置、Authorization location / processor 错配仍可消费。
2. PM 复跑 `py_compile` 与 `run_validation.py`，结果为 16 PASS / 0 FAIL / P0 失败 0 / P1 遗留 0。
3. PM 抽查 evidence：`test_results.json`、`regression_assertions.json`、`snapshot_manifest.json` 与 `test_run.log` 均支持报告结论；回归断言为 62 / 62 PASS，工程快照为 `285c74ac96f2ea978c91baaf8d526c61fbbb944407f21e221aabe1556a21860c`。
4. PM 另行重放四个原始 P0 反例，结论为 `direct_counterexample_replay=PASS`：Project B 未进入 Project A 导出闭包、撤回后旧包不复活、已确认候选不被重复建议重置、授权 location 错配 fail closed。
5. 交付物未修改 Stitch、PRD、冻结产品资产、技术架构合同或外部系统；未启用真实数据、真实 Vault、真实 Tauri 文件能力、云 / 第三方模型、向量、L3 或外部用户。
6. P3-003 可作为返工完成证据被接受；但 P3-001 仍不得恢复为工程基线，必须等待后续独立工程复评。

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人 / 技术架构负责人覆盖充分，四项 P0 均有实现修复、自动回归和证据。
- 协审角色覆盖情况：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM 范围检查均有对应证据。
- 已通过关卡：Gate 1 范围检查通过；Gate 2 / Gate 3 / Gate 4 在本次返工 PM 验收层面通过。
- 未通过或需后续确认关卡：P3-001 工程基线恢复仍需独立工程复评；Gate 5 结果层不在本任务范围。
- 是否属于关键冻结事项：否。本任务是工程返工验收，不冻结生产 Schema、API、UI、Tauri 配置、导出格式或 SLA。
- 是否需要独立评审：Yes。
- 独立评审路径：建议后续创建 `LIFEOS-P3-004` 独立工程复评。
- 独立评审结论：待后续任务。
- 是否允许进入下一任务或下一阶段：允许在用户确认后进入 P3-004；不允许进入下一阶段或散开开发。

## 验收与冻结区分

- 任务是否验收通过：是，P3-003 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-001 工程基线、生产 Schema、API、UI、真实 Tauri 配置、正式导出格式、生产 SLA、真实数据能力、真实 Vault、云 / 第三方模型、向量、L3、外部用户。
- 是否允许进入下一任务：Conditional，需用户确认后启动 P3-004 独立工程复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，P3-003 更新为 Accepted，但 P3-001 继续保持 Rework。

## 需要用户确认的事项

1. 问题：是否采纳 P3-003 PM 验收结论，并启动 P3-004 独立工程复评？
   - PM 建议：采纳并启动。
   - 可选方向：A. 采纳并启动 P3-004；B. 要求 P3-003 继续补充证据；C. 暂停工程线。
   - 不确认的影响：P3-001 继续停留在 Rework，后续工程不能以其作为基线。
2. 问题：是否确认 P3-004 通过前，P3-001 仍不得作为工程基线？
   - PM 建议：确认。
   - 可选方向：A. 维持 Rework，等待复评；B. 降低标准提前使用。
   - 不确认的影响：若提前使用，可能把已修补但未独立复验的关键安全边界带入后续实现。

## 整改建议

本任务暂无必须返工项。后续独立复评应重点检查：

- 四个原始 P0 反例是否仍可被独立重放。
- 新增测试是否真实断言关键不变量，而不是只验证固定摘要或 happy path。
- restore / export / suggestion / authorization 四个入口是否存在新的绕路消费路径。
- Evidence 快照与源码、测试、日志是否一致。

## 可接受内容

- 四项 P0 的根因、修复和回归测试可作为 P3-004 输入。
- `16 PASS / 0 FAIL / P0=0 / P1=0` 可作为本次返工 PM 复跑结果。
- `regression_assertions.json`、`snapshot_manifest.json` 与 `MANIFEST.md` 可作为后续复评优先证据。
- 本次返工未产生能力启用请求、产品方向变化、技术架构变化或 AI 权限边界变化。

## 不接受或需谨慎内容

- 不接受把 P3-003 验收通过等同于 P3-001 恢复工程基线。
- 不接受把合成工程通过外推为真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、L3 或外部用户能力可用。
- 不接受把本次实现细节外推为生产 Schema、API、导出格式、搜索 SLA 或同步方案冻结。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：将 P3-003 更新为 Accepted，追加 D-0136。
- `lifeos/FREEZE_STATUS.md`：将 P3-003 更新为 Accepted；P3-001 保持 Rework，注明返工已 PM 验收但仍待独立复评。
- `lifeos/DECISION_LOG.md`：新增 D-0136。
- `lifeos/RISK_LOG.md`：R-0041 保持 Open，补充 P3-003 已 PM 验收，待 P3-004 独立复评。
- `lifeos/OPEN_QUESTIONS.md`：不更新。
- `lifeos/CURRENT_STATUS.md`：更新当前等待用户确认与下一步。

## 下一步任务建议

建议用户确认采纳 P3-003 后，启动：

- `LIFEOS-P3-004｜P3-001 四项 P0 返工独立工程复评`

P3-004 应只做独立复评，不写新功能、不启用真实能力、不直接恢复工程基线；复评通过后再由 PM 决定是否恢复 P3-001 为后续工程基线候选。
