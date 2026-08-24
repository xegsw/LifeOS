# LIFEOS-P3-105 Acceptance Basis Freeze｜三张冻结 Stitch 页面高保真 Tauri UI 整合

## 冻结信息

- 任务 ID：`LIFEOS-P3-105`
- ABF ID／版本：`ABF-P3-105-v1`
- 生效决策：D-0427
- 创建与冻结时间：2026-08-23 16:45:33 CST (+0800)
- 状态：Frozen / Executable After Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 本轮唯一用户结果

在全新 `lifeos/engineering/LIFEOS-P3-105/` 中，以 P3-104 已获 PM Pass 的真实 Tauri/IPC/runtime 为只读技术底座，用 HTML/CSS/JS 高保真实现三张已冻结 `LifeOS 精修版` Stitch 页面，并让实际 Tauri app 在不增加 IPC、不接入真实数据、不削弱任何 runtime 安全不变量的前提下展示三种状态、完成固定非敏感 capture/today 生命周期和真实关闭重开。

“高保真”在本任务中明确表示：直接以三张 1280×1024 冻结截图为视觉权威输入，复现其桌面应用壳、布局层级、主组件、间距关系、色彩气质和三态差异；不得继续使用 P3-104 当前绿色文档／工程验证页作为完成结果，也不得把仅保留语义称为高保真。

明确不冻结：新的产品需求、动态交互规范、生产视觉系统、品牌资产、响应式设计系统、Schema/API、runtime 架构、风险关闭、工程基线、Stage 4 或最终发布 UI。

明确非范围：retained pilot、真实个人输入／DB／路径、clear/delete/export、Vault、模型、云／网络、同步、多设备、L3、外部用户、签名／发布、Stitch 在线画面修改、P3-104 工程修改，以及 P3-105 的最终独立复评。

## 授权和能力边界

- 用户授权事实：用户采纳 P3-104 技术候选，并明确要求先创建高保真 UI 新任务、继承全部 runtime 安全不变量，最终对组合候选统一做全新隔离独立复评。
- 允许写入：`lifeos/engineering/LIFEOS-P3-105/`、`lifeos/deliverables/LIFEOS-P3-105_three_frozen_stitch_pages_high_fidelity_tauri_ui_integration.md`、该任务局部预检输出，以及执行时新建的 `/private/tmp/lifeos-p3-105-*` 固定非敏感夹具。
- 允许数据：仅任务卡冻结的固定非敏感文本、全新 task-local SQLite 和本地生成的中性占位视觉；不得读取任何真实个人内容。
- 允许入口：实际 P3-105 Tauri debug app；renderer 仍只能调用 `capture_record`、`get_today`、`runtime_status`。
- 允许工具／环境：现有 Rust `1.98.0`、Cargo、Tauri CLI `2.11.4` 和 P3-104 已锁定依赖缓存；全程 `CARGO_NET_OFFLINE=true`、`--locked`；本机既有截图／图像检查工具和 Computer Use 仅用于本地实际 app。
- 严格只读：P3-104 全部工程／Review／Evidence，三张冻结参考图，P1-004/P1-006 PRD、P1-009/P1-011 报告、全部历史账本与 Frozen 资产。
- 禁止能力：网络、localhost、dev server、npm／新依赖、远程 asset、截图作为整页背景或大面积覆盖伪装实现、直接文件／DB／path／shell／process capability、额外 IPC、真实数据和任何外部目标。
- 投递前额外用户确认：已由本轮用户指令覆盖“新高保真 UI 任务 + 不变 Tauri/runtime 安全边界”；任务卡投递只启动该窄范围。任何新依赖、runtime／IPC 修改、真实路径或数据仍须重新确认。

## 固定视觉权威输入

| 状态 | 路径 | 尺寸 | SHA-256 |
|---|---|---:|---|
| 默认恢复 | `lifeos/deliverables/evidence/LIFEOS-P1-009/01_default_recovery_preview.jpg` | 1280×1024 | `7b98a48319338a238b02cb7cdeb3d18a1e7eaecf9e7ee791b5c1d18017ba3df1` |
| 暂无可靠建议 | `lifeos/deliverables/evidence/LIFEOS-P1-011/02_no_reliable_suggestion_preview.jpg` | 1280×1024 | `55344c4ef11fc561afe1aaf0eef76e83a8fa06da5b62c88955e84adec4e56697` |
| 权限受限／离线 | `lifeos/deliverables/evidence/LIFEOS-P1-011/03_permission_offline_preview.jpg` | 1280×1024 | `9e03b7673d9b3d74828bd1ad0ea806a8a769dd6ffed17c0d6cc7c2a1c5ae0661` |

三张参考图只能用于只读视觉比对，不得被嵌入页面充当背景、截图蒙层或主体 UI。画面中的第三方缩略图不得从网络下载；以本地代码绘制的中性占位图保持相同构图角色，并明确不冒充真实来源。

## P3-104 技术底座固定输入

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-104/Cargo.lock` | `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1` |
| `lifeos/engineering/LIFEOS-P3-104/src/runtime.rs` | `0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529` |
| `lifeos/engineering/LIFEOS-P3-104/src/main.rs` | `4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c` |
| `lifeos/engineering/LIFEOS-P3-104/tauri.conf.json` | `7c30529e69e5b30900156512f396a5d58fd8e20739786cc77abf5d0f7f6780ef` |
| `lifeos/engineering/LIFEOS-P3-104/capabilities/main.json` | `ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b` |
| `lifeos/engineering/LIFEOS-P3-104/scripts/offline_actual_app_replay.sh` | `cf82f88faa7b80d5818f85d5f23e87dbae228ac0314b9b8642be8ef55157db73` |
| `lifeos/engineering/LIFEOS-P3-104/evidence/rework/attempt-1/MANIFEST.md` | `8ff0bbc1f8c98ea5eec9c571d29f54bcfe70e074735960fe5f84a5160509d1f1` |
| `lifeos/reviews/LIFEOS-P3-104_pm_review.md` | `8d888be0f0ebd698986b418d092033d379cb4fa1fc8a185509b03e1438515795` |
| `lifeos/reviews/LIFEOS-P3-104/pm_evidence/rework-1/MANIFEST.md` | `e552c01ba683ec2c441be190b6880c42d71a7be1e79b0f91ea853d95f3dd3cc4` |

P3-105 必须复制 P3-104 到新目录后工作。`Cargo.lock`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json` 必须字节不变；只允许修改 UI HTML/CSS/JS、仅窗口尺寸／标题相关的 `tauri.conf.json` 字段、P3-105 自有测试／runner／Evidence。若实现需要修改 runtime、IPC、依赖或 capability，立即停止并回报 PM，不能在本 ABF 内继续。

## 引用的 L1 长期原则

- L1-1 数据主权：只使用全新 task-local 固定非敏感夹具，renderer 不获得路径和文件能力。
- L1-2 内容身份：用户原文、固定演示、系统状态、AI 关闭和不可用来源必须可辨，不以视觉稿内容冒充真实 runtime 事实。
- L1-3 生命周期完整：capture、today、刷新、导航、关闭重开保持同一 backend 权威状态。
- L1-4 失败关闭：继承 P3-104 的 DB／sidecar／路径／原子失败全部反例。
- L1-5 用户控制：只有明确 capture 动作可写固定非敏感记录；设计稿中的未实现动作不得伪装成功。
- L1-6 审计可信：saved、repeat、conflict 和失败的数量与含义不变。
- L1-7 Evidence 诚实：高保真必须由实际 app 截图和逐行动作证明，不得用参考图背景或静态 DOM 计数替代。
- L1-8 历史保全：P1 与 P3-104 全部输入只读，P3-105 Evidence 独立。
- L1-9 授权不漂移：不继承真实 pilot、风险关闭或 Stage 4 权限。
- L1-10 可复核性：固定 viewport、候选 hash、逐行视觉合同和离线 runner 可重复。

## 冻结视觉合同

### 共享桌面骨架（1280×1024 比对画布）

1. 左侧必须是贯穿全高的窄白色导航轨，宽度约占画布 5%–8%，含顶部主入口、纵向次入口和底部设置／身份入口；不得退化成顶部文本链接。
2. 主内容从画布约 11%–13% 的横向位置开始，右侧留白约 3%–5%；背景为参考图的冷浅灰／淡紫气质，主要强调色为蓝／靛蓝，不得以 P3-104 绿色文档卡片体系为主视觉。
3. 底部必须有居中的浮动捕获 composer，位于画布下方约 90%–98% 高度区，包含附件／语音视觉入口、原文提示和深色发送按钮；只有冻结的固定非敏感 capture 能触发 backend，其他入口必须 disabled 或诚实披露未启用。
4. 圆角、浅阴影、留白、卡片层级和中文系统字体应与参考图同一视觉语言；不得把安全说明大段堆在首屏主视觉中，边界信息应渐进披露且仍可访问。
5. 实际 app 截图必须裁取／规范化为 1280×1024 webview 内容画布，并与对应参考图生成并列图；不得只提交局部截图。

### 三态结构锚点

- 默认恢复：顶部问候／日期／当前 Project；大幅双栏恢复卡（左侧 Project、摘要、证据与继续动作，右侧视觉预览）；其下独立 AI／系统建议卡；底部 composer。
- 暂无可靠建议：顶部问候／日期；中央大空态卡与两个明确选择；其下最近留下的痕迹三列卡片；底部 composer。不得生成可靠建议或静默选择 Project。
- 权限受限／离线：顶部 Project 语境；网络离线与来源权限受限两条分层警示；中部恢复卡与不可用来源区域；权限受限浮层／内嵌卡；下方今日安排与底部 composer。必须清楚显示可继续本地使用且 AI／外部能力关闭。

允许因固定非敏感数据和关闭态调整具体文案、图片内容与数字，但不得移除上述骨架、主组件或三态差异。所有设计稿中看似可执行但本任务未实现的按钮必须 disabled、无副作用或点击后明确显示“未启用”；不得假成功。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 三张冻结视觉输入身份固定 | P0 | 3/3 路径、尺寸、hash 匹配；未选错旧画面 | 停止，不生成候选 |
| ABF-I-02 | 高保真共享骨架成立 | P1 | 左轨、主内容、状态卡、底部 composer、蓝灰视觉语言全部存在；无绿色文档页回退 | Not Pass |
| ABF-I-03 | 三态结构和差异成立 | P1 | 三张实际 app 全画布截图分别满足冻结锚点 | Not Pass |
| ABF-I-04 | 视觉实现真实 | P0 | HTML/CSS/JS 元素实际渲染；参考截图未作为背景／蒙层／主体图片 | 停止并 Rework |
| ABF-I-05 | 内容身份与关闭态诚实 | P0 | 固定演示、用户原文、系统状态、AI 关闭、来源不可用清楚；未实现动作不假成功 | 无写入、明确失败 |
| ABF-I-06 | Runtime 与依赖不漂移 | P0 | lock、runtime、main、capability hash 与 P3-104 固定值一致；完全离线 locked build | 停止 |
| ABF-I-07 | Renderer／IPC 最小权限不回退 | P0 | 仍只有三项 IPC；零直接文件／DB／path／shell／process／network capability | 拒绝启动／调用 |
| ABF-I-08 | capture/today 生命周期不回退 | P0 | saved、repeat、conflict、failure、刷新、导航、关闭重开均由 backend 权威状态驱动 | DB/UI/哨兵不变 |
| ABF-I-09 | 路径／DB／sidecar fail-closed 不回退 | P0 | P3-104 已知矩阵与 final/journal/wal/shm dangling 反例全部通过 | 变更前停止 |
| ABF-I-10 | 可访问性与窄屏适配 | P1 | skip link、实际 Tab/Enter、可见焦点、reduced motion；窄屏无横向丢失关键动作 | Not Pass |
| ABF-I-11 | Evidence 可复核且历史保全 | P0 | 逐行结果、三张全图、结构锚点、动作日志、hash、Manifest、clean replay 完整 | Not Pass |
| ABF-I-12 | 风险／冻结／阶段不漂移 | P0 | R-0040/R-0052 保持 Open，R-0051 不变，Not Frozen，未进入 Stage 4 | 停止并报告 |

## 冻结验收矩阵

每行必须独立执行并生成唯一 test／fixture／execution ID；不得从一个总 PASS 批量映射。

| 行 ID | 入口／前置 | 实际操作 | 预期结果 | 必须保持不变 | Evidence |
|---|---|---|---|---|---|
| ABF-M-001 | 启动前 | 核对授权、ABF、3 张参考图及 P3-104 固定输入 hash | 全部匹配；质疑窗口关闭 | 历史文件 | hash log + structured row |
| ABF-M-002 | 无 build target 副本 | 完全离线 `--locked` clean build 与实际 `.app` bundle | 构建／启动成功，无网络／dev server | lock/runtime/capability | build log + binary hash |
| ABF-M-003 | 默认恢复、1280×1024 | 打开实际 app 并截取完整画布 | 共享骨架及默认态锚点全部成立 | DB 初态 | full screenshot + side-by-side |
| ABF-M-004 | 暂无可靠建议、1280×1024 | 实际导航并截取完整画布 | 空态、双选择、三列痕迹与 composer 成立；无假建议 | DB 状态 | full screenshot + side-by-side |
| ABF-M-005 | 权限受限／离线、1280×1024 | 实际导航并截取完整画布 | 双警示、受限恢复卡、权限提示、今日安排与 composer 成立 | DB 状态 | full screenshot + side-by-side |
| ABF-M-006 | 三张实际截图 | 逐项核对共享骨架、三态锚点及非绿色文档页门 | 每个必填锚点独立 PASS | 参考图 hash | visual contract JSON |
| ABF-M-007 | 页面 DOM／资源 | 检查背景图、img、CSS 和资源清单 | 无整页／大面积参考截图复用，无远程 asset | 参考图只读 | static scan + resource manifest |
| ABF-M-008 | 首次固定 capture | 在 composer 明确执行唯一允许的固定非敏感保存 | backend saved 后才显示成功；身份正确 | sentinel | action log + DB snapshot |
| ABF-M-009 | 已 saved | 重复同 key／异文本 conflict／注入失败 | repeat 合法；conflict/failure blocked，无假 UI 成功 | DB、audit、sentinel | three independent rows |
| ABF-M-010 | saved 状态 | 刷新、三页往返、关闭 app、重启 | 三页均从 backend 恢复同一 today 状态 | record/audit 数量 | actual app log + screenshots |
| ABF-M-011 | 未实现视觉控件 | 实际点击附件、语音、Project、AI／来源相关控件 | disabled 或明确“未启用”，零 IPC／零 DB 副作用 | DB、audit、sentinel | per-control closure rows |
| ABF-M-012 | renderer | unknown IPC、额外 path/sql/shell 字段与 capability/CSP 扫描 | 全部 fail-closed；仅三项 IPC；network 0 | DB、sentinel | IPC trace + static/dynamic checks |
| ABF-M-013 | 新 task-local 夹具 | 复跑路径、symlink、hardlink、shadow、sidecar、Schema/content tamper | 全部变更前失败 | 外部目标、DB、sentinel | regression runner |
| ABF-M-014 | 四个独立夹具 | final DB、journal、wal、shm dangling symlink 实际二进制反例 | 4/4 fail-closed，链接／缺失目标／哨兵／残留不变 | 全部夹具状态 | per-variant results |
| ABF-M-015 | 键盘／窄屏／reduced motion | 实际 Tab、Enter、skip link、focus；窄屏；系统 reduced motion | 每项实际可观察 PASS，关键功能不丢失 | backend 状态 | individual screenshots/logs |
| ABF-M-016 | 结束 | 复算 source/history hash、隐私扫描、Manifest、临时清理、风险对账 | 历史不变、真实数据 0、网络 0、残留 0、风险／阶段不变 | 所有历史资产 | final manifest + cleanup log |

## Evidence 合同

- 可运行源码：P3-105 自有静态／runtime regression、visual contract verifier、实际 `.app` replay runner。
- 逐行结构化结果：16 行矩阵及所有子动作具有唯一 ID、PASS/FAIL、严重级别和 Evidence 路径。
- 视觉 Evidence：三张 1280×1024 实际 app 全画布截图、对应参考图、并列对照图；不得只给局部图或 DOM 计数。
- 动态闭环：使用 `UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md` 或等价机器可读格式；刷新不代替关闭重开，静态 focus 不代替实际 Tab/Enter。
- before／after：DB quick_check、record/audit 数、sentinel hash、link/target/type、进程与临时残留。
- Manifest：不自指；覆盖所有源码、runner、结果、日志、截图和对照图。
- 复跑命令：从无 build target 副本、完全离线、locked，能重建实际 `.app` 并完成视觉／runtime 矩阵。
- 临时清理：只清理本任务明确创建的 `/private/tmp/lifeos-p3-105-*`；残留必须为 0。

## 计数与 Pass 公式

- P0：任一数据／能力／runtime／历史／Evidence 真实性／截图作弊／网络越界。
- P1：任一共享骨架、三态锚点、可访问性或视觉完成定义不成立。
- P2：不影响完成定义但需清洁的文案／Evidence 可读性问题；本轮 Pass 仍要求为 0。
- Unknown：无法复核的关键视觉、runtime、hash、动作或状态。
- Not Implemented：任一必填页面、锚点、实际 app 动作、runner 或 Evidence 缺失。
- Pass 公式：ABF-I-01 至 I-12、ABF-M-001 至 M-016 及全部子动作实际 PASS；P0/P1/P2/Unknown/Not Implemented 全为 0；三张参考图 hash、P3-104 固定 runtime hash、离线 actual-app build/replay、三张全画布对照、runtime 回归和残留 0 必须同时成立。
- 允许 N/A：仅 macOS 不暴露的装饰性视觉差异可逐项说明；任何页面、共享骨架、三态锚点、IPC、生命周期、失败关闭、实际 app、a11y 或全图 Evidence 不得 N/A。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅限 P3-105 UI、视觉合同、测试、Evidence 或不改变 hash 的窗口配置问题，且用户结果／ABF／runtime／IPC／数据／依赖／授权均不变。
- 必须新建任务：需要修改 runtime、main、Cargo.lock、capability、IPC、Schema/API、引入依赖／网络／真实数据，改变冻结视觉权威输入，增加产品能力，关闭风险、冻结资产或进入 Stage 4；或正式 Rework 达到两轮。
- Blocked：现有官方工具链／缓存无法离线重建、Computer Use 无法操作实际 app、参考图损坏或必要本地输入不可读，且不能在原 ABF 安全恢复。

## 候选基线与只读保全

- 候选输入：上述三张参考图和 P3-104 九项固定技术输入。
- 允许变化：仅 P3-105 新目录、交付物和 P3-105 Evidence；P3-104 与历史资产严格只读。
- 最终组合候选必须在 P3-105 PM Pass、用户采纳后进入全新隔离独立复评；独立评审不得由 P3-105 执行会话或本 PM 验收上下文替代。

## 启动前质疑窗口

- 执行方是否提出歧义：尚未投递。
- PM 处理：任务卡要求执行方在任何复制、构建或 UI 修改前核对视觉权威、不可变 runtime hash、允许修改文件和高保真锚点；有歧义立即停止。
- 最终冻结版本：`ABF-P3-105-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
