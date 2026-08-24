# LIFEOS-P3-096｜捕获完成点、审计语义与逐行 Evidence 收口

## 任务信息

- 任务 ID：`LIFEOS-P3-096`
- 优先级：P0
- 任务类型：补丁／条件整改型受控能力包
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 唯一用户结果：在不修改 P3-094 历史资产的前提下，关闭 D-0399 的捕获完成点、审计语义和逐行 Evidence 三项缺口。
- 验收依据：`lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md`；V1 作为规范性继承输入只读保留。
- ABF ID：`ABF-P3-096-v2`
- ABF SHA-256：`bc529ddaf2ed965e96047dc6681acdd9e17c892a4db2ddd850038cbbd239ea09`
- 生效决策：D-0401、D-0402
- 正式 Rework 上限：2；超过后关闭本任务并重新拆卡，不再增加 attempt。
- 是否允许修改项目账本：No

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本任务仅使用项目工作区及 `/private/tmp` 新建的固定非敏感夹具，用于防御性修复、失败原子性验证、审计完整性验证和 Evidence 完整性验证。

- 不访问真实个人文件、既有个人数据库、真实用户路径、网络、云、第三方系统、凭据或外部目标。
- 不启用 Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。
- 不扩大或演示攻击能力；失败注入和伪造状态只作用于本任务新建的固定非敏感夹具。
- 不关闭或重开 R-0051，不冻结资产或 Schema/API，不恢复工程基线，不进入 Stage 4。

用户已于 D-0401 采纳并应用新治理流程，授权 PM 创建本任务。用户将本任务卡路径投递至符合隔离要求的新 Codex 工程会话，即授权在本卡和 ABF 冻结范围内执行；无需重复“授权执行”口令。

## Agent、模型与会话路由

- 推荐执行 Agent：Codex 工程执行。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`high`
- 选择理由：任务涉及真实本地数据边界候选、失败原子性、审计可信度和 Evidence 自动门，错误后果高且需要跨代码、测试和结构化证据复核。
- 允许降级模型：None
- 禁止降级条件：删除／路径、SQLite 生命周期、失败后持久化、审计语义、Evidence 冲突、P0/P1 或范围争议。
- 必须升级／停止：接触真实文件／DB、外部访问、ABF 歧义、需要改变 Schema/API／能力／目录／授权、无法保全 P3-094 历史 hash。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用时使用并记录原因。
- 是否建议新建会话：Yes
- 推荐执行方式：Create New Session
- 推荐会话类型：Codex 工程执行
- 会话判断理由：P3-094 已按 D-0401 关闭为未通过并由本任务接替；必须建立新的任务边界、工程目录、Evidence 和 ABF 读取状态，避免继续继承 attempt-9 上下文。
- 是否需要独立性隔离：后续独立复评 Yes；本执行会话不得独立评审自身成果。
- 任务完成后是否建议保留会话：Yes，仅供本任务最多两轮正式 Rework；不得接续其他任务。

## 启动前验收依据冻结关卡

专项会话在任何工程动作前必须完整读取 ABF V1 与当前 Frozen 的 `lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md`，并在首份报告记录：

- 收到的任务卡和 ABF 完整路径。
- ABF ID、版本及 PM 记录的 SHA-256。
- 会话类型、接收时间和实际模型。
- 是否发现验收歧义。

若有歧义，必须在工程开始前停止并回报 PM；不得自行解释或修改 ABF。工程开始后 ABF 不再修改；任何实质变化必须关闭本任务并新建任务。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. `lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze.md`（V1，SHA-256 `2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58`）
5. `lifeos/tasks/LIFEOS-P3-096_acceptance_basis_freeze_v2.md`（当前 Frozen ABF）
6. `lifeos/reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md`
7. `lifeos/ACCEPTANCE_GOVERNANCE.md`
8. `lifeos/reviews/LIFEOS-P3-094_pm_review.md` 的 D-0399 至 D-0402 章节
9. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/MANIFEST.md`
10. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.py`
11. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.json`
12. `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/sources/` 初次候选快照
13. `lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`
14. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
15. `lifeos/PM_OPERATING_MODEL.md` 的两层验收、受控能力包、删除／失败关闭、Rework 分界章节
16. `lifeos/ROLE_MATRIX.md` 的 PM、技术架构、数据／领域模型、AI 信任与安全职责
17. `lifeos/STAGE_GATES.md` 的 Gate 2–4
18. `lifeos/DECISION_LOG.md` 中 D-0398 至 D-0402、`lifeos/RISK_LOG.md` 中 R-0051

仅在发现直接冲突时定向补读，不全文翻读无关历史。

## 允许修改

只允许新建并修改：

- `lifeos/engineering/LIFEOS-P3-096/`
- `lifeos/deliverables/LIFEOS-P3-096_post_commit_audit_evidence_closure.md`

工程开始时，先按晚到提交 Manifest 复算全部候选 hash；一致后从其列出的 P3-094 路径复制候选代码到 P3-096 新工程目录。初次 PM Evidence `sources/` 仅作为对照。不得修改原 P3-094 工程、交付物、Review 或 Evidence。

P3-096 工程目录至少包含：

- `src/local_capture.py`
- `scripts/operator_cli.py`
- `tests/test_runtime.py`
- `scripts/run_p3_096.py`
- `README.md`
- `evidence/`

## 严格只读

- P3-094 attempt-1 至 attempt-9 的全部工程、交付物、Review、PM Evidence 和 Manifest。
- P3-095 的任务、交付物、Review 和 Evidence。
- `lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/sources/` 候选基线。
- `lifeos/reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md` 及其列出的所有候选路径。
- 项目账本、冻结状态、风险日志和其他任务资产。

## 冻结范围

只处理：

1. 捕获完成点：任何返回失败的 capture 不得留下新 DB、记录、audit、页面变化、sidecar、staging 或临时残留；成功则持久化状态和返回值一致且无残留。
2. 审计语义：future capture／saved、saved 与 capture 时间不一致、逆序 repeat、无对应 active capture 的 repeat、错误 clear count 和乱序审计必须 fail closed。
3. Evidence 自动门：每个 ABF 矩阵行必须由独立夹具和实际测试执行决定 PASS；不得以整个 suite 的单一布尔值批量映射。

## 非范围

- 不重新设计 P3-094 已通过的路径、文件类型、canonical Schema、来源标注、render／clear 页面合同。
- 不新增产品功能、公开入口、业务 Schema、迁移、并发／崩溃恢复或生产能力。
- 不读取或修复任何既有个人 DB。
- 不创建独立复评、风险关闭、冻结、基线恢复或 Stage 4 任务。
- 发现冻结范围之外的新问题时，不得扩卡；记录证据并回报 PM，由 PM 按 L1/L2 判断当前结论和新任务候选。

## 执行与 Evidence 要求

- 先运行 P3-094 候选基线和 PM 六个反例，形成只读 baseline 结果。
- 按 ABF 每一矩阵行建立独立夹具、测试 ID、实际执行记录和 before／after 断言。
- runner 必须记录实际执行的测试 ID；缺失、重复冒充、未执行或由 suite 汇总映射时退出非零。
- 所有测试只使用 `/private/tmp/lifeos-p3-096-*` 固定非敏感目录，结束时精确清理。
- Evidence 不得包含 SQLite、HTML、pyc、缓存、真实内容或未列入 Manifest 的文件。
- 新 Evidence 至少包括：runner 源码、`results.json`、`acceptance_matrix.json`、`state_transitions.json`、`audit_semantics_results.json`、`failure_injection_results.json`、`executed_test_ids.json`、unit／regression 日志、source／history hash、临时残留报告、复跑说明和 Manifest。
- 本地模型预检可因高风险最终判断跳过，但交付物必须注明理由。

## 完成定义

以 `ABF-P3-096-v2` 为当前 L2 依据，并规范性继承 V1 的全部不变量和矩阵。只有全部强制矩阵行实际 PASS，P0/P1/P2/Unknown/Not Implemented 均为 0，历史只读 hash 一致且临时残留为 0，才允许提交 PM。

执行侧提交前发现的同范围问题必须自行修正，不计正式 Rework。PM 或独立评审正式判定 Rework 后，最多允许两轮；ABF 不变。超过上限或需要修改 ABF，任务终止并回到 PM 新建任务。

## PM 与后续关卡

- PM 将在全新 `/private/tmp` 固定非敏感夹具复算 hash、复跑 runner，并仅使用可映射到 L1 或 ABF 的反例。
- PM Pass 后等待用户采纳；采纳后才可创建全新隔离独立复评。
- P3-096 不关闭 R-0051、不冻结资产、不恢复基线、不进入 Stage 4。

## 回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出执行结论、ABF ID／hash 核对、测试与 Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、修改文件、交付物、Evidence、临时残留和是否需要 PM 决策。
