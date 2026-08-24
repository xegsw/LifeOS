# P3-108 rework-1 独立测试设计（候选与旧提交执行资产读取前冻结）

## 冻结元数据与独立性

- 任务：`LIFEOS-P3-108` rework-1；ABF：`ABF-P3-108-v1`，SHA-256 `54cbb4a8d302a1dd4007bcdbd7c7844f0d98588f54c51d941e197a8176c1ae10`。
- 授权：用户直接指示同一 P3-108 rework-1 全量重跑；D-0440 确认模型路由 `gpt-5.6-terra + xhigh`，D-0441 确认 macOS“减少动态效果”已由用户手工开启。本专项不得更改、关闭或恢复该偏好，不得调整显示缩放。
- 本轮目录：`lifeos/reviews/LIFEOS-P3-108/evidence/rework-1/`，创建时为空；P3-108 initial Evidence、Review 和 delivery 均只读保全，不能被引用为本轮 PASS 证据。
- 截至本文件写入，未读取、复制、导入或执行 P3-104/P3-106/P3-107 的 runner、tests、tools、结构化结果或 Evidence；未读取 P3-106 candidate 源码。P3-108 PM rework 指令仅作为本轮治理输入。
- 固定 token：`p3108r1a1`。临时路径逐项入 ledger；创建前检查目标缺失和祖先无链接；只允许精确删除 ledger 中的条目。

## P0 整改设计

1. `authorization.json` 必须在候选读取前落盘，记录用户/D-0440/D-0441 的模型与系统偏好授权事实、任务/ABF hash、会话与本轮 Evidence 路径。模型值的证据来源是用户/PM 记录，而不是不可观察的运行时标签。
2. 每一个动态 PASS 必须同时包含：独立结构化 JSON、原始实际 app 或 clean-binary stdout/stderr 日志、before/after 哈希/metadata、必要截图和 SHA-256。摘要 Markdown 或相邻动作不能代替。
3. 最终 verifier 必须自行读取 16 行结果、动态闭环、必需 Evidence 和 hash；任意缺失、非 PASS、无日志或清理失败必须非零退出，不得只相信汇总状态字段。

## 16 行测试矩阵

| ABF 行 | rework-1 ID | 独立方法与 PASS 条件 | 必须保留的本轮 Evidence |
|---|---|---|---|
| M-001 | `P3108R1-M001-authorization` | authorization + ABF/task hash + current fixed snapshot + 旧路径 lstat | `authorization.json`、`snapshot-before.json` |
| M-002 | `P3108R1-M002-design` | 本设计 hash/mtime 先于任何提交 runner/tests/tools/candidate 读取 | 本文件、`read-order.json` |
| M-003 | `P3108R1-M003-manifests` | P3-106 325/325；P3-104 唯一 `PASS_TIME_QUALIFIED` | `manifest-verification.json` |
| M-004 | `P3108R1-M004-copy` | 空工作副本正向 allowlist，禁项/额外根目录为 0 | `copy-inventory.json` |
| M-005 | `P3108R1-M005-build` | empty target、offline、locked test/build/tauri build 均 0 | `build/*.log`、`build-results.json` |
| M-006 | `P3108R1-M006-static` | runtime/IPC/capability/path/network/provenance 静态反查 | `static-results.json` |
| M-007 | `P3108R1-M007-visual` | 实际 app 窗口逐态在 1280×1024 与三张权威 Stitch 独立比较 | `visual/*.json`、逐态 app 截图/哈希 |
| M-008 | `P3108R1-M008-responsive` | 原工作区和精确 700×760 实际窗口，三态可滚动、无关键遮挡、动作可达 | `responsive/*.json`、截图/哈希 |
| M-009 | `P3108R1-M009-first` | actual app 首次 capture 后，DB/audit/sentinel 仅在成功回执后一致 | `lifecycle/first.json`、raw log、截图 |
| M-010 | `P3108R1-M010-negative-lifecycle` | repeat/conflict/injected failure 各自独立 before/after/日志/截图 | `lifecycle/repeat.json`、`conflict.json`、`failure.json` |
| M-011 | `P3108R1-M011-restart` | refresh、三态往返、close/reopen 后由 backend 恢复，不用旧前端缓存 | `lifecycle/refresh.json`、`navigation.json`、`reopen.json` |
| M-012 | `P3108R1-M012-denied` | disabled UI、unknown IPC、extra fields 的实际拒绝和零副作用 | `denied.json`、raw log、截图 |
| M-013 | `P3108R1-M013-boundary` | path/link/hardlink/type/**external path** 每类在变更前 actual fail-closed | `boundary/*.json`、raw process logs、before/after |
| M-014 | `P3108R1-M014-negative` | dangling final/journal/wal/shm，content/schema tamper 各自独立 fail-closed | `negative/*.json`、raw logs、截图 |
| M-015 | `P3108R1-M015-a11y` | 实际 Tab 顺序、Enter skip、main focus、用户已启用的 reduced-motion、remote/real-data/screenshot-reuse scan | `a11y/*.json`、截图/日志、`scans.json` |
| M-016 | `P3108R1-M016-cleanup` | exact cleanup、历史重算、P3-107 path、Legacy metadata、manifest 和 final negative gate | `cleanup.json`、`final-verifier.json`、非自指 Manifest |

## 动态闭环动作（全部必填）

| 动作 ID | 前置与实际操作 | 独立结果 |
|---|---|---|
| `P3108R1-D01` | 1280×1024 default 实际 app 与 Stitch 比较 | `visual/default.json` |
| `P3108R1-D02` | 1280×1024 no-suggestion 实际 app 与 Stitch 比较 | `visual/no-suggestion.json` |
| `P3108R1-D03` | 1280×1024 restricted 实际 app 与 Stitch 比较 | `visual/restricted.json` |
| `P3108R1-D04` | nominal 首次 capture | `lifecycle/first.json` |
| `P3108R1-D05` | repeat capture | `lifecycle/repeat.json` |
| `P3108R1-D06` | conflict capture | `lifecycle/conflict.json` |
| `P3108R1-D07` | injected failure | `lifecycle/failure.json` |
| `P3108R1-D08` | 实际 refresh | `lifecycle/refresh.json` |
| `P3108R1-D09` | default → no-suggestion → restricted → default 导航 | `lifecycle/navigation.json` |
| `P3108R1-D10` | close 后带同一 fixture reopen | `lifecycle/reopen.json` |
| `P3108R1-D11` | disabled 未实现 UI 实际动作 | `denied.json` |
| `P3108R1-D12` | unknown IPC 实际动作 | `denied.json` |
| `P3108R1-D13` | extra fields 实际动作 | `denied.json` |
| `P3108R1-D14` | 原工作区三态可达/滚动 | `responsive/original.json` |
| `P3108R1-D15` | 700×760 default/no-suggestion/restricted 可达/滚动 | `responsive/narrow.json` |
| `P3108R1-D16` | Tab 顺序和焦点环 | `a11y/tab.json` |
| `P3108R1-D17` | Enter 激活 skip，main 实际得到焦点 | `a11y/enter.json` |
| `P3108R1-D18` | user-enabled reduced-motion 实际行为 | `a11y/reduced-motion.json` |
| `P3108R1-D19` | path/link/hardlink/type/external-path 启动边界 | `boundary/*.json` |
| `P3108R1-D20` | dangling 与 content/schema tamper | `negative/*.json` |

## 判定与停止规则

- 每个动态 ID 必须有前置、操作、观察、结果 JSON、视觉或 raw log 及 SHA-256；缺一即 `NOT IMPLEMENTED`，不能标 PASS。
- 任何候选 P0/P1、固定输入漂移、allowlist 污染、网络/真实数据越界或历史写入：停止并结论 Rework/Blocked（按 ABF）。
- 正常 GUI 控制连续两次不可用、离线 locked 工具不可用或固定输入漂移：Blocked；不得使用 initial 动态 Evidence 替代。
- 完成后清理只作用于本轮 ledger 精确路径，随后运行 final verifier；任何非 PASS 都必须使 verifier 非零。
