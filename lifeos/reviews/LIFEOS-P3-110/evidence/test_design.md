# P3-110 独立测试设计（冻结前置）

## 设计冻结与独立性

- 任务：`LIFEOS-P3-110`；ABF：`ABF-P3-110-v1`。
- 本文件只依据任务卡、Frozen ABF 和 L1 设计；编写时尚未读取 P3-109 的 runner、工具、动态结果或结论。
- 不复制、导入或执行 P3-107、P3-108、P3-109 的任何 runner、工具或动态 Evidence；本轮仅在 P3-110 允许目录编写独立 runner 和 Evidence。
- 候选及 P3-104 至 P3-109 历史资产全程只读。任何固定输入漂移、模型／离线工具／actual app／两种 native geometry 查询不可用、或 unit-path 执行前集合非空，均停止为 `Blocked`，不使用历史 Evidence 替代。

## 启动前门槛

1. 记录收到的任务卡绝对路径、会话类型、接收时间、任务规定的 `gpt-5.6-terra + xhigh` 路由以及会话可观察的实际配置；不能证实合规即不启动候选操作。
2. 重算并逐项记录 10 个 ABF 固定输入：P3-106 Manifest、write-path inventory、P3-109 PM Review、P3-109 PM Manifest、三张 Stitch 图与三张 P3-106 1280×1024 图。
3. 建立新旧读取顺序日志；只有本设计的 SHA-256 记录后，才阅读 P3-109 限定材料；旧 runner 永不执行。
4. 从 `write_path_inventory.json` 逐字取三条 ABF regex，且仅枚举 `/private/tmp` 直接子项名称并即时过滤。三个执行前集合必须为空；建立 cargo/test PID、时间和新路径台账。

## 独立执行策略

- 在 `/private/tmp/lifeos-p3-110-review-work-v1` 以正向 allowlist 构建候选副本；库存必须证明未带入任何历史 Evidence、runner、tests、tools 或非 allowlist 路径。
- 使用该副本、断网环境和任务允许的固定 ASCII 夹具，独立编写 P3-110 runner。Cargo 的 `--locked` test/build/bundle、actual unsigned debug app、三项 IPC 和所有写入仅限 ABF 枚举路径。
- 对每次动态操作记录命令／PID／时间、输入、预期、原始输出、before/after snapshot、截图及 SHA-256；不以 Markdown 自述或已有矩阵 status 作为通过输入。
- native geometry 仅采用两种 ABF 授权的只读 macOS API 查询相同 app 窗口；保存查询源码、原始输出、bundle/title/PID、解析过程。窗口原始态与 GUI resize 后均须实际三态操作，700×760 以 native outer points 判定。

## 16 行测试矩阵设计

| ABF 行 | 独立测试设计 | 核心原始 Evidence |
|---|---|---|
| M-001 | 授权、路由、会话隔离、ABF 和 10 项固定输入逐项重算 | `authorization.json`、`fixed-inputs.json` |
| M-002 | 写入本设计 hash 后才阅读 P3-109 限定材料，证明旧 runner 未执行 | `read_order.json`、test-design hash |
| M-003 | 重算 P3-106 Manifest、runtime provenance 和限定 P3-109 历史 hash | `manifest_verification.json` |
| M-004 | 正向 allowlist copy；枚举副本并拒绝 Evidence/runner/tests/tools | `copy_inventory.json` |
| M-005 | unit pre/during/post ledger；离线 locked test/build/bundle 与 network=0 | unit ledger、命令 raw logs |
| M-006 | 静态检查 runtime、三 IPC、capability、路径与锁定依赖 | `static_results.json` |
| M-007 | 对固定六张图逐态人工/程序化骨架、层级、锚点、身份和状态差异比较 | `visual/fixed-comparison.json` |
| M-008 | 实际 app 原窗口及 700×760 native outer frame 的三态、截图、滚动与动作可达性 | dual-API raw、AX、截图、scroll log |
| M-009 | 首次 capture 后核对 DB、audit、sentinel 与成功时序 | raw app log、before/after |
| M-010 | repeat、conflict、注入失败的幂等、拒绝和原子性 | 独立结果、before/after |
| M-011 | refresh、三页导航、close/reopen 后只从 backend 恢复权威状态 | app/process/DB raw Evidence |
| M-012 | 未实现控件、unknown IPC、extra fields 必须拒绝且零副作用 | denied matrix、raw logs |
| M-013 | 目录、软链、硬链、类型、dangling final、外部路径在变更前 fail-closed | boundary matrix、sentinel |
| M-014 | dangling journal/wal/shm、content/schema tamper 各自 fail-closed | negative matrix、before/after |
| M-015 | 实际 Tab、Enter、skip、focus；只读 reduced-motion 与 app 披露；隐私/网络 scan | a11y raw、system read-only、scan |
| M-016 | 从 raw Evidence 构造 payload，独立 semantic verifier 与六类 mutation；清理和非自指 Manifest | verifier/mutation raw、PAYLOAD_MANIFEST、cleanup、MANIFEST |

## Verifier 与退出纪律

- semantic verifier 直接解析 raw logs、snapshots、geometry、cleanup、unit ledger 与哈希，不信任 `pass`／`status` 或 Markdown。缺文件、hash 改变、cleanup/unit 残留、负向退出码为零、DB/audit 数错误、geometry 非 700×760 六类 mutation 必须逐一使 verifier 非零。
- 后处理只可逐条清理由本轮 PID、时间和台账归属的、精确匹配的 P3-110 路径或 unit regex 路径；不使用 wildcard、broad prefix，也不处理执行前项或归属不明项。
- 通过条件严格采用 ABF：I-01 至 I-14、M-001 至 M-016 和所有子动作通过，五类计数皆为零，且固定输入、历史、路径、清理、payload、mutation 与顶层 Manifest 全部可复算。否则按 ABF 分类为 Pass/Rework/Blocked 并交 PM 裁决。
