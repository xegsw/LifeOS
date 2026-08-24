# LIFEOS-P3-025｜PM Review：生产 Schema / API 设计草案

## 验收信息

- 任务 ID：LIFEOS-P3-025
- 任务名称：生产 Schema / API 设计草案
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-025_production_schema_api_design.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-025_pm_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-025_LIFEOS-P3-025_production_schema_api_design_local_precheck.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

1. P3-025 完成了任务卡要求的生产候选 Schema / API 设计草案，覆盖 Project、Source、Artifact、ArtifactVersion、ContentIdentity、Authorization、Derivation、DerivationInput、Feedback、ImportantLink / LinkEvidence、Tombstone、OutboxJob、FTS / SearchIndex、Export / Restore package projection 等核心对象。
2. 交付物清楚区分了权威内容、控制账本、派生 / 索引和任务队列，没有把 FTS、导出包、恢复候选、summary、suggestion 或 evidence pointer 错写成权威来源。
3. Tauri IPC / 本地 API 命令草案覆盖 capture、read、search、suggestion candidate、feedback、retract feedback、important link、revoke authorization、delete、export candidate、restore candidates read-only、capability status 和 health check，并强调 Renderer 不可信、服务端重建上下文、默认拒绝。
4. 交付物明确声明不冻结 Schema / API、不写 SQL migration、不安装 / 配置 / 运行真实 Tauri、不启用真实能力、不关闭 R-0040、不进入下一阶段，未发现越权推进。
5. Gate 2 / Gate 3 / Gate 4 均可作为设计层 Pass with Conditions，但还缺少独立反例评审、migration / 约束验证、真实 IPC 旁路验证、SQLite 耐久 / 备份验证和 P3-024 M-01～M-26 实测。
6. 本地预检因本地模型连接重置被跳过，不作为验收依据；PM 已按任务卡、交付物、冻结状态和最近决策完成独立核对。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：P3-025 是生产候选 Schema / API 设计任务，涉及后续 Schema、API、Tauri IPC 合同和 R-0040 相关边界；不是低风险 P1 / P2 工程补丁。

## 角色与关卡验收

- 主责角色覆盖情况：通过。技术架构负责人 / 数据模型负责人视角均有覆盖，尤其是权威表、版本、generation、消费门、outbox、FTS 可重建投影、候选 API 命令和错误码。
- 协审角色覆盖情况：条件通过。AI 信任与安全、QA / Evidence、体验状态语义均有覆盖，但仍需独立评审验证反例。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass with Conditions
  - Gate 3 AI 权限与信任评审：Pass with Conditions
  - Gate 4 技术可行性评审：Pass with Conditions
- 未通过或需后续确认关卡：
  - Schema / API 正式冻结：未通过，需后续独立评审与实现验证。
  - R-0040 关闭：未通过，本任务不构成真实 Tauri / IPC 安全证据。
  - 下一阶段进入：未通过。
- 是否属于关键冻结事项：Yes，若未来要冻结 Schema / API 或启用真实 Tauri / IPC，必须按关键冻结 / 高风险能力启用流程处理。
- 是否需要独立评审：Yes
- 独立评审路径：待创建，建议 `lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- 独立评审结论：未开始
- 是否允许进入下一任务或下一阶段：允许进入独立评审任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No，Accepted but Not Frozen。
- 冻结范围：无。
- 未冻结内容：Schema 表名、字段、枚举、约束、索引、IPC 命令名、DTO、错误码、Tauri capability、导出格式、恢复协议、生产 SLA、工程基线。
- 是否允许进入下一任务：Conditional，建议用户确认后启动 P3-026 独立反例评审。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，将 P3-025 从 Ready 更新为 Accepted but Not Frozen。

## 需要用户确认的事项

1. 问题：是否采纳 P3-025 作为后续独立评审输入，并启动 P3-026？
   - PM 建议：采纳，并启动 P3-026 生产 Schema / API 独立反例评审。
   - 可选方向：A. 启动独立评审；B. 要求 P3-025 先返工补充；C. 暂停 Schema/API 线。
   - 不确认的影响：不能进入 migration 设计、最小 Tauri 壳或真实 IPC 验证任务。
2. 问题：是否暂时接受 `semantic_object` 聚合承载 Assertion / Decision / Action / Event 作为评审候选？
   - PM 建议：接受为评审候选，但在独立评审中重点攻击是否损害已冻结领域语义。
   - 可选方向：A. 保持聚合候选；B. 要求立即拆表；C. 让独立评审给出拆分条件。
   - 不确认的影响：后续 migration / API 合同无法稳定。

## 整改建议

当前不要求 P3-025 返工。以下内容应放入 P3-026 独立评审重点，而不是让执行 Agent 自审：

- 多 Project / 多 Source / 授权冲突下的消费门反例。
- `semantic_object` 聚合是否会稀释 Assertion / Decision / Action / Event 的领域语义。
- Tombstone、Feedback retract、Authorization revoke / expire、Source disconnect 的 generation 传播是否存在遗漏。
- `export_memory_package_candidate` 与 `evaluate_restore_candidates` 是否足够阻断旧包复活。
- IPC 三窄命令映射是否会滑向任意 dispatcher。
- 错误码是否存在泄露对象存在性或可被自动重试扩大权限的问题。

## 可接受内容

- 单机 SQLite 权威库 + FTS-first + 可重建派生的总体方向。
- 不可变 `ArtifactVersion`、独立 `ContentIdentity`、完整 `DerivationInput`、追加式 `Feedback`。
- 六维授权、统一消费门、双 generation / tombstone、幂等写、outbox lease fencing、FTS 回连权威。
- 恢复候选只读评估、导出候选不写真实文件、真实能力默认关闭。
- 与 P3-024 M-01～M-26 的映射可作为后续验证设计输入。

## 不接受或需谨慎内容

- 不接受将本文当成 Schema / API 冻结合同。
- 不接受基于本文直接写 SQL migration、创建 IPC handler 或运行真实 Tauri。
- 不接受将 `semantic_object` 聚合自动视为最终生产模型。
- 不接受将 P3-025 视为 R-0040 关闭证据。
- 不接受将候选 Export / Restore projection 视为真实导出 / 导入能力已授权。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：将 P3-025 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将“生产 Schema / API 设计草案”更新为 Accepted but Not Frozen。
- `lifeos/DECISION_LOG.md`：新增 D-0184，记录 PM 接受 P3-025 且建议启动 P3-026 独立评审。
- `lifeos/CURRENT_STATUS.md`：更新当前等待用户确认与下一步。
- `lifeos/RISK_LOG.md`：不更新，R-0040 保持 Open / Conditional。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：结构化能力强，能把领域规则、Schema、API、错误码、验证矩阵整合成可执行合同草案。
- 主要问题：设计深度较高，后续必须由独立评审防止执行者自证。
- 以后更适合分派给该 Agent 的任务类型：技术 / 数据合同草案、migration 设计、测试矩阵落地、工程实现。
- 不建议分派给该 Agent 的任务类型：独立反例评审自己刚完成的 Schema / API 草案。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No。

## 下一步任务建议

建议用户确认后启动：

- LIFEOS-P3-026｜生产 Schema / API 独立反例评审

建议推荐 Agent：WorkBuddy。原因：本任务需要从独立视角攻击 Schema/API 的越权、复活、来源混淆、反馈撤回、授权冲突、错误泄露和 IPC dispatcher 风险；不应由 P3-025 执行 Agent 自评。

## 聊天回复边界

PM 主会话只输出验收结论、资产状态、是否允许下一步、修改文件和需要用户确认的问题，不复述完整 Review。
