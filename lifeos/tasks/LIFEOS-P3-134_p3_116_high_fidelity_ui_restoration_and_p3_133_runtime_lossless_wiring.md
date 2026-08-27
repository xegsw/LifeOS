# LIFEOS-P3-134｜P3-116 高保真产品 UI 恢复与 P3-133 Runtime 无损接线

## 任务信息

- 任务 ID：`LIFEOS-P3-134`
- 风险等级：`L2`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / User Task Contract Confirmed / Awaiting Task-card Delivery`
- 主责 Agent／会话类型：Codex 工程执行会话；建议新建工程会话，避免继续继承 P3-130～P3-133 已发生视觉漂移的实现假设
- 所需执行能力：本地文件、HTML／CSS／JavaScript、Rust／SQLite、离线 actual Tauri、十一项严格 IPC、三档应用视口、结构化视觉与 Runtime Evidence
- 是否需要独立评审：`Conditional`
- 独立评审触发理由：本任务为 synthetic-only L2，不因 P0 或 actual Tauri 自动触发；仅当 PM 无法复算视觉／Runtime Evidence、发生越权或历史污染、Closure Cycle 后视觉一致性仍有争议、候选拟转长期冻结基线，或用户明确要求时触发
- 适用治理：Governance V2 结果级任务；使用本任务卡内嵌 Acceptance Contract，不另建 ABF
- 用户一次性确认：2026-08-27，用户在完整 Task Contract 未变化时明确回复“开始”；本确认覆盖候选复制、实现、构建、离线 actual Tauri、十一项 IPC、全新合成 DB、三档视觉验证、测试、Evidence、包内修正与 PM 验收

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只允许在新任务工程根和唯一固定 `/private/tmp` 根内，以 P3-116 高保真原型源码与 P3-133 已验收 Runtime 候选为双只读输入，使用全新合成 DB 和固定非敏感文本完成离线 actual Tauri 整合。禁止访问 Pilot、真实 DB／路径／文本、网络、模型、凭据、第三方或外部目标，不授权扩大能力。

本任务只恢复产品视觉与 Runtime 的正确组合关系，不回滚架构，不推翻 P3-133 的功能／安全验收，也不追溯改写 P3-116、P3-130～P3-133 的历史结论。

## Task Contract

### 1. 唯一用户结果

用户获得一个可在 actual Tauri 中运行的 LifeOS 组合候选：

`P3-116 的 Person-centered 高保真 DOM／CSS／视觉 Token／页面与空间关系 + P3-133 已验证的本地 Runtime／SQLite／十一 IPC／失败关闭行为`

最终 App 必须重新呈现 P3-116 的完整产品外观，而不是工程验证工作台：窄纯图标 Rail、Today／Me／Contexts／Memory 一级 IA、弱化 Settings、常驻 Global AI、Context Detail、Memory Detail、AI Workspace、原有留白／字号／色彩／卡片密度和三档响应式均保留。Runtime 只替换数据与状态来源，不得重写页面结构、缩减页面数量、改变视觉层级或加入调试 Dashboard。

本任务不接入真实模型。P3-135 多模型 Work Intelligence 路线顺延，P3-134 完成前不创建、不实现。

### 2. 固定双只读输入

#### 2.1 产品／视觉权威输入

- Frozen 前向架构权威：`lifeos/architecture/LifeOS架构基线V1.0.md`，SHA-256 `1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236`
- P3-116 实际 HTML：`lifeos/prototypes/LIFEOS-P3-116/index.html`，SHA-256 `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b`
- P3-116 实际 DOM／交互源码：`lifeos/prototypes/LIFEOS-P3-116/app.js`，SHA-256 `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f`
- P3-116 实际 CSS／Token：`lifeos/prototypes/LIFEOS-P3-116/styles.css`，SHA-256 `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3`
- P3-116 fixture：`lifeos/prototypes/LIFEOS-P3-116/fixtures.js`，SHA-256 `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93`
- P3-116 visual contract：`lifeos/prototypes/LIFEOS-P3-116/visual_contract.json`，SHA-256 `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49`
- P3-116 interaction contract：`lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md`，SHA-256 `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393`
- P3-116 state machine：`lifeos/prototypes/LIFEOS-P3-116/state_machine.json`，SHA-256 `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc`
- P3-116 IA reconciliation：`lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md`，SHA-256 `bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467`

P3-116 的历史截图／AX／runner／Evidence 不作为本任务正 Evidence；本任务必须从上述固定源码在新鲜隔离环境中生成新的参考渲染和对比结果。P3-116 历史任务仍保持 `Closed / Not Frozen`，本合同只把用户本轮明确指定的实际源码作为 P3-134 的视觉继承基线。

#### 2.2 Runtime／安全权威输入

- P3-133 accepted candidate：`lifeos/engineering/LIFEOS-P3-133/candidate/`，精确 75 个普通文件、0 个链接，全部只读
- P3-133 Closure-2 Final Manifest：`lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/FINAL_MANIFEST.json`，SHA-256 `697d2a788e177b259bed741b8c257bcd3dbdabe550b02b1ddff947b2a2633d35`
- P3-133 Closure-2 source lineage：`lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/source-lineage.json`，SHA-256 `35d18652df5fac1c63224996a5e2f40e8fa9de2278ce8aa3ff5f283d9de16ec0`
- P3-133 independent re-review：`lifeos/reviews/LIFEOS-P3-133/re-review-1/independent_review.md`，SHA-256 `2ff4c246a5913bc3a591e0b3489367577ccc353f29512177070d20efab75bf21`
- P3-133 final PM Review：`lifeos/reviews/LIFEOS-P3-133_pm_review.md`，SHA-256 `5bb5f7bcebd249cd6069b21685ae53338474747714ceffeb1852754770584e8b`

执行方必须在任何复制或构建前复核两组输入的路径、普通文件类型、bytes 与 SHA-256。任一固定输入漂移、额外文件、链接、非普通文件或历史冲突必须在工程动作前 fail closed；不得自行修复历史输入。

### 3. 允许范围

- 允许写入：
  - `lifeos/engineering/LIFEOS-P3-134/`
  - `lifeos/deliverables/LIFEOS-P3-134_p3_116_high_fidelity_ui_restoration_and_p3_133_runtime_lossless_wiring.md`
  - `/private/tmp/lifeos-p3-134-ui-restoration-v1`
- PM 会话后续允许写入 P3-134 PM Review、PM Evidence 与项目账本。
- 候选根：`lifeos/engineering/LIFEOS-P3-134/candidate/`
- Evidence 根：`lifeos/engineering/LIFEOS-P3-134/evidence/`
- 唯一临时根：`/private/tmp/lifeos-p3-134-ui-restoration-v1`
- Runtime 根必须由构建时 `LIFEOS_RUNTIME_ROOT` 显式绑定到唯一临时根内的全新 run 子目录；每个场景使用新的合成 `capture.sqlite`。
- 允许复制 P3-133 的 75 文件候选到 P3-134，再以 P3-116 的实际 UI 源码恢复 UI；所有改动只发生在 P3-134 candidate。
- 允许离线 actual Tauri、固定合成 UI 操作、十一项 IPC、SQLite／audit 只读核对、关闭重开、三档应用视口、键盘与 reduced-motion 验证、自动测试、结构化视觉 Evidence、同范围包内修正。
- 允许新增清晰的 UI state／Runtime adapter 层，但其职责只能是将 Runtime DTO 映射到 P3-116 已有页面节点和交互，不得成为第二套页面渲染器或通用 IPC／SQL／path 接口。

### 4. 强制视觉继承合同

- 一级 IA 必须保持：`Today / Me / Contexts / Memory`；Settings 仅为 Rail 底部弱化图标；AI 不是一级页面。
- Rail 必须恢复 P3-116 的 SVG 纯图标、Tooltip、当前页状态和窄宽度；禁止文字 Rail、`T/G/M/R` 字符导航、宽 Sidebar、通知铃铛、账户头像和 Profile 区。
- P3-116 `styles.css`、`fixtures.js`、`visual_contract.json`、`interaction_contract.md`、`state_machine.json` 与 `ia_reconciliation.md` 在候选中必须 byte-identical 继承；如确需改变任一文件，必须在工程动作前停止并回 PM，不得以“实现需要”为由自行漂移视觉基线。
- P3-116 的 page renderer、semantic landmarks、class names、卡片分组和 Global AI 空间关系必须直接继承。允许的差异只包括：Runtime 数据绑定、明确的 loading／error／empty 状态、Tauri script 引入、无布局影响的 `data-*`／ARIA 属性及事件 adapter。
- 运行状态不得通过新增大卡片、调试 receipt、工程编号、IPC 列表或 JSON dump 占用产品主界面；技术诊断只进入 Evidence。
- Global AI 底栏、右侧渐进面板与 AI Workspace 必须保持同一入口关系；Context Inspector 继续展示 Person／Page／Selection／权限／Evidence refs，临时移除只影响当前请求。
- 视觉风格继续为克制、轻量、大量留白、个人空间、Apple/macOS-adjacent；使用系统字体、原有字号／tracking／leading、低饱和 identity 色和单层材料权重，不新增 Dashboard 墙。
- 动效必须从当前可见状态开始、可被输入打断；非手势普通过渡默认无弹跳。`prefers-reduced-motion: reduce` 下使用短淡化或静态切换，禁止位移／弹性；不得要求用户修改 macOS 系统设置。

### 5. 页面、状态与 Runtime 映射

必须在同一 P3-116 DOM 体系中至少覆盖以下稳定状态，不得删页或用一个工程工作台替代：

1. Today normal：Runtime 的已确认开放 Action 映射为最多一个 Today's Focus；可靠 Understanding 映射为最多一条 LifeOS noticed。
2. Today empty：无开放 Action 时显示“今天没有特别需要你处理的事情”。
3. Today insufficient：无可靠 Evidence 时显示“暂时没有足够证据判断”，不凑建议。
4. Me：保留“现在的我／正在关注／长期视角／LifeOS 对我的理解”结构；未接入的内容必须标为固定合成或尚未接入，不得冒充 Runtime 事实。
5. Contexts active／watching／past：P3-133 当前 Project-backed Context 映射到正确状态；未持久化的展示项保持明确 synthetic 身份。
6. Context Detail：保留“现在 → Next → 最近发生 → LifeOS understands → Related／Evidence”；当前 Context 驱动 Runtime 调用。
7. Memory list／filter：保留七类身份和 Evidence Browser 结构。
8. Memory Detail connected／source unavailable：沿 Understanding → Derivation → Evidence → Source／Artifact 回溯；断链不产生可靠建议。
9. Global AI panel closed／open：Person／Page／Selection 可见，临时移除不持久化。
10. AI Workspace：Conversation + Work + Context Inspector 空间关系保留；产品对象仍标明 Observation／Suggestion／Candidate／Decision 身份。
11. Quick Capture modal：输入必须先于 busy/render 读取；调用 `capture_record` 后由用户显式决定 Context／Action 路径。
12. Context candidate modal、Domain activation Gate、Settings 与 reduced-motion 状态继续可达。

对于 P3-133 尚无真实持久化来源的 Me／Health／多 Context／完整 Memory 展示，只允许保留 P3-116 固定非敏感 synthetic fixture并显著披露，不得新建 IPC、Schema、表或伪造真实 Runtime 能力。

### 6. Runtime／IPC 不变量

候选实际暴露的 Tauri command 必须恰好保持 P3-133 的十一项：

1. `capture_record`
2. `get_today`
3. `runtime_status`
4. `confirm_capture_context`
5. `get_context_recovery`
6. `get_context_next_action`
7. `decide_context_next_action`
8. `record_action_result`
9. `assemble_global_ai_context`
10. `get_evidence_backed_understanding`
11. `decide_understanding_feedback`

- Rust Runtime、SQLite schema、DTO、audit、capability、CSP、`LIFEOS_RUNTIME_ROOT`、幂等、3条／200字符 real-mode限制和模型禁用语义必须保持请求／响应兼容。
- 本任务 actual Tauri 只运行 `offline synthetic` 模式；不得创建或访问 Pilot-3，也不得复用 P3-133 真实 DB。
- UI 只能通过受控 Runtime adapter 调用上述 typed IPC；不得直连 SQL、文件系统、网络、模型、Agent 或 generic invoke。
- 任何非法路径、缺失 Runtime root、链接链、错误文件类型、既有 DB、DTO 错误、幂等冲突、第四条输入、过长输入或 stale Evidence 必须在任何文件／DB变化前停止。
- 不允许第十二项 IPC，也不允许 clear／delete／export／restore／permission／generic path／generic SQL／generic model command。

### 7. 禁止范围

- 禁止重新设计 P3-116 页面、缩减页面集合、改变 IA、Rail、Global AI 空间关系、卡片密度、视觉 Token或三档响应式策略。
- 禁止把 P3-133 简化工作台或 P3-130～P3-133 任一后继页面作为视觉输入；它们只提供 Runtime／安全行为。
- 禁止访问、stat、hash、复制、打开或清理 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-3` 及其 `capture.sqlite`；禁止读取任何真实文本。
- 禁止网络、云、第三方、真实模型、本地模型、Agent、凭据、Vault、外部 Source、Health 真实数据或推断、新 Domain 激活、跨领域智能。
- 禁止修改 P3-116、P3-133及此前任务的候选、交付物、Review、Evidence、Manifest或任何历史 Runtime 根。
- 禁止删除、覆盖或迁移真实资产；禁止修改风险、关闭 R-0053、冻结产品／UI／Runtime／IPC／Schema/API／工程基线、进入 Stage 4或自动创建 P3-135。
- 禁止调整 macOS 显示缩放、减少动态效果或其他系统设置。

### 8. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | P3-116八项视觉输入与P3-133候选75文件／关键历史hash在执行前精确匹配，历史只读 | 路径／bytes／SHA-256／类型与pre/post inventory | fixed-inputs + source-lineage + history-integrity |
| AC-02 | P3-116六项强制byte-identical视觉合同文件保持不变，候选无第二套样式或页面系统 | byte/hash核对 + source inventory | visual-source-lineage |
| AC-03 | 一级IA、纯图标Rail、Global AI、完整页面／状态集合与P3-116语义DOM／class／landmark一致 | baseline与candidate DOM signature逐状态对比 | 逐状态DOM matrix + diff allowlist |
| AC-04 | 三档actual-app视口1280×1024、1160×768、700×760均保持原布局策略、主操作和Global AI可达 | actual Tauri native content bounds + WebView/DOM geometry | 三档截图 + geometry JSON |
| AC-05 | 同synthetic fixture下候选与新鲜P3-116参考渲染无结构漂移，视觉差异仅在允许的数据绑定区域 | computed tokens、关键节点bounds、masked pixel/perceptual diff | visual comparison report + images |
| AC-06 | Today normal／empty／insufficient、Me、Contexts、Context Detail、Memory、Memory Detail、AI panel、AI Workspace及modals全部可操作 | actual Tauri逐状态导航与断言 | page-state matrix + action receipts |
| AC-07 | Runtime只替换数据／状态来源，不新增调试卡、JSON dump、工程工作台或改变页面密度 | DOM／text inventory + visual inspection | no-debug-ui assertion |
| AC-08 | 恰好十一IPC，DTO／SQLite／audit／capability／CSP／root／幂等与P3-133兼容 | source scan、contract tests、command inventory | runtime regression results |
| AC-09 | Capture在busy/render前读取原始输入，Context／Action／Feedback均需用户显式处置 | actual Tauri正负路径 + DB/audit关联 | UI→IPC→DB→UI chain |
| AC-10 | Today Focus只来自开放已确认Action；noticed只来自有效basis；空／不足状态诚实 | 零／一／多Action和stale Evidence场景 | Today structured states |
| AC-11 | Me／Health／多Context／未持久化Memory均明确synthetic或未接入，不冒充真实Runtime | visible identity与数据来源核对 | authority-label matrix |
| AC-12 | Global AI Context继承Person／Page／Selection，临时移除不写持久状态，关闭重开后一致 | request-local前后与DB hash | context state chain |
| AC-13 | 非手势动效克制且可中断；reduced-motion、键盘、focus-visible、Escape和窄屏可达 | CSS media query + actual keyboard／motion run | accessibility/motion results |
| AC-14 | 非法路径／链接链／文件类型／既有DB／DTO／幂等／额度／stale Evidence均写前失败关闭 | pristine disposable mutations | mutation + sentinel／DB unchanged proof |
| AC-15 | 刷新、关闭重开后Runtime状态、页面选择、Focus、Context、Action与Memory refs一致 | actual App quit/reopen，不以refresh替代 | run identity + correlated state |
| AC-16 | 唯一临时根精确清理，工程Evidence保留，历史不变，Final Manifest非自指且可复算 | pre/post inventory + hash重算 | cleanup.json + Final Manifest |

Pass 公式：AC-01～AC-16 全部 PASS；`P0/P1/Unknown/Not Implemented=0`；P2 仅允许有明确理由且不影响唯一用户结果的非阻断项。任何页面集合缩减、视觉结构漂移、文字 Rail、调试工作台、隐藏 IPC、真实资产触达、历史漂移、自动确认或未解释的 Runtime 状态均不得 Pass。

### 9. Evidence 等级

- 本任务采用：`L2 actual Tauri + structured visual comparison`。
- 必须保留：执行前固定输入核对、P3-116新鲜参考渲染、逐状态DOM signature、computed token与关键几何、三档actual-app截图／native bounds／DOM bounds、十一IPC inventory、UI→IPC→SQLite／audit→UI关联、刷新／重启、负例／mutation、source lineage、history integrity、cleanup与非自指Final Manifest。
- 视觉结论不得仅由“看起来一致”、单张截图或静态CSS hash得出；必须同时验证 DOM／class／landmark、computed style／关键bounds和新鲜参考图。
- Runtime结论不得仅由单元测试、源扫描或UI文案得出；必须绑定当前bundle/run的actual Tauri动作、IPC与SQLite／audit事实。
- 执行侧提交前必须完成同范围包内修正并报告 `P0/P1/P2/Unknown/Not Implemented`。

### 10. 清理、停止与新任务触发器

- `/private/tmp/lifeos-p3-134-ui-restoration-v1` 在Evidence完成后按精确绝对路径清理并确认absent；不得使用glob、`find`或宽前缀删除。
- 只清理本任务自己创建的临时根；不得探测或清理Pilot-3、P3-133真实DB或任何历史Runtime根。
- 以下任一情况立即停止并回PM：固定输入漂移；必须修改P3-116六项强制byte-identical视觉合同；需要第十二项IPC、Schema/API变化、真实数据／模型／网络、系统设置、产品IA变化或风险／冻结／Stage决策；无法建立同一actual-app run的视觉与Runtime关联。
- 同合同内的DOM恢复、Runtime adapter、样式接线、测试、Evidence、Manifest、scanner/verifier、响应式和文案一致性问题直接包内修正，不拆微任务、不重复授权。
- 只有用户结果、能力、数据、入口、权限、风险、架构、Schema/API、核心语义或冻结合同变化，或历史污染无法可信恢复时关闭并新建任务。

## 输入与最小启动包

必须完整读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- P3-116上述八项固定产品／视觉输入
- `lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/FINAL_MANIFEST.json`
- `lifeos/engineering/LIFEOS-P3-133/evidence/closure-2/source-lineage.json`
- `lifeos/reviews/LIFEOS-P3-133_pm_review.md`
- `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`

仅在固定输入、Runtime生命周期或视觉基线事实冲突时定向补读P3-133 Closure-2／独立复评Evidence；不得全文扫描无关历史，不得读取Pilot-3或真实文本。

## 执行要求

1. 开始前检查工作区已有修改并保全用户资产。
2. 先复核固定双输入，再创建P3-134候选或临时根；任何漂移先fail closed。
3. 先建立P3-116新鲜参考渲染与机器可读DOM／视觉签名，再实施Runtime接线，避免以完成后的候选自证视觉标准。
4. UI必须由P3-116结构主导；P3-133只提供Runtime／安全行为。
5. 完成实现、自动测试、actual Tauri、三档视觉、结构化Evidence、负例和包内修正后再提交PM。
6. 不修改PM账本、风险、冻结或Stage；不自动创建后继任务。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-134_p3_116_high_fidelity_ui_restoration_and_p3_133_runtime_lossless_wiring.md`
- 候选：`lifeos/engineering/LIFEOS-P3-134/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-134/evidence/`
- PM Review：由PM主会话在提交后创建
- 复跑：执行侧提供一条只写P3-134工程根和唯一临时根的task-local命令
- 聊天回复：结论、视觉／Runtime Evidence摘要、五类计数、路径、需PM决策事项

## PM 验收

- PM只按长期质量原则与AC-01～AC-16验收，不在提交后移动终点。
- PM必须分别给出“视觉继承”和“Runtime回归”结论；任一不通过，任务整体不Pass。
- 若未触发独立评审，PM Pass后按Governance V2自动`Accepted / Complete / Not Frozen`，无需用户逐任务采纳。
- 若出现独立评审触发事实，PM记录具体原因并在同一任务号下安排只读隔离复评，不新建微型评审任务。
- Pass不证明真实模型、多模型、Health深度智能、真实Pilot兼容、风险关闭、产品冻结或Stage 4准入。

## 一次性授权方式

用户已在本完整Task Contract未变化时明确回复“开始”，任务已获得一次性创建与执行授权。现在只需将最终任务卡绝对路径投递至专项工程会话；不得再重复确认合同内边界。

## D-0553 最终收口执行指令

本节不改变唯一结果、范围、数据、权限、架构、十一IPC、Acceptance Contract或Pass标准，只改变工程提交节奏，终止把包内修正拆成多轮PM交付。

### 单次终局提交

- P3-134继续作为唯一结果任务，不创建P3-135或新的修复任务。
- Closure-1、Closure-2、Closure-3全部转为只读历史，不再覆盖、改写或作为当前候选的正证明。
- 工程会话从当前候选继续，在内部完成“修正 → fresh验证 → 发现缺陷 → 再修正 → 全量重跑”，不得再向PM提交Partial、Not Pass、中间截图或单项进展包。
- 下一次PM只接收以下两种终局结果之一：
  1. `Final Pass Candidate`：AC-01～AC-16逐项PASS，`P0/P1/Unknown/Not Implemented=0`；或
  2. `Blocked`：已穷尽本合同允许的task-local probe、测试、actual-Tauri与替代实现路径，仍存在不能由工程会话消除的外部能力阻断，并提供可复核停止证据。
- 普通失败、测试红灯、视觉差异、runner缺陷、Manifest问题、当前候选缺陷或Evidence遗漏都属于包内修正，不得作为Blocked或提前提交理由。

### 本次必须一次关闭的已知项

1. 修复并fresh验证当前post-patch Quick Capture；任何强制视口下不得出现空白、缺文案、缺控件、遮挡或AX与视觉不一致。
2. 对最终candidate而非pre-patch版本，在1280×1024、1160×768、700×760完成任务卡全部页面／状态／键盘／motion／关闭重开的actual-Tauri动作矩阵、native bounds与DOM geometry。
3. 使用同fixture P3-116 reference与最终candidate完成逐状态DOM/class/landmark matrix、明确diff allowlist及masked pixel/perceptual comparison。
4. 完成AC-10零／一／多Action、同时间tie-break、stale Evidence、刷新及重启的UI→IPC→DB→audit闭环。
5. 完成AC-14全部独立disposable fixture：非法路径、目录链接链、文件类型、既有DB、DTO、幂等、第四条、超200字符、stale及未知IPC；逐例证明写前停止、sentinel／DB不变且无残留。
6. 默认只读verifier必须同时校验Final Manifest、AC-01～AC-16、必需Evidence角色和五类计数；任何非PASS或缺项必须exit 1。不得再次出现整体Not Pass而verifier Pass。

### 最终Evidence组织

- 新的唯一当前Evidence根：`lifeos/engineering/LIFEOS-P3-134/evidence/final-closure/`。
- 内部失败尝试仅保留在`final-closure/work/`并在最终Manifest中按失败历史角色明确标注，不得用作正Evidence。
- 最终稳定Evidence、默认只读verifier和非自指Final Manifest位于`final-closure/`；所有正Evidence必须绑定同一最终candidate hash。
- 提交前工程会话必须自行运行默认verifier并得到exit 0，复核临时根精确absent，再更新主交付物为`Final Pass Candidate`。
- 若未达到上述条件，继续在工程会话内部工作，不向PM提交路径。
