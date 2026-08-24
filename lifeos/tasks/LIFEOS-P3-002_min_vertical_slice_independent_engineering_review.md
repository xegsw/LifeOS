# LIFEOS-P3-002 合成数据最小纵向闭环独立工程评审

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项独立评审会话，不是 PM 主会话，也不是 P3-001 的实现会话。请只完成本任务，不要自行扩大范围。本任务允许读取代码、复跑测试、检查 evidence 和形成独立评审结论；不允许写新功能、不允许修改 P3-001 代码、不允许启用真实能力、不允许冻结生产资产。

## 任务信息

- 任务 ID：LIFEOS-P3-002
- 任务名称：合成数据最小纵向闭环独立工程评审
- 优先级：P0
- 任务类型：独立评审型任务
- 建议篇幅：2000-4000 字；代码问题可列清楚，但不要扩展为完整重构方案
- 主责角色：独立工程评审负责人
- 协审角色：技术架构负责人、AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅确认没有被错误外推，不做结果层验证
- 状态：Ready

## 背景

`LIFEOS-P3-001` 已完成首个受控工程实现，并通过 PM 复跑：11 PASS / 0 FAIL / P0=0。用户已采纳 P3-001，并允许启动 P3-002。

但 P3-001 是首个可运行工程基线，仍可能存在“测试过拟合夹具”“实现只满足表面断言”“证据不够独立”“语义与冻结合同有偏差”等风险。因此在继续扩展真实能力、UI 或更大工程骨架前，需要一次独立工程评审。

本任务的目标不是写代码，而是判断 P3-001 是否可以作为后续 MVP 工程基线输入，或是否需要先返工、拆分、补测或降级。

## 目标

完成后需要回答：

- P3-001 的实现是否真实跑通 P2-019 / P2-020 要求的最小纵向闭环？
- 11 项 P0 测试是否覆盖关键风险？是否存在漏测、误测、过拟合或证据不可复跑？
- P3-001 是否遵守技术架构 V0.1、核心领域语义和 AI 信任边界？
- P3-001 是否存在真实数据、真实 Vault、真实 Tauri / IPC、云 / 第三方模型、向量、L3 或外部用户等越界入口？
- P3-001 应被判为 Pass、Pass with Conditions、Rework、Fail 还是 Paused？
- 下一步应进入工程基线整理、返工补测，还是继续暂停？

## 范围

本任务必须覆盖：

- 阅读 P3-001 任务卡、PM Review、工程报告、evidence manifest、机器测试结果和关键实现代码。
- 复跑 P3-001 的验证命令：
  - `python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py`
  - `cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py`
- 抽查关键实现：
  - 权威保存与“已保存”语义；
  - ArtifactVersion 不可变；
  - Source / Artifact / Derivation / Feedback / Authorization / AuditEntry / Link 身份区分；
  - Project 合法上下文恢复；
  - 候选下一步身份与未确认状态；
  - 五类 Feedback 不改写原文；
  - 四类控制命令与活跃阻断；
  - tombstone / generation / lease fencing；
  - 默认关闭能力；
  - 受控导出 / 恢复候选与不复活；
  - FTS-first 与权威回连；
  - 合成夹具隐私扫描。
- 对照 P2-019 的 H1-H9、`T-ARCH`、能力启用门和 P2-020 的 P3-001 任务卡要求。
- 明确 P0 / P1 / P2 问题；P0 问题不得判 Pass with Conditions。
- 给出是否允许 P3-001 作为后续工程基线输入的独立建议。

## 非范围

本任务暂时不要做：

- 不写新功能代码。
- 不修改 P3-001 代码、测试、夹具或 evidence；如发现问题，只在评审报告中记录。
- 不创建工程脚手架、产品 UI、Tauri 应用、API、生产 Schema 或正式导出格式。
- 不处理真实数据、低敏真实副本、真实 Vault、真实文件路径、真实敏感材料。
- 不启用真实 Tauri / IPC、文件导出扩权、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化。
- 不冻结 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 不修改 Stitch、PRD、冻结资产或项目账本。
- 不把评审通过外推为 Gate 5 结果层通过、正式 MVP 完成或可面向外部用户。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/reviews/LIFEOS-P3-001_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-020_min_vertical_slice_engineering_task_card.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/FREEZE_STATUS.md` 中 P3-001、技术架构、MVP 开发准入、R-0040 相关行

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取最近 5-10 条或任务卡指定相关决策。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 复跑测试时，聊天中只报告 PASS / FAIL 数量、P0 失败数、关键失败和证据路径；完整日志写入评审报告引用。

## 角色检查点

主责角色必须重点回答：

- 实现是否真实满足合同，而不是只把测试写成通过？
- 测试是否覆盖 P2-019 / P2-020 的 P0 底线？
- 证据是否可复跑、可追踪、可用于后续工程基线判断？
- 是否存在任何越界能力、隐藏依赖、真实数据风险或冻结误读？

协审角色必须重点检查：

- 技术架构：SQLite + FTS-first、权威 / 派生 / outbox 分责、generation / lease、FTS 回连权威是否成立。
- AI 信任与安全：用户原文、规则 / AI 候选、用户确认、授权、撤回 / 删除、默认关闭能力是否清楚。
- 数据 / 领域模型：Source、ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry、Link 是否语义清楚。
- 质量 / 测试：P0/P1 分类是否合理，测试是否存在夹具过拟合或漏测。
- 体验设计：语义级状态走查是否充分说明“未做 UI”，是否误导为动态 UI 已完成。
- PM：是否避免把 P3-001 外推为真实能力启用、正式 MVP 完成、Gate 5 或商业化通过。

## 核心问题

请重点回答：

- 复跑结果是什么？是否与 P3-001 报告一致？
- 哪些实现与测试可以作为后续工程基线输入？
- 哪些实现、测试或证据存在缺口？
- 是否存在 P0 阻断？如有，结论必须是 Rework / Fail / Paused。
- 是否存在可接受的 P1 条件项？条件是什么，是否能关闭或降级？
- 是否建议进入下一步？下一步应该是工程基线整理、返工补测、能力启用评审，还是暂停？

## 交付物

请将完整独立评审报告保存为：

`lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`

请输出的文件内容包括：

- 评审结论摘要
- 复跑命令与结果
- 代码 / 测试 / evidence 抽查范围
- P2-019 / P2-020 / P3-001 对照验收
- H1-H9 与 `T-ARCH` 独立判断
- 默认关闭能力与数据边界审查
- P0 / P1 / P2 问题清单
- 是否允许 P3-001 作为后续工程基线输入
- 不得外推的结论
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 已读取指定输入材料。
- 已复跑 P3-001 的验证命令，或明确说明无法复跑的原因。
- 已抽查关键代码、测试、夹具和 evidence。
- 已明确 P3-001 是否可作为后续工程基线输入。
- 已列出 P0 / P1 / P2 问题；若无，写“无”。
- 若存在任何 P0 问题，结论不得写 Pass 或 Pass with Conditions。
- 已明确说明本评审不写代码、不启用真实能力、不冻结生产资产。
- 完整评审报告已保存为指定文件。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、评审路径、复跑结果和是否需要 PM 决策。

## 限制条件

- 不修改代码、测试、夹具、evidence、Stitch、PRD 或项目账本。
- 不处理真实数据、真实 Vault、真实文件系统广泛路径或真实外部服务。
- 不调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不启用向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不冻结新的 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终工程目录结构。
- 如果发现需要改变 V1 范围、技术架构、核心领域语义或 AI 权限边界，必须标记为“需 PM 决策”，不得自行调整。
