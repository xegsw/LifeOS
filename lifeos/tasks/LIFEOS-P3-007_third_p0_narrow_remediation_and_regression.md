# LIFEOS-P3-007 P3-001 第三轮 P0 窄范围返工与补测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程返工会话，不是 PM 主会话，不是独立评审会话。请只完成本任务，不要自行扩大范围。本任务允许在 `lifeos/engineering/LIFEOS-P3-001/` 既有合成工程目录内进行窄范围代码修复、测试补充、合成夹具调整、验证复跑和 evidence 更新；不允许修改项目账本、冻结资产、恢复工程基线、关闭风险或启动后续任务。

## 任务信息

- 任务 ID：LIFEOS-P3-007
- 任务名称：P3-001 第三轮 P0 窄范围返工与补测
- 优先级：P0
- 任务类型：补丁 / 条件整改型任务
- 建议篇幅：1500-3000 字；必须清楚列出修复点、回归结果和证据路径，不扩展为架构重写方案
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要修改既有合成工程代码、补充自动回归、复跑验证并整理 evidence，适合工程执行 Agent；后续仍需 WorkBuddy 或其他独立评审 Agent 复评
- 是否需要后续独立评审：Yes
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-001/`
- 是否允许修改项目账本：No
- 主责角色：工程返工负责人 / 技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、PM
- 必须通过的评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅确认没有被错误外推，不做结果层验证
- 状态：Ready

## 背景

`LIFEOS-P3-006` 独立工程复评任务已通过 PM 验收，但复评结论为 `Rework`。P3-006 在既有验证 19 PASS / 0 FAIL / P0=0 / P1=0 的基础上，发现当前 P3-001 仍存在 4 项 P0：

1. 恢复包重算 checksum 后篡改实际载荷，仍可能被 `restore_candidates()` 返回为 `restored`。
2. `add_feedback()` 与 `add_important_link()` 写入口绕过当前授权、证据、Project、版本、tombstone 与 generation 门。
3. 混合 Project Derivation / Feedback 状态通过导出包中的 state 字段泄漏。
4. Derivation 证据未绑定 Artifact / Source generation，代际变化后旧候选仍保持活跃。

PM 已抽样复核确认其中三类问题真实存在：伪造原文被 restored、Authorization deny 后仍可 `add_feedback()`、公共 `add_important_link()` 可写跨 Project Link。

用户已采纳 P3-006 Rework，并要求启动 P3-007。P3-007 通过 PM 验收和后续独立复评前，P3-001 继续保持 Rework，R-0041 继续保持 Open。

## 目标

完成后需要回答：

- 是否已关闭 P3-006 指出的 4 项 P0？
- 是否已把 P3-006 的关键失败反例纳入自动回归，而不是只做手工验证？
- 现有 `run_validation.py` 是否仍能稳定通过，且新增测试不是仅适配单一 happy path？
- evidence 是否能证明修复覆盖恢复包载荷、写入口授权、Project 闭包、generation 证据绑定四类根因？
- 是否仍存在 P0 / P1 / P2 风险？
- 是否建议进入下一轮独立工程复评？

## 范围

本任务必须覆盖：

### 1. 修复 P0-1：恢复包载荷不得自证

必须实现：

- `restore_candidates()` 不得信任包内 Artifact / Derivation / Feedback / Link 的可变载荷作为恢复结果。
- 恢复候选应以当前权威 SQLite 状态为准返回权威投影，或逐字段验证包内身份与内容完全匹配当前权威行后再返回。
- 即使攻击者修改包内 `original_text`、Artifact title/category/source、Derivation output/rule/status/generation、Feedback kind/user_text/status、Link relation/source_kind/confirmation_status 并重算公开 checksum，也不得把伪造载荷返回为 `restored`。
- checksum 只能证明包未被未重签损坏，不得被实现或文档表达为真实性、防伪或信任证明。

必须补测：

- 篡改 Artifact 原文并重算 checksum。
- 篡改 Derivation 输出文本 / rule / generation 并重算 checksum。
- 篡改 Feedback user_text / kind 并重算 checksum。
- 注入或篡改 Link 并重算 checksum。

### 2. 修复 P0-2：Feedback / Link 写入口必须重检当前门

必须实现：

- `add_feedback()` 必须验证候选当前可消费，且其全部证据输入仍满足 Project、Authorization、版本、Artifact generation、Source generation、tombstone、source connected、purpose、location、processor、now 等上下文要求。
- `add_important_link()` 必须验证 from/to Artifact 均属于允许 Project 闭包，均满足当前授权与版本 / generation 门，不允许公共方法写入跨 Project Link 或对已删除 / 已撤权 / 断源对象建立可信 Link。
- 写入口不得依赖宽松默认授权；需要显式上下文或内部构造可审计上下文，并 fail closed。
- 写入失败时必须不产生 Feedback / Link 记录，不改变 Derivation 状态。

必须补测：

- Authorization deny / revoked 后，`add_feedback()` 不得确认候选。
- 缺失、冲突、过期、location / processor / purpose 错配时，Feedback 写入 fail closed。
- 跨 Project Link 写入 fail closed。
- 任一端 Artifact 删除 / 撤权 / 断源 / generation 错配时，Link 写入 fail closed。
- 合法上下文下的 Feedback / Link happy path 仍可工作。

### 3. 修复 P0-3：导出包所有 state 字段也必须遵守 Project 最小闭包

必须实现：

- `export_test_package()` 中 `derivation_states`、`feedback_states`、`control_states`、`excluded`、`partial_failures` 等非活跃列表也不得泄漏当前 Project 闭包外的 Artifact、ArtifactVersion、Source、Authorization、Derivation、Feedback、Link 或用户文本。
- 混合 Project Derivation 若证据集合不完全属于当前 Project 允许闭包，不得出现在当前 Project 包的 `derivations`、`derivation_states`、`feedback`、`feedback_states` 或任何可恢复 / 可识别载荷中。
- 任何“状态说明”也必须执行最小披露原则；不能用字段名带 state 来绕过导出闭包。

必须补测：

- 构造 A + B 混合证据 Derivation，导出 A 时不得出现 B 的 version_id、Derivation ID、Feedback ID、Feedback user_text 或 Link。
- 导出 B 时同理不得泄漏 A。
- 合法单 Project Derivation / Feedback 状态仍可按预期出现。

### 4. 修复 P0-4：Derivation 证据身份必须绑定 Artifact / Source generation

必须实现：

- Derivation 依赖身份不仅绑定 ArtifactVersion ID，还必须绑定 Artifact generation 与 Source generation，或在消费 / 建议 / 导出 / 恢复 / Feedback / Link 写入时重检这些 generation。
- 当 Artifact generation 或 Source generation 发生变化，即使 version_id 不变，旧候选也必须 stale / invalid / fail closed，或生成新的、能体现新代际身份的候选 ID。
- `suggest_next_step()`、`export_test_package()`、`restore_candidates()`、`add_feedback()`、`add_important_link()` 不能继续消费 generation 已变化的旧候选。

必须补测：

- Artifact generation 递增且 Authorization generation 同步更新后，旧候选不得继续以同一身份保持 `unconfirmed`。
- Source generation 递增后，旧候选不得继续活跃。
- 代际变化后导出、恢复、Feedback、Link、搜索和建议均 fail closed 或给出新身份。
- 合法未变化 generation 的候选仍可建议和确认。

### 5. 回归历史 P0 与基础合同

必须保证历史问题不回归：

- P3-002 四项历史 P0：跨 Project 导出泄漏、控制命令后旧包复活、确认状态回退、Authorization location / processor 错配消费。
- P3-004 三项新增 P0：旧控制包自证恢复、非主证据撤回不传播、读取型入口缺失 / 冲突授权放行。
- P3-005 三项修复不能被本次改动破坏。
- `run_validation.py` 必须展示新增回归测试，并保持 P0=0；若存在 P1，应清楚列出是否阻断 PM 验收。

## 非范围

本任务暂时不要做：

- 不修改 `lifeos/CURRENT_STATUS.md`、`lifeos/TASK_REGISTRY.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/DECISION_LOG.md`、`lifeos/RISK_LOG.md`、`lifeos/OPEN_QUESTIONS.md`。
- 不修改 `lifeos/PROJECT_CONTEXT.md`、PRD、Stitch、首页 / 今日页原型或产品定义文件。
- 不创建新 UI、Tauri 应用、真实 API、生产 Schema、正式导出格式、同步方案或云 / 模型网关。
- 不处理真实数据、低敏真实副本、真实敏感材料、真实 Vault、真实文件路径或真实外部服务。
- 不调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不启用真实 Tauri / IPC、文件导出扩权、向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不自行恢复 P3-001 工程基线。
- 不自行关闭 R-0041。
- 不自行启动 P3-008 或其他后续任务；如认为需要，只写入“后续任务建议”。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/tasks/LIFEOS-P3-005_second_p0_remediation_and_regression.md`
- `lifeos/tasks/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-005_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-006_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/regression_assertions.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- 决策 `D-0143`、`D-0144` 与风险 `R-0041`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的直接依赖。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0143、D-0144 或最近 5-10 条相关决策。
- 不读取无关 Review、无关 Deliverable、无关 Evidence。
- 测试输出只在聊天中报告摘要：PASS / FAIL 数量、P0 失败数、关键失败、证据路径；详细日志写入或引用交付物。

## 角色检查点

主责角色必须重点回答：

- 四项 P0 是否均有根因级修复，而不是只让当前反例通过？
- 新增测试是否覆盖恢复载荷篡改、写入口授权、Project state 闭包、generation 绑定四类不变量？
- 代码改动是否仍保持 P3-001 的“合成数据、最小闭环、非生产冻结”边界？
- 是否建议进入下一轮独立工程复评？

协审角色必须重点检查：

- 技术架构：权威 / 派生 / outbox 分责、恢复 gate、导出闭包、消费前重检是否成立。
- AI 信任与安全：用户原文、AI 候选、用户确认、Feedback、Link、撤回、证据和授权是否可信。
- 数据 / 领域模型：Artifact、Source、ArtifactVersion、DerivationInput、Feedback、Authorization、Link 的身份、来源和 generation 是否一致。
- 质量 / 测试：新增测试是否包含负测、变形反例、历史回归和合法 happy path。
- PM：是否避免把合成工程结论外推为真实能力、Gate 5、Beta、商业化或生产冻结。

## 核心问题

请重点回答：

- 具体修改了哪些工程文件？
- 四项 P0 分别如何修复？
- 新增了哪些自动回归测试和断言？
- 复跑结果是什么？
- Evidence manifest 和关键证据文件是否已更新？
- 是否仍存在 P0 / P1 / P2？
- 是否建议进入下一轮独立工程复评？

## 交付物

请将完整返工报告保存为：

`lifeos/deliverables/LIFEOS-P3-007_third_p0_narrow_remediation_and_regression_report.md`

报告必须包括：

- 任务结论摘要，并明确区分事实、推断、建议
- 修改文件清单
- 四项 P0 的根因、修复方式、覆盖测试
- 历史 P0 回归检查
- 复跑命令与结果
- evidence 更新说明和路径
- P0 / P1 / P2 清单；若无，写“无”
- 是否建议进入下一轮独立工程复评
- 不得外推的结论
- 需要 PM 主会话确认的问题
- 后续任务建议

## 验收标准

只有满足以下条件，任务才算完成：

- 已读取指定输入材料。
- 已在 `lifeos/engineering/LIFEOS-P3-001/` 内完成必要窄范围工程修改。
- 已补充 P3-006 四项 P0 对应自动回归。
- 已回归 P3-002、P3-004、P3-005 历史 P0。
- 已复跑：
  - `python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py`
  - `cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py`
- 如遇 pyc 缓存权限问题，可使用临时 `PYTHONPYCACHEPREFIX`，并在报告中说明。
- `run_validation.py` 输出 P0=0；若 P0 不为 0，本任务不得标记 Completed。
- Evidence manifest、test results、regression assertions、snapshot manifest 已更新或明确说明无需更新的原因。
- 完整交付物已保存为指定文件。
- 已完成本地预检：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-007_third_p0_narrow_remediation_and_regression_report.md`，或明确说明允许跳过的原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、交付物路径、复跑结果、预检路径和是否需要 PM 决策。

## 限制条件

- 只允许修改 `lifeos/engineering/LIFEOS-P3-001/` 内的工程代码、测试、合成夹具、README 或 evidence，以及指定交付物报告。
- 不修改项目账本、PM Review、冻结状态、风险状态、决策记录或当前状态索引。
- 不修改 Stitch、PRD、产品定义、技术架构冻结文件或任务模板。
- 不处理真实数据、真实 Vault、真实文件系统广泛路径或真实外部服务。
- 不调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不启用真实 Tauri / IPC、文件导出扩权、向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不自行恢复 P3-001 工程基线；只能建议是否进入下一轮独立复评。
- 不自行关闭 R-0041；只能建议是否具备后续关闭条件。
- 如果发现需要改变 V1 范围、技术架构、核心领域语义或 AI 权限边界，必须标记为“需 PM 决策”，不得自行调整。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中不要粘贴完整报告、任务卡全文或大段日志。
