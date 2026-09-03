# LIFEOS-P3-145 Mandatory Independent Review — Phase B Closure-2

## 评审信息与终局

- 任务：`LIFEOS-P3-145`；评审性质：同一独立评审的 D-0635 Closure-2。
- 固定候选：commit `579914d06923db65db8c3b421b2da663a1950354`，tree `481ffa80e88838669a233ced526cb5321ca0b697`；Task／ABF SHA-256 分别为 `2cbaedabc1049d1e4e13d58c39b13095bd498a685cc5f8028ba0e9a17816f626`／`040c7166afac7e45bfcdf893c1cc23bfa28827e6e2d1d186ffd8cc4f049e66b1`。
- 本 Closure 只补 Closure-1 的合成 response、feedback、credential lifecycle/failure-closed 矩阵；不重跑已成立的 20 IPC、候选绑定、PID→AXWindow→WebView、三档截图或基础 Today 矩阵。
- Closure-1 的 `Blocked` 报告及 Attempt-1 的 P0-145-IR-001 隔离历史均保持只读、未改写；Attempt-1 的错误 App Evidence 未被用作本结论。
- **终局：Blocked（不是候选工程 Rework）**。本 Closure 完成了所允许的缺口测试，但 Frozen Pass 公式仍要求 AC-01～20 全 Pass、Unknown=0；若干未重跑的 inherited gap 仍是 Unknown。
- P0/P1/P2/Unknown/Not Implemented：**0 / 0 / 1 / 7 / 0**。

## 独立性、边界与动态事实

1. Closure-2 先完成 review-owned test design、allowlist、禁止路径声明和 precontact seal，之后才接触 detached、只读候选。候选与临时构建目录已在本报告前 marker-gated 精确清理。
2. `review_synthetic_adapter_contract.py` 独立通过两项检查，并拒绝三项破坏 mutation：把 synthetic model/response 改为 real，以及移除 credential-presence guard。完整机器可读结果在 `evidence/synthetic_adapter_static_results.json`。
3. 仅使用 sealed 的固定非敏感 Health、Work、Durable Memory、问题和 Keychain canary。UI 对每次模型测试和回答均明确显示合成／无网络；运行期 receipt ledger 的两次 `test_models` 与两次 `confirmed_minimal_context` 均为 `methodClass=NONE`、`requestBucket=0B`、`responseBucket=0B`、`statusClass=synthetic_no_network`。
4. 绑定到本 Closure bundle 的 PID `64146`、`64216` 和纠正后重启 PID `64530` 的 `lsof -nP -a -p PID -i` 均为空；第二次请求前后也记录为零 socket。没有真实 Provider 调用、重定向、fallback、重试或其他 authority 的动态证据。
5. 固定 canary 保存后只出现 masked suffix；SQLite 只观察到 AES-256-GCM 元数据及密文长度。删除当前 canary 后，UI 返回“密钥材料不存在；已在网络前拒绝。”；socket 仍为零，credential、derivation、feedback 计数无意外写入。随后重新保存同一固定 canary，并在最终清理前按当前 synthetic database 的精确 key reference 删除并复核不存在。
6. 两次本地逐项披露均展示三个固定 refs、DeepSeek 目标、`deepseek-synthetic-v1`、预算与取消／移除控件。每次确认仅一次。两条持久化结果均为 `understanding`、`deepseek`／`deepseek-synthetic-v1`、source-ref 元数据长度 66；先后形成一个 `confirmed` 与一个 `invalidated` 终态。
7. 首条结果收到“确认”后，UI 变为 `已确认`；第二条结果收到“纠正”后变为 `已纠正并失效`，Today 解释同步显示“撤回或重算受影响理解”。新的 PID `64530` 重启后仍显示同一 Understanding 终态和该 Today 理由，未重发请求。
8. Health 高风险医疗语义的网络前拒绝、typed 数据分离、最多一个 Focus／空 Today、取消披露、20 IPC、fresh PID/AX/WebView 和三档 target-only 视觉证据继承 Closure-1 有效记录，不被本 Closure 重做或替换。

## AC-01～20 终局矩阵

| AC | 终局 | Closure-2 事实／未满足原因 |
| --- | --- | --- |
| AC-01 | **Unknown** | Closure-1 已复核 20 IPC、handler 与三档 native UI，但完整 P3-144 baseline lineage matrix 未在本独立评审重算；本 Closure 按 checkpoint 未重跑。 |
| AC-02 | **Pass** | 两个 Closure 均有 seal／allowlist；Pilot-7、真实 DB、真实正文、真实凭据、真实 Provider 与真实网络零接触。 |
| AC-03 | **N/A（Phase C）** | 真实 DB before/after 在 Phase B 被明确禁止，不能用合成 SQLite 替代。 |
| AC-04 | **Pass** | 合成 Health Current State、confirmed Durable Memory、Work 三种类型分离；高风险 Health 写前拒绝来自 Closure-1。 |
| AC-05 | **Pass** | 两条结果均持久化为 `understanding`，携带 provider/model/source-ref metadata，没有升级为 Memory 或用户事实。 |
| AC-06 | **Pass** | 纠正后第二条 Understanding 为 `invalidated`，Today 明确撤回或重算受影响理解；已确认的第一条历史仍保留。 |
| AC-07 | **Pass** | Closure-1 已验证跨域单一 Focus 与合法空 Today；本 Closure 重启后仍显示单一 Person-level Today 解释。 |
| AC-08 | **Unknown** | 正向 Work+Health refs 可审计；“某域不需要时不得强行披露”的完整负向 resolver matrix 未执行。 |
| AC-09 | **Unknown** | 动态显示逐项 refs、目标、模型、预算、取消／移除控件；但未实际执行移除后的集合变更断言。 |
| AC-10 | **Unknown** | 两次独立确认、取消、空问题拒绝及重启已见；集合变化和旧确认 token 的完整反例矩阵未执行。 |
| AC-11 | **Pass** | 正好两次合成 confirmed request；receipt 为 `NONE/0B/synthetic_no_network`，所有 live-PID socket 检查为零，未见其他 target。 |
| AC-12 | **Pass** | 两条 typed Understanding 具有 source refs、provider、model、状态，且跨重启可见。 |
| AC-13 | **Unknown** | 已证明受影响 Today／Understanding 的可解释变化；未建立独立无关投影以证明其不变。 |
| AC-14 | **Pass** | 确认／纠正各一次；终态 UI 不再给重复反馈控件，static pending-gate mutation 与 UI/DB 状态共同支持单次消费；纠正保留历史并失效受影响投影。 |
| AC-15 | **Pass** | Closure-1 的高风险 Health 网络前拒绝、零部分写入和零网络记录有效。 |
| AC-16 | **Unknown** | 密文+分离 Keychain、重启、删除／缺失 key 网络前失败均通过；篡改密文反例未执行。 |
| AC-17 | **Pass** | 仅固定合成文本和非内容 metadata 入 Evidence；未读写真实正文或真实凭据。 |
| AC-18 | **Pass** | fresh PID 后 Understanding 的确认／纠正终态、Today 理由与披露状态保持，且无重新发送。 |
| AC-19 | **Unknown** | 一次新隔离 independent review 已实际执行并保留非自指 Manifest；但它尚未达到全 AC Pass，不能称为 Independent Pass 或进入 Phase C。 |
| AC-20 | **Pass（见 P2）** | checkpoint 完整；当前 Closure runtime root、build root、detached candidate worktree 和当前 canary 已 marker-gated／精确清理。 |

## ABF 行级结论

| ABF 行 | 终局 |
| --- | --- |
| M-001 | Unknown：同 AC-01。 |
| M-002 / M-003 / M-004 | Pass：Closure-1 合成 typed state/memory/Today 矩阵。 |
| M-005 / M-006 / M-007 | Unknown：负向 resolver、实际移除集合、旧确认 token 未完整执行。 |
| M-008 / M-009 | Pass：synthetic adapter receipt、typed response/persistence。 |
| M-010 | Unknown：已验证确认与纠正及单次消费链，但未覆盖五类 feedback 的完整矩阵。 |
| M-011 | Pass：Closure-1 Health safety。 |
| M-012 | Unknown：缺失／删除 key fail-closed 已通过，ciphertext tamper 未执行。 |
| M-013 / M-014 | Pass：Closure-1 native chain 加本 Closure response/feedback/correction restart。 |
| M-015 | Pass：precontact seal、review-owned static mutation 与本报告。 |
| M-016 / M-017 / M-018 | N/A（Phase C，仍不得触达 Pilot-7）。 |
| M-019 | Pass（见 P2）：当前两根和当前 canary 精确清理。 |
| M-020 | Pass：本 Closure 输出非自指 Manifest。 |

## P2、清理与不得外推的结论

- **P2-145-IR-C2-001（已披露、可分离）**：当前 Closure-2 canary 的精确 account 已删除并验证缺席；随后按 service 名复核时发现一个不同 opaque account 的同服务 synthetic Keychain item。它不匹配 Closure-2 的数据库 key reference，且无可证明归属，故未盲删。该条目不含真实凭据、不属于已删除的 Closure-2 runtime root，也未参与正 Evidence；它不改变 AC-16 当前 canary 的 delete/missing 事实。其归属与清理必须由 PM 另行界定，不能借本 Closure 扩大删除范围。
- 首次 cleanup 运行因只读 candidate 工作树的目录权限遭 Git 拒绝；该次停止发生在两个 marker 校验之后、任何根删除之前。脚本随后仅给该 exact temp candidate 恢复 owner 写权限，检测到 Git 已 deregister 后以已验证的 exact candidate path 删除，继而验证 runtime/build roots 与 worktree registration 均不存在。
- **不得外推**：本报告不是 Phase C 许可、真实 Provider／真实凭据许可、PM Pass、用户最终采纳、风险关闭、产品冻结、main 合并或 Stage 4 准入。

## 角色检查点与建议

- 独立评审角色：已按 review-owned seal、候选只读、mutation、fresh PID 与非内容动态 Evidence 执行；未修复候选。
- L3 Phase-B 评审关卡：**Blocked**，原因是 7 个 Frozen contract Unknown，而非候选缺陷或环境暂停。
- 需 PM 决策：是否在同一 Closure Cycle 另行授权／安排未覆盖的负向 resolver、集合变化／旧确认、无关投影、ciphertext tamper、完整 lineage 与 feedback action 矩阵；在此之前不得进入 Phase C。
