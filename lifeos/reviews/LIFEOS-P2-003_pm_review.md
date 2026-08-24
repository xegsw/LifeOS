# LIFEOS-P2-003｜PM 验收记录

## 验收信息

- 任务 ID：LIFEOS-P2-003
- 任务名称：SP-02 Obsidian Vault 只读接入与来源身份技术 Spike
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Yes，建议进入 SP-04 六维授权判定与本地 / 云 / 第三方处理边界技术 Spike
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-08

## PM 总结

1. `LIFEOS-P2-003` 按任务卡完成了 SP-02 技术 Spike，交付物、模拟 Vault、验证脚本、测试矩阵、只读不变量报告、reconciliation 报告、来源指针样例、隐私扫描和清理说明齐全。
2. PM 复跑 `python3 lifeos/spikes/SP-02/run_spike.py`，结果为 24/24 PASS，P0 失败 0；证据包与报告结论一致。
3. 本任务证明了在 macOS arm64 / Python 3.9.6 / 确定性合成 Vault / 候选扫描器范围内，Obsidian 来源只读接入、来源身份、对账、边界拒绝、移动 / 重命名降级、来源指针和日志隐私具备最小可行性。
4. 本任务没有连接或读取用户真实 Obsidian Vault，没有处理真实敏感数据，没有调用云 / 第三方 / 真实模型，没有修改 Stitch、PM 文件或产品代码。
5. 项目级结论应保持 `Pass with Conditions`，因为跨平台、同步盘、大 Vault、正式解析库、真实运行时授权、历史索引 / 缓存清理和真实用户 Vault 行为尚未验证。
6. Obsidian 可继续保留为 V1 `Should Have + 条件性需求`；不得升级为 Must，不得直接承诺正式接入。
7. 正式 MVP 开发仍未准入；SP-02 通过不代表真实 Vault 授权、AI / 云 / 第三方处理许可、写回许可、插件、双向同步、技术架构冻结或 Stage 3 准入。

## 角色与关卡验收

- 主责角色覆盖情况：技术架构负责人视角覆盖充分；报告给出了模拟 Vault、只读快照、访问计数、移动 / 重命名策略、reconciliation 机制、边界探针和非冻结说明。
- 协审角色覆盖情况：
  - 数据 / 领域模型负责人：覆盖 Vault → Source、Markdown 文件 → Artifact、内容观察 → Version、frontmatter / 标签 / 双链 / 附件 → 外部片段或候选 Link 的边界。
  - AI 信任与安全负责人：覆盖连接 Vault 不等于 AI / 云 / 第三方授权，排除 / 撤回 / 断源默认拒绝，外发 mock 为 0。
  - 产品架构负责人：未把任务扩成 Obsidian 管理器、插件、同步器或企业连接平台，仍服务个人项目恢复和证据来源。
  - 体验设计负责人：提供了不可达、解析失败、疑似移动、排除、断开、来源缺口等可转译为用户状态的语义。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass（SP-02 测试语义层）。
  - Gate 3 AI 权限与信任评审：Pass（本地只读 / 默认拒绝 / 外发边界层）。
  - Gate 4 技术可行性评审：Pass with Conditions。
- 未通过或需后续确认关卡：
  - 未验证 Windows / Linux / 同步盘 / 网络盘 / 跨卷移动 / 复制恢复下的文件身份可靠性。
  - 未验证真实 Vault 规模、真实社区插件语法、正式解析库、长期 watcher 成本。
  - 未验证运行时六维授权、AI / 云 / 第三方处理、撤回 / 删除传播、同步和容量性能。
- 是否属于关键冻结事项：否。它是技术 Spike 结果，不是技术架构冻结、数据模型冻结或 MVP 开发准入。
- 是否需要独立评审：当前任务不需要独立评审；未来技术架构冻结和进入正式 MVP 开发必须另行独立评审。
- 独立评审路径：不适用。
- 独立评审结论：不适用。
- 是否允许进入下一任务或下一阶段：允许进入下一技术 Spike；不允许进入 Stage 3 MVP 工程实现。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否，Pass with Conditions。
- 冻结范围：无。
- 可作为后续输入的范围：
  - SP-02 在合成 Vault 中验证过的只读接入与来源身份不变量。
  - Vault / Markdown / 内容观察 / 外部结构到 Source / Artifact / Version / 候选 Link 的测试语义映射。
  - watcher 不作为唯一真相、reconciliation 承担最终对账的技术原则。
  - 唯一强证据可自动移动；hash-only、复制替换、歧义场景必须候选化。
  - frontmatter、标签、双链、文件夹、附件指针不得自动成为 Project、事实、Action、Decision 或 Authorization。
  - 排除、撤回、路径越界、隐藏项和 `.obsidian` 默认拒绝的边界。
- 未冻结内容：
  - Obsidian 正式 V1 接入承诺。
  - 真实 Vault 启用。
  - 文件监听库、解析库、存储、Schema、API、桌面框架或技术架构。
  - 跨平台文件身份策略。
  - 同步盘 / 网络盘对账策略。
  - 附件正文提取。
  - 块级永久定位。
  - 云 / 第三方处理授权。
  - 写回、插件、双向同步。
  - MVP 开发准入。
- 是否允许进入下一任务：Yes，建议启动 SP-04。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

### 1. 是否采纳 SP-02 `Pass with Conditions`

- 问题：是否确认 `LIFEOS-P2-003` 作为 SP-02 `Pass with Conditions`，并允许后续任务继承其只读来源身份和候选化原则？
- PM 建议：采纳。
- 可选方向：
  - 采纳：SP-02 成为 SP-04、SP-05、SP-06、SP-08 和未来技术架构候选输入。
  - 不采纳：要求专项会话补充或重做 Obsidian 只读接入验证。
- 不确认的影响：Obsidian 条件需求仍不能继续进入后续授权 / 清理验证。

### 2. 是否维持 Obsidian 为 V1 `Should Have + 条件性需求`

- 问题：SP-02 已有最小可行性证据，但仍有跨平台、同步盘、大 Vault 等条件；是否继续把 Obsidian 保持为条件项，而不是升为 Must？
- PM 建议：维持 `Should Have + 条件性需求`。
- 可选方向：
  - 维持条件项：继续验证授权、清理、同步和容量。
  - 升为 Must：不建议，当前证据不足。
  - 降级为手工导入 / 来源指针：保守可行，但会削弱 V1 对技术型独立产品构建者的高价值来源支持。
- 不确认的影响：后续范围表述容易在“正式接入”和“条件验证”之间摇摆。

### 3. 是否启动 SP-04

- 问题：下一步是否启动六维授权判定与本地 / 云 / 第三方处理边界 Spike？
- PM 建议：启动 SP-04。
- 可选方向：
  - 启动 SP-04：验证 Vault 内容、LifeOS 内容和 AI 派生在本地 / 云 / 第三方路径上的具体授权判定。
  - 先做 SP-05：也可行，但删除 / 撤回传播需要先知道运行时授权和处理者边界。
  - 暂停技术 Spike：转做管理或文档整理。
- 不确认的影响：真实 Vault 内容仍不得进入 AI、云或第三方路径；MVP 开发继续阻塞。

## 整改建议

当前不要求 P2-003 专项会话返工。

后续任务应补充验证：

1. SP-04：六维 Authorization、处理者政策包络、默认拒绝、本地 / 云 / 第三方路径和 Project / Link 不扩权。
2. SP-05：断源、撤权、删除、撤回对索引、缓存、队列、备份、离线设备和第三方 mock 的活跃阻断与物理清理状态。
3. SP-06：多设备、离线、同步盘、旧设备重连时的来源身份、墓碑、用户确认和候选 Link 一致性。
4. SP-09 或架构复验：大 Vault、长时间 watcher、reconciliation 成本和解析性能。

## 可接受内容

- SP-02 任务结论：Pass with Conditions（限 macOS arm64、Python 3.9.6、确定性合成 Vault、候选只读扫描器）。
- 在本次范围内，Vault 写 / 改名 / 删除 / sidecar / `.obsidian` 修改为 0。
- 扫描窗口前后树、hash 和强断言元数据一致。
- 首扫、增量、漏 watcher 事件、离线变化、暂不可达和恢复可达均可对账。
- 同内容不同文件不得自动合并；hash-only、复制替换、歧义场景候选化。
- frontmatter、标签、标题、块引用、Markdown 链接、双链、嵌入、附件指针可保真解析或明确失败；解析失败不覆盖有效版本。
- 排除目录、撤回目录、路径遍历、绝对路径、越界符号链接、隐藏目录和 `.obsidian` 的读取 / 索引 / 外发为 0。
- 来源指针可返回文件 / 标题 / 块或明确缺口；不可达不伪装为最新；断开来源后监听和新读取为 0。

## 不接受或需谨慎内容

- 不接受把 SP-02 解释为 Obsidian 正式接入已经通过。
- 不接受把“只读扫描通过”解释为允许本地 AI、云同步、第三方模型或长期保留副本。
- 不接受把 file key、路径、hash、mtime、大小中的任一项单独当作永久身份。
- 不接受把 frontmatter、标签、双链或文件夹自动解释为 LifeOS Project、事实、Action、Decision 或 Authorization。
- 不接受把候选扫描器、解析器、watcher、Schema、API 或技术架构冻结。
- 需谨慎处理同步盘、跨平台、跨卷移动、复制恢复、临时文件和社区插件语法带来的身份漂移。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：需要更新，记录 SP-02 PM 验收通过及条件边界。
- `lifeos/PM_OPERATING_MODEL.md`：不需要更新。
- `lifeos/TASK_REGISTRY.md`：需要更新，P2-003 从 Ready 改为 Accepted。
- `lifeos/FREEZE_STATUS.md`：需要更新，SP-02 改为 Pass with Conditions，等待用户确认是否采纳。
- `lifeos/DECISION_LOG.md`：需要更新，新增 D-0097。
- `lifeos/RISK_LOG.md`：需要更新，新增 SP-02 条件通过被误读为真实 Vault / 正式接入准入的风险。
- `lifeos/OPEN_QUESTIONS.md`：需要更新，新增技术架构冻结前需回答的 Obsidian 复验问题。

## 下一步任务建议

PM 建议用户确认采纳 P2-003 后，启动：

`LIFEOS-P2-004｜SP-04 六维授权判定与本地 / 云 / 第三方处理边界技术 Spike`

建议原因：

- SP-01 已证明内容能可靠保存。
- SP-03 已证明内容能被可信追溯、确认、失效。
- SP-02 已证明 Obsidian 作为本地只读来源有最小可行性。
- 下一块地基应验证“哪些内容、在什么范围、为了什么目的、由谁、在哪里、何时可以处理”，否则真实 Vault 内容仍不能进入 AI、云或第三方路径。
