# LIFEOS-P3-065｜基础权限设置受控实现与验证

## 任务结论

本任务在新建隔离目录 `lifeos/engineering/LIFEOS-P3-065/` 中完成一套仅面向非敏感合成记录的基础权限设置 CLI、SQLite 适配层、自动化回归与可复跑 Evidence。实现没有改动 P3-009、P3-031、P3-063、P3-064、项目账本或任何历史 Evidence。

事实：D-0280 窄 Rework 后的当前测试为 **23 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**，测试入口退出码为 0。初版 14 PASS Evidence 已封存于 `evidence/initial/`，没有覆盖。受控 `allow` 只产生 SQLite 内的 `local_decision_only` 返回值，不读取／发送内容，不调用 AI、网络、Tauri/IPC、真实路径、Vault、导出或外部动作。

推断：在任务卡限定的单进程、合成 SQLite 范围内，默认拒绝、显式设置、时效和四维绑定、撤回后的 fail-closed 消费门、可观察审计及幂等回执均有运行证据。

建议：提交 PM 验收后，按任务卡要求新建隔离安全／体验复评会话；不得把本任务结果升级为真实权限、真实 AI 处理许可、风险关闭、基线恢复、冻结或 Stage 4 准入。

## 范围与实现

实现使用 Python 标准库与 SQLite。操作者 CLI 要求 `--synthetic-only`，并只接受预置的合成 Project `project-synthetic-001`、合成数据类别、受控目的、位置和处理者枚举。`--run-id` 仅允许字母、数字和连字符，不能传入路径。运行文件只写入本任务的 `runtime/` 目录。

设置前可调用 `preview` 查看摘要；摘要明确显示 `default_decision: deny`、`external_action: none` 和 `ai_consumption: disabled_until_local_allow`。创建设置必须提供决定、正整数毫秒有效期、幂等键以及精确的 `CONFIRM`。这避免了将普通参数输入误当成授权事实。`grant` 记录为 `granted`，`deny` 记录为 `denied`；默认没有记录时一律拒绝。

已授予设置在消费时必须同时匹配：受控 Project、数据类别、处理目的、处理位置、处理者，并且有效期必须严格晚于当前时刻。D-0280 Rework 明确了冲突语义：任一同一精确绑定的当前有效 `denied` 一律优先并返回 `explicit_deny_current`；没有有效 deny 时，仅恰好一项有效 `granted` 能 allow；多个有效 grant 因无法明确选择而返回 `ambiguous_multiple_current_grants`。任何其他情况都返回 `allowed: false`。拒绝理由同时保留 `default_deny`、`authorization_not_current_or_not_matching` 和 `invalid_context`，所有结果均固定声明 `external_action: none`。

撤回只接受精确 `REVOKE`、授权 ID 和幂等键。撤回把授权状态更新为 `revoked`、版本递增，并追加审计项；后续同一消费请求不再命中有效授权。重复撤回返回可观察的幂等回执，不重复写入。冲突的幂等键、空输入、非法值、无效确认和不可撤回状态都以可见失败返回，绝不报告成功。

## 授权矩阵

| 场景 | 预期 | 运行结果 |
|---|---|---|
| 无授权消费 | 默认 deny | PASS：`default_deny` |
| 有效 `grant` 且四维绑定匹配 | 仅允许本地合成决定 | PASS：`allowed_local_synthetic` |
| grant → deny（同精确绑定） | deny 优先阻断 | PASS：`explicit_deny_current` |
| deny → grant（同精确绑定） | deny 优先阻断 | PASS：`explicit_deny_current` |
| 多项并列有效 grant | 无法选择时阻断 | PASS：`ambiguous_multiple_current_grants` |
| 已撤回授权 | 阻断且版本递增 | PASS |
| 到达有效期 | 阻断 | PASS |
| purpose / location / processor / category 不匹配 | 阻断 | PASS |
| 空／非法输入或错误确认 | 拒绝且不成功 | PASS |
| 重复 grant / deny、重复撤回 | 幂等；不重复持久化 | PASS |
| 撤回幂等键用于另一授权 | 可见失败；不改变第二项授权 | PASS |
| 审计、确认、时间、版本 | 可查看、可复跑 | PASS |

审计快照保留授权 ID、决定、操作者确认、时间、版本与结构化决定细节。该快照明确区分：授权事实在 `authorizations`，操作者确认在 `operator_confirmation`，消费结果在 `audit_events`；本任务没有保存用户原文，也没有 AI 生成、推断或建议对象。因此不存在把原文、AI 状态与确认事实混写为同一字段的问题。

## 失败路径与安全边界

拒绝或失败不会触发回退许可。未知 Project、未列入白名单的类别／目的／位置／处理者、非正有效期、无确认、错误确认、空幂等键、冲突幂等键、未知授权以及对 denied/revoked 状态的错误操作均可见失败或拒绝。消费函数先执行输入范围校验，再查询 SQLite；不能校验的上下文返回 `invalid_context`，没有开放式默认值。

针对 P3-009 的只读消费门输入，本实现继承“精确绑定、有效期、默认拒绝”的最小方向，但未复制或改动其工程资产。针对 P3-031 的只读授权约束输入，本实现使用独立简化表来证明操作者级设置流程，不声称实现其候选 SQL 生命周期、audit/outbox、清理、并发或 migration 合同。针对 P3-063 的只读闭环输入，本实现沿用合成 Project、SQLite、显式操作者输入、可复跑快照和无外部动作边界，但没有调用或修改其代码。

本实现不处理真实身份、个人数据、真实数据库迁移、真实路径或 Vault；不运行 Tauri/IPC；不使用网络、云或第三方处理者；不做导出、同步、多设备、L3 或外部用户动作。R-0013、R-0014、R-0015、R-0021 和 R-0040 继续为项目账本中的既有风险：本任务没有关闭、重开或修改它们。

## 验证与 Evidence

复跑命令：

```sh
lifeos/engineering/LIFEOS-P3-065/scripts/run_tests.sh
```

运行结果和完整用例名见 `lifeos/engineering/LIFEOS-P3-065/evidence/test_results.json`；原始输出见 `evidence/test_run.log`；基础授权、审计、确认、时间与版本快照见 `evidence/snapshot.json`；九项顺序／冲突矩阵的返回、审计、版本与持久化快照见 `evidence/conflict_matrix_snapshot.json`。初版 14 PASS Evidence 已保留在 `evidence/initial/`。所有当前输入和产物 SHA-256 见 `lifeos/engineering/LIFEOS-P3-065/evidence/MANIFEST.md`。静态关闭态抽查未发现网络客户端、Tauri/IPC 实现、导出或路径访问调用；唯一匹配为显式边界状态文字。

工程资产包括 `src/permissions.py`、`scripts/permission_cli.py`、`scripts/run_tests.sh`、`tests/test_permissions.py`、`README.md` 和 `evidence/`。CLI 回归验证“预览 → CONFIRM 授予 → 受控消费允许 → CONFIRM 拒绝 → 后续消费阻断”；测试套件覆盖其余正负路径。测试全程没有访问任务目录外的工程输入。

## 角色与关卡

AI 信任与安全主责检查通过本任务适用项：授权必须显式确认，默认拒绝，当前有效 deny 优先，撤回和过期后不再允许消费，审计可观察，且 allow 不产生 AI 或外部动作。数据／领域模型协审通过适用项：授权、确认、撤回命令与审计分表且带版本、时间；没有把 AI 或用户原文伪装为授权事实。产品／体验协审通过适用项：设置摘要、明确 `CONFIRM` / `REVOKE` 和失败回执让操作者可辨别状态，但尚无真实 UI 可用性证据。技术架构与独立 QA 协审通过受控运行项：标准库、SQLite、单目录、23 项回归、初版封存快照、Rework 冲突矩阵、结构化结果和 hash 均可复跑。

Gate 2 通过本任务受控设置适用项：没有混淆内容身份、授权事实和确认。Gate 3 通过本任务受控设置适用项：具体绑定、确认、拒绝、撤回、有效期和 fail-closed 均有运行证据。Gate 4 通过本任务受控可行性适用项：本地最小实现可运行、可审计、可复跑且未引入重型架构。Gate 1、Gate 5，以及 Gate 2–4 的真实能力、真实数据、恢复和 Alpha 范围仍未通过；绝不判定任一 Stage 4 Gate 通过。

## 未实现能力与 PM 决策

未实现能力包括：真实身份鉴别、多进程／并发／WAL、真实数据与路径、真实 Tauri/IPC、真实 AI／云／第三方处理、真实清理状态机、导出、同步、备份恢复、用户界面与外部用户验证。这些不是失败伪装为通过，而是明确非范围；`not_implemented: 0` 仅指任务卡所要求的受控合成验收场景均已实现并测试。

需要 PM 决策：Yes。请 PM 对本交付物和 Evidence 做验收判断，并在通过后按任务卡新建隔离独立安全／体验复评。无需 PM 在本任务中批准真实能力；任何向真实权限或 Stage 4 的变化都需要新的明确授权。
