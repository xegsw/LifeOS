# LIFEOS-P3-108 Acceptance Basis Freeze｜组合候选全新隔离独立复评后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-108`
- ABF ID／版本：`ABF-P3-108-v1`
- 生效决策：D-0438
- 创建与冻结时间：2026-08-24 09:07:44 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 本轮唯一用户结果

由一个未参与 P3-104、P3-106、P3-107 工程执行、评审或 PM 验收的全新隔离 Codex 会话，对当前固定 P3-106 高保真三页 Tauri candidate 与 P3-104 runtime 安全底座完成一次可达、独立、可复核的组合复评：实际 app 的视觉、响应式、生命周期、路径、IPC、失败关闭、Evidence 与清理须同时满足合同。

本 ABF 不冻结产品需求、品牌／生产视觉系统、Schema/API、runtime 架构、工程基线、风险、发布资产、正式 MVP 或 Stage 4。

明确非范围：修改候选；真实个人数据／DB／路径或 retained pilot；clear/delete/export；Vault；模型；网络／云／第三方；同步／多设备；L3；外部用户；签名／发布；风险关闭／重开；系统显示设置修改。

## 授权和能力边界

- 用户授权事实：用户已采纳 P3-107 关闭结论，授权精确清理其三条残留，并授权创建本后继任务与新 ABF。
- 允许写入：`lifeos/reviews/LIFEOS-P3-108/`、`lifeos/deliverables/LIFEOS-P3-108_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_successor.md` 以及下列精确 `/private/tmp` 合同路径。
- 允许数据：固定、显著非敏感短文本、全新 task-local SQLite、HTML、哨兵、日志和截图；真实内容为 0。
- 允许入口：当前固定 P3-106 Tauri debug candidate 的 allowlist 构建副本；仅既有 `capture_record`、`get_today`、`runtime_status` 三项 IPC。
- 允许工具：现有 Rust 1.98.0、Cargo、Tauri CLI 2.11.4、锁定缓存、正常本地 GUI app 控制与截图；全程 `CARGO_NET_OFFLINE=true`、`--locked`。
- 严格只读：P3-104 至 P3-107 全部工程／Evidence／Review／交付物；三张冻结 Stitch；项目账本；retained pilot；既有 `/private/tmp/lifeos-p3-104-rework-static-results.json`。
- 禁止：联网、localhost、dev server、npm／新依赖、远程 asset、generic file/path/DB/shell/process/network capability、额外 IPC、真实数据、外部目标、系统显示修改。

## 精确临时路径与构建副本合同

- 工作副本：`^/private/tmp/lifeos-p3-108-review-work-[a-z0-9-]+$`。
- actual-app 夹具：`^/private/tmp/lifeos-p3-104-p3-108-review-(nominal|repeat|conflict|failure|reopen|dangling-final|dangling-journal|dangling-wal|dangling-shm|path|link|hardlink|tamper|a11y|narrow)-[a-z0-9-]+$`。
- 不可变 Rust unit tests 仅允许源码既有十类 PID 路径；执行前静态枚举并与 P3-106 ABF 合同核对。
- 每个路径创建前必须 `lstat` 缺失且祖先无链接；仅清理本轮台账精确路径，禁止 glob、find 或 broad prefix 清理。
- 工作副本必须从空目录按正向 allowlist 复制，且只允许：`.gitignore`、`Cargo.lock`、`Cargo.toml`、`README.md`、`build.rs`、`capabilities/`、`icons/`、`rust-toolchain.toml`、`src/`、`tauri.conf.json`、`ui/`。
- 必须排除且不得复制：`evidence/`、`scripts/`、`tests/`、`write_path_inventory.json`、`target/`、任何 Review／delivery、任何 runner／tools、缓存与隐藏构建状态。复制后必须先做路径 inventory 负门，发现任一禁项立即非零停止并清理。
- 旧 P3-107 三条路径必须保持缺失；旧 `rework-static-results.json` 只允许 `lstat` metadata 前后核对，不读取内容、hash、复制、覆盖或删除。

## 固定候选与当前快照

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-106/Cargo.lock` | `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1` |
| `lifeos/engineering/LIFEOS-P3-106/Cargo.toml` | `9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e` |
| `lifeos/engineering/LIFEOS-P3-106/src/runtime.rs` | `0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529` |
| `lifeos/engineering/LIFEOS-P3-106/src/main.rs` | `4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c` |
| `lifeos/engineering/LIFEOS-P3-106/capabilities/main.json` | `ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b` |
| `lifeos/engineering/LIFEOS-P3-106/tauri.conf.json` | `d44e1e03ade7ecc5dc75f5431295de78735ccf0596a421eae0f553411294e0f0` |
| `lifeos/engineering/LIFEOS-P3-106/ui/default-recovery.html` | `4a6464236b03ad5ffee1d50268169558320ca90484fe646933ff19c2497a5d56` |
| `lifeos/engineering/LIFEOS-P3-106/ui/no-reliable-suggestion.html` | `1fdd0129ffa056fd64a08e0c6227cdf84b90cc8e964ff811dde2efabfaa85ce2` |
| `lifeos/engineering/LIFEOS-P3-106/ui/restricted-offline.html` | `fa918f044fa9cbb4f3eafcb117af97bc039c5bbeb075ada2e91f9da34eecd27d` |
| `lifeos/engineering/LIFEOS-P3-106/ui/app.js` | `62d6685c8911efb5ccaabadde350e267cb0ce58b829abbeca0580ff7025a6507` |
| `lifeos/engineering/LIFEOS-P3-106/ui/styles.css` | `5b93977e863bd33a6f505e585080cdf85a547c08cee1bca9c7fa05008d26d50d` |
| `lifeos/engineering/LIFEOS-P3-106/evidence/rework-1/MANIFEST.md` | `7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe` |
| `lifeos/reviews/LIFEOS-P3-106_pm_review.md` | `97b1ad439729155588b3fbcc134f1a55144273976041f80e15443aa53c1e875f` |
| `lifeos/reviews/LIFEOS-P3-106/pm_evidence/rework-1/MANIFEST.md` | `a4a8a56e31703c7636f7b3a10a8d8e55ffc2a910ad5ac2187b981681a0946b38` |
| `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md` | `8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1` |
| `lifeos/reviews/LIFEOS-P3-104_pm_review.md` | `8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795` |
| `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md` | `e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4` |
| `lifeos/reviews/LIFEOS-P3-107_pm_review.md` | `4b87f341bc673409c37c8a022944e087757db1c4195cb432154849a809cb667d` |
| `lifeos/reviews/LIFEOS-P3-107/evidence/MANIFEST.md` | `206bb4cc47593475b2089b092e58f0264008cd93e12acbc2fbaa78be2475b105` |
| `lifeos/reviews/LIFEOS-P3-107/pm_evidence/resume-1/MANIFEST.md` | `c2a244fb3b721e3f945134aaab7b53834abfca28a4a6551fb93b1e8b95534a77` |
| `lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md` | `370c88454c809369f80e53f993702e9e61577d623b2a7c10cab61ab44c944b1b` |

P3-106 的 lock、Cargo、runtime、main 与 capability 必须与 P3-104 对应文件字节相等。

## 历史 Manifest 的时间限定验证规则

- P3-106 rework-1 Engineering Manifest：按当前树逐项完整复算，要求 325/325 匹配、无 missing／extra／self-reference。
- P3-104 attempt-1 Engineering Manifest：Manifest 文件本身必须匹配上表 hash；其条目按当前树复算时，除下列唯一时间限定例外外均须匹配。
- 唯一时间限定例外：该 Manifest 记录 `lifeos/reviews/LIFEOS-P3-104_pm_review.md` 的生成时 hash `da83f2adbe4aff8449d153c9eb32a6000a2b9dce54c24a218ab4e89b2b0d8aba`；当前 PM Review 已在 Manifest 核验后完成最终写入，其当前权威 hash 为上表 `8d888…`。本轮必须同时验证“Manifest 中记录值仍为 `da83…`”和“当前文件为 `8d888…`”，并标记 `PASS_TIME_QUALIFIED`，不得标 bad，也不得修改任一历史文件。
- 任何第二个不匹配、例外路径／旧 hash／当前 hash不精确一致，均为真实失败，不得类推豁免。

## 引用的 L1 长期原则

L1-1 数据主权、L1-2 内容身份、L1-3 生命周期完整、L1-4 失败关闭、L1-5 用户控制、L1-6 审计可信、L1-7 Evidence 诚实、L1-8 历史保全、L1-9 授权不漂移、L1-10 可复核性全部适用。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 独立性真实 | P0 | 全新会话；先冻结新测试设计；不复制／导入／执行提交 runner、tools 或 Evidence | Rework／Blocked |
| ABF-I-02 | 固定身份与时间语义 | P0 | 当前快照全匹配；历史 Manifest 仅唯一例外为 `PASS_TIME_QUALIFIED` | Blocked／Rework |
| ABF-I-03 | allowlist clean build | P0 | 空副本仅含正向 allowlist；禁项 0；locked test/build/bundle 成功；network 0 | Rework |
| ABF-I-04 | 路径授权完整 | P0 | 全部写路径匹配 allowlist；旧路径保持缺失／只读 | Rework |
| ABF-I-05 | Renderer／IPC 最小权限 | P0 | 仅三项 IPC，无 generic capability | Rework |
| ABF-I-06 | 三态高保真结构 | P1 | 独立逐态目视比较通过，无截图充当 UI | Rework |
| ABF-I-07 | 应用适配屏幕 | P1 | 原工作区与 700×760 下关键内容和动作可达，不改系统显示 | Rework |
| ABF-I-08 | 内容身份与关闭态诚实 | P0 | 固定演示／原文／系统／AI／来源可辨；未实现控件零副作用 | Rework |
| ABF-I-09 | 生命周期与审计 | P0 | saved、repeat、conflict、failure、refresh、close/reopen 独立成立 | Rework |
| ABF-I-10 | 路径／类型／sidecar fail-closed | P0 | 全部负向夹具在变更前拒绝 | Rework |
| ABF-I-11 | 可访问性与用户控制 | P1 | 实际 Tab／Enter／skip／focus／reduced-motion 成立 | Rework |
| ABF-I-12 | Evidence 诚实与完整 | P0 | 每行独立 Evidence；复制负门、缺行／FAIL／泄密负门真实非零 | Rework |
| ABF-I-13 | 历史保全与精确清理 | P0 | 历史不变；P3-108 台账残留 0；P3-107 旧路径仍缺失 | Rework |
| ABF-I-14 | 风险／冻结／阶段不漂移 | P0 | 风险不变；Not Frozen；Stage 4 未进入 | Rework |

## 冻结验收矩阵

| 行 ID | 独立操作 | 预期结果 | Evidence |
|---|---|---|---|
| ABF-M-001 | 核对授权、模型、会话、ABF 和当前快照 | 全匹配、零歧义 | authorization + hashes |
| ABF-M-002 | 读取提交 runner 前冻结新测试设计 | design hash 与时间顺序可证 | test-design |
| ABF-M-003 | 按时间限定规则复算两层 Manifest | P3-106 325/325；P3-104 仅唯一 `PASS_TIME_QUALIFIED` | manifest-verification |
| ABF-M-004 | 正向 allowlist 复制并执行禁项负门 | 禁止目录／runner／Evidence 0 | copy-inventory |
| ABF-M-005 | 空 target 离线 locked test/build/bundle | 全部退出 0，network 0 | build logs |
| ABF-M-006 | 静态反查 runtime、IPC、capability、路径、依赖 | provenance 相等，仅三 IPC | static results |
| ABF-M-007 | 独立比较三张 1280×1024 Evidence 与 Stitch | 三态共享骨架和独立锚点成立 | visual review |
| ABF-M-008 | 原显示环境三态与 700×760 实际行为 | 可滚动、无遮挡、关键动作可达 | responsive evidence |
| ABF-M-009 | actual-app 首次 capture | commit 后才成功，DB/audit/sentinel 一致 | lifecycle |
| ABF-M-010 | repeat、conflict、注入失败 | 幂等／冲突／原子失败正确 | negative lifecycle |
| ABF-M-011 | refresh、三页往返、关闭重开 | backend 权威状态恢复 | restart evidence |
| ABF-M-012 | 未实现控件、unknown IPC、额外字段 | 明确拒绝，零副作用 | denied matrix |
| ABF-M-013 | 路径、链接、hardlink、类型、外部路径 | 变更前 fail-closed | boundary matrix |
| ABF-M-014 | dangling 四类与 content/schema tamper | 各自独立 fail-closed | negative matrix |
| ABF-M-015 | 实际 a11y、隐私／网络／截图复用扫描 | 用户控制成立；remote／真实数据／网络为 0 | a11y + scans |
| ABF-M-016 | 精确清理、历史复算、最终负门 | P3-108 残留 0；旧路径仍缺失；历史不变 | cleanup + verifier |

## Evidence 合同

- Review：`lifeos/reviews/LIFEOS-P3-108/independent_review.md`；Evidence：`lifeos/reviews/LIFEOS-P3-108/evidence/`；不得创建工程目录。
- 必须保存新测试设计、独立 runner、16 行结构化结果、唯一 ID、copy inventory、Manifest 时间语义结果、clean build、actual-app 动态／负向／视觉／a11y、before/after、scan、cleanup、final verifier、复跑命令和非自指 Manifest。
- 固定测试设计后可只读提交源码作反查；不得复制、导入或执行 P3-104/P3-106/P3-107 runner、tests、tools、Evidence。
- 每项动态动作须有前置、操作、可观察结果、结构化 ID、视觉／日志路径与 SHA-256；静态或旧 Evidence 不得替代实际动作。
- 临时夹具不得进入 Evidence；结束时只按台账精确清理。

## 计数与 Pass 公式

- P0：独立性、数据／路径／授权、runtime／IPC、生命周期／失败关闭、Evidence 真实性、历史保全或网络越界。
- P1：高保真、响应式、可访问性或关键用户控制失败。
- P2：非阻断清洁项；本轮 Pass 仍要求 0。
- Unknown：关键 hash、视觉、动作、状态或清理不可复核。
- Not Implemented：任一矩阵行、actual-app 动作、负向夹具或 Evidence 缺失。
- Pass：I-01 至 I-14、M-001 至 M-016 与全部子动作独立通过；P0/P1/P2/Unknown/Not Implemented 全 0；历史不变；P3-108 残留 0；P3-107 旧残留仍缺失。
- N/A：仅系统不暴露的装饰性指标可说明；独立性、copy 负门、视觉、actual app、生命周期、路径、IPC、失败关闭、a11y、清理和 Manifest 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限 2；当前 0。
- 同任务 Rework：仅 P3-108 自身 runner／Evidence／Manifest／文案缺陷，且本 ABF、独立性、候选、目录、能力与授权不变。
- 必须新建任务：实质改变 ABF、用户结果、runtime／IPC／依赖、路径、真实数据、视觉权威、风险／冻结／阶段，或两轮正式 Rework 用尽。
- Blocked：正确配置或正常本地 actual-app 控制在授权内不可用、固定输入来源不明漂移、锁定工具链无法离线运行；不得以旧动态 Evidence 替代。

## 启动前质疑窗口

- 执行方在复制、构建、夹具或 app 操作前核对 ABF ID/hash、模型、独立性、固定输入、时间限定规则、copy allowlist 与写路径。
- 必须先写入并 hash 新测试设计，再读取提交 runner／结构化结论。
- 有歧义立即停止；不得修改 ABF。专项会话开始后需要实质修改本 ABF时关闭 P3-108 并新建任务。
