# LIFEOS-P3-109 Acceptance Basis Freeze｜P3-104 + P3-106 组合候选全新隔离独立复评最终后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-109`
- ABF ID／版本：`ABF-P3-109-v1`
- 生效决策：`D-0443`
- 冻结时间：2026-08-24（Asia/Shanghai）
- ABF 文件 SHA-256：由 PM 冻结后记录在任务卡与 `DECISION_LOG.md`；本文件不自指。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 要完成的单一结果：由未参与 P3-104、P3-106、P3-107、P3-108 工程／评审／PM 验收的全新独立会话，只读判断固定 P3-106 高保真 Tauri candidate 与 P3-104 runtime 安全底座的组合候选，是否在固定非敏感、纯本地、离线、task-local 边界同时满足视觉、响应式、可访问性、本地生命周期、IPC／路径失败关闭与 Evidence 可复核性。
- 明确不冻结的产品需求：本任务不冻结 UI、runtime、Schema/API、工程基线、风险或阶段；Pass 也只代表固定候选在本 ABF 边界取得独立复评通过。
- 明确非范围：候选修复；retained pilot；真实个人文本／DB／文件；系统显示缩放或偏好修改；网络／云／第三方；新 IPC／依赖／capability；导出、同步、多设备、L3、外部用户；风险关闭／重开；资产冻结、基线恢复或 Stage 4。

## 授权和能力边界

- 允许目录：只写 `lifeos/deliverables/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor.md`、`lifeos/reviews/LIFEOS-P3-109/independent_review.md`、`lifeos/reviews/LIFEOS-P3-109/evidence/`；只在下列精确 `/private/tmp` 路径创建／清理工作副本与夹具。
- 允许临时路径：`/private/tmp/lifeos-p3-109-review-work-v1`；以及 `/private/tmp/lifeos-p3-104-p3-109-review-{nominal,reopen,failure,dangling-final,dangling-journal,dangling-wal,dangling-shm,path,link,hardlink,tamper,a11y,narrow}-v1`。花括号仅表示上述 13 个逐字枚举名，不授权 broad prefix 或其他后缀。
- 允许数据与夹具：任务卡固定的短 ASCII 非敏感文本／key、全新 SQLite、哨兵和不可包含个人内容的测试文件；禁止读取 retained pilot 或任何既有个人文件内容。
- 允许入口／接口：实际 unsigned debug Tauri app；固定三项 `capture_record`、`get_today`、`runtime_status`；独立离线构建／runner；只读 macOS AX／CGWindow／System Events 窗口几何查询。
- 允许工具／环境：本地锁定 Rust／Cargo／Tauri、shell、Python 标准库、Computer Use；窗口几何只允许读 `position`／`size`／`bounds`、应用／窗口身份和时间，不允许设置窗口以外的系统显示参数。允许通过普通 GUI resize 将 LifeOS app 窗口调整到目标尺寸；不得改变显示缩放。
- 严格只读资产：P3-104、P3-106 候选与全部历史 Review／Evidence；P3-107、P3-108 全部资产；三张 Stitch 权威图；项目账本、风险与冻结文件。
- 禁止能力与外部目标：网络、安装／更新、真实数据、真实用户路径、任意文件读取／写入、raw SQL、shell／process IPC、外部 URL、系统偏好写入、显示缩放、删除历史资产。
- 投递前额外用户确认：None。用户已采纳 P3-108 关闭结论并授权创建全新后继独立复评任务。任务卡路径投递到合格的新会话即构成执行授权；任何越出本 ABF 的动作需新确认。

## 固定视觉与候选身份

### Stitch 权威图

| 状态 | 路径 | SHA-256 |
|---|---|---|
| 默认恢复 | `lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg` | `7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1` |
| 无可靠建议 | `lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg` | `55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697` |
| 受限／离线 | `lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg` | `9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661` |

### 固定 P3-106 1280×1024 actual-app Evidence

| 状态 | 路径 | SHA-256 |
|---|---|---|
| 默认恢复 | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m004-default-1280x1024.png` | `d64921229aab0bbae1fdca0c29cf107e8e11dd7aa7ade732f5a71f3d2c024c5f` |
| 无可靠建议 | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m005-no-suggestion-1280x1024.png` | `373c16c24cb334f34de6c3d4cddb8818905814efec75e83a9fcf09a7b1187f1b` |
| 受限／离线 | `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/m006-restricted-1280x1024.png` | `05fa817ab31c874e8505c5c4091f6a438dab56f86b51930003bb1a68d5442da6` |

- P3-106 权威 Manifest：`lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md`，SHA-256 `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe`。
- P3-108 关闭 PM Review：`lifeos/reviews/LIFEOS-P3-108_pm_review.md`，SHA-256 `db2c1b32d1be49fb91d37f75e3774d46a31510ac66cdd2a919b43662d1fa6be5`。
- P3-108 PM Evidence Manifest：`lifeos/reviews/LIFEOS-P3-108/pm_evidence/rework-1/MANIFEST.md`，SHA-256 `7e5221a5cec16b419e432ef59c9a3f9327f57e3192d08d9c6a9feca63efe9d9f`。

## 引用的 L1 长期原则

L1-1 数据主权、L1-2 内容身份、L1-3 生命周期完整、L1-4 失败关闭、L1-5 用户控制、L1-6 审计可信、L1-7 Evidence 诚实、L1-8 历史保全、L1-9 授权不漂移、L1-10 可复核性全部适用。PM 只能用具体条款、证据和严重级别裁决，不得新增普通标准。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 独立性与读序真实 | P0 | 全新会话；新测试设计及 hash 先于任何 P3-107/P3-108 runner／结果阅读；旧 runner 不复制、不导入、不执行 | Rework／Blocked |
| ABF-I-02 | 固定身份与历史保全 | P0 | 上述固定 hash、P3-106 Manifest 与任务列出的历史入口一致；历史零写入 | Blocked／Rework |
| ABF-I-03 | allowlist clean build | P0 | 空副本仅含候选正向 allowlist；Evidence／runner／tests／tools 0；离线 locked test/build/bundle 通过 | Rework |
| ABF-I-04 | 路径与数据授权 | P0 | 全部写入只命中逐字枚举路径；固定非敏感数据；外部目标 0 | Rework |
| ABF-I-05 | runtime／IPC 最小权限 | P0 | P3-104 provenance 不漂移；仅三项 strict IPC；capability 空；未知／多余字段拒绝 | Rework |
| ABF-I-06 | 固定三态视觉比较 | P1 | 独立评审者逐态比较本 ABF 固定的六张图，按骨架、层级、锚点、身份、状态差异逐项给出 PASS／FAIL；不得要求重新量测 1280 窗口 | Rework |
| ABF-I-07 | 当前应用适配屏幕 | P1 | 当前实际 app 原窗口与精确 700×760 窗口均由只读 native geometry 记录；三态可滚动、无遮挡、关键动作可达 | Rework／Blocked |
| ABF-I-08 | 内容身份与关闭态 | P0 | 用户原文／本地来源／系统／AI 未启用可辨；未实现控件零副作用 | Rework |
| ABF-I-09 | 生命周期与审计 | P0 | saved、repeat、conflict、failure、refresh、navigation、close/reopen 各自独立成立 | Rework |
| ABF-I-10 | 路径／类型／sidecar fail-closed | P0 | 逐类新夹具在任何 DB／文件变更前拒绝，哨兵和状态不变 | Rework |
| ABF-I-11 | 可访问性与用户控制 | P1 | 实际 Tab／Enter／skip／focus 成立；当前系统 reduced-motion 状态只读值与 app 披露一致；固定 P3-106 reduced-motion Evidence 独立复核 | Rework |
| ABF-I-12 | 语义级 Evidence verifier | P0 | verifier 从 raw evidence 重新计算断言，不接受 row/action 自报状态作为通过输入；mutation self-tests 全部使 verifier 非零 | Rework |
| ABF-I-13 | Manifest 与精确清理 | P0 | payload manifest 经 verifier 复算；顶层非自指 Manifest 完整；临时路径 0；PM 可独立复算 | Rework |
| ABF-I-14 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 不变，R-0051 原有限关闭不变；Not Frozen；Stage 4 未进入 | Rework |

## 冻结验收矩阵

每行必须有独立结构化结果和原始输入，不得从总状态批量映射。

| 行 ID | 入口／操作 | 冻结预期 | 必须 Evidence |
|---|---|---|---|
| ABF-M-001 | 核对任务、ABF、授权、模型、会话、固定 hash | 全匹配，独立性无歧义 | `authorization.json`、`fixed-inputs.json` |
| ABF-M-002 | 先冻结新测试设计，再记录读取旧 runner／结果的时间 | design hash 早于旧提交读取 | `read-order.json`、`test_design.md` |
| ABF-M-003 | 复算 P3-106 Manifest、P3-104 精确时间语义和 P3-108 只读入口 | 无未授权差异 | `manifest-verification.json` |
| ABF-M-004 | 正向 allowlist 复制，执行禁止项 inventory | 禁止目录／runner／Evidence／tools 0 | `copy-inventory.json` |
| ABF-M-005 | 空 target 离线 locked test/build/bundle | 全部退出 0，network 0 | build logs、`build-results.json` |
| ABF-M-006 | 独立静态反查 runtime、IPC、capability、路径、依赖 | provenance 相等，仅三 IPC | `static-results.json` |
| ABF-M-007 | 逐态比较本 ABF 固定 P3-106 1280×1024 图与 Stitch | 三态共享骨架、独立锚点、身份与状态差异逐项判定 | `visual/fixed-comparison.json`；至少 3 行、每行含观察与结论 |
| ABF-M-008 | 当前 actual app 原窗口和 GUI resize 后 700×760 三态操作 | native outer window size 精确为 700×760；关键内容／动作可达 | `responsive/native-window-geometry.json`、AX、截图、滚动动作 |
| ABF-M-009 | actual-app 首次 capture | commit 后才报告成功；DB／audit／sentinel 一致 | raw app log、before/after DB／fixture |
| ABF-M-010 | repeat、conflict、注入失败 | 幂等／冲突／原子失败正确，失败零副作用 | 三个独立结果和 before/after |
| ABF-M-011 | refresh、三页往返、关闭重开 | backend 权威状态恢复 | actual app 动作、进程与 DB Evidence |
| ABF-M-012 | 未实现控件、unknown IPC、额外字段 | 明确拒绝／disabled，零副作用 | denied matrix、raw logs、before/after |
| ABF-M-013 | 目录、软链、硬链、类型、悬挂 final、外部路径 | 全部变更前 fail-closed；外部目标不创建 | boundary matrix、stdout/stderr、sentinel |
| ABF-M-014 | dangling journal/wal/shm 与 content/schema tamper | 各自独立 fail-closed，状态不变 | negative matrix、raw logs、before/after |
| ABF-M-015 | 实际 Tab／Enter／skip／focus、current reduced-motion 披露、隐私／网络扫描 | 用户控制成立，remote／个人数据／网络 0 | a11y matrix、只读系统值、actual app 披露、scan |
| ABF-M-016 | 运行语义 verifier mutation tests、payload hash、精确清理、顶层 Manifest | 真实 payload 全通过；六类篡改均非零；残留 0；Manifest 可复算 | `verifier/semantic-result.json`、mutation logs、cleanup、Manifest |

## Native 窗口几何冻结口径

- `700×760` 指 macOS native outer window frame 的整数 point size：`width=700`、`height=760`，不是 CUA 缩放截图像素、屏幕坐标或 CSS viewport。
- 评审者先用普通 GUI resize 调整 LifeOS app 窗口，再只读查询同一 PID／bundle／window 的 native `position` 与 `size`。允许 AX API、CGWindow API 或 System Events 只读查询；必须保留查询源码／命令、原始输出、PID／bundle/window title、时间与解析结果。
- 禁止修改系统显示缩放、分辨率或辅助功能偏好。若两种已授权只读 native 查询均因权限／工具条件无法获得尺寸，必须在任何通过声明前停止为 Blocked；不得降格为视觉估计或 Unknown 后继续自称完成。

## Evidence 合同与语义 verifier

- 交付必须包含可运行独立 runner、逐行 raw evidence、before/after、原始日志／AX／截图、固定输入 hash、复跑命令、精确 cleanup 和非自指 Manifest。
- `PAYLOAD_MANIFEST.json` 覆盖除自身、`final-verifier.json`、顶层 `MANIFEST.md` 外的全部已冻结 payload。`final-verifier.json` 必须在 payload 不再变化后由 verifier 生成。
- verifier 必须直接解析 raw JSON／logs／DB snapshots／geometry／cleanup 和 payload hashes，重新计算每个条件；`status`、`pass`、Markdown 结论只能作为待核字段，不能作为通过依据。
- verifier 至少对 disposable index／fixture copy 执行六类 mutation self-test：缺必需文件、hash 改变、cleanup 路径存在、负向退出码被改为 0、DB／audit 数量不符、geometry 非 700×760。六类都必须使 verifier 非零且保留日志；不得修改权威 Evidence。
- 顶层 `MANIFEST.md` 在 final verifier 生成后覆盖目录内除自身外全部文件。由于非自指 Manifest 不能证明自身，专项须提供只读复算命令；PM 验收时独立复算顶层 Manifest。不得让 verifier 声称验证包含自身 hash 的循环结构。
- 初次 P3-109 Evidence 不得引用 P3-108 动态结果作为当前 PASS；P3-108 只用于反例设计和历史保全。固定 P3-106 视觉／reduced-motion Evidence 仅在本 ABF 明列的 M-007／M-015 范围作为冻结输入。

## 计数与 Pass 公式

- P0：独立性、授权／路径／数据、runtime／IPC、生命周期／失败关闭、Evidence 语义、历史保全或网络越界。
- P1：固定视觉、响应式、可访问性或关键用户控制失败。
- P2：非阻断清洁项；本任务 Pass 仍要求 0。
- Unknown：关键 hash、动作、状态或清理存在 Evidence 但无法复核。
- Not Implemented：任一矩阵行、子动作、负向夹具或必需 Evidence 未执行／缺失。
- Pass 公式：I-01 至 I-14、M-001 至 M-016 和所有子动作独立通过；语义 verifier 真实 payload 退出 0、六类 mutation 均非零；P0/P1/P2/Unknown/Not Implemented 全 0；历史不变；全部 P3-109 路径残留 0；顶层 Manifest 由 PM 独立复算一致。
- 允许的 N/A：仅无法适用于当前 OS 的装饰性指标；独立性、视觉比较、native geometry、actual app、生命周期、路径／IPC／失败关闭、a11y、语义 verifier、清理和 Manifest 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：仅 P3-109 自身 runner／Evidence／Review／Manifest 缺陷，且本 ABF、候选、目录、数据、能力、独立性和授权不变。
- 必须新建任务条件：达到两轮上限；需要修改本 ABF；改变候选、runtime／IPC／依赖、目录、数据、窗口口径、视觉权威、权限、风险、冻结、基线或阶段；Evidence／独立性污染无法只读保全。
- Blocked 条件：正确模型不可用；锁定工具链无法离线运行；正常 actual app 控制连续两次不可用；两种已授权 native 几何只读查询均不可用；固定输入来源不明漂移。Blocked 不得以旧动态 Evidence 替代。

## 候选基线与只读保全

- 候选输入：固定 P3-106 candidate 与上述 P3-106 Manifest；P3-104 runtime provenance 按 P3-108 已冻结的时间限定规则核对。
- 历史只读：P3-104 至 P3-108 全部任务卡、ABF、交付物、Review、Evidence 与 PM Evidence；三张 Stitch 权威图。
- 允许发生变化的文件：仅 P3-109 自己的交付物、独立 Review、Evidence 与本 ABF 枚举临时路径；专项不得修改 ABF 或项目账本。

## 启动前质疑窗口

- 执行方在任何复制、构建、夹具、旧 runner 阅读或 app 操作前，核对 ABF ID/hash、固定六张图、native geometry 定义、语义 verifier 输入／输出与精确路径。
- 有歧义立即停止并回报 PM；PM 仅能在执行开始前修订并重新冻结。
- 最终冻结版本：`ABF-P3-109-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
