# LIFEOS-P3-004 PM Review｜P3-001 四项 P0 返工独立工程复评

## 验收信息

- 任务 ID：LIFEOS-P3-004
- 任务名称：P3-001 四项 P0 返工独立工程复评
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-004_LIFEOS-P3-004_p0_remediation_independent_engineering_re_review_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-004_pm_review.md`
- 任务验收状态：Accepted
- 独立复评结论：Rework
- P3-001 资产状态：Rework
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P3-004 已完成任务卡要求的独立工程复评：复跑验证、抽查 evidence、重放四个原始 P0 反例、检查新绕路和过拟合，并明确给出 Rework 结论。
2. PM 复跑 `py_compile` 与 `run_validation.py`，结果仍为 16 PASS / 0 FAIL / P0=0 / P1=0，与 P3-003、P3-004 报告一致。
3. PM 定向复现 P3-004 指出的三项新增 P0：旧控制包 / 重算校验控制包可自证恢复对象；候选未持久化完整证据依赖，撤回非主证据后候选仍活跃并可导出；真实消费入口依赖默认授权上下文，冲突 Authorization 仍可放行。
4. 因存在新增 P0，P3-001 不得恢复为后续工程基线候选，R-0041 不得关闭。
5. 本复评任务本身可验收为 Accepted；但其结论是 Rework，不是 Pass / Pass with Conditions。
6. P3-004 未修改产品方向、V1 范围、技术架构合同、核心领域语义、AI 权限边界、Stitch 或真实外部能力。

## PM 复核证据

- 基础复跑结果：`{"pass": 16, "fail": 0, "p0_fail": 0, "p1_open": 0}`。
- 直接反例验证：
  - `restore_candidates(stale, stale)` 可恢复已撤回对象。
  - 重算公开 SHA-256 后的伪造控制包仍可恢复已撤回对象。
  - 撤回 `artifact-decision` 后，依赖该证据集合生成的候选仍为 `unconfirmed` 且继续出现在导出 `derivations` 中。
  - 插入同 subject 的冲突 deny Authorization 后，`can_consume()` 与 `read_artifact()` 仍返回可消费。
- 本地预检结论：需要人工复核；PM 已完成复核，并确认 Rework 结论成立。

## 角色与关卡验收

- 主责角色覆盖情况：覆盖充分，独立指出 P3-003 之外的绕路问题。
- 协审角色覆盖情况：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、PM 范围均有判断。
- 已通过关卡：Gate 1 范围检查通过；Gate 5 未被错误外推。
- 未通过或需后续确认关卡：Gate 2、Gate 3、Gate 4 因新增 P0 未通过。
- 是否属于关键冻结事项：否；本任务不冻结生产资产。
- 是否需要独立评审：本任务本身即独立工程复评。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- 独立评审结论：Rework。
- 是否允许进入下一任务或下一阶段：允许用户确认后进入 P3-005 窄范围二次返工；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：是，P3-004 复评任务 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：P3-001 工程基线、生产 Schema、API、UI、真实 Tauri 配置、正式导出格式、生产 SLA、真实数据、真实 Vault、云 / 第三方模型、向量、同步、多设备、L3、外部用户。
- 是否允许进入下一任务：Conditional，需用户确认后启动 P3-005。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-004 的 Rework 结论？
   - PM 建议：采纳。
   - 可选方向：A. 采纳并启动 P3-005；B. 要求 P3-004 补充复评证据；C. 暂停工程线。
   - 不确认的影响：P3-001 继续保持 Rework，无法作为后续工程基线。
2. 问题：是否授权创建 P3-005 窄范围二次返工任务？
   - PM 建议：授权。
   - 可选方向：A. 创建 P3-005；B. 先要求人工讨论整改边界；C. 暂停。
   - 不确认的影响：新增三项 P0 不会进入可执行整改队列。

## 整改建议

建议 P3-005 仅覆盖以下三项 P0：

1. 恢复候选必须在可信执行边界读取权威当前控制状态，不得由旧包或可重算校验控制包自证。
2. Derivation 必须持久化完整证据依赖，并在任一证据撤回 / 删除 / 断源 / 授权失效后失效或阻断导出。
3. 所有消费入口必须显式传入授权上下文；多条 Authorization 冲突、缺失或歧义必须 fail closed。

## 可接受内容

- P3-004 作为独立复评任务的完整性可接受。
- P3-004 的 Rework 结论可作为后续 P3-005 的直接输入。
- P3-004 的三项新增 P0 可进入 R-0041 的补充风险说明。

## 不接受或需谨慎内容

- 不接受将 P3-001 恢复为工程基线候选。
- 不接受关闭 R-0041。
- 不接受把当前 16 PASS / 0 FAIL 外推为 H4、H5、H9 和 `T-ARCH` 通过。
- 不接受散开开发 UI、真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、同步、多设备、L3 或外部用户能力。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：不更新。
- `lifeos/PM_OPERATING_MODEL.md`：不更新。
- `lifeos/TASK_REGISTRY.md`：P3-004 更新为 Accepted，P3-001 保持 Rework。
- `lifeos/FREEZE_STATUS.md`：P3-004 更新为 Accepted / Rework conclusion，P3-001 保持 Rework。
- `lifeos/DECISION_LOG.md`：新增 D-0138。
- `lifeos/RISK_LOG.md`：R-0041 保持 Open，补充三项新增 P0。
- `lifeos/OPEN_QUESTIONS.md`：不更新。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-004 Rework 并启动 P3-005。

## 下一步任务建议

建议用户确认后启动：

- `LIFEOS-P3-005｜P3-001 第二轮 P0 返工与补测`

P3-005 不应扩展范围，只允许在既有合成工程目录内修复 P3-004 指出的三项 P0，并补入自动回归与 evidence。P3-005 完成后仍需 PM 验收和再次独立复评。
