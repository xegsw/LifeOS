# LIFEOS-P3-058｜R-0043 风险关闭决策评估

## 1. 决策摘要

**建议：Blocked；不得关闭 R-0043，维持 `Reopened / Closure Candidate`。**

这不是对 P3-037 至 P3-039 历史结论的否定：P3-037 已结构化记录 3 个 P1 失败；P3-038 已整改；P3-039 的隔离独立反例确认其中 Tombstone 的 14 项 P2-2/P2-3 攻击均 fail closed。阻塞原因是当前候选 SQL / 合同测试已在 P3-039 后实质演进，而 P3-031 的当前主 Evidence Manifest 与 `test_results.json` 仍指向早期 hash 和 70 项快照，不能为当前候选提供一致、可追溯的关闭证据。任务卡规定任何 hash/Evidence 冲突均不得建议关闭。

本文件仅为 PM 与用户的风险决策输入；不关闭、不重开任何风险，不冻结任何资产，也不代表真实能力、生产 migration 或下一阶段准入。

## 2. 已验证事实

1. P3-037 的结构化 `test_results.json` 为 7 PASS / 3 FAIL；三个 FAIL 都是 P1：Tombstone 可 DELETE / REPLACE / 降代重插、可伪造非 `accepted` 初态，以及 active Authorization 子表可 DELETE 而无 generation/audit fencing。D-0209 据此重新打开 R-0043。
2. P3-038 的结构化文件型回归为 12 PASS / 0 FAIL / 0 Unknown / 0 Not Implemented；P3-031 当时为 38 PASS。其 P2-2/P2-3 证据显示 DELETE、REPLACE、DELETE+INSERT 和四种非法初态均被 DB 层 trigger 拒绝。
3. P3-039 是与 P3-038 执行会话隔离的独立复评。其 `counter_example_results.json` 共 29 项：P2-2 为 6/6 PASS、P2-3 为 8/8 PASS、P2-4 为 4/4 PASS；其余 11 个 P1 是 active Authorization 子表 INSERT/UPDATE/REPLACE/改绑旁路，PM 已归入 R-0044/R-0046 路线，而不是 Tombstone 的 R-0043 面。
4. P3-039 评审快照的 SQL / tests / shell hash 分别为 `008cd328…c4cf2`、`246f3675…39da`、`611a2714…6230d`。当前对应源为 `bda3e8db…9b1`、`45d19e56…224a`、`611a2714…6230d`：SQL 与 tests 已演进，shell 未变。
5. 当前 SQL 仍保留并扩展了 R-0043 的 DB 约束：Tombstone 仅能以 `accepted` 创建、同一 subject 不可 reinsert、直接 DELETE 被拒绝、generation 不可降低、状态机维持单向。复制到系统临时目录的当前 P3-031 入口复跑退出码为 0，得到 74 PASS / 0 FAIL / 0 Not Implemented（P0=18、P1=29、P2=27）；未写入原工程目录。
6. 但当前 `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md` 仍将源 SQL/tests 写为 `56f3c77f…ac6d` / `6729d48e…b3b5`，并将 `test_results.json` 写为 70 PASS（P1=27、P2=25）。实际当前源 hash 与当前历史结果快照均不相符。这是当前主 Evidence 的 hash/输入/结果冲突。

## 3. 判断

- **R-0043 的历史整改事实仍成立：** 当前证据没有显示 P3-037 的 DELETE/REPLACE/非法初态旁路被恢复；当前 SQL 的相关限制仍存在，临时副本的当前合同入口亦通过。
- **但历史 Pass 不会自动延续到当前候选：** P3-039 只对 hash `008cd328…c4cf2` 的快照形成独立结论。当前 SQL 与合同 tests 已变更，且 P3-031 主 Manifest/结果未和当前输入同步，无法把 P3-039 的结论无条件映射到 `bda3e8db…9b1`。
- **结论为 Blocked 而非“建议关闭”：** 这是证据完整性与候选身份冲突，不是已确认的新 Tombstone P1。按任务卡的硬停止条件，在未有一致的当前结构化证据、独立性与 PM Evidence 前，不能把正向复跑替代为关闭依据。

## 4. 严格范围、非范围与条件

若 PM 后续解除阻塞并再次评估，候选范围只能是：当前 hash `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` 的候选 SQL、与之匹配的 `45d19e56…224a` 合同 tests、未变 runner `611a2714…6230d`、合成 SQLite、单进程、本地受控的有限 Stage 3 边界；不包含真实 DB / 非空 upgrade、并发/WAL/恢复、真实 Vault/文件、Tauri/IPC、网络/云、外部用户或任何生产 SLA。

非范围：R-0040、R-0044、R-0045、R-0046、R-0047、R-0048、R-0049、R-0050 的状态和关闭依据；Schema/API/工程基线冻结；真实能力启用；阶段推进。本任务不因 P3-039 的 11 个 Authorization P1 而改变其他风险状态。

解除 Blocked 的最低条件是：以当前 SQL/tests/runner 重新建立一致的结构化 P3-031 Evidence（输入 hash、准确命令、退出码、逐项统计、before/after 保留）；明确将 CT-P1-10/11 的 Tombstone 覆盖和当前候选绑定；由与相关工程整改隔离的评审复核该证据；再由 PM 和用户分别验收、决定。任何新 P0/P1、明确 P2 bypass、Unknown、Not Implemented、hash/Evidence 冲突、独立性不足，或上述三项输入的实质变化，均保持/重新进入 Open 或 Blocked，不能沿用本评估关闭。

## 5. 角色与关卡

- 主责（独立 QA / Evidence Reviewer）：**已完成**历史失败、整改、独立反例、PM Evidence、输入 hash 与只读隔离核对。
- 协审（技术架构、数据/领域模型、AI 信任与安全）：确认 Tombstone 删除不复活和候选身份/证据可追溯均是关闭前提；Authorization 的其他风险未被混同。
- Gate 2、Gate 3、Gate 4：**不通过风险关闭关卡 / Blocked**，唯一阻塞项为当前候选的主 Evidence hash/结果不一致；不是冻结、开发准入或其他风险的裁决。

## 6. Evidence 与本地预检

- 任务专属清单、before/after SHA-256、隔离声明及临时副本复跑摘要：[MANIFEST.md](../reviews/LIFEOS-P3-058/evidence/MANIFEST.md)
- 独立评审记录：[independent_review.md](../reviews/LIFEOS-P3-058/independent_review.md)
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-058_independent_review_local_precheck.md`；本地模型不可用，按项目规则跳过，不影响以上人工核验。
