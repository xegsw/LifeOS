# LIFEOS-P3-130｜Project-backed Context Recovery Fast Track 垂直切片

## 任务信息

- 任务 ID：`LIFEOS-P3-130`
- 执行 Agent：Codex
- 当前状态：`Partial / Not Pass — 工程与 L2+ actual-Tauri Evidence 已完成，但存在 1 项清理后的 P1 流程偏差`
- 需要 PM 决策：Yes
- 任务类型：L2 Project-backed Context Recovery Fast Track 工程执行
- 风险等级：L2（任务卡标注 P0 优先级）
- Task Contract：`lifeos/tasks/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md`，SHA-256 `f39f1ca8460389fa637f8e1e175f43ef67742697efbb5ea1e8081ed8aacd10ec`
- L3/Gate ABF：N/A（Governance V2 L2 内嵌验收合同）
- 启动前合同歧义：No。此前 `D-0526` 残留 hash 已由 PM 更正；本轮启动预检通过，首次正确 fail-closed 不计 Rework。
- 当前阶段：Closure Cycle / PM decision required
- 交付物篇幅：Slightly Over（L2+ actual-App Evidence 与流程偏差均需可复核记录）。

## 执行摘要

- **事实：** 按更正后的 Task Contract 重新启动，75 行 source allowlist SHA-256 `af8fe84d2c809821bd076903ee2bfc303ae397b512c628adc4cf6e6ed7ef6b9c`、行数 75 和任务卡 hash 均匹配；75 个允许源文件复制到 P3-130 candidate，历史源保持只读。
- **事实：** 候选实现恰好五项 Tauri command：`capture_record`、`get_today`、`runtime_status`、`confirm_capture_context`、`get_context_recovery`。没有第六 IPC、通用 Context／Memory 表、真实数据、网络、Model 或 Agent 路径。
- **事实：** 离线测试 5/5 通过。actual Tauri run-a 覆盖空状态、capture、capture 幂等、candidate、confirm、关闭重开、Memory provenance 与 Inspector 临时选中移除；run-b 独立覆盖 reject；run-c 覆盖窄视口。所有 SQLite/audit 读取均来自 task-local synthetic DB 快照。
- **事实：** native geometry 文件保留了 `1280×1024`、`1160×768`、`700×760` 三种实际逻辑内容边界；1280 截图受主机可见区域限制为 960×768，未将其表述为完整逻辑像素截图。
- **异常（P1）：** 为解析 Final Manifest 曾短暂写入未授权临时路径 `/private/tmp/p3-130-manifest-parse.json`；已精确删除，未接触任何真实数据、历史 Runtime、网络、Model、Agent 或外部资产，但不能从执行历史中抹去。
- **结论：** 工程行为和合同内 Evidence 已达成；但 Task Contract 的 Pass 公式要求 P1=0。因此本专项不能自报 `Pass`、`Candidate Ready`、冻结、风险关闭或 Stage 变更，也不会自行启动独立复评。

## 实现与 Evidence

- 候选：`lifeos/engineering/LIFEOS-P3-130/candidate/`
- Evidence 根：`lifeos/engineering/LIFEOS-P3-130/evidence/`
- 可复跑结构核查：`python3 -B lifeos/engineering/LIFEOS-P3-130/tools/verify_p3_130.py verify --output lifeos/engineering/LIFEOS-P3-130/evidence/static-verification.json`
- 可复跑测试：在 candidate 目录以 task-local `LIFEOS_RUNTIME_ROOT`、`CARGO_TARGET_DIR` 和缓存执行 `/Users/xxe/.cargo/bin/cargo test --locked --offline`；本轮日志见 `evidence/unit-tests.log`。
- 实际应用闭环：`evidence/actual-app-action-trace.json`、`run-a-*.json`、`run-b-rejected-db.json`、实际窗口截图和三份 `native-geometry-*.jsonl`。
- 逐行验收：`evidence/dynamic-closure-matrix.md`。
- 负路径／mutation：`evidence/mutation-results.json` 与 `evidence/unit-tests.log`。
- 来源、静态约束和五 IPC：`evidence/static-verification.json`（PASS，75/75 lineage）。
- 清理、临时根 inventory 和非自指清单：`evidence/pre-cleanup-inventory.json`、`evidence/cleanup.json`、`evidence/FINAL_MANIFEST.json`。
- P1 事实与删除状态：`evidence/scope-deviation.json`。

## 五类计数

- P0：0
- P1：1（任务唯一临时根之外的短暂 task-owned manifest parse 文件；已精确清理，但违反该合同的临时路径边界）
- P2：0
- Unknown：0
- Not Implemented：1（独立复评未启动；任务明确要求另一个新隔离会话，且本专项不得自行启动）

## 角色与关卡

- 主责角色：Codex 工程执行。
- 协审角色：独立复评须由另一全新隔离会话完成；本会话未自评自己实现的成果。
- Evidence 等级与已覆盖关卡：L2+ actual Tauri 工程侧动态闭环、严格 DTO、SQLite/audit、关闭重开、失败关闭、三逻辑视口、精确清理均已覆盖。
- 仍需 PM/后续任务确认的关卡：P1 流程偏差的治理处理；其后才可由独立会话依据完整 Evidence 决定是否开展复评。

## 会话与上下文

- 本任务执行方式：Reused Session；由 PM 明确重新投递校正后的同一 Task Contract。
- 执行授权证据：用户通过 PM delegation 明确允许在原工程会话继续同一 P3-130，确认不需要新任务、Rework 或额外边界确认。
- 上一状态是否已结束：Yes；此前为正确 fail-closed，PM 已更正合同残留 hash 并记录为 Rework 0。
- 是否发现旧任务授权或范围被错误继承：No。
- 已重新读取的关键文件：根 `AGENTS.md`、最新 `lifeos/CURRENT_STATUS.md`、校正任务卡、source allowlist、PM Review 和 PM preflight Evidence；本轮沿用并核对任务卡指定的架构、P3-128、P3-126、P3-127、模板输入。
- 工具输出截断或补读：Yes；构建输出曾截断，但完成状态通过 bundle existence、单元日志和后续 actual App 验证复核；未将截断文本作为结论依据。

## Agent 自评提示

- 本任务是否适合当前 Agent：High（工程实现、离线测试与 actual Tauri Evidence）。
- 如果不适合，建议后续交给：PM + 独立评审 Agent。
- 原因：剩余问题不是工程能力缺口，而是 Frozen Task Contract 下已发生的路径边界偏差及其治理裁决。

## 交付物

- 完整交付物路径：本文件。
- 文件状态：Updated（替换此前正确 fail-closed 记录；保留其历史事实，不把其计入 Rework）。

## 需要 PM 决策

1. 是否将 `scope-deviation.json` 所记录、已精确清理的 P1 路径偏差作为本合同不可接受的执行历史，并据此建立新的受控任务／合同；或作出其他治理处理。专项 Agent 无权自行豁免。
2. 在 P1 处理完成前，不应启动独立复评；若 PM 允许继续，应由全新隔离会话读取本 Evidence 而非本会话自证。

## 后续任务建议

无自动后继任务。任何继续动作均以 PM 对 P1 的治理决定为前提。

## 阻塞或异常

`/private/tmp/p3-130-manifest-parse.json` 在 Manifest JSON 解析时被短暂创建，随后已精确删除；`/private/tmp/lifeos-p3-130-context-recovery-v1` 也已按合同精确清理并记录为 absent。该偏差不改变实现、测试、actual-app、DB/audit 或历史完整性事实，但使本合同当前无法满足 `P1=0` 的 Pass 公式。
