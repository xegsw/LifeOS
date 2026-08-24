# LIFEOS-P3-114 Rework 1｜独立评审 Evidence 映射窄整改

## 评审信息

- 对应任务 ID：`LIFEOS-P3-114`；正式 Rework：1/2。
- Rework 授权：用户已采纳 PM 的 `PM-CE-001 / P1`，授权原 P3-114 独立评审会话在不变 `ABF-P3-114-v1` 下完成 Evidence-only 窄整改。
- 被评审范围：仅原 P3-114 的 Frozen ABF M-001～M-013「行号 → 冻结动作 → 测试 ID → 实际 Evidence → 结论」映射。
- 严格只读：P3-113 候选、初次 P3-114 交付物／Review／Evidence、历史资产、PM Evidence、账本、风险、冻结与阶段。
- Rework 结论：**Evidence-mapping Rework Pass — Awaiting PM Re-Acceptance**。

## PM finding 与整改结果

PM-CE-001 不是 P3-113 产品候选缺陷：原 `results.json` 的四个矩阵行将相邻主题的 Evidence 绑定为本行 Evidence，因而不满足 ABF-I-12 的逐行可复核性。

| Frozen 行 | 原漂移 | Rework 1 正确绑定 |
|---|---|---|
| M-002 / IR-002 | 绑定历史冻结资产影响 | `test_design.md` + `read_order.json`，证明候选阅读前独立设计 |
| M-005 / IR-005 | 绑定 Source／记忆反例 | `frozen_asset_impact_review.json`，核对历史资产影响 |
| M-008 / IR-008 | 绑定跨领域回放 | `feedback_lifecycle_counterexamples.json`，核对反馈生命周期 |
| M-010 / IR-010 | 绑定 Gate／路线 | `cross_domain_replay.json`，复演完整双域闭环 |

`matrix_mapping.json` 已重建 **全部** M-001～M-013 的 Frozen 动作、原始测试 ID、ABF 指定 Evidence 名称、实际路径和行结论。独立 runner 直接解析 Frozen ABF 表格并逐项比较：13/13 action、test ID、Evidence 名称和实际路径全部一致。

## 只读保全与复跑

- 原 P3-114 Evidence Manifest：21/21 hash／bytes 一致，且其自身 hash 与 PM 记录一致。
- P3-113 初次 Manifest：14/14 一致；Rework 1 Manifest：12/12 hash／bytes 一致。
- 任务卡、Frozen ABF 与当前 PM Review 的 hash 均与 Rework 授权记录一致。
- 原精确临时根在 Rework 起止均不存在。本次只运行 Markdown／JSON／hash 映射验证，未创建夹具或其他临时目录。
- 独立 runner 可重复运行，且不调用任何原专项 runner、应用、DB、模型、网络、外部来源或真实数据。

## 计数与关卡

- Rework 自检计数：**P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0**。
- Gate 1、Gate 2、Gate 3 的原候选层独立实质判断保持不变；本 Rework 不重写或扩大这些判断。
- Gate 4 仍只为条件性历史输入；Gate 5 仍只为可证伪假设。两者都不是本 Rework 的通过结论。

## 边界与 PM 决策

本 Rework 不等于 P3-114 已 PM Pass，也不等于 P3-113 Frozen、用户价值成立、原型／工程获授权、风险关闭或 Stage 4 准入。

需要 PM 复验：新 Rework Manifest、13 行正确映射和原资产 hash 保全。PM 复验与其后的用户采纳前，不允许任何后续任务或冻结动作。
