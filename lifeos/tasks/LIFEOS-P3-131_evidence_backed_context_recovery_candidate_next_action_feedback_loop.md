# LIFEOS-P3-131｜Evidence-backed Context Recovery 与 Candidate Next Action 用户闭环

## 任务信息

- 任务 ID：`LIFEOS-P3-131`
- 风险等级：`L2`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / User Task Contract Confirmed / Awaiting Task-card Delivery`
- 主责 Agent／会话类型：Codex 工程执行会话；建议复用已结束的 P3-130 工程线会话，若其上下文或工作状态不清楚则新建工程会话
- 所需执行能力：本地文件、Rust／JavaScript、SQLite、离线 actual Tauri、八项严格 IPC、固定合成数据、结构化 Evidence
- 是否需要独立评审：`Conditional`
- 独立评审触发理由：普通 L2 不因 P0 标签或 Tauri／IPC 自动触发；仅当 PM 无法复算关键 Evidence、发生候选／Evidence 污染或越权、Closure Cycle 后仍有关键争议，或用户明确要求时触发
- 适用治理：Governance V2 结果级任务；使用本任务卡内嵌 Acceptance Contract，不另建 ABF
- 用户一次性确认：2026-08-26，用户明确回复“确认并启动 P3-131 完整 Task Contract”；该确认覆盖本卡已展示的创建、候选复制、实现、构建、actual Tauri、八项 IPC、测试、Evidence、包内修正与 PM 验收

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只使用工作区任务根、唯一固定 `/private/tmp` 根、P3-130 只读候选以及全新合成 DB／固定非敏感文本；不访问 Pilot、真实个人数据、真实 DB／路径／文件、历史 Runtime 根、网络、云、第三方、凭据、Vault、产品模型或 Agent，不扩大能力。

本任务卡完整展示后，用户的一次“确认并启动”覆盖候选复制、实现、构建、actual Tauri 动态验证、八项 IPC、SQLite／audit 核对、同范围修正、Evidence／Manifest 和 PM 验收；合同内不再拆分确认。若执行中需要新增真实数据、不可逆动作、网络、权限／导出、风险／冻结／Stage 等未展示边界，必须停止并重新确认。

## Task Contract

### 1. 唯一用户结果

在 P3-130 已通过的 Project-backed Context Recovery 基础上，完成 V1 第一场景缺失的后半段：

`找回 Context → 基于可见 Evidence 返回零个或最多一个 Candidate Next Action → 用户确认／编辑后确认／拒绝／延后 → 已确认 Action 进入 Today → 用户记录完成结果 → Memory 可追溯 Derivation、Evidence、Feedback、Action 与结果 → 关闭重开后状态一致`

候选必须明确是系统派生的建议，不是用户原文、用户事实或已确认 Action。系统不得为了填满页面强行生成建议；证据不足时必须明确显示“暂时没有足够证据判断”。用户不确认时不得创建 Action，AI／系统不得替用户确认、完成或改变重要状态。

### 2. 固定只读输入

- Frozen 前向架构权威：`lifeos/architecture/LifeOS架构基线V1.0.md`，SHA-256 `1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236`
- P3-128 Application／Port 合同：`lifeos/architecture/LIFEOS-P3-128/application_port_contract.json`，SHA-256 `eacdb329d84262bd46e1102b3d95cfad82abdfd927fee81bc410ecb19f7e5387`
- P3-128 Context Resolver 合同：`lifeos/architecture/LIFEOS-P3-128/context_resolver_contract.json`，SHA-256 `6949e21b6c167611d9faaf1796ac1a1fe8bdfd62b15274c600ea619cd8097837`
- P3-128 Memory provenance 合同：`lifeos/architecture/LIFEOS-P3-128/memory_provenance.json`，SHA-256 `019c86f2578bb1658421d7a3fb9313530edb7d8e24b80540b12333d702a5a045`
- P3-130 accepted candidate：`lifeos/engineering/LIFEOS-P3-130/candidate/`，精确 75 个普通文件，全部只读
- P3-130 Engineering Final Manifest：`lifeos/engineering/LIFEOS-P3-130/evidence/FINAL_MANIFEST.json`，SHA-256 `539d5dc984afe51cbed63009599ae89d2923542a52256f087a8b158ffb076584`
- P3-130 PM Final Review：`lifeos/reviews/LIFEOS-P3-130_pm_final_review.md`，SHA-256 `098c54c91772ed3ba159bb127c6fc3035da00fdcee92326ead17ee457bdafd7f`
- P3-130 独立评审、Evidence、PM Evidence及 D-0529 失败历史全部只读；不得把工程侧合同外临时文件历史作为正 Evidence

执行方必须在复制前从 P3-130 Final Manifest 复核 75 个 candidate 文件的相对路径、bytes 和 SHA-256；任一不一致、额外文件、链接、非普通文件或历史 hash 冲突均在工程动作前 fail closed，不得自行修复 P3-130。

### 3. 允许范围

- 允许写入：
  - `lifeos/engineering/LIFEOS-P3-131/`
  - `lifeos/deliverables/LIFEOS-P3-131_evidence_backed_context_recovery_candidate_next_action_feedback_loop.md`
  - `/private/tmp/lifeos-p3-131-next-action-v1`
- PM 会话后续允许写入 P3-131 PM Review、PM Evidence及项目账本。
- 候选根：`lifeos/engineering/LIFEOS-P3-131/candidate/`
- Evidence 根：`lifeos/engineering/LIFEOS-P3-131/evidence/`
- 唯一临时根：`/private/tmp/lifeos-p3-131-next-action-v1`
- Runtime 根必须由构建时 `LIFEOS_RUNTIME_ROOT` 显式绑定到唯一临时根内的全新 run 子目录；不得使用默认、回退或历史根。
- 仅可将 P3-130 candidate 的 75 个已核验普通文件复制到 P3-131 candidate；P3-130及此前资产保持只读。
- 允许离线 actual Tauri 启动、固定合成 UI 操作、八项 IPC、SQLite／audit 只读核对、关闭重开、任务内构建缓存、自动测试、结构化 Evidence和同范围修正。

### 4. 固定合成场景

- Person：`person:synthetic-owner`
- Domain：`work`
- Project：`synthetic-lifeos-product`
- Context：`ctx:project:synthetic-lifeos-product`
- 有充分 Evidence 的原文：`整理 LifeOS Context Recovery 合成验收记录。`
- 固定 Candidate Next Action：`整理 LifeOS Context Recovery 合成验收记录。`
- 编辑后确认文本：`整理并复核 LifeOS Context Recovery 合成验收记录。`
- 固定完成结果：`已完成合成验收记录整理与复核。`
- 证据不足原文：`LifeOS Context Recovery 合成记录。`
- 每个 run 使用唯一全新 `capture.sqlite`，只存在于对应 task-local Runtime 根内。

固定场景必须至少覆盖：直接确认、编辑后确认、拒绝、延后、证据不足为零候选、已确认后完成、关闭重开。不得增加真实文本、真实标识、真实路径或其他数据集。

### 5. IPC 与实现边界

候选实际暴露的 Tauri command 必须恰好为以下八项：

1. `capture_record`
2. `get_today`
3. `runtime_status`
4. `confirm_capture_context`
5. `get_context_recovery`
6. `get_context_next_action`
7. `decide_context_next_action`
8. `record_action_result`

前五项保持 P3-130 严格请求／响应兼容。新增三项只服务本任务用户结果：

- `get_context_next_action`：严格 `{context_id}`；返回零个或最多一个候选，并包含 `candidate_id`、候选文本、内容身份、Derivation processor/version、完整 basis refs、Evidence 状态和“为什么”。本任务只允许确定性本地规则 `local_rule:p3-131-v1`，不得调用或冒充 AI 模型。
- `decide_context_next_action`：严格 `{candidate_id,decision:accept|edit_accept|reject|defer,edited_text?,idempotency_key}`；只有 `accept`／`edit_accept` 创建用户已确认 Action，其他处置只追加 Feedback，不创建 Action。
- `record_action_result`：严格 `{action_id,result:completed,result_text,idempotency_key}`；只能作用于已确认且尚未完成的 Action，结果、时间与审计追加写入；不得倒写用户原文或候选 Derivation。

实现遵循 `UI → Application → Domain → Ports → Adapters`。UI／resolver 不得直连 SQL、文件系统、网络、ModelPort 或 AgentPort。允许在未冻结的候选 SQLite 内实现最小 Derivation／Candidate／Feedback／Action／ActionResult 投影与 append-only audit；不得声明为 Schema/API 或 IPC 冻结。

### 6. 产品和视觉约束

- 直接继承 P3-130 的 Person-centered Tauri Shell、纯图标 Rail、DOM/CSS/Token、留白、字号、色彩和 Global AI 空间关系；不重新设计 UI。
- Candidate Next Action 在 Context Detail 中呈现；只有用户已确认且未完成的 Action 才进入 Today 的“用户已确认安排”，不得自动占用 `Today's Focus`。
- Memory Detail 必须显示 `Candidate/Derivation → Evidence → Source/Artifact`，并分别展示用户 Feedback、已确认 Action 和 Action Result；不得复制第二份原文权威。
- “为什么”必须指向实际 basis refs；Evidence 失效、权限失效或不足时不得继续显示可靠建议。
- Global AI 保持可达但本任务不调用模型、不新增 AI Workspace 能力。

### 7. 禁止范围

- 禁止第九项 IPC、generic SQL／path command、通用 Action API、clear/delete、export、权限设置、恢复、搜索／FTS、sync、网络、模型或 Agent 调用。
- 禁止 Pilot、真实 DB／路径／文本／文件、Vault、外部 Source、云／第三方、凭据、向量、健康推断、新 Domain 激活、跨领域优先级或外部用户。
- 禁止静默创建 Context、自动确认 Action、自动完成 Action、把候选写成用户事实、把本地规则标成 AI 判断，或在无 Evidence 时强行建议。
- 禁止修改 P3-130及此前任务、候选、交付物、Review、Evidence、Manifest或历史临时根。
- 禁止冻结 Schema/API、IPC、Runtime、工程基线、产品 IA、风险或 Stage；禁止关闭／重开 R-0052、进入 Stage 4或自动创建后继任务。
- 禁止调整 macOS 显示缩放、辅助功能或其他系统设置。

### 8. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | P3-130候选精确75文件复制，全部历史资产只读 | 复制前后路径／bytes／SHA-256及类型核对 | source lineage + history integrity |
| AC-02 | 前五IPC、Runtime root fail-closed、现有Context Recovery和零renderer plugin permission保持兼容 | strict DTO、配置负例、P3-130生命周期回归 | structured results + logs |
| AC-03 | 候选为系统派生内容，零或最多一个；basis、processor/version和“为什么”完整 | actual Tauri正向与不足Evidence场景 | action rows + provenance JSON |
| AC-04 | Evidence不足时返回零候选并显示固定披露，不创建Derivation／Action／Feedback副作用 | pristine disposable negative control | UI/IPC + DB/audit before/after |
| AC-05 | accept与edit_accept只通过显式用户决定创建Action；候选、编辑文本、用户确认身份分离 | actual Tauri UI→IPC→DB/audit | state chain + identity assertions |
| AC-06 | reject与defer只追加各自Feedback，不创建Action，不改变原文、Link或Context事实 | 正向、重复和冲突路径 | feedback rows + unchanged authority hashes |
| AC-07 | record result只作用于已确认开放Action；重复幂等，非法／冲突请求在变更前停止 | completed、duplicate、wrong-state controls | Action/Result/audit snapshots |
| AC-08 | 关闭重开后Context、Today、Memory恢复一致；Today只展示已确认开放Action且不自动占Today's Focus | actual App close/reopen，不以refresh替代 | PID/run log + correlated UI/IPC/DB |
| AC-09 | Memory完整回链Derivation、basis Evidence、Source/Artifact、Feedback、Action、Result，不复制原文权威 | DTO与持久状态核对 | provenance graph JSON + visible state |
| AC-10 | basis版本／generation／tombstone／Authorization／Link任一失效，候选立即不可靠或消失，且不残留新Action | 至少四类独立mutation | mutation results + no-write proof |
| AC-11 | unknown字段、非法ID、缺edited_text、对非开放Action写结果、idempotency冲突均在任何DB/audit变化前停止 | pristine disposable negative controls | structured errors + before/after hash |
| AC-12 | command恰好八项；UI／resolver无SQL、filesystem、network、Model或Agent路径 | source scan + runtime/capability assertion | command inventory + runtime_status |
| AC-13 | actual Tauri逐行动作覆盖直接确认、编辑确认、拒绝、延后、零候选、完成和关闭重开 | 动态闭环矩阵 | action log + UI/IPC/DB/audit correlation |
| AC-14 | 唯一临时根精确清理，工程Evidence保留，历史资产不变，Final Manifest非自指 | pre/post inventory + exact path checks | cleanup.json + Final Manifest |

Pass 公式：AC-01～AC-14 全部 PASS；P0/P1/Unknown/Not Implemented 为 0；P2 仅允许有明确理由且不影响唯一用户结果的非阻断项；无越权路径、真实数据、隐藏 IPC、历史漂移、身份混淆或未解释状态。

### 9. Evidence 合同

- Evidence 等级：`L2 actual Tauri`。
- 必须保留：可运行 runner、自动测试、actual-app action log、逐行 dynamic closure、严格 DTO 结果、DB／audit快照、失败前后 hash、mutation results、source lineage、history integrity、cleanup和非自指 Final Manifest。
- 每个实际动作必须关联同一 run 的 UI 状态、IPC 请求／响应、SQLite／audit 事实；截图不能单独证明持久化。
- 必须包含纯净 disposable control；汇总、静态扫描、测试总数或 UI fixture 不得替代逐行动态 Evidence。
- 执行侧提交前完成包内修正并报告 `P0/P1/P2/Unknown/Not Implemented`。

### 10. 清理、停止与新任务触发器

- `/private/tmp/lifeos-p3-131-next-action-v1` 在 Evidence 完成后按精确绝对路径清理并确认 absent；不得使用 glob、`find` 或宽前缀删除。
- 只清理本任务自己创建的临时根；不得访问、stat、hash、create或cleanup任何历史 Runtime 根。
- 以下任一情况立即停止并回 PM：需要改变 Frozen V1.0或核心语义；需要通用 Action／Context 实体冻结；需要真实数据／路径／模型／网络；需要第九项IPC；需要导出／删除／权限／恢复；无法建立 actual App 的 UI→IPC→SQLite/audit→UI关联。
- 同合同内的实现缺陷、测试、Evidence、Manifest、视觉接线和文案一致性直接包内修正，不拆微任务、不重复授权。
- 只有用户结果、能力、数据、入口、权限、风险、架构、Schema/API、冻结合同变化，或历史污染无法可信恢复时关闭并新建任务。

## 输入与最小启动包

必须完整读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/architecture/LIFEOS-P3-128/application_port_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/context_resolver_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/memory_provenance.json`
- `lifeos/engineering/LIFEOS-P3-130/evidence/FINAL_MANIFEST.json`
- `lifeos/reviews/LIFEOS-P3-130_pm_final_review.md`
- `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`

仅在固定输入或生命周期事实冲突时定向补读 P3-130 独立 Review／Evidence；不得全文扫描无关历史。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-131_evidence_backed_context_recovery_candidate_next_action_feedback_loop.md`
- 候选：`lifeos/engineering/LIFEOS-P3-131/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-131/evidence/`
- PM Review：由 PM 主会话在提交后创建
- 复跑：执行侧提供一条只写任务根和唯一临时根的 task-local 命令
- 聊天回复：结论、测试／Evidence摘要、五类计数、交付物路径、需 PM 决策事项

## PM 验收与关闭

- PM只按长期质量原则与AC-01～AC-14验收，不在提交后移动终点。
- 若未触发独立评审，PM Pass后按Governance V2自动`Accepted / Complete / Not Frozen`；无需用户逐任务采纳。
- 若出现独立评审触发事实，PM记录具体原因并在同一任务号下安排只读隔离复评，不新建微型评审任务。
- Pass不恢复工程基线、不关闭风险、不启用真实能力、不准入Stage 4；后继由PM另行规划。
