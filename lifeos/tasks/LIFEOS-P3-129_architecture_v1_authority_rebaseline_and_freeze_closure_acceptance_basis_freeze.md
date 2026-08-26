# LIFEOS-P3-129 Acceptance Basis Freeze

## 冻结信息

- 任务 ID：`LIFEOS-P3-129`
- ABF ID／版本：`ABF-P3-129-v1`
- 生效决策：用户于 2026-08-26 明确确认 `确认以架构 V1.0 正式取代 V0.1`
- 冻结时间：2026-08-26
- ABF 文件 SHA-256：由 PM 在 D-0521 与任务卡记录
- 状态：`Frozen`
- 本文件是否在专项会话开始前冻结：`Yes`

## 本轮唯一用户结果

- 要完成的单一结果：形成并独立评审一个可精确 promotion 的技术架构 V1.0 冻结包，使其在最终用户关卡后正式 supersede V0.1 的后续规范权威，同时保全 V0.1 历史与兼容不变量。
- 明确不冻结的产品需求：产品 IA、页面、功能优先级、真实用户启用、Stage 4。
- 明确非范围：工程迁移、Runtime 执行、Schema/API、IPC/capability、真实数据、模型／Agent 调用、网络、风险关闭、工程基线恢复。

## 授权和能力边界

- 允许目录：`lifeos/architecture/LIFEOS-P3-129/`、指定主交付物；独立评审会话仅写 `lifeos/reviews/LIFEOS-P3-129/`。
- 允许数据与夹具：仅仓库内固定架构／治理文本及合成结构化矩阵；无数据库或用户数据。
- 允许入口／接口：本地文件只读与 task-local Markdown／JSON 输出。
- 允许工具／环境：`rg`、`wc`、`sed`、`shasum`、只读 parser、task-local verifier。
- 严格只读资产：当前 V1.0 canonical、全部 V0.1 冻结历史、P0-003/P0-009、P3-126/P3-127、P3-128、PM 账本。
- 禁止能力与外部目标：Runtime、Tauri/IPC、DB、浏览器、Pilot、真实文件／路径／文本、网络、云、第三方、模型、Agent、Vault、export、delete/clear、recovery、sync。
- 投递前额外用户确认：已由上述明确替代决定覆盖；最终 canonical promotion 仍需独立评审、PM Pass 后的用户 Gate 确认。

## 引用的 L1 长期原则

- L1-1 数据主权：仅固定仓库文本，不访问未授权目标。
- L1-2 内容身份：区分 canonical V1.0、V0.1 历史、候选矩阵和 PM 冻结状态。
- L1-3 生命周期完整：Draft→Freeze Candidate→Independent Pass→PM Pass→User Confirmed→Frozen 顺序不可跳步。
- L1-4 失败关闭：任一 hash、语义、独立性或关卡失败均不得 promotion。
- L1-5 用户控制：关键架构冻结在最终动作前保留用户 Gate。
- L1-6 审计可信：替代范围、时间、hash、决策和历史适用性可追溯。
- L1-7 Evidence 诚实：方向确认不替代逐行兼容与独立评审。
- L1-8 历史保全：V0.1 与 P3-128 历史不得覆盖或追溯改写。
- L1-9 授权不漂移：不得借架构替代执行工程迁移、真实能力或 Stage 变更。
- L1-10 可复核性：同一固定候选与 verifier 应给出一致结果。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | V1.0 canonical 输入唯一绑定 SHA-256 `2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32` | P0 | candidate 与所有矩阵引用同一 bytes/hash | Blocked / no promotion |
| ABF-I-02 | V0.1 历史不删除、不改写；只 supersede 后续规范效力 | P0 | history hash before/after 一致，适用性明确 | Rework / no promotion |
| ABF-I-03 | V1.0 不得削弱核心领域、数据主权、AI 权限、Evidence、授权重检与失败关闭 | P0 | 兼容矩阵无冲突或空白 | Rework / no promotion |
| ABF-I-04 | 冻结范围仅为 V1.0 文档明确固定项 | P0 | 非冻结实现细节逐项排除 | Rework / no promotion |
| ABF-I-05 | P3-126 保持历史事实；V1.0 是后续目标，不追溯宣布旧 Runtime 失败 | P1 | transition matrix 明确 preserve/adapt/defer | Rework |
| ABF-I-06 | canonical promotion 只有经评审的状态／supersession 元数据变化 | P0 | pre/post diff 无正文变化 | Blocked / new ABF if semantic edit required |
| ABF-I-07 | 执行与独立评审会话隔离 | P0 | 独立 runner、Review、Evidence lineage 成立 | Blocked |
| ABF-I-08 | PM／用户 Gate 前不得写 Frozen 主账本结论 | P0 | canonical 与 FREEZE_STATUS 未提前 promotion | Blocked |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | fixed inputs | canonical V1.0 + V0.1 history | 复算路径、bytes、hash | 全部匹配且无缺失 | 原文件 | T-FIXED | `fixed_inputs.json` |
| ABF-M-002 | V0→V1 reconciliation | 固定两代架构 | 逐项分类 | 无未分类／无隐式删除 | V0.1 history | T-RECON | `v0_to_v1_reconciliation.json` |
| ABF-M-003 | product/domain/trust | 固定 Constitution/Core/Trust | 双向语义检查与反例 | 无削弱或身份混淆 | Frozen core/trust | T-COMPAT | `cross_baseline_compatibility.json` |
| ABF-M-004 | freeze scope | V1.0 §9及全文 | 区分 normative/deferred | Schema/API等仍 Not Frozen | 非范围 | T-SCOPE | `freeze_scope.json` |
| ABF-M-005 | Runtime transition | P3-126/P3-128只读 | preserve/adapt/defer映射 | 不追溯否定；后继继承V1 | 历史候选 | T-TRANSITION | `runtime_transition.json` |
| ABF-M-006 | promotion patch | canonical Draft bytes | 生成精确状态 patch 与post-hash | 仅元数据行变化 | 正文 bytes | T-PROMOTE | `canonical_promotion_patch.json` |
| ABF-M-007 | pristine verifier | 完整候选包 | 运行候选 verifier | 全矩阵 PASS | 输入／历史 | T-VERIFY | `verification.json` |
| ABF-M-008 | mutation: candidate hash | disposable manifest | 替换 V1 hash | verifier fail closed | pristine package | T-MUT-HASH | mutation result |
| ABF-M-009 | mutation: omitted legacy row | disposable matrix | 删除一条 V0.1 规范 | verifier fail closed | pristine package | T-MUT-LEGACY | mutation result |
| ABF-M-010 | mutation: scope expansion | disposable scope | 将 Schema/API 标为 Frozen | verifier fail closed | pristine package | T-MUT-SCOPE | mutation result |
| ABF-M-011 | mutation: body change | disposable promotion | 修改 V1 正文字节 | verifier fail closed | pristine package | T-MUT-BODY | mutation result |
| ABF-M-012 | history preservation | 固定只读历史清单 | 复算 before/after | 100% hash一致 | 全部历史 | T-HISTORY | history verification |
| ABF-M-013 | independent review | 候选 final hash | 全新会话自建核对 | Gate 1～4明确，结论Pass | 候选只读 | T-INDEPENDENT | independent Review/Evidence |
| ABF-M-014 | final closure | 全部前行Pass | 生成非自指Manifest与PM输入 | 计数全零、无提前Frozen | canonical／账本 | T-FINAL | Final Manifest + delivery |

## Evidence 合同

- 可运行 runner／测试源码：候选侧与独立评审侧各自保留源码；独立侧不得导入候选侧 runner。
- 逐行结构化结果：ABF-M-001～M-014 每行独立结果。
- before／after 状态：canonical、V0.1 history、P3-128 history hash。
- 日志／快照：静态任务不要求 GUI；保留命令、stdout/stderr 和 parser 结果。
- source／history hash：固定输入与所有保护资产。
- Manifest：候选与独立评审分别生成非自指 Manifest。
- 复跑命令：各一条，禁止网络和产品 Runtime。
- 临时清理：如未使用临时目录，明确 N/A；如使用，只允许任务卡预先声明的单一 task-local 根并精确清理。

## 计数与 Pass 公式

- P0：0
- P1：0
- P2：0
- Unknown：0
- Not Implemented：0
- Pass 公式：ABF-I-01～I-08、ABF-M-001～M-014全部PASS；候选和独立 Manifest可复算；独立评审Pass；五类计数全零。
- 允许的 N/A：仅 GUI、Runtime、DB 与临时清理在未使用时可逐项写明 N/A 理由；不得用于语义矩阵、mutation、独立评审或历史保全。

## Closure Cycle 与退出规则

- 首次 PM 不通过时的完整 Closure List：一次列出全部合同内缺口，原任务 Closure Cycle 收口。
- 同任务 Closure Cycle 条件：V1.0 当前正文、冻结范围、用户结果、只读输入和本 ABF 不变。
- 必须新建任务条件：需要实质修改 V1.0 正文、核心语义、AI 权限、V1 范围、Schema/API冻结范围，或本 ABF／授权边界变化。
- 不使用统一两轮 Rework 上限作为机械终止条件。
- Blocked 条件：固定输入冲突、V1.0 与 Frozen Core/Trust 不可调和、独立性不足、历史漂移、promotion 无法限制为元数据，或任何提前冻结／越权。

## 候选基线与只读保全

- 候选输入 hash／Manifest：V1.0 canonical SHA-256 `2db0cbeda30eea2a56d965220363fb6af6622acf413dfb4ee8c11ec867009a32`。
- 历史只读 hash／Manifest：D-0521 更新后的 FREEZE_STATUS `3d32e56876175636c00cf36b26e18bc284ff3d13123e291bce9f28f9e8f74a10`；P2-016 package `3ab2cece5252c7d982683d1a1cae9c9106f6fa707e6a308e86d27667e4aff8fa`；P2-016 PM Review `348b038cb01bde3eea27605d04c714c153ecb798131281dc08f2e859eb86152b`；P0-003 `e7c0b03ba0b9844cc9b515eaf42f88a844502e0ad3481ee01dff88e001d3cf29`；P0-009 `1c6759df1da2f9a95d6b1072c157eda023b9a985439290599dfae19577f90305`；P3-128 delivery `c385beb8267724945c7665f7a419e1358b5f1571a389055d7642fb660fca1a6b`；P3-128 PM Review `490ad63606597724465f594c63a49f2d370a9a8aebd236ad1f0ec819cda3dab3`。
- 允许发生变化的文件：仅任务卡列出的 P3-129 architecture/deliverable/review 输出；canonical promotion 由 PM 在最终用户 Gate 后另行精确执行。

## 启动前质疑窗口

- 执行方是否提出歧义：待投递后填写。
- PM 处理：若固定 V1.0 正文或冻结范围有歧义，任何候选动作前停止；不得自行折中回 V0.1。
- 最终冻结版本：`ABF-P3-129-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
