# LIFEOS-P3-027｜PM Review｜Schema / API 条件整改包

## 1. 验收结论

- 任务 ID：LIFEOS-P3-027
- 任务名称：Schema / API 条件整改包
- 交付物：`lifeos/deliverables/LIFEOS-P3-027_schema_api_condition_remediation.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-027_LIFEOS-P3-027_schema_api_condition_remediation_local_precheck.md`
- PM 验收结论：Accepted
- 资产状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一阶段：No
- 是否冻结 Schema / API：No
- 是否关闭 R-0040：No
- 是否允许写 SQL migration：No
- 是否允许安装、配置或运行真实 Tauri：No
- 是否触发用户确认：Yes

## 2. 本地预检说明

本地预检已按项目规则调用，但局域网本地模型连接重置，状态为 `Skipped / Local Model Unavailable`，错误为 `[Errno 54] Connection reset by peer`。该结果不作为 PM 验收依据。PM 已按原流程核对任务卡、交付物、当前状态和最近决策完成验收。

## 3. 覆盖检查

P3-027 对 P3-026 提出的 7 个 P1 条件均给出了设计层整改口径：

| 条件 | PM 判断 |
|---|---|
| P1-1 Authorization scope 解析 | 通过。明确 deny 全层级阻断、多 allow 规范化合并、无“更具体 allow 覆盖 deny”，且提供可测试伪代码。 |
| P1-2 Feedback retract 级联 | 通过。明确追加式 retract、显式 dependency、自动失效效果、无隐式 retract 事件，并区分现实结果证据与当前工作流效果。 |
| P1-3 IPC DTO / `lifeos_control` | 条件通过。严格联合 DTO 设计成立；但建议拆为 `lifeos_mutate` / `lifeos_destruct` 会改变候选 invoke / capability 面，需轻量独立复核。 |
| P1-4 `details_token` | 通过。默认不发、短时单次、会话 / 请求 / 主体 / 错误码绑定、只返回安全摘要，泄露面控制清楚。 |
| P1-5 `semantic_object` | 通过。四类 schema 与强制拆表触发器清楚；未改变核心领域模型，仅保留 V1 聚合实现候选。 |
| P1-6 DerivationInput | 通过。给出 DB 级恰一非空和 type / column 一致性 CHECK 口径，并明确应用层校验不可替代 DB 约束。 |
| P1-7 ContentIdentity | 通过。按身份类型明确 `origin_actor_ref` / `derivation_id` 可空性，保护用户原文、AI 输出和外部来源身份不混用。 |

5 个 P2 清洁项也给出了 Should 级处理口径，可作为后续 migration / API 合同测试输入，但不构成已实现、已冻结或已验证。

## 4. PM 判断

P3-027 完成了 P3-026 要求的“设计层条件整改”：它把原评审中的风险点转成了可被 migration、DTO、IPC handler 和合同测试引用的约束文本。交付物没有修改 P3-025 主文档，没有写 migration，没有改代码，没有运行 Tauri，也没有把候选规则写成已冻结资产。

需要注意的是，P3-027 不只是“补字段说明”，它提出了一个更安全但更明确的候选方向：将原候选 `lifeos_control` 拆为 `lifeos_mutate` 与 `lifeos_destruct`。这个建议符合最小权限原则，也更利于把普通创建 / 追加与撤权 / 断源 / 删除隔离；但它会影响 P3-024 的 M-01 / M-04 capability 验证矩阵和后续真实 Tauri shell / handler 任务。因此 PM 不应直接把它作为冻结决定或立即进入 Tauri 实现。

PM 接受 `semantic_object` 继续作为 V1 候选聚合表，并采用“任一类型持久化顶层专属字段超过 5 个，或类型间不变量无法由 JSON Schema + 公共列无歧义表达时，必须拆表”的触发规则。该判断不改变已经冻结的核心领域模型，只是后续 Schema 设计的实现约束。

## 5. 角色检查点

- 技术架构负责人 / 数据模型负责人：Pass with Conditions。P1-1 至 P1-7 均可转入后续设计输入；四 invoke 拆分需独立复核。
- AI 信任与安全负责人：Pass with Conditions。授权、撤回、来源身份、诊断脱敏规则符合 LifeOS 信任边界；真实 Tauri / IPC 仍未验证。
- QA / Evidence Reviewer：Pass with Conditions。交付物已把条件转成可测试规则；但尚无 SQL migration、Rust / TypeScript DTO、真实 IPC 或 evidence 测试。
- 体验设计负责人：Pass。撤回、review_required、unconfirmed、诊断摘要等状态可支撑后续 UI 文案与状态设计，但本任务不冻结 UI。

## 6. 阶段与关卡

- Gate 2 数据与来源评审：Pass with Conditions
- Gate 3 AI 权限与信任评审：Pass with Conditions
- Gate 4 技术可行性评审：Pass with Conditions

这些结论只表示 P3-027 设计补丁可作为下一步输入，不表示 Schema / API 冻结、真实 Tauri / IPC 安全通过、R-0040 关闭或进入下一阶段。

## 7. 状态与后续动作

P3-027 可验收为 Accepted。PM 建议用户采纳后，下一步不要直接写 SQL migration，也不要直接启动真实 Tauri；应先启动 `LIFEOS-P3-028` 轻量独立复核，重点复核：

1. P1-1 至 P1-7 是否确实被 P3-027 完整关闭。
2. 四 invoke 拆分是否优于保留三 invoke。
3. `lifeos_mutate` / `lifeos_destruct` 是否需要同步修改 P3-024 M-01 / M-04 / M-20 验证矩阵。
4. `semantic_object` 聚合与拆表触发器是否足以支撑下一步 migration 设计。

在用户确认采纳 P3-027 前，PM 不启动 P3-028。即便用户采纳，P3-028 仍只应为只读轻量独立复核，不得写 migration、不得改代码、不得运行真实 Tauri、不得冻结 Schema / API、不得关闭 R-0040。

## 8. 是否需要用户确认

需要。

请用户确认：

- 是否采纳 P3-027 的 PM 验收结论。
- 是否同意把四 invoke 拆分作为候选方案进入轻量独立复核。
- 是否同意下一步启动 P3-028：Schema / API 条件整改轻量独立复核。

