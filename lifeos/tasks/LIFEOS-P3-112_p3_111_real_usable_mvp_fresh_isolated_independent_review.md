# LIFEOS-P3-112｜P3-111 可真实使用 MVP 全新隔离独立复评

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。用户已采纳 P3-111 Rework 1 PM Pass，并授权创建本任务。本任务只在项目工作区和全新 `/private/tmp/lifeos-p3-112-review-v1` 中，使用 P3-111 脱敏只读 Evidence 与固定非敏感合成夹具进行防御性独立复评；不启动会访问真实路径的 app，不访问 Pilot-2／真实个人文件／DB，不联网，不访问云、第三方、凭据或外部目标，不扩展通用文件、数据库或进程能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-112`
- 任务名称：P3-111 可真实使用 MVP 全新隔离独立复评
- 优先级：P0
- 任务类型：全新隔离、只读、工程／安全／数据生命周期／体验／Evidence 独立复评
- 单一结果：独立判断固定 P3-111 candidate、初次／Rework Evidence 与 PM Evidence 是否满足 `ABF-P3-112-v1` 的 15 行矩阵，并给出 Pass／Rework／Blocked。
- 是否为受控能力包：Yes；本任务自身是 P3-111 后继独立复评，不修复候选。
- 唯一风险边界：固定 P3-111 candidate 与脱敏 Evidence；唯一临时根；Pilot-2 和真实 app 零访问。
- 包内允许工作：独立测试设计、只读固定输入复算、正向 candidate 临时副本、offline locked test/build、静态与动态 Evidence 审计、独立 verifier／mutation、Evidence／Manifest／Review。
- 包内整改授权：仅 P3-112 自有 runner、Evidence、Review 和交付物；不得修改 P3-111 或项目账本。
- 必须拆分：候选修复、真实 app／DB 访问、导出、权限、恢复、风险、冻结、基线或 Stage 4 均不得混入。
- 建议篇幅：2000–4000 字；完整日志写入 Evidence。
- 是否适用 P3 Engineering Fast Lane：No
- 推荐执行 Agent：Codex 全新独立评审会话
- 推荐理由：需要独立 runner、离线 Rust 复跑、Evidence 语义与 mutation specificity 联合判断；不得形成自证循环。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 模型选择理由：P0 独立性、真实数据零访问、Tauri/IPC 静态边界、生命周期和 Evidence 真实性需要高强度联合判断。
- 允许降级模型：None
- 禁止降级条件：全部范围
- 必须升级条件：首选配置、离线 Cargo 或隔离副本工具不可用时 Blocked；不得换模或访问真实 app 绕过。
- 后备模型：None
- 是否需要后续独立评审：No；本任务自身即全新隔离独立复评，之后仍需 PM 验收和用户采纳。
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No
- 主责角色：独立 QA／安全与数据生命周期评审
- 协审角色：产品体验、可访问性、技术架构、数据与来源、AI 信任安全
- 必须通过的评审关卡：Gate 1、Gate 3、Gate 4；Gate 5 仅记录本人真实使用 Evidence 的范围，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Not Frozen`
- 验收治理文件：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-112-v1`
- ABF SHA-256：`780ffb07c8f1bd4948ae568771f7b5c334d7fd7bcc2de925a38edcf95e9f78bf`
- ABF 状态：Frozen
- 本任务正式 Rework 上限：2
- 当前正式 Rework 次数：0
- 生效决策：D-0453
- 执行授权方式：用户将本任务卡绝对路径投递至合格全新 Codex 会话即授权执行。
- 投递授权的会话类型与隔离要求：必须是未参与 P3-104 至 P3-111 工程、评审或 PM 验收的全新 Codex 独立评审会话；不得复用 P3-111 工程会话或 PM 主会话。
- 投递前额外用户确认：None；本任务禁止访问真实路径／DB／app。若任何步骤需要 Pilot-2 或真实 app，立即 Blocked 并回 PM，不得请求会话内扩大。
- 授权证据记录：首份会话报告记录收到的本任务卡绝对路径、会话类型、接收时间、实际模型／推理强度和独立性声明。

## 会话隔离与读序

- 必须新建会话；P3-111 工程会话不得评审自身结果。
- 在读取 `lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py`、`run_disposable_mutations.py`、初次／Rework `semantic-verifier-result.json`、`mutation-results.json` 前，先根据任务卡、Frozen ABF 和 L1 创建 `lifeos/reviews/LIFEOS-P3-112/evidence/test_design.md`，记录 SHA-256 与时间。
- 独立 runner 不得导入、复制或调用 P3-111 runner／verifier 作为 Pass 主证据；冻结独立设计后可只读运行提交 verifier作交叉比较。
- P3-104 至 P3-111 的全部资产只读；旧授权、结论和范围不得继承为本任务授权。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. `ABF-P3-112-v1`
5. `lifeos/ACCEPTANCE_GOVERNANCE.md`
6. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
7. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
8. P3-111 原任务卡、Frozen ABF、初次／Rework 交付物
9. P3-111 `candidate_provenance.md`、`product_gap_matrix.md`、初次／Rework Engineering Manifest
10. P3-111 PM Review、初次／Rework PM Evidence Manifest

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：独立评审、任务投递、真实能力、两层验收相关章节。
- `lifeos/ROLE_MATRIX.md`：PM、独立 QA、工程、体验、数据、AI 信任职责。
- `lifeos/STAGE_GATES.md`：Gate 1／3／4／5 与 Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0448 至 D-0453。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。

只在发现账本或固定输入冲突时定向补读，不全文重读无关历史；不读取 `PROJECT_CONTEXT.md`，因为本任务不改变产品方向、架构或范围。

## 启动前关卡

在任何 copy／test／build 或工程 verifier／mutation 结果阅读前：

1. 核对 `gpt-5.6-terra + xhigh`、全新会话与独立性。
2. 核对 ABF hash、12 项固定输入和 72-file candidate tree hash。
3. 只以存在性检查 `/private/tmp/lifeos-p3-112-review-v1` 必须不存在；若存在，Blocked，不删除。
4. 写入并冻结独立 `test_design.md`／hash／时间及 read-order。
5. 明确记录 Pilot-2 path lookup、metadata、open、read、hash、copy、cleanup 和真实 app launch 全为禁止动作。

## 验收范围

完整执行 Frozen M-001 至 M-015：

- 授权、模型、全新会话、独立读序；
- 12 项固定输入与 72-file candidate tree；
- allowlist 临时副本、offline locked test/build、8 个固定非敏感 tests、静态三 IPC／关闭态；
- 初次／Rework 动态闭环 12 行及脱敏 JSON、AX、截图、hash、内容身份／来源；
- 评审自有 raw semantic verifier；初次 37/37 与 Rework 38/38；
- 未篡改祖先含 `/disposable/noop` control exit 0；
- 六类独立真实 mutation 的唯一预期失败；
- 提交 verifier 只读交叉比较、PM finding closure、历史保全、Manifest 与精确清理；
- 风险、冻结和阶段不变。

不得以 P3-111 Markdown Pass、自报计数、工程 runner 或 PM Pass 直接代替本任务独立 Evidence。

## 允许修改与交付

仅允许写入：

- `lifeos/deliverables/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-112/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-112/evidence/`
- `/private/tmp/lifeos-p3-112-review-v1`（最终必须精确清理）

Evidence 至少包含：authorization、session-boundary、test-design、read-order、fixed-inputs、candidate-manifest、copy-inventory、offline logs、structured test/build results、static-results、dynamic/privacy audit、独立 verifier 源码及结果、unchanged control、六 mutation、提交 verifier cross-check、closure matrix、cleanup、逐行 M-001–M-015 与顶层非自指 Manifest。

完整交付物：`lifeos/deliverables/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review.md`

独立 Review：`lifeos/reviews/LIFEOS-P3-112/independent_review.md`

## 结论与退出

- 专项结论：Pass / Rework / Blocked；PM 最终裁决。
- Pass：Frozen I-01–I-11、M-001–M-015 与全部子动作通过；P0/P1/P2/Unknown/Not Implemented 全 0；Pilot-2 访问 0；历史写入 0；临时残留 0；Review Manifest 可复算。
- 同任务 Rework：仅 P3-112 自身 runner／Evidence／Review 问题，ABF 不变且未达两轮上限。
- 候选 P0/P1 或固定输入漂移：评审不得修复，交 PM 决定关闭／新任务。
- Blocked：独立性、模型、固定输入、离线工具或临时根空基线不成立；需要真实 app／Pilot-2 才能判断。
- 即使 Pass，也不关闭 R-0040／R-0052，不扩大 R-0051，不冻结、不恢复基线、不进入 Stage 4。

## 本地预检与聊天回复

- 可跳过本地模型预检：本任务是 P0 独立性、真实数据零访问和 Evidence 真实性最终判断；Review 必须注明，预检不得决定结论。
- 聊天严格使用 `SESSION_REPORT_TEMPLATE.md`，只输出结论、Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、资产／风险、下一步、Review／Evidence 路径及需 PM 确认事项。
