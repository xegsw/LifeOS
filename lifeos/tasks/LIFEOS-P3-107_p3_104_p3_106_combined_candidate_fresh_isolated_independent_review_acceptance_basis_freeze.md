# LIFEOS-P3-107 Acceptance Basis Freeze｜P3-104 + P3-106 组合候选全新隔离独立复评

## 冻结信息

- 任务 ID：`LIFEOS-P3-107`
- ABF ID／版本：`ABF-P3-107-v1`
- 生效决策：D-0434
- 创建与冻结时间：2026-08-23 21:32:24 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 本轮唯一用户结果

由一个未参与 P3-104／P3-106 工程执行或 PM 验收的全新隔离 Codex 独立评审会话，对当前固定 P3-106 高保真三页 Tauri candidate 与其继承的 P3-104 runtime 安全底座做一次独立、可复核的组合判断：实际 app 的视觉、响应式、生命周期、路径、IPC、失败关闭、Evidence 和清理是否同时满足既有冻结合同，且没有因 UI 整合破坏 runtime 安全不变量。

明确不冻结：产品需求、品牌／生产视觉系统、Schema/API、runtime 架构、工程基线、风险状态、发布资产、Stage 4 或正式 MVP。

明确非范围：修改候选；真实个人数据／DB／路径或 retained pilot；clear/delete/export；Vault；模型；网络／云／第三方；同步／多设备；L3；外部用户；签名／发布；风险关闭／重开；系统显示缩放修改。

## 授权和能力边界

- 用户授权事实：用户已采纳 P3-106 PM Pass，并明确授权创建本全新隔离独立复评与 Frozen ABF。
- 允许写入：`lifeos/reviews/LIFEOS-P3-107/`、`lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md`，以及本 ABF 精确列明的全新 `/private/tmp` 路径。
- 允许数据：仅固定、显著非敏感短文本、全新 task-local SQLite、HTML、哨兵和评审日志／截图；真实内容为 0。
- 允许入口：当前固定 P3-106 Tauri debug candidate 的离线临时副本；renderer 只允许既有 `capture_record`、`get_today`、`runtime_status`。
- 允许工具：现有 Rust 1.98.0、Cargo、Tauri CLI 2.11.4、锁定缓存、本地 app 操作／截图工具；全程 `CARGO_NET_OFFLINE=true` 与 `--locked`。
- 严格只读：P3-104、P3-105、P3-106 全部工程／Evidence／Review／交付物；三张冻结 Stitch 参考图；项目账本；retained pilot；既有 `/private/tmp/lifeos-p3-104-rework-static-results.json`。
- 禁止能力：联网、localhost、dev server、npm／新依赖、远程 asset、generic file/path/DB/shell/process/network capability、额外 IPC、真实数据、外部目标、系统显示设置修改。
- 投递前额外用户确认：已由本次“采纳，并创建”覆盖任务创建和固定非敏感独立复评。任务卡投递只启动本 ABF；任何真实数据／路径、显示设置、runtime／IPC／依赖或风险／冻结／阶段变化仍需新确认。

## 精确临时路径合同

- 独立工作副本仅允许直接位于 `/private/tmp` 的全新目录，名称匹配：`^lifeos-p3-107-review-work-[a-z0-9-]+$`。
- actual app DB 夹具仅允许直接位于 `/private/tmp` 的全新目录，名称匹配：`^lifeos-p3-104-p3-107-review-(nominal|repeat|conflict|failure|reopen|dangling-final|dangling-journal|dangling-wal|dangling-shm|path|link|hardlink|tamper|a11y|narrow)-[a-z0-9-]+$`。
- 不可变 Rust unit tests 仅允许其源码既有十类 PID 路径：`lifeos-p3-104-unit-*-[0-9]+`、`lifeos-p3-104-unit-link-target-[0-9]+`、`lifeos-p3-104-unit-link-[0-9]+`；执行前必须静态枚举并与 P3-106 ABF 精确合同一致。
- 每个路径创建前必须 `lstat` 为缺失且祖先无链接；只清理本轮运行台账记录的精确路径，禁止 glob、find 或 prefix 清理。
- 旧 `lifeos-p3-104-app-evidence`、`rework-replay-*`、`rework-static-results.json` 和其他未列 `lifeos-p3-104-*` 路径不得创建、读取内容、hash、复制、覆盖或清理。仅允许对固定旧文件做 `lstat` metadata 前后核对。

## 固定候选基线

### P3-106 live candidate

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

### P3-104 runtime provenance

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md` | `8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1` |
| `lifeos/reviews/LIFEOS-P3-104_pm_review.md` | `8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795` |
| `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md` | `e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4` |

P3-106 的 lock、Cargo、runtime、main 和 capability 必须与 P3-104 对应文件字节一致；评审不得只接受提交报告中的布尔值。

### 固定视觉 Evidence 输入

| 状态 | P3-106 actual-app Evidence | SHA-256 |
|---|---|---|
| 默认恢复 1280×1024 | `evidence/rework-1/m004-default-1280x1024.png` | `d64921229aab0bbae1fdca0c29cf107e8e11dd7aa7ade732f5a71f3d2c024c5f` |
| 暂无可靠建议 1280×1024 | `evidence/rework-1/m005-no-suggestion-1280x1024.png` | `373c16c24cb334f34de6c3d4cddb8818905814efec75e83a9fcf09a7b1187f1b` |
| 权限受限／离线 1280×1024 | `evidence/rework-1/m006-restricted-1280x1024.png` | `05fa817ab31c874e8505c5c4091f6a438dab56f86b51930003bb1a68d5442da6` |
| 默认恢复 1160×768 | `evidence/rework-1/m015-workspace-1160x768-default.jpg` | `46f86bdc916d68eaf55bb3c83bbb04db8a528aad371281e53e3177d73d95bdf8` |
| 暂无可靠建议 1160×768 | `evidence/rework-1/m015-workspace-1160x768-no-suggestion.jpg` | `5ddf3e956f9cbe961da7fbacaf5d9b62ec1b9141e8c5bb7a1ca1ac63439700b2` |
| 权限受限／离线 1160×768 | `evidence/rework-1/m015-workspace-1160x768-restricted.jpg` | `2832cf9015fda510ec76c74ff41ad515964d3739bc98ebc2c54722991a41ffc5` |
| 窄屏 700×760 | `evidence/rework-1/m015-narrow-responsive.jpg` | `c087412a0780703fb3bd9c5ed14834c9fb3a49ac0d03a93f247639c93de0d6cb` |

独立评审必须自行目视比较这些固定 actual-app Evidence 与三张冻结 Stitch 权威图，并独立运行当前 candidate 验证响应式与动态行为。不得修改系统显示缩放；不得把已提交 PASS 结论当作独立判断。

## 引用的 L1 长期原则

- L1-1 数据主权：只用精确固定非敏感夹具；renderer 不获得通用路径／文件能力。
- L1-2 内容身份：固定演示、用户原文、系统状态、AI／来源关闭态明确区分。
- L1-3 生命周期完整：capture、today、刷新、导航、关闭重开以 backend 权威状态为准。
- L1-4 失败关闭：路径、DB、sidecar、链接、tamper 和 IPC 反例在任何持久化前停止。
- L1-5 用户控制：只有明确 capture 可写；未实现控件不得假成功。
- L1-6 审计可信：saved、repeat、conflict、failure 的记录与回执一致。
- L1-7 Evidence 诚实：独立动作、结果、视觉／日志和 hash 逐项闭环。
- L1-8 历史保全：P3-104／P3-106 与其历史 Evidence 全部只读。
- L1-9 授权不漂移：所有写路径在执行前列出并匹配本 ABF。
- L1-10 可复核性：独立测试设计、runner、固定输入、结构化矩阵、Manifest 和精确清理可重复。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 独立性真实 | P0 | 会话、测试设计、runner 和 Evidence 均未参与 P3-104/P3-106 执行／PM 验收；先冻结独立测试设计再读提交 runner | Rework／Blocked |
| ABF-I-02 | 固定候选身份 | P0 | 上述全部 hash 匹配，P3-106 runtime 五文件与 P3-104 字节一致 | Blocked |
| ABF-I-03 | 离线 clean 可重建 | P0 | 全新临时副本无 target，locked test/build/bundle 成功，network 0 | Rework |
| ABF-I-04 | 路径授权完整 | P0 | 全部写路径 100% 匹配精确 allowlist；旧路径只做 lstat 且不变 | Rework |
| ABF-I-05 | Renderer／IPC 最小权限 | P0 | 仅三项 IPC；无 generic file/path/DB/shell/process/network capability | Rework |
| ABF-I-06 | 三张冻结 Stitch 高保真结构成立 | P1 | 独立逐态目视比较共享骨架和每态锚点，无绿色工程页回退或截图充当 UI | Rework |
| ABF-I-07 | 应用适配屏幕 | P1 | 当前原工作区和 700×760 下关键内容、composer、capture、导航、错误披露可达，无依赖系统改屏 | Rework |
| ABF-I-08 | 内容身份与关闭态诚实 | P0 | 固定演示／原文／系统／AI／来源可辨；未实现控件零副作用 | Rework |
| ABF-I-09 | 生命周期与审计不回退 | P0 | saved、repeat、conflict、failure、refresh、close/reopen 均由 backend 独立验证 | Rework |
| ABF-I-10 | 路径／类型／sidecar fail-closed | P0 | 路径、链接、hardlink、类型、tamper、final/journal/wal/shm dangling 均在变更前拒绝 | Rework |
| ABF-I-11 | 可访问性与用户控制 | P1 | 实际 Tab／Enter／skip／focus／reduced-motion 和错误恢复可用 | Rework |
| ABF-I-12 | Evidence 隐私与诚实 | P0 | 仅固定非敏感内容；每行独立 Evidence；缺行／FAIL／泄密非零退出 | Rework |
| ABF-I-13 | 历史保全与精确清理 | P0 | 候选／历史 100% 未变；台账路径残留 0；无 broad cleanup | Rework |
| ABF-I-14 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 不变，R-0051 原有限关闭不扩大；Not Frozen；Stage 4 未进入 | Rework |

## 冻结验收矩阵

| 行 ID | 独立操作 | 预期结果 | 必须保持不变 | Evidence |
|---|---|---|---|---|
| ABF-M-001 | 核对授权、独立性、ABF 和固定输入 hash | 全部匹配，零歧义 | 所有输入 | authorization + hash matrix |
| ABF-M-002 | 在读取 P3-104/P3-106 runner 前冻结独立测试设计、夹具与断言 | design hash 固定且时间顺序可证 | 候选／提交 runner | test-design.json + hash |
| ABF-M-003 | 独立复算 P3-104/P3-106 Engineering／PM Manifest | 无 bad/missing/extra/self-reference | 历史资产 | manifest-verification.json |
| ABF-M-004 | 全新无 target 副本离线 locked test/build/bundle | 全部退出 0；network 0 | live candidate | clean-build logs |
| ABF-M-005 | 独立静态反查 runtime、IPC、capability、路径与依赖 | 五项 provenance 相等，仅三 IPC | P3-104/P3-106 | static-results.json |
| ABF-M-006 | 逐态独立比较三张 1280×1024 actual-app Evidence 与冻结 Stitch | 三态共享骨架与独立锚点成立 | 图片与参考图 | visual-review.json |
| ABF-M-007 | 在原显示环境运行三态并测试 1160×768 与 700×760 行为 | 关键动作可达、可滚动、无遮挡；不改系统显示 | 系统显示设置 | responsive evidence |
| ABF-M-008 | 独立 actual-app 首次 capture | saved 后才显示成功，DB/audit/sentinel 一致 | 非范围路径 | lifecycle row |
| ABF-M-009 | repeat、conflict、注入失败独立执行 | 幂等／冲突／原子失败正确，失败零持久化 | sentinel/DB on failure | three rows |
| ABF-M-010 | refresh、三页往返、关闭重开 | backend 权威 today 恢复，动作不互相替代 | candidate | restart evidence |
| ABF-M-011 | 逐项操作未实现控件、unknown IPC 与额外字段 | disabled／明确未启用／拒绝，零 DB/IPC 副作用 | DB/audit | denied matrix |
| ABF-M-012 | 路径规范化、父／终点链接、hardlink、FIFO／目录、外部路径 | 全部变更前 fail-closed | link/target/sentinel/DB | boundary matrix |
| ABF-M-013 | final DB、journal、wal、shm dangling 与 content/schema tamper | 各自独立 fail-closed | fixture state | negative matrix |
| ABF-M-014 | 实际 Tab、Enter、skip、focus、reduced-motion | 用户控制链可达且状态诚实 | system setting restored | a11y evidence |
| ABF-M-015 | 资源／隐私／网络／截图复用扫描 | remote、真实数据、参考图嵌入、网络均为 0 | candidate | scan results |
| ABF-M-016 | 精确台账清理、历史 hash 复算、最终负门 | 残留 0、历史不变、缺行／FAIL／泄密非零退出 | 全部只读资产 | cleanup + final verifier |

## Evidence 合同

- 独立 Review：`lifeos/reviews/LIFEOS-P3-107/independent_review.md`。
- 独立 Evidence：`lifeos/reviews/LIFEOS-P3-107/evidence/`；不得创建 `lifeos/engineering/LIFEOS-P3-107/`。
- 必须保存：先冻结的独立测试设计、独立 runner 源码、16 行结构化矩阵、唯一 test／fixture／execution ID、源码／Manifest hash、clean build 日志、实际 app 生命周期／负向结果、视觉与响应式评估、路径 inventory、before/after、隐私／网络扫描、cleanup、final verifier、复跑命令和非自指 Manifest。
- 不得导入或执行 P3-104/P3-106 提交 runner；固定测试设计之后可只读源码反查并复算其 Evidence。
- 每个动态动作须包含前置状态、实际操作、可观察结果、结构化结果 ID、视觉／日志路径和 SHA-256；刷新不得替代关闭重开，静态 focus 不得替代实际 Tab／Enter。
- PM 与工程历史 Evidence 不得复制到 P3-107；只记录路径、预期／实际 hash 和匹配结果。
- 临时目录在 Evidence 落盘后按精确台账清理；禁止把 SQLite、HTML、app bundle、target、缓存或真实内容带入 Evidence。

## 计数与 Pass 公式

- P0：独立性、数据／路径／授权、runtime／IPC／依赖、生命周期／失败关闭、Evidence 真实性／隐私、历史保全或网络越界。
- P1：高保真共享骨架／三态锚点、响应式、可访问性或关键用户控制失败。
- P2：不影响完成定义的清洁项；本轮 Pass 仍要求 0。
- Unknown：关键视觉、hash、动作、路径、状态或清理不可复核。
- Not Implemented：任一矩阵行、独立 runner、actual-app 动作、负向夹具或 Evidence 缺失。
- Pass：ABF-I-01 至 I-14、ABF-M-001 至 M-016 及全部子动作均独立 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；候选与历史 hash 不变；临时残留为 0。
- N/A：仅硬件／系统不暴露的装饰性指标可逐项说明；独立性、视觉三态、响应式、actual app、生命周期、路径、IPC、失败关闭、a11y、清理和 Manifest 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- P3-107 自身 Rework：只允许修正独立 Review runner、Evidence、Manifest 或文案，且 ABF、独立性、候选、数据、目录、能力和授权不变。
- 发现组合候选 P0/P1、明确合同违反或完成定义缺口：P3-107 结论为 Rework；评审不得修复。PM 再判断是否将 P3-106 返回其剩余的一轮正式 Rework。
- 必须新建任务：需要改变本 ABF、用户结果、runtime／IPC／依赖、路径正则、真实数据、视觉权威输入、风险／冻结／阶段边界，或对应任务达到正式 Rework 上限。
- Blocked：无法证明独立性、固定 hash 漂移且来源不明、现有锁定工具链无法离线运行、正常本地 app 控制不可用，且无法在本 ABF 内安全恢复。

## 启动前质疑窗口

- 执行方在任何复制、构建、夹具创建或 app 操作前，必须核对 ABF ID/hash、独立性、全部固定输入和写路径合同。
- 必须先写入并 hash 独立测试设计，之后才可读取 P3-104/P3-106 runner 源码或其结构化结论。
- 发现歧义或任何动作将写 ABF 外路径时立即停止；不得先执行后解释。
- 专项会话开始后不得实质修改本 ABF；如需修改，关闭 P3-107 并新建任务。
