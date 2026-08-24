# LIFEOS-P3-107｜P3-104 + P3-106 组合候选全新隔离独立复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-107`；受控能力包：Yes。
- 能力包边界：只读复评固定 P3-106 三页 Tauri candidate 与字节继承的 P3-104 runtime；不修复候选、不触及账本、风险、冻结或阶段。
- 对应交付物：`lifeos/deliverables/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md`。
- 独立评审角色：独立 QA／安全与数据生命周期评审；协审视角：体验、可访问性、技术架构、数据／领域、AI 信任安全。
- 评审关卡：Gate 1–4；Gate 5 仅核对固定非敏感内部理解。
- 独立评审路径：用户于 2026-08-23 投递任务卡 `lifeos/tasks/LIFEOS-P3-107_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review.md`，ABF 为 `ABF-P3-107-v1`，SHA-256 为 `1088f7bcfa3a014c526ff3e13d5a9fe923053ddbc877938d362a3aa2b038acee`。
- 路由记录：任务要求 `gpt-5.6-terra`／`xhigh`、禁止降级。当前会话元数据已记录为该精确配置，见 `resume-1/current-configuration.json`；旧 `startup_configuration.json` 的 `sol`／`medium` 是 D-0436 已采纳 Blocked 的前次启动记录。本评审未使用降级、外部 Agent 或子任务转派。
- 评审结论：**Blocked**。

## 能力包独立性与回流规则

- 执行侧与评审侧隔离：Yes。本会话未参与 P3-104/P3-106 工程、提交 runner、Evidence 或 PM 验收；未导入、调用、复制或改写它们的 runner。
- 测试设计先于提交 runner：Yes。`resume-1/test-design.json` 于 `2026-08-23T22:10:23+08:00` 固定，SHA-256 `76101cd7961841163b553ced05655c599dd046232189d79560493e5a0e5956c7`；之后才阅读候选源码及提交结构化结果。
- 独立 runner／结构化结果／Manifest／复跑入口：已保留于 `lifeos/reviews/LIFEOS-P3-107/evidence/`。`independent_runner.py` SHA-256 为 `81cb1debc10c05ee7f77808590293364245116893435bc63d6d896720e9325a2`。
- 是否发现需要回包内整改的候选 P0/P1：未确认候选 P0/P1；但有 1 项 Evidence 时间语境 Unknown、9 行验收矩阵未实施，且实际 app 动态控制不可用。Blocked 不等于候选通过，也不建议据此对 P3-106 发起修复。
- 更新时间：2026-08-23（本任务执行时）。

## 本地动态 Evidence 预检

- 本任务不适用浏览器或 `file:` 预检；ABF 明确要求操作实际 Tauri app，浏览器、HTTP、DOM mock 均不可替代。
- 新鲜离线构建二进制以允许的 nominal SQLite fixture 启动时输出 `runtime_start status=restricted_offline db_scope=task_local`。但是 Computer Use 不能将原始二进制解析为可控制 app；为使其可访问而准备的临时 app 外壳启动后退出 `134`。
- 为启动既有本地 `.app` 并传入同一精确 fixture 的受控 GUI 启动请求，被执行环境以用量限制拒绝。拒绝明确禁止改用间接或规避路径，因此未继续尝试。
- 详情、未执行动作和不替代原则见 `resume-1/dynamic-blocker.json`（SHA-256 `ebc47b74a3b7049a03c794893ef806382377676d0e71294e83fe7b2e49dd7ea5`）。没有把 P3-106 既有截图、提交 PASS、静态焦点或刷新当成这轮动态 Evidence。

## 评审摘要

1. 固定 ABF 与 17 个固定候选／P3-104 provenance 输入 hash 均匹配；P3-106 的 lock、Cargo、runtime、main、capability 五文件与 P3-104 逐字节一致。
2. 一份全新 `work-r2` 副本在创建时无 `target`，在 `CARGO_NET_OFFLINE=true` 下完成 `cargo test --locked`、`cargo build --locked` 和 `cargo tauri build --debug -- --locked`，三项退出均为 0。
3. 静态独立反查仅见 `capture_record`、`get_today`、`runtime_status` 三项 command definition 与 renderer invoke；capability `permissions` 为 `[]`。资源扫描未见 remote asset、`img`／背景图 URL、base64／data 截图替代或非允许网络入口；配置中唯一 schema URL 被单独记录，非运行时资源。
4. 三张固定 1280×1024 actual-app Evidence 已和冻结 Stitch 图独立目视比对：共享桌面骨架、三态锚点、composer、来源／AI 关闭态与信息层级成立；受控候选使用有标签的中性占位，不是把参考图嵌入 UI。此结论仅覆盖 M-006，不能覆盖本轮运行中的响应式或键盘行为。
5. P3-106 Engineering Manifest 的 325 条目经独立 rehash 为 0 bad；P3-104 PM 和 P3-106 PM inventory 分别 8／2 条为 0 bad。P3-104 Engineering Manifest 中一个指向当前 PM Review 的历史哈希不匹配当前文件：记录为 `da83…`，当前为 `8d888…`。当前 PM Review 第 28 行说明该 Manifest 在 PM 更新 Review **前** 16/16 匹配，故它解释了差异的时间来源，却不能满足 ABF-M-003 的“当前逐项无 bad”字面条件；本项记为 Unknown，而非静默豁免或候选代码缺陷。
6. 关键 actual-app 生命周期、路径／类型／sidecar 反例、unknown IPC、响应式、Tab／Enter／skip／focus／reduced-motion、关闭重开和清理均没有独立动作闭环。依据 ABF fail-closed 规则，这些不是可忽略的 N/A。

## 已通过内容

- ABF 身份、任务投递边界、独立测试设计的先后顺序及固定输入 hash 的静态核对通过。
- `work-r2` clean build 的完整结果见 `resume-1/static-results.json`，测试／构建／Tauri debug build 日志均位于 `resume-1/logs/`；它们没有联网、没有修改 live candidate。
- 独立静态 IPC／capability／resource scan 通过。`prohibited_capability_tokens` 中的 `plugin` 是描述性 token 扫描结果，不是已授予 permission；实际 capability permission list 为空，报告未将这个文本扫描误称为权限。
- 固定三态图的结构性、高保真意图和内容身份检查通过。完整逐态观察、参考图与实际图 hash 位于 `resume-1/visual-review.json`。
- 已保护的旧 `/private/tmp/lifeos-p3-104-rework-static-results.json` 仅 lstat，前后均为 `type=Regular File,size=2176,mtime=1787473226,ctime=1787473226`；没有读取、hash、复制、覆盖或清理其内容。

## 关键问题

### K-01｜正常实际 app 控制不可用，动态闭环不能声称完成

这是 Blocked 的主因。任务卡和 ABF 要求在实际 Tauri app 中逐项操作，且明确禁止用浏览器／mock、已提交截图、静态 AX 或刷新代替。原始 debug 二进制可以启动，但无法由允许的 Computer Use attach；正常 GUI 启动路径遭执行环境拒绝后，继续绕行会违反该拒绝和 ABF 的 Evidence 诚实原则。因此 M-007 至 M-014 以及 M-016 的 required dynamic sub-actions 均为 Not Implemented。

### K-02｜历史 Manifest 对当前 PM Review 的时间语境差异

独立 `manifest_verifier.py` 不执行任何提交 runner。它复算 P3-104 Engineering／PM 与 P3-106 PM inventory，并保留了 P3-104 Engineering Manifest 中的一个当前不匹配。PM Review 自身解释其为“更新 Review 前”的历史快照，故没有证据证明 runtime 或 UI 被篡改；但 ABF-M-003 的固定、当前“无 bad”措辞缺少时间快照例外，不能写成 PASS。此处需要 PM 判断是维持历史叙述并在后续新 ABF 中明确时间化验证，还是以新的受控任务建立可复核历史快照；本评审不修改任一历史资产。

### K-03｜精确清理未完成

执行环境拒绝了精确临时路径清理，且禁止以替代删除方式达成同一目的。残留均在 ABF allowlist 内：`/private/tmp/lifeos-p3-107-review-work-r1`、`/private/tmp/lifeos-p3-107-review-work-r2`、`/private/tmp/lifeos-p3-104-p3-107-review-nominal-r1`。未使用 glob、prefix 或 broad cleanup。故 M-016 不可通过，路径台账已放入 Evidence Manifest。

## 必须整改项

- 本轮不授权、也不建议修改 P3-104/P3-106 候选。若 PM 希望继续，必须在可正常控制实际本地 app 且允许精确清理的执行环境中，使用新的明确任务投递／ABF 或由 PM 依法决定本任务的后续处理。
- 后续复评必须从实际 app 重新完成 M-007–M-014 的每一动态子动作：首次／repeat／conflict／注入失败、refresh 与真实 close/reopen、三页往返、unknown IPC／额外字段／未实现控件、路径／链接／hardlink／类型、四类 dangling 与 tamper、Tab／Enter／skip／focus／reduced-motion。
- PM 应明确 M-003 对“历史 Manifest 在 PM Review 之后更新”的可接受验证语义。没有新 ABF 或可复核历史快照，不得把这项 Unknown 重写为 PASS。

## 条件通过项

不适用。任务可选结论仅为 Pass／Rework／Blocked；本 Review 是 Blocked，未使用条件性措辞掩盖未验证内容。

## 冻结验收矩阵

| 行 | 结果 | 独立 Evidence／说明 |
|---|---|---|
| M-001 | PASS | ABF hash、授权和固定输入核对：`static-results.json` |
| M-002 | PASS | 先设计后读提交 runner：`test-design.json`、`.sha256` |
| M-003 | Unknown | 325 条 P3-106 Engineering rehash PASS；其余 inventory 见 `manifest-verification.json`；P3-104 历史 PM Review hash delta 如 K-02 |
| M-004 | PASS | `work-r2` 初始无 target；三项离线 locked command exit 0：`static-results.json`、logs |
| M-005 | PASS | 三 IPC、空 permission、provenance 和资源扫描：`static-results.json` |
| M-006 | PASS | 固定三态独立目视及抗截图／remote 反查：`visual-review.json` |
| M-007 | Not Implemented | 实际 app 原屏／700×760／滚动／composer／导航无法闭环 |
| M-008 | Not Implemented | 无实际首 capture、DB／audit／sentinel 闭环 |
| M-009 | Not Implemented | repeat、conflict、注入失败均未操作 |
| M-010 | Not Implemented | refresh、三页往返、真实 close/reopen 未操作 |
| M-011 | Not Implemented | unknown IPC、额外字段、未实现控件未实际操作 |
| M-012 | Not Implemented | path／link／hardlink／FIFO／目录／外部路径未操作 |
| M-013 | Not Implemented | dangling final/journal/wal/shm 与 tamper 未操作 |
| M-014 | Not Implemented | 实际 Tab／Enter／skip／focus／reduced-motion 未操作 |
| M-015 | PASS | 静态 remote、真实数据、截图嵌入／网络入口扫描为 0 |
| M-016 | Not Implemented | 精确 cleanup 被环境拒绝；残留台账非 0 |

冻结不变量 I-01、I-02、I-03、I-05、I-06 的静态部分可复核；I-04、I-07、I-08 至 I-14 不能因上述 Not Implemented／Unknown 达到 PASS。Pass 公式不成立。

## 关卡检查

- Gate 1 产品一致性评审：**未通过本轮关卡**。固定三态结构可接受，但实际屏幕适配、交互和恢复无独立动态证据。
- Gate 2 数据与来源评审：**未通过本轮关卡**。静态内容身份／来源关闭态合理，但 capture、审计、路径及失败持久化未实机复核。
- Gate 3 AI 权限与信任评审：**未通过本轮关卡**。静态显示 AI／外部能力关闭、renderer 最小 IPC，但未知 IPC／额外字段／未实现控件未实际动作。
- Gate 4 技术可行性评审：**未通过本轮关卡**。离线 locked clean build 成功，但实际 app 正常控制及 fail-closed 矩阵不完整。
- Gate 5 用户价值验证评审：**不作为 Pass**。仅固定非敏感内部受控理解，未接触真实用户或真实数据。

## 风险

- 不更新 `RISK_LOG.md`。`R-0040` 仍为 Open / Conditional；本轮静态 check 不足以关闭真实 Tauri/IPC 路径风险。`R-0051` 仍仅限既有受控关闭范围，未扩大；`R-0052` 仍 Open / Authorized Controlled Execution Boundary。
- 不关闭／重开风险，不冻结／恢复候选，不进入 Stage 4。本次 Blocked 不是 R-0040/R-0052 的关闭证据，也不是 P3-106 用户采纳的替代或否定结论。

## 需要 PM 决策

1. 接收本任务的 **Blocked** 结论，并决定是否在可控制实际本地 app、可进行精确清理的环境中创建新的独立复评；该动作需要新的任务投递和 ABF，不应把本轮未完成动态 Evidence 追记为 PASS。
2. 对 M-003 的历史 Manifest／后续 PM Review 更新关系作治理判断。若要改变其核对语义，应新建 ABF，不得回写或改动既有历史 Manifest 来制造当前一致性。
3. 对三条 ABF allowlist 临时残留安排拥有执行权限的维护方做**精确路径**清理并记录；不得授权 broad cleanup。此项不是用户数据、真实 DB 或风险关闭操作。

## 最终建议

不建议冻结、恢复工程基线、进入下一阶段或把候选宣称为独立 Pass。建议 PM 保全本轮 Evidence，承认静态／构建／固定视觉子集的正向结果，同时保留 `P0=0、P1=0、P2=0、Unknown=1、Not Implemented=9` 的 fail-closed 事实。待有合规的 actual-app 控制与清理环境后，再以新任务完成动态矩阵；在此之前不请求候选代码整改，也不改变 R-0040、R-0051、R-0052、冻结或 Stage 4 状态。

## 本地预检说明

未调用本地模型预检。原因是本任务是 P0 独立 Tauri／IPC／本地路径最终判断，且结果取决于实际 app 动态动作和 Evidence 真实性；本地模型摘要不能降低或替代该关卡。
