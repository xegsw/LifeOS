# LIFEOS-P3-026｜PM Review：生产 Schema / API 独立反例评审

## 验收信息

- 任务 ID：LIFEOS-P3-026
- 任务名称：生产 Schema / API 独立反例评审
- 专项交付物路径：`lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-026_pm_review.md`
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-026_LIFEOS-P3-026_production_schema_api_independent_review_local_precheck.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：WorkBuddy
- Agent 与任务匹配度：High
- 更新时间：2026-08-13

## PM 总结

1. P3-026 完成了 P3-025 生产 Schema / API 草案的独立反例评审，结论为 Pass with Conditions。
2. 评审未发现 P0 级设计漏洞；P3-025 的不可变 ArtifactVersion、ContentIdentity、完整 DerivationInput、追加式 Feedback、六维授权、统一消费门、双 generation / tombstone、FTS 回连权威、只读恢复评估等核心安全方向可接受。
3. 评审发现 7 项 P1 条件：授权 scope 解析算法、Feedback retract 级联规则、`lifeos_control` DTO 联合验证边界、`details_token` 生命周期、`semantic_object` 类型 schema、DerivationInput 列互斥 DB 约束、`origin_actor_ref` 按身份必填规则。
4. 评审发现 5 项 P2 清洁项，主要围绕 idempotency 命名空间、FTS 命中数量泄露、health_check 枚举、semantic_object_version 清理规则、capture 去重语义。
5. PM 接受 P3-026 的主结论，但收紧后续顺序：在 P1-1 至 P1-7 条件整改前，不得进入 SQL migration 编写、最小 Tauri 壳搭建或真实 IPC 验证。
6. P3-026 自身本地预检因本地模型连接重置跳过，不作为验收依据。交付物中引用的 P3-025 预检路径不作为 P3-026 预检依据，PM 已另行补跑 P3-026 预检并记录。
7. 本任务不冻结 Schema / API、不关闭 R-0040、不写 migration、不运行 Tauri、不启用真实能力、不进入下一阶段。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：P3-026 是关键 Schema / API 独立评审，涉及后续生产数据合同、Tauri IPC 合同与 R-0040 边界；不属于低风险 P1 / P2 工程补丁。

## 角色与关卡验收

- 主责角色覆盖情况：通过。数据 / 领域模型负责人、AI 信任与安全负责人视角均覆盖，尤其是身份、来源、授权、反馈、派生输入、tombstone 与恢复不复活。
- 协审角色覆盖情况：通过。技术架构、QA / Evidence、体验状态语义均有覆盖。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass with Conditions
  - Gate 3 AI 权限与信任评审：Pass with Conditions
  - Gate 4 技术可行性评审：Pass with Conditions
- 未通过或需后续确认关卡：
  - Schema / API 正式冻结：未通过。
  - SQL migration 编写准入：未通过，需先完成 P1 条件整改。
  - 最小 Tauri 壳搭建准入：未通过，需先完成 P1 条件整改并另立任务。
  - R-0040 关闭：未通过，仍需真实 Tauri / IPC 验证、独立复评和用户确认。
- 是否属于关键冻结事项：Yes，涉及未来 Schema / API 冻结前的独立评审输入。
- 是否需要独立评审：本任务自身即为独立评审。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-026_production_schema_api_independent_review.md`
- 独立评审结论：Pass with Conditions
- 是否允许进入下一任务或下一阶段：允许进入 P1 条件整改任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：Schema 表名、字段、约束、索引、错误码、API / IPC DTO、Tauri capability、导出 / 恢复格式、生产 SLA、R-0040、工程基线。
- 是否允许进入下一任务：Conditional。建议用户确认后启动 P3-027，处理 P3-026 发现的 P1 条件整改。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 问题：是否采纳 P3-026 的 Pass with Conditions 结论？
   - PM 建议：采纳。
   - 可选方向：A. 采纳并启动 P3-027 条件整改；B. 要求 P3-026 返工；C. 暂停 Schema/API 线。
   - 不确认的影响：不能进入下一步 Schema/API 条件整改，也不能进入 migration 或 Tauri 壳。
2. 问题：是否按 PM 建议先启动 P3-027，而不是直接进入 migration 或最小 Tauri 壳？
   - PM 建议：先启动 P3-027。
   - 可选方向：A. 启动 P3-027；B. 直接进入 migration（不建议）；C. 暂停。
   - 不确认的影响：P1 条件未澄清，后续工程实现容易把安全边界写歪。
3. 问题：`semantic_object` 聚合是否继续作为 V1 候选，并采用“专属字段超过 5 个或不变量冲突无法用 JSON schema 表达时必须拆表”的拆分条件？
   - PM 建议：采纳为 P3-027 条件之一。
   - 可选方向：A. 采纳拆分条件；B. 要求立即拆表；C. 让 P3-027 输出两个方案。
   - 不确认的影响：migration 设计时无法稳定处理 Assertion / Decision / Action / Event。
4. 问题：`lifeos_control` 是否拆分为 `lifeos_mutate` 与 `lifeos_destruct`？
   - PM 建议：让 P3-027 给出最终建议；当前倾向拆分以支持差异化 capability。
   - 可选方向：A. P3-027 评估并给出合同；B. 现在直接决定拆分；C. 保持三命令但强化 DTO 约束。
   - 不确认的影响：Tauri capability 配置与 P3-024 M-01 / M-04 仍不稳定。

## 整改建议

建议启动 `LIFEOS-P3-027｜Schema / API 条件整改包`，不写 migration、不改代码，只对 P3-025 草案补充 7 个 P1 条件：

1. 授权 scope 解析形式化算法。
2. Feedback retract 级联规则。
3. `lifeos_control` DTO 联合安全约束与是否拆分命令。
4. `details_token` 生命周期、可检索内容和脱敏规则。
5. `semantic_object` 各类型最小 JSON schema 与拆表触发条件。
6. DerivationInput 列互斥 DB 级约束表达。
7. `content_identity.origin_actor_ref` 按 `identity_kind` 的必填 / 可空规则。

P2 清洁项可纳入 P3-027 的“Should”部分，但不得拖大范围。

## 可接受内容

- P3-026 的 Pass with Conditions 结论。
- P3-026 对 P3-025 未发现 P0 的判断。
- 7 个 P1 条件作为 migration / 最小 Tauri 壳前的硬前置。
- P3-025 可作为后续整改输入，但暂不得作为冻结合同。
- `semantic_object` 聚合可继续作为候选，但必须设置拆分条件。
- R-0040 继续保持 Open / Conditional。

## 不接受或需谨慎内容

- 不接受直接进入 SQL migration 编写。
- 不接受直接进入最小 Tauri 壳搭建。
- 不接受将 P3-025 或 P3-026 视为 Schema / API 冻结。
- 不接受将 P3-026 视为 R-0040 关闭证据。
- 不接受“P1 条件后续再说”的工程推进方式；P1 条件必须在 migration 前澄清。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：将 P3-026 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将“生产 Schema / API 独立反例评审”更新为 Accepted / Pass with Conditions。
- `lifeos/DECISION_LOG.md`：新增 D-0186，记录 PM 接受 P3-026 并建议用户确认后启动 P3-027。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P3-026 并启动 P3-027。
- `lifeos/RISK_LOG.md`：暂不更新。P3-026 的 R-P3-026-01 至 R-P3-026-07 作为任务内条件风险处理；若 P3-027 后仍未关闭，再考虑登记入项目风险账本。

## Agent 分派与适配度评估

- 本任务推荐 Agent：WorkBuddy
- 本任务实际执行 Agent：WorkBuddy
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：反例覆盖清晰，能够把“无 P0”与“P1 条件不可跳过”区分开，没有越权宣布冻结或关闭 R-0040。
- 主要问题：交付物中的本地预检路径引用了 P3-025 预检而非 P3-026 自身预检；PM 已补跑并在本 Review 中修正。
- 以后更适合分派给该 Agent 的任务类型：独立评审、反例攻击、风险复核、关键合同冻结前检查。
- 不建议分派给该 Agent 的任务类型：直接工程实现或自己评审自己产出的整改。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：No。

## 下一步任务建议

建议用户确认后启动：

- LIFEOS-P3-027｜Schema / API 条件整改包

推荐 Agent：Codex 技术 / 数据设计会话。

推荐原因：P3-027 需要把 P3-026 的 7 个 P1 条件转成更精确的设计补丁、伪代码 / 约束表达和可供后续 migration 使用的合同文本；Codex 更适合结构化技术整改。但 P3-027 仍不写 migration、不改代码、不运行 Tauri、不冻结 Schema / API、不关闭 R-0040。

## 聊天回复边界

PM 主会话只输出验收结论、资产状态、是否允许下一步、修改文件和需要用户确认的问题，不复述完整 Review。
