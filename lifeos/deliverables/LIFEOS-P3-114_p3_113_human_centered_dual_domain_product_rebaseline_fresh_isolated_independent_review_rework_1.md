# LIFEOS-P3-114 Rework 1｜Evidence 映射窄整改交付物

## 1. 任务与授权状态

- 任务：`LIFEOS-P3-114`，Rework 1/2。
- 授权依据：用户采纳 `LIFEOS-P3-114 PM Review` 所记录的 `PM-CE-001 / P1`，并将 PM Review 路径投递至原独立评审会话。
- ABF：`ABF-P3-114-v1` 保持 Frozen，SHA-256 `22d1b5f89ce608e72cdf42d3e08fe3adf11f57b10f23a64d2cf7b1273f27b96d`。
- 范围：只重建 P3-114 自身 M-001～M-013 的 Evidence 映射；不重做产品候选、不变更 ABF、不修改原 P3-114 资产或 P3-113 输入。
- 提交状态：**Evidence-mapping Rework Pass — Awaiting PM Re-Acceptance**。

## 2. 事实：原 P1 的边界

PM 发现的 P1 仅为原 `results.json` 对 M-002、M-005、M-008、M-010 的行号→Evidence 错配。对应的独立 Evidence 文件均已存在，P3-113 产品候选没有被确认出 P0/P1；但 Evidence 存在不能替代每个 Frozen 矩阵行动作的精确、机器可读绑定。

本 Rework 没有通过手工解释宣称原结果已合格，而是以独立 runner 将新 `matrix_mapping.json` 的每行同 Frozen ABF 表格逐项比较。

## 3. 13 行恢复结果

| 行 | 测试 | 正确实际 Evidence | 结果 |
|---|---|---|---|
| M-001 | IR-001 | 原 `session_boundary.json` | PASS |
| M-002 | IR-002 | 原 `test_design.md`、`read_order.json` | PASS |
| M-003 | IR-003 | 原 `input_integrity.json` | PASS |
| M-004 | IR-004 | 原 `product_center_review.json` | PASS |
| M-005 | IR-005 | 原 `frozen_asset_impact_review.json` | PASS |
| M-006 | IR-006 | 原 `source_memory_counterexamples.json` | PASS |
| M-007 | IR-007 | 原 `home_advice_contract_review.json` | PASS |
| M-008 | IR-008 | 原 `feedback_lifecycle_counterexamples.json` | PASS |
| M-009 | IR-009 | 原 `health_safety_review.json` | PASS |
| M-010 | IR-010 | 原 `cross_domain_replay.json` | PASS |
| M-011 | IR-011 | 原 `gate_and_route_review.json` | PASS |
| M-012 | IR-012 | 原 `independent_counterexamples.json` | PASS |
| M-013 | IR-013 | 本 Rework `results.json`、`temporary_residue.json`、`MANIFEST.md` | PASS |

每行的 Frozen 动作、指定 Evidence 名称、实际相对路径和独立结论均记录于 `rework/rework-1/evidence/matrix_mapping.json` 与本 Rework `results.json`。

## 4. 可复核性与历史保全

- 原 P3-114 Evidence Manifest 21/21、P3-113 初次 Manifest 14/14、P3-113 Rework Manifest 12/12 均复算匹配。
- 任务卡、ABF、PM Review 与原 Manifest 的记录 hash 在 Rework 授权与完整性 Evidence 中可查。
- 新 runner 只读取文本／JSON、重新计算 SHA-256／bytes，并逐行对照 Frozen ABF；两次运行均为 PASS。
- 原临时根 `/private/tmp/lifeos-p3-114-product-review-v1` 全程不存在；本 Rework 未创建任何临时夹具或访问其他 `/private/tmp` 路径。

## 5. 自检结论与不外推边界

- 自检计数：**P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0**。
- 已关闭的仅是 P3-114 自身的 Evidence 映射 P1，尚待 PM 复验。
- 本交付物不改变原产品实质判断，且不构成 P3-114 PM Pass、P3-113 冻结、产品／原型／工程授权、真实价值验证、风险动作或 Stage 4 结论。

## 6. 需要 PM 决策

请 PM 仅复验 Rework 1 的 13 行映射、原资产 hash 保全、Rework Manifest 与临时根关闭态。复验通过后，才可决定是否接受 P3-114 的独立评审结论；任何候选冻结仍须单独用户／PM 决策。
