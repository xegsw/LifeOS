# LIFEOS-P3-106 Acceptance Basis Freeze｜高保真 Tauri UI 路径合同后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-106`
- ABF ID／版本：`ABF-P3-106-v1`
- 生效决策：D-0429
- 创建与冻结时间：2026-08-23 17:21:04 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 本轮唯一用户结果

在全新 `lifeos/engineering/LIFEOS-P3-106/` 中，以 P3-104 的不可变 Tauri/runtime/IPC 安全底座和 P3-105 的只读 UI 草案为输入，用真实 HTML/CSS/JS 高保真实现三张冻结 Stitch 页面，并在本 ABF 精确授权的固定非敏感 `/private/tmp` 夹具路径内完成实际 Tauri app、三态视觉、capture/today 生命周期、失败关闭、关闭重开和动态 Evidence。

本任务只修复 P3-105 的治理合同矛盾，不改变 runtime。P3-104 `Cargo.lock`、`Cargo.toml`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json` 和直接依赖必须字节不变。

明确不冻结：产品需求、生产视觉系统、品牌资产、Schema/API、runtime 架构、工程基线、风险状态、Stage 4 或发布 UI。

明确非范围：retained pilot、真实个人数据／DB／路径、clear/delete/export、Vault、模型、网络／云／第三方、同步、多设备、L3、外部用户、签名发布、Stitch 在线修改、P3-104/P3-105 修改及最终独立复评。

## 授权和能力边界

- 用户授权事实：用户采纳 P3-105 `Blocked / Closed — Acceptance Not Met`，并明确授权创建后继任务。该采纳采用 PM 建议：保持 runtime 不变，在新 ABF 中精确授权其固定非敏感夹具路径。
- 允许写入：`lifeos/engineering/LIFEOS-P3-106/`、`lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md`、本任务局部预检输出，以及下述固定 `/private/tmp` 路径。
- 允许数据：仅冻结的固定非敏感文本、全新 task-local SQLite、哨兵和本地代码生成的中性占位视觉；真实内容为 0。
- 允许入口：实际 P3-106 Tauri debug app；renderer 仍只能调用 `capture_record`、`get_today`、`runtime_status`。
- 允许工具：现有 Rust `1.98.0`、Cargo、Tauri CLI `2.11.4` 和已锁定缓存；全程 `CARGO_NET_OFFLINE=true`、`--locked`；本机本地 app 操作／截图工具。
- 严格只读：P3-104、P3-105 全部工程／Review／Evidence／交付物，三张参考图，历史账本、retained pilot 和 Frozen 资产。
- 禁止能力：网络、localhost、dev server、npm／新依赖、远程 asset、整页参考截图复用、直接文件／DB／path／shell／process capability、额外 IPC、真实数据和外部目标。
- 投递前额外用户确认：本轮已覆盖新任务及下述固定非敏感夹具授权；任务卡投递只启动本 ABF。任何其他 `/private/tmp` 名称、真实路径／数据、runtime／IPC／依赖变化仍须新确认。

## 精确临时路径合同

### P3-106 实际 app／runner 可写路径

仅允许直接位于 `/private/tmp` 下、名称完全匹配以下正则的全新目录：

```text
^lifeos-p3-104-p3-106-(app|replay|dangling-final|dangling-journal|dangling-wal|dangling-shm|path|tamper|a11y|visual)-[a-z0-9-]+$
```

目录内只允许 `capture.sqlite`、SQLite sidecar、固定非敏感 `sentinel.txt`、任务结果 JSON／日志和本地截图。每个目录必须在创建前 `lstat` 为缺失，所有祖先无链接；只清理本次运行台账记录的精确路径，禁止 glob 清理。

### 不可变 Rust unit tests 可写路径

因为 `src/runtime.rs` 字节冻结，执行 `cargo test --locked` 时仅额外授权其源码可静态枚举的以下直接 `/private/tmp` 路径：

```text
^lifeos-p3-104-unit-(lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+$
^lifeos-p3-104-unit-link-target-[0-9]+$
^lifeos-p3-104-unit-link-[0-9]+$
```

这些目录／链接只能由冻结 unit tests 创建，内容只能是固定测试 DB／哨兵／链接；测试结束必须不存在。执行前必须静态复核源码写路径仍精确等于本表，否则停止。

### 明确禁止的旧路径

不得创建、读取、覆盖或清理 `/private/tmp/lifeos-p3-104-app-evidence`、`/private/tmp/lifeos-p3-104-rework-replay-*`、`/private/tmp/lifeos-p3-104-rework-static-results.json` 或任何其他 `lifeos-p3-104-*`。当前已存在的旧 `rework-static-results.json` 仅做路径 metadata 只读前后核对，不读取内容，不得变化。

## 固定视觉权威输入

| 状态 | 路径 | 尺寸 | SHA-256 |
|---|---|---:|---|
| 默认恢复 | `lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg` | 1280×1024 | `7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1` |
| 暂无可靠建议 | `lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg` | 1280×1024 | `55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697` |
| 权限受限／离线 | `lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg` | 1280×1024 | `9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661` |

参考图只用于只读比对，不得嵌入页面充当背景、蒙层或主体 UI；第三方缩略图只能以本地代码生成的中性占位构图替代。

## P3-104 不可变技术输入

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-104/Cargo.lock` | `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1` |
| `lifeos/engineering/LIFEOS-P3-104/Cargo.toml` | `9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e` |
| `lifeos/engineering/LIFEOS-P3-104/src/runtime.rs` | `0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529` |
| `lifeos/engineering/LIFEOS-P3-104/src/main.rs` | `4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c` |
| `lifeos/engineering/LIFEOS-P3-104/capabilities/main.json` | `ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b` |
| `lifeos/engineering/LIFEOS-P3-104/tauri.conf.json` | `7c30529e69e5b30900156512f396a5d58fd8e20739786cc77abf5d0f7f6780ef` |
| `lifeos/engineering/LIFEOS-P3-104/scripts/offline_actual_app_replay.sh` | `cf82f88faa7b80d5818f85d5f23e87dbae228ac0314b9b8642be8ef55157db73` |
| `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md` | `8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1` |
| `lifeos/reviews/LIFEOS-P3-104_pm_review.md` | `8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795` |
| `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md` | `e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4` |

## P3-105 只读 UI 草案输入

| 路径 | SHA-256 |
|---|---|
| `ui/default-recovery.html` | `4a6464236b03ad5ffee1d50268169558320ca90484fe646933ff19c2497a5d56` |
| `ui/no-reliable-suggestion.html` | `1fdd0129ffa056fd64a08e0c6227cdf84b90cc8e964ff811dde2efabfaa85ce2` |
| `ui/restricted-offline.html` | `fa918f044fa9cbb4f3eafcb117af97bc039c5bbeb075ada2e91f9da34eecd27d` |
| `ui/app.js` | `62d6685c8911efb5ccaabadde350e267cb0ce58b829abbeca0580ff7025a6507` |
| `ui/styles.css` | `5b93977e863bd33a6f505e585080cdf85a547c08cee1bca9c7fa05008d26d50d` |
| `tauri.conf.json` | `d44e1e03ade7ecc5dc75f5431295de78735ccf0596a421eae0f553411294e0f0` |
| P3-105 Engineering Manifest | `b3bb63eb3605499fe70885f3056c3a1fb177227f20cff0fa6e3ec2d95cdb9b92` |
| P3-105 PM Review | `8f7c1add69313082863012dc04576dc20beb3889eff0ad73f431a07710820cc6` |
| P3-105 PM Evidence Manifest | `73212af186afb8aa4bb5dccf41f05a6836e20e4ec58824f459a0049ef4c3d73b` |

P3-106 必须从 P3-104 复制不含 `.tooling/`、`target/`、`evidence/` 的技术底座，再只复制上述 P3-105 六个 UI／窗口文件。不得复制 P3-104 或 P3-105 Evidence 到 P3-106 live `evidence/`；该目录必须全新、初始为空。

## 引用的 L1 长期原则

- L1-1 数据主权：只用上述精确固定非敏感路径，renderer 无路径／文件能力。
- L1-2 内容身份：用户原文、固定演示、系统状态、AI 关闭和不可用来源清楚。
- L1-3 生命周期完整：capture、today、刷新、导航、关闭重开保持 backend 权威。
- L1-4 失败关闭：DB、sidecar、链接、路径、Schema/content tamper 均在变更前停止。
- L1-5 用户控制：只有明确 capture 可写；未实现控件禁用或诚实披露。
- L1-6 审计可信：saved、repeat、conflict、failure 数量和语义不漂移。
- L1-7 Evidence 诚实：实际 app 动作逐行证明，源码／静态不代替动态。
- L1-8 历史保全：P3-104/P3-105 严格只读，P3-106 Evidence 全新独立。
- L1-9 授权不漂移：执行前枚举全部写路径，只能匹配本 ABF。
- L1-10 可复核性：固定 viewport、hash、路径台账、runner、Manifest 和精确清理可重复。

## 冻结视觉合同

- 共享骨架：1280×1024 全画布；5%–8% 全高白色左轨；主内容约从 11%–13% 横向位置开始；冷浅灰／淡紫背景与蓝／靛强调；底部 90%–98% 高度区固定浮动 composer；不得回退为 P3-104 绿色工程页。
- 默认恢复：问候／日期／Project；双栏恢复卡；独立 AI／系统建议卡；底部 composer。
- 暂无可靠建议：问候／日期；中央空态与两个选择；最近痕迹三列卡；底部 composer；不得伪造建议或静默选 Project。
- 权限受限／离线：Project 语境；网络离线和来源受限双警示；受限恢复卡、权限提示、今日安排和 composer；明确本地可继续、AI／外部能力关闭。
- 未实现按钮必须 disabled、零副作用或明确显示“未启用”；不得假成功。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 |
|---|---|---|---|
| ABF-I-01 | 固定输入身份 | P0 | 视觉 3/3、P3-104 10/10、P3-105 9/9 hash 匹配 |
| ABF-I-02 | 路径合同完整 | P0 | 执行前静态枚举全部写路径，100% 匹配精确 allowlist；旧路径前后不变 |
| ABF-I-03 | Runtime／依赖不漂移 | P0 | lock、Cargo、runtime、main、capability hash 不变，离线 locked clean build |
| ABF-I-04 | Renderer／IPC 最小权限 | P0 | 仅三项 IPC，零直接文件／DB／path／shell／process／network capability |
| ABF-I-05 | 高保真共享骨架 | P1 | 左轨、蓝灰主内容、三态卡、底部 composer 全部存在，无绿色工程页回退 |
| ABF-I-06 | 三态结构差异 | P1 | 三张实际 app 全图逐态满足结构锚点 |
| ABF-I-07 | 真实 UI 实现 | P0 | HTML/CSS/JS 元素渲染；无参考截图背景／蒙层／主体复用 |
| ABF-I-08 | 内容身份／关闭态诚实 | P0 | 固定演示、原文、系统、AI／来源状态可辨；未实现动作零假成功 |
| ABF-I-09 | 生命周期不回退 | P0 | saved、repeat、conflict、failure、刷新、导航、关闭重开由 backend 驱动 |
| ABF-I-10 | 路径／DB／sidecar fail-closed | P0 | 已知矩阵及 final/journal/wal/shm dangling 4/4 在变更前失败 |
| ABF-I-11 | 可访问性／窄屏 | P1 | 实际 Tab/Enter/skip/focus、reduced-motion、窄屏关键动作可用 |
| ABF-I-12 | Evidence 独立完整 | P0 | 空 evidence 起步；逐行结果、全图、动作、hash、Manifest、clean replay 完整 |
| ABF-I-13 | 清理和历史保全 | P0 | 仅删除运行台账中的精确路径；P3-104/P3-105/旧 temp metadata 不变；残留 0 |
| ABF-I-14 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 Open，R-0051 不变，Not Frozen，未进入 Stage 4 |

## 冻结验收矩阵

每行及子动作必须有唯一 test／fixture／execution ID；不得批量继承总 PASS。

| 行 ID | 实际操作 | 预期 Evidence |
|---|---|---|
| ABF-M-001 | 核对授权、ABF、全部固定输入 hash | 22/22 hash log + structured row |
| ABF-M-002 | 静态枚举 runtime unit、P3-106 runner 和 cleanup 的所有写路径 | path inventory 100% allowlisted；legacy path metadata before |
| ABF-M-003 | 从无 target、空 evidence 副本离线 locked clean test/build/bundle | unit 7/7、build 0、binary/source/lock hash、network 0 |
| ABF-M-004 | 默认恢复实际 app 1280×1024 全画布 | full screenshot + reference side-by-side + anchors |
| ABF-M-005 | 无可靠建议实际导航全画布 | full screenshot + side-by-side + anchors |
| ABF-M-006 | 权限受限／离线实际导航全画布 | full screenshot + side-by-side + anchors |
| ABF-M-007 | 逐项视觉合同与防截图／远程资源扫描 | visual contract JSON + resource manifest |
| ABF-M-008 | 首次固定 capture | backend saved 后才显示成功；DB/audit/sentinel before-after |
| ABF-M-009 | repeat、conflict、注入失败分别执行 | 三个独立结果；失败零持久化／零假成功 |
| ABF-M-010 | 刷新、三页往返、关闭 app、重启 | backend 恢复同一 today；关闭重开独立 Evidence |
| ABF-M-011 | 附件、语音、Project、AI、来源等未实现控件逐项实际操作 | disabled／未启用；每项零 IPC／DB 副作用 |
| ABF-M-012 | unknown IPC、额外 path/sql/shell 字段、capability/CSP | 全部拒绝，仅三项 IPC，network 0 |
| ABF-M-013 | 路径、目录链接、DB 链接／hardlink、shadow、Schema/content tamper | 每个反例变更前 fail-closed |
| ABF-M-014 | final DB、journal、wal、shm dangling 四独立夹具 | 4/4 fail-closed；链接／target／sentinel／残留不变 |
| ABF-M-015 | 实际 Tab、Enter、skip、focus、窄屏、reduced-motion | 每项独立截图／日志／结果 ID |
| ABF-M-016 | 对每个创建路径执行台账驱动精确清理 | 无 glob；允许路径残留 0；legacy metadata 不变 |
| ABF-M-017 | 复算 P3-104/P3-105 历史与候选 hash、隐私／网络扫描 | history unchanged、真实数据 0、network 0 |
| ABF-M-018 | 最终 Manifest 与 clean replay verifier | Manifest 不自指、覆盖全部 live Evidence，缺行／FAIL 非零退出 |

## Evidence 合同

- P3-106 `evidence/` 必须新建为空，不得复制历史 Evidence；历史仅以路径和 hash 引用。
- 保存可运行静态、路径 inventory、runtime regression、visual contract、actual-app replay、dynamic closure 与 cleanup verifier 源码。
- 三张实际 app 1280×1024 全画布、三张 reference side-by-side；不得只给局部图或 DOM 计数。
- 每个动态动作记录前置、操作、可观察结果、唯一结果 ID、截图／日志路径和 SHA-256；刷新不代替关闭重开，静态 focus 不代替实际 Tab/Enter。
- before/after 包含 DB quick_check、record/audit 数、sentinel hash、link/target/type、进程、路径台账、legacy temp metadata 和残留。
- Manifest 不自指，覆盖所有 live P3-106 源码、runner、结果、日志、截图和对照图；必须验证全部引用文件存在且 hash 匹配。
- 复跑从无 target、空 evidence 副本开始，完全离线 locked 重建 actual `.app` 并完成 18 行矩阵。

## 计数与 Pass 公式

- P0：任何数据／路径／授权／runtime／IPC／依赖／历史／Evidence 真实性／截图作弊／网络越界。
- P1：共享骨架、三态锚点、可访问性或视觉完成定义不成立。
- P2：不影响完成定义的清洁项；本轮 Pass 仍要求 0。
- Unknown：关键视觉、runtime、hash、动作、写路径或状态不可复核。
- Not Implemented：任一页面、锚点、actual-app 动作、runner、路径台账或 Evidence 缺失。
- Pass：ABF-I-01 至 I-14、ABF-M-001 至 M-018 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；actual app、三张全图、runtime 回归、路径台账、精确清理和残留 0 同时成立。
- N/A：仅 macOS 不暴露的装饰差异可逐项说明；路径、页面、IPC、生命周期、失败关闭、actual app、a11y 或全图 Evidence 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅限 P3-106 UI、视觉合同、P3-106 runner／Evidence 或不改变 hash 的窗口配置，且用户结果、ABF、runtime、IPC、数据、目录、依赖和授权不变。
- 必须新建任务：需要改 runtime/main/Cargo/Cargo.lock/capability/IPC、扩充临时路径正则、引入依赖／网络／真实数据、改变视觉权威输入、风险／冻结／阶段边界，或达到两轮 Rework。
- Blocked：锁定工具链／缓存无法离线重建、必要本地 app 控制不可用、参考图损坏，且不能在本 ABF 安全恢复。

## 启动前质疑窗口

- 执行方必须在任何复制、构建或测试前核对 22 项固定输入、P3-106 空 Evidence、全部写路径正则、旧路径 metadata 和禁止路径。
- 任何 runner／test 会写本 ABF 外路径时必须停止；不得先执行后解释。
- 专项会话开始后不得修改本 ABF；如需修改，关闭 P3-106 并新建任务。
