# LIFEOS-P3-098｜P3-097 完成点边界全新隔离独立复评

## 任务信息

- 任务 ID：`LIFEOS-P3-098`
- 优先级：P0
- 任务类型：全新隔离独立安全／数据生命周期／Evidence 复评
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 唯一用户结果：由未参与 P3-097 工程执行或 PM 验收的会话，使用全新独立 runner 与固定非敏感夹具，判断当前固定候选是否真正满足不可逆完成点和 task-local 失败关闭合同。
- 验收依据：`lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF ID：`ABF-P3-098-v1`
- ABF SHA-256：`249239ef03a84576d7cec01bd0c9eb0a21bccf032b032348a1665e7f8ca36fff`
- 生效决策：D-0408
- 正式 Rework 上限：2；评审发现候选 P0/P1 时直接把 P3-097 返回其 Frozen ABF 的 Rework，不在评审会话修候选。
- 是否允许修改项目账本：No

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。用户已采纳 P3-097 PM Pass，并明确要求创建本独立复评任务。

- 本次“采纳并创建”授权 PM 创建和登记任务，但不在 PM 主会话执行评审。
- 用户把本任务卡完整路径投递至一个全新隔离 Codex 独立评审会话时，该投递即授权本卡 Frozen ABF 范围内执行，无需重复口令。
- 仅使用项目只读候选与 `/private/tmp/lifeos-p3-098-*` 新建的固定非敏感夹具。
- 不读取真实个人文件、既有个人 DB、真实用户路径、网络、云、第三方、凭据或外部目标。
- 不启用 Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。
- 不关闭或重开 R-0051，不冻结资产／Schema/API，不恢复工程基线，不进入 Stage 4。

## Agent、模型与独立性

- 推荐执行 Agent：Codex 独立评审。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`high`
- 选择理由：评审涉及 SQLite 原子发布、删除／页面生命周期、路径链接边界、失败注入、P0/P1 与 Evidence 独立性。
- 允许降级模型：None。
- 禁止降级条件：全任务；完成点、路径／删除、真实本地数据边界、独立性、P0/P1 或 hash 冲突均不得降级。
- 后备模型：`gpt-5.5` + `xhigh`，仅首选不可用时使用并记录原因。
- 是否建议新建会话：Yes，强制。
- 推荐执行方式：Create New Session。
- 推荐会话类型：Codex 独立评审。
- 禁止复用：P3-097 工程执行会话、本 PM 主会话、任何参与 P3-094/P3-095/P3-096/P3-097 实现或 PM 反例设计的会话。
- 必须停止：无法证明会话独立、候选 hash 漂移、需要修改 P3-097、需要真实数据／外部访问、ABF 歧义或越界。

## 启动前验收依据冻结关卡

任何评审动作前必须完整读取 Frozen ABF，并在首份报告记录：

- 收到的任务卡与 ABF 完整路径。
- `ABF-P3-098-v1` 与 PM 记录的 SHA-256。
- 新隔离会话类型、精确接收时间、实际模型／推理强度。
- 与 P3-097 工程执行、PM 验收及历次相关会话的隔离声明。
- 是否发现验收歧义。

若发现歧义，必须在写 runner 或创建夹具前停止并回报 PM；不得自行改变 ABF。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. `lifeos/tasks/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review_acceptance_basis_freeze.md`
5. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
6. `lifeos/ACCEPTANCE_GOVERNANCE.md`
7. `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`
8. `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md`
9. `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md`
10. `lifeos/reviews/LIFEOS-P3-097_pm_review.md`
11. `lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md`
12. `lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md`
13. `lifeos/PM_OPERATING_MODEL.md` 的独立复评、P0、两层验收、删除／失败关闭章节
14. `lifeos/ROLE_MATRIX.md` 的独立评审、技术架构、数据／领域模型与安全职责
15. `lifeos/STAGE_GATES.md` 的 Gate 2–4
16. `lifeos/DECISION_LOG.md` 中 D-0401 至 D-0408、`lifeos/RISK_LOG.md` 中 R-0051

不得读取 P3-097 runner/tests/PM 反例源码来设计或复制测试；完成独立测试设计并将其 hash 落盘后，才可定向阅读被评审 runtime/CLI 源码做静态反查。仅在账本冲突时补读其他历史。

## 固定候选 hash

评审开始和结束时均须独立复算：

| 只读输入 | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md` | `3355c7f3e744abfd3be392902217f8abfa02bb783a492d87e88d8a63ddb2a09f` |
| `lifeos/tasks/LIFEOS-P3-097_irreversible_commit_completion_boundary_acceptance_basis_freeze.md` | `0160640bdee51436dba4da4fd1b8d4bde9a3b0e101fc09c2b0c5be79e254f048` |
| `lifeos/deliverables/LIFEOS-P3-097_irreversible_commit_completion_boundary_closure.md` | `a214e681ebf9449af9097edde42cd04b02dc83be2a09eec472e1a3b67c386ee1` |
| `lifeos/engineering/LIFEOS-P3-097/src/local_capture.py` | `1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453` |
| `lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py` | `ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659` |
| `lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py` | `9cc727e7510a4a269f5c8cb1f41e95662b84fc48311a7f229e47ab8bd395d986` |
| `lifeos/engineering/LIFEOS-P3-097/tests/test_runtime.py` | `e6cb780daa9b271adce01022c95dd414f9b34c0248f6b727785e9167a75306bf` |
| `lifeos/engineering/LIFEOS-P3-097/README.md` | `7fa834dbb9ecaf78200af01c37c2ba8029a3c511affce9c184a3042c8cfa6adf` |
| `lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md` | `63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311` |
| `lifeos/reviews/LIFEOS-P3-097_pm_review.md` | `057cbf047f412c38cc606ef033604a9e7591de83272ad2523ab0e02d86a58fee` |
| `lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md` | `90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183` |

还须复算 Engineering Manifest 16 个条目、PM Evidence Manifest 23 个条目及其引用的历史 hash；不得覆盖或修复任何 mismatch。

## 允许修改

只允许新建并修改：

- `lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md`
- `lifeos/reviews/LIFEOS-P3-098/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-098/evidence/`

独立 runner、fixture、结构化结果、日志、hash 与 Manifest 全部写入 P3-098 Evidence；不得创建 `lifeos/engineering/LIFEOS-P3-098/`。

## 严格只读与独立性禁令

- P3-094、P3-095、P3-096、P3-097 的全部资产和项目账本。
- 不得导入、执行、复制或改写 P3-097 `scripts/run_p3_097.py`、`tests/test_runtime.py`、`evidence/runner_source.py` 或 PM `pm_boundary_counterexamples.py`。
- 不得以 P3-097 的 27/27、53 unit 或 PM 9/9 结果代替独立动作。
- 可读取两个 Manifest、结构化结果和 PM Review 以核对声明，但独立测试设计必须先完成并 hash 固定。
- 可以直接载入当前固定 `src/local_capture.py` 并调用公开入口；静态源码反查必须在独立测试设计固定之后进行。

## 必须独立核查

1. 按 Frozen ABF 的 I-01 至 I-10、M-001 至 M-015 建立独立矩阵，所有 `-*` 子行分别执行。
2. 实际拦截 live `os.replace` syscall，不能只在调用前 hook 报错；覆盖 existing saved、repeat、missing DB。
3. 独立验证 candidate close、sidecar、清理重试、页面失效、发布后 FD close 的前后状态和残留。
4. 独立构造祖先目录链接、最终 DB/page 链接、hardlink、FIFO/dir、非规范路径及 render/clear 外部哨兵；任何变化前拒绝。
5. 独立变异 Schema、source、时间与 audit 顺序，确认 fail closed 和页面合同；不得使用真实内容。
6. 独立 Evidence 门必须实际拒绝缺行、重复 ID、缺断言或不可复核结果。
7. 前后复算所有固定 hash 与 Manifest；扫描禁止能力关闭态。
8. 全部 `/private/tmp/lifeos-p3-098-*` 在结束时精确清理；Evidence 不得含 SQLite、HTML、pyc、缓存或真实内容。

## Evidence 与交付要求

- 独立 Review：`lifeos/reviews/LIFEOS-P3-098/independent_review.md`
- 交付物：`lifeos/deliverables/LIFEOS-P3-098_p3_097_completion_boundary_fresh_isolated_independent_review.md`
- Evidence：`lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md`
- 至少保留：独立 runner 源码、frozen test-design hash、`results.json`、`acceptance_matrix.json`、`executed_test_ids.json`、`state_transitions.json`、`failure_injection_results.json`、source/history hash、静态扫描、残留报告、操作日志、复跑说明和非自指 Manifest。
- 每行必须记录独立 test/fixture/execution ID、before/after、实际断言与 Evidence 路径；不得批量映射 suite 结果。
- 本地模型预检可因 P0 高风险独立判断跳过，但必须在 Review 记录理由。

## 结论与回退

- 结论仅可为 Pass / Pass with Conditions / Rework / Blocked。
- Pass 条件：独立性成立、Frozen ABF 全部行独立 PASS、P0/P1/P2/Unknown/Not Implemented 全为 0、hash 一致、残留为 0。
- 发现候选 P0/P1、明确合同违反、Evidence 冲突或完成定义缺口：P3-098 结论为 Rework，P3-097 返回其同一 `ABF-P3-097-v1` 的 Rework 1/2；不得修改候选或另定新标准。
- 独立性不足、hash 不明漂移或授权环境无法完成：Blocked。
- 即使 Pass，R-0051 仍 P0/Open，P3-097 仍 Not Frozen；风险关闭、冻结、基线恢复与 Stage 4 必须另行任务、PM 验收和用户确认。

## 回复格式

严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天只输出独立结论、ABF/hash 核对、独立矩阵与 Evidence 摘要、P0/P1/P2/Unknown/Not Implemented、临时残留、Review/Evidence 路径和需要 PM 决策事项。
