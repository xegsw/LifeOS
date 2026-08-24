# LIFEOS-P3-095｜PM 验收 Review

## 验收信息

- 任务 ID：LIFEOS-P3-095
- 是否为受控能力包：Yes（P3-094 当前 hash 的全新隔离独立复评）
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-095_real_local_capture_persistence_today_view_fresh_isolated_independent_re_review.md`
- 独立 Review：`lifeos/reviews/LIFEOS-P3-095/independent_review.md`
- PM Review：本文件
- 执行授权证据：交付物记录用户于 2026-08-22 08:50 CST 将任务卡投递至新建隔离 Codex 独立评审会话；实际模型 `gpt-5.6-terra` + `high`，未降级。
- 验收状态：Accepted / Rework / User Adopted
- P3-094 资产：Not Frozen / Independent Re-review Rework
- 是否允许进入下一任务：No；已回到同一 P3-094 能力包执行 attempt-4 窄整改
- 是否允许进入下一阶段：No
- 更新时间：2026-08-22

## PM 总结

1. 独立性成立：新隔离会话、新独立 runner，仅加载 P3-094 公开运行时；没有调用或复制执行侧测试／runner。
2. 独立离线矩阵为 9 PASS / 1 FAIL。首次捕获、幂等、同键异文拒绝、空输入拒绝、跨进程复读、身份／时间／来源、原子回滚和损坏 DB fail-closed 均通过。
3. 实质 P1 成立：精确清空 SQLite 后，旧 `today.html` 未失效；PM 使用新的固定非敏感临时副本复现相同结果。
4. 评审侧另遗留精确 `/private/tmp/lifeos-p3-095-pycache`，约 716 KB、无用户内容；这不是 P3-094 工程缺陷，但违反本任务残留为零的完成条件。
5. 因离线 P1，Chrome 动态 4 项按任务卡停止为 Not Implemented；不能用 P3-094 旧动态 Evidence 替代。
6. 历史 PM Manifest 相对路径存在 P2，但所记 PM Review hash 与目标文件一致，不构成内容冲突。

## 计数与关卡

- P0=0；P1=2；P2=1；Unknown=0；Not Implemented=4。
- Gate 2：未通过，清理后旧展示工件仍可暴露已清理内容。
- Gate 3：本轮关闭态静态核查通过；未启用 AI 或外部处理。
- Gate 4：未通过，生命周期清理合同存在 P1，动态矩阵未实施。
- Gate 1：有限一致性通过；Gate 5 未覆盖。

## 同一能力包整改要求

用户采纳后，P1-01 回到 P3-094 同一能力包，不创建新任务号：

1. 清理成功后，先前内部展示工件必须立即失效或被精确删除；清理失败不得留下“数据已清理但旧页面仍可展示”的状态。
2. 增加“先捕获并渲染→精确确认清理→旧页面不存在／不可展示”的正向回归，以及清理失败／页面失效失败的 fail-closed 负向回归。
3. 使用新的保全型 Evidence 目录，不覆盖 P3-094 attempt-1／2／3 或 P3-095 Review／Evidence；修复后重新 PM 验收，并创建另一全新隔离独立复评完整重跑离线与 Chrome `file:` 动态矩阵。
4. 经用户明确确认后，仅精确删除 `/private/tmp/lifeos-p3-095-pycache`；不得使用 glob 或处理其他临时目录。
5. 历史 PM Manifest 不追溯覆盖；后续 PM Evidence 使用正确相对路径并保留目标 hash。

## 状态边界

- P3-095 任务完成但独立结论为 Rework；P3-094 不冻结。
- R-0051 继续 Open，不因整改或后续复评自动关闭。
- 不恢复工程基线，不冻结 Schema/API，不进入 Stage 4。
- 本地预检未调用：本轮是涉及真实本地数据清理边界的 P0 独立最终判断，局域网模型不应替代人工复核。

## 用户采纳记录

用户已于 2026-08-22 采纳本 Rework，并允许精确删除 `/private/tmp/lifeos-p3-095-pycache`。PM 已核对目标为该精确目录、完成删除并确认路径不存在。工程整改已按 D-0387 回到同一 P3-094 能力包 attempt-4；该采纳不扩大真实数据、既有文件／DB、网络、云、Tauri/IPC、导出、风险、冻结、基线或阶段范围。
