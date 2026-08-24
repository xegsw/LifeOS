# LIFEOS-P1-017｜PM 验收报告

## 验收信息

- 任务 ID：LIFEOS-P1-017
- 任务名称：Obsidian 只读接入条件需求
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P1-017_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Yes
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-08

## PM 总结

- P1-017 清楚回答了“为什么 Obsidian 只读”与“LifeOS 新知识写在哪里”这两个关键问题：Obsidian 是外部只读来源，LifeOS 有自己的可写权威层。
- 交付物没有把 LifeOS 降格成 Obsidian 插件、同步器或知识库管理器，也没有把一次性 Markdown 导出偷换成后台写回或双向同步。
- Source / Artifact / 版本 / Derivation / Feedback / Authorization / Link 的语义映射清楚，能继承已冻结的核心领域模型和 AI 信任基线。
- 对 Obsidian 的 frontmatter、标签、双链、文件夹、附件等内容处理保持克制：它们首先是外部来源片段或候选关系，不自动成为 LifeOS Project、事实、Action、Decision 或授权范围。
- Must / Should / Not Now 划分合理，尤其把“SP-02 与 SP-03 均 Pass”列为 Obsidian 正式接入的前提，避免定义线越过验证线。
- 第 11 节已足够转化为 SP-02 / SP-03 技术 Spike 任务卡输入；同时对 SP-04 / SP-05 / SP-08 的影响也有提示。
- 本交付物仍是条件需求基线候选，不冻结实现范围、技术架构、Schema、API、插件方案或正式 MVP 开发准入。

## 角色与关卡验收

- 主责角色覆盖情况：Pass。数据 / 领域模型负责人视角下，Obsidian Source、外部 Artifact/版本、LifeOS 写入层、AI Derivation、用户确认和 Feedback 边界清楚。
- 协审角色覆盖情况：Pass。产品架构、AI 信任与安全、技术架构、体验设计四个协审视角均被覆盖。
- 已通过关卡：Gate 1 产品一致性；Gate 2 数据与来源；Gate 3 AI 权限与信任；Gate 4 技术可行性中的“验证合同层”。
- 未通过或需后续确认关卡：Gate 4 实现层未通过，需 SP-02 / SP-03 实测；SP-04 / SP-05 / SP-08 也会影响最终实现边界。
- 是否属于关键冻结事项：否。本任务不是技术架构冻结、V1 范围调整或 MVP 开发准入。
- 是否需要独立评审：当前不需要。若未来要把 Obsidian 接入正式纳入 V1 实现承诺，应基于 Spike 结果另行评审。
- 独立评审路径：不适用。
- 独立评审结论：不适用。
- 是否允许进入下一任务或下一阶段：允许进入下一任务；不允许进入 Stage 3 或正式 MVP 开发。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否，Accepted but Not Frozen。
- 冻结范围：无。
- 未冻结内容：Obsidian 是否正式进入 V1 实现承诺、具体文件监听实现、解析器方案、Schema、API、同步策略、导出格式细节、frontmatter 命名、块定位算法、移动识别算法、删除 / 保留 SLA、插件方案、正式 MVP 开发准入。
- 是否允许进入下一任务：是。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是，将“Obsidian 只读接入条件需求”更新为 Accepted but Not Frozen。

## 需要用户确认的事项

1. 是否采纳 P1-017 的 Must / Should / Not Now 作为 Obsidian 条件需求基线。
   - PM 建议：采纳。
   - 可选方向：采纳；或要求进一步压缩 Obsidian 接入能力，仅保留手工导入 / 来源指针。
   - 不确认的影响：SP-02 / SP-03 任务卡缺少统一验收边界。

2. 是否接受“一次性 Obsidian 兼容 Markdown 导出”为 Should，而不是 Must。
   - PM 建议：接受。
   - 可选方向：作为 Should；提升为 Must；或完全后置。
   - 不确认的影响：导出和 Obsidian 写回边界可能在后续任务中被混淆。

3. 是否批准 P1-017 第 11 节作为 SP-02 / SP-03 的强制夹具、断言和验收案例输入。
   - PM 建议：批准。
   - 可选方向：批准；或先拆成更轻的 Spike 输入整理任务。
   - 不确认的影响：SP-02 / SP-03 可能只验证 happy path，漏掉只读、排除目录、撤权、不可达和证据链。

4. 是否接受 SP-02 或 SP-03 失败时，Obsidian 接入应降级为手工导入 / 来源指针，或移出 V1。
   - PM 建议：接受。
   - 可选方向：接受降级规则；或坚持 Obsidian 必进 V1。
   - 不确认的影响：技术失败时会出现范围争议，拖慢进入可运行产品。

## 整改建议

- 无需返工。
- 后续任务应把 P1-017 第 11 节转成可执行的 SP-02 / SP-03 技术 Spike 任务卡。
- Markdown 导出的具体 frontmatter、文件命名、冲突预览和部分失败体验，不应在 P1-017 内继续扩写，建议后续作为导出专项或原型状态处理。
- 断开来源后的副本保留策略需要后续 PRD / Spike 明确，但当前不阻塞 P1-017 验收。

## 可接受内容

- Obsidian V1 只读接入定义：读取、解析、索引、来源指针、版本记录、用户明确触发的导出允许；静默修改、插件、双向同步、后台写回禁止。
- 只读不变量：除用户明确导出外，LifeOS 不应改变 Vault 树、文件内容 hash 或文件元数据。
- LifeOS 新知识写入 LifeOS 自己的写入层，包括内部原始 Artifact、Derivation、用户确认对象、Feedback、Authorization、AuditEntry 和 Link。
- Vault 是 Source；Markdown 文件是外部原始 Artifact；文件版本是可追溯来源版本；路径用于定位但不作为唯一永久身份。
- frontmatter、标签、双链、文件夹不自动成为 LifeOS Project、事实、Action、Decision 或授权范围。
- Project 不扩权；连接 Vault 不等于允许云同步或第三方模型处理。
- 一次性 Markdown 导出是用户明确触发的数据迁移动作，不建立持续同步关系。
- SP-02 / SP-03 可继承 P1-017 第 11 节的夹具、断言和验收案例。

## 不接受或需谨慎内容

- 不接受把 P1-017 解释为 Obsidian 正式进入 V1 实现承诺。
- 不接受把“只读”简化为“不写文件”而忽略索引、派生、云同步、第三方处理和保留副本的授权边界。
- 不接受把导出到 Vault 内目录描述为同步、发布、持续更新或自动写回。
- 不接受用文件夹、标签、双链自动创建或确认 Project、Action、Decision、事实或授权。
- 不接受在 SP-02 / SP-03 / SP-04 通过前处理真实敏感 Vault 或将 Vault 内容送入 AI/云/第三方链路。
- 不接受在 SP-02 失败后继续强行承诺 Obsidian 正式接入。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：更新 P1-017 验收结论和当前下一步。
- `lifeos/PM_OPERATING_MODEL.md`：无需更新。
- `lifeos/TASK_REGISTRY.md`：将 P1-017 更新为 Accepted。
- `lifeos/DECISION_LOG.md`：新增 D-0089。
- `lifeos/RISK_LOG.md`：新增 Obsidian 文件身份、只读越权、导出误解、外部结构误解释等风险。
- `lifeos/OPEN_QUESTIONS.md`：新增 Obsidian 断源保留、导出格式、平台可靠性、附件提取等开放问题。
- `lifeos/FREEZE_STATUS.md`：将 Obsidian 只读接入条件需求更新为 Accepted but Not Frozen。

## 下一步任务建议

建议下一步启动 `LIFEOS-P1-018 首批技术 Spike 任务卡：SP-01 / SP-02 / SP-03`。

理由：

- SP-01 是真实自用数据进入 LifeOS 前的保存底线。
- SP-02 是 Obsidian 只读接入能否成立的技术底线。
- SP-03 是来源、版本、Derivation 与证据链能否成立的信任底线。
- 三者共用 P1-016 / P1-017 的夹具与 E2E 断言，适合先形成统一任务卡，再分别执行技术验证。
