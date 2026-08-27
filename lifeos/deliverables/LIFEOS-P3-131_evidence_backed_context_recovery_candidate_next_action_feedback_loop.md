# LIFEOS-P3-131｜Evidence-backed Context Recovery 与 Candidate Next Action 用户闭环

## 任务信息

- 任务 ID：LIFEOS-P3-131
- 执行 Agent：Codex
- 当前状态：Completed，等待 PM 按 AC-01～AC-14 验收；不冻结
- 任务类型：同一受控工程线的 L2 actual Tauri 能力闭环
- Task Contract：`lifeos/tasks/LIFEOS-P3-131_evidence_backed_context_recovery_candidate_next_action_feedback_loop.md`
- L3/Gate ABF：N/A
- 启动前合同歧义：无
- 需要 PM 决策：无；仅需正常 PM 验收

## 执行摘要

- 从 P3-130 最终 Manifest 验证并复制 75 个候选文件；最终来源核对无问题，候选目录仍恰为 75 个普通文件。
- 实现了八项严格 IPC 和离线确定性规则 `local_rule:p3-131-v1`：有充分 Evidence 时零或一条系统派生 Candidate；不足时返回零条和固定披露。
- 用户只能显式 `accept` 或 `edit_accept` 创建开放 Action；`reject`、`defer` 仅追加 Feedback。Today 只显示用户确认且开放的 Action，`todays_focus` 始终为 `null`。
- 实际 Tauri 分别验证了直接确认、编辑确认、拒绝、暂缓、证据不足、完成结果与关闭重开；每条运行均有 UI→IPC→SQLite/audit 对应快照。
- 关闭重开后开放 Action 仍可见；完成后从 Today 移除，Memory provenance 显示 Derivation、Candidate、Feedback、Action、Result 引用，且 `memory_copy_created=false`。
- 包内修正了两项首次实际运行发现的状态/文案缺口：终态 Candidate 不再重新显示；证据不足时界面显示固定披露。两个缺陷运行均未计入最终 Evidence。
- 唯一临时根已按精确绝对路径清理并确认不存在。P0/P1/P2/Unknown/Not Implemented 均为 0。

## 验收与 Evidence

| AC | 结论 | 主要 Evidence |
|---|---|---|
| AC-01 | PASS：75 个 P3-130 来源路径、bytes、SHA-256 与类型受核对；P3-131 仅在限定文件中修改。 | `evidence/source-lineage.json` |
| AC-02 | PASS：前五兼容 IPC、八项总命令、零 renderer permission 与 runtime-root fail-closed 均已验证。 | `evidence/source-scan.json`、`evidence/runtime-root-negative.log` |
| AC-03 | PASS：Candidate 是 system-derived、至多一条，具有 processor/version、basis 和 why。 | `evidence/run-b-direct-accept-complete-reopen.json`、`evidence/actual-app-action-log.json` |
| AC-04 | PASS：纯净 `run-g` 显示固定披露且 Derivation/Candidate/Feedback/Action/Result 均为零。 | `evidence/run-g-insufficient.json` |
| AC-05 | PASS：actual UI 直接确认与编辑确认均只经显式决定创建 Action，并保持文字/身份分离。 | `evidence/run-b-direct-accept-complete-reopen.json`、`evidence/run-c-edit-accept.json` |
| AC-06 | PASS：actual reject/defer 均只产生对应 Feedback，Action/Result 为零。 | `evidence/run-d-reject.json`、`evidence/run-e-defer.json` |
| AC-07 | PASS：已确认开放 Action 才能完成；重复结果幂等，冲突/终态写入 fail-closed。 | `evidence/contract-test.log`、`evidence/run-b-direct-accept-complete-reopen.json` |
| AC-08 | PASS：actual App 关闭重开后开放 Action 保持一致；完成后 Today 不再显示，Focus 不被占用。 | `evidence/actual-app-action-log.json`、`evidence/run-b-direct-accept-complete-reopen.json` |
| AC-09 | PASS：Memory DTO/持久状态回链 Derivation、Evidence basis、Source/Artifact、Feedback、Action、Result，未复制原文。 | `evidence/run-b-direct-accept-complete-reopen.json`、`evidence/actual-app-action-log.json` |
| AC-10 | PASS：Source、generation、tombstone、authorization、evidence-ready 五类 mutation 都得到零候选且 DB hash 不变。 | `evidence/contract-test.log` |
| AC-11 | PASS：unknown 字段、缺 edited_text、非法 ID、幂等冲突和非开放 Action 均在写入前停止。 | `evidence/contract-test.log` |
| AC-12 | PASS：命令精确八项；renderer 无 SQL/filesystem/network/Model/Agent 直连；capability permission 为空。 | `evidence/source-scan.json` |
| AC-13 | PASS：actual Tauri 逐行动作覆盖直接确认、编辑确认、拒绝、延后、零候选、完成、关闭重开。 | `evidence/UI_DYNAMIC_CLOSURE.md`、`evidence/actual-app-action-log.json` |
| AC-14 | PASS：临时根精确清理；历史无写入；Final Manifest 非自指且全量 hash 重验通过。 | `evidence/cleanup.json`、`evidence/FINAL_MANIFEST.json` |

动态闭环自检为 PASS，详见 `evidence/closure-check.json`。Final Manifest 记录 75 个候选文件和 14 个保留 Evidence 项，明确排除自身与可重建 build cache。

## 测试与复跑

- Rust：`cargo test --locked --offline`，6/6 通过。
- UI 语法：bundled Node `--check` 通过。
- Diff 格式：`git diff --check` 通过。
- Manifest 重验：候选 75、Evidence 14，hash 问题/未列入项/缺失项均为 0。
- task-local 复跑命令（仅写任务工程根和唯一临时根）：

```sh
zsh /Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-131/tools/replay.sh
```

## 角色与关卡

- 主责角色：Codex 工程执行。
- 协审角色：PM 主会话按 AC-01～AC-14 验收。
- Evidence 等级：L2 actual Tauri；结构化快照、动态闭环、负例、mutation、清理和 non-self Manifest 已覆盖。
- 独立评审：未触发。没有可复算性失败、Evidence 污染、越权或 Closure Cycle 后关键争议。
- 仍需关卡：PM 验收；PM Pass 后按 Governance V2 进入 `Accepted / Complete / Not Frozen`。

## 范围与边界

- 事实：没有触碰 P3-130 或更早任务的候选、Evidence、Review、Manifest 或历史 Runtime 根。
- 事实：没有真实数据、网络、模型、Agent、通用 Action/Context API、权限、导出、同步、Schema/API/Runtime 冻结或 Stage 操作。
- 推断：该合成切片的用户闭环在合同范围内可复算；它不证明真实能力、风险关闭、工程基线恢复或 Stage 4 准入。
- 建议：无合同外后续任务建议；由 PM 在验收后独立决定后续规划。

## 异常与清理

- 运行中发现的两项合同内缺陷已包内修正并由后续全新 Runtime 根重跑；不将失败运行用作正向 Evidence。
- 已删除（不可恢复）：`/private/tmp/lifeos-p3-131-next-action-v1`，清理前 26 个目录、14 个文件、662272 bytes；清理后路径不存在。
- 阻塞：无。
