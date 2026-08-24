# LIFEOS-P3-104 Acceptance Basis Freeze｜三页 UI→本地 Runtime 与受控 Tauri/IPC 整合

## 冻结信息

- 任务 ID：`LIFEOS-P3-104`
- ABF ID／版本：`ABF-P3-104-v1`
- 生效决策：D-0424
- 创建时间：2026-08-23 12:10:20 CST (+0800)
- 冻结完成时间：2026-08-23 12:16:34 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 用户授权与工具链供应链冻结

用户于 2026-08-23 明确允许 P3-104 使用官方 Rust／Tauri 工具链，并允许后续专项会话仅从官方分发和 registry 下载依赖，写入 `/Users/xxe/.rustup`、`/Users/xxe/.cargo` 及 P3-104 task-local `.tooling/`；禁止系统级安装、全局 npm、第三方镜像。bootstrap 完成后必须离线构建和复跑。

### 精确版本与实现方式

| 项目 | 冻结值 |
|---|---|
| Rust toolchain | `1.98.0`，profile `minimal` |
| Tauri CLI | `tauri-cli 2.11.4`，以 `cargo install tauri-cli --version 2.11.4 --locked` 安装 |
| Tauri app crate | `tauri = "=2.11.5"` |
| Tauri build crate | `tauri-build = "=2.6.3"` |
| SQLite crate | `rusqlite = "=0.40.2"`；不得启用 SQLCipher；如使用 `bundled` 必须在 lock 与 Evidence 中披露 |
| Serialization | `serde = "=1.0.229"`（仅必要 features）；`serde_json = "=1.0.151"` |
| Frontend | 本地静态 HTML/CSS/JS；不使用 npm、pnpm、yarn、Node package、dev server 或 localhost；`app.withGlobalTauri=true` 后只从 `window.__TAURI__.core.invoke` 调用三项冻结 IPC |
| OS 前置 | 只允许复用已存在的 Xcode／Command Line Tools；若缺失或需更新，停止，不执行系统级安装 |

版本依据仅限官方 Rust release／installer、Tauri release／documentation 和 crates.io 官方 registry metadata；不得把搜索摘要或第三方教程作为安装源。

### 唯一允许的网络来源与写入路径

- Rust bootstrap：`https://sh.rustup.rs` 与其官方分发 `https://static.rust-lang.org`。
- Cargo sparse registry：`https://index.crates.io`；crate 下载：`https://static.crates.io`；metadata：`https://crates.io`。
- 不允许 Git dependency、GitHub release asset、第三方 CDN、镜像、npm registry、任意 dev server、遥测、updater 或 app runtime 网络。
- 允许写入：`/Users/xxe/.rustup`、`/Users/xxe/.cargo`、`lifeos/engineering/LIFEOS-P3-104/`，以及执行时新建的固定 `/private/tmp/lifeos-p3-104-*` 测试夹具。
- `CARGO_TARGET_DIR`、下载脚本、bootstrap 日志和任务专用临时物必须位于 `lifeos/engineering/LIFEOS-P3-104/.tooling/`；不得写入其他用户目录、系统目录或历史工程目录。
- Rust 安装脚本不得直接 pipe 到 shell：先保存到 task-local `.tooling/bootstrap/`，记录最终 URL、SHA-256 与时间，再以 `--profile minimal --default-toolchain 1.98.0 --no-modify-path -y` 执行。重定向若离开允许域名立即停止。
- 必须显式设置 `RUSTUP_HOME=/Users/xxe/.rustup`、`CARGO_HOME=/Users/xxe/.cargo`、`CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse` 和 task-local `CARGO_TARGET_DIR`；不得修改 shell profile 或系统 PATH。

### Lock 与网络停止程序性规则

1. 任务卡投递后，专项会话只可在一次受控 bootstrap 阶段联网：安装精确 Rust/Tauri CLI、创建 P3-104 工程和解析冻结的直接依赖。
2. 首次成功解析必须生成并保存 `Cargo.lock`；立即记录其 SHA-256、全部 package name/version/source/checksum 和工具链版本。该首次记录即成为本轮程序性 lock freeze。
3. 从该点起禁止 `cargo update`、新增依赖、改 source 或重新解析；任何 `Cargo.lock` hash 漂移均为 P0 停止条件，除非回到 PM 新建 ABF 版本。
4. bootstrap 完成后必须设置 `CARGO_NET_OFFLINE=true`，并使用 `--locked` 完成 clean debug build、测试、runner 和实际 app Evidence；同时证明无网络连接、无 localhost、无远程 asset。
5. 若官方源不可用、版本不可获得、lock 不能离线复现、安装需要系统级权限／额外域名／额外包管理器，结论为 Blocked，不得替换版本或来源。

## 本轮唯一用户结果

创建一个真实可运行的本地桌面候选：三页 UI 通过三项窄 IPC 调用 backend，在全新 task-local SQLite 与固定非敏感夹具上完成捕获、幂等、today、重启、失败关闭和身份展示；renderer 无直接文件／DB／路径／网络能力。

明确不包括：retained pilot、真实个人内容、生产安装、release 签名／分发、风险关闭、资产／Schema/API 冻结、工程基线恢复或 Stage 4。

## 固定只读输入

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-091/default-recovery.html` | `e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b` |
| `lifeos/engineering/LIFEOS-P3-091/no-reliable-suggestion.html` | `e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793` |
| `lifeos/engineering/LIFEOS-P3-091/restricted-offline.html` | `b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e` |
| `lifeos/engineering/LIFEOS-P3-091/app.js` | `a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac` |
| `lifeos/engineering/LIFEOS-P3-091/styles.css` | `35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91` |
| `lifeos/engineering/LIFEOS-P3-091/evidence/rework/attempt-2/MANIFEST.md` | `5dd7e82804dd9c60fcc2ad378d7fa80393a1d767586c6aff7673b09c4e6bef6e` |
| `lifeos/reviews/LIFEOS-P3-092_pm_review.md` | `bd2a6bf0dddc5b4b8b59208bc08dd8eb0307d2e77628b9eefdc6e3b175ce2831` |
| `lifeos/deliverables/LIFEOS-P3-093_three_frozen_today_pages_controlled_ui_closure_and_next_capability_decision_package.md` | `52496a8e37a3e865c2968f9f66de05fa092f2dabae15325d263e084e90124687` |
| `lifeos/reviews/LIFEOS-P3-093_pm_review.md` | `15d5e91e52a30e2c782bd61fe54779e3d5d98e73c166521b0b935c096467f9ae` |
| `lifeos/engineering/LIFEOS-P3-097/src/local_capture.py` | `1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453` |
| `lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py` | `ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659` |
| `lifeos/spikes/P2-015-tauri-ipc-boundary/equivalent_capability_contract.json` | `ce5d918fa5afc7cc016d1df7b2f5c863aade3b1d6eba2b5372bf6466763ff36b` |
| `lifeos/reviews/LIFEOS-P3-103_pm_review.md` | `ec649e224bcba7e3d4a5d92f98ed8b9d79f5d0ac0b41ecc05d1ca3311793f07e` |
| `lifeos/reviews/LIFEOS-P3-103/pm_evidence/initial/MANIFEST.md` | `cb099df64da3b87284e88e889bf7bd739d6118d6433a119dcad1972cf270d482` |

专项执行前与提交前必须复算；任何漂移必须停止并报告，不得静默更新。

## 引用的 L1

- L1-1 数据主权；L1-2 内容身份；L1-3 生命周期完整；L1-4 失败关闭；L1-5 用户控制；L1-6 审计可信；L1-7 Evidence 诚实；L1-8 历史保全；L1-9 授权不漂移；L1-10 可复核性。

## 冻结不变量

| ID | 不变量 | 级别 | 通过条件 |
|---|---|---|---|
| ABF-I-01 | 工具链、依赖与网络供应链固定 | P0 | 仅上述版本／官方源／允许路径；程序性 lock freeze 后 hash 不变且全流程离线可复跑 |
| ABF-I-02 | 三页设计语义不回退 | P0 | 三页均保留身份、AI 关闭、离线、响应式、键盘和失败披露合同 |
| ABF-I-03 | Renderer 零直接 capability | P0 | 无 filesystem/raw DB/path/shell/process/network；CSP 无远程源 |
| ABF-I-04 | IPC 窄 allowlist | P0 | 只有 `capture_record`、`get_today`、`runtime_status`；unknown 默认拒绝 |
| ABF-I-05 | Backend 独占 task-local DB | P0 | renderer 不传路径；仅新建固定非敏感 DB；retained pilot 零访问 |
| ABF-I-06 | capture 生命周期准确 | P0 | saved、repeat、conflict、restart today 与 audit/source/identity 一致 |
| ABF-I-07 | 失败原子与状态诚实 | P0 | 失败不改 DB/UI 成功态/哨兵，无 half state 或假成功 |
| ABF-I-08 | 三页 runtime 状态一致 | P0 | 导航／刷新／关闭重开后均由 backend 权威状态驱动，不靠假内存成功 |
| ABF-I-09 | clear／delete／export 与外部能力关闭 | P0 | 命令未注册、调用为 0；网络／Vault／模型／同步等关闭 |
| ABF-I-10 | 可访问性与视觉闭环 | P1 | 实际 app 中 Tab/Enter、focus、宽窄屏、reduced motion、三页动作逐项 Evidence |
| ABF-I-11 | Evidence 与历史完整 | P0 | runner、逐行结果、IPC trace、screenshots、hash、Manifest、历史 before/after 完整 |
| ABF-I-12 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 保持 Open；R-0051 不扩大；Not Frozen；Stage 4 未进入 |

## 冻结验收矩阵

| 行 ID | 实际动作 | 通过条件 |
|---|---|---|
| ABF-M-001 | 核验投递、Frozen ABF、精确工具链／来源／lock／离线 clean rebuild | I-01 全部成立；bootstrap 与离线阶段边界有 Evidence |
| ABF-M-002 | 构建并启动真实 Tauri debug app | app 真实启动；无 dev server／localhost／远程资源 |
| ABF-M-003 | 打开三页并实际导航 | 三页实际呈现且身份／边界文案正确 |
| ABF-M-004 | UI 明确确认固定非敏感 capture | backend 返回 saved；UI 只在返回后显示成功 |
| ABF-M-005 | UI 同 key 同文本重复 | idempotent repeat；capture 不增，audit 合法 |
| ABF-M-006 | UI 同 key 异文本与注入失败 | 明确 blocked；DB、UI、哨兵不变 |
| ABF-M-007 | 关闭 app 后重启并 `get_today` | 权威记录恢复；来源／身份正确；三页状态一致 |
| ABF-M-008 | unknown IPC、额外参数、路径／SQL／shell 注入 | 全部 schema gate 前拒绝；无副作用 |
| ABF-M-009 | 静态／动态 capability、CSP 与 network 检查 | renderer 零直接 capability；network 0；unknown deny |
| ABF-M-010 | 实际 Tab／Enter、skip link、focus、宽窄屏、reduced motion | 每项独立动态／视觉 Evidence PASS |
| ABF-M-011 | clear/delete/export/Vault/model/sync 等关闭态 | 未注册、未调用、无可达入口 |
| ABF-M-012 | 前后 hash、隐私、临时清理、风险／阶段对账 | 历史不变；真实数据 0；残留 0；风险／阶段不变 |

## Pass 公式

- 12 项不变量、12 行矩阵及全部子项必须实际 PASS。
- P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0；不得用 N/A 隐藏实际 Tauri、IPC、动态 app、重启或视觉未实现。
- 真实 Tauri app 动态 Evidence、离线 clean rebuild、固定非敏感 SQLite、IPC fail-closed、历史保全和临时清理必须同时成立。
- 实际 Tauri app 未能构建／启动，或任何核心动作只能由 mock／等价 harness 证明，结论必须 Blocked 或 Not Implemented，不得 Pass。

## Rework 与新任务边界

- 本 ABF 不变时，P3-104 自身实现、测试、Evidence、配置和文案问题可包内整改；正式 Rework 上限 2。
- 需要接入 retained pilot／真实个人数据、扩大 IPC、增加 clear/export/Vault/network、修改架构方向、改变依赖版本／来源、风险关闭、冻结或 Stage 4 时必须新任务和新授权。
- 即使 P3-104 Pass，也不关闭 R-0040/R-0052，不冻结资产，不恢复工程基线，不进入 Stage 4。
