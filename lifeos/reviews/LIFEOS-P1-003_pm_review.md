# LIFEOS-P1-003｜PM 验收意见

## 验收信息

- 任务 ID：LIFEOS-P1-003
- 任务名称：V1 范围冻结条件整改
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P1-003_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：No
- 更新时间：2026-08-08

## PM 总结

1. P1-003 已按任务卡完成 V1 范围冻结条件整改，PM 验收为 Accepted。
2. P1-002 提出的 M-01 至 M-04 已逐项关闭：Must 最小切片、四类命令、Obsidian 条件、最小用户验证合同均已补齐。
3. 本补丁没有重写 P1-001，没有扩大 V1 范围，也没有提前进入首页 / 今日页 PRD、Stitch、技术架构或工程排期，符合补丁 / 条件整改型任务边界。
4. PM 认可 P1-003 对 Must 的收紧：文件最低为文件 / 来源指针及必要元数据；AI 最低围绕 Project 恢复信息与 1 个可核对候选下一步；FTS + 元数据为最低找回路径。
5. PM 认可 P1-003 对四类命令的显式继承：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 不得互相冒充。
6. PM 认可 P1-003 对 Obsidian 的 V1 口径：Should Have + 条件性需求，不作为最小闭环成立的 Must 前提。
7. PM 认可 P1-003 的最小用户验证合同；但该合同不是用户验证结果，Gate 5 仍只是验证合同层通过。
8. PM 建议将 `P1-001 + P1-003` 联合冻结为 V1 范围 V0.1 产品范围与条件合同，但正式冻结需用户确认。

## 角色与关卡验收

- 主责角色覆盖情况：产品架构负责人视角覆盖充分，补丁只处理冻结条件，没有重写或扩大 V1；Must / Should / Could / Non-goals 边界更清楚。
- 协审角色覆盖情况：
  - 用户研究 / 市场验证负责人：形成了可执行的最小用户验证合同，包含招募门槛、真实/等价中断项目、现有工具基线、观察项、反证和失败动作。
  - 体验设计负责人：补丁为首页 / 今日页 PRD 保留了用户主动选择 Project、无可靠建议、证据缺口、权限受限和非焦虑表达等约束。
  - 数据 / 领域模型负责人：继承 Source、Artifact、Derivation、Feedback、Authorization、AuditEntry 与四类命令语义。
  - AI 信任与安全负责人：AI 输出身份、用户确认、撤回、删除、派生失效和高风险边界保持清楚。
  - 技术架构负责人：Obsidian、文件、搜索、AI、导出、审计、撤回 / 删除仍绑定 Spike 和失败降级，没有写成已实现承诺。
- 已通过关卡：
  - Gate 1 产品一致性评审：Pass。
  - Gate 2 数据与来源评审：范围与语义辅助检查 Pass。
  - Gate 3 AI 权限与信任评审：范围与语义辅助检查 Pass。
  - Gate 4 技术可行性评审：验证合同层 Pass；实现层 Not Yet Passed。
  - Gate 5 用户价值验证评审：验证合同层 Pass；一手用户证据 Not Yet Passed。
- 未通过或需后续确认关卡：
  - V1 范围尚未由用户确认冻结。
  - 技术 Spike 尚未实测。
  - 用户验证尚未执行。
- 是否属于关键冻结事项：是。P1-003 是 V1 范围冻结前的条件整改。
- 是否需要独立评审：已由 P1-002 完成独立评审，本任务为针对性条件整改，不再要求新增独立评审。
- 独立评审路径：`lifeos/reviews/LIFEOS-P1-002_v1_scope_independent_review.md`
- 独立评审结论：Pass with Conditions，条件已由 P1-003 补齐，待用户确认冻结。
- 是否允许进入下一任务或下一阶段：用户确认冻结后，允许启动 P1-004 首页 / 今日页 PRD；不允许进入 Stage 2 或 MVP 开发。

## 验收与冻结区分

- 任务是否验收通过：是，LIFEOS-P1-003 Accepted。
- 对应资产是否冻结：否，当前为 Accepted but Not Frozen，等待用户确认冻结。
- 建议冻结范围：`P1-001 + P1-003` 联合构成 V1 范围 V0.1 产品范围与条件合同，包括一句话范围、目标用户 / 第一场景 / 价值排序、经补丁收紧的 MoSCoW、Non-goals、条件性需求 / Spike 依赖 / 失败降级、首页 / 今日页范围输入边界、指标框架与最小用户验证合同、四类命令在 V1 范围层的继承。
- 未冻结内容：完整 V1 PRD、信息架构、详细交互、首页 / 今日页 PRD、Stitch、用户验证结果、样本量与数字阈值、Obsidian 实现、Spike 结果、数据库/API/同步/搜索/导出/清理实现、技术栈/架构、任一 L3 上线范围、删除/备份/第三方 SLA、供应商能力、工程排期、Stage 2 / Stage 3 准入。
- 是否允许进入下一任务：Conditional。仅在用户确认冻结 V1 范围后，启动 P1-004 首页 / 今日页 PRD。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：否。它是 V1 范围冻结补丁。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是，V1 范围更新为 Accepted but Not Frozen，下一动作为用户确认是否冻结。

## 需要用户确认的事项

### 1. 是否冻结 V1 范围 V0.1？

- PM 建议：冻结。
- 冻结方式：将 `LIFEOS-P1-001` 与 `LIFEOS-P1-003` 联合冻结为 V1 范围 V0.1 产品范围与条件合同。
- 可选方向：
  - A：采纳，冻结并继续。
  - B：暂不冻结，要求补充说明。
  - C：返工 P1-003。
- 不确认的影响：P1-004 首页 / 今日页 PRD 不建议启动。

### 2. 是否确认冻结边界？

- PM 建议：确认冻结只覆盖产品范围与条件合同，不覆盖 PRD、交互、Stitch、技术实现、用户验证结果、Spike 结果、架构或开发准入。
- 可选方向：
  - A：确认该冻结边界。
  - B：要求等完整 V1 PRD 后再冻结范围。
  - C：扩大冻结范围。
- 不确认的影响：后续容易再次出现“范围冻结 = 可以开发”的误解。

### 3. 是否确认冻结后下一步为 P1-004 首页 / 今日页 PRD？

- PM 建议：确认。V1 范围冻结后，下一步进入首页 / 今日页 PRD，但仍不修改 Stitch。
- 可选方向：
  - A：确认，冻结后启动 P1-004。
  - B：冻结后先做信息架构。
  - C：冻结后先做用户验证计划细化。
- 不确认的影响：Stage 1 后续定义线无法继续有序推进。

## 整改建议

无需返工。

若用户选择冻结，PM 后续应：

1. 将 V1 范围在 `FREEZE_STATUS.md` 标记为 Frozen。
2. 在 `DECISION_LOG.md` 记录 V1 范围 V0.1 冻结决策。
3. 将 P1-004 更新为 Ready，并创建首页 / 今日页 PRD 任务卡。
4. 将 `PROJECT_CONTEXT.md` 更新为继承 V1 范围冻结基线。

## 可接受内容

可以沉淀为项目共识和后续输入的内容：

1. V1 Must 最小范围合同。
2. 文件 / 来源指针与完整文件处理的边界。
3. AI 最低产出：Project 恢复信息 + 1 个可核对候选下一步。
4. FTS + 元数据作为最低找回路径。
5. 四类命令范围级约束。
6. Obsidian 为 Should Have + 条件性需求。
7. 最小用户验证合同。
8. `P1-001 + P1-003` 联合冻结建议。

## 不接受或需谨慎内容

1. 不得把 P1-003 任务 Accepted 解释为 V1 范围已经 Frozen。
2. 不得把用户验证合同解释为用户验证结果。
3. 不得把 Obsidian 静默升级为 Must。
4. 不得把 AI 摘要、分类、关联、今日重点和下一步扩成五个完整 Must 功能面。
5. 不得把文件 / 来源指针扩成完整文件系统或全格式解析。
6. 不得将本次冻结扩展到 PRD、交互、Stitch、技术架构或开发准入。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：用户确认冻结后更新；当前暂不更新。
- `lifeos/PM_OPERATING_MODEL.md`：无需更新。
- `lifeos/TASK_REGISTRY.md`：将 LIFEOS-P1-003 更新为 Accepted；用户确认冻结后将 LIFEOS-P1-004 更新为 Ready。
- `lifeos/DECISION_LOG.md`：记录接受 P1-003；用户确认冻结后再记录 Frozen 决策。
- `lifeos/RISK_LOG.md`：暂无新增风险类型。
- `lifeos/OPEN_QUESTIONS.md`：暂无必须新增；冻结确认问题由本 PM Review 承载。
- `lifeos/FREEZE_STATUS.md`：V1 范围更新为 Accepted but Not Frozen，下一动作为用户确认是否冻结。

## 下一步任务建议

PM 建议：

1. 用户确认“采纳，冻结并继续”。
2. PM 将 `P1-001 + P1-003` 冻结为 V1 范围 V0.1。
3. PM 创建 `LIFEOS-P1-004｜首页 / 今日页 PRD` 任务卡。
4. 新专项会话执行 P1-004；仍不修改 Stitch。
