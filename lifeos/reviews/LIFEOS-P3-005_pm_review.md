# LIFEOS-P3-005 PM Review｜P3-001 第二轮 P0 返工与补测

## 验收信息

- 任务 ID：LIFEOS-P3-005
- 任务名称：P3-001 第二轮 P0 返工与补测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-005_LIFEOS-P3-005_second_p0_remediation_and_regression_report_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-005_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-11

## PM 总结

1. P3-005 已按任务卡完成三项新增 P0 的窄范围返工：恢复门读取权威当前状态、Derivation 完整证据依赖持久化与失效传播、显式授权上下文与冲突 fail closed。
2. 本地预检因当前网络沙箱无法访问局域网本地模型而跳过，输出为 `Skipped / Local Model Unavailable`；PM 未以本地预检作为验收依据。
3. PM 复跑 `py_compile` 与 `run_validation.py`。因系统默认 pyc 缓存路径被沙箱拒绝，PM 将 `PYTHONPYCACHEPREFIX` 指向 `/tmp` 后复跑通过；统一验证结果为 19 PASS / 0 FAIL / P0=0 / P1=0。
4. PM 定向重放 P3-004 的三条失败反例，均已关闭：旧 / 伪造控制包不能恢复已撤回对象；撤回非主证据会使候选 stale 且不导出；缺失 / 冲突授权上下文在 can / read / search / recovery / export 入口均 fail closed。
5. 交付物未修改 Stitch、PRD、冻结产品资产、技术架构合同或外部系统；未启用真实数据、真实 Vault、真实 Tauri 文件能力、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
6. P3-005 可作为第二轮返工完成证据被接受；但 P3-001 仍不得恢复为工程基线，必须等待后续独立工程复评。

## PM 复核证据

- 基础复跑结果：`{"pass": 19, "fail": 0, "p0_fail": 0, "p1_open": 0}`。
- Evidence 快照：`3779cd5efe2d55a5bafe7e78cef4bd8eac230df52b394c14be69fe189965f3a3`。
- 记录断言：85 / 85 PASS；其中 P3-005 新增三组对抗回归为 23 / 23 PASS。
- PM 直接反例验证：
  - `restore_candidates()` 读取当前权威状态，撤回后的 `artifact-stop` 未恢复。
  - 修改旧包控制字段并重算 checksum 后，`artifact-stop` 仍未恢复。
  - 撤回 `artifact-decision` 后，候选状态为 `stale`，且不再导出。
  - 缺失授权上下文直接读取返回 None；插入 allow / deny 冲突授权后，can / read / search / recovery / export 均拒绝。

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人 / 技术架构负责人覆盖充分，三项 P0 均有实现层修复、自动回归和 evidence。
- 协审角色覆盖情况：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM 范围检查均有对应证据。
- 已通过关卡：Gate 1 范围检查通过；Gate 2 / Gate 3 / Gate 4 在本次返工 PM 验收层面通过。
- 未通过或需后续确认关卡：P3-001 工程基线恢复仍需独立工程复评；Gate 5 结果层不在本任务范围。
- 是否属于关键冻结事项：否。本任务是工程返工验收，不冻结生产 Schema、API、UI、Tauri 配置、导出格式或 SLA。
- 是否需要独立评审：Yes，建议启动 P3-006。
- 独立评审路径：待后续创建 `LIFEOS-P3-006` 独立工程复评。
- 独立评审结论：待后续任务。
- 是否允许进入下一任务或下一阶段：允许在用户确认后进入 P3-006；不允许进入下一阶段或散开开发。

## 验收与冻结区分

- 任务是否验收通过：是，P3-005 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-001 工程基线、生产 Schema、API、UI、真实 Tauri 配置、正式导出格式、生产 SLA、真实数据、真实 Vault、云 / 第三方模型、向量、同步、多设备、L3、外部用户。
- 是否允许进入下一任务：Conditional，需用户确认后启动 P3-006 独立工程复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-005 PM 验收结论，并启动 P3-006 独立工程复评？
   - PM 建议：采纳并启动。
   - 可选方向：A. 采纳并启动 P3-006；B. 要求 P3-005 补充证据；C. 暂停工程线。
   - 不确认的影响：P3-001 继续保持 Rework，后续工程不能以其作为基线。
2. 问题：是否确认 P3-006 通过前，P3-001 仍不得作为工程基线？
   - PM 建议：确认。
   - 可选方向：A. 维持 Rework，等待复评；B. 降低标准提前使用。
   - 不确认的影响：若提前使用，可能把未经独立复验的恢复、证据依赖和授权边界带入后续实现。

## 整改建议

本任务暂无必须返工项。后续独立复评应重点检查：

- 从实现外部重新构造旧包、伪造控制字段和重算 checksum 的恢复反例。
- 分别撤回候选证据集合中的每一项，检查建议、导出、恢复、Feedback 和 Link 是否完整阻断。
- 构造缺失、重复 allow、allow / deny 冲突、未知 decision、过期、generation / source_generation 错配与维度错配授权。
- 从 `read_artifact()`、`recovery_package()`、`search()`、`export_test_package()`、`restore_candidates()` 等真实消费入口重放反例。

## 可接受内容

- P3-005 的三项 P0 修复与回归测试可作为 P3-006 输入。
- `19 PASS / 0 FAIL / P0=0 / P1=0` 可作为本次返工 PM 复跑结果。
- `MANIFEST.md`、`test_results.json`、`regression_assertions.json` 与 `snapshot_manifest.json` 可作为后续复评优先证据。
- 本次返工未产生能力启用请求、产品方向变化、技术架构变化或 AI 权限边界变化。

## 不接受或需谨慎内容

- 不接受把 P3-005 验收通过等同于 P3-001 恢复工程基线。
- 不接受关闭 R-0041。
- 不接受把合成工程通过外推为真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、同步、多设备、L3 或外部用户能力可用。
- 不接受把本次实现细节外推为生产 Schema、API、导出格式、搜索 SLA 或同步方案冻结。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：P3-005 更新为 Accepted，P3-001 保持 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-005 更新为 Accepted；P3-001 保持 Rework，注明待 P3-006 独立复评。
- `lifeos/DECISION_LOG.md`：新增 D-0140。
- `lifeos/RISK_LOG.md`：R-0041 保持 Open，补充 P3-005 已通过 PM 验收但仍待独立复评。
- `lifeos/OPEN_QUESTIONS.md`：不更新。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-005 并启动 P3-006。

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-006｜P3-001 第二轮 P0 返工独立工程复评`

P3-006 应只做独立复评，不写新功能、不启用真实能力、不直接恢复工程基线；复评通过后再由 PM 决定是否恢复 P3-001 为后续工程基线候选、是否关闭 R-0041。
