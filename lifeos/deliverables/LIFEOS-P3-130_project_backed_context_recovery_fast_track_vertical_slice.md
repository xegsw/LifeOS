# LIFEOS-P3-130｜Project-backed Context Recovery Fast Track 垂直切片

## 任务信息

- 任务 ID：`LIFEOS-P3-130`
- 执行 Agent：Codex
- 当前状态：`Blocked — Fixed-input hash mismatch before candidate copy or engineering action`
- 需要 PM 决策：Yes
- 任务类型：L2 Project-backed Context Recovery Fast Track 工程执行
- 风险等级：L2（任务卡标注 P0 优先级）
- Task Contract：`lifeos/tasks/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md`
- L3/Gate ABF：N/A（Governance V2 L2 内嵌验收合同）
- 是否在启动前发现合同歧义：Yes；固定 source allowlist 的实际 SHA-256 与任务卡声明不一致，已按任务卡第 2 节停止。
- 当前阶段：Blocked
- 交付物篇幅：Yes（阻塞记录）。

## 执行摘要

- **事实：** 在创建 `lifeos/engineering/LIFEOS-P3-130/`、复制候选或创建任何 `/private/tmp/lifeos-p3-130-context-recovery-v1` 内容之前，预检复算 source allowlist 得到 `af8fe84d2c809821bd076903ee2bfc303ae397b512c628adc4cf6e6ed7ef6b9c`。
- **事实：** 任务卡固定输入要求该同一文件为 `71dc5675d153c8a240ff59b7dcbcc17576e6eed41c6ceb969a44378be9aaad80`；两值不相等。
- **事实：** allowlist 的物理 Markdown 数据行数为 75；架构 V1.0、P3-128 handoff、P3-126 Final Manifest 的任务卡指定 SHA-256 均匹配；P3-130 candidate 根和唯一临时根均初始不存在。
- **结论：** 任务卡规定任一固定输入 hash、物理行数或路径不一致时必须在复制或工程动作前 fail closed。未读取逐个 P3-126 候选源文件、未复制任何文件、未创建候选／Evidence／临时根、未启动 Tauri、SQLite 或 IPC。
- **建议：** PM 需先裁决实际 allowlist 文件与 Task Contract 中哪一项为权威，并以新的明确 Task Contract／固定输入处理方式恢复；本专项无权改写已确认 allowlist 或任务卡哈希。

## 预检记录

| 检查项 | 任务卡预期 | 实际 | 结论 |
|---|---|---|---|
| 架构 V1.0 SHA-256 | `1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236` | 相同 | PASS |
| P3-128 handoff SHA-256 | `4e15c8006275b10058d6c307a35ac4e04ebcb63e59a249ed0eaf09962eefd3fd` | 相同 | PASS |
| P3-126 Final Manifest SHA-256 | `9b9df14db36eee2d31b9869527a46368de1b3e66e65e90b78eb893c6a86342c8` | 相同 | PASS |
| P3-130 source allowlist SHA-256 | `71dc5675d153c8a240ff59b7dcbcc17576e6eed41c6ceb969a44378be9aaad80` | `af8fe84d2c809821bd076903ee2bfc303ae397b512c628adc4cf6e6ed7ef6b9c` | FAIL / fail closed |
| source allowlist 物理数据行 | 75 | 75 | PASS |
| P3-130 candidate 根初始状态 | 不存在 | 不存在 | PASS |
| P3-130 唯一临时根初始状态 | 不存在 | 不存在 | PASS |

## 五类计数

- P0：1（固定 source allowlist hash 与 Task Contract 不一致，阻断任何候选复制或工程执行）
- P1：0
- P2：0
- Unknown：0
- Not Implemented：13（AC-01～AC-13 未执行；不是失败后伪写 Pass）

## 角色与关卡

- 主责角色：Codex 工程执行。
- 协审角色：后续必须由另一全新隔离会话完成独立复评；本轮未触发，因为工程未启动。
- Evidence 等级与已覆盖关卡：仅启动前固定输入／授权路径预检；未达到 L2+ actual-Tauri Evidence。
- 仍需 PM/后续任务确认的关卡：固定输入权威与恢复执行的合同边界。

## 会话与上下文

- 本任务执行方式：New Session。
- 执行授权证据：用户投递本任务卡绝对路径；D-0527 已确认合同内合成离线 Tauri／五 IPC／唯一根边界。
- 若复用会话，上一任务是否已结束：N/A。
- 是否发现旧任务授权或范围被错误继承：No。
- 已重新读取的关键文件：根 `AGENTS.md`、`lifeos/CURRENT_STATUS.md`、P3-130 任务卡、P3-130 source allowlist、架构 V1.0、P3-128 handoff／Application Port／Context Resolver／Memory provenance／negative cases、P3-128交付物和 PM Review、P3-126交付物、P3-127 PM Review、UI Dynamic Evidence Closure 与 Session Report 模板。
- 是否发生工具输出截断或补读：Yes；`CURRENT_STATUS.md` 曾截断，已分段补读至 EOF；未将截断输出作为预检依据。

## Agent 自评提示

- 本任务是否适合当前 Agent：High。
- 如果不适合，建议后续交给：PM。
- 原因：当前阻塞是固定输入／Task Contract 权威冲突，超出工程专项会话改写权限。

## 交付物

- 完整交付物路径：本文件。
- 文件状态：Created。

## 需要 PM 决策

PM 需确认 P3-130 source allowlist 的正确固定 hash，并按治理规则提供可执行且一致的 Task Contract／输入。现有合同不支持由本专项会话自行修复或绕过该差异。

## 后续任务建议

无；应先解决当前 Task Contract 固定输入冲突，再决定是否恢复 P3-130 或建立新合同。

## 阻塞或异常

固定 source allowlist SHA-256 不一致。已在任何候选复制、工程根／Evidence 根创建、临时根创建、Tauri 构建、IPC、SQLite、UI 动态操作和历史资产读取之前停止。
