# LIFEOS-P3-097｜不可逆提交完成点边界收口

## 任务信息

- 任务 ID：`LIFEOS-P3-097`
- 优先级：P0
- 任务类型：全新后继任务／高风险受控能力包
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 唯一用户结果：以 live DB 原子发布为唯一不可逆完成点，一次收口新捕获与幂等重复在发布前失败、发布失败和发布后资源释放错误下的返回语义、持久化状态、页面状态与 task-local 残留一致性。
- 验收依据：`lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md`
- ABF ID：`ABF-P3-097-v1`
- ABF SHA-256：`0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048`
- 生效决策：D-0406
- 正式 Rework 上限：2；超过后关闭本任务并重新拆卡，不增加第三轮。
- 是否允许修改项目账本：No

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本任务只使用项目工作区只读候选和 `/private/tmp` 新建的固定非敏感夹具，验证防御性的 task-local 路径、SQLite 完成点、失败关闭与生命周期一致性。

- 用户于 D-0406 明确要求 PM 创建本任务；这只授权任务登记与 ABF 冻结，不自动启动工程执行。
- 用户将本任务卡的明确路径投递至一个全新隔离 Codex 工程会话时，该投递才构成本卡冻结范围内的执行授权；无需在该专项会话重复口令。
- 不访问真实个人文件、既有个人数据库、真实用户路径、网络、云、第三方系统、凭据或外部目标。
- 不启用 Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。
- 不关闭或重开 R-0051，不冻结资产或 Schema/API，不恢复工程基线，不进入 Stage 4。

## Agent、模型与会话路由

- 推荐执行 Agent：Codex 工程执行。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`high`
- 选择理由：任务涉及删除／页面失效、SQLite 不可逆完成点、失败原子性、sidecar 生命周期和证据真实性，属于 P0 高风险工程收口。
- 允许降级模型：None
- 禁止降级条件：路径／删除、SQLite 生命周期、post-publish 语义、sidecar、P0/P1、Evidence 冲突或范围争议。
- 必须升级／停止：需要接触真实文件／DB、外部访问、修改 ABF、改变公开状态或 Schema/API、扩大目录／能力／授权、无法保全历史 hash。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用时使用并记录原因。
- 是否建议新建会话：Yes，强制。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 工程执行。
- 会话判断理由：P3-096 已达到正式 Rework 2/2 并关闭；P3-097 是新任务、新 ABF、新工程目录与新授权边界，禁止继承旧会话的任务授权。
- 是否需要独立性隔离：后续独立复评 Yes；本执行会话不得独立评审自身成果。
- 任务完成后是否建议保留会话：Yes，仅供本任务最多两轮同 ABF 正式 Rework；不得接续其他任务。

## 启动前验收依据冻结关卡

专项会话在任何工程动作前必须完整读取 Frozen ABF，并在首份报告记录：

- 收到的任务卡与 ABF 完整路径。
- `ABF-P3-097-v1` 及 PM 记录的 SHA-256。
- 新隔离工程会话类型、精确接收时间、实际模型和推理强度。
- 是否发现验收歧义。

若存在歧义，必须在工程动作前停止并回报 PM；不得自行改写 ABF。专项会话启动后若需实质修改验收依据，P3-097 必须关闭并由 PM 新建任务。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md`
5. `lifeos/ACCEPTANCE_GOVERNANCE.md`
6. `lifeos/reviews/LIFEOS-P3-096_pm_review.md`
7. `lifeos/engineering/LIFEOS-P3-096/rework-1/evidence/MANIFEST.md`
8. `lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/MANIFEST.md`
9. `lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/pm_post_commit_sidecar_counterexample.py`
10. `lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/pm_post_commit_sidecar_counterexample.json`
11. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
12. `lifeos/PM_OPERATING_MODEL.md` 的两层验收、受控能力包、删除／失败关闭与 Rework 分界章节
13. `lifeos/ROLE_MATRIX.md` 的 PM、技术架构、数据／领域模型、AI 信任与安全职责
14. `lifeos/STAGE_GATES.md` 的 Gate 2–4
15. `lifeos/DECISION_LOG.md` 中 D-0401 至 D-0406、`lifeos/RISK_LOG.md` 中 R-0051

仅在发现账本冲突时定向补读，不全文翻读无关历史。

## 候选基线

以下 P3-096 live candidate 与全部历史资产严格只读；专项会话开始时须先复算：

| 输入 | 冻结 SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-096/src/local_capture.py` | `c56b3232be91b60edad5e428e1a00407c4dd40366899123e2cc4d5c6e550fe64` |
| `lifeos/engineering/LIFEOS-P3-096/scripts/operator_cli.py` | `632f58e2e4ca66153db0992139dd5579504c2d06b0010d4fea65497c30db437b` |
| `lifeos/engineering/LIFEOS-P3-096/scripts/run_p3_096.py` | `e1832b146a97df1651f950e9ada359514caa8d5466771783c44e35a99fc3994b` |
| `lifeos/engineering/LIFEOS-P3-096/tests/test_runtime.py` | `6f090e720094a77cc28830d9343c532e3a46ee2be227d416fe5571e6252d3bba` |
| `lifeos/engineering/LIFEOS-P3-096/README.md` | `0a8c3545c734254331bcc303a0f12757132b87e829a627a91d225299ad296899` |
| `lifeos/deliverables/LIFEOS-P3-096_post_commit_audit_evidence_closure.md` | `2f39a5f4def9344301ce67b34416afb653ab98199435f3359fb0c141b1d6e8ff` |

专项会话核对上述 hash 与两个 P3-096 Manifest 一致后，才可把候选复制到新的 P3-097 工程目录。不得原地修改 P3-096。

## 允许修改

只允许新建并修改：

- `lifeos/engineering/LIFEOS-P3-097/`
- `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`

P3-097 工程目录至少包含：

- `src/local_capture.py`
- `scripts/operator_cli.py`
- `tests/test_runtime.py`
- `scripts/run_p3_097.py`
- `README.md`
- `evidence/`

## 严格只读

- P3-094、P3-095、P3-096 的全部任务卡、ABF、工程、交付物、Review、PM Evidence、Engineering Evidence 与 Manifest。
- `lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/` 中 PM 反例和结果。
- 项目账本、风险日志、冻结记录及其他任务资产。

## 冻结工程范围

只处理：

1. 重组内部完成点，使 live DB 原子发布成为唯一不可逆完成点；允许在 P3-097 内采用 task-local shadow DB／copy、预发布验证和原子替换等内部实现，但不得改变公开 Schema/API 或产品语义。
2. 确保所有可能导致公开失败的候选 commit、close、sidecar 检查／清理、页面失效准备、路径稳定性检查、Schema/audit 验证与发布准备在 live 发布前完成。
3. 确保 live 发布后的资源释放错误不会覆盖准确成功；不得用吞掉发布前完整性错误的方式实现。
4. 对新捕获与幂等重复覆盖 ABF 的正常、失败和 Evidence 门矩阵，保证 DB、audit、页面、sidecar、staging、temp 和返回值终态一致。

## 非范围与越界停止

- 不新增或改变公开 `saved`／`idempotent_repeat` 状态、CLI 入口、业务字段、Schema/API、来源或审计业务定义。
- 不重新设计已经冻结在 ABF 之外的产品能力；不增加并发／崩溃恢复或生产部署承诺。
- 不读取或修复任何既有个人 DB，不访问工作区外既有文件。
- 不创建独立复评、风险关闭、冻结、基线恢复或 Stage 4 任务。
- 若发现只有改变上述边界、允许持久残留、允许假成功／假失败或修改 ABF 才能完成，立即停止并回报 PM，不得扩卡。

## 实现与 Evidence 要求

- 先复制候选到 P3-097，再在新目录修改；P3-096 保持字节级只读。
- 必须实现 `ABF-P3-097-v1` 的全部 I-01 至 I-08、M-001 至 M-017；M-015 的每个适用失败点必须有独立子测试 ID。
- 每个矩阵行必须独立创建固定非敏感夹具、实际执行、记录 before/after 并产生结构化结果；不得用 unit suite 总布尔值批量标 PASS。
- 所有生命周期操作均须验证同一 task-local 目录、规范化路径、完整目录链接链、最终文件类型及 render/clear 本地目录约束。
- 失败路径必须在任何 live 文件／数据库变化前停止；成功与失败均须核对哨兵、DB、audit、页面和残留。
- runner 必须在缺行、fixture 断言缺失、执行 ID 重复冒充、Evidence 缺失或 Manifest 不一致时退出非零并计入 Not Implemented／相应严重度。
- Evidence 至少包含：runner 源码、`results.json`、`acceptance_matrix.json`、`executed_test_ids.json`、`completion_point_trace.json`、`state_transitions.json`、`failure_injection_results.json`、source/history hash、unit/regression 日志、临时残留报告、操作日志、复跑说明和非自指 Manifest。
- Evidence 不得包含 SQLite、HTML、pyc、缓存、真实内容或未列入 Manifest 的文件。
- 所有 `/private/tmp/lifeos-p3-097-*` 产物在结束时精确清理；不得覆盖工程或 PM 历史 Evidence。
- 本轮属于删除及真实本地数据完成点边界的高风险最终判断，可跳过本地模型预检；若跳过，须在交付物注明本地模型不得决定该高风险边界，执行侧仍完成全部确定性自检。

## 完成定义

仅当 Frozen ABF 的全部不变量和矩阵行独立 PASS，P0/P1/P2/Unknown/Not Implemented 均为 0，候选与历史只读 hash 一致，临时残留为 0，runner 退出 0，才允许提交 PM。

执行侧提交前发现的同范围问题必须在本任务内自行修正，不计正式 Rework。PM 或后续独立评审正式判定后，最多允许两轮同 ABF Rework；达到上限或需要修改 ABF 时，本任务关闭并新建任务，不得无限膨胀。

## PM 与后续关卡

- PM 将在全新 `/private/tmp` 固定非敏感夹具复算候选、Manifest 与历史 hash，复跑提交 runner，并只使用可映射到 L1 或 Frozen ABF 的反例。
- PM Pass 后必须等待用户采纳；用户采纳后才可创建一个全新隔离独立复评。
- P3-097 不关闭 R-0051、不冻结资产、不恢复基线、不进入 Stage 4。

## 回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出执行结论、ABF ID／hash 核对、测试与 Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、修改文件、交付物、Evidence、临时残留和是否需要 PM 决策。
