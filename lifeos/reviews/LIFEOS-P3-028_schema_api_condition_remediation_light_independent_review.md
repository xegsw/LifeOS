# LIFEOS-P3-028｜Schema / API 条件整改轻量独立复核

## 评审信息

- 对应任务 ID：LIFEOS-P3-027
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- 独立评审角色：AI 信任与安全负责人 / 数据模型负责人
- 协审视角：技术架构负责人、QA / Evidence Reviewer、体验设计负责人
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-028_schema_api_condition_remediation_light_independent_review.md`
- 评审结论：**Pass**
- 本地预检路径：`lifeos/local_prechecks/LIFEOS-P3-027_LIFEOS-P3-027_schema_api_condition_remediation_local_precheck.md`
- 本地预检状态：Skipped / Local Model Unavailable（502 Bad Gateway），符合允许跳过场景
- 更新时间：2026-08-13

## 评审摘要

1. **[事实]** P3-027 逐项关闭了 P3-026 提出的 7 个 P1 条件，每项均给出了可测试的算法、状态规则、DB/DTO 表达或约束文本。整改质量在设计层充分。
2. **[事实]** 未发现 P3-027 引入新的 P0 或 P1 风险。四 invoke 拆分（`lifeos_read` / `lifeos_export_candidate` / `lifeos_mutate` / `lifeos_destruct`）比保留三 invoke 更安全，符合最小权限原则。
3. **[事实]** 发现 3 项 P2 清洁项（retract-of-retract 语义未显式声明、feedback_dependency 跨 target 强制级别未指定、`strict_intersection` 术语需形式化定义），均不阻塞 migration 设计。
4. **[推断]** P3-024 M-01 / M-04 / M-20 需要从"三窄命令"更新为"四窄命令"并扩展 DTO 变体验证项；这是设计层补丁，不是 P0/P1 风险。
5. **[推断]** `semantic_object` 聚合可继续。Decision 和 Action 各有 5 个专属字段，已触及拆表触发器上限；后续 migration 设计时须复查字段数。
6. **[建议]** 允许在 PM 确认四 invoke 采纳后启动"SQL migration 设计 / 合同测试任务"（仅设计，不执行）。最小 Tauri 壳任务需在 migration 设计和 P3-024 矩阵补丁完成后方可启动。
7. **[声明]** 本评审不冻结 Schema / API、不写 migration、不运行 Tauri、不关闭 R-0040、不启用真实能力、不进入下一阶段。

## 已通过内容

1. **P1-1 授权 scope 形式化算法**：deny 任意层级全局阻断、多 allow 按 (grantor, processor, purpose, location, action) 分组后取严格交集、无"更具体 allow 胜出"——可接受。
2. **P1-2 Feedback retract 级联**：显式 dependency 表、状态折叠器自动计算、不伪造 retract 事件、correct 默认独立、complete/defer 基础失效后 Action 转 review_required——可接受。
3. **P1-3 IPC DTO 严格联合 + 四 invoke 拆分**：Rust 封闭 enum + `deny_unknown_fields`、TS discriminated union + strict schema、先校验顶层再反序列化、exhaustive match 缺 variant 构建失败——可接受。
4. **P1-4 `details_token` 生命周期**：默认省略、256-bit 随机不透明、TTL ≤5 分钟单次兑换、内存-only、安全摘要限定 6 个字段、永久禁止 13 类敏感信息——可接受。
5. **P1-5 `semantic_object` 类型 schema + 拆表门**：四类型 `additionalProperties:false`、major/minor 版本规则、未知 major fail closed、嵌套对象不得规避计数、强制拆表触发器——可接受。
6. **P1-6 DerivationInput DB 级约束**：恰一非空 CHECK + type/column 一致性 CHECK + 独立随机主键 + partial unique index——可接受。
7. **P1-7 ContentIdentity 条件约束**：按 `identity_kind` 明确 `origin_actor_ref` / `derivation_id` 可空性、`external:unknown` 不用 NULL 吞来源、AI 类禁止冒充外部作者——可接受。
8. **P2 清洁项**：5 项 Should 级口径（idempotency 命名空间、FTS 数量泄露、health detail 枚举、SemanticObjectVersion 清理、Capture 去重）均可作为 migration / API 合同测试输入。

## P1-1 至 P1-7 逐项复核

### P1-1：Authorization scope 解析

**P3-026 要求**：形式化解析算法，覆盖 deny 传播、多 allow 冲突定义、scope 优先关系。

**P3-027 整改**：§3 提供完整伪代码。权威闭包 R 排除候选 Project link 和 Renderer 声称归属；deny 任意 scope 命中 R 即全局阻断；deny 未命中后按 (grantor, processor, purpose, location, action) 分组 allow，groups.count != 1 → DENY_AMBIGUOUS；strict_intersection 不可判定 → DENY_AMBIGUOUS。对外统一 E_NOT_FOUND_OR_DENIED，E_AUTH_AMBIGUOUS 仅进受限诊断。

**反例验证**：
- 场景 A（project allow + source deny）：deny 全局阻断 → DENY ✓
- 场景 B（project deny + source allow）：deny 全局阻断 → DENY ✓（P3-026 标记的危险场景已关闭）
- 场景 C（不同 grantor 的 project allow + source allow）：groups.count = 2 → DENY_AMBIGUOUS ✓
- Renderer 伪造归属：R 排除 Renderer 声称 ✓
- tombstone/generation 先于 auth 检查：R 解析失败 → DENY，外部 E_NOT_FOUND_OR_DENIED 不泄露 ✓
- 跨 Project/processor 决定缓存不复用 ✓

**结论：P1-1 关闭。**

### P1-2：Feedback retract 级联

**P3-026 要求**：明确 retract confirm 是否级联失效依赖该 confirm 的 correct/complete/defer。

**P3-027 整改**：§4 引入 `feedback_dependency` 显式关系。retract 追加新 Feedback；状态折叠器递归使显式依赖效果变为 `inactive_due_to_basis_retracted`，不伪造 retract 事件。correct 默认独立（不依赖旧 confirm）；complete/defer 基础 confirm 被撤回后工作流效果失效、Action 转 review_required。已确认 Link 回退 unconfirmed/candidate。Derivation 确认撤回回退 available_unconfirmed。

**反例验证**：
- retract confirm → correct F2 独立保留 ✓
- retract confirm → complete F2 基础失效、Action 转 review_required ✓
- 重复 retract 幂等 ✓
- 环形 / 乱序 / 跨 target / 指向已失效 basis → fail closed ✓

**结论：P1-2 关闭。** P2-1：retract-of-retract 语义未显式声明（规则隐含允许且安全，但 migration 设计时应明确）。

### P1-3：IPC DTO / capability 拆分

**P3-026 要求**：discriminated union + exhaustive matching、action-parameter 绑定、考虑拆分 lifeos_control。

**P3-027 整改**：§5 建议四 invoke 拆分（详见下文专项复核），Rust 封闭 enum + `deny_unknown_fields`，TS discriminated union + strict schema。先校验 `contract_version` + `action`，再反序列化该 variant 参数。未知 action → E_UNKNOWN_COMMAND；缺字段/错类型/额外字段/跨 variant → E_INVALID_ARGUMENT。exhaustive match 缺 variant 构建失败。

**反例验证**：
- Renderer 发 `lifeos_mutate` 携带 `delete_artifact` action → E_UNKNOWN_COMMAND ✓
- Renderer 发 `lifeos_mutate` 参数混入 `lifeos_destruct` 字段 → E_INVALID_ARGUMENT ✓
- 未知 contract_version → E_UNKNOWN_COMMAND ✓
- 零业务副作用、零 outbox、零详细解析错误回传 ✓

**结论：P1-3 关闭。**

### P1-4：`details_token` 生命周期

**P3-026 要求**：可检索信息、可检索者、有效期、脱敏规则。

**P3-027 整改**：§6 完整约束。256-bit 随机不透明 token，绑定 app session + request_id + 调用主体 + 错误码。TTL ≤5 分钟、单次兑换。内存-only，不进 SQLite / AuditEntry / 日志 / 遥测 / 导出。可检索内容限定 `{public_code, operation_class, retryable, component_category, coarse_time_bucket, correlation_id}`。永久禁止路径 / SQL / 对象 ID / Project 名 / 正文 hash / 授权匹配数量 / DB 计数 / 密钥。

**反例验证**：
- 路径泄露？禁止 ✓
- SQL / 堆栈泄露？禁止 ✓
- 对象 ID 泄露？禁止 ✓
- 授权匹配数量泄露？禁止 ✓
- 跨会话重放？绑定 session，过期 / 重放 → 不可用 ✓
- 进程退出？内存-only，立即失效 ✓
- Renderer 被 XSS 后兑换 token？可检索内容均为安全摘要，不构成额外风险 ✓

**结论：P1-4 关闭。**

### P1-5：`semantic_object` 类型 schema 与拆表门

**P3-026 要求**：每个 object_type 的最小 JSON schema、类型间不变量差异强制、schema 版本演进规则。

**P3-027 整改**：§7 四类型 schema 均 `additionalProperties:false`。major = 破坏性变化，minor = 向后兼容且不得放宽身份/确认规则。未知 major → fail closed。版本迁移确定性转换、原子切换、失败保留旧版并标 migration_required。拆表触发器：持久化顶层专属字段 > 5（含 optional，不含公共 envelope，嵌套不得规避）或类型间不变量冲突无法由 JSON Schema + 公共列表达 → 必须拆表。

**当前字段计数**：
- Assertion：statement, valid_from, valid_until, qualification = 4
- Decision：decision_text, question, options_considered, rationale, validity_window = 5（**触及上限**）
- Action：action_text, due_at, defer_until, commitment_to, result_ref = 5（**触及上限**）
- Event：event_type, description, occurrence = 3

**结论：P1-5 关闭。** Decision 和 Action 已在拆表触发器边界，migration 设计时必须复查。

### P1-6：DerivationInput DB 级约束

**P3-026 要求**：显式 CHECK 约束或触发器表达"恰一非空"和 type-column 一致性。

**P3-027 整改**：§8 两条 CHECK 约束：恰一非空（布尔求和 = 1）和 type-column 一致性（input_type 匹配非空列）。独立随机 id 主键 + 四个 partial unique index `WHERE <fk> IS NOT NULL`。明确应用层校验不可替代 DB 约束。

**验证**：
- SQLite 支持布尔表达式算术 ✓
- SQLite ≥3.8.0 支持 partial index ✓
- 复合 nullable FK 主键问题已通过独立随机 id 规避 ✓
- 直接 DB 写入（migration / 调试工具）无法绕过 CHECK ✓

**结论：P1-6 关闭。**

### P1-7：ContentIdentity 条件约束

**P3-026 要求**：`origin_actor_ref` 按 `identity_kind` 区分必填 / 可空。

**P3-027 整改**：§9 明确四组约束：
- user_original / user_edited：actor 可空，derivation 必须空
- external_original / external_reference：actor 必填，derivation 必须空；未知作者用 `external:unknown` 不用 NULL
- quoted_excerpt：actor 必填，derivation 可空
- ai_generated / ai_inference / ai_suggestion：actor 必须空，derivation 必填

**验证**：
- AI 文本冒充外部作者？actor 必须空 + derivation 必填 ✓
- 外部来源丢失 actor？必填 + `external:unknown` 兜底 ✓
- 用户原文被 AI 改写身份？derivation 必须空 ✓
- AI 输出经用户确认后仍保留 AI 身份？上位规则不变 ✓

**结论：P1-7 关闭。**

## 四 invoke 拆分专项复核

| invoke | 允许 action | capability 性质 | 安全评估 |
|---|---|---|---|
| `lifeos_read` | read/search/capability_status/health_check | 只读、最小诊断 | 无风险 |
| `lifeos_export_candidate` | export candidate/evaluate restore candidates | 只生成内存候选、禁止路径写入 | 无风险 |
| `lifeos_mutate` | capture/create suggestion/record or retract feedback/create link | 权威创建或追加，不含删除/断源/撤权 | 最小权限，创建流程不获得 destruct 能力 |
| `lifeos_destruct` | revoke authorization/disconnect source/delete artifact | 高影响控制；独立 capability + preview token + expected generation + 幂等键 | 独立隔离，可独立撤销 |

**四 invoke 优于三 invoke 的理由**：
1. 最小权限：创建类页面不获得 destruct capability。
2. 审计清晰：destruct 操作独立 capability，可独立审计和撤销。
3. 可测试性：P3-024 M-01/M-04 可精确测试每个 invoke 的 capability 边界。
4. 降级安全：若 destruct capability 被撤销，创建流程不受影响。

**反例验证**：
- 仅持 `lifeos_mutate` 的 Renderer 调 `lifeos_destruct`？capability 不匹配 → 拒绝 ✓
- `lifeos_mutate` 中发送 `delete_artifact` action？E_UNKNOWN_COMMAND ✓
- 跨 variant 字段注入？E_INVALID_ARGUMENT ✓
- exhaustive match 缺 variant？构建失败 ✓

**结论：四 invoke 拆分应作为后续候选输入。**

## P3-024 验证矩阵影响

| 矩阵项 | 当前表述 | 需更新为 | 影响 |
|---|---|---|---|
| M-01 | capability 声明只含三窄命令 | 四窄命令 (read/export_candidate/mutate/destruct) | P0 测试项需更新；须验证非全页面获得全部四 invoke |
| M-04 | 只注册三窄命令 handler | 四窄命令 handler | P0 测试项需更新 |
| M-20 | IPC 参数端到端校验 | 四 DTO variant 各自正测 + 跨 variant 反例 + destruct 额外必填字段（preview token/expected generation/idempotency key） | P0 测试项需扩展 |

**判断**：M-01 / M-04 / M-20 需设计层补丁，从"三窄命令"更新为"四窄命令"。这是验证矩阵的设计更新，不是安全风险。补丁应在最小 Tauri 壳搭建前完成。

## `semantic_object` 聚合与拆表门复核

- 四类型 schema 均 `additionalProperties:false`，公共 envelope 固定，类型专属字段不充当权威 ✓
- 拆表触发器可执行：字段计数明确（Decision 和 Action 已触及 5 上限），不变量冲突条件可判定 ✓
- 嵌套 JSON 规避漏洞已堵：嵌套对象不得规避计数 ✓
- 版本迁移规则完整：确定性转换、原子切换、失败保留旧版 ✓
- **判断**：聚合可继续，拆表触发器足够硬。migration 设计时须复查 Decision / Action 字段数。

## 新发现问题

### P0

无。

### P1

无。P3-026 的 7 个 P1 条件全部关闭。

### P2

| # | 发现 | 位置 | 建议 |
|---|---|---|---|
| P2-1 | retract-of-retract 语义未显式声明。规则隐含允许（retract 指向当前有效的 retract Feedback 会恢复原 Feedback 效果），且行为安全，但未在文档中明确。 | P3-027 §4 | migration 设计时明确 retract-of-retract 是否允许及其状态效果。 |
| P2-2 | `feedback_dependency` 跨 target 依赖的强制级别未指定。规则声明"跨 target 依赖 → fail closed"，但未说明是 DB CHECK 还是应用层校验。 | P3-027 §4 | migration 设计时指定 DB 级或触发器级强制。 |
| P2-3 | 授权算法中 `strict_intersection` 术语未形式化定义。复杂 policy envelope 交集为空时的行为可从上下文推断为 DENY_AMBIGUOUS，但术语本身需要精确定义。 | P3-027 §3 | migration 设计时补充 strict_intersection 的形式化定义。 |

## 关卡检查

### Gate 2：数据与来源评审 — Pass

- 用户原文 / AI 生成 / AI 推断建议 / 外部引用 / 用户确认事实的区分清晰：ContentIdentity 八类 + DB CHECK 约束 + `origin_actor_ref` 按身份必填 ✓
- 授权、撤回、删除、来源身份、诊断脱敏均 fail closed ✓
- `semantic_object` 聚合不破坏核心领域语义，拆表触发器可执行 ✓
- DerivationInput DB 级约束防止直接 DB 写入绕过 ✓

### Gate 3：AI 权限与信任评审 — Pass

- deny 不可被更具体 allow 覆盖，任意层级全局阻断 ✓
- 四 invoke 拆分降低权限风险，destruct capability 独立隔离 ✓
- `details_token` 不泄露路径 / SQL / 对象 ID / 授权匹配数量 ✓
- Feedback retract 效果可解释，不伪造事件，不逆转现实行为 ✓
- AI / 外部 / 用户身份不混用 ✓

### Gate 4：技术可行性评审 — Pass

- SQLite CHECK / partial unique index 可实现 ✓
- Rust 封闭 enum + TS discriminated union 可生成双端合同 ✓
- P3-024 M-01 / M-04 / M-20 补丁为设计层更新，不影响技术可行性 ✓
- 每项 P1 整改均可转成正反例测试 ✓
- 尚无 migration、Rust / TS DTO 或真实 IPC 证据——后续任务范围 ✓

## 风险

| 风险 ID | 描述 | 级别 | 状态 |
|---|---|---|---|
| R-P3-028-01 | Decision / Action 专属字段已触及 5 上限，migration 设计时可能新增字段触发拆表 | P2 | Open，migration 设计时复查 |
| R-P3-028-02 | P3-024 M-01/M-04/M-20 矩阵补丁未完成即启动 Tauri 壳 | P2 | Open，需 PM 在 Tauri 壳任务前确认补丁 |
| R-0040 | Tauri / IPC 安全风险 | 既有 | 保持 Open / Conditional |

## 需要 PM 决策

1. **[需 PM 确认]** 是否认定 P3-026 的 7 个 P1 条件已在设计层完整关闭，允许 P3-025 + P3-027 继续作为 migration 设计输入？
2. **[需 PM 确认]** 是否正式采纳四 invoke 拆分（`lifeos_read` / `lifeos_export_candidate` / `lifeos_mutate` / `lifeos_destruct`）作为候选 invoke 面？
3. **[需 PM 确认]** 是否允许启动"SQL migration 设计 / 合同测试任务"（仅设计，不执行 migration）？
4. **[需 PM 确认]** 最小 Tauri 壳任务的启动条件是否为：(a) PM 采纳四 invoke；(b) P3-024 M-01/M-04/M-20 补丁完成；(c) migration 设计任务完成或至少 DTO 合同冻结？
5. **[需 PM 确认]** P2-1 至 P2-3 是否纳入 migration 设计任务的检查清单？

## 最终建议

1. **评审结论：Pass。** P3-027 在设计层完整关闭了 P3-026 的 7 个 P1 条件，未引入新的 P0 或 P1 风险。四 invoke 拆分比三 invoke 更安全、更清晰、更可验证。
2. **允许启动"SQL migration 设计 / 合同测试任务"**，前提是 PM 确认四 invoke 采纳。migration 设计时须复查 P2-1 至 P2-3 和 Decision / Action 字段数。
3. **最小 Tauri 壳任务需在以下条件满足后启动**：(a) PM 采纳四 invoke；(b) P3-024 M-01/M-04/M-20 补丁完成；(c) migration 设计完成或 DTO 合同冻结。
4. **P3-027 不改变核心领域模型、AI 权限边界或技术架构 V0.1 冻结合同。** 四 invoke 是 P3-025 候选映射的独立评审结果，P3-025 明确声明"最终映射需独立评审"。
5. **P3-027 不作为 R-0040 关闭输入。** R-0040 关闭仍需真实 Tauri / IPC 验证 + 进程杀死耐久 + 独立复评 + 用户确认。
6. **P3-027 不作为 Schema / API 冻结合同。** 冻结前须完成 migration / 约束验证、真实 IPC 旁路验证和 P3-024 M-01～M-26 实测。
7. **声明**：本评审为只读轻量独立复核，未修改 P3-027 / P3-025 主交付物、工程代码、Stitch、项目账本或冻结资产；未写 SQL migration、未创建 IPC handler、未安装 / 配置 / 运行真实 Tauri；未关闭 R-0040、未冻结 Schema / API、未进入下一阶段。
