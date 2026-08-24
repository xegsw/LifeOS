# P3-109 独立测试设计（冻结先行）

## 设计元数据

- 任务：`LIFEOS-P3-109`
- ABF：`ABF-P3-109-v1`
- 依据：仅本任务卡、Frozen ABF 与 L1-1 至 L1-10；未读取 P3-107／P3-108 runner、工具或结果后形成。
- 设计目的：以全新、正向 allowlist 副本和 task-local 非敏感夹具，独立验证 P3-104 + P3-106 组合候选；任何候选问题只记录，不修复。
- 通过规则：逐行满足 ABF I-01–I-14、M-001–M-016；verifier 的真 payload 为零退出，六种 mutation 均非零；所有计数为零；历史零写入且允许临时路径精确清理。

## 先决条件与停止规则

1. 先核对任务卡与 ABF hash、用户投递授权、会话隔离、模型／推理档位与允许写入路径；任一不可核实或不匹配时停止为 `Blocked`，不复制、构建、启动 app 或形成通过声明。
2. 所有候选和历史资产只读；仅写 ABF 枚举的 P3-109 Review、Evidence、交付物及精确 `/private/tmp` 路径。
3. 使用正向 allowlist 建立空副本；inventory 必须证明不存在旧 runner、tests、tools 或 Evidence。禁止复制、导入或执行 P3-107／P3-108 runner、工具、Evidence。
4. 所有实际 app、DB、文件、路径和 IPC 操作均使用新建短 ASCII 非敏感夹具；不读取 retained pilot、个人文件或真实 DB。
5. native 700×760 必须由普通 GUI resize 后，对同一 PID／bundle／window 以两种允许的只读 native 查询记录。不允许改变系统显示或偏好；若两种查询均不可用则 `Blocked`。

## 独立矩阵设计

| ABF 行 | 独立测试设计 | 原始 Evidence 与判定方式 |
|---|---|---|
| M-001 | 记录投递路径、接收时间、任务/ABF hash、会话隔离声明、运行配置可核实性与固定输入 hash。 | `authorization.json`、`fixed-inputs.json`；逐字段比较，不以自报 PASS 判定。 |
| M-002 | 本文件 hash 固定后，才记录任何 P3-107/P3-108 runner／结果的读取；验证未复制/导入/执行。 | `read-order.json`、read log、文件 hash；时间与路径逐项比对。 |
| M-003 | 重算 P3-106 Manifest；按时间限定例外核验 P3-104；核验 P3-108 只读入口，不采纳其动态结果。 | `manifest-verification.json`、逐项 hash／时间来源。 |
| M-004 | 从候选正向 allowlist 构造新工作副本，枚举全部路径，确认零 runner/tests/tools/Evidence。 | `copy-inventory.json`、复制命令、路径清单。 |
| M-005 | 空 target 下离线 locked test、build、bundle；记录命令、环境、stdout/stderr、退出码及网络为零的静态证据。 | 原始 build logs、`build-results.json`。 |
| M-006 | 对副本独立静态检查 runtime provenance、三项 IPC 的 strict 输入、空 capability、路径控制与锁定依赖。 | `static-results.json` 与逐条源码定位／hash。 |
| M-007 | 对 ABF 固定三组 Stitch 与 P3-106 1280×1024 Evidence 做逐态人工比较：共享骨架、层级、身份、状态锚点和差异。 | `visual/fixed-comparison.json`，每状态独立观察与结论；不重捕获或量测 1280 窗口。 |
| M-008 | actual app 在原窗口和 native outer frame 700×760 下，分别执行三态滚动、无遮挡及关键动作可达验证。 | 两种 native 查询原始输出、PID/bundle/title/time、AX、截图与动作日志。 |
| M-009 | 全新 DB 首次 capture；只在 commit 后确认成功，并比对 DB/audit/sentinel 前后状态。 | raw app log、before/after snapshots、独立结构化行。 |
| M-010 | 分别执行 repeat、conflict 和注入失败；每种独立建立 fixture、前后快照与退出／回执检查。 | 三套 raw logs、before/after 与结构化结果；失败必须零副作用。 |
| M-011 | 在新 fixture 上分别 refresh、三页往返与 close/reopen，核验 backend 权威状态恢复。 | actual app 动作、PID／生命周期与 DB Evidence。 |
| M-012 | 逐项触发未实现控件、unknown IPC、extra field；核验显式拒绝／disabled 且 DB/audit/sentinel 不变。 | denied matrix、raw logs、before/after。 |
| M-013 | 用独立 fixture 覆盖 directory、symlink、hardlink、type、dangling final、外部 path；每项均在变更前拒绝。 | boundary matrix、stdout/stderr、sentinel、外部目标不存在证明。 |
| M-014 | 分别验证 dangling journal/wal/shm、content tamper、schema tamper，核验 fail-closed 与前后不变。 | negative matrix、raw logs、before/after。 |
| M-015 | 实际执行 Tab、Enter、skip、focus；读取当前 reduced-motion 值并对比 app 披露，检查隐私/网络。 | a11y matrix、原始 AX、系统只读值、截图、scan。 |
| M-016 | semantic verifier 直接解析 raw logs/snapshots/geometry/cleanup/hashes；不使用矩阵 `status/pass`。先验真 payload，再在 disposable copy 做六类 mutation。 | `semantic-result.json`、六类非零 mutation logs、payload manifest、cleanup、顶层非自指 Manifest。 |

## 语义 verifier 最低断言

- 对每一矩阵行验证所需原始文件存在、hash 一致、解析值满足冻结预期；不得把 Markdown 或汇总字段作为判定输入。
- 解析退出码、DB/audit/sentinel 前后数量、negative mutation 的拒绝前状态、native geometry 的整数 700×760、a11y 动作及 cleanup 路径。
- 在 disposable copy 中分别验证：必需文件缺失、hash 改变、cleanup 路径仍存在、negative 退出码变为 0、DB/audit 数量不符、geometry 非 700×760；每一种均必须使 verifier 非零。
- 生成顺序固定为：raw payload → `PAYLOAD_MANIFEST.json` → verifier/`final-verifier.json` → 顶层非自指 `MANIFEST.md`；顶层复算命令必须不让 manifest 验证自身。

## 计数与结论

- P0：授权／独立性／路径数据、runtime/IPC、生命周期失败关闭、Evidence 语义、历史保全、网络越界。
- P1：固定视觉、原窗口／700×760 响应式、a11y/用户控制。
- P2、Unknown、Not Implemented 按 ABF；任一非零均不得给出 Pass。
- 正常 app、工具链或两种 native geometry 查询的真实不可用属于 Blocked；候选 P0/P1 或 ABF 违反属于 Rework。专项不修改候选、ABF、风险或账本。
