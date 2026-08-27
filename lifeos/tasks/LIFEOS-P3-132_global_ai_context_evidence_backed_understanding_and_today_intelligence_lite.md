# LIFEOS-P3-132｜Global AI Context、Evidence-backed Understanding 与 Today Intelligence Lite

## 任务信息

- 任务 ID：`LIFEOS-P3-132`
- 风险等级：`L2`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / User Task Contract Confirmed / Awaiting Task-card Delivery`
- 主责 Agent／会话类型：Codex 工程执行会话；可复用已结束的 P3-131 工程线会话，若其上下文或工作状态不清楚则新建工程会话
- 所需执行能力：本地文件、Rust／JavaScript、SQLite、离线 actual Tauri、十一项严格 IPC、固定合成数据、结构化 Evidence
- 是否需要独立评审：`Conditional`
- 独立评审触发理由：普通 L2 不因 P0、Tauri、IPC 或 ModelPort 接口自动触发；仅当 PM 无法复算关键 Evidence、出现越权／污染、Closure Cycle 后关键结论仍有争议、候选拟转长期冻结基线，或用户明确要求时触发
- 适用治理：Governance V2 结果级任务；使用本任务卡内嵌 Acceptance Contract，不另建 ABF
- 用户一次性确认：2026-08-26，用户在完整 Task Contract 未变化时明确回复“开始”；本确认覆盖创建、候选复制、实现、构建、actual Tauri、十一项 IPC、测试、Evidence、包内修正与 PM 验收

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只使用工作区新任务根、唯一固定 `/private/tmp` 根、P3-131 只读候选以及全新合成 DB／固定非敏感文本。任务只实现离线可替换 ModelPort 合同及合成适配器，不调用真实模型。禁止访问 Pilot、真实个人数据、真实 DB／路径／文件、历史 Runtime 根、网络、云、第三方、凭据、Vault、真实模型或 Agent，不扩大能力。

本 Task Contract 完整展示且未变化时，用户回复“创建”“采纳并创建”或“开始”，即一次性授权创建、候选复制、实现、构建、actual Tauri 动态验证、十一项 IPC、SQLite／audit 核对、同范围修正、Evidence／Manifest 与 PM 验收。合同内不再拆分确认。若执行中需要真实数据、真实模型、网络、权限／导出、删除／恢复、风险／冻结／Stage 等未展示边界，必须停止并重新确认。

## Task Contract

### 1. 唯一用户结果

在 P3-131 已完成的 `Context Recovery → Candidate Next Action → 用户处置 → Today／Memory` 合成闭环上，完成下一段可见产品体验：

`Global AI 明确展示 Person + Page + Selection Context → 用户可临时移除 Context → 离线可替换 ModelPort 合成适配器基于有效 Evidence 返回零或最多一条 Observation 与零或最多一条 Suggestion → 用户确认／编辑确认／拒绝／纠正／忽略 → Today Intelligence Lite 只从可信输入给出零或一个 Today's Focus 与零或一条 LifeOS noticed → 关闭重开后持久 Feedback、Action、Today 与 Memory provenance 一致`

本任务验证的是 Global AI／ModelPort／Evidence／Feedback／Today 的产品与架构合同，不宣称真实 AI 已启用。页面必须显著标注 `Offline synthetic adapter`；不得把固定适配器输出冒充真实模型判断。证据不足时必须显示“暂时没有足够证据判断”，没有可靠焦点时必须显示“今天没有特别需要你处理的事情”。

### 2. 固定只读输入

- Frozen 前向架构权威：`lifeos/architecture/LifeOS架构基线V1.0.md`，SHA-256 `1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236`
- P3-128 Application／Port 合同：`lifeos/architecture/LIFEOS-P3-128/application_port_contract.json`，SHA-256 `eacdb329d84262bd46e1102b3d95cfad82abdfd927fee81bc410ecb19f7e5387`
- P3-128 Context Resolver 合同：`lifeos/architecture/LIFEOS-P3-128/context_resolver_contract.json`，SHA-256 `6949e21b6c167611d9faaf1796ac1a1fe8bdfd62b15274c600ea619cd8097837`
- P3-128 Memory provenance 合同：`lifeos/architecture/LIFEOS-P3-128/memory_provenance.json`，SHA-256 `019c86f2578bb1658421d7a3fb9313530edb7d8e24b80540b12333d702a5a045`
- P3-131 accepted candidate：`lifeos/engineering/LIFEOS-P3-131/candidate/`，精确 75 个普通文件，全部只读
- P3-131 Engineering Final Manifest：`lifeos/engineering/LIFEOS-P3-131/evidence/FINAL_MANIFEST.json`，SHA-256 `4341c989a9199f7cb860518ba76d304923ea0571a47be3205c983198685c80a8`
- P3-131 source lineage：`lifeos/engineering/LIFEOS-P3-131/evidence/source-lineage.json`，SHA-256 `95de01185b27014e6b3517cd47d60d72de7c3cee2cac6ed7627675b919d194e6`
- P3-131 PM Review：`lifeos/reviews/LIFEOS-P3-131_pm_review.md`，SHA-256 `ff90316e927bd9eb0fd265aacf25f8f4c858751ac81e8b36af38bfddac03f01a`
- P3-131 PM verification：`lifeos/reviews/LIFEOS-P3-131/pm_evidence/acceptance/verification.json`，SHA-256 `c26bdd26c1b1833b2c3e8979ac8b3d25523bd6334e366d8e433ea44b287c6a1d`

执行方必须在复制前从 P3-131 Final Manifest 复核 75 个 candidate 文件的相对路径、bytes、SHA-256 与普通文件类型。任一不一致、额外文件、链接、非普通文件或历史 hash 冲突均在工程动作前 fail closed；不得自行修复 P3-131。P3-131 两项非阻断 P2 必须在新 Evidence 工具中避免复现：动态证据必须绑定可复核的当前 bundle/run 身份，scanner 不得以无上下文子串或表格自报 PASS 作为结论。

### 3. 允许范围

- 允许写入：
  - `lifeos/engineering/LIFEOS-P3-132/`
  - `lifeos/deliverables/LIFEOS-P3-132_global_ai_context_evidence_backed_understanding_and_today_intelligence_lite.md`
  - `/private/tmp/lifeos-p3-132-global-ai-today-lite-v1`
- PM 会话后续允许写入 P3-132 PM Review、PM Evidence 和项目账本。
- 候选根：`lifeos/engineering/LIFEOS-P3-132/candidate/`
- Evidence 根：`lifeos/engineering/LIFEOS-P3-132/evidence/`
- 唯一临时根：`/private/tmp/lifeos-p3-132-global-ai-today-lite-v1`
- Runtime 根必须由构建时 `LIFEOS_RUNTIME_ROOT` 显式绑定到唯一临时根内的全新 run 子目录；不得使用默认、回退或历史根。
- 仅可将 P3-131 candidate 的 75 个已核验普通文件复制到 P3-132 candidate；P3-131及此前全部资产只读。
- 允许离线 actual Tauri、固定合成 UI 操作、十一项 IPC、SQLite／audit 只读核对、关闭重开、任务内构建缓存、自动测试、结构化 Evidence及同范围包内修正。

### 4. 固定合成场景

- Person：`person:synthetic-owner`
- Domain：`work`
- Project：`synthetic-lifeos-product`
- Context：`ctx:project:synthetic-lifeos-product`
- Page Context：`today` 或 `context_detail`
- Selection Context：P3-131 固定 Capture 或已确认 Action 的内容身份引用，不复制原文
- 有充分 Evidence 原文：`整理 LifeOS Context Recovery 合成验收记录。`
- 固定 Observation：`当前 Context 已具备继续推进所需的已确认 Evidence。`
- 固定 Suggestion：`继续完成 LifeOS Context Recovery 合成验收记录的复核。`
- 编辑确认文本：`继续完成并复核 LifeOS Context Recovery 合成验收记录。`
- 纠正文本：`该 Context 仍需补充一项合成 Evidence 后再推进。`
- 证据不足原文：`LifeOS Context Recovery 合成记录。`
- 固定适配器标识：`offline_synthetic_model:p3-132-v1`
- 每个 run 使用唯一全新 `capture.sqlite`，只位于对应 task-local Runtime 根。

至少覆盖：Context Inspector 完整显示、Selection 临时移除／恢复、充分 Evidence、证据不足、确认、编辑确认、拒绝、纠正、忽略、已有开放 Action 成为唯一 Today's Focus、无开放 Action 的诚实空状态、LifeOS noticed、关闭重开。

### 5. IPC 与实现边界

候选实际暴露的 Tauri command 必须恰好为以下十一项：

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

前八项保持 P3-131 严格请求／响应兼容；`get_today` 只允许兼容追加 `todays_focus`、`lifeos_noticed` 和诚实空状态字段。

- `assemble_global_ai_context`：严格 `{page,selection_ref?,removed_context_kinds?}`。仅返回当前请求可用的 Person、Page、Selection、Domain、Context、Memory/Source refs、Authorization 摘要和 permissions；临时移除只影响当前请求，不写持久状态。
- `get_evidence_backed_understanding`：严格 `{context_id,page,selection_ref?,removed_context_kinds?,request_id}`。先完成授权、Source/Artifact/version/generation/tombstone/Link/Evidence 检查，再通过 `ModelPort` 调用唯一离线合成适配器；返回零或最多一条 Observation、零或最多一条 Suggestion，并包含内容身份、processor/version、完整 basis refs、Evidence 状态、“为什么”和 `synthetic_adapter=true`。
- `decide_understanding_feedback`：严格 `{understanding_id,decision:confirm|edit_confirm|reject|correct|ignore,edited_text?,idempotency_key}`。只追加带身份 Feedback；`edit_confirm`／`correct` 必须提供文本。不得修改 Capture、Source、Artifact、Derivation，不得自动创建 Action、Decision、用户事实或 Memory 原文副本。

实现必须遵循 `UI → Application → Domain → Ports → Adapters`。新增 `ModelPort` 只定义可替换合同；唯一实现为 task-local `OfflineSyntheticModelAdapter`，不得调用网络、系统模型、CLI 模型、云、第三方或 Agent。UI／resolver 不得直连 SQL、文件系统、网络、Model adapter 或 AgentPort。不得声明为 Schema/API、IPC、ModelPort 或产品资产冻结。

### 6. Today Intelligence Lite 规则

- `Today's Focus` 必须为零或一个，只能从用户已确认且仍开放的 Action 中确定性选择；Observation、Suggestion、Candidate 或未确认内容不得直接成为 Focus。
- 多个开放 Action 的测试夹具必须按稳定、可解释的 `confirmed_at / action_id` 规则选一个；不得按 Domain 平均分配。
- `LifeOS noticed` 本任务最多一条，只能显示当前仍有效、具有完整 basis refs 的 Observation 或 Suggestion，并显著标识为系统派生／离线合成适配器输出。
- 用户 `reject` 或 `ignore` 后，对应 understanding 不再进入 noticed；`correct` 后显示用户纠正状态，不把纠正文本改写为系统观察。
- 无开放 Action 时 `todays_focus=null` 并显示“今天没有特别需要你处理的事情”。无可靠 Understanding 时显示“暂时没有足够证据判断”。
- Today 允许完全为空；不得为了填满页面强行生成 Focus 或 noticed。

### 7. 禁止范围

- 禁止第十二项 IPC、generic SQL／path command、通用模型 prompt、通用 Action／Context API、clear/delete、export、权限设置、恢复、搜索／FTS、sync、网络、真实模型或 Agent 调用。
- 禁止 Pilot、真实 DB／路径／文本／文件、Vault、外部 Source、云／第三方、凭据、向量、Health 真实数据或推断、新 Domain 激活、跨领域智能、外部用户。
- 禁止静默创建 Context、自动确认／完成 Action、把 Observation／Suggestion 写成用户事实、把固定适配器冒充真实 AI、持久化临时移除选择、复制原文到 Memory。
- 禁止修改 P3-131及此前任务、候选、交付物、Review、Evidence、Manifest或历史 Runtime 根。
- 禁止冻结 Schema/API、IPC、ModelPort、Runtime、工程基线、产品 IA、风险或 Stage；禁止关闭／重开 R-0052、启用真实能力、进入 Stage 4或自动创建后继任务。
- 禁止调整 macOS 显示缩放、辅助功能或其他系统设置。

### 8. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | P3-131候选精确75文件继承，历史全部只读 | 复制前后路径／bytes／SHA-256／类型核对 | source lineage + history integrity |
| AC-02 | 前八IPC、Runtime root、P3-131生命周期保持兼容 | strict DTO、root负例、P3-131回归 | structured results + logs |
| AC-03 | command恰好十一项，renderer／resolver无SQL、filesystem、network或adapter直连 | 语义source scan + runtime/capability assertion | command inventory + scan findings |
| AC-04 | Global AI Context准确显示Person／Page／Selection及使用的数据、权限与证据引用 | actual Tauri逐项观察 | context assembly JSON + visible state |
| AC-05 | Selection／Context临时移除只影响当前请求，刷新／重启后不改变持久事实 | before/after request与DB hash | request-local removal chain |
| AC-06 | ModelPort可替换边界成立，唯一适配器离线且显著标注synthetic | contract test、capability和UI核对 | port/adapter inventory + visible label |
| AC-07 | 充分Evidence时至多一条Observation和一条Suggestion，identity／basis／why完整 | actual Tauri + IPC + DB/audit | understanding rows + provenance |
| AC-08 | Evidence不足或Context被移除时零可靠Understanding、固定披露且无副作用 | pristine disposable controls | UI/IPC + before/after hash |
| AC-09 | confirm/edit_confirm/reject/correct/ignore只追加各自Feedback并保持内容身份分离 | 五个独立actual Tauri run | feedback rows + authority hashes |
| AC-10 | Understanding Feedback不自动创建Action／Decision／用户事实；P3-131 Action仍只经原显式路径创建 | DB/audit与UI核对 | no-auto-action assertions |
| AC-11 | Today Focus为0或1且仅来自开放已确认Action；排序稳定，不按Domain配额 | 零／一／多Action夹具 | Today rows + deterministic order |
| AC-12 | LifeOS noticed最多一条、basis有效；reject/ignore抑制，correct保持用户纠正身份 | actual Tauri反馈后刷新 | noticed state chain |
| AC-13 | 无Focus／无noticed时诚实空状态，不强行生成内容 | 空DB与不足Evidence run | visible empty states + structured result |
| AC-14 | 关闭重开后Feedback、开放Action、Focus、noticed与Memory provenance一致 | actual App quit/reopen，不以refresh替代 | run identity + UI/IPC/DB/audit correlation |
| AC-15 | Source/version/generation/tombstone/Authorization/Link失效及非法DTO／幂等冲突均在写前停止 | 至少五类mutation和纯净负例 | mutation + no-write proof |
| AC-16 | 唯一临时根精确清理，工程Evidence保留，历史不变，Final Manifest非自指且动态bundle/run可复核 | pre/post inventory + hash重算 | cleanup.json + Final Manifest |

Pass 公式：AC-01～AC-16 全部 PASS；P0/P1/Unknown/Not Implemented 为 0；P2 仅允许有明确理由且不影响唯一用户结果的非阻断项；无真实模型／网络、越权路径、隐藏 IPC、历史漂移、内容身份混淆、自动确认或未解释状态。

### 9. Evidence 等级

- 本任务采用：`L2 actual Tauri`。
- 必须保留：可运行 runner、自动测试、每个 actual-app run 的当前 bundle／run identity、逐项动态闭环、严格 DTO 结果、Global AI Context、Understanding／Feedback／Today／Memory DTO、SQLite／audit快照、失败前后hash、mutation、source lineage、history integrity、cleanup和非自指 Final Manifest。
- 每个实际动作必须关联同一 run 的 UI 状态、IPC 请求／响应、SQLite／audit事实；静态字符串、测试总数、表格自报PASS或未绑定的bundle路径不得替代实际动作。
- source scanner 必须区分真实API调用和普通标识符子串；closure verifier必须验证结构化 Evidence及hash，而非只读取Markdown中的`PASS`文本。
- 执行侧提交前完成同范围包内修正并报告 `P0/P1/P2/Unknown/Not Implemented`。

### 10. 清理、停止与新任务触发器

- `/private/tmp/lifeos-p3-132-global-ai-today-lite-v1` 在 Evidence 完成后按精确绝对路径清理并确认 absent；不得使用 glob、`find` 或宽前缀删除。
- 只清理本任务自己创建的临时根；不得访问、stat、hash、create或cleanup任何历史 Runtime 根。
- 以下任一情况立即停止并回 PM：需要真实模型／网络／凭据；需要改变 Frozen V1.0或核心领域语义；需要通用 Model／Action／Context API；需要真实数据、Health真实推断、第十二项IPC、导出／删除／权限／恢复；无法建立 actual App 的 UI→IPC→SQLite/audit→UI关联。
- 同合同内的实现缺陷、测试、Evidence、Manifest、视觉接线、scanner/verifier和文案一致性直接包内修正，不拆微任务、不重复授权。
- 只有用户结果、能力、数据、入口、权限、风险、架构、Schema/API、核心语义或冻结合同变化，或历史污染无法可信恢复时关闭并新建任务。

## 输入与最小启动包

必须完整读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/architecture/LIFEOS-P3-128/application_port_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/context_resolver_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/memory_provenance.json`
- `lifeos/engineering/LIFEOS-P3-131/evidence/FINAL_MANIFEST.json`
- `lifeos/reviews/LIFEOS-P3-131_pm_review.md`
- `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`

仅在固定输入或生命周期事实冲突时定向补读 P3-131 Engineering Evidence／PM Evidence；不得全文扫描无关历史。

## 执行要求

1. 开始前检查工作区已有修改，保全用户资产。
2. 复制前核验 P3-131 固定候选；任何冲突在工程动作前 fail closed。
3. 只执行 Task Contract 范围；不得修改 PM 账本、风险、冻结或 Stage。
4. 完成实现、自动测试、actual Tauri、结构化 Evidence 和包内修正后再提交 PM。
5. 不把 OfflineSyntheticModelAdapter 的结果外推为真实模型能力或真实用户价值。
6. 不自动创建后续任务。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-132_global_ai_context_evidence_backed_understanding_and_today_intelligence_lite.md`
- 候选：`lifeos/engineering/LIFEOS-P3-132/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-132/evidence/`
- PM Review：由 PM 主会话在提交后创建
- 复跑：执行侧提供一条只写任务根和唯一临时根的 task-local命令
- 聊天回复：结论、测试／Evidence摘要、五类计数、交付物路径、需 PM 决策事项

## PM 验收

- PM只按长期质量原则与AC-01～AC-16验收，不在提交后移动终点。
- 若未触发独立评审，PM Pass后按Governance V2自动`Accepted / Complete / Not Frozen`；无需用户逐任务采纳。
- 若出现独立评审触发事实，PM记录具体原因并在同一任务号下安排只读隔离复评，不新建微型评审任务。
- Pass不证明真实模型、真实数据、自用价值、风险关闭、工程基线恢复或Stage 4准入；后继由PM另行规划。

## 一次性授权方式

用户已在本完整 Task Contract 未变化时回复“开始”，任务已获一次性创建与执行授权。现在只需将最终任务卡绝对路径投递至专项会话；不得再重复确认同一边界。
