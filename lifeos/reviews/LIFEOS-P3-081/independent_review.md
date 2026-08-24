# LIFEOS-P3-081｜Stage 3 整合能力收口与 Stage 4 候选就绪独立复核

## 评审信息

- 对应任务 ID：LIFEOS-P3-081
- 是否为受控能力包：No（阶段治理／证据复核）
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-081_stage3_integrated_capability_closure_and_stage4_candidate_readiness_review.md`
- 独立评审角色：阶段治理／产品架构
- 协审视角：AI 信任与安全、数据／领域模型、技术架构、用户价值
- 评审关卡：Stage 3→4；Gate 1／3／4／5 证据就绪度
- 独立评审路径：新隔离只读会话
- 评审结论：**Blocked**

## 评审摘要

- P3-063–080 的最终 PM／独立 Review、任务登记、冻结与风险叙述一致：各能力只在合成、单进程、task-local SQLite／临时目录等受控范围内被采纳，均 Not Frozen，Stage 4 未准入。
- P3-079 Rework 的当前源码和五项 PM Evidence hash、P3-080 独立 runner／结果／快照／日志与当前源码 hash 均一致。
- P3-080 PM Evidence Manifest 的自指 hash 当前不一致：记录 `4114715c…a0b98e`，实际 `61fea805…8c6a2a`。该记录的 P3-080 独立 Evidence Manifest hash 本身是正确的。
- 因任务卡将任何 Evidence 冲突列为 Rework 或 Blocked 条件，且本会话无权更改历史 PM Evidence，整体复核为 Blocked。

## 已通过内容

- 五项 Stage 4 硬门槛均已明确为“真实能力 Evidence 缺失”，未将合成 CLI／SQLite／沙盒通过表述为真实能力通过。
- P3-079／080 整合闭环、P3-070–073 导出沙盒、P3-074 使用说明、P3-067／069 恢复和 P3-077／078 权限设置的可证明范围与不可外推范围均可追溯。
- R-0013、R-0014、R-0015、R-0019、R-0021 保持 Open，R-0040 保持 Open / Conditional；无风险、冻结或基线状态被误写。

## 关键问题

P3-080 PM Evidence Manifest 自身 SHA-256 不一致，造成当前 Evidence 完整性冲突。此问题不证明运行时漏洞，却阻断“全部 Evidence/Manifest 一致”的本任务验收项。

## 必须整改项

PM 必须在不覆盖历史 Evidence 的前提下决定并记录该 Manifest 冲突的可复查处置；处置完成后才可重新进行本阶段复核。不得将 P3-080 的独立 Pass 或本报告用作 Stage 4 准入。

## 条件通过项

无。P0=0，P1=1，P2=0，Unknown=0，Not Implemented=0，因此不适用 Pass with Conditions。

## 关卡检查

- Gate 1 产品一致性评审：定义与有限闭环输入齐备；真实 MVP 体验 Evidence 缺失，未通过 Stage 4 Gate。
- Gate 2 数据与来源评审：受控来源／状态／审计 Evidence 可用；真实导出与恢复链未验证。
- Gate 3 AI 权限与信任评审：受控 fail-closed 输入可用；真实权限设置与真实处理链未验证，未通过 Stage 4 Gate。
- Gate 4 技术可行性评审：受控 CLI／SQLite Evidence 可用；真实耐久、Tauri／IPC、path scope、文件与恢复未验证，R-0040 继续阻断。
- Gate 5 用户价值验证评审：未通过；没有 Alpha 用户真实使用或价值／反证 Evidence。

## 风险

不新增、不关闭或重开风险。P3-080 PM Evidence Manifest 冲突需要 PM 关注，但本会话不修改 `RISK_LOG.md`。

## 需要 PM 决策

决定如何在保留历史资产的前提下处理 P3-080 PM Evidence Manifest 的 hash 冲突。完成前，唯一安全方向是保持有限 Stage 3。

## 最终建议

保持 Blocked；不进入 Stage 4，不授权真实能力，不冻结、不恢复基线。冲突处理后，重新做一次只读阶段治理复核，再由用户在“维持有限 Stage 3”与“单独授权首项真实能力前置验证”之间作唯一重大选择。
