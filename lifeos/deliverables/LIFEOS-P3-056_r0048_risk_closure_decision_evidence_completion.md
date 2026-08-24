# LIFEOS-P3-056｜R-0048 风险关闭决策 Evidence 补全

## 结论与权限边界

**建议：在下述严格受控边界内建议关闭 R-0048；本任务不关闭风险。**

这是对 P3-055 被 PM 标记为 Rework 的程序性 Evidence 缺口的独立补全，不是把 P3-055 草案直接当作证据。本任务已建立专属独立 Review、47 项输入的 SHA-256 前置登记、历史材料交叉核对与只读 after 核验入口。实际模型路由为 `gpt-5.6-terra` + `xhigh`；D-0251、当前任务卡和 `CURRENT_STATUS.md` 均记录本会话是与 P3-053/P3-054/P3-055 分离的新会话。

最终关闭仍必须由 PM 验收并取得用户明确授权。本任务没有修改工程、历史 Review/Evidence、任何项目账本、R-0048、R-0049、冻结状态、工程基线或阶段状态。

## 已验证事实

1. **P3-045 合同。** 已验收的方案 B 将 DB lifecycle 不变量、原子 evidence、generation/time 约束与应用层真实 actor/确认/编排分开。真实身份不是、也不能被本建议证明。
2. **P3-052 反证完整保留。** 独立结果显示 152 PASS / 32 BYPASS / 0 FAIL / 0 UNKNOWN；其中 16 个 P1 与 16 个 P2 bypass 分别对应两类 Outbox 与两类初始 lifecycle 缺口。184 项完整性检查均无异常，故“文件完整”不能被错误当成“合同已通过”。
3. **P3-053 窄整改成立。** 对同一问题域的当前候选回归为 74 PASS / 0 FAIL / 0 Not Implemented，八配置矩阵为 88 PASS / 0 FAIL；当前 SQL 和 runner hash 分别为 `bda3…9b1` 与 `45d1…224a`，与 P3-053 PM Evidence 一致。
4. **P3-054 新隔离独立 Pass 与 PM Evidence 一致。** 自建 10 个逻辑用例在 8 配置为 80 PASS / 0 FAIL / 0 Unknown / 0 Not Implemented，P0/P1/明确 P2 bypass 均 0；40 个文件型合成库完整性无异常；P3-031 隔离回归 74 PASS、八配置 88 PASS；P3-052/P3-053 的 37 项历史只读资产 before/after 相同。
5. **P3-055 的返工原因已被准确限定。** PM Review 表明其范围、非范围与重开条件本身审慎，但它缺少专属 Review/Manifest、输入 hash、保留与预检记录；并非发现了新的技术 bypass。
6. **本任务的新证据链。** `lifeos/reviews/LIFEOS-P3-056/evidence/MANIFEST.md` 和 `input_hashes_before.sha256` 记录了本轮 47 项完整输入与 individual SHA-256；没有把历史结论替代为本任务事实。

## 合理推断

P3-052 发现的四项可复现缺口先被隔离记录，再由 P3-053 只针对该四项整改，最后由 P3-054 的新隔离自建攻击和 PM 隔离复跑验证。当前候选 hash、历史 preservation 以及本任务独立的输入登记均一致。因此，在下述有限受控边界内，已没有证据要求仅因已知 lifecycle/Outbox/generation/time 结构性缺口而继续维持 R-0048 为 Open。

此为有限推断，不把孤立的 AuditEntry、Outbox、lifecycle command、actor claim 或运行态字段解释为真实用户授权、真实身份或生产可用性。

## 建议关闭的严格适用范围

- 当前 SHA-256 为 `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` 的候选 SQL及其当前 P3-031 直接合同 runner；
- 合成 memory/file SQLite，`foreign_keys` 与 `recursive_triggers` 各 ON/OFF 的八配置；
- P3-045 合同、P3-052 失败、P3-053 整改、P3-054 独立复评/PM Evidence，以及 P3-056 本任务 Manifest 登记的当前输入；
- 有限 Stage 3、单用户、单设备、本地受控验证边界。

## 明确非范围

真实 actor/用户确认/进程身份，真实 DB/migration 或非空库升级，WAL/多 writer 并发、多进程 worker、崩溃/断电/备份恢复、跨平台、真实 retention 运维权限、真实 Vault/Tauri/IPC/文件、云或第三方模型、同步/多设备、L3、外部用户、生产 SLA，均不在本建议内。

R-0049 不在本任务范围，继续保持 **Closed / Limited Controlled Boundary**；本任务不触发其重开条件。建议关闭 R-0048 也不意味着冻结 Schema/API、候选 SQL 或工程基线，更不意味着进入下一阶段。

## 反证、重开与阻断条件

任一条件成立，应保持/重新打开 R-0048 或建立等价风险，而不是依赖本建议：

1. 本任务前后 47 项输入有任一 hash 不一致、缺失、被重写，或 P3-054/本任务的会话隔离、Evidence 保留失效；
2. 候选 SQL、lifecycle/Submission/Audit/Outbox/retention trigger、P3-031 合同 runner 或 P3-054 主 Evidence 有实质变更；
3. 出现可提交的伪造、预置或重放 lifecycle 组合，或可绕过 provenance、lease CAS、retention fence、generation/time 或原子回滚；
4. 任一消费、审计展示或后续实现将孤立 AuditEntry、Outbox、lifecycle command 或 actor claim 作为真实用户授权/真实操作证明；
5. 出现 P0/P1、明确 P2 bypass、Not Implemented、Unknown、不可复现的测试冲突，或范围扩展到任一上述非范围（尤其真实 actor、真实 DB、并发、恢复或真实能力）。

## 角色、关卡与建议状态

- 主责角色：独立 QA / Evidence Reviewer。
- 协审视角：技术架构、数据/领域模型、AI 信任与安全。
- Gate 2、Gate 3、Gate 4：在候选 SQL + 合成 SQLite 的严格范围内 **Pass with Conditions**；Gate 1、Gate 5 不适用。
- 任务建议状态：after hash 已对 47/47 输入验证为 `OK`，预检已按允许跳过规则记录；P3-056 可供 PM 验收为 **Evidence-complete / Pass with Conditions**。
- 风险建议状态：**R-0048 建议关闭**，但在 PM 和用户明确行动前它仍是 **Open / Remediation Candidate**。

## 需要 PM 决策

1. 审阅本任务的 after hash 和本地预检记录后，是否验收 P3-056 的 Evidence 补全。
2. 若验收，是否将本“建议关闭”的有限范围、非范围与重开条件提交用户作最终关闭授权。

PM 即使接受本建议，也不得在没有用户明确授权时关闭 R-0048；不得改变 R-0049、冻结资产、恢复工程基线、启用真实能力或进入下一阶段。

## Evidence 与本地预检

- Evidence Manifest：`lifeos/reviews/LIFEOS-P3-056/evidence/MANIFEST.md`
- 输入前置 hash：`lifeos/reviews/LIFEOS-P3-056/evidence/input_hashes_before.sha256`
- 输入后置 hash：`lifeos/reviews/LIFEOS-P3-056/evidence/input_hashes_after.sha256`（与前置清单逐字节一致；47/47 `OK`）
- 独立 Review：`lifeos/reviews/LIFEOS-P3-056/independent_review.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-056_LIFEOS-P3-056_r0048_risk_closure_decision_evidence_completion_local_precheck.md`（Skipped / Local Model Unavailable；`Operation not permitted`，已按规则记录）。
