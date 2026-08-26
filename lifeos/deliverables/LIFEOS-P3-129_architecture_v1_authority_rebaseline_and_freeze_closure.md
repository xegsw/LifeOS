# LIFEOS-P3-129｜架构 V1.0 权威重基线与冻结收口（执行侧候选交付）

## 任务信息

- 任务 ID：`LIFEOS-P3-129`
- 任务名称：架构 V1.0 权威重基线与冻结收口
- 执行 Agent：Codex
- 当前状态：`Partial — execution-side candidate complete / mandatory independent review pending / Not Frozen`
- 需要 PM 决策：Yes
- 任务类型：技术架构 Gate 冻结候选
- 风险等级：Gate / P0
- Task Contract：`lifeos/tasks/LIFEOS-P3-129_architecture_v1_authority_rebaseline_and_freeze_closure.md`
- Frozen ABF：`ABF-P3-129-v1`，SHA-256 `df3c4e9879a624e05ef8f7eb5b71d1a5835422db0eea278e2fc88404032b40fb`
- 启动前合同歧义：No。V1.0 的现有正文、冻结范围与 promotion 权限均足以形成候选；未发现需要改写 V1.0 正文的实质冲突。
- 交付物篇幅：Slightly Over；Gate 任务需保留可核对的边界、状态与 Evidence 指针。

## 执行摘要

1. **[事实]** 已复算 ABF 与 V1.0 canonical：ABF SHA-256 为 `df3c…40fb`，canonical `lifeos/architecture/LifeOS架构基线V1.0.md` 为 `2db0…9a32`，均与 Frozen ABF 一致。canonical 第 3 行仍为 `Architecture Baseline Draft`，未执行 promotion。
2. **[事实]** 创建候选包 `lifeos/architecture/LIFEOS-P3-129/`：15 项固定输入、16 行 V0.1→V1.0 reconciliation、13 行兼容矩阵、冻结正负清单、P3-126/P3-127/P3-128 transition、唯一 promotion patch、pristine verifier、4 类 mutation、历史保全和非自指 Manifest 均可复核。
3. **[结论]** V0.1 的 16 项可操作技术规范已全部分类：`retained=13`、`changed=1`、`superseded=1`、`deferred=1`，无未分类规范。唯一 `changed` 是 V1.0 明确了目标层次、TypeScript Core、Tauri 2/React 方向和 Port 家族；这不冻结具体实现。
4. **[结论]** 未发现 V1.0 与产品宪法、11 核心对象+Link、AI 信任模型或 P3-126/P3-128 事实的语义冲突。Gate 1-4 为候选侧 PASS；Gate 5 对静态架构冻结为 `N/A`，不是 Pass。
5. **[事实]** `verifier.py verify` pristine PASS；4/4 mutation 均 fail-closed：canonical hash 替换、V0.1 行遗漏、Schema 冻结越界、非授权正文变化均被拒绝。
6. **[事实]** 15 项固定输入 before/after SHA-256 全部一致；未使用临时目录，未运行 Runtime/Tauri/IPC/DB/浏览器/模型/网络，也未修改 canonical、历史资产、PM 账本或风险。
7. **[限制]** ABF-M-013（全新隔离独立评审）和 ABF-M-014（Gate 最终收口）尚未执行，故本交付物不是 Gate Pass，也不请求或宣称 Frozen。

## 候选结论与边界

### V0.1 → V1.0 处理

完整逐行内容见 [v0_to_v1_reconciliation.json](../architecture/LIFEOS-P3-129/v0_to_v1_reconciliation.json)。前向 authority 的精确口径是：只有最终 Gate promotion 后，V1.0 才 supersede V0.1 的**后续技术架构规范效力**；V0.1 的历史事实、Review、Evidence 和仍适用的安全不变量继续保全。

- 保留：local-first、SQLite/FTS-first、可重建派生、权威/派生/outbox 责任分离、消费前重检/失败关闭、撤回删除活跃阻断、Obsidian 条件适配器、Tauri 默认拒绝安全合同、可迁移导出/恢复责任、供应商可替换、R-0040 的条件与复测触发器、所有不冻结实现细节与 Stage 禁止外推。
- 有界改变：V1.0 把目标 Modular Monolith + Hexagonal、Application/Orchestrator/Ports/Adapters、TypeScript Core、Tauri 2 + React 方向写成架构方向；它没有把这些变成 API/Schema/能力配置冻结。
- 后置：具体云/同步/队列/向量/工作流产品仅为候选 Adapter，不进入本次冻结。
- 取代：只取代 V0.1 的前向技术架构 authority；不删改 V0.1 历史。

### 兼容与冻结范围

完整语义和反例见 [cross_baseline_compatibility.json](../architecture/LIFEOS-P3-129/cross_baseline_compatibility.json) 与 [freeze_scope.json](../architecture/LIFEOS-P3-129/freeze_scope.json)。候选固定的是责任边界和架构方向：本地优先、模块化单体、Ports/Adapters、Domain 与 Infrastructure 分离、Model/Agent 分离、SQLite/FTS-first、派生可重建、重要消费/执行路径授权和 V0.1 保留安全不变量。

明确仍不冻结：Schema、Domain→Table 映射、IPC 签名、Tauri capability、FTS 表/PRAGMA/worker、Adapter 函数签名、特定模型/Agent 供应商、向量/Redis/Temporal/PostgreSQL/云同步方案、生产 SLA、P3-126 Runtime、产品 IA、风险、工程基线、真实能力和 Stage 4。

### Runtime 与工程继承

[runtime_transition.json](../architecture/LIFEOS-P3-129/runtime_transition.json) 将 P3-126/P3-127 作为只读的合成离线 Runtime/Evidence 事实 `preserve`，将 P3-128 后续 Fast Track 作为需新合同的 `adapt`，并将真实能力/Schema/API/云同步/Stage 4 标记 `defer`。P3-128 的工程 handoff 在本 Gate 完成前保持暂停。

## Evidence 与复跑

候选包路径：[LIFEOS-P3-129](../architecture/LIFEOS-P3-129/)

```bash
python3 -B lifeos/architecture/LIFEOS-P3-129/verifier.py verify
python3 -B lifeos/architecture/LIFEOS-P3-129/verifier.py mutations
```

本轮实测：

| 项目 | 结果 | Evidence |
| --- | --- | --- |
| Pristine verifier | PASS / `error_count=0` | [verification.json](../architecture/LIFEOS-P3-129/verification.json) |
| 4 类 mutation | 4/4 REJECT | [mutation_results.json](../architecture/LIFEOS-P3-129/mutation_results.json) |
| 固定输入／历史保全 | 15/15 MATCH | [history_verification.json](../architecture/LIFEOS-P3-129/history_verification.json) |
| 非自指候选 Manifest | PASS；11 项候选文件，Manifest 自身排除 | [FINAL_MANIFEST.json](../architecture/LIFEOS-P3-129/FINAL_MANIFEST.json) |
| promotion patch | 未执行；仅允许 canonical 第 3 行状态／supersession 元数据替换 | [canonical_promotion_patch.json](../architecture/LIFEOS-P3-129/canonical_promotion_patch.json) |

候选侧 ABF-M-001～M-012 均 PASS；ABF-M-013 为 `PENDING_MANDATORY_INDEPENDENT_REVIEW`，ABF-M-014 为 `PENDING_GATE_CLOSURE`。候选侧已发现计数为 `P0/P1/P2/Unknown/Not Implemented = 0/0/0/0/0`；该计数不替代独立评审或最终 Gate 公式。

## 角色与关卡

- 主责角色：技术架构负责人。
- 协审视角：产品架构、数据/领域模型、AI 信任与安全、PM。
- Gate 1：候选侧 PASS；未偏离个人外脑、5 分钟上下文恢复和用户控制。
- Gate 2：候选侧 PASS；核心 11 对象+Link、Source/Artifact、Derivation/Feedback/Authorization 及非 Schema 冻结得到保留。
- Gate 3：候选侧 PASS；Model/Agent 分离、任务授权、证据与确认边界未放宽。
- Gate 4：候选侧 PASS；不提前冻结重型实现，R-0040 和真实能力重测要求保留。
- Gate 5：N/A；本任务无用户价值验证，绝不把架构文档当作价值证据。
- 强制独立评审：已触发且未完成。理由是技术架构正式冻结替换；评审必须由另一个全新隔离会话只读进行，并自建 runner/Manifest，不得调用本包 verifier。

## 会话与上下文

- 执行方式：New Session。
- 授权证据：用户投递 P3-129 最终任务卡绝对路径；该授权覆盖候选包、Evidence、同范围修正、独立评审和 PM 验收，但不覆盖最终 promotion。
- 上一任务：N/A；未错误继承旧任务授权。
- 已完整读取：`AGENTS.md`、`CURRENT_STATUS.md`、任务卡、Frozen ABF、V1.0 canonical、P2-016 与 PM Review、P0-003/P0-009、P3-128 与 PM Review、`PROJECT_CONTEXT.md`、治理/PM/角色/Gate 定向章节和独立评审模板；另为 Runtime 事实定向读取 P3-126 交付物与 Re-Acceptance Review、P3-127 PM Review。
- 工具输出截断：曾发生；已按文件分页补读，未将截断内容作为 Evidence。
- 本地模型预检：未调用。任务卡与 ABF 均禁止模型使用；关键架构冻结结论不由本地预检决定。

## 需要 PM 决策

1. 将候选包交给**另一个全新隔离会话**完成只读独立评审；该会话须输出 `lifeos/reviews/LIFEOS-P3-129/independent_review.md`、独立 runner、逐项结果和非自指 Manifest。
2. 若独立评审 Pass，由 PM 同时验收候选与独立 Review。此时状态只能转为 `Awaiting Final User Freeze Confirmation`。
3. 最终用户 Gate 确认后，只有 PM 可按 [canonical_promotion_patch.json](../architecture/LIFEOS-P3-129/canonical_promotion_patch.json) 的 exact one-line patch 更新 V1.0 canonical 及 PM 账本；本会话未执行、也无权执行该动作。

## 后续任务建议

无新的工程任务建议。独立评审之前不得恢复 P3-128 Fast Track；独立评审之后也不得自动创建工程任务。

## 阻塞或异常

无候选侧技术阻塞。全局 Gate 未完成的唯一原因是合同强制的执行/评审会话隔离，而非 Evidence 缺失或可由本会话自行消除的问题。
