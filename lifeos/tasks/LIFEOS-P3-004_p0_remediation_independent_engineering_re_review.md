# LIFEOS-P3-004 P3-001 四项 P0 返工独立工程复评

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立工程复评会话，不是 PM 主会话，不是 P3-001 / P3-003 的实现会话。请只完成本任务，不要自行扩大范围。本任务允许读取代码、复跑验证、检查 evidence、设计并运行只读 / 临时反例验证脚本、形成独立复评结论；不允许写新功能、不允许修改 P3-001 源码 / 测试 / 夹具、不允许启用真实能力、不允许冻结生产资产。

## 任务信息

- 任务 ID：LIFEOS-P3-004
- 任务名称：P3-001 四项 P0 返工独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2000-4000 字；反例与证据可列清楚，但不要扩展为完整重构方案
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、PM
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅确认没有被错误外推，不做结果层验证
- 状态：Ready

## 背景

`LIFEOS-P3-002` 独立工程评审曾发现 P3-001 存在四项 P0：

1. 跨 Project 导出泄漏。
2. 撤回处理后旧测试包恢复导致对象复活。
3. 已确认候选被重复建议静默重置为未确认。
4. Authorization 的 `location` / `processor` 错配仍可消费。

`LIFEOS-P3-003` 已完成窄范围返工并通过 PM 验收：16 PASS / 0 FAIL / P0=0 / P1=0，PM 直接重放四个原始 P0 反例均 PASS。用户已采纳 P3-003，并要求启动 P3-004。

但 P3-003 是实现会话的返工结果。为了避免“修复者自证通过”或 evidence 过拟合，P3-001 在恢复为后续工程基线前，必须接受一次独立工程复评。P3-004 通过前，P3-001 继续保持 Rework，R-0041 继续保持 Open。

## 目标

完成后需要回答：

- P3-003 是否真实关闭了 P3-002 指出的四项 P0？
- 新增 5 项回归测试与 62 条断言是否真实覆盖关键不变量，而不是只适配固定夹具或摘要？
- 现有实现是否还存在新的绕路消费路径、Project 泄漏、撤回后复活、确认语义回退或授权维度漏检？
- P3-001 是否可以恢复为后续工程基线候选，还是仍需 Rework？
- R-0041 是否可以建议关闭，或应继续保持 Open？
- 下一步应该是恢复工程基线、继续补丁返工、拆分新风险任务，还是暂停工程线？

## 范围

本任务必须覆盖：

### 1. 复跑与证据一致性

- 复跑 P3-001 当前验证命令：
  - `python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py`
  - `cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py`
- 抽查并引用：
  - `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
  - `lifeos/engineering/LIFEOS-P3-001/evidence/test_results.json`
  - `lifeos/engineering/LIFEOS-P3-001/evidence/regression_assertions.json`
  - `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
  - `lifeos/engineering/LIFEOS-P3-001/evidence/test_run.log`
- 判断报告中的 16 PASS / 0 FAIL、P0=0、P1=0、62 / 62 断言和快照标识是否可复核。

说明：如果验证命令会重写 evidence 文件，只允许由验证命令自然生成，不得手工编辑 evidence；复评报告需说明复跑前后是否发现不一致。

### 2. 四个原始 P0 反例独立重放

必须至少独立重放或构造等价反例：

- 导出 Project A 时，Project B 的 Artifact、ArtifactVersion、Source、Authorization、Derivation、Feedback、Link、跨 Project Link 均不得进入 A 的合法闭包。
- 旧测试包在 `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 后不得恢复被控制对象、非法派生、Feedback、搜索结果或队列候选。
- `confirmed` 与 `edited_confirmed` 候选在重复建议后不得回退为 `unconfirmed`，旧确认与 Feedback 必须可追踪。
- Authorization 的 `location`、`processor`、purpose、Project / subject、精确版本、generation、时效、decision 任一不匹配或缺失均应 fail closed。

### 3. 新绕路与过拟合检查

必须重点检查：

- `export_test_package()` 是否仍存在全表扫描、跨 Project Link 拼入、Source / Authorization 闭包过宽或 tombstone / control state 漏检。
- `restore_candidates()` 是否只在 happy path 检查控制状态，是否能被包篡改、旧 generation、旧授权、断源、删除或反馈撤回绕过。
- `suggest_next_step()` 是否通过派生身份、证据集合或写入语句导致用户确认状态、编辑确认状态或 Feedback 被覆盖。
- `can_consume()` 与所有消费入口是否完整传入并校验授权上下文，而不是只在单个测试入口校验。
- 新增测试是否存在“只检查固定字符串 / 固定摘要 / 单一夹具”的过拟合。

### 4. 合同与边界复评

- 对照 `LIFEOS-P2-019` 的 H1-H9、`T-ARCH`、能力启用门，重点复核 H2、H3、H4、H5、H9。
- 对照技术架构 V0.1：SQLite + FTS-first、本地权威原文、可重建派生、权威 / 派生 / outbox 分责、消费入口重检授权 / 来源 / 版本 / tombstone / generation / 证据 / 租约。
- 对照 AI 信任边界：用户原文不可静默改写，用户确认不可被 AI 或重复建议覆盖，AI 候选 / 推断必须保留证据和状态。
- 确认没有启用真实数据、真实 Vault、真实 Tauri / IPC、导出路径扩权、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化能力。

## 非范围

本任务暂时不要做：

- 不修改 P3-001 源码、测试、夹具、README 或项目账本。
- 不修复任何发现的问题；如发现问题，只写入复评报告。
- 不创建新产品功能、UI、Tauri 应用、API、生产 Schema、正式导出格式或同步方案。
- 不处理真实数据、低敏真实副本、真实敏感材料、真实 Vault、真实文件路径或真实外部服务。
- 不调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不启用向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不冻结 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 不自行关闭 R-0041；只能给出是否建议 PM 关闭的独立结论。
- 不自行把 P3-001 标记为工程基线；只能给出是否建议 PM 恢复基线候选的结论。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/tasks/LIFEOS-P3-003_p0_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/deliverables/LIFEOS-P3-003_p0_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-003_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/regression_assertions.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_run.log`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/FREEZE_STATUS.md` 中 P3-001、P3-003、MVP 开发准入、技术架构相关行
- 决策 `D-0134`、`D-0135`、`D-0136`、`D-0137` 与风险 `R-0041`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的直接依赖。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0134 至 D-0137 或最近 5-10 条相关决策。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 测试输出只在聊天中报告摘要：PASS / FAIL 数量、P0 失败数、关键失败、证据路径；详细日志写入或引用评审报告。

## 角色检查点

主责角色必须重点回答：

- P3-003 是否真实修复四项 P0 根因，而非只让当前测试通过？
- 新增测试和 evidence 是否足以支撑 P3-001 恢复工程基线候选？
- 是否还存在 P0 / P1 / P2 缺口？
- 是否建议关闭 R-0041，或继续保持 Open？

协审角色必须重点检查：

- 技术架构：权威 / 派生 / outbox 分责、FTS-first、generation、tombstone、包恢复 gate 和消费前重检是否成立。
- AI 信任与安全：确认状态、编辑确认、Feedback、授权撤回、location / processor、默认关闭能力是否可信。
- 数据 / 领域模型：Project、Source、ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry、Link 身份是否隔离。
- 质量 / 测试：回归测试是否覆盖原始反例、负测、包篡改、四类控制命令、提交边界和非 happy path。
- PM：是否避免把合成工程结论外推为真实能力、Gate 5、Beta、商业化或生产冻结。

## 核心问题

请重点回答：

- 复跑结果是什么？是否与 P3-003 报告和 PM Review 一致？
- 四个原始 P0 反例是否已经被独立重放并通过？
- 是否发现新的 P0 / P1 / P2 问题？
- 是否允许建议 P3-001 恢复为后续工程基线候选？
- 是否建议 PM 关闭 R-0041？
- 若不建议恢复基线，必须列出阻断原因和最小返工建议。

## 交付物

请将完整独立复评报告保存为：

`lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`

报告必须包括：

- 复评结论摘要，并明确区分事实、推断、建议
- 复跑命令与结果
- evidence 抽查范围与一致性判断
- 四个原始 P0 反例独立重放结果
- 新绕路 / 过拟合检查结果
- H1-H9、`T-ARCH` 与能力启用门对照
- P0 / P1 / P2 问题清单；若无，写“无”
- 是否建议 P3-001 恢复为后续工程基线候选
- 是否建议 PM 关闭 R-0041
- 不得外推的结论
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 已读取指定输入材料。
- 已复跑指定验证命令，或明确说明无法复跑的原因。
- 已抽查关键代码、测试、夹具和 evidence。
- 已独立重放四个原始 P0 反例或构造等价反例。
- 已明确列出 P0 / P1 / P2 问题；若无，写“无”。
- 若存在任何 P0 问题，结论不得写 Pass 或 Pass with Conditions，必须建议 Rework / Fail / Paused。
- 已明确是否建议 P3-001 恢复为后续工程基线候选。
- 已明确是否建议 PM 关闭 R-0041。
- 已明确说明本复评不写代码、不启用真实能力、不冻结生产资产。
- 完整复评报告已保存为指定文件。
- 已完成本地预检：`python3 lifeos/tools/local_precheck.py lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`，或明确说明允许跳过的原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、评审路径、复跑结果、预检路径和是否需要 PM 决策。

## 限制条件

- 不修改代码、测试、夹具、README、Stitch、PRD 或项目账本。
- 不处理真实数据、真实 Vault、真实文件系统广泛路径或真实外部服务。
- 不调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不启用真实 Tauri / IPC、文件导出扩权、向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不冻结新的 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 如果发现需要改变 V1 范围、技术架构、核心领域语义或 AI 权限边界，必须标记为“需 PM 决策”，不得自行调整。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中不要粘贴完整报告、任务卡全文或大段日志。
