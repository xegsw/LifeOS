# LIFEOS-P3-126｜P3-125 当前技术候选清洁启动与验收链重建

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务只拟在新的 task-local 工程目录与固定 `/private/tmp` 隔离根中，使用 P3-125 Rework-1 当前技术候选的只读副本和全新非敏感合成 SQLite，重建未受污染的启动、执行与 Evidence 链。不访问、创建、stat、hash、复制或清理旧 P3-122 Runtime root、Pilot、真实个人数据、真实 DB／路径／文本、网络、模型、云、第三方、凭据或外部目标；不扩大既有三项 IPC。

## 任务信息

- 任务 ID：`LIFEOS-P3-126`
- 任务名称：P3-125 当前技术候选清洁启动与验收链重建
- 优先级：P0
- 任务类型：受控本地 Tauri/IPC clean-start Evidence closure
- 是否为受控能力包：Yes
- 唯一风险边界：不修改 P3-125 已完成的 Runtime-root 技术合同，只在全新任务／ABF／根中从零建立无越界的 preflight、双根运行、三 IPC、失败关闭、history、mutation、Manifest 与 cleanup 证据链。
- 包内允许工作：75-file byte-exact source copy、task-owned runner／tests、离线 actual-Tauri 复跑、Evidence／Manifest 与交付物。
- 包内整改授权：仅限 Evidence、runner、测试和文案；production candidate 必须 byte-exact，任何 production source 修改均停止回 PM。
- 必须拆分事项：production 修复、独立复评、产品短合同、Fast Track、风险／冻结／基线／Schema/API／真实能力／Stage 4。
- 推荐执行 Agent：Codex
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 路径授权、actual-Tauri 与 Evidence 清洁链要求质量优先。
- 允许降级模型：`None`
- 禁止降级条件：全部任务范围。
- 必须升级条件：若首选配置不可用、启动身份不可记录、候选 hash 不符或需要访问未授权路径，行动前停止。
- 后备模型：`gpt-5.5`，仅首选不可用且在任何 candidate read／执行根创建前披露并由 PM 确认后使用 `xhigh`。
- 是否需要后续独立评审：Yes；仅 PM Pass、用户采纳后另建全新隔离任务。
- 是否允许修改工程文件：Yes，仅 P3-126 task-owned runner/Evidence；production candidate 不得改动。
- 是否允许修改项目账本：No。
- 主责角色：路径安全、Rust/Tauri Runtime、Evidence QA。
- 协审角色：数据主权、授权不漂移、生命周期、历史保全。
- 必须通过关卡：Gate 2、Gate 4；Gate 1/3 仅核对零产品／接口漂移；Gate 5 不适用。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/1 / Not Frozen`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- ABF：`lifeos/tasks/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-126-v1`
- ABF SHA-256：`8e98f4d874d3925bdad308f800f01d7c44b02c3016e71f19083cad4fc13fb908`
- ABF 状态：Frozen
- 正式 Rework 上限：1；当前 0/1。
- 执行授权方式：用户向全新 Codex 工程会话投递本最终任务卡绝对路径即启动 Frozen 范围；只在 PM 会话查看或转述路径不启动。
- 会话隔离：必须新建会话；不得复用 P3-125 会话，避免继承已经发生的 preflight 污染和旧授权。
- 投递前额外用户确认：Completed；用户已确认新工程根、固定 temp root、全新合成 DB、P3-125 Rework-1 全部只读、仅构建时 root与三 IPC、旧 P3-122 Runtime root零 access/stat/hash/create/cleanup，以及全部真实／网络／模型禁止边界。
- 授权证据记录要求：专项首报记录最终任务卡路径、全新会话类型、接收时间、actual model/effort、`D-0511`、Frozen ABF／allowlist／Freeze Manifest hash；任何 candidate read 或 execution-root创建前完成。

## 本轮唯一用户结果

同一份 P3-125 Rework-1 技术候选在 byte-exact 不变的前提下，于新任务的两个授权子根完成构建、actual-Tauri 三 IPC 生命周期、失败关闭和精确清理，并形成从 clean preflight 开始、没有旧历史 Runtime root access/stat 的机器可复核验收链。

## 拟允许目录与数据

- `lifeos/engineering/LIFEOS-P3-126/`
- `lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md`
- `lifeos/local_prechecks/` 中 P3-126 专属报告（如适用）
- `/private/tmp/lifeos-p3-126-clean-closure-v1`
- 仅 temp root 内的 `run-a/`、`run-b/`、disposable negatives、task-local caches、固定合成短文本与全新 SQLite。

结束时只精确删除上述唯一 temp root；禁止 glob、`find`、宽前缀删除或未解析变量。

## 严格只读输入

- `lifeos/engineering/LIFEOS-P3-125/rework-1/candidate/`（75 files，最终 source allowlist 冻结后逐行绑定）
- `lifeos/engineering/LIFEOS-P3-125/rework-1/FINAL_MANIFEST.json`
- `lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_rework_1.md`
- `lifeos/reviews/LIFEOS-P3-125_pm_rework_1_review.md`
- `lifeos/reviews/LIFEOS-P3-125/pm_evidence/rework-1/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-125/pm_evidence/final-adoption/MANIFEST.md`
- 最终冻结的 `lifeos/tasks/LIFEOS-P3-126_source_allowlist.md`

P3-122/P3-124 及 P3-125 initial 资产不作为本任务执行输入；不得为“补历史”主动读取。旧 P3-122 Runtime root 是禁止目标，不得作任何 existence/metadata/hash 操作。

## 最小启动包与定向补读

执行前完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 最终任务卡与 Frozen ABF
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
7. 上述 P3-125 Rework-1 只读输入
8. `PM_OPERATING_MODEL.md` 的任务授权、P0/Tauri/IPC、模型和隔离章节
9. `ROLE_MATRIX.md` 的 Codex、技术、数据、QA章节
10. `STAGE_GATES.md` 的 Gate 2、Gate 4 与 Stage 3/4 区分
11. `TASK_REGISTRY.md` 中 P3-125/P3-126、`DECISION_LOG.md` 中 D-0508 起相关记录、`RISK_LOG.md` 中 R-0040/R-0051/R-0052

## 必须完成

1. 在任何 candidate read 或 execution-root 创建前记录任务投递、会话隔离、平台暴露的 actual model/effort、任务／ABF／allowlist hash；命令计划必须证明不包含旧 Runtime root existence/metadata 操作。
2. 按 Frozen allowlist建立 byte-exact 75-file candidate；production source 0 changes。
3. 同一 source 分别以新 temp root 的 `run-a/`、`run-b/` 构建并运行，只改变构建时 `LIFEOS_RUNTIME_ROOT`。
4. actual Tauri 执行 `runtime_status`、首次／重复 `capture_record`、`get_today`、刷新、关闭重开，绑定 UI、IPC、DB、audit、geometry、process/log Evidence。
5. 独立覆盖配置、path、DB/sidecar/geometry 类型、原子失败和不可写失败；所有失败在变更前停止并证明 sentinel/DB before-after不变。
6. 静态验证 production 只有一个构建时 root、无 fixed parent/fallback、三 IPC/UI/Schema/capability不漂移；不得对禁止的旧 root 做运行态探测。
7. P3-125 固定输入 before/after hash 一致；pristine verifier先 PASS，再完成 root/fallback/derive/order/history/extra/path/omission mutations。
8. 精确 cleanup，生成 M-001～M-012 独立行与非自指 Final Manifest；verifier 必须重算所有声明路径、bytes/hash、角色、遗漏、extra 与历史漂移。

## 非范围与停止条件

- 不修改 production candidate；若 byte-exact candidate不能通过，停止并回 PM。
- 不访问、stat、hash、创建或清理旧 P3-122 Runtime root或其他旧临时根。
- 不读取 Pilot、真实 DB／路径／文本；不联网、不调用产品模型。
- 不新增 IPC、CLI、设置页、目录选择器、capability、Schema/API；不改 UI。
- 不修改 P3-125 或更早资产；不修改风险、冻结、基线或阶段。
- 不创建后续独立复评、产品合同或 Fast Track 任务。
- 任一启动门失败必须在 candidate copy、temp root创建、构建或 actual-App 动作前 fail closed。

## 交付与验收

- 工程／Evidence：`lifeos/engineering/LIFEOS-P3-126/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md`
- 必须报告 actual model/effort、12行矩阵、P0/P1/P2/Unknown/Not Implemented、source/history hashes、复跑命令、Manifest、cleanup 和禁止路径零操作声明。
- P0 高风险最终判断允许跳过本地模型预检，但须说明。
- 只有 Frozen ABF 全部不变量和矩阵 PASS、五类计数全零、silent N/A=0，才能提交 PM Pass 候选。

## 当前启动状态

`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`。用户已完成精确 synthetic-only Tauri/IPC 边界确认；PM 已复算 source allowlist 75/75、确认新 engineering/temp roots absent并冻结 `ABF-P3-126-v1`。现在只可将本最终任务卡绝对路径投递至全新 Codex 工程会话；专项必须在任何 candidate read 或 root创建前完成 clean startup gate。
