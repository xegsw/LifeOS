# LIFEOS-P0-003 PM Review

## 验收信息

- 任务 ID：LIFEOS-P0-003
- 任务名称：核心领域模型前置研究
- 专项交付物路径：`/Users/xxe/Documents/No.2/lifeos/deliverables/LIFEOS-P0-003_core_domain_model_research.md`
- PM Review 路径：`/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P0-003_pm_review.md`
- 验收状态：Accepted
- 更新时间：2026-08-08

## PM 总结

- 003 任务交付质量达标，可以作为 Stage 0 后续 AI 权限模型、技术 Spike、首页/今日页 PRD 的关键输入。
- 文档没有越界到数据库表、API 或技术选型，而是以对象身份、生命周期、来源、派生、反馈和权限边界定义领域语义，符合任务要求。
- 推荐的 `Project`、`Artifact`、`Source`、`Assertion`、`Decision`、`Action`、`Event`、`Derivation`、`Feedback`、`Authorization`、`AuditEntry` + `Link` 模型比较完整，能支撑 V1 第一场景。
- `Source` 与 `Artifact` 分离、`Decision` 独立、`Feedback` 独立、`Derivation` 记录输入版本和权限上下文，这些判断非常关键，应进入后续系统设计。
- Obsidian Vault 只读接入模型表达清楚：Vault 作为 Source，Markdown 文件作为外部原始 Artifact，AI 派生不写回原文。
- 最大风险是模型语义被后续会话误读为“必须实现 11 张表/11 个 UI 模块”，需要在后续任务中继续强调这是领域语义边界，不是实现冻结。

## 需要用户确认的事项

### Q1：是否接受 11 个对象 + Link 作为 V0.1 领域语义边界？

问题：003 建议使用 `Project`、`Artifact`、`Source`、`Assertion`、`Decision`、`Action`、`Event`、`Derivation`、`Feedback`、`Authorization`、`AuditEntry` + `Link`。

PM 建议：接受，但明确这不是数据库表冻结，也不是 UI 模块清单。

可选方向：

- A：接受为 V0.1 领域语义模型。
- B：压缩模型，暂不独立 `Assertion` 或 `AuditEntry`。
- C：要求 003 返工成更小模型。

不确认的影响：P0-004、技术 Spike 和 V1 PRD 会缺少统一数据语义。

### Q2：是否确认 `Project` 是 V1 核心上下文边界？

问题：V1 第一场景需要一个恢复上下文的边界。

PM 建议：确认。但 `Project` 不是系统最高根对象，也不是企业项目容器。

可选方向：

- A：确认 `Project` 为 V1 核心上下文边界。
- B：用 `Topic` 或标签代替 Project。
- C：用 `Area` 作为最高上下文边界。

不确认的影响：“从哪里继续”的恢复包很难稳定组织。

### Q3：是否确认 `Source` 与 `Artifact` 分离？

问题：`Source` 回答“从哪里来、以什么权限取得”，`Artifact` 回答“保存/指向的具体内容是什么”。

PM 建议：确认分离。尤其为了 Obsidian Vault、网页链接、文件快照和来源失联场景。

可选方向：

- A：确认分离。
- B：V1 合并，后续再拆。

不确认的影响：来源权限、来源不可达、多版本、多快照和导出语义会变弱。

### Q4：是否确认 `Assertion` 独立为核心语义？

问题：`Assertion` 用于表达用户确认事实、外部主张、AI 推断等可判断陈述。

PM 建议：接受，但 V1 只为影响恢复、决定和行动的关键陈述创建，不做通用知识本体。

可选方向：

- A：接受 `Assertion` 为独立核心语义。
- B：把 Assertion 暂时放在 Derivation 输出里。
- C：放到后续版本再考虑。

不确认的影响：用户确认事实、冲突、有效期和多证据关系会难以表达。

### Q5：是否确认 `Decision` 独立？

问题：Decision 负责保存“为什么这样做”和“用户最终选择了什么”。

PM 建议：确认。它是 LifeOS 区别于普通笔记和任务列表的关键对象。

可选方向：

- A：确认 `Decision` 独立。
- B：把 Decision 作为 Artifact 标签。
- C：把 Decision 作为 Action 属性。

不确认的影响：项目恢复只能看到任务和摘要，看不到理由、修订和替代关系。

### Q6：是否确认 `Action / Commitment / Next Step` 的划界？

问题：003 建议 `Action` 独立，`Commitment` 是行动类型/约束，`Next Step` 是某时点的角色或选择结果。

PM 建议：确认。这样足够表达承诺和下一步，又不制造三套行动对象。

可选方向：

- A：确认该划界。
- B：拆成三个独立对象。
- C：全部合并成简单任务状态。

不确认的影响：要么 V1 太重，要么无法区分 AI 候选、用户承诺和当前下一步。

### Q7：是否确认重要 `Link` 需要来源、确认状态和有效期？

问题：AI 候选关联、来源支持、决定依据、行动动机等关系不能只是普通边。

PM 建议：确认“重要关系”需要身份与状态；普通展示关系可简化。

可选方向：

- A：确认重要 Link 具备来源/确认/有效期。
- B：所有关系都轻量化。
- C：所有关系都重型化。

不确认的影响：AI 错误关联很难被纠正或失效，或者实现成本被过度拉高。

### Q8：权限撤回后派生物与审计如何处理？

问题：003 提出应停止处理、使派生/缓存失效；历史审计保留规则交 P0-004/安全任务。

PM 建议：接受该方向，并要求 P0-004 细化。

可选方向：

- A：接受，交 P0-004 定义细则。
- B：要求 003 返工补完整规则。

不确认的影响：AI 权限模型无法处理撤回、删除、派生物和历史审计的边界。

### Q9：是否新增 P1 风险“核心领域语义过度实体化导致 V1 实现和交互负担超出价值”？

问题：003 的模型完整，但后续可能被误读成实现规模。

PM 建议：确认登记为 P1 Open。

可选方向：

- A：确认登记。
- B：暂不登记。

不确认的影响：后续技术/产品会话可能把语义模型等同于数据库和界面模块，导致 V1 变重。

## 整改建议

本任务不要求返工。建议把以下事项转入后续任务：

- `LIFEOS-P0-004` 必须基于 `Authorization`、`Derivation`、`Feedback`、`AuditEntry` 细化 AI 权限、确认、纠正、撤回和派生失效策略。
- 技术 Spike 必须验证 Source/Artifact 分离、版本、Obsidian 文件变动、权限撤回、派生失效与导出的成本。
- V1 PRD 必须围绕“Project 恢复包 + 候选下一步 + 来源证据 + Feedback”定义首页/今日页验收。
- 后续文档必须反复声明：11 个对象是领域语义模型，不是数据库表结构或 UI 模块清单。

## 可接受内容

- 11 个对象 + Link 可作为 V0.1 领域模型候选。
- `Project` 是 V1 第一场景的核心上下文边界。
- `Source` 与 `Artifact` 分离是必要设计。
- `Decision` 独立是必要设计。
- `Action` 统一 Task/Commitment/Next Step 的基础语义，较适合 V1 控制复杂度。
- `Derivation` 与 `Feedback` 是 AI 可信、可纠正和可重建的关键支撑。
- Obsidian 只读接入模型可以进入后续技术 Spike 输入。

## 不接受或需谨慎内容

- 不能把 11 个对象直接理解为 11 张数据库表。
- 不能把 11 个对象直接理解为 11 个用户可见模块。
- 不能在 V1 对所有文本都强制创建 Assertion。
- 不能把 Project 做成企业项目管理容器。
- 不能把 GitHub、IDE、Issue、部署或运维系统做成顶层核心对象。
- 不能因为需要审计就建设重型企业合规平台。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：建议将 `LIFEOS-P0-003` 更新为 Accepted。
- `lifeos/DECISION_LOG.md`：待用户确认 Q1-Q8 后，写入领域模型边界、核心对象、关键划界和权限撤回方向。
- `lifeos/RISK_LOG.md`：待用户确认 Q9 后，加入过度实体化风险。
- `lifeos/PROJECT_CONTEXT.md`：待用户确认后，吸收 V0.1 核心领域模型摘要。
- `lifeos/OPEN_QUESTIONS.md`：待用户确认后，更新核心领域模型相关开放问题。

## 下一步任务建议

- 若用户确认 Q1-Q9：更新项目文件，并产出 `LIFEOS-P0-004 AI 权限与信任模型` 正式任务卡。
- `LIFEOS-P0-004` 完成后，再启动 `LIFEOS-P0-005 技术可行性 Spike 计划`。
- 暂不启动 V1 PRD，因为 AI 权限与信任模型还没有完成。
