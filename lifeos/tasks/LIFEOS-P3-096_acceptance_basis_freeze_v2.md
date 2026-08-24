# LIFEOS-P3-096 Acceptance Basis Freeze V2

## 冻结信息

- 任务 ID：`LIFEOS-P3-096`
- ABF ID／版本：`ABF-P3-096-v2`
- 生效决策：D-0402
- 冻结时间：2026-08-22
- 前一版本：`lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze.md`，SHA-256 `2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58`
- SHA-256：由 PM 冻结后记录于任务卡与 D-0402；本文件不使用自指 hash。
- 状态：Frozen
- 本文件在专项会话开始前冻结：Yes

## V2 唯一变化

D-0401 后核对发现，D-0400 已授权的 P3-094 卡内修正在 D-0401 生效前已经完成写入。V2 仅把 P3-096 的只读候选输入从 attempt-9 首次 PM 快照切换为该“已授权但未 PM 验收”的晚到提交；不改变 V1 的用户结果、L1 映射、六个冻结不变量、二十行验收矩阵、Evidence 合同、Pass 公式、Rework 预算、目录、数据、入口、权限或非范围。

晚到提交入口：`lifeos/reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md`。

## 规范性继承

`ABF-P3-096-v1` 中以下章节全部逐字作为 V2 的规范性组成部分：

- 本轮唯一用户结果
- 授权和能力边界
- 适用的 L1 原则
- 冻结不变量
- 冻结验收矩阵 ABF-M-001 至 ABF-M-020
- Evidence 合同
- 计数与 Pass 公式
- Rework 预算与退出规则
- 启动前质疑窗口

执行会话必须同时读取 V1 和 V2；发生冲突时，仅“候选基线与只读保全”由 V2 替代，其余以 V1 原文为准。

## V2 候选基线与只读保全

- 首选只读候选：`lifeos/reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md` 列出的当前 P3-094 文件；复制前必须逐项复算 hash。
- 初次 PM 快照仍作为对照：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/sources/`。
- 初次 PM 反例：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.py`／`.json`。
- 允许变化：仅 P3-096 新工程目录、新交付物和新 Evidence。
- D-0401 后全部 P3-094／095 路径严格只读；hash 不一致即停止，不得修复或覆盖原路径。

## 启动门

- 用户将引用 `ABF-P3-096-v2` 的 P3-096 任务卡投递至新隔离 Codex 工程会话后才开始。
- 首份报告必须核对 V1 hash、V2 hash、晚到提交 Manifest 和其中全部候选 hash。
- 有任何歧义或漂移，在复制／测试／修改前停止并回报 PM。
