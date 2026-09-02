# LIFEOS-P3-143 Mandatory Independent Re-review-3

## 评审信息

- 对应任务 ID：LIFEOS-P3-143
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：immutable composite commit `a95a0beb27dc0dac183f8a29da550f43af0d6ce3`；candidate tree digest `e65a9599fd691b01c2dc87a2b468c01980d56bdaf5e8b8d401371f4fa669bad8`（85 paths）
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- 独立评审角色：独立技术架构／AI 信任与安全复评
- 协审视角：数据生命周期、凭据最小披露、root authority、Evidence 可复算性
- 评审关卡：Mandatory Independent Re-review-3
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-143/independent-re-review-3/`
- 评审结论：**Invalidated — New Isolated Re-review Required**
- 风险等级：L3
- 独立评审触发事实：L3 凭据／网络／安全边界，以及 r1 `IR-RR1-P0-001` 修复后的全新隔离复评

## 独立性与回流规则

- 执行侧与评审侧是否隔离：Yes。目录在任何候选、Engineering Evidence 或历史 Review 接触前新建。
- 是否只评审最终 Evidence／hash：Yes。固定输入、candidate、工程和历史均只读；候选代码未修改。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留：Yes；保留于 `review_tools/`、`review_runtime_harness/`、逐项矩阵和本轮 Evidence。
- 是否可验证 runner 未导入或调用 candidate verifier：Yes。runner 只编译 candidate 原始 `runtime.rs`；Manifest、静态合同和 mutation 检查均为 review-owned。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented 或 Evidence 冲突：候选 P0=0、P1=0、P2=0；评审程序 P0=1（`IR-RR3-P0-001`）；技术 GUI Unknown=0、Not Implemented=0，但其正 Evidence 已不可用于本轮结论。
- 若需整改：未复现 Frozen Task Contract 候选缺陷，故不发起候选 Rework；必须由 PM 发起全新隔离复评。
- 更新时间：2026-09-02（native 取证完成后发现 sealed single-root 程序 P0）

## 评审摘要

1. 所有预接触控制先写入并 hash；完整精确输入和十项 Freeze Manifest hash 均通过后才接触候选。
2. `a95a0beb`、P3-143 Engineering Final Manifest 126/126、P3-142 Manifest 以及 original/r1/r2 三份 review Manifest 都由 review-owned verifier 零错误复算；candidate 85 个文件与 immutable Git blob 一致。
3. Cloud 8／Local 4、ordered exact 20 IPC、凭据—测试—选模型—启用—canary 动作分离、DeepSeek exact authority 和 no-proxy/no-redirect 静态合同通过；四个反例 mutation 均被独立检测。
4. review-owned Rust harness 编译实际 candidate `runtime.rs`，以封存的 root 覆盖 root absent、marker、runtime、DB、root shape、run-id 和环境注入矩阵；全部通过，且每个拒绝路径保持 sentinel/DB/filesystem 不变。
5. 修正 raw executable 识别方式后，fresh source-built `.app` 的 direct PID `99755` 被绑定到 exact-title AXWindow 和 AXWebArea；desktop、1160×768 compact 与700×760 narrow 的 target-only screenshots 都由同一 PID 与同一 CG window id 取得。
6. 该修正 bundle 编译为 `bundleui-20260902` 并创建第二个 review root，违反封存 test design／binding 所要求的唯一 `rereview3-20260902` root。这是 `IR-RR3-P0-001`；技术成功结果不得充当本轮独立正 Evidence。
7. PID 已停止；两条已知 review root 均经 marker-gated cleanup 后确认不存在。候选未修改、禁止边界零接触，但稍后清理不能恢复本轮独立性。

## 已通过内容

- 以下仅为已保全的技术观察，不能构成本轮 Independent Pass：r1 missing-marker 修复的 fail-closed 动态反例、目录/IPC/action/authority/root-authority 静态与合成检查，以及 native PID/AX/截图链。
- 当前 Final Manifest、P3-142 baseline 和指定历史 Review 的非自指 hash/lineage 仍可复算；它们不消除 `IR-RR3-P0-001`。

## 关键问题

- `IR-RR3-P0-001`：封存测试设计与 `runtime_root_binding.md` 限制本次只有一条 literal root。native 修正过程创建了第二条 candidate-derived root。其完整事实、containment 和不得用后续删除补救的原因见 `p0_procedural_invalidation.md`。

## Closure List

1. 不得恢复本 attempt，也不得将其技术 Evidence 转写为 Independent Pass。
2. PM 如仍需结论，应新建全新隔离的 independent re-review：新 output root、test design、allowlist、prohibited declaration、precontact seal 和单一 compile-derived runtime root 都必须在 candidate contact 前完成。
3. 新评审必须重取自己的 native PID→exact-title AXWindow→AXWebView/Area→target-only screenshot 链，并独立完成其 cleanup/Manifest；不得复用 PID `99755` 或本包正 Evidence。

## 条件通过项

无。本轮不是 Pass with Conditions，也不是候选 Rework；它是程序 P0 失效记录。

## 关卡检查

- Gate 1 产品一致性评审：Invalidated — technical native chain captured but cannot form an independent conclusion.
- Gate 2 数据与来源评审：Containment Pass only — no personal data, real DB, retained root, Provider or network target contacted.
- Gate 3 AI 权限与信任评审：Invalidated — offline technical observations cannot close the review after P0.
- Gate 4 技术可行性评审：Invalidated — static/root/native technical observations are non-positive after P0.
- Gate 5 用户价值验证：N/A — 本轮不验证用户价值或 Stage 4。

## 风险

- 无新增风险关闭结论。R-0055／R-0056 继续 Open。
- `PHASE_A_PRE_REAL_GATE_MANIFEST.json` 是保留历史；其 113 条源值没有声明可复算的 immutable Git snapshot，且与修复后的当前 candidate 不同，因此本 review 不将它作为当前正 Evidence。

## 需要 PM 决策

需要 PM 决定是否创建新的全新隔离 independent re-review。此不是产品、风险关闭、真实凭据、Provider 或网络授权；本包不得继续恢复。

## 最终建议

记录 **Invalidated — New Isolated Re-review Required**。没有复现 Frozen Task Contract 候选缺陷，因此不能给候选 Rework；同样不能将本包写为 Independent Pass、PM Accepted、产品 Frozen、风险关闭、Phase C 或 Stage 4。
