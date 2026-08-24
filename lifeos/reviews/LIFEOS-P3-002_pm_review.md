# LIFEOS-P3-002 PM Review｜合成数据最小纵向闭环独立工程评审

## 验收信息

- 任务 ID：LIFEOS-P3-002
- 任务名称：合成数据最小纵向闭环独立工程评审
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-002_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Rework
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P3-002 独立工程评审已完成任务目标：复跑 P3-001、抽查代码 / 测试 / evidence，并给出独立结论。
2. PM 接受 P3-002 的评审结论：`Rework`。P3-001 暂不得作为后续 MVP 工程基线输入。
3. 独立评审确认原验证器仍为 11 PASS / 0 FAIL / P0=0，但额外对抗检查发现 4 项 P0：跨 Project 导出泄漏、处理撤回后恢复复活、已确认候选被静默重置、Authorization location / processor 错配仍可消费。
4. 这些问题击穿 H2、H4、H5、H9 与 `T-ARCH` 的消费重检合同，按 P2-019 / P2-020 规则不得判为 Pass with Conditions。
5. 本次评审未修改代码、未启用真实能力、未冻结生产资产；下一步必须先做窄范围返工补测，而不是扩展 UI、真实数据、Tauri、云模型或向量。

## 角色与关卡验收

- 主责角色覆盖情况：Pass。独立工程评审覆盖复跑、代码抽查、测试覆盖、证据质量、P0/P1/P2 问题和后续建议。
- 协审角色覆盖情况：Pass。技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、体验设计、PM 边界均有明确判断。
- 已通过关卡：Gate 1。
- 未通过或需后续确认关卡：Gate 2、Gate 3、Gate 4 未通过；Gate 5 未评结果层。
- 是否属于关键冻结事项：否，但影响 P3-001 是否可作为后续工程基线。
- 是否需要独立评审：已完成，本任务即独立评审。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`
- 独立评审结论：Rework。
- 是否允许进入下一任务或下一阶段：允许在用户确认后启动 P3-003 窄范围返工 / 补测；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：是，P3-002 评审任务 Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无新增冻结。
- 未冻结内容：P3-001 工程实现、测试、Schema、API、UI、Tauri capability、导出格式、生产 SLA、最终工程目录结构、真实数据、真实 Vault、云 / 第三方模型、向量、L3、外部用户。
- 是否允许进入下一任务：Conditional。用户确认采纳 P3-002 的 Rework 结论后，启动 P3-003。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是，P3-001 更新为 Rework，P3-002 更新为 Accepted。

## 需要用户确认的事项

1. 问题：是否采纳 P3-002 的 `Rework` 结论？
   - PM 建议：采纳。
   - 可选方向：A. 采纳并启动 P3-003 窄范围返工 / 补测；B. 要求 P3-002 补充评审证据；C. 暂停工程线。
   - 不确认的影响：P3-001 的基线状态无法明确，后续工程不应继续叠加。

2. 问题：是否确认 P3-003 只关闭 4 个 P0 和必要补测，不扩展 UI、真实数据、真实 Tauri、云模型、向量或 L3？
   - PM 建议：确认。
   - 可选方向：A. 严格窄修；B. 合并更大工程重构，但风险和范围会明显上升。
   - 不确认的影响：返工任务容易变成重构或新功能，继续扩大未验证面。

## 整改建议

建议创建 `LIFEOS-P3-003` 窄范围返工 / 补测任务，必须关闭：

- Project / 授权约束下的导出过滤，避免 Feedback / Link 跨 Project 泄漏；
- 恢复门统一消费撤回、断源、删除、当前授权与 generation，避免旧包复活；
- 已确认候选状态保护，避免再次建议静默重置；
- Authorization 的 location / processor 完整 fail-closed 校验；
- 补充双 Project、旧包 + 四命令、确认后重复建议、错配授权、强杀 / 提交边界和真实断言驱动 evidence。

## 可接受内容

- P3-002 对 P3-001 的 Rework 判断。
- P3-001 局部可保留探索材料：权威捕获事务轮廓、不可变版本触发器、FTS 回连、outbox 同事务登记、stale lease 拒绝、合成夹具。
- “P3-001 暂不得作为后续工程基线”的边界。

## 不接受或需谨慎内容

- 不得继续把 P3-001 当作通过独立评审的工程基线。
- 不得把原 11 PASS 当作 P2-019 DoD 通过。
- 不得把 Rework 弱化为 P1 条件项；4 个 P0 必须关闭后再复评。
- 不得启用真实数据、真实 Vault、真实 Tauri / IPC、云 / 第三方模型、向量、L3 或外部用户。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：无需更新。
- `lifeos/PM_OPERATING_MODEL.md`：无需更新。
- `lifeos/TASK_REGISTRY.md`：P3-002 更新为 Accepted；P3-001 标记为 Rework。
- `lifeos/DECISION_LOG.md`：新增 D-0134。
- `lifeos/RISK_LOG.md`：新增 R-0041，记录 P3-001 自测通过但独立评审发现 P0 漏洞的工程验收风险。
- `lifeos/OPEN_QUESTIONS.md`：无需更新。

## 下一步任务建议

用户确认采纳后，建议启动：

- `LIFEOS-P3-003`：P3-001 四项 P0 返工与补测

P3-003 应是补丁 / 条件整改型工程任务，只允许修复 P3-002 指出的 P0 / 必要 P1 测试证据，不允许扩展真实能力或产品 UI。

## 聊天回复边界

PM 主会话在聊天中只输出验收结论、资产状态、是否允许下一步 / 下一阶段、修改文件、需要用户确认的问题；不复述完整 Review。
