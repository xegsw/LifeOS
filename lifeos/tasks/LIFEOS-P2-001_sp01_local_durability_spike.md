# LIFEOS-P2-001｜SP-01 本地可靠落盘、离线捕获、备份恢复技术 Spike

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的相关文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-001
- 任务名称：SP-01 本地可靠落盘、离线捕获、备份恢复技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵和脚本可放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、体验设计负责人、产品架构负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

LifeOS 已完成 P1-018 首批技术 Spike 任务卡，并由用户确认采纳为执行合同。当前正式 MVP 开发仍为 `Blocked / Not Allowed`。

SP-01 是首个真实技术验证任务，验证 LifeOS 最底层的信任地板：

> 用户输入内容后，系统能否在本地可靠保存、离线可用、故障后可恢复，并且不会把未耐久提交的内容提前告诉用户“已保存”。

如果 SP-01 不成立，后续 Obsidian 接入、AI 证据链、搜索、同步和真实自用数据启用都没有可靠地基。

本任务允许在本地创建最小验证代码、夹具、脚本、日志和报告，但只限于 Spike 工作区，不能把实验代码视为产品代码或技术架构冻结。

## 目标

本任务完成后，要回答：

1. LifeOS 能否在无网络场景下可靠保存用户原始文本、版本、最小元数据和状态？
2. “已保存”回执是否只在耐久提交完成后出现？
3. 写前、写中、提交后、回执后强杀，是否会导致已确认保存内容丢失、半写、重复或覆盖？
4. 磁盘满、I/O 失败、重复提交、时钟偏移、长读 / 后台索引等场景下，系统是否能保持正确状态和可行动错误？
5. 一致备份和恢复是否能保留原文、版本、墓碑、撤回状态和待同步状态？
6. 删除墓碑和撤回状态是否能在恢复、重导入或旧数据重放前优先生效，避免已删内容复活？
7. 当前候选实现是否足以进入下一项 Spike，还是必须返工、降级或调整技术方向？

## 范围

本任务必须覆盖：

- 最小本地存储验证：
  - 用户原文。
  - 内容版本。
  - 幂等键 / 重复提交处理。
  - 最小保存状态：编辑中、保存中、耐久已保存、失败、离线本地已保存、待同步。
  - 删除墓碑。
  - 撤回 Feedback 或撤回处理许可的最小状态样本。
- 故障注入：
  - 写前强杀。
  - 写中强杀。
  - 提交后 / 回执前强杀。
  - 回执后强杀。
  - 磁盘满或模拟写失败。
  - I/O 错误。
  - 重复提交。
  - 备份恢复。
  - 长读或后台索引并发影响。
- 测试夹具：
  - 至少 1,000 条确定性记录。
  - 包含重复幂等键。
  - 包含同一 Artifact 的两个版本。
  - 包含删除墓碑、撤回 Feedback、待同步状态。
  - 不包含真实敏感数据。
- 验证输出：
  - 可复跑脚本。
  - 测试矩阵。
  - 运行环境说明。
  - 原始日志。
  - 失败样例。
  - 性能 / 资源数据。
  - 备份恢复报告。
  - 清理说明。
  - PM 可读的 Spike 结论报告。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能。
- 不修改 Stitch。
- 不连接真实 Obsidian Vault。
- 不处理真实敏感数据。
- 不调用真实模型、云服务或第三方 API。
- 不实现云同步、多设备同步、正式附件架构或生产备份 SLA。
- 不冻结数据库、框架、同步架构、API、Schema 或技术栈。
- 不实现完整 UI。
- 不进入正式 MVP 开发。
- 不把本次 Spike 通过解释为 SP-02 / SP-03 / SP-04 通过。
- 不把 LifeOS 作为重要真实数据的唯一副本。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-01/` 下创建和修改验证脚本、夹具、测试数据、日志、环境说明、测试矩阵和清理说明。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`
- 运行本地命令执行测试与故障模拟。
- 创建临时目录用于测试，但必须是明确的任务目录或系统临时目录，且不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话：

- 修改 `PROJECT_CONTEXT.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md` 等 PM 文件。
- 修改现有非 Spike 项目代码或无关文件。
- 删除、覆盖或移动用户真实数据。
- 使用破坏性命令清理宽泛目录。

## 输入材料

请参考：

- `lifeos/PROJECT_CONTEXT.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md`
- `lifeos/TASK_REGISTRY.md`
- `lifeos/DECISION_LOG.md`
- `lifeos/RISK_LOG.md`
- `lifeos/OPEN_QUESTIONS.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-015_self_use_mvp_min_slice_entry_checklist.md`
- `lifeos/reviews/LIFEOS-P1-015_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/reviews/LIFEOS-P1-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-018_first_technical_spike_task_cards.md`
- `lifeos/reviews/LIFEOS-P1-018_pm_review.md`

## 角色检查点

主责角色必须重点回答：

- 本地保存方案是否能在有限实验中证明正确性？
- 故障注入是否覆盖 P1-018 指定的关键风险？
- 证据是否可复跑、可复核，而不是只给主观结论？
- 候选实现是否暴露出技术栈风险、性能风险或架构风险？
- 是否避免把 Spike 代码当成正式产品架构？

协审角色必须重点检查：

- 数据 / 领域模型负责人：用户原文、Artifact、Version、墓碑、撤回状态、幂等键和待同步状态是否语义清楚。
- AI 信任与安全负责人：撤回、墓碑和恢复顺序是否防止旧数据复活；日志是否避免可还原敏感原文。
- 体验设计负责人：保存中、已保存、保存失败、离线已本地保存、待同步、恢复后状态是否能转成用户可理解表达。
- 产品架构负责人：本 Spike 是否服务个人终身外脑的可信记录地基，没有扩成正式开发或无边界技术研究。

## 核心问题

请重点回答：

1. 你采用了什么最小验证实现？为什么足以验证 SP-01，而不是冻结架构？
2. 夹具如何生成？是否满足 1,000 条、重复幂等键、两版本、墓碑、撤回和待同步状态？
3. “已保存”在实现中对应哪个耐久点？如何证明没有早报？
4. 强杀、磁盘满 / I/O 失败、重复提交、长读 / 后台索引、备份恢复分别如何测试？
5. 已确认保存记录的 hash、版本、数量、幂等结果是否全部一致？
6. 删除墓碑和撤回状态在恢复 / 重导入前是否优先生效？是否存在复活？
7. 性能和资源数据是否满足 P1-018 的暂定工程预算？若不满足，是否仍满足正确性底线？
8. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
9. 若 Fail 或 Pass with Conditions，允许什么降级，阻塞哪些后续任务？
10. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- 已返回“已保存”的记录，恢复后 100% 存在且 hash 一致。
- 未确认提交可以不存在，但不得出现半条原文、错误版本或静默覆盖。
- 写前、写中、提交后 / 回执前、回执后强杀场景均有测试证据。
- 磁盘满或模拟写失败时，误报保存次数为 0。
- 重复提交不会创建不可解释重复记录，也不会覆盖旧版本。
- 删除墓碑和撤回状态在备份恢复后优先生效，活跃路径复活数为 0。
- 长读或后台索引不阻塞捕获主路径；若性能预算未达标，必须说明影响和降级。
- 日志、AuditEntry 夹具和报告不得包含可还原真实敏感原文。

参考工程预算：

- 单条文本捕获 p95 ≤ 150ms。
- 单条文本捕获 p99 ≤ 500ms。
- 至少覆盖 1,000 条确定性记录。

以上预算用于 Spike 判断，不是市场承诺。正确性底线优先于性能优化。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-01/`

证据包至少包括：

- `SP-01_report.md`
- `test_matrix.csv` 或等价测试矩阵文件
- `environment.md`
- `raw_logs/`
- `backup_restore_report.md`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 验证实现说明
3. 测试夹具说明
4. 故障注入与测试矩阵
5. 验收断言结果
6. 性能 / 资源结果
7. 备份恢复与墓碑 / 撤回不复活验证
8. 日志与隐私检查
9. 结论：Pass / Pass with Conditions / Fail / Blocked
10. 降级建议与后续影响
11. 需要 PM / 用户确认的问题
12. 角色与关卡自检
13. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 原始日志、测试矩阵、脚本、夹具说明可放证据包，不在正文无限展开。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-01/`。
- 会话回复中提供完整交付物路径和证据包路径。
- 已实际运行本地验证，不只是写计划。
- 覆盖 1,000 条确定性记录或明确说明无法覆盖的阻塞原因。
- 覆盖指定强杀 / 写失败 / 重复提交 / 备份恢复 / 墓碑不复活测试，或明确说明阻塞原因。
- 明确给出 Pass / Pass with Conditions / Fail / Blocked 结论。
- 明确说明 Gate 2、Gate 3、Gate 4 是否通过。
- 明确区分事实、推断、建议。
- 标记所有需要 PM / 用户确认的结论。
- 不处理真实敏感数据、不连接真实 Vault、不调用云 / 第三方 / 真实模型、不修改 Stitch、不冻结技术架构、不进入正式 MVP 开发。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 限制条件

- 只能使用合成、脱敏或可丢弃数据。
- 不得使用 LifeOS 作为真实重要数据的唯一副本。
- 不得读取、复制、移动、删除用户真实文档、Obsidian Vault 或敏感文件。
- 不得调用外部模型、云服务、第三方 API 或付费资源。
- 不得修改 PM 文件。
- 不得把本地验证代码迁入正式产品目录。
- 不得把候选实现、库、数据库或脚本写成技术架构冻结结论。
- 不得以性能优化牺牲耐久性、版本、墓碑、撤回或不复活底线。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要、完整交付物路径、证据包路径和是否需要 PM 决策。
