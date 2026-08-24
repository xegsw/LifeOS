# LIFEOS-P2-014｜FTS 维护隔离窄测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-014
- 任务名称：FTS 维护隔离窄测
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：2000-4000 字正文；原始日志、测试结果、性能数据和失败样例放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-009` 暴露了一个 P0 条件项：全量 FTS rebuild 可能阻塞前台权威捕获约 4 秒，超过已采纳的 1 秒候选门槛。`LIFEOS-P2-012` 与 `LIFEOS-P2-013` 已确认：FTS 维护隔离窄测是技术架构冻结前硬条件。

本任务只验证 FTS 维护任务能否与权威捕获隔离。它不是正式搜索实现，不冻结 FTS 表结构、调度策略、性能 SLA 或技术架构。

## 目标

本任务完成后，需要回答：

1. 前台权威捕获是否能在 FTS 增量维护、全量重建、影子索引切换或中断恢复期间保持短事务优先？
2. “已保存”是否只在权威数据耐久提交后出现，且误报保存数为 0？
3. 搜索结果是否始终回连当前权威状态，做到权限、tombstone、restriction generation 泄漏数为 0？
4. 影子索引或分块重建失败时，是否能安全回退，不破坏权威库或旧索引？
5. 当前结果是否足以关闭 R-0039，或需要降级 / 返工？

## 范围

本任务必须覆盖：

- 使用确定性合成数据，不使用真实用户数据、真实 Vault、真实路径或真实敏感内容。
- 至少完成 10 万内容单元 / 30 万分块快速回归。
- 尽力完成 100 万内容单元 / 300 万分块主档验证；如本机资源不足，必须说明原因、完成可复跑较小规模验证，并标记结论上限。
- 验证前台捕获与以下任务并发：
  - FTS 增量索引；
  - 全量影子索引或可中断分块重建；
  - 索引校验；
  - generation 切换；
  - 切换失败回退；
  - 空间不足或重建中断。
- 报告捕获 p50 / p95 / p99 / 最大等待。
- 验证保存失败注入下误报保存数为 0。
- 验证陈旧 posting 回连当前权威状态后，权限、tombstone、restriction generation 泄漏数均为 0。
- 形成证据包入口 `README.md` 或 `MANIFEST.md`。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能、UI、搜索服务或同步服务。
- 不冻结技术架构、SQLite Schema、FTS 表结构、PRAGMA、调度策略、性能 SLA、API 或队列实现。
- 不修改 Stitch、PRD、V1 范围、核心领域模型或 AI 权限模型。
- 不连接真实 Obsidian Vault，不处理真实敏感数据。
- 不调用真实模型、真实云、真实第三方 API、外部账号或付费资源。
- 不进入正式 MVP 开发。
- 不为了性能绕过权威保存、权限过滤、墓碑优先、来源追踪、用户原文保护或 AI 内容身份边界。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/P2-014-fts-maintenance-isolation/` 下创建和修改合成数据、验证脚本、测试矩阵、原始结果、失败样例、环境说明和证据入口。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-014_fts_maintenance_isolation_narrow_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确任务目录或系统临时目录；不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话修改 PM 文件、现有非 Spike 项目代码或无关文件；不得删除、覆盖或移动用户真实数据。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md` 中“技术架构”“技术架构冻结条件最终补丁”“SP-09”“MVP 开发准入”相关行
- `lifeos/RISK_LOG.md` 中 R-0039
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P2-009_sp09_capacity_performance_spike.md`
- `lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-009_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-013_technical_architecture_freeze_condition_final_patch.md`
- `lifeos/reviews/LIFEOS-P2-013_pm_review.md`
- `lifeos/DECISION_LOG.md` 中 D-0109、D-0117、D-0118

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取 P2-013 第 5 节 FTS 窄测合同和 P2-009 中 FTS rebuild 失败证据。
- 不主动读取完整 evidence 日志；先读 evidence `README.md` / `MANIFEST.md`，仅在需要复核失败原因时读取对应日志。
- 不主动读取完整 `PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `DECISION_LOG.md`；只读取任务卡指定决策或最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。

## 核心 P0 断言

必须至少验证并报告：

1. 前台权威捕获不等待长索引事务。
2. 捕获最大等待不超过已采纳的 1 秒候选门槛；必须报告 p50 / p95 / p99 / 最大等待。
3. 保存失败注入下误报保存数为 0。
4. 权限泄漏数为 0。
5. tombstone 泄漏数为 0。
6. restriction generation 泄漏数为 0。
7. 索引切换必须在校验通过后发生；切换失败可回退合法旧索引。
8. 空间不足、校验失败或重建中断不得破坏权威库；捕获继续可用或明确失败。
9. 旧任务、旧索引或旧 generation 不得覆盖更高 generation。
10. 日志和证据包不得包含真实敏感原文、真实路径、真实 Vault 名或完整真实 prompt / 输出。

## Pass / Conditions / Fail 标准

- Pass：全部 P0 断言通过；主档规模达到 100 万内容单元 / 300 万分块；最大等待 ≤ 1 秒；误报保存、权限泄漏、tombstone 泄漏、generation 泄漏均为 0；切换可校验回退；证据包可复核。
- Pass with Conditions：全部 P0 安全与保存真实性断言通过，仅主档规模、非目标平台或非 V1 能力存在有限缺口；必须列出条件范围、关闭能力、补测触发器和 PM 可接受理由。
- Fail：任一 P0 断言失败；包括捕获超时、误报保存、权限 / tombstone / generation 泄漏、长事务依赖、不可回退、权威库或旧索引损坏、证据不可复核。

## 角色检查点

主责角色必须重点回答：

- FTS 维护隔离是否真的关闭 R-0039？
- 实测数据与未验证边界是否清楚？
- 是否存在必须降级为增量、维护窗口、分块重建或暂缓全量 rebuild 的证据？

协审角色必须重点检查：

- 数据 / 领域模型负责人：权威、派生、generation、tombstone、Source、ArtifactVersion 边界是否没有被 FTS 优化绕过。
- AI 信任与安全负责人：权限撤回、restriction generation、派生重建和日志隐私是否仍 fail closed。
- 体验设计负责人：索引中、索引失败、部分索引、维护中、回退中是否能转译成诚实用户状态。
- PM：本任务是否只关闭 R-0039，不偷渡技术架构冻结或 MVP 准入。

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P2-014_fts_maintenance_isolation_narrow_spike_report.md`

交付物至少包括：

1. 执行摘要
2. 测试环境与合成数据说明
3. 验证方案与证据入口
4. P0 断言结果矩阵
5. 捕获延迟、索引维护、切换 / 回退结果
6. 泄漏、误报保存、损坏与隐私扫描结果
7. Pass / Conditions / Fail 结论
8. 可冻结输入、不可外推内容与降级建议
9. 风险与待 PM 确认事项

## 验收标准

只有满足以下条件，任务才算完成：

- 已运行本地可复核验证，或明确说明本机资源阻塞和已完成的替代验证边界。
- 完整证据包已写入 `lifeos/spikes/P2-014-fts-maintenance-isolation/`，并有 `README.md` 或 `MANIFEST.md`。
- 完整交付物已保存到指定路径。
- 明确区分事实、实测、估算、推断和建议。
- 覆盖所有 P0 断言。
- 明确结论是 Pass、Pass with Conditions、Fail 还是 Blocked。
- 明确哪些结论需要 PM / 用户确认。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，且不粘贴完整交付物正文。

## 限制条件

- 不修改产品代码。
- 不修改 Stitch。
- 不处理真实敏感数据、真实 Vault 或真实第三方数据。
- 不调用真实模型、真实云、真实第三方 API 或付费资源。
- 不冻结技术架构、Schema、API、性能 SLA 或 MVP 开发准入。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入交付物文件。
