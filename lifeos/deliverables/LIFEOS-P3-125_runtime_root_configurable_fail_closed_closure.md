# LIFEOS-P3-125｜Runtime 根可配置化与失败关闭收口

## 任务信息

- 任务 ID：`LIFEOS-P3-125`
- 任务名称：Runtime 根可配置化与失败关闭收口
- 执行 Agent：Codex
- 当前状态：Completed（包内自检完成；仅为提交 PM 的候选，不代表 PM Pass、用户采纳、风险关闭或 Stage 4）
- 需要 PM 决策：Yes
- 任务类型：P0 受控本地 Tauri/IPC 路径边界工程补丁
- Acceptance Basis Freeze 路径：`lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_acceptance_basis_freeze.md`
- ABF ID／版本／PM 记录 SHA-256：`ABF-P3-125-v1`／`4ab5ed8a0c1349041d1d9b13452be5059abf510f4d2ecae386e23283c1956057`
- ABF 是否在任何工程动作前核对为 Frozen：Yes
- 是否在启动前发现验收依据歧义：No；完成一次标准质疑窗口后开始工程动作。
- 当前正式 Rework 次数／上限：`0 / 1`
- 交付物篇幅是否在建议范围内：Yes

## 执行摘要

- 冻结 allowlist 已按 `75/75` 行建立全新 P3-125 candidate；历史 P3-122/P3-124、ABF、账本、风险、冻结均保持只读。
- 新增唯一构建期 `LIFEOS_RUNTIME_ROOT`：`build.rs` 要求绝对、规范化、真实且无链接祖先的 P3-125 临时根直接子目录，并把值嵌入产物；无旧根 fallback、无独立 DB／viewport／geometry 环境变量。
- `capture.sqlite`、`viewport-request.txt`、`native-geometry-*.jsonl`、sidecar 与候选 shadow 均从同一 `RuntimePaths.root` 派生；每次 DB/UI 前先验证 root、类型、链接和残留。
- 空、相对、含 `..`、符号链接、普通文件 root 均在构建期失败；运行时覆盖非 SQLite、DB 链接、sidecar、geometry 类型冲突、不可写根与注入原子失败，DB/sentinel 不变。
- 实际 Tauri App 在 `run-a`、`run-b` 和 final 根完成验证。`run-b` 先显示空 Runtime，再保存一条固定 synthetic 原文；final 根显示 `restricted_offline / 1 record / 2 audit`，关闭重开后 SQLite 仍为一条 capture 与 `capture_saved,capture_repeat`。
- `cargo test --locked --offline -- --test-threads=1` 为 `4 passed`；机器校验器为 `31/31 PASS`。本地模型预检按 P0 Tauri/IPC 最终边界规则跳过，未用其替代任何结论。

## 逐行验收与 Evidence

| ABF 行 | 冻结动作／测试 ID | 实际 Evidence | 结论 |
|---|---|---|---|
| M001 | 冻结输入与 75 行 allowlist 复算 | `evidence/results/verification.json` 的 `hash:*`、`allowlist_*` | Pass；实际会话 model/effort 独立 attestation 不可得，另列 Unknown |
| M002–M004 | source lineage 与单根派生静态核验 | `source-lineage.json`；verifier `single_root_*` | Pass |
| M005 | 空／相对／`..`／链接／普通文件 root | `evidence/logs/build-*.log`；verifier `fail_closed_log:*` | Pass，build output 前拒绝 |
| M006–M007 | run-a/run-b/final，首录、重复、刷新、关闭重开 | `actual-app/*.jpeg`、`runtime-snapshots/final-*.sqlite`、`final-geometry.jsonl` | Pass |
| M008 | 原子失败、非 SQLite、sidecar、链接／类型、不可写根 | `evidence/logs/unit-test-final.log`（4 passed） | Pass |
| M009–M010 | 旧根／独立 viewport env 移除；三 IPC 不变 | verifier `no_legacy_runtime_root_literal`、`no_independent_viewport_environment`、`three_ipc_unchanged` | Pass |
| M011 | PID／bundle-path 绑定的实际 App Quick Capture | `actual-app/final-runtime-loaded.jpeg` + final SQLite snapshot | Pass |

可复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-125/tools/verify_p3_125.py
python3 -B lifeos/engineering/LIFEOS-P3-125/tools/write_manifest.py
```

## 包内自检与范围保全

- 自检结果：`PASS`（31 项机器检查）；`P0=0, P1=0, P2=0, Unknown=1, Not Implemented=0`。
- Unknown：运行环境未提供可独立读取的当前 session model/effort attestation API；未将任务卡的推荐 `gpt-5.6-terra / xhigh` 伪报为实测配置。
- 修改范围仅为 `lifeos/engineering/LIFEOS-P3-125/`、本交付物及任务专属临时根；未修改历史输入、PM 账本、风险／冻结／阶段、UI 页面结构、三 IPC 名称/参数/回执、schema/API 或 capability。
- 未访问、创建、stat、hash、复制或清理旧 P3-122 临时根；未触碰 Pilot、真实数据／DB／路径／文本、网络、云、模型、第三方、权限、导出、恢复、同步、多设备或 L3。
- 历史输入 hash、candidate lineage、测试日志、截图、SQLite/geometry snapshots、动态闭环和非自指 Manifest 均已保留在任务工程根。
- 已在关闭受控 App 后精确删除唯一临时根 `/private/tmp/lifeos-p3-125-runtime-root-config-v1`；已复核该精确路径不存在，未使用 glob、`find` 或宽前缀删除。

## 角色与关卡

- 主责角色：技术架构／Rust-Tauri Runtime／路径安全／Evidence QA。
- 协审角色：数据主权、生命周期、失败关闭、历史保全。
- 已覆盖评审关卡：Gate 2（合成数据、来源、DB/audit 归属）与 Gate 4（构建期路径合同、actual-Tauri、失败关闭）。Gate 1/3 仅核对无语义扩张，Gate 5 不适用。
- 仍需 PM/后续任务确认的关卡：PM 验收；若 PM Pass 且用户采纳，再新建 P3-126 的全新隔离独立复评。此任务不自行复评。

## 会话与上下文

- 本任务执行方式：New Session。
- 执行授权证据：用户于 `2026-08-26 Asia/Shanghai` 投递绝对任务卡路径 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md`；任务卡已记录投递前 synthetic-only Tauri/IPC 单独确认。
- 实际 model/effort：Unknown（无独立 attestation API）；未降级、未静默切换的可核实记录不可获得。
- 若复用会话，上一任务是否已结束：N/A；是否发现旧任务授权或范围被错误继承：No。
- 已重新读取的关键文件：`AGENTS.md`、`CURRENT_STATUS.md`、任务卡、Frozen ABF、验收治理、会话模板、UI 动态闭环模板、P3-122 candidate/runtime/Manifest/PM Review、P3-124 Rework-1 Review/PM Review/Evidence，以及任务卡列出的高风险规则章节。
- 是否发生工具输出截断或补读：Yes；P3-122 runtime/UI 大输出均按定位分页补读至所需范围，未把截断内容作为结论。

## Agent 自评提示

- 本任务是否适合当前 Agent：High。
- 如果不适合，建议后续交给：PM / 独立评审 Agent。
- 原因：工程补丁与本地 Evidence 已完成；P3-126 必须保持与本执行会话隔离。

## 交付物

- 完整交付物路径：本文件。
- 文件状态：Created。
- 工程与 Evidence 根：`lifeos/engineering/LIFEOS-P3-125/`
- 动态闭环：`lifeos/engineering/LIFEOS-P3-125/evidence/DYNAMIC_CLOSURE.json`
- 验证结果：`lifeos/engineering/LIFEOS-P3-125/evidence/results/verification.json`
- 非自指 Manifest：`lifeos/engineering/LIFEOS-P3-125/evidence/FINAL_MANIFEST.json`

## 需要 PM 决策

1. 审核本候选的 P0 路径边界、31 项自检和 `Unknown=1` 的 model/effort attestation 限制；决定是否进入 PM 验收。该 Unknown 不被伪造为 Pass。
2. 仅在 PM Pass 且用户采纳后，按冻结治理另建 P3-126 全新隔离独立复评；不得在本会话或本任务内启动。

## 后续任务建议

无；P3-126 是任务卡已定义的独立评审，不由本任务自行创建。

## 阻塞或异常

无工程阻塞。唯一限制是当前平台未暴露可独立核验的实际 model/effort 元数据，已如实记为 Unknown。
