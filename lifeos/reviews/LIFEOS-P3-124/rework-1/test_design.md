# LIFEOS-P3-124 Rework 1｜独立测试设计（候选读取前）

## 身份与边界

- 任务：`LIFEOS-P3-124`，PM 正式 Rework `1/2`；Frozen `ABF-P3-124-v1` 不变。
- 会话类型：全新隔离独立复评线的同任务窄整改；不是工程实现、PM 验收或风险裁决。
- 写入：仅本目录与 `/private/tmp/lifeos-p3-124-independent-review-v1`。
- 只读：P3-122 candidate、P3-123、P3-124 初次 Review/Evidence、任务卡、ABF、PM 账本和全部历史资产。
- 允许：离线 task-local candidate 副本、全新固定非敏感 SQLite、三项既有 IPC、实际 Tauri、本地 native/read-only geometry 与实际 App capture。
- 禁止：真实/Pilot 数据或路径、网络、模型、第四 IPC、clear/export/权限/恢复、系统设置、候选或 ABF 修改、风险/冻结/阶段动作。

## 时间语义（P124-M001）

本轮必须分开记录，绝不把不同时间点压缩为“两个根均 absent”：

1. `freeze_time`: D-0499/ABF 所记的初始 P3-124 review 根和 temp 根不存在，是冻结前提的历史事实。
2. `rework_session_start`: 初始 P3-124 review 根依法保留且存在；本轮专属 `rework-1` 和 temp 根均不存在。
3. `preflight_before_execution_root`: 创建本 Rework Evidence 目录前已确认专属 rework root 与 temp 根不存在；随后才创建 rework root 以保存 preflight。不可将该已创建的 root 标作当前 absent。

## 独立性约束与工具设计

- 只写 `rework_runner.py`、`native_probe.swift` 和本目录 Evidence；不读取、复制、import、调用或 subprocess P3-122/P3-123/initial P3-124 runner。
- `native_probe.swift` 是本轮自写、只读的 AppKit/CoreGraphics helper：以 bundle identifier、task-local bundle path 和 PID 验证 native process 与唯一 window；不注入输入、不改候选、不截取环境外内容。
- Computer Use 只在 helper 绑定 bundle-build-hash、`local.lifeos.p3-122`、PID、唯一 window 后，用该 bundle target 进行实际 App 操作与 capture。
- 未取得上述四元绑定时，不执行页面/IPC 动作；记录真实失败，不以静态、缩略图或旧 Evidence 替代。

## 矩阵与具体测试

| ABF 行 | 测试 ID | 前置／动作 | 必须保存的实际 Evidence | 预期 |
|---|---|---|---|---|
| M-001 | P124R-M001 | 解析 Frozen allowlist；校验授权、ABF、固定 inputs、时间语义与空根 | `preflight.json` | 75 physical rows；所有 hash 相符；仅 rework root 可在记录后出现 |
| M-002 | P124R-M002 | 扫描本轮 runner/helper 的 import、subprocess、content 指纹 | `independence.json` | 不复用历史 runner/tool |
| M-003 | P124R-M003 | 从 allowlist copy 独立重算 visual 8/8、runtime 65/65、tree hash | `source-lineage.json` | candidate/source lineage 全匹配 |
| M-004 | P124R-M004 | task-local copy 的 locked offline test、build、bundle | `build-result.json`, logs | 仅离线写入 temp，exit 0 |
| M-005/M-006/M-007 | P124R-UI-01..18 | 三个 frozen logical viewports 下的六个页面／状态；每行捕获 native window、WebView/DOM、DPR/display、截图、动作结果 | `ui-closure.json`, `screenshots/`, `geometry/` | 18/18 行可独立复核，不以相邻行代替 |
| M-008 | P124R-IPC-01..05 | fresh status、first capture、repeat、refresh、verified close/reopen | `runtime-results.json`, DB/audit/UI traces | 三 IPC、DB/audit/UI 一致 |
| M-009 | P124R-NEG-01..04 | task-local path/type/DB/atomic failure before state change | `negative-results.json`, before/after hashes | fail closed，DB/sentinel/UI 无错误成功残留 |
| M-010 | P124R-BND-01 | 静态 allowlist/inventory + task-local runtime trace | `boundary.json` | 只有三 IPC，禁能/真实边界关闭 |
| M-011 | P124R-LIN-01 | 复算 Engineering Final、PM acceptance/adoption 和本轮 fixed inputs | `lineage.json` | lineage 无遗漏/错绑/自指 |
| M-012 | P124R-MUT-01..09 | pristine control 后，对 disposable payload 实作九类独立变异 | `mutation-results.json` | pristine pass；每类以预期原因 fail closed |
| M-013 | P124R-CLN-01 | 先终止已验证 task-local PID，再精确删除唯一 temp root，复算历史 | `cleanup.json` | temp root absent，历史 hash 不变 |
| M-014 | P124R-FIN-01 | runner 检查逐行结构化结果、hash 和非自指 Manifest | `FINAL_MANIFEST.json`, review | 全部行 PASS 才可给 Pass；否则诚实 Not Pass |

## UI 闭环行定义

18 行固定为：每个 logical viewport `1280x1024`、`1160x768`、`700x760` 各包含 `Today`、`Capture`、`Memory`、`Context`、`Settings`、`Global AI expanded`。每一行至少产生：唯一 action ID、前后 native-probe JSON、renderer geometry JSON、独立截图、capture hash 与结论。实际屏幕像素与 logical viewport 分栏记录，不互相冒充。

## 失败和停止规则

- 固定输入/hash/allowlist/授权/根状态失败：停止于 preflight。
- bundle、identifier、bundle hash、PID 或唯一 native window 任何一项未绑定：不进行 App action；该动态行 `NOT IMPLEMENTED`/`Unknown`，不得用替代 Evidence 标 PASS。
- 任一失败测试改变了 DB、sentinel 或 UI：立即停止后续同类测试，保全 before/after Evidence。
- 任何 matrix、closure、mutation、cleanup 或 non-self Manifest 不完整：最终不得写 Pass。

## 预期产物

- 本轮 runner、native helper、逐行 JSON、闭环表、日志摘要、截图/geometry、独立 Review 和非自指 Final Manifest 均位于 `rework-1/`。
- 本轮无需本地模型预检：P0 actual-Tauri/native geometry/Evidence-lineage 终局判断不适用，避免其输出误导正式结论。
