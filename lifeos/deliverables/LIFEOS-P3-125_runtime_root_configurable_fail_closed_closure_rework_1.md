# LIFEOS-P3-125 Rework-1｜Runtime 根可配置化与失败关闭收口

## 任务信息

- 任务 ID：`LIFEOS-P3-125`
- ABF：`ABF-P3-125-v1`（未修改）
- 正式 Rework：`1/1`
- 实际执行配置：`gpt-5.6-terra / xhigh`，由平台 request metadata 在工程动作前记录。
- 当前执行侧结论：`Technical Evidence Complete / Self-check Not Pass / Awaiting PM Review`。

## 本轮窄整改结果

Rework 候选位于 `lifeos/engineering/LIFEOS-P3-125/rework-1/candidate/`，从初次 P3-125 candidate 的 75 个文件建立独立副本。与初次 candidate 相比，只有 `build.rs` 改动；与 Frozen P3-122 75-file input 相比，仍只有已授权的 `build.rs` 与 `src/runtime.rs` 两个路径合同差异。

生产 `build.rs` 已移除任务编号固定父目录常量。`LIFEOS_RUNTIME_ROOT` 仍是唯一构建时配置，且仍拒绝缺失、空、相对、含 `.`／`..`、链接链、不可 canonicalize 和非目录 root。production 不再知道 P3-125 临时根；Rework runner 则只允许本 ABF 的 `run-a`、`run-b`、`test-root` 与明确的 disposable negative 子根，未增加设置页、目录选择、CLI flag、IPC、Schema/API 或 capability。

实际离线 Tauri 运行在两个独立 bundle 中完成。run-a 从空 Runtime 开始，实际 UI 显示 `restricted_offline` 与 0 record/0 audit；首次确认固定 synthetic capture 后显示 1/1，重复相同操作后显示 1/2 且 UI 明示幂等重复没有创建重复记录；关闭并重新打开同一 bundle 后仍为 1/2。run-b 使用同一 source、只改变构建时 root，初始状态为 0/0，首次操作后为 1/1。两个根的 SQLite、audit 和 native geometry 均在当前根内封存，截图、DB 快照、geometry 与 action hash 由 `actual-app/actions.json` 和 `ipc-lifecycle.json` 对应。

配置负向覆盖缺失、空值、相对、`..`、symlink root 和普通文件 root，均在 build 阶段拒绝。任务内离线单测覆盖 DB symlink、geometry 类型冲突、非 SQLite DB、sidecar、不可写 root 和注入的原子失败，保留 DB/sentinel 的前后不变约束。所有 Cargo target、临时夹具、bundle 和 mutation 副本只在唯一 P3-125 临时根中产生。

## Evidence 与 Manifest

Rework 资产使用新的、独立的 runner 与 Manifest verifier，未 import/copy/call P3-122 或 P3-124 runner。`verify_rework.py` 不信任 Manifest 的结果字段：它固定以 repository root 解析每个路径、复算 bytes/SHA-256、拒绝相对逃逸/重复/漏项/自指、要求所有 Rework 文件被 inventory，并独立解析 production `build.rs` 与 active `runtime.rs` 的单根、派生、验证顺序合同。

M-011 先以未变异 Manifest 验证 PASS，再对 disposable candidate 或 Manifest 执行固定父根、root fallback、DB 派生、验证顺序、历史 hash、额外文件、非法 Manifest path 与必填 role omission 八类真实变异；每一类都必须由 verifier 拒绝。M-012 只用经验证的精确路径删除唯一 P3-125 临时根，之后再生成 cleanup、history-after、逐行闭环和非自指 `FINAL_MANIFEST.json`。

主要 Rework Evidence：

- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/preflight.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/source-lineage.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/config-negatives.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/ipc-lifecycle.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/boundary.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/history-integrity.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/mutation-results.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/evidence/cleanup.json`
- `lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json`

## 如实披露与状态

开始 Rework 前，预检命令曾错误包含一个禁止的历史 Runtime root 存在性检查。其结果没有被读取、保存或用于任何结论；用户随后明确要求继续。该命令仍违反本任务的“不得 access/stat 旧根”约束，已写入 `preflight.json`。因此执行侧不会把技术 Evidence 的完成写成任务 Pass：逐行闭环中 M-001 为 `NOT_PASS`，其余技术行由独立 Evidence 覆盖；执行侧计数为 `P0=1, P1=0, P2=0, Unknown=0, Not Implemented=0`。

本报告不修改 PM 账本、风险、冻结、Stage、初次 candidate、初次 Evidence 或初次 deliverable，也不自行关闭任务。是否将该披露分类为当前任务的 P0、以及 P3-125 最终状态，均须由 PM 依 Frozen L1/L2 决定。

本轮跳过本地模型预检：这是 P0 路径／actual-Tauri／Evidence 最终边界工作，本地预检不能替代本报告的原始执行记录、Manifest verifier 或 PM 裁决。

## 角色与关卡

- 主责：技术架构／Rust-Tauri Runtime／路径安全／Evidence QA。
- 协审：数据主权、生命周期、失败关闭与历史保全。
- Gate 2：只核对 synthetic DB 来源与用户原文身份；无语义扩张。
- Gate 4：技术根可配置性、失败关闭、实际 App 生命周期、Manifest 与精确清理已取证；最终任务结论仍待 PM。
- Gate 1/3：无 UI、IPC、Schema/API、AI 或 capability 扩张；Gate 5 不适用。
