# LIFEOS-P3-125｜Runtime 根可配置化与失败关闭收口

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅拟在指定 task-local 工程目录与固定 `/private/tmp` 隔离根中，使用 P3-122 只读候选和全新非敏感合成 SQLite 夹具，修复 Runtime／DB／geometry 根不可移植问题并验证失败关闭。不访问 Pilot、真实个人数据、真实 DB／路径／文件、真实文本、网络、模型、云、第三方、凭据或外部目标；不授权任意路径写入或扩大既有三项 IPC 能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-125`
- 任务名称：Runtime 根可配置化与失败关闭收口
- 优先级：P0
- 任务类型：受控本地 Tauri/IPC 路径边界工程补丁
- 是否为受控能力包：Yes
- 能力包边界／唯一风险边界：只把 P3-122 candidate 的固定 P3-122 Runtime 根改为单一、显式、构建时冻结且可复核的 task-local root；DB、viewport request、geometry trace 与所有 Runtime 生命周期文件必须从该根派生。
- 包内允许完成的工作：实现、回归、必要补测、actual-Tauri 最小验证、Evidence／Manifest 整理和文案对齐。
- 包内整改授权：仅限上述范围；不得扩大目录、数据、IPC、架构、真实能力、风险、冻结或阶段范围。
- 必须拆分事项：P3-126 全新隔离独立复评、产品短合同、Fast Track、风险关闭／重开、基线恢复、Schema/API／架构冻结、真实 DB／路径、Stage 4。
- 建议篇幅：1500–2500 字短报告。
- 是否适用 P3 Engineering Fast Lane：No；这是 P0 路径授权与 Tauri/IPC 失败关闭修复。
- 推荐执行 Agent：Codex
- 推荐理由：需要窄改 Rust/Tauri 路径合同、运行离线回归并生成机器可复核 Evidence。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 路径授权、失败关闭和实际 Tauri 生命周期要求质量优先。
- 允许降级模型：`None`
- 禁止降级条件：任何涉及路径规范化、目录链接链、DB／geometry 写入、失败前置或 actual-Tauri 结果的判断。
- 必须升级条件：若 `xhigh` 无法可靠证明路径派生／失败前置或出现未冻结的新平台行为，停止并回 PM；不得缩减矩阵。
- 后备模型：`gpt-5.5`，仅首选不可用且在首报披露后使用 `xhigh`；不得降低验收依据。
- 是否需要后续独立评审：Yes；PM Pass 和用户采纳后另建 P3-126，不在本任务内自评。
- 是否允许修改工程文件：Yes；仅在用户确认后的 P3-125 自有工程根。
- 是否允许修改项目账本：No。
- 主责角色：技术架构／Rust-Tauri Runtime／路径安全／Evidence QA。
- 协审角色：数据主权、生命周期、失败关闭、历史保全。
- 必须通过的评审关卡：Gate 2 数据与来源、Gate 4 技术可行性；Gate 1/3 只核对无语义扩张，Gate 5 不适用。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/1 / Not Frozen`
- 验收治理文件：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze 路径：`lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-125-v1`
- ABF SHA-256：`4ab5ed8a0c1349041d1d9b13452be5059abf510f4d2ecae386e23283c1956057`
- ABF 状态：Frozen
- 本任务正式 Rework 上限：1
- 当前正式 Rework 次数：0
- 执行授权方式：用户将本最终任务卡绝对路径投递至全新或明确复用的 Codex 工程会话即启动 Frozen 范围；只在 PM 主会话查看或转述路径不启动。
- 投递授权的会话类型与隔离要求：优先复用 P3-122 工程线会话，但必须把 P3-125 视为新任务、停止继承旧授权并重读最新状态；如无法确认上下文或旧任务仍活动，则新建 Codex 工程会话。
- 投递前仍需单独用户确认的例外：**Completed**；用户已确认工程根、临时根、全新合成 DB、P3-122/P3-124 全部只读、构建时单一 root、三项 IPC 与全部禁止边界。
- 授权证据记录要求：专项首报记录最终任务卡路径、会话类型、接收时间、实际 model/effort 与 D-0503 后的正式冻结记录。

## 为什么是新任务

P3-124 已证明 P3-122 candidate 将 Runtime、DB、viewport request 和 setup geometry trace 固定在旧 P3-122 temp root，而 P3-124 只能使用新 P3-124 root。修复需要修改 candidate 的路径合同，已越出 P3-124 Frozen ABF，不能继续 Rework。P3-125 只消除这一项可移植性阻断，不重做 UI 或扩大 Runtime。

## 本轮唯一用户结果

同一份 P3-125 source 在不修改源码的情况下，可由明确的构建时配置绑定到本任务授权的 task-local Runtime 根；DB、viewport request、native geometry 与所有 sidecar 只从该根派生。配置缺失、非法、非规范、目录链接链异常或文件类型异常时，必须在任何文件／DB 变化前失败关闭。

## 拟采用的窄实现合同

1. 移除生产源码中对 `/private/tmp/lifeos-p3-122-native-evidence-v1` 的固定依赖。
2. 使用单一构建时配置 `LIFEOS_RUNTIME_ROOT`；构建产物必须记录其值与 source/build hash。不得保留旧根 fallback，也不得由多个独立变量分别配置 DB、viewport 或 geometry。
3. `capture.sqlite`、`viewport-request.txt`、`native-geometry-*.jsonl` 及其他 Runtime 文件全部以安全 join 从同一根派生。
4. 配置必须是绝对、规范化的授权 root；拒绝空值、相对路径、`.`／`..`、NUL、非目录祖先、symlink 祖先链、root 为链接／普通文件，以及 DB／sidecar 类型冲突。
5. 验证顺序必须先于目录创建、文件创建、DB open/migration、geometry append 或 UI 成功回执。
6. 不新增 Runtime root 选择 UI，不新增 IPC，不改变现有三 IPC 的名称、参数、回执、DB schema 或页面结构。

## 拟允许写入与环境

正式确认后仅允许：

- `lifeos/engineering/LIFEOS-P3-125/`
- `lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md`
- `lifeos/local_prechecks/` 中 P3-125 专属报告（如适用）
- `/private/tmp/lifeos-p3-125-runtime-root-config-v1`

临时根内可含 `run-a/`、`run-b/`、build/cache、全新合成 DB、sentinel、日志和 disposable mutation。结束时必须精确删除唯一 P3-125 临时根；禁止 glob、`find`、宽前缀或未解析变量删除。

## 严格只读输入

- `lifeos/engineering/LIFEOS-P3-122/candidate/`（当前 75-file candidate）
- `lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json`
- `lifeos/reviews/LIFEOS-P3-122_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-122/pm_evidence/acceptance/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-122/pm_evidence/final-adoption/MANIFEST.md`
- P3-123、P3-124 全部任务、ABF、Review、Evidence、授权与 PM Evidence，尤其：
  - `lifeos/reviews/LIFEOS-P3-124_pm_rework_1_review.md`
  - `lifeos/reviews/LIFEOS-P3-124/pm_evidence/rework-1/MANIFEST.md`
- `lifeos/tasks/LIFEOS-P3-125_source_allowlist.md`：UTF-8/LF、87 physical lines、75 candidate rows，75/75 bytes/hash 匹配，SHA-256 `807ff8e1dd565eed4fec4c1b6bf5c6bca133861a9dffdbae1ca2bac60293dc4b`；Frozen 后只读。

不得修改、覆盖、复制回或用新 Evidence 改写任何历史资产。

## 最小启动包与定向补读

正式冻结后的专项会话必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡与 Frozen ABF
4. `lifeos/ACCEPTANCE_GOVERNANCE.md`
5. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
6. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`（仅用于三 IPC actual-App 动作闭环）
7. P3-122 `runtime.rs`、`main.rs`、`Cargo.toml`、Tauri config、最终 Manifest 与 PM Review
8. P3-124 Rework-1 Independent Review、PM Review 与 PM Evidence Manifest

高风险定向补读：

- `PM_OPERATING_MODEL.md`：任务投递授权、P0/Tauri/IPC、模型路由、会话隔离、独立评审规则。
- `ROLE_MATRIX.md`：Codex 工程、技术架构、数据与 QA 职责。
- `STAGE_GATES.md`：Gate 2、Gate 4、任务级评审与 Stage 3→4 区分。
- `TASK_REGISTRY.md`：P3-122～P3-125。
- `DECISION_LOG.md`：D-0492～D-0503。
- `RISK_LOG.md`：R-0040、R-0051、R-0052。

## 必须完成的实现与回归

1. 从 Frozen source allowlist 逐文件建立 P3-125 candidate；除路径配置及必要测试／Evidence instrumentation 外保持 byte-equivalent。
2. 对同一 source 分别构建并运行 `run-a/` 与 `run-b/`，只改变冻结的构建时 Runtime root 值；两次均只能写各自子根，证明无需修改源码即可重绑定。
3. 在 actual Tauri App 中最小复跑 `runtime_status`、首次／重复 `capture_record`、`get_today`、刷新、关闭重开；核对 UI 回执、DB、audit 和 geometry 均属于当前根。
4. 负向覆盖：配置缺失、相对／非规范路径、symlink 祖先、root 普通文件、DB 链接／目录／非 SQLite、geometry 文件类型冲突和不可写失败；每项检查 sentinel 与 DB before/after 完全不变。
5. 静态和运行态确认旧 P3-122 root 不再出现在 production source、bundle string、日志或写入 inventory；测试夹具中的负向字面值必须单独标注。
6. 完成首次、重复、关闭重启、原子失败、半成品清理、失败披露、审计、历史只读 hash、pristine control 和 mutation fail-closed。
7. 生成非自指 Final Manifest，覆盖 task/ABF/allowlist、P3-122/P3-124 固定输入、current candidate、runner、逐行结果、actual-App Evidence、mutation、delivery、cleanup 与历史保全。

## 冻结完成定义

- 同一 source 在 `run-a/` 与 `run-b/` 两个授权子根均成功，不修改 source hash。
- 所有 Runtime-owned 文件只位于当前配置根；另一子根、工程外和旧 P3-122 root 均无写入。
- 所有负向在任何文件／DB 变化前失败，sentinel、DB bytes/schema/rows/audit 与历史 hash 不变。
- UI、视觉 Token、页面结构、三 IPC、schema/API、capability、网络／模型关闭态均未变化。
- Evidence 逐行可复核；Final Manifest、cleanup 与五类计数均满足 Frozen ABF。

## 非范围与停止条件

- 不重做或调整 P3-116/P3-122 UI、响应式布局、页面密度或 Global AI。
- 不新增 runtime root 设置页、目录选择器、CLI flag、IPC、capability、Schema/API 或产品权限模型。
- 不访问／创建／stat／hash／复制／清理旧 P3-122 temp root、Pilot、真实 DB／路径／文本或其他历史临时根。
- 不联网，不使用产品模型，不启用 clear/export/权限/恢复/同步/多设备/L3/外部用户。
- 不修改风险、冻结、工程基线或阶段；不创建 P3-126、P3-127 或 P3-128。
- 如修复必须引入运行时任意路径选择、改变三 IPC／Schema/API、访问旧根或扩大授权目录，立即停止并回 PM；当前任务不得膨胀。

## 交付物与报告

- 工程与 Evidence：`lifeos/engineering/LIFEOS-P3-125/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md`
- 必须报告：包内自检、逐行矩阵、P0/P1/P2/Unknown/Not Implemented、actual model/effort、修改文件、复跑命令、Manifest 和精确 cleanup。
- 聊天回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只给摘要和路径。
- 本地模型预检可因 P0 路径／Tauri/IPC 最终边界而跳过，但必须说明；不得替代 PM 或后续独立复评。

## 当前启动状态

`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`。用户已完成精确 synthetic-only Tauri/IPC 边界确认；PM 已复算 source allowlist 75/75、确认工程根和唯一临时根均不存在，并冻结 `ABF-P3-125-v1`。现在可把本任务卡绝对路径投递至合格 Codex 工程会话；专项必须先完成启动前质疑窗口，且不得越出 Frozen 边界。
