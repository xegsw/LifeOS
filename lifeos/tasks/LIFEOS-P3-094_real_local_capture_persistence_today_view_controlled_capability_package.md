# LIFEOS-P3-094｜真实本地捕获、持久化与今日页展示受控能力包

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。用户已明确确认本任务可使用**新的本地 SQLite 数据库**和用户在任务执行期间明确输入的数据，完成“本地捕获 → 本地持久化 → 今日页展示”的真实本地闭环。

操作仅限本任务指定的隔离工作区、task-local SQLite 数据库和用户主动输入的数据，用于防御性软件工程、缺陷修复与本地回归验证。不得访问既有个人文件、外部目标、真实凭据或第三方系统；不涉及网络、云、Tauri/IPC、Vault、同步、多设备、文件导出、外部用户、未授权访问或安全控制规避。

## 任务信息与授权

- 任务 ID：LIFEOS-P3-094
- 优先级：P0
- 任务类型：受控真实本地能力包。
- 唯一能力边界：用户主动输入的本地捕获记录，写入新的 task-local SQLite 数据库，在同一隔离目录生成仅供本地展示的“今日页”内部渲染视图。
- 明确授权：新的本地 SQLite 数据库；用户在执行期间主动输入的数据；同一任务的本地持久化、重启复读、今日展示、失败披露、删除／清理验证与 Evidence。
- 包内允许工作：在新隔离目录完成实现、回归、必要补测、Evidence 整理和文案对齐。
- 禁止事项：不得读取／导入任何既有个人文件或数据库；不得联网、使用 HTTP、云、模型、第三方、Tauri/IPC、Vault、同步、多设备或文件导出；不得写入用户指定路径以外的真实文件。内部生成的 task-local `today.html` 仅是应用展示工件，不构成导出，不得复制到用户目录或作为分享文件。
- 必须独立处理：风险关闭／重开、工程基线恢复、Schema/API 或关键资产冻结、真实文件导出、Tauri/IPC、网络／云／第三方、同步、多设备、L3、外部用户和 Stage 4。
- 状态：`Closed — Acceptance Not Met / Superseded by LIFEOS-P3-096 / Not Frozen`。
- 执行授权：D-0401 已终止 P3-094 后续 attempt；本卡与最终收口卡均为历史只读，不得重新投递启动工程。D-0399 三项缺口由 `lifeos/tasks/LIFEOS-P3-096_post_commit_audit_evidence_closure.md` 接替。
- 单独确认例外：如需读取既有个人文件／DB、把内部页面写到用户目录、启用网络／Tauri/IPC／云／导出或扩大数据范围，必须停止并回报 PM 取得新的明确确认。

## Agent、模型与会话

- 推荐 Agent：Codex，新建隔离工程会话。
- 推荐模型／推理强度：`gpt-5.6-terra` + `high`。
- 允许降级：None；后备模型：`gpt-5.5` + `xhigh`（仅首选不可用时，必须记录原因）。
- 禁止降级条件：真实本地数据边界、SQLite 持久化／清理、失败披露、Evidence、P0/P1 或范围争议。
- 必须升级／回报：P0/P1、数据泄露或越权风险、任何外部访问、hash／Evidence 冲突、真实能力范围扩大或无法保持本地隔离。
- 是否需要后续独立评审：Yes；PM Pass 与用户采纳后须一次全新隔离独立复评。
- 可修改工程／项目账本：`lifeos/engineering/LIFEOS-P3-094/` / No。

## 最小读取包与直接输入

- 必读：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向补读：P3-079／080 的交付物、PM Review 与 Evidence Manifest（仅作受控本地闭环／审计／fail-closed 输入）；P3-093 PM Review；`PM_OPERATING_MODEL.md` 的受控能力包、真实数据、P0、交付前自检章节；`ROLE_MATRIX.md`、`STAGE_GATES.md`。
- 直接输入均只读：P3-079／080、P3-089／092、P3-093 的工程／Review／Evidence。不得导入、调用或复制其 runner 作为本任务主证据。
- 首份会话报告必须记录任务卡路径、会话类型、接收时间及用户确认范围。

## 实现与验证范围

1. 仅在 `lifeos/engineering/LIFEOS-P3-094/` 新建实现、测试、runner 和 Evidence。真实运行期数据库只可位于明确的 task-local 运行目录（默认 `/private/tmp/lifeos-p3-094-runtime/`），不得纳入工程、Evidence、版本控制或用户目录。
2. 实现最小真实本地闭环：用户显式输入一条捕获记录 → SQLite 原子写入 → 进程重启后读取 → 按确定规则在内部“今日页”展示。每个显示条目明确标识用户原文、记录时间、来源为本地捕获；不得生成、改写或推断用户原文。
3. 今日页展示可由同一隔离目录的本地渲染器生成 task-local `today.html`，只可在 Chrome 本地 `file:` 查看；不得监听端口、启动 HTTP 服务或形成用户文件导出。真实用户输入不得进入截图、日志、hash 明文或提交的 Evidence；自动化 Evidence 仅用固定非敏感测试文本。
4. 默认 fail-closed：空输入、无记录、损坏／不可读 DB、写入失败、渲染失败均不得显示成功或部分成功；须显示明确失败披露、保留可诊断的最小本地审计元数据且不泄露原文。删除／清理只处理本任务本地 DB 中用户本轮明确创建的记录，必须有显式确认与验证；不得触碰既有数据。
5. 在干净临时副本与独立 task-local DB 中验证首次捕获、重复／幂等策略、重启、今日展示、原子失败、半成品清理、失败披露、拒绝／阻断、显式删除／清理、真实边界静态关闭态与历史只读资产 hash。
6. 若用户在会话中提供真实文本，仅可用其完成用户允许的本地闭环；Evidence 只记录“用户主动输入已验证”的无内容事实、数据库记录数／不含原文的标识和清理结果。不得在聊天、交付物、日志、截图或 Manifest 中复述真实文本。

## Evidence 与完成定义

- 保存可运行 runner、逐项结构化结果、操作日志、快照、hash、Manifest、复跑命令和“验收标准→测试→Evidence”矩阵。
- 自动化测试和视觉 Evidence 必须使用固定非敏感文本；真实输入的存在不得成为通过条件，也不得被收集到项目资产。
- 所有 task-local DB 的创建、路径、记录数、清理结果和最终不存在／为空状态须可复核；禁止把 DB 内容或原文写入 Evidence。
- 执行侧提交 PM 前必须报告 P0/P1/P2/Unknown/Not Implemented 与未覆盖项；同范围问题在本能力包内整改，不另建微型任务。
- 若任何真实数据越界、外部访问、网络、Tauri/IPC、导出或不可清理的数据残留出现，立即停止，记录为 P0/P1 并回报 PM。

## 交付与验收

- 工程：`lifeos/engineering/LIFEOS-P3-094/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md`
- Evidence：`lifeos/engineering/LIFEOS-P3-094/evidence/MANIFEST.md`
- 通过条件：真实本地闭环只在授权 SQLite／主动输入范围内成立；重启后可复读与今日展示；失败／清理 fail-closed；无真实原文进入 Evidence；无网络、云、Tauri/IPC、导出或外部访问；完整 Evidence 且 P0/P1/Unknown/Not Implemented 为零。
- 会话回复仅使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，输出摘要、交付物路径和是否需要 PM 决策。

## PM 已授权窄 Rework（D-0381）

本节仅覆盖首次执行后的 P1 整改。用户已采纳 PM Review 的 Rework，并明确允许在**同一 P3-094**内处理下列经核验、仅含固定非敏感测试文本的临时目录；这不是新能力、新任务号或对既有个人数据／文件的授权。

### 会话与只读保全

- 使用**新建隔离 Codex 工程会话**，以本任务卡重新投递作为该会话执行授权。首份报告仍须记录任务卡路径、会话类型、接收时间和 D-0381 范围。
- 首次执行的 `lifeos/engineering/LIFEOS-P3-094/evidence/`、交付物、P1 事件记录与 PM Evidence 全部只读保留。新的 runner、结果、日志、快照、hash 和 Manifest 必须写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-2/`；不得覆盖 attempt-1。

### 唯一允许的整改

1. 修复测试与自检的临时资源清理：每个测试必须在 `finally`／等价清理钩子中删除其自行创建的 SQLite、HTML 和精确父目录；重跑前后均须证明系统临时目录不存在 `lifeos-p3-094-*` 残留。
2. 在修复前，允许只删除以下 15 个精确目录及其直接内容；不得使用 glob、宽范围递归删除或处理任何其他目录：
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-y8fjnatj`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-tus0xgt4`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-7_6egpbp`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-s36e1vt4`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-c03_a8d9`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-eh4rjzie`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-z4lh7awx`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-zhdpmtgx`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-cbdaimbe`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-dogu1luf`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-e3lr_gcz`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-sjr5u9ah`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-khkjkogn`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-m5goazqg`
   - `/var/folders/9m/92lnss312hz8kf__cs_9stcc0000gn/T/lifeos-p3-094-test-dgldcs8f`
3. 使用唯一允许的 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 完成动态 Evidence。仅在新 Chrome 标签页直接打开 attempt-2 task-local 的**完整 `file:` URL**；导航前、后均核对地址栏保持 `file:`，并留存时间、入口、加载结果和副本 hash。不得在地址栏输入可被解析为搜索查询的裸路径／文本；不得使用 In-app Browser、HTTP、CDP、命令行浏览器、搜索引擎、网络或任何替代／规避路径。
4. 若按上述正常直接 `file:` 预检连续两次仍失败，保留两次记录并停止为 Blocked；不得再次触发外部 URL。若预检通过，完成首次、重复／幂等、重启、拒绝／fail-closed、清理和动态展示矩阵。

### Rework 完成条件

- 旧残留已逐个精确清除，修复后每次测试／runner 后均无 `lifeos-p3-094-*` 残留；Evidence 只保存计数、路径类别、无内容 hash 与清理结果，不保存真实文本或 SQLite／HTML 内容。
- attempt-2 静态、单元与动态 `file:` Evidence 均可复跑、逐项结构化、hash 完整，且 P0/P1/P2/Unknown/Not Implemented 全为零。
- 仍不得读取既有个人文件／DB、访问网络、云、Tauri/IPC、Vault、同步、多设备、文件导出或外部用户；R-0051 仍 Open，不能由本 Rework 关闭。

## PM 已授权窄 Rework attempt-3（D-0383）

用户已采纳 attempt-2 的 PM Rework。仅允许在**新建隔离 Codex 工程会话**新增 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-3/`，补齐可保全的 Chrome 动态 Evidence；不修改、不删除、不重跑 attempt-1／attempt-2 的任一工程、Evidence、交付物、Review 或 Manifest。

1. 创建一个不会删除已有 Evidence 的可运行 runner。它必须将本轮固定非敏感测试数据、task-local DB／HTML、动态逐项结果、操作日志、复跑说明、截图、source hashes 与 Manifest 全部写在 attempt-3 下；运行期 DB／HTML 在截图后用 `finally` 清理。
2. 先运行结构化离线前置检查，记录时间、退出码、运行前后 `lifeos-p3-094-*` 残留计数和 source hash；不得以旧 attempt 的结构化结果代替。
3. 仅用 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky`，在新标签页直接导航至由 runner 生成的**完整** task-local `file:` URL。每项记录 Chrome 预检、时间、入口 URL 类别、地址栏仍为 `file:` 的可观察结果、截图／日志路径、SHA-256 与结构化 ID。不得输入裸路径或搜索文本，不得使用 In-app Browser、HTTP、CDP、命令行浏览器、搜索引擎、网络或替代／规避路径。
4. 只有预检实际通过后才可记录动态 PASS；若连续两次正常直接 `file:` 预检失败，记录两次结果并将整个 attempt-3 结论写为 Blocked。不得在同一 attempt 同时提交 Blocked 和 Pass。
5. 完成成功今日页、空输入拒绝／fail-closed、关闭标签、临时 DB／HTML 清理四项动态闭环。Manifest 必须逐项列出本次所有 Evidence（除 Manifest 自身外）及 SHA-256；交付物、README、结构化结果、闭环表和 Manifest 的最终结论必须一致。

任务卡重新投递至该新隔离会话即授权执行本节；不扩大真实数据、网络、云、Tauri/IPC、导出、风险、冻结、基线或阶段范围。

## PM 已授权窄 Rework attempt-4（D-0387）

用户已采纳 P3-095 独立复评的 Rework。整改继续回到**同一 P3-094 能力包**，不创建新任务号；不得复用 P3-095 独立评审会话，不得覆盖 attempt-1／2／3 或 P3-095 的 Review／Evidence。

### 唯一允许的工程整改

1. 修复“SQLite 已精确清空，但旧 `today.html` 仍存在并展示清理前记录”的 P1。清理操作必须先使既有内部展示工件不可展示；若页面失效／精确删除失败，必须在数据库变更前 fail closed，不得报告清理成功。
2. 增加正向回归：捕获并渲染 → 显式确认清理 → SQLite 记录数为零 → 旧页面不存在或不可展示 → 再次渲染明确失败。
3. 增加负向回归：模拟页面失效／删除失败时，数据库记录不得被清空，操作必须明确失败；不得出现“数据库已清空但旧页面仍可展示”的中间或最终状态。
4. 继续覆盖首次、幂等、跨进程复读、原子失败、损坏 DB fail-closed、临时资源清理和禁止能力关闭态；自动化 Evidence 仅使用固定非敏感文本。

### 会话、写入与 Evidence

- 使用新的或 PM 明确指定且不承担 P3-095 独立评审的 Codex 工程会话。用户将本任务卡路径投递至该会话即授权执行本节，无需额外“授权执行”口令。
- 只允许修改 `lifeos/engineering/LIFEOS-P3-094/` 内与上述缺陷直接相关的运行时、测试和 runner；新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/`。
- 新交付物写入 `lifeos/deliverables/LIFEOS-P3-094_rework_attempt_4_stale_today_view_invalidation.md`；必须保留结构化逐项结果、日志、源码 hash、Manifest、复跑命令和验收标准追溯矩阵。
- 执行前后核对 attempt-1／2／3、P3-095 Review／Evidence 未被覆盖，并证明所有本轮 task-local DB／HTML／缓存残留为零。
- `/private/tmp/lifeos-p3-095-pycache` 已由 PM 按用户明确授权精确删除；本工程会话不得再次创建、修改或处理该路径，也不得使用 glob 清理其他系统临时目录。

### 完成后关卡

完成后回到 PM 验收；PM Pass 与用户采纳后，仍须另一个全新隔离独立评审会话完整重跑离线与 Chrome `file:` 动态矩阵。R-0051 保持 Open；不恢复基线、不冻结资产、不进入 Stage 4，也不扩大至既有个人文件／DB、网络、云、Tauri/IPC、Vault、真实文件导出、同步、多设备、L3 或外部用户。

## PM 已授权窄 Rework attempt-5（D-0389）

用户已采纳 D-0388 的 PM Rework。整改继续留在**同一 P3-094 能力包**，不创建新任务号；可复用已经结束 attempt-4、且未承担 P3-095 独立评审的工程会话。用户将本任务卡路径重新投递至该工程会话即授权执行本节，无需额外口令。

### 唯一允许的工程整改

1. `delete_all()` 的内部展示目标必须由运行时强制绑定为 `db_path.parent / "today.html"`。任何调用方提供的其他文件名、父目录、绝对路径、相对路径、`..` 绕路或规范化后不等价路径，均须在任何文件或 DB 变更前 fail closed。
2. CLI 优先移除 `clear --output`；如为兼容保留，只能接受与上述唯一内部路径严格等价的值。不得依赖调用者自觉遵守目录授权。
3. 对既有 `today.html` 的文件类型和符号链接边界进行安全检查；符号链接、目录、特殊文件或无法确认的目标必须在文件与 DB 变更前拒绝。不得跟随链接删除其他位置的内容。
4. 保持 attempt-4 已成立的顺序：合法内部页面先精确失效，成功后才进入 SQLite 清理；页面失效失败时 DB 不变，数据库清理失败时不得报告成功。

### 强制负向回归

- DB 父目录外的固定非敏感哨兵文件作为 API／CLI 输出目标时：操作失败、哨兵存在且 hash 不变、DB 记录不变。
- 同目录但非 `today.html`、相对路径规范化绕路、`..`、符号链接和目录目标：全部在变更前拒绝，文件与 DB 均保持不变。
- 合法精确 `today.html`：继续证明页面失效、DB 清空、旧页面不存在、重渲染失败。
- 继续回归首次、幂等、跨进程复读、原子失败、损坏 DB fail-closed、禁止能力关闭态和零临时残留。

### Evidence 与完成后关卡

- 只允许修改 `lifeos/engineering/LIFEOS-P3-094/` 中与删除目标边界直接相关的运行时、CLI、测试、README 和 runner。
- 新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/`；新交付物写入 `lifeos/deliverables/LIFEOS-P3-094_rework_attempt_5_task_local_delete_boundary.md`。
- attempt-1／2／3／4、P3-095 与 PM Evidence 全部只读保全；不得使用真实用户文本或真实文件做测试。
- 提交 PM 前必须报告 P0/P1/P2/Unknown/Not Implemented，并保留逐项结果、哨兵前后 hash、日志、源码 hash、Manifest、复跑命令与追溯矩阵。
- 完成后重新 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离独立评审。R-0051 保持 P0 / Open；不恢复基线、不冻结、不进入 Stage 4，不扩大到既有个人文件／DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。

## PM 已授权窄 Rework attempt-6（D-0392）

用户已采纳 D-0390 的 attempt-5 PM Rework，并明确授权同一 P3-094 能力包继续窄整改。不得新建任务号；可复用已结束 attempt-5、且未承担 P3-095 独立评审的工程会话，或使用新的隔离 Codex 工程会话。用户将本任务卡路径投递至该工程会话即授权执行本节，无需额外口令。

### 唯一允许的工程整改

1. `render_today()` 的内部展示目标必须由运行时强制绑定为 `db_path.parent / "today.html"`，与 clear 使用同一唯一 task-local 页面。运行时不得接受任意输出文件；CLI 移除 `render --output`，或仅兼容接受经完整边界验证后与唯一内部路径严格等价的值。
2. render 与 clear 必须在任何文件或数据库变更前验证 DB 路径、DB 父目录和页面路径的**完整现有目录组件链**。任一路径组件为符号链接、规范化后不等价、含 `..`、非绝对路径或无法确认时，必须 fail closed；不得只检查直接父目录。
3. render 写入前必须以不跟随链接的方式验证最终 `today.html` 文件类型。既有目标为符号链接、目录、FIFO／特殊文件或类型无法确认时必须拒绝；不得跟随链接覆盖其他位置。clear 继续保持相同文件类型门和“先页面失效、后 DB 清理”顺序。
4. 失败路径必须明确披露且保持原子边界：所有边界拒绝发生在文件和 DB 变更前；页面失效失败时 DB 不变；数据库清理失败时不得报告成功。不得借本轮修改 capture/list 的数据模型、Schema/API 或扩大运行时能力。

### 强制负向与正向回归

- render API／CLI 以 DB 目录外固定非敏感哨兵作为目标：操作失败、哨兵存在且 hash 不变、DB 记录不变。
- render 的最终文件符号链接、祖先目录符号链接、目录、FIFO／特殊文件、相对路径、`..` 和规范化绕路：全部在变更前拒绝，目标与 DB 保持不变。
- clear 的祖先目录符号链接链：操作失败，真实目标页面 hash／存在状态与 DB 记录均保持不变。
- 合法绝对且无链接的 task-local DB 与精确 `today.html`：render 成功；clear 继续证明页面失效、DB 清空、旧页面不存在且重渲染失败。
- 继续回归首次、幂等、跨进程复读、原子写入失败、损坏 DB、禁止能力关闭态、提交 runner 干净副本与零临时残留。

### 写入、Evidence 与完成后关卡

- 只允许修改 `lifeos/engineering/LIFEOS-P3-094/` 中与 render／clear 路径边界直接相关的运行时、CLI、测试、README 和 runner。
- 新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/`；新交付物写入 `lifeos/deliverables/LIFEOS-P3-094_rework_attempt_6_task_local_render_clear_boundary.md`。
- attempt-1／2／3／4／5、P3-095、PM Review 与全部 PM Evidence 只读保全；测试只可使用 `/private/tmp` 新建的固定非敏感夹具，不得使用真实个人文件、既有个人 DB 或真实用户文本。
- 提交前必须保留逐项结构化结果、哨兵前后 hash、日志、源码 hash、历史只读 hash、Manifest、复跑命令和验收追溯矩阵，并报告 P0/P1/P2/Unknown/Not Implemented。
- 本轮涉及真实本地文件写入／删除与 DB 边界，可跳过本地模型预检，但交付物须记录原因。
- 完成后重新 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离独立评审。R-0051 保持 P0 / Open；不关闭风险、不恢复基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到既有个人文件／DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。

## PM 已授权窄 Rework attempt-8（D-0396）

用户已采纳 D-0395 的 attempt-7 PM Rework，并同时明确授权同一 P3-094 能力包继续窄整改。不得新建任务号；可复用已结束 attempt-7、且未承担 P3-095 独立评审的工程会话，或使用新的隔离 Codex 工程会话。用户将本任务卡路径投递至该工程会话即授权执行本节。

### 唯一允许的工程整改

1. DB 文件完全缺失、但安全 task-local 父目录和普通旧 `today.html` 可由 attempt-6 路径边界确认时，render 必须先使旧页面不可展示，再返回 DB 缺失失败；不得创建 DB、Schema、journal、WAL 或其他文件。
2. render 的数据库读取必须使用严格只读、禁止创建和禁止 Schema 初始化／补写的连接路径。零字节、无 Schema、Schema 不完整或查询失败的 SQLite 必须返回失败，使旧页面不可展示，并保持 DB bytes、大小和 SHA-256 不变。
3. capture/list 的现有写入和数据模型、SQLite Schema/API 不得借本轮改变；只允许为 render 引入只读验证／读取入口及安全父目录页面失效辅助逻辑。
4. 必须保留 attempt-6／7 已成立的唯一内部页面、完整目录组件链、规范化路径、最终文件类型、不跟随链接、合法 render 原子发布、发布失败保留当前有效页面、clear 顺序和失效失败披露。

### 强制回归

- DB 缺失 + 固定非敏感旧页面：render 失败；旧页面不存在或不可展示；DB 及任何 SQLite 副文件均未创建。
- 零字节 SQLite + 旧页面：render 失败；旧页面不可展示；DB bytes／大小／hash 均不变。
- 有效 SQLite 但缺少 captures／audit Schema、或仅有部分 Schema + 旧页面：render 失败；旧页面不可展示；DB bytes／大小／hash 均不变，不创建或补写表、索引、trigger。
- 已初始化空 DB、损坏／不可读 DB、注入查询失败和页面失效失败：继续满足 attempt-7 合同。
- 合法非空 DB render、原子发布失败、clear、render／clear 越界目标、最终链接、祖先目录链接链、相对／`..`、文件类型、首次、幂等、跨进程、禁止能力关闭态与零残留继续全量回归。

### 写入、Evidence 与关卡

- 首份会话报告必须记录任务卡路径、会话类型、精确接收时间和 D-0396 授权范围。
- 只允许修改 `lifeos/engineering/LIFEOS-P3-094/` 中与 render 缺失 DB 旧页面失效及只读数据库读取直接相关的运行时、测试、README 和 runner；CLI 仅在确有接口对齐必要时可修改，不得新增能力。
- 新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/`；新交付物写入 `lifeos/deliverables/LIFEOS-P3-094_rework_attempt_8_read_only_render_missing_db_fail_closed.md`。
- attempt-1 至 attempt-7、P3-095、PM Review 与全部 PM Evidence 只读保全；只使用 `/private/tmp` 新建固定非敏感夹具，不得使用真实个人文件、既有个人 DB 或真实用户文本。
- 所有语法检查、缓存和临时产物仅可位于项目允许目录或新建 `/private/tmp`；不得尝试用户缓存目录。
- 提交前必须保留逐项结构化结果、旧页面状态、DB 前后 bytes／大小／hash、SQLite 对象清单、日志、源码 hash、历史只读 hash、Manifest、复跑命令和验收追溯矩阵，并报告 P0/P1/P2/Unknown/Not Implemented。
- 本轮涉及真实本地页面与 DB 生命周期，可跳过本地模型预检，但交付物须记录原因。
- 完成后重新 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离独立评审。R-0051 保持 P0 / Open；不关闭风险、不恢复基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到既有个人文件／DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。

## PM 已授权窄 Rework attempt-7（D-0394）

用户已采纳 D-0393 的 attempt-6 PM Rework，并同时明确授权同一 P3-094 能力包继续窄整改。不得新建任务号；可复用已结束 attempt-6、且未承担 P3-095 独立评审的工程会话，或使用新的隔离 Codex 工程会话。用户将本任务卡路径投递至该工程会话即授权执行本节。

### 唯一允许的工程整改

1. 当 render 无法确认 DB 内容有效，包括 DB 为空、损坏、不可读或查询失败时，必须在返回失败前使既有 task-local `today.html` 不可展示；不得留下可继续显示旧内容的页面。
2. 旧页面失效必须复用 attempt-6 已建立的唯一内部页面、完整目录组件链、规范化路径、最终文件类型与不跟随链接边界；不得重新接受调用方输出路径，不得越出 DB 同目录或跟随链接。
3. render 失败不得改写捕获记录或 SQLite 状态。合法非空 DB 的 render、原子发布失败保留当前有效页面、clear 的先页面失效后 DB 清理顺序均须保持不变。
4. 不得修改 capture/list 的数据模型、SQLite Schema/API、今日页视觉内容或引入任何新能力。

### 强制回归与 Evidence 卫生

- 空 DB + 已存在固定非敏感旧页面：render 返回失败；旧页面不存在或不可展示；DB 保持为空。
- 损坏／不可读 DB + 已存在固定非敏感旧页面：render 返回失败；旧页面不存在或不可展示；不得声称 DB 已修复或清理成功。
- 旧页面失效失败注入：不得报告 render 成功；须明确披露无法完成 fail-closed，DB 不被 render 改写。
- 继续回归 attempt-6 的合法 render、发布失败原子性、render／clear 越界目标、最终链接、祖先目录链接链、相对／`..` 路径、文件类型、clear、首次、幂等、跨进程、损坏 DB、禁止能力关闭态与零残留。
- 首份会话报告必须记录任务卡路径、会话类型、**精确接收时间**和 D-0394 授权范围。
- 所有语法检查、缓存和临时产物仅可位于项目允许目录或新建 `/private/tmp`；使用 `-B`、内置 `compile()` 或显式 `/private/tmp` 缓存，不得尝试用户缓存目录。

### 写入与完成后关卡

- 只允许修改 `lifeos/engineering/LIFEOS-P3-094/` 中与 render 失败时旧页面失效直接相关的运行时、CLI、测试、README 和 runner。
- 新 Evidence 固定写入 `lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/`；新交付物写入 `lifeos/deliverables/LIFEOS-P3-094_rework_attempt_7_stale_page_fail_closed.md`。
- attempt-1／2／3／4／5／6、P3-095、PM Review 与全部 PM Evidence 只读保全；只使用 `/private/tmp` 新建固定非敏感夹具，不得使用真实个人文件、既有个人 DB 或真实用户文本。
- 提交前必须保留逐项结构化结果、旧页面前后状态／hash、DB 状态、日志、源码 hash、历史只读 hash、Manifest、复跑命令和验收追溯矩阵，并报告 P0/P1/P2/Unknown/Not Implemented。
- 本轮涉及真实本地页面与 DB 生命周期，可跳过本地模型预检，但交付物须记录原因。
- 完成后重新 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离独立评审。R-0051 保持 P0 / Open；不关闭风险、不恢复基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到既有个人文件／DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
