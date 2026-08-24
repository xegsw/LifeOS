# LIFEOS-P3-056｜R-0048 风险决策 Evidence Manifest

## 任务与受控边界

- 任务：`LIFEOS-P3-056`，全新隔离的 R-0048 风险关闭决策 Evidence 补全；实际路由为 `gpt-5.6-terra` + `xhigh`，无降级或后备模型。
- 派发与隔离事实：任务卡、`CURRENT_STATUS.md` 与 D-0251 均记录本任务使用新会话 `01a02251-614d-7c00-ac79-62f1261e97c8`，且与 P3-053/P3-054/P3-055 分离。本核验不把任何旧会话的结论当作本任务自身证据；它们仅作为已散列的历史输入。
- 写入范围：仅本任务的 deliverable、`lifeos/reviews/LIFEOS-P3-056/` 和本任务 local-precheck 报告。工程、历史 Review/Evidence 与所有 PM 账本均只读。
- 不执行：真实数据/凭据、真实 DB/migration、网络、外部目标、真实 Tauri/IPC/Vault/文件、云/第三方模型、并发、多进程、备份/恢复或真实能力。

## 完整输入清单与前置散列

前置快照文件：`input_hashes_before.sha256`。它逐项列出本轮实际读取或用于核对的 **47** 个输入及 SHA-256；hash 由 `shasum -a 256` 对工作区相对路径生成。输入分组如下，完整的“路径—SHA-256”登记以该快照为准，不以叙述性引用替代。

| 组别 | 数量 | 覆盖内容 |
|---|---:|---|
| 项目规则、模板、任务与账本 | 13 | `AGENTS.md`、状态/分派/治理/角色/关卡、两份模板、P3-056 任务卡、风险/任务/决策/冻结账本 |
| P3-045 合同 | 3 | 任务卡、合同交付物、PM Review |
| P3-052 失败 | 8 | 任务、交付物、独立 Review、两个 Manifest、PM Review、主结果与完整性 JSON |
| P3-053 整改 | 7 | 任务、交付物、工程/PM Manifest、PM Review、P3-031 回归与八配置 JSON |
| P3-054 隔离 Pass | 11 | 任务、交付物、独立 Review、两个 Manifest、PM Review、独立结果、回归摘要、完整性和 preservation before/after JSON |
| P3-055 草案/Rework | 3 | 任务、交付物、PM Review |
| 当前候选实施核对 | 2 | `001_candidate_schema.sql` 与 `run_contract_tests.py` |

关键 hash 交叉核对：当前候选 SQL 为 `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`，与 P3-053 PM Evidence 和 P3-054 Evidence Manifest 一致；当前 runner 为 `45d19e56fc3aaf75ccd12c5de678dec770c425fec9e8d570e3783f4a7bb8224a`，与 P3-053 PM Evidence 一致。P3-054 的独立结果、完整性结果和其 before/after 记录的实际散列也分别与其 Manifest 相符。

## 独立核对记录

| 输入链 | 已核对的事实 | 本任务判断 |
|---|---|---|
| P3-045 合同 | 方案 B 要求 DB 原子约束 lifecycle、AuditEntry/Outbox 证据及 generation/time；真实 actor/用户确认仍由应用层负责，不能由 DB 字段替代。 | 是 R-0048 技术关闭范围的边界来源，不是对真实身份的证明。 |
| P3-052 失败 | 结构化主结果为 152 PASS / 32 BYPASS / 0 FAIL / 0 UNKNOWN；16 个 P1 与 16 个 P2 bypass；184 个完整性记录无异常。 | 2 个 Outbox P1 与 2 个 initial-value P2 是有效的历史反证，不能被省略。 |
| P3-053 整改 | 当前候选回归为 74 PASS / 0 FAIL / 0 Not Implemented，八配置为 88 PASS / 0 FAIL；其结果散列与工程/PM Manifest 一致。 | 为 P3-052 四项缺口提供窄范围整改证据，尚不能单独构成关闭。 |
| P3-054 独立 Pass 与 PM Evidence | 自建 10 个逻辑用例 × 8 配置为 80 PASS / 0 FAIL / 0 Unknown / 0 Not Implemented，P0/P1/明确 P2 bypass 均 0；40 个文件型合成库完整性无异常；P3-031 回归 74 PASS，八配置 88 PASS；P3-054 自身 37 项历史只读资产 before/after 字节一致。 | 这是本建议的独立技术主证据；只证明候选 SQL + 合成 SQLite 的受控范围。 |
| P3-055 Rework | PM 明确承认其范围、非范围与重开条件审慎，但拒绝其进入用户关闭授权，因为缺少该任务自身 Review、Manifest、输入 hash、preservation 与预检记录。 | P3-055 仅是被审查的草案；P3-056 以独立输入快照、Review 和 Manifest 补齐该程序性缺口。 |

## 本轮只读保留

- 前置登记：`input_hashes_before.sha256`（47 项）。
- 后置登记：`input_hashes_after.sha256`。对 `input_hashes_before.sha256` 执行 `shasum -a 256 -c`，47/47 项均为 `OK`；after 与 before 逐字节相同。
- 判定规则：任一输入 hash 变化、缺失或两份登记不一致，本任务的建议即降为 **Blocked**，不得进入 PM 风险关闭讨论。

## 本地预检

- 命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-056_r0048_risk_closure_decision_evidence_completion.md`。
- 报告：`lifeos/local_prechecks/LIFEOS-P3-056_LIFEOS-P3-056_r0048_risk_closure_decision_evidence_completion_local_precheck.md`。
- 状态：`Skipped / Local Model Unavailable`；脚本生成报告，但对本地模型请求返回 `Operation not permitted`。这是项目规则允许的跳过情形，不阻断人工核验。
- 规则：预检只能检查模板/措辞/风险提示；不能决定风险关闭、PM 验收、冻结或阶段推进。

## 明确不产生的状态变化

本 Manifest 不关闭 R-0048、不重新打开或修改 R-0049、不修改 PM 账本、不冻结任何资产、不恢复工程基线、不启用真实能力，也不进入下一阶段。
