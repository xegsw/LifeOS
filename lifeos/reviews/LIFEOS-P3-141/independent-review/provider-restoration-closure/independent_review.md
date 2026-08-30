# LIFEOS-P3-141 Provider Restoration Closure — 独立评审

## 评审信息

- 对应任务 ID：LIFEOS-P3-141 Provider Restoration Closure
- 风险等级：L3；Mandatory Independent Review
- 评审关卡：ABF-P3-141-v2，ABF2-M-001～009
- 被评审候选：current worktree `48a26320646219117b28e81cd77dd6c8206fe99c` 的 `lifeos/engineering/LIFEOS-P3-141/closure-provider-restoration/candidate/`
- 工程来源声明：`5e9b5160`；本评审未采信工程结论，并从当前 HEAD 自行复算候选身份。
- 评审路径：本目录
- 评审结论：**Rework — P0 fail closed**
- 独立性：新隔离会话；评审自写 test design、write allowlist、precontact seal 与检查器。未复用工程 runner、fixture、PID、截图、结论或正 Evidence。

## 结论摘要

- **P0：Phase-C 授权链仍硬绑定已撤回的 `ABF-P3-141-v1`。** 当前候选 `build.rs` 将 `phase_c_real` 的 receipt validator 同时要求 `receipt.abf_id == ABF_ID` 与 v1 hash；Revision 2 已冻结 v2 并明确 v1 不能再用于正向验收。因此，即使本轮取得 v2 独立 Pass，候选也不能把它作为 Phase-C 授权。
- 本评审自有检查器直接复算该事实，见 `evidence/p0_revision2_phase_gate.json`。这是 `ABF2-M-008 / CL-PROV-06` 的 P0，不是工程报告可用旧 Phase-B receipt 代替的文档问题。
- P0 出现在临时根、合成 DB、loopback、candidate copy/build、mutation 和 actual-Tauri 启动之前；因此这些正向动态步骤均未执行，避免把不完整的证据误读为 Pass。
- 只读静态复算仍确认：Revision-2 固定输入 7/7 一致；P3-140 Candidate Manifest 79/79 一致；当前候选与工程 Manifest 79/79 一致；五 profile／五 Adapter／mode mapping 与 DeepSeek/Kimi/Custom 标签逐行一致；IPC 恰好 20。此类静态事实不抵消 P0，也不构成动态验收。
- 原 attempt-8 的 `ABF-P3-141-v1` receipt 与 Phase-B Pass 已按 Revision 2 作为只读、已 supersede 的历史保留，未被复用为本轮结论。

## 独立性与边界

- 预接触封存：`test_design.md`、`write_allowlist.txt`、`precontact_seal.json` 的 SHA-256 已在 `precontact_hashes.txt` 固定。
- 禁止路径与真实／外部边界零触达，见 `evidence/prohibited_target_attestation.json`。
- `/private/tmp/lifeos-p3-141-provider-restoration-independent-review-v1` 在 P0 前未创建；因此没有清理动作，见 `evidence/cleanup_receipt.json`。这不是 ABF2-M-009 的 Pass。
- 未修改候选、工程目录、PM 账本或历史资产；未进入 Phase C。

## 逐行矩阵与五类计数

完整矩阵见 `ABF2_MATRIX.md`。

- P0：1
- P1：0
- P2：0
- Unknown：0
- Not Implemented：6（M-001～005、M-009 在 P0 后未执行）

## 关键问题与 Closure 建议

工程必须在同一 P3-141 Closure 内修正候选的 Phase-C build/receipt authorization binding，使它只接受与 `ABF-P3-141-v2`、Revision-2 candidate identity和新的独立 Manifest相绑定的收据；不得接受已撤回 v1 的 `attempt-8` receipt，也不得为兼容性引入绕过、fallback、额外 IPC、真实 Provider 或网络。

修正后必须由**新的隔离独立评审会话**重新从预接触封存开始，独立执行完整 review-owned loopback 正反例、20 IPC／非 Provider 回归、四类候选语义 mutation、synthetic DB 与 desktop/compact/narrow actual-Tauri PID→AXWindow→AXWebView/WebArea 绑定、非自指 Manifest 与 marker-gated cleanup。当前失败评审不得转为正向 Evidence。

## 关卡检查

- Gate 1 产品一致性：未通过（Phase-C 新授权链与 Revision 2 冻结冲突）。
- Gate 2 数据与来源：部分静态通过；P0 后未完成完整动态闭环。
- Gate 3 AI 权限与信任：未通过（撤回的 v1 receipt 仍可作为唯一 Phase-C 绑定）。
- Gate 4 技术可行性：未通过（完整动态和 actual-Tauri 证据按 fail-closed 未启动）。
- Gate 5 用户价值验证：不适用／未进入真实 Pilot。

## 最终边界

本结论只覆盖 Provider Restoration 合成 Closure 的独立失败发现；不构成 Phase C、真实 Provider、风险关闭、产品冻结、Stage 4 或任何真实数据处理结论。
