# LIFEOS-P2-003｜SP-02 Obsidian Vault 只读接入与来源身份技术 Spike

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

- 任务 ID：LIFEOS-P2-003
- 任务名称：SP-02 Obsidian Vault 只读接入与来源身份技术 Spike
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：3000-6000 字正文；原始日志、测试矩阵、夹具文件树、样例 JSON 和脚本可放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型负责人、AI 信任与安全负责人、产品架构负责人、体验设计负责人
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-001` 已通过 PM 验收并由用户确认采纳，证明在本次候选实现与 macOS arm64 环境下，本地保存、版本追加、幂等、离线保存 / 待同步分离、墓碑 / 撤回恢复优先等最小可靠存储语义成立。

`LIFEOS-P2-002` 已通过 PM 验收并由用户确认采纳，证明在合成映射和本地脚本范围内，Source / Artifact / Version / Derivation / Feedback / Authorization / AuditEntry / Link 的最小证据链包络成立，可支撑来源追溯、身份分离、依赖失效、权限继承、候选 Link 不扩权、导出 / 重导入不复活。

现在要验证 SP-02：

> Obsidian 作为 LifeOS 的优先外部来源，能否在“只读、不越权、不写回、不混淆来源身份”的前提下，稳定地产生 Source / Artifact / Version / 候选 Link 输入，并在新增、修改、移动、重命名、删除、不可达、断开、排除和撤权时保持可对账、可解释、可降级。

本任务允许在 `lifeos/spikes/SP-02/` 下创建模拟 Vault、最小本地验证代码、夹具、样例 JSON、日志和证据包，但不能连接或读取用户真实 Obsidian Vault，不能把实验代码视为产品代码、数据库 Schema 冻结或技术架构冻结。

## 目标

本任务完成后，要回答：

1. LifeOS 能否在模拟 Obsidian Vault 中做到全程只读：不写文件、不改名、不删除、不创建 sidecar、不修改 `.obsidian` 或元数据？
2. 首扫、增量、漏 watcher 事件后的 reconciliation、离线期间变化，能否稳定对账？
3. Markdown 文件能否映射为 Source / Artifact / Version，路径、hash、mtime、大小、解析状态和来源指针能否保持清楚？
4. 移动、重命名、复制、同内容不同文件、并发修改 / 删除时，能否避免错误强合并；不确定时能否降级为候选？
5. frontmatter、标签、标题、块引用、Markdown 链接、双链、嵌入、附件指针、乱码和破损链接，能否保真解析或明确失败？
6. 排除目录、撤回目录、路径遍历、绝对路径、越界符号链接、隐藏目录和 `.obsidian` 是否做到读取 / 索引 / 外发为 0？
7. 来源暂不可达、恢复可达和 `disconnect_source` 时，系统能否停止访问、保留合法副本边界，并把来源指针缺口表达清楚？
8. SP-02 结果是否足以支撑 Obsidian 作为 V1 `Should Have + 条件性需求` 继续保留、降级为手工导入 / 来源指针，或移出 V1 正式接入？

## 范围

本任务必须覆盖：

- 模拟 Vault 夹具：
  - 多目录 Markdown 文件；
  - 正常 / 异常 / 重复 YAML frontmatter；
  - 标签、标题、块引用、Markdown 链接、`[[双链]]`、嵌入、附件指针；
  - 破损链接、同名文件、同内容不同文件、乱码 / 非 UTF-8 文件；
  - 隐藏项、`.obsidian`、排除目录、越界符号链接；
  - 新增、修改、删除、重命名、移动、复制后删除、并发修改 / 删除、离线期间变化、暂不可达。
- 只读不变量验证：
  - 扫描前后 Vault 文件树一致性；
  - 原文件内容 hash 无 LifeOS 引起变化；
  - 元数据变化检测；
  - 写 / 改名 / 删除 / sidecar / `.obsidian` 修改调用为 0；
  - 若技术上无法拦截所有写调用，必须用前后快照 + 权限或 mock 层说明覆盖边界。
- 来源身份验证：
  - Vault → `Source`；
  - Markdown 文件 → 外部原始 `Artifact`；
  - 观察到的文件内容状态 → 来源版本 / `ArtifactVersion` 测试映射语义；
  - frontmatter / 标签 / 双链 / 文件夹 / 附件指针 → 外部来源片段或候选 Link，不自动成为 LifeOS Project、Action、Decision、事实或 Authorization。
- 对账与变化验证：
  - 首扫；
  - 正常增量；
  - 人为丢失 watcher 事件后的 reconciliation；
  - 应用离线期间新增 / 修改 / 删除；
  - 来源暂不可达后恢复。
- 移动 / 重命名 / 复制验证：
  - 明确移动 / 重命名样例；
  - 歧义样例；
  - 同内容不同文件；
  - 复制后删除；
  - 错误强合并为 0；
  - 不确定时产生候选而非自动合并。
- 边界与权限验证：
  - 排除目录；
  - 撤回目录；
  - 路径遍历；
  - 绝对路径；
  - 越界符号链接；
  - `.obsidian`；
  - 隐藏目录；
  - 外发 mock 字段为 0。
- 来源指针验证：
  - 可回到文件；
  - 可回到标题或块的近似定位；
  - 不可达时显示缺口，不伪装为最新；
  - 断开后停止监听和读取。

## 非范围

本任务暂时不要做：

- 不开发正式产品功能。
- 不修改 Stitch。
- 不连接、读取或扫描用户真实 Obsidian Vault。
- 不处理真实敏感数据、真实笔记、真实附件或真实 `.obsidian` 配置。
- 不读取用户 Home、桌面、文档目录中的真实 Vault 或笔记。
- 不调用真实模型、云服务、第三方 API、付费资源或外部账号。
- 不实现 Obsidian 插件。
- 不实现写回、双向同步、后台同步或 Vault 内导出。
- 不冻结数据库 Schema、API、事件流、文件监听方案、桌面框架、技术栈或技术架构。
- 不实现 SP-04 运行时授权、SP-05 删除 / 撤回物理清理、SP-06 离线同步、SP-07 搜索质量、SP-08 正式导出迁移、SP-09 容量性能。
- 不进入正式 MVP 开发。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/SP-02/` 下创建和修改：
  - 模拟 Vault；
  - 验证脚本；
  - 夹具文件；
  - 样例 JSON；
  - 测试矩阵；
  - 日志；
  - 环境说明；
  - 清理说明；
  - 兼容性矩阵；
  - 只读不变量报告；
  - reconciliation 报告；
  - 来源指针样例。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确任务目录或系统临时目录；不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话：

- 修改 `PROJECT_CONTEXT.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md` 等 PM 文件。
- 修改现有非 Spike 项目代码或无关文件。
- 删除、覆盖或移动用户真实数据。
- 使用破坏性命令清理宽泛目录。
- 读取真实 Obsidian Vault；即使用户机器上存在 Vault，也必须视为非授权目标。

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
- `lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- `lifeos/deliverables/LIFEOS-P0-009_core_domain_model_freeze_patch.md`
- `lifeos/deliverables/LIFEOS-P0-004_ai_permission_trust_model.md`
- `lifeos/deliverables/LIFEOS-P0-007_ai_trust_model_condition_remediation.md`
- `lifeos/deliverables/LIFEOS-P0-005_technical_feasibility_spike_plan.md`
- `lifeos/reviews/LIFEOS-P0-005_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-016_core_ia_end_to_end_flow.md`
- `lifeos/reviews/LIFEOS-P1-016_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- `lifeos/reviews/LIFEOS-P1-017_pm_review.md`
- `lifeos/deliverables/LIFEOS-P1-018_first_technical_spike_task_cards.md`
- `lifeos/reviews/LIFEOS-P1-018_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-001_sp01_local_durability_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-001_pm_review.md`
- `lifeos/spikes/SP-01/`
- `lifeos/deliverables/LIFEOS-P2-002_sp03_evidence_chain_mapping_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-002_pm_review.md`
- `lifeos/spikes/SP-03/`

## 角色检查点

主责角色必须重点回答：

- 模拟 Vault 验证是否足以证明“只读、不越界、可对账、来源身份稳定”的最小技术可行性？
- 只读不变量是否有机器可复核证据，而不是只靠承诺？
- 文件身份策略是否避免把路径、hash 或文件夹误当唯一永久身份？
- 移动 / 重命名 / 复制 / 删除的降级策略是否可解释？
- 任务是否避免冻结 watcher、数据库、Schema、API 或技术架构？

协审角色必须重点检查：

- 数据 / 领域模型负责人：Source、Artifact、Version、外部结构、候选 Link 与 LifeOS 业务对象是否边界清楚。
- AI 信任与安全负责人：Vault 连接是否不等于 AI、云、第三方或跨 Project 处理授权；排除 / 撤回 / 断源是否默认拒绝。
- 产品架构负责人：SP-02 是否服务 V1 的个人项目恢复与证据来源，而不是扩成 Obsidian 管理器、插件或同步器。
- 体验设计负责人：来源不可达、解析失败、疑似移动、部分扫描、排除、断开和缺口是否能转成用户可理解状态。

## 核心问题

请重点回答：

1. 你采用了什么模拟 Vault 夹具？为什么足以验证 SP-02，而不是连接真实 Vault？
2. 如何证明 LifeOS 对 Vault 全程只读？前后树、hash、元数据、写调用或 mock 拦截证据是什么？
3. Source / Artifact / Version / 候选 Link 的最小映射是什么？哪些内容绝不自动成为 Project、Action、Decision、事实或 Authorization？
4. 首扫、增量、漏 watcher 事件、离线期间变化、暂不可达和恢复可达如何对账？对账漏报和误报如何统计？
5. 移动、重命名、复制后删除、同内容不同文件和并发修改 / 删除如何判断？什么时候必须降级为候选？
6. Markdown、frontmatter、标签、标题、块、双链、嵌入、附件指针和乱码如何解析或明确失败？
7. 排除目录、撤回目录、路径遍历、绝对路径、越界符号链接、隐藏目录和 `.obsidian` 的读取 / 索引 / 外发如何证明为 0？
8. `disconnect_source` 后如何停止监听 / 读取？已有副本如何服从既有保留许可？本任务不能验证的部分是什么？
9. 来源指针如何回到文件、标题或块？不可达时如何显示缺口？
10. 最终结论是 Pass、Pass with Conditions、Fail 还是 Blocked？依据是什么？
11. 若 SP-02 不是无条件 Pass，Obsidian 在 V1 中应如何降级？
12. 哪些结论需要 PM / 用户确认？

## 最低验收断言

必须至少验证并报告：

- Vault 写 / 改名 / 删除 / sidecar / `.obsidian` 修改为 0。
- 扫描前后 Vault 原文件内容 hash 无 LifeOS 引起变化。
- 若检查元数据，必须说明哪些元数据稳定、哪些因测试环境不可作为强断言；不得伪造稳定性。
- 首扫后，稳定窗口内新增 / 修改 / 删除 100% 对账。
- 人为漏 watcher 事件后，reconciliation 可恢复一致状态。
- 明确移动 / 重命名样例可识别；歧义样例错误强合并为 0。
- 同内容不同文件不得自动合并为同一 Artifact。
- 排除目录、撤回目录、路径遍历、绝对路径、越界符号链接、隐藏目录和 `.obsidian` 读取 / 索引 / 外发为 0。
- frontmatter、标签、标题、双链、嵌入、附件指针能保真解析或明确失败；解析失败不覆盖上次有效版本，不把部分解析标为完整。
- 来源暂不可达时不伪装为最新；恢复可达后可对账；断开后监听和新读取为 0。
- 来源指针可返回文件 / 标题 / 块或明确缺口。
- AuditEntry、日志和样例不得包含真实敏感原文、用户真实路径、真实 Vault 名、完整提示词、模型输出、向量或可还原真实数据。

## 建议测试矩阵

至少包含：

1. 首扫模拟 Vault。
2. 新增 Markdown 文件。
3. 修改 Markdown 文件并生成新版本。
4. 删除 Markdown 文件并标记来源侧删除 / 不可达。
5. 漏 watcher 事件后 reconciliation。
6. 应用离线期间新增 / 修改 / 删除。
7. 同目录重命名。
8. 跨目录移动。
9. 复制后删除。
10. 同内容不同文件。
11. 并发修改 / 删除。
12. 正常 YAML frontmatter。
13. 异常 / 重复 YAML frontmatter。
14. 标签、标题、块引用。
15. Markdown 链接、双链、嵌入、附件指针。
16. 破损链接、乱码 / 非 UTF-8。
17. 排除目录不可读 / 不索引 / 不外发。
18. 路径遍历、绝对路径、越界符号链接拒绝。
19. `.obsidian` 与隐藏目录忽略。
20. 来源暂不可达与恢复可达。
21. `disconnect_source` 后停止监听 / 读取。
22. 来源指针返回与不可达缺口。
23. 只读前后树 / hash / 元数据核对。
24. 日志与 AuditEntry 隐私扫描。

## 交付物

请将完整 PM 可读交付物保存为 Markdown 文件，路径：

`lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`

同时将证据包保存到：

`lifeos/spikes/SP-02/`

证据包至少包括：

- `SP-02_report.md`
- `vault_fixture_manifest.md`
- `compatibility_matrix.csv`
- `readonly_invariant_report.md`
- `reconciliation_report.md`
- `source_pointer_samples.md`
- `environment.md`
- `raw_logs/`
- `cleanup.md`
- 本地验证脚本和夹具说明

最终 Markdown 交付物内容必须包括：

1. 任务边界与结论摘要
2. 模拟 Vault 夹具说明
3. 只读不变量验证
4. Source / Artifact / Version / 候选 Link 最小映射
5. 首扫、增量、漏事件、离线变化与 reconciliation 结果
6. 移动 / 重命名 / 复制 / 删除身份判断与降级策略
7. Markdown 兼容性与解析失败处理
8. 排除、撤回、路径越界、隐藏项和 `.obsidian` 边界验证
9. 来源暂不可达、恢复可达、断开来源和来源指针验证
10. 测试矩阵与最低验收断言结果
11. 日志与隐私检查
12. 最终结论：Pass / Pass with Conditions / Fail / Blocked
13. 对 V1 Obsidian 条件需求、后续 Spike、风险和技术架构候选的影响
14. 需要 PM / 用户确认的问题
15. 角色与关卡自检
16. 证据包路径清单

篇幅控制：

- 正文建议 3000-6000 字。
- 超出 SP-02 的问题放入“后续任务建议”，不要扩写 SP-04 / SP-05 / SP-06 / SP-08 / SP-09。

## 验收标准

只有满足以下条件，任务才算完成：

- 回答所有核心问题。
- 完整交付物已保存为 `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`。
- 证据包已保存到 `lifeos/spikes/SP-02/`。
- 证据包可复跑、可复核，且不依赖真实 Vault 或真实敏感数据。
- 覆盖主责角色检查点。
- 覆盖协审角色检查点。
- 明确说明 Gate 2、Gate 3、Gate 4 在本任务范围内是否通过。
- 明确区分事实、推断、建议和待确认问题。
- 列出风险、限制、降级路径和需 PM 确认的问题。
- 使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md` 的格式回复。

## 判定规则

- **Pass**：全部只读、边界、对账、来源身份、解析失败、断开和隐私 P0 断言通过；证据可复跑。
- **Pass with Conditions**：P0 断言全部通过，仅自动移动识别率、块定位精度、附件元数据覆盖、平台差异或性能预算存在有界缺口，且已有明确降级和复验条件。
- **Fail**：任一 Vault 改写、越界读取 / 索引 / 外发、错误强合并、不可恢复对账漂移、解析失败覆盖有效版本、断开后继续读取、日志泄露真实敏感信息，或证据不可复现。
- **Blocked**：缺少必要环境或任务边界不足，无法安全执行；不得用真实 Vault 弥补夹具不足。

## 降级路径

若 SP-02 无法无条件通过，应明确建议以下一种或多种降级：

- Obsidian V1 正式接入继续保持条件性需求，不进入 Must。
- 降级为手工导入。
- 降级为来源指针：用户手动提供文件 / 路径 / 引用，不做自动扫描。
- 移动 / 重命名仅作为候选关系，需要用户确认。
- 附件仅保留指针、类型、大小和可达状态，不提取正文。
- 块定位仅提供标题 / 附近文本 / 文件级返回，不承诺永久块级稳定。
- 将 Obsidian 正式接入移出 V1。

只读、不越权、不写回、不把外部结构自动业务化、不读取真实敏感数据不可降级。

## 限制条件

- 不修改代码，除本任务授权的 `lifeos/spikes/SP-02/` 验证代码和证据包。
- 不修改 Stitch。
- 不创建外部账号、部署服务或调用付费资源。
- 不改变 LifeOS 产品定位。
- 不擅自冻结 V1 范围、技术架构、Schema、API 或数据模型。
- 不读取、扫描或连接真实 Obsidian Vault。
- 不处理真实敏感数据。
- 不使用 `$HOME`、`~`、仓库根目录或广泛目录作为清理目标。
- 不把 SP-02 Pass 解释为 Obsidian 正式接入承诺、云 / 第三方处理许可、写回许可或 MVP 开发准入。

## 会话回复格式

任务完成后，请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

会话回复不要粘贴完整交付物正文，只输出摘要、交付物路径、证据包路径、是否需要 PM 决策。
