# LIFEOS-P3-110 Acceptance Basis Freeze｜组合候选独立复评路径授权后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-110`
- ABF ID／版本：`ABF-P3-110-v1`
- 生效决策：`D-0445`
- 冻结时间：2026-08-24（Asia/Shanghai）
- ABF 文件 SHA-256：冻结后记录在任务卡与决策日志；本文件不自指。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 单一结果：由未参与 P3-104 至 P3-109 工程、评审或 PM 验收的全新独立会话，只读判断固定 P3-106 高保真 Tauri candidate 与 P3-104 runtime 安全底座的组合候选，是否在固定非敏感、离线、task-local 边界同时满足视觉、响应式、可访问性、本地生命周期、IPC／路径失败关闭与语义级 Evidence 可复核性。
- 治理修正：仅修复 P3-109 ABF 遗漏候选既有 unit-test 写路径的授权冲突；不降低或改变 P3-109 的用户结果、候选、视觉、数据、IPC、native geometry、verifier、风险或阶段标准。
- 明确非范围：候选修改；retained pilot／真实个人数据；网络／云／第三方；系统显示缩放或偏好修改；新 IPC／依赖／capability；导出、同步、多设备、L3、外部用户；风险关闭／重开；冻结、基线恢复或 Stage 4。

## 授权和能力边界

### 项目写入

- 仅允许：
  - `lifeos/deliverables/LIFEOS-P3-110_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_path_authorization_successor.md`
  - `lifeos/reviews/LIFEOS-P3-110/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-110/evidence/`
- 不得创建 `lifeos/engineering/LIFEOS-P3-110/`；候选、历史、ABF 和账本全部只读。

### 精确 P3-110 临时路径

- 工作副本：`/private/tmp/lifeos-p3-110-review-work-v1`
- actual-app／负向夹具：`/private/tmp/lifeos-p3-104-p3-110-review-{nominal,reopen,failure,dangling-final,dangling-journal,dangling-wal,dangling-shm,path,link,hardlink,tamper,a11y,narrow}-v1`。花括号仅代表这 13 个逐字枚举值。

### 候选既有 unit-test 路径授权

仅 `cargo test --locked` 运行期间允许候选不可变 tests 创建、读取、修改并清理以下三条正则匹配的直接 `/private/tmp` 子路径：

1. `^/private/tmp/lifeos-p3-104-unit-(lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+$`
2. `^/private/tmp/lifeos-p3-104-unit-link-target-[0-9]+$`
3. `^/private/tmp/lifeos-p3-104-unit-link-[0-9]+$`

- 正则来源：`lifeos/engineering/LIFEOS-P3-106/write_path_inventory.json`，SHA-256 `4ac147ce251dd10632ec9b639c31c6de0445af3c4c21597e334b9abdc573fc56`。
- 执行前：只允许枚举 `/private/tmp` 的直接子项名称、立即丢弃不匹配名称，不读取非匹配项 metadata／内容；三条正则的匹配集合必须为空。若存在任何预存匹配项，停止为 Blocked，不删除、不归因。
- 执行中：记录 cargo/test 主进程与测试进程 PID、开始／结束时间以及新出现的精确匹配路径；禁止 broad prefix 或未匹配路径。
- 执行后：候选 tests 应自行清理。若仍有本轮新出现且可由 PID／时间／台账归属的精确匹配路径，只允许逐路径清理这些本轮路径；不得删除执行前存在项或使用 wildcard／broad cleanup。最终三条正则匹配集合必须为空。

### 允许数据、入口与工具

- 固定短 ASCII 非敏感文本／key、全新 SQLite、哨兵和测试文件；禁止任何真实个人内容。
- 允许 actual unsigned debug Tauri app、`capture_record`／`get_today`／`runtime_status`、锁定离线 Rust／Cargo／Tauri、独立 runner、Computer Use。
- 允许普通 GUI resize LifeOS 窗口；允许 AX／CGWindow／System Events 只读查询同一 app 窗口 native `position`／`size`／`bounds`。禁止设置显示缩放、分辨率或辅助功能偏好。
- 禁止网络、安装／更新、retained pilot、任意外部文件内容、raw SQL／shell／process IPC、外部 URL、真实删除或其他外部目标。
- 投递前额外用户确认：None。用户已采纳 P3-109 关闭结论并授权创建 P3-110。向合格新会话投递任务卡路径即启动本 ABF。

## 固定输入与历史保全

| 输入 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md` | `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe` |
| `lifeos/engineering/LIFEOS-P3-106/write_path_inventory.json` | `4ac147ce251dd10632ec9b639c31c6de0445af3c4c21597e334b9abdc573fc56` |
| `lifeos/reviews/LIFEOS-P3-109_pm_review.md` | `9fa1c820ab030461a0c623fbf95d1a8d656d749dae1ccec65246891d5128e5a0` |
| `lifeos/reviews/LIFEOS-P3-109/pm_evidence/initial/MANIFEST.md` | `c5565437f2d7c38559192ae37136fc1c319489c05193e2198af7cb09d0595e8f` |

固定 Stitch 与 P3-106 actual-app 图：

| 状态 | Stitch 路径／SHA-256 | P3-106 1280×1024 路径／SHA-256 |
|---|---|---|
| 默认恢复 | `lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg` / `7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1` | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m004-default-1280x1024.png` / `d64921229aab0bbae1fdca0c29cf107e8e11dd7aa7ade732f5a71f3d2c024c5f` |
| 无可靠建议 | `lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg` / `55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697` | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m005-no-suggestion-1280x1024.png` / `373c16c24cb334f34de6c3d4cddb8818905814efec75e83a9fcf09a7b1187f1b` |
| 受限／离线 | `lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg` / `9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661` | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m006-restricted-1280x1024.png` / `05fa817ab31c874e8505c5c4091f6a438dab56f86b51930003bb1a68d5442da6` |

- `fixed-inputs.json` 必须逐项包含本节全部 10 个输入（4 个文档／Manifest + 6 张图）的路径、预期 hash、当前 hash 和匹配结果；缺任一项时 M-001 必须 FAIL／Not Implemented，不得标 PASS。
- P3-104 至 P3-109 的任务卡、ABF、交付物、Review、Evidence／PM Evidence 和候选全部只读；P3-109 runner／结果只能在新测试设计冻结后阅读，永不复制、导入或执行。

## 引用的 L1

L1-1 至 L1-10 全部适用，重点为数据主权、生命周期完整、失败关闭、用户控制、审计可信、Evidence 诚实、历史保全、授权不漂移和可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 |
|---|---|---|---|
| ABF-I-01 | 独立性与读序 | P0 | 全新会话；测试设计／hash 先于 P3-109 runner／结果阅读；旧 runner 不执行 |
| ABF-I-02 | 固定身份完整 | P0 | 本 ABF 10 项固定输入逐项记录并匹配；历史零写入 |
| ABF-I-03 | clean test/build/bundle | P0 | 正向 allowlist 副本；离线 locked test/build/bundle 全通过；network 0 |
| ABF-I-04 | 路径授权完整 | P0 | P3-110 枚举路径和三条 unit regex 之外写入 0；unit baseline／PID／新路径／清理闭环 |
| ABF-I-05 | runtime／IPC 最小权限 | P0 | provenance 不漂移；仅三项 strict IPC；capability 空；未知／多余字段拒绝 |
| ABF-I-06 | 固定三态视觉 | P1 | 逐态比较固定六张图并给出骨架、层级、锚点、身份、状态差异结论 |
| ABF-I-07 | 当前响应式 | P1 | actual app 原窗口与 native outer frame 精确 700×760；三态可滚动、无遮挡、关键动作可达 |
| ABF-I-08 | 内容身份／关闭态 | P0 | 用户原文、本地来源、系统、AI 未启用可辨；未实现控件零副作用 |
| ABF-I-09 | 生命周期／审计 | P0 | saved、repeat、conflict、failure、refresh、navigation、close/reopen 独立成立 |
| ABF-I-10 | 路径／类型／sidecar | P0 | 逐类新夹具在任何变更前 fail-closed，哨兵和状态不变 |
| ABF-I-11 | a11y／用户控制 | P1 | 实际 Tab／Enter／skip／focus；当前 reduced-motion 只读值与 app 披露一致 |
| ABF-I-12 | 语义 verifier | P0 | 从 raw Evidence 重算，不信任 status/pass；六类 mutation 全部非零 |
| ABF-I-13 | Manifest／清理 | P0 | payload hash、P3-110 路径和 unit regex 最终残留 0；顶层 Manifest 可由 PM复算 |
| ABF-I-14 | 风险／冻结／阶段 | P0 | R-0040/R-0052 不变，R-0051 原有限关闭；Not Frozen；Stage 4 未进入 |

## 冻结验收矩阵

| 行 ID | 独立操作 | 预期结果 | Evidence |
|---|---|---|---|
| ABF-M-001 | 授权、模型、会话、ABF 与全部 10 项固定输入 | 全匹配、零遗漏 | authorization、fixed-inputs |
| ABF-M-002 | 先冻结新测试设计，再记录旧 P3-109 阅读时间 | design hash 先行，旧 runner 未执行 | test-design、read-order |
| ABF-M-003 | 复算 P3-106 Manifest／runtime provenance 与 P3-109 历史 | 无未授权差异 | manifest-verification |
| ABF-M-004 | 正向 allowlist copy 与禁项 inventory | Evidence／runner／tests／tools 0 | copy-inventory |
| ABF-M-005 | unit baseline 空 → offline locked test/build/bundle → unit 清理闭环 | 命令全 0、network 0、越权路径 0、unit 残留 0 | build logs、unit-path-ledger |
| ABF-M-006 | 静态 runtime、IPC、capability、路径、依赖 | provenance 相等，仅三 IPC | static-results |
| ABF-M-007 | 固定三张 P3-106 1280×1024 图逐态对比 Stitch | 共享骨架及独立锚点成立 | visual/fixed-comparison.json |
| ABF-M-008 | current actual app 原窗口及 GUI resize 后 native 700×760 三态操作 | native outer width=700、height=760；内容／动作可达 | native geometry raw output、AX、截图、滚动 |
| ABF-M-009 | actual-app 首次 capture | commit 后才成功；DB／audit／sentinel 一致 | raw log、before/after |
| ABF-M-010 | repeat、conflict、注入失败 | 幂等／冲突／原子失败正确 | 独立结果、before/after |
| ABF-M-011 | refresh、三页往返、关闭重开 | backend 权威状态恢复 | app／process／DB Evidence |
| ABF-M-012 | 未实现控件、unknown IPC、额外字段 | disabled／拒绝，零副作用 | denied matrix、raw logs |
| ABF-M-013 | 目录、软链、硬链、类型、悬挂 final、外部路径 | 全部变更前拒绝；外部目标不创建 | boundary matrix、sentinel |
| ABF-M-014 | dangling journal/wal/shm、content/schema tamper | 各自独立 fail-closed | negative matrix、before/after |
| ABF-M-015 | Tab／Enter／skip／focus、current reduced-motion 披露、隐私／网络 scan | 用户控制成立，个人数据／网络 0 | a11y、系统只读值、scan |
| ABF-M-016 | raw semantic verifier、六类 mutation、payload hash、全部路径清理、顶层 Manifest | 真 payload 0；六类 mutation 非零；残留 0；Manifest 可复算 | verifier、mutation logs、cleanup、Manifest |

## Native geometry 与 Evidence verifier

- `700×760` 是 macOS native outer window frame 的整数 point size，不是截图像素、屏幕坐标或 CSS viewport。
- 必须保留只读查询源码／命令、原始输出、PID／bundle／window title、时间和解析结果。两种已授权只读 API 均不可用时，在任何通过声明前 Blocked。
- verifier 必须直接解析 raw logs、DB／fixture snapshots、geometry、cleanup、unit ledger 和 hashes；矩阵 `status/pass` 与 Markdown 结论不是通过输入。
- 六类 disposable mutation：缺文件、hash 改变、cleanup／unit 残留、负向退出码变 0、DB／audit 数量错误、geometry 非 700×760；全部必须使 verifier 非零。
- 使用 `PAYLOAD_MANIFEST.json` → semantic verifier → 顶层非自指 `MANIFEST.md`；PM 独立复算顶层 Manifest，禁止自引用伪验证。

## 计数、Pass 与退出

- P0：独立性、固定输入、授权／路径、runtime／IPC、生命周期／失败关闭、Evidence、历史或网络越界。
- P1：视觉、响应式、a11y 或关键用户控制失败。
- P2：非阻断清洁项；Pass 仍要求 0。
- Unknown：有 Evidence 但关键事实不可复核。
- Not Implemented：任一行、子动作、负测或必需 Evidence 未执行／缺失。
- Pass：I-01–I-14、M-001–M-016 与全部子动作通过；全部 10 项固定输入存在；unit baseline/ledger/cleanup 成立；真 payload verifier 0、六类 mutation 非零；P0/P1/P2/Unknown/Not Implemented 全 0；历史不变、全部临时残留 0、PM Manifest 复算一致。
- N/A：不得用于独立性、固定输入、unit test、视觉、native geometry、actual app、生命周期、IPC／路径／失败关闭、a11y、verifier、清理或 Manifest。
- 正式 Rework 上限：2；当前 0。仅 P3-110 自身 runner／Evidence／Review 缺陷且 ABF 不变时可同任务 Rework。
- 必须新任务：ABF、候选、unit regex、目录、数据、能力、授权、视觉、native geometry、风险、冻结、基线、阶段变化，或两轮用尽／独立性污染。
- Blocked：正确模型、离线工具、actual app、两种 native geometry 查询不可用；固定输入漂移；unit-test 执行前正则集合非空；路径归属无法证明。Blocked 不得清理预存项或借旧 Evidence 通过。

## 启动前质疑窗口

- 在任何 copy、build、test、fixture、旧 runner 阅读或 app 操作前，逐项核对 10 个固定输入、14 个 P3-110 路径、三条 unit regex、执行前空集合和清理归属规则。
- 有歧义立即停止；仅可在执行开始前由 PM 修订并重新冻结。
- 最终冻结版本：`ABF-P3-110-v1`。专项开始后不得修改；如需修改，关闭并新建任务。
