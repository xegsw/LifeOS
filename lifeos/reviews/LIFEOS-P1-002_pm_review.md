# LIFEOS-P1-002｜PM 验收意见

## 验收信息

- 任务 ID：LIFEOS-P1-002
- 任务名称：V1 范围独立评审
- 专项交付物路径：`lifeos/reviews/LIFEOS-P1-002_v1_scope_independent_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P1-002_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：No
- 更新时间：2026-08-08

## PM 总结

1. P1-002 已完成 V1 范围独立评审任务，结论为 `Pass with Conditions`，PM 验收为 Accepted。
2. 独立评审确认 P1-001 的产品方向、第一目标用户、第一场景、MoSCoW 主结构、Non-goals 和条件性降级路径基本成立，不需要推倒重来。
3. V1 范围当前仍不能冻结。冻结前必须完成 M-01 至 M-04 的有限整改：Must 最小范围合同、四类命令显式继承、Obsidian 优先级与失效条件、最小用户验证合同。
4. 评审提出的最大价值是把“语义完整”压回“V1 最小可验收切片”，避免开发阶段把文件处理、AI 分类/关联、今日智能和 Obsidian 接入误读成全量实现。
5. PM 认可评审对 Obsidian 的判断：Obsidian 应为 Should Have + 条件性需求，不是 V1 最小闭环成立的 Must 前提。
6. PM 认可评审对数据主权底线的判断：基础导出、最小审计、撤回 / 删除应继续保留在 Must，但只冻结最低用户价值合同，不冻结完整后台、日志架构、物理清理 SLA 或具体实现。
7. 首页 / 今日页 PRD 暂不启动；建议先插入一个有限的 V1 范围冻结条件整改任务。

## 角色与关卡验收

- 主责角色覆盖情况：产品架构负责人视角覆盖充分，明确判断 V1 范围是否服务个人终身外脑、目标用户、第一场景和最小闭环。
- 协审角色覆盖情况：
  - 用户研究 / 市场验证负责人：指出指标框架可用，但缺少最小用户验证合同。
  - 体验设计负责人：指出首页 / 今日页后续必须补空状态、证据不足、权限受限、用户选择 Project 优先权和非焦虑表达。
  - 数据 / 领域模型负责人：指出文件 / 来源指针边界、Source/Artifact、Derivation、四类命令和证据状态必须继承。
  - AI 信任与安全负责人：指出“撤回/删除”不可合并表达，AI 候选、确认、纠正、撤回和高风险边界必须延续冻结基线。
  - 技术架构负责人：明确技术可行性仍只是验证合同层通过，未完成实现层 Spike。
- 已通过关卡：
  - Gate 1 产品一致性评审：Pass with Conditions。
  - Gate 2 数据与来源评审：Pass with Conditions。
  - Gate 3 AI 权限与信任评审：Pass with Conditions。
  - Gate 4 技术可行性评审：验证合同层 Pass；实现层 Not Yet Passed。
  - Gate 5 用户价值验证评审：验证框架 Pass with Conditions；一手用户证据未完成。
- 未通过或需后续确认关卡：
  - V1 范围冻结条件尚未完成。
  - 技术 Spike 尚未实测。
  - 用户价值尚未通过真实用户验证。
- 是否属于关键冻结事项：是。V1 范围冻结属于关键冻结事项。
- 是否需要独立评审：已完成。
- 独立评审路径：`lifeos/reviews/LIFEOS-P1-002_v1_scope_independent_review.md`
- 独立评审结论：Pass with Conditions。
- 是否允许进入下一任务或下一阶段：允许进入有限条件整改任务；不允许进入首页 / 今日页 PRD、Stage 2 或 MVP 开发。

## 验收与冻结区分

- 任务是否验收通过：是，LIFEOS-P1-002 Accepted。
- 对应资产是否冻结：否，V1 范围为 Pass with Conditions。
- 冻结范围：暂无冻结。
- 未冻结内容：V1 MoSCoW 最终口径、Obsidian 优先级合同、文件能力最小切片、AI Must 最小切片、四类命令在 V1 范围层的表达、用户验证合同、首页 / 今日页 PRD、Stitch 原型、技术架构、数据库/API、工程排期、Spike 实测结果、Stage 2/Stage 3 准入。
- 是否允许进入下一任务：Conditional。仅允许进入 V1 范围冻结条件整改。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：否。它是 V1 范围冻结前的正式独立评审。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是，V1 范围更新为 Pass with Conditions。

## 需要用户确认的事项

### 1. 是否采纳 P1-002 的 `Pass with Conditions` 结论？

- PM 建议：采纳。
- 可选方向：
  - A：采纳，启动有限条件整改。
  - B：不采纳，要求重新评审。
  - C：跳过整改，直接冻结。
- 不确认的影响：V1 范围不能冻结，也不建议启动首页 / 今日页 PRD。

### 2. 是否插入 `LIFEOS-P1-003｜V1 范围冻结条件整改`？

- PM 建议：插入，并将当前首页 / 今日页 PRD 顺延为 `LIFEOS-P1-004`。
- 可选方向：
  - A：插入 P1-003 条件整改，首页 PRD 顺延。
  - B：保留 P1-003 为首页 PRD，在首页 PRD 中顺带处理整改。
  - C：暂缓全部 Stage 1 后续任务。
- 不确认的影响：若直接做首页 PRD，范围层问题会被带入交互设计，后续返工概率高。

### 3. 是否确认 Obsidian 的 V1 口径？

- PM 建议：确认 Obsidian 为 Should Have + 条件性需求，不作为 V1 最小闭环成立的 Must 前提；SP-02/03 失败时降级为手工导入 / 来源指针或移出 V1。
- 可选方向：
  - A：采纳该口径。
  - B：提升为 Must。
  - C：移出 V1。
- 不确认的影响：后续 PRD 和 Spike 会持续混淆 Obsidian 到底是核心闭环还是优先来源增强。

### 4. 是否确认文件与 AI Must 的最小切片？

- PM 建议：确认“文件/来源指针为 Must 最低切片，完整文件处理为 Should/条件项”；确认“AI 摘要/分类/关联是 Project 恢复与候选下一步的支撑手段，不是每项都要做成独立完整功能面”。
- 可选方向：
  - A：采纳最小切片。
  - B：要求 Must 覆盖完整文件处理和完整 AI 整理功能。
  - C：进一步收窄 AI Must。
- 不确认的影响：MVP 范围会偏大，工程和设计都会被“能力包”拖重。

### 5. 是否确认 V1 范围冻结的边界？

- PM 建议：未来冻结仅覆盖一句话范围、用户/场景边界、整改后的 MoSCoW、条件性依赖/降级、首页输入边界和指标框架；不覆盖 PRD、交互、Stitch、技术实现、Spike 结果、架构或 Stage 3 准入。
- 可选方向：
  - A：采纳该冻结边界。
  - B：要求冻结更完整的 PRD 后再算 V1 范围冻结。
  - C：暂不冻结 V1 范围。
- 不确认的影响：后续仍容易出现“范围冻结 = 可以开发”的误解。

## 整改建议

建议启动一个补丁 / 条件整改型任务，只回应以下四项，不重写 P1-001：

1. M-01：给 Must 补最小范围合同。
2. M-02：显式继承四类命令：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback`。
3. M-03：固定 Obsidian 为 Should Have + 条件性需求，并写清 SP-02/03 失败降级。
4. M-04：补最小用户验证方案与判定动作。

建议任务编号：`LIFEOS-P1-003｜V1 范围冻结条件整改`。  
建议交付物路径：`lifeos/deliverables/LIFEOS-P1-003_v1_scope_freeze_condition_patch.md`。  
若用户采纳，当前 `LIFEOS-P1-003｜首页 / 今日页 PRD` 应顺延为 `LIFEOS-P1-004`。

## 可接受内容

可以沉淀为后续输入的内容：

1. P1-002 的 `Pass with Conditions` 评审结论。
2. 对 P1-001 主方向“不推倒重来”的判断。
3. Obsidian 为 Should Have + 条件性需求的建议。
4. 文件 / 来源指针与完整文件处理的边界建议。
5. AI Must 从“能力包”收敛为 Project 恢复与候选下一步支撑手段的建议。
6. 基础导出、最小审计、撤回 / 删除保留为 Must，但只冻结最低用户价值合同的建议。
7. 首页 / 今日页 PRD 后续必须补充的状态要求。

## 不接受或需谨慎内容

1. 不得把 P1-002 的条件通过解释为 V1 范围已冻结。
2. 不得跳过 M-01 至 M-04 直接进入首页 / 今日页 PRD。
3. 不得把 Obsidian 静默升级为 Must。
4. 不得把“文件/来源指针”扩成完整文件系统、附件管理或全格式解析。
5. 不得把 AI 摘要、分类、关联、今日重点、下一步全部做成独立完整 Must 功能面。
6. 不得把 Gate 4 验证合同通过解释为技术实现已通过。
7. 不得把 Gate 5 验证框架通过解释为用户价值已验证。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：用户采纳整改后，再写入 V1 范围冻结候选的最终口径；当前暂不更新。
- `lifeos/PM_OPERATING_MODEL.md`：无需更新。
- `lifeos/TASK_REGISTRY.md`：将 LIFEOS-P1-002 更新为 Accepted；用户采纳后插入 P1-003 条件整改并顺延首页 PRD。
- `lifeos/DECISION_LOG.md`：记录接受 P1-002 的 Pass with Conditions 结论；用户采纳后再记录启动 P1-003。
- `lifeos/RISK_LOG.md`：暂无新增风险类型，延续既有范围膨胀、Obsidian 反客为主、AI 权限和用户价值未验证风险。
- `lifeos/OPEN_QUESTIONS.md`：可在用户采纳后补充 Obsidian、文件能力、AI Must、用户验证合同的范围确认问题；当前由本 PM Review 承载。

## 下一步任务建议

PM 建议：

1. 用户确认采纳 P1-002 的 `Pass with Conditions` 结论。
2. 创建 `LIFEOS-P1-003｜V1 范围冻结条件整改`。
3. 将首页 / 今日页 PRD 顺延为 `LIFEOS-P1-004`。
4. P1-003 完成并经 PM 验收后，再判断是否冻结 V1 范围。
5. V1 范围冻结后，再启动首页 / 今日页 PRD；仍不修改 Stitch。
