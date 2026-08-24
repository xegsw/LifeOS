# LIFEOS-P3-006 P3-001 第二轮 P0 返工独立工程复评

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立工程复评会话，不是 PM 主会话，不是 P3-001 / P3-005 的实现会话。请只完成本任务，不要自行扩大范围。本任务允许读取代码、复跑验证、检查 evidence、设计并运行只读 / 临时反例验证脚本、形成独立复评结论；不允许写新功能、不允许修改 P3-001 源码 / 测试 / 夹具、不允许启用真实能力、不允许冻结生产资产。

## 任务信息

- 任务 ID：LIFEOS-P3-006
- 任务名称：P3-001 第二轮 P0 返工独立工程复评
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2000-4000 字；反例、证据与结论要清楚，但不要扩展为完整重构方案
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、PM
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅确认没有被错误外推，不做结果层验证
- 状态：Ready

## 背景

`LIFEOS-P3-004` 独立工程复评在 P3-003 之后发现了三项新增 P0：

1. 恢复门仍可能被旧控制包 / 重算校验控制包自证，导致已撤回对象被恢复。
2. 候选未持久化完整证据依赖，撤回非主证据后仍可能活跃、可导出、可被反馈 / Link 继续引用。
3. 真实消费入口依赖默认授权上下文，缺失、冲突或维度错配的 Authorization 仍可能被放行。

`LIFEOS-P3-005` 已完成窄范围返工并通过 PM 验收：19 PASS / 0 FAIL / P0=0 / P1=0，85 / 85 断言通过，PM 直接重放 P3-004 三条失败反例均已关闭。用户已采纳 P3-005，并要求启动 P3-006。

但 P3-005 是实现会话的返工结果。为了避免“修复者自证通过”、测试过拟合或真实消费入口仍有绕路，P3-001 在恢复为后续工程基线前，必须接受第二轮独立工程复评。P3-006 通过前，P3-001 继续保持 Rework，R-0041 继续保持 Open。

## 目标

完成后需要回答：

- P3-005 是否真实关闭了 P3-004 指出的三项新增 P0？
- 新增 3 项回归测试、23 条新增断言和总计 85 条断言是否真实覆盖关键不变量，而不是只适配固定夹具或固定调用方式？
- 现有实现是否还存在新的绕路消费路径、恢复包自证、证据撤回不传播、授权上下文缺失 / 冲突放行、跨 Project 泄漏、确认状态回退或派生物复活？
- P3-001 是否可以建议恢复为后续工程基线候选？
- R-0041 是否可以建议 PM 关闭，或应继续保持 Open？
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
- 判断报告中的 19 PASS / 0 FAIL、P0=0、P1=0、85 / 85 断言和快照标识是否可复核。

说明：如果验证命令会重写 evidence 文件，只允许由验证命令自然生成，不得手工编辑 evidence；复评报告需说明复跑前后是否发现不一致。

### 2. P3-004 三个新增 P0 反例独立重放

必须至少独立重放或构造等价反例：

- 旧恢复包、被篡改并重算校验的恢复包、旧 generation / 旧 tombstone 状态不得自证恢复已撤回、已断源、已删除或已失效对象。
- 任意一个候选证据输入被撤回 / 删除 / 断源 / generation 变化后，候选、导出、恢复包、Feedback、Link、搜索结果和下一步建议必须 fail closed 或标记 stale，不得继续作为可信建议消费。
- Authorization 缺失、重复 allow、allow / deny 冲突、未知 decision、过期、location / processor / purpose / Project / subject / version / generation / source_generation 任一错配都必须 fail closed；并且 `read_artifact()`、`search()`、`recovery_package()`、`export_test_package()`、`restore_candidates()`、`suggest_next_step()` 等真实消费入口不能依赖宽松默认上下文。

### 3. 回归历史 P0 与新绕路检查

必须检查 P3-002 与 P3-004 两轮历史 P0 是否被当前实现共同守住：

- Project A 导出不得带出 Project B 的 Artifact、ArtifactVersion、Source、Authorization、Derivation、Feedback、Link 或跨 Project Link。
- `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 后，旧包不得恢复被控制对象、非法派生、Feedback、搜索结果或队列候选。
- `confirmed` 与 `edited_confirmed` 候选在重复建议后不得回退为 `unconfirmed`，旧确认与 Feedback 必须可追踪。
- 恢复、导出、搜索、读取、建议、反馈、Link 等入口必须重检授权、来源、版本、tombstone、generation、证据集合和消费上下文。
- 新增测试是否存在“只检查固定字符串 / 固定摘要 / 单一夹具 / 单一调用方式”的过拟合。

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
- 不冻结新的 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 不自行关闭 R-0041；只能给出是否建议 PM 关闭的独立结论。
- 不自行把 P3-001 标记为工程基线；只能给出是否建议 PM 恢复基线候选的结论。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/tasks/LIFEOS-P3-005_second_p0_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-005_pm_review.md`
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
- `lifeos/FREEZE_STATUS.md` 中 P3-001、P3-005、MVP 开发准入、技术架构相关行
- 决策 `D-0138`、`D-0139`、`D-0140`、`D-0141` 与风险 `R-0041`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的直接依赖。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0138 至 D-0141 或最近 5-10 条相关决策。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 测试输出只在聊天中报告摘要：PASS / FAIL 数量、P0 失败数、关键失败、证据路径；详细日志写入或引用评审报告。

## 角色检查点

主责角色必须重点回答：

- P3-005 是否真实修复三项新增 P0 根因，而非只让当前测试通过？
- 新增测试和 evidence 是否足以支撑 P3-001 恢复工程基线候选？
- 是否还存在 P0 / P1 / P2 缺口？
- 是否建议关闭 R-0041，或继续保持 Open？

协审角色必须重点检查：

- 技术架构：权威 / 派生 / outbox 分责、FTS-first、generation、tombstone、包恢复 gate 和消费前重检是否成立。
- AI 信任与安全：确认状态、编辑确认、Feedback、证据撤回、授权撤回、location / processor、默认关闭能力是否可信。
- 数据 / 领域模型：Project、Source、ArtifactVersion、Derivation、DerivationInput、Feedback、Authorization、AuditEntry、Link 身份是否隔离。
- 质量 / 测试：回归测试是否覆盖原始反例、新增反例、负测、包篡改、证据集合、授权冲突和非 happy path。
- PM：是否避免把合成工程结论外推为真实能力、Gate 5、Beta、商业化或生产冻结。

## 核心问题

请重点回答：

- 复跑结果是什么？是否与 P3-005 报告和 PM Review 一致？
- P3-004 三个新增 P0 反例是否已经被独立重放并通过？
- P3-002 历史四个 P0 是否仍未回归？
- 是否发现新的 P0 / P1 / P2 问题？
- 是否允许建议 P3-001 恢复为后续工程基线候选？
- 是否建议 PM 关闭 R-0041？
- 若不建议恢复基线，必须列出阻断原因和最小返工建议。

## 交付物

请将完整独立复评报告保存为：

`lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`

报告必须包括：

- 复评结论摘要，并明确区分事实、推断、建议
- 复跑命令与结果
- evidence 抽查范围与一致性判断
- P3-004 三个新增 P0 反例独立重放结果
- P3-002 历史四个 P0 回归检查结果
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
- 已独立重放 P3-004 三个新增 P0 反例或构造等价反例。
- 已回归检查 P3-002 四个历史 P0 是否未复发。
- 已明确列出 P0 / P1 / P2 问题；若无，写“无”。
- 若存在任何 P0 问题，结论不得写 Pass 或 Pass with Conditions，必须建议 Rework / Fail / Paused。
- 已明确是否建议 P3-001 恢复为后续工程基线候选。
- 已明确是否建议 PM 关闭 R-0041。
- 已明确说明本复评不写代码、不启用真实能力、不冻结生产资产。
- 完整复评报告已保存为指定文件。
- 已完成本地预检：`python3 lifeos/tools/local_precheck.py lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`，或明确说明允许跳过的原因。
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
