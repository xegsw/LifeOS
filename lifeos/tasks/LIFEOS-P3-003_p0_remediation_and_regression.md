# LIFEOS-P3-003 P3-001 四项 P0 返工与补测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程返工会话，不是 PM 主会话，也不是独立评审会话。请只完成本任务，不要自行扩大范围。本任务明确授权你在 `lifeos/engineering/LIFEOS-P3-001/` 内修改关闭四项 P0 所需的最小代码、测试、合成夹具和 evidence，并创建返工报告；不得扩展 UI、真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、L3 或外部用户能力。

## 任务信息

- 任务 ID：LIFEOS-P3-003
- 任务名称：P3-001 四项 P0 返工与补测
- 优先级：P0
- 任务类型：条件整改 / 补丁型工程任务
- 建议交付报告篇幅：1500-3000 字；完整日志、测试输出和断言证据写入 evidence
- 主责角色：工程负责人 / 技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、PM
- 必须通过的评审关卡：Gate 2、Gate 3、Gate 4；Gate 1 仅检查未扩范围，Gate 5 不做结果层验证
- 状态：Ready

## 背景

用户已采纳 `LIFEOS-P3-002` 的 `Rework` 结论并允许启动本任务。P3-002 复跑 P3-001 原验证器仍为 11 PASS / 0 FAIL / P0=0，但独立对抗检查发现四项原测试未覆盖的 P0：

1. 导出 Project A 时混入 Project B 的 Feedback / Link。
2. `revoke_processing` 后，旧测试包仍可恢复 Artifact。
3. 已确认候选再次执行 `suggest_next_step()` 后被静默重置为 `unconfirmed`。
4. Authorization 的 `location` / `processor` 错配时仍可消费。

这些问题击穿 P2-019 的 H2、H4、H5、H9 与 `T-ARCH`。P3-001 当前为 `Rework`，在四项 P0 关闭并完成后续独立复评前，不得作为后续 MVP 工程基线。

## 目标

在不扩大能力与产品范围的前提下，最小修改 P3-001 实现与验证体系，关闭上述四项 P0，并补齐会直接证明修复有效的回归测试、强杀 / 提交边界测试和真实断言驱动 evidence。

## 范围

本任务必须覆盖：

### 1. 跨 Project 导出隔离

- `export_test_package(project_id)` 中 Artifact、ArtifactVersion、Feedback、Link、Derivation、Source、Authorization 等所有被导出对象必须按目标 Project、当前授权和依赖可达性形成合法闭包。
- 使用至少两个 Project 的确定性合成夹具，断言导出 Project A 时 Project B 的 Artifact、Feedback、Link 及仅属于 B 的关联对象均为零命中。
- 对缺失、跨 Project 或已失效依赖必须诚实排除或记录部分失败，不得通过全表扫描拼入包内。

### 2. 四类控制命令后的旧包不复活

- 恢复门必须在恢复 / 重导入前重新检查当前 `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 控制状态，以及适用的授权、来源、精确版本、tombstone、generation 和证据状态。
- 为四类控制命令分别构造“先生成旧包 → 接受控制命令 → 尝试恢复”的确定性测试。
- 断言被控制对象及其非法派生、搜索、建议、队列、导出 / 恢复候选不会复活；物理清理未完成时仍需诚实披露状态。

### 3. 已确认候选状态保护

- 再次生成相同候选不得通过 `INSERT OR REPLACE` 或等价路径把 `confirmed`、`edited_confirmed` 等用户已确认状态静默回退为 `unconfirmed`。
- 必须保留用户 Feedback、确认身份、来源、精确输入版本和审计轨迹。
- 补充“确认 → 再次建议”和“编辑后确认 → 再次建议”的回归测试；若证据变化确需产生新候选，必须使用可区分的新派生身份并保持旧确认记录可追踪，不得覆盖。

### 4. Authorization 完整 fail-closed

- 所有消费入口至少完整校验当前任务既有授权语义中的 Project / subject、purpose、location、processor、授权版本 / 状态和时效；未知、缺失、过期、撤回或不匹配均拒绝。
- 补齐 `location='cloud'`、`processor='third_party'` 与本地允许上下文错配的负测，并覆盖 location 与 processor 分别错配、同时错配及合法精确匹配。
- 不得因为当前没有真实云适配器而跳过该检查，也不得通过修改关闭能力开关来“证明”通过。

### 5. 必要 P1 补测与 evidence

- 为 `T-SAVE` 增加进程强杀 / 提交边界测试，至少证明：提交前强杀不误报保存且不留半提交权威记录；提交完成后重启可读；FTS / 派生故障不逆转权威提交。
- 修复或补充 `T-GATE`、`T-DEL`、`T-EXPORT`，确保不是单 Project / 单 happy path 过拟合。
- evidence 必须由实际测试断言和运行结果生成，不得使用超出真实覆盖范围的固定摘要。
- evidence manifest 必须记录本次工作区内容哈希或等价可唯一定位快照的标识、夹具版本、环境、命令、断言、结果、限制和复跑时间。
- 保留并复跑 P3-001 原有完整验证集，防止修复破坏权威保存、不可变版本、FTS-first、默认关闭能力和合成数据边界。

## 非范围

本任务暂时不要做：

- 不扩展产品 UI、动态交互、首页 / 今日页、Stitch 或 PRD。
- 不处理任何真实数据、低敏真实副本、真实敏感材料、真实 Vault 或用户真实路径。
- 不启用真实 Tauri / IPC / 文件导出扩权、Obsidian、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化。
- 不重写 P3-001 为生产应用，不做无关重构、技术栈迁移或工程目录大调整。
- 不冻结 Schema、API、UI、Tauri capability、正式导出格式、生产 SLA 或最终目录结构。
- 不调整核心领域实体、技术架构合同、V1 范围或 AI 权限边界；如修复必须改变这些冻结边界，立即暂停并标记“需 PM 确认”。
- 不自行把 P3-001 恢复为工程基线，不自行关闭 R-0041，不自行宣称独立复评通过。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-002_min_vertical_slice_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-002_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/FREEZE_STATUS.md` 中 P3-001、P3-002、技术架构和 MVP 开发准入相关行
- 决策 `D-0134`、`D-0135` 与风险 `R-0041`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的直接依赖。
- 重点读取 P3-002 第 4、5、7、9、10 节；四项 P0 是强制关闭项，P1 是必要证据补强项。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`；如发现需要改变产品定位、V1 范围、技术架构、数据模型或 AI 权限边界，停止实现并请求 PM 确认。
- 不主动读取全量项目历史或无关 Review / Deliverable / Evidence。
- 测试日志写入 evidence；聊天只报告 PASS / FAIL、P0 失败数、P1 遗留与关键路径。

## 工程与证据路径

在既有 P3-001 工程目录内完成最小补丁：

- 实现与测试：`lifeos/engineering/LIFEOS-P3-001/`
- evidence：`lifeos/engineering/LIFEOS-P3-001/evidence/`
- 返工报告：`lifeos/deliverables/LIFEOS-P3-003_p0_remediation_and_regression_report.md`

如新增专项 evidence 文件，应从 `evidence/MANIFEST.md` 建立可追踪入口；不要另建会被误认为生产目录的新工程骨架。

## 角色检查点

主责角色必须重点回答：

- 四项 P0 是否在实现层根因修复，而非只修改测试或屏蔽反例？
- 修复是否保持 SQLite + FTS-first、权威 / 派生 / outbox 分责和消费前重检合同？
- 全部测试与 evidence 是否可复跑、断言驱动并唯一定位本次代码快照？

协审角色必须重点检查：

- AI 信任与安全：确认状态不可静默回退；授权 location / processor 等维度未知即拒绝；撤回后不再消费。
- 数据 / 领域模型：跨 Project 闭包、Source / Artifact / Derivation / Feedback / Link 身份和精确版本不混淆。
- 质量 / 测试：四个原独立反例全部成为自动回归测试；强杀 / 提交边界和多 Project / 多控制命令覆盖真实执行路径。
- PM：任务未扩展到真实能力、UI、冻结、Gate 5、Beta 或商业化结论。

## 核心问题

请重点回答：

- 四项 P0 的根因、最小修复和对应自动回归测试分别是什么？
- “旧包 + 四命令”是否全部不复活？跨 Project 导出是否零泄漏？
- 已确认与编辑后确认候选在重复建议后是否保持用户确认语义？
- Authorization 的 location / processor 及其他既有维度是否完整 fail-closed？
- 强杀 / 提交边界测试结果是什么？evidence 是否由实际断言生成并能定位代码快照？
- 原 11 项验证集和新增回归集的 PASS / FAIL、P0 失败数、P1 遗留是什么？
- 是否存在范围、架构、核心语义或 AI 权限边界偏离？

## 交付物

请将完整返工报告保存为：

`lifeos/deliverables/LIFEOS-P3-003_p0_remediation_and_regression_report.md`

报告必须包括：

- 结论摘要，并明确区分事实、推断、建议
- 四项 P0 的根因、代码改动、测试 ID、断言与结果对照
- 必要 P1 补测与 evidence 改进
- 创建 / 修改文件清单
- 复跑命令和测试摘要：PASS / FAIL、P0 失败数、P1 遗留
- H2、H3、H4、H5、H9 与 `T-ARCH` 对照
- evidence manifest 路径与快照标识
- 原验证集回归结果
- 能力启用请求；如无，写“无”
- 范围 / 架构 / 核心语义 / AI 权限边界偏离；如无，写“无”
- 未关闭风险、需 PM 确认事项与后续独立复评建议

## 验收标准

只有满足以下条件，任务才算完成：

- 四项 P0 均有实现层修复和自动回归测试，且 P0 失败数为 0。
- 双 Project 导出测试证明跨 Project Artifact、Feedback、Link 及关联对象零泄漏。
- 旧包分别经过四类控制命令后均不能使被控制对象或非法派生复活。
- 已确认和编辑后确认候选在重复建议后不会静默回到未确认；旧确认和 Feedback 可追踪。
- location / processor 分别错配、同时错配、未知 / 缺失与合法精确匹配均有 fail-closed 测试。
- 强杀 / 提交边界测试通过；权威提交、重启读取及 FTS / 派生故障隔离不回退。
- 原 P3-001 验证集完整通过，且新增回归测试实际纳入统一验证命令。
- evidence 由真实断言 / 结果生成，manifest 能唯一定位本次内容快照且不夸大覆盖。
- 已生成指定返工报告，并完成本地预检或说明允许跳过的原因。
- 未处理真实数据、未启用真实能力、未扩 UI、未修改 Stitch、未冻结新的生产资产。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、报告路径、evidence 路径、测试结果和是否需要 PM 决策。

若任何 P0 失败、四项 P0 缺少真实执行路径证据，或修复必须改变冻结边界，任务必须报告 `Partial` / `Blocked`，不得写 Pass、Accepted 或已恢复工程基线。

## 限制条件

- 只允许使用合成数据和本地受控目录。
- 只允许修改关闭四项 P0、必要 P1 补测和 evidence 所需的最小文件。
- 不允许删除或弱化既有测试来获得通过结果。
- 不允许调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不允许启用真实 Vault、Tauri 文件能力、导出路径扩权、向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不允许冻结 Schema、API、UI、Tauri capability、正式导出格式、生产 SLA 或最终目录结构。
- P3-003 完成后仍须 PM 验收，并建议另行启动独立工程复评；本任务自身不能把 P3-001 标记回工程基线。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中不要粘贴完整报告或大段日志。
