# LIFEOS-P3-121 Acceptance Basis Freeze｜P3-116 设计忠实继承与 P3-120 Runtime 组合收口

## 冻结信息

- 任务 ID：`LIFEOS-P3-121`
- ABF ID／版本：`ABF-P3-121-v1`
- 生效决策：`D-0485`
- 创建与冻结时间：2026-08-25 CST (+0800)
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes；尚未投递
- ABF 文件 SHA-256：由 PM 冻结后记录在最终任务卡与 D-0485；本文件不使用自指 hash。
- 正式 Rework：0/2

## 本轮唯一用户结果

在全新 P3-121 task-local 工程和全新合成 SQLite 中，将 P3-116 当前只读产品／视觉合同忠实实现到 P3-120 已通过的三 IPC Runtime 上，形成一个实际可启动、跨三个 viewport 自适应、核心页面与身份语义一致，并完整保持合成 capture→Today→重复→第二次 capture→刷新→关闭重开和失败关闭行为的组合候选。

本轮不冻结产品需求、视觉资产、IA、架构、Schema/API、IPC、Runtime、工程基线、风险或阶段；不证明真实个人使用、模型智能、生产可靠性或 Stage 4 准入。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-121/`、指定 P3-121 交付物、P3-121 本地预检报告、`/private/tmp/lifeos-p3-121-combined-v1`。
- 允许数据：固定文本 `P3-121 synthetic capture one`、`P3-121 synthetic capture two` 和固定 Person/Work/Health/Context/Memory fixtures；不得接受真实输入。
- 允许入口／接口：本地 Tauri `.app`；仅 `capture_record`、`get_today`、`runtime_status`；renderer 无直接 DB/file/shell/network。
- 允许工具／环境：本地离线 Rust/Cargo/Tauri、SQLite、代码测试、actual-app runner、task-local screenshot／state trace；不把 GUI 自动注入作为 Pass 依赖。
- 严格只读：P3-116 与 P3-120 全部任务、ABF、候选、Review、Evidence；两份架构／IA 输入；项目账本；Pilot 和历史真实使用资产。
- 禁止能力：真实 DB／路径／文本、clear/export/权限/恢复、Vault/文件导入、模型、网络、云／第三方、同步、多设备、L3、外部用户、通知中心、新 IPC、新 Schema/API、风险／冻结／阶段变化。
- 投递前额外用户确认：**Completed**。用户已明确确认上述两个写入根、全新合成 DB、仅三项既有 Tauri/IPC，并禁止 Pilot、真实 DB、真实路径、真实文本、网络和模型。授权 Evidence：`lifeos/reviews/LIFEOS-P3-121/pm_evidence/authorization/MANIFEST.md`。

## 冻结输入

PM 已在冻结前重新复算下列输入；专项仍须在创建 P3-121 工程或临时根前再次复算：

| 输入 | Frozen SHA-256 |
|---|---|
| `lifeos/architecture/LifeOS高保真原型IA-V1.0.md` | `adcc9daf3b8f0fcf27a13176eabb1581c6079d47b48a26ee88cbaba209704243` |
| `lifeos/architecture/LifeOS架构基线V1.0.md` | `2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32` |
| `lifeos/prototypes/LIFEOS-P3-116/index.html` | `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b` |
| `lifeos/prototypes/LIFEOS-P3-116/styles.css` | `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3` |
| `lifeos/prototypes/LIFEOS-P3-116/app.js` | `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f` |
| `lifeos/prototypes/LIFEOS-P3-116/fixtures.js` | `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93` |
| `lifeos/prototypes/LIFEOS-P3-116/visual_contract.json` | `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49` |
| `lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md` | `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393` |
| `lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md` | `bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467` |
| `lifeos/prototypes/LIFEOS-P3-116/state_machine.json` | `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc` |
| `lifeos/reviews/LIFEOS-P3-116_pm_review.md` | `09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa` |
| `lifeos/engineering/LIFEOS-P3-120/evidence/final-manifest-closure/FINAL_MANIFEST.json` | `b766c79063caa5e170fe87d88f9642ed2a5e549b1bedf93a6946529647b4d1d2` |
| `lifeos/reviews/LIFEOS-P3-120_pm_reacceptance_review.md` | `23b57a5c524ce723dc666320c92e2bf6198bf94e27b4edd44c85151ad058ecf9` |
| `lifeos/tasks/LIFEOS-P3-121_source_allowlist.md`（P3-120 candidate 70/70） | `99220398b03baad9acdc3d88d38ab822ed661b926ec740317c5f05ce6e14a242` |
| `lifeos/reviews/LIFEOS-P3-121/pm_evidence/authorization/MANIFEST.md` | `f983d431d4897701728fdb0e30b2667ccfed20fc715037365b21b66d21492cf1` |

P3-116 历史截图、raw AX、旧动态闭环与 P3-120 历史 DB／运行目录不属于 positive input。旧 Evidence 仅作为只读治理历史，不能证明 P3-121 Pass。

## 引用的 L1 长期原则

- L1-1 数据主权：仅全新 P3-121 根、唯一临时根和合成 DB；Pilot／真实路径绝对禁止。
- L1-2 内容身份：持久化 capture、只读 fixture、AI Observation/Inference/candidate、用户确认内容不得混淆。
- L1-3 生命周期完整：视觉适配后首次、重复、刷新、关闭重开和失败语义不得退化。
- L1-4 失败关闭：UI／IPC／DB／path/type 任一失败不得留下持久化或伪成功状态。
- L1-5 用户控制：capture、Context、Action、Decision 与重要状态变化必须显式；AI 不替用户确认。
- L1-6 审计可信：页面、动作、IPC、DB、时间顺序、screenshot 和结果语义一致。
- L1-7 Evidence 诚实：实际 App 每页／状态分别执行；源码、旧截图或相邻动作不得批量推定。
- L1-8 历史保全：P3-116/P3-120 全部只读；只从 positive allowlist 逐文件建立新候选。
- L1-9 授权不漂移：不得继承 Pilot、真实输入、P3-116 browser 或 P3-119 GUI 注入授权。
- L1-10 可复核性：固定 source/candidate hash、viewport、fixture、runner、逐行 Evidence 与 Manifest 可重复。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权、模型、输入、positive allowlist 与目录不漂移 | P0 | 正式 Frozen hash、会话、模型、目录全部匹配后才创建 | 动作前 Blocked/Not Pass |
| ABF-I-02 | P3-116 产品／视觉合同忠实继承 | P1 | Shell、层级、空间、气质、身份色和禁止元素逐项满足 | Not Pass |
| ABF-I-03 | 三 viewport 由应用自适应 | P1 | 1280×1024、1160×768、700×760 同 DOM 可用，无裁切主操作 | Not Pass |
| ABF-I-04 | 核心页面／展开态与交互可达 | P1 | Today、Me、Contexts、Memory、两详情、Global AI、Workspace、弱化 Settings 均实际到达 | Not Pass |
| ABF-I-05 | 语义、用户权威与无障碍不退化 | P0 | 身份、Evidence、确认／拒绝／纠正、键盘、focus、reduced-motion 均成立 | Not Pass |
| ABF-I-06 | 仅三项 IPC；renderer 无直接敏感能力 | P0 | command/capability/renderer inventory 精确匹配 | Not Pass |
| ABF-I-07 | 全新合成 DB 与 task-local path/type 边界 | P0 | canonical、ancestor link、DB/sidecar type 负测全通过 | Not Pass |
| ABF-I-08 | capture→Today、重复、刷新、关闭重开完整 | P0 | 实际 renderer→IPC→DB→UI 逐层一致 | Not Pass |
| ABF-I-09 | 失败先于变更且 UI 不伪成功 | P0 | DB/sentinel/UI before-after 不变，错误准确 | Not Pass |
| ABF-I-10 | Global AI/Workspace 无模型、网络或执行 | P0 | disabled/offline 清晰；无 model/network/tool calls | Not Pass |
| ABF-I-11 | 禁止能力保持关闭 | P0 | clear/export/permission/recovery/file/new IPC 均不存在或拒绝 | Not Pass |
| ABF-I-12 | Evidence 逐状态真实、非空、版本绑定 | P0 | 每行真实 App、viewport、结果、截图/log hash、candidate hash 一致 | Not Pass |
| ABF-I-13 | 历史保全、Final Manifest 与精确清理 | P0 | 历史 hash 不变，Manifest 完整，唯一临时根不存在 | Not Pass |

## 冻结验收矩阵

每行必须独立生成结构化结果；视觉与 Runtime 可在同一实际 App 时序中执行，但不得以总计数、源码扫描或一张 screenshot 批量替代。

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | P3-121 根均不存在 | 复算正式输入、模型、授权、allowlist | 全匹配后才创建 | P3-116/P3-120 history | P121-M001 | fixed inputs + inventory |
| ABF-M-002 | build | positive copy | locked offline test/build/bundle | exit 0，无外部写／网 | history/Pilot | P121-M002 | build logs + inventory |
| ABF-M-003 | shell | empty synthetic DB | 逐项检查 Icon Rail、IA、Global AI、Settings、禁止元素 | 合同全满足 | DB empty | P121-M003 | state result + screenshots |
| ABF-M-004 | Today | empty DB | 正常／合法空／证据不足状态 | Focus≤1，不凑建议，层级与气质成立 | DB empty | P121-M004 | three state rows |
| ABF-M-005 | Me | fixture | Work/Health 深度、其他未启用、理解纠正／撤回入口 | Person 主体与身份清晰 | fixture/read-only | P121-M005 | state + screenshot |
| ABF-M-006 | Contexts/detail | fixture | 三关系分组、打开 detail、建议创建待确认 | 非 Kanban/Domain 栏；Context 继承可见 | fixture/read-only | P121-M006 | navigation trace |
| ABF-M-007 | Memory/detail | fixture | identity→Understanding→Derivation→Evidence→Source | 可追溯、断链／不足诚实 | fixture/read-only | P121-M007 | trace + screenshot |
| ABF-M-008 | Global AI/Workspace | fixture | 打开 panel、检查三 Context、移除 Health、展开 Workspace | 同一全局入口；移除临时；模型关闭 | persistent data | P121-M008 | interaction trace |
| ABF-M-009 | responsive | pristine app states | 1280×1024、1160×768、700×760 逐页抽样 | 同 DOM 自适应，主操作／composer 可达 | semantics/data | P121-M009 | viewport matrix |
| ABF-M-010 | accessibility | app states | Tab/Shift+Tab/Enter/Escape、focus、reduced-motion | 实际交互成立，不以静态替代 | data | P121-M010 | key trace + state |
| ABF-M-011 | runtime status | app running | 调用 `runtime_status` | local/offline/synthetic/allowed commands 准确 | DB | P121-M011 | IPC + UI result |
| ABF-M-012 | capture one | empty DB | 提交 fixed synthetic one | 一次成功；原文身份保存；Today 可见 | fixture content | P121-M012 | IPC/DB/UI before-after |
| ABF-M-013 | repeat | one row | 重复相同提交 | 冻结幂等语义，不双重伪成功 | first row | P121-M013 | repeat + DB diff |
| ABF-M-014 | capture two | one row | 提交 fixed synthetic two | 第二条独立保存，顺序／身份正确 | first row | P121-M014 | IPC/DB/UI |
| ABF-M-015 | refresh/reopen | two rows | 刷新；关闭并重开同一合成 DB | 两条仍可见，无身份漂移；status 正确 | DB hash/rows | P121-M015 | two separate lifecycle rows |
| ABF-M-016 | path/type | pristine disposable | escape、ancestor link、DB/sidecar link/dir/special | 变更前拒绝，DB/sentinel/UI 不变 | canonical copy | P121-M016 | mutation results |
| ABF-M-017 | IPC/DB failure | pristine disposable | invalid input、open/write/read failure | fail closed，无伪成功／半提交 | DB/sentinel | P121-M017 | before-after + errors |
| ABF-M-018 | prohibited | candidate + app | 扫描／尝试 clear/export/permissions/recovery/file/network/model/new IPC | 不存在或明确拒绝 | DB/files/network | P121-M018 | static + runtime negatives |
| ABF-M-019 | visual evidence integrity | completed app states | 验证截图尺寸、非空、状态语义、candidate/build/viewport 绑定 | 无空白、错态、复用冒充或旧图替代 | candidate/Evidence | P121-M019 | semantic verifier + mutations |
| ABF-M-020 | final | completed/failed | 复算 history/candidate/Evidence，关闭 app，精确清理 | Final Manifest 成立；history unchanged；root absent | all history | P121-M020 | final results + cleanup |

## Evidence 合同

- runner／测试：fixed-input preflight、positive source inventory、static boundary、Rust/unit/integration、actual-app replay、viewport/state closure、keyboard/reduced-motion、path/type/failure mutations、visual semantic verifier、Final Manifest、cleanup。
- 逐行结构化结果：M-001～M-020 每行记录操作、输入、viewport、actual result、before/after、Evidence path/hash 与结论；M-004、M-009、M-015 内的明确子动作必须分别成行。
- 视觉 Evidence：只接受当前 P3-121 actual app；每张绑定 candidate/build hash、页面／状态、viewport、时间与操作；重复 hash 对应不同可观察状态时 fail closed。
- Runtime Evidence：实际 renderer→IPC→DB→UI；unit test、源码扫描或 screenshot 不得单独证明持久化。
- source/history hash：P3-116/P3-120 固定输入 before/after；不得读取或复活受污染历史内容。
- Manifest：非自指，分层覆盖 source、current candidate、tests/tools、results/logs/screenshots、deliverable、authorization 与 cleanup；当前和历史交付物不得混淆。
- mutation：pristine disposable control 先 PASS，再验证缺页、错 viewport、空白／复用图、candidate mismatch、遗漏 current delivery、extra file、DB 变化后失败回执等 fail closed。
- 临时清理：只精确清理 `/private/tmp/lifeos-p3-121-combined-v1`；目标必须在清理前校验为本任务固定根。

## 计数与 Pass 公式

- P0：越界数据／目录／能力、失败后变更／伪成功、身份或用户权威混淆、新 IPC／网络／模型、Evidence 造假／版本错绑、历史漂移或错误清理。
- P1：冻结 Shell／页面／信息层级／空间关系／响应式／可访问性未满足，或生命周期用户结果退化。
- P2：不影响冻结用户结果的轻微视觉／文案偏差；本轮 Pass 仍要求 0，或由 PM 明确移出 L2 后另建候选，不得静默接受。
- Unknown：任一视觉状态、viewport、IPC、DB、路径、生命周期、lineage、历史保全或 cleanup 无法独立复核。
- Not Implemented：任一不变量、矩阵行、必要子动作、runner、结果或 Evidence 缺失。
- Pass 公式：I-01～I-13、M-001～M-020 及其必填子动作全部 PASS；P0/P1/P2/Unknown/Not Implemented 全零；无静默 N/A。
- 允许 N/A：仅当前 OS 确实不支持的 special-file 子类型，且同风险已有实际等价负测，并逐行说明。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-121 candidate、测试、Evidence、Manifest 或同一视觉／Runtime 适配；ABF、用户结果、目录、数据、三 IPC、Schema/API、风险不变。
- 必须新建任务：改变视觉用户结果、目录、数据类型、IPC/capability、Schema/API、架构、核心语义、真实路径/DB、模型、网络、禁止能力、风险/冻结/阶段；ABF 实质修改；两轮正式 Rework 未通过；Evidence/历史污染不可恢复。
- Blocked：正式 Frozen 工具链离线不可用或系统无法启动 actual Tauri App，且不改变 ABF 无法安全恢复；任何替代入口前停止。

## 候选基线与只读保全

- 冻结时 P3-121 候选不存在；PM 已确认工程根与唯一临时根均不存在。
- PM 已复算全部输入，并从 P3-120 Final Manifest 的 `current_candidate` 分层生成 70/70 positive allowlist；表内 path/bytes/hash 与磁盘逐项一致。
- P3-116/P3-120 全部资产只读；P3-116 历史截图和 raw AX 不是 Pass 输入；P3-120 的 actual-app Evidence 只证明历史 Runtime，不替代 P3-121 当前执行。
- 允许变化仅限正式授权后的 P3-121 工程、交付物、P3-121 local precheck 和唯一临时根。

## 启动前质疑窗口

- 执行方是否提出歧义：N/A；尚未投递。执行方在任何工程动作前仍拥有一次标准质疑窗口。
- PM 处理：用户已确认精确 synthetic-only Tauri/IPC 执行边界；PM 已重算固定输入、生成 70/70 positive allowlist、确认两根不存在并冻结本文件。
- 最终冻结版本：`ABF-P3-121-v1`。
- 专项会话开始后不得实质修改正式 ABF；如需修改，关闭 P3-121 并新建任务。
