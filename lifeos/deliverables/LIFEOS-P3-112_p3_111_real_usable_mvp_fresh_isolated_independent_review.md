# LIFEOS-P3-112｜P3-111 可真实使用 MVP 全新隔离独立复评交付物

## 任务信息

- 任务 ID：`LIFEOS-P3-112`
- 任务类型：P0、全新隔离、只读工程／安全／数据生命周期／体验／Evidence 独立复评。
- 当前状态：**Rework 1 独立 Pass，待 PM 验收**。
- 正式 Rework：1/2；本次为 PM 已调整、用户已采纳的同任务 Rework。
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review_acceptance_basis_freeze.md`
- ABF：`ABF-P3-112-v1`，SHA-256 `780ffb07c8f1bd4948ae568771f7b5c334d7fd7bcc2de925a38edcf95e9f78bf`；启动前已复算为 Frozen。
- 执行授权：用户在本会话投递 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review.md`，接收时间 2026-08-24 Asia/Shanghai。
- 会话与模型：全新 Codex 独立评审会话；任务卡配置 `gpt-5.6-terra + xhigh`，无降级。

## 初次 Blocked 的事实摘要（历史）

1. 独立设计先行。`evidence/test_design.md` 于读取 P3-111 语义 verifier、mutation runner 及其结果之前创建，随后以 SHA-256 `8b36b61cc891ae3a803ffa52def84c113a2283425e7a59948951a35338346aa9` 固定；读序和会话边界另有独立记录。
2. 冻结身份成立。P3-111 任务卡、ABF、两份交付物、candidate provenance、gap matrix、两份 Engineering Manifest、PM Review、Rework PM Evidence Manifest、提交 verifier 和 mutation runner 共 12 项 SHA-256 全部匹配；candidate 的 72-file tree hash 为 Frozen 值 `cc1ff0f05d5d3993c8b113dae80a043b3d7f535a05a8236771b980a4892718a3`。
3. 唯一临时根在启动时不存在。任务在其中完成正向 candidate copy；复制后有 72 个普通文件，源／副本 `diff -r -q` 无差异，未复制 P3-111 的历史 Evidence、tools、tests 或 target。
4. 固定工具门失败。独立 runner 即将执行 `cargo test --locked --offline` 时获得 `FileNotFoundError: cargo`；之后单独检查也确认 `cargo` 和 `rustc` 均不在本会话可用路径。因此 8 个固定非敏感 tests、offline locked build、独立 static／dynamic audit、自有 raw verifier、unchanged control、六类 mutation 和 submitted-verifier cross-check 都没有执行。
5. 为保持失败关闭，没有安装 Rust、没有联网、没有启动 Tauri app、没有换模型或调用真实路径。Pilot-2 路径查找、metadata、打开、读取、hash、复制、覆盖和清理均为 0；P3-111 和项目账本写入均为 0。
6. 临时根只含本任务产生的 candidate copy（清理前 780 KiB）；已精确删除 `/private/tmp/lifeos-p3-112-review-v1` 并验证不存在。

## 初次 Blocked 的 Frozen 矩阵与计数（历史）

| 范围 | 结果 |
|---|---|
| M-001 授权／模型／隔离／ABF | Pass |
| M-002 独立设计与读序 | Pass |
| M-003 固定输入与 candidate identity | Pass（12/12；72 文件） |
| M-004 正向 allowlist copy | Pass |
| M-005 offline locked test/build／8 tests | Not Implemented / **Blocked** |
| M-006～M-013 | Not Implemented；未用现有 P3-111 或 PM Evidence 代替本任务独立执行 |
| M-014 清理 | Pass（退出范围；不宣称 Review Pass Manifest） |
| M-015 风险／冻结／阶段边界 | Pass |

计数：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=9。

这些计数不表示 P3-111 candidate 已通过或失败：本次外部工具阻断使其质量保持 **未评估**。尤其不能把 P3-111 PM Pass、初次 37/37、Rework 38/38、提交 verifier、历史 unchanged control 或 mutation 结果直接转写成 P3-112 Pass。

## 初次 Blocked 的角色与关卡（历史）

- 主责：独立 QA／安全与数据生命周期评审。
- 协审：产品体验、可访问性、技术架构、数据与来源、AI 信任安全。
- Gate 1：范围没有扩大；但本任务 Blocked，不能给 P3-111 独立 Gate Pass。
- Gate 3：AI／网络／外部能力仍为关闭态的范围边界未被改变；独立隐私与内容身份审计未完成，不能给 Gate Pass。
- Gate 4：Blocked，仅因离线 Rust/Cargo 工具不可用。
- Gate 5：仅保留 P3-111 的有限本人使用 Evidence 范围描述；本任务零真实路径访问，不作 Gate 5 或 Stage 4 Pass。

## 初次 Blocked 的资产、风险和阶段（历史）

事实：P3-111 历史和 candidate 未写入；R-0040 仍 Open / Conditional，R-0052 仍 Open / Authorized Controlled Execution Boundary，R-0051 保持 Closed / Limited Controlled Boundary。资产继续 Not Frozen，工程基线没有恢复，Stage 4 没有进入。

推断：本次 `cargo`／`rustc` 缺失是评审环境阻断，不构成已证实的 P3-111 工程缺陷。

建议：PM 按 Blocked 处理，不把它记作 Rework 或候选 Pass。只有在相同 Frozen ABF、无网络、无真实 app／Pilot-2 访问且离线工具可用的合规环境中，才可从全新的同一精确临时根完整执行 M-005～M-013。那次执行必须重新保留 test/build logs、自有 verifier、祖先 `/disposable/noop` unchanged control、六类真实 mutation、提交 verifier cross-check、清理和非自指 Manifest；之后仍由 PM 验收与用户采纳决定后续状态。

## 交付与 Evidence

- 独立 Review：`lifeos/reviews/LIFEOS-P3-112/independent_review.md`
- Evidence 根：`lifeos/reviews/LIFEOS-P3-112/evidence/`
- 关键 Evidence：`authorization.md`、`session-boundary.md`、`test_design.md`、`read-order.md`、`fixed-inputs.json`、`candidate-manifest.json`、`copy-inventory.json`、`offline-results.json`、`blocked-matrix.json`、`cleanup-before.json`。
- 本地模型预检：已跳过；任务卡明确允许因 P0 独立性、真实数据零访问与 Evidence 真实性判断而跳过，且预检不得决定本结论。

## 初次结论时需 PM 确认（历史）

1. 采纳本次 `Blocked`（非 Rework）结论。
2. 若要继续，决定何时在可用的离线 Rust/Cargo 环境下重新完成同一 Frozen ABF 的全量独立复评；不得以当前不完整资产推进风险、冻结、基线或 Stage 4。

## Rework 1 交付补充（当前结果）

初次 Blocked 是已保全的历史结果：evidence/MANIFEST.md 仍为 8b89d329a7eb109b5a3bd21084eedd5ea0e5c906f73140bf249b293ef172692d。本轮只更新 P3-112 自有 runner、Rework Evidence、Review 与本交付物；P3-111 固定输入 12/12 和 72-file candidate tree cc1ff0f05d5d3993c8b113dae80a043b3d7f535a05a8236771b980a4892718a3 全部复算匹配。

从空的精确临时根完整执行 M-005～M-013。已存在的离线 Cargo/Rustc fallback 经明确验证，根内 TMPDIR／CARGO_TARGET_DIR 已设置；offline locked test 为 8/8，build exit 0。静态关闭态、12 条动态／隐私闭环、自有 37/37 与 38/38 verifier、祖先 unchanged control、六种真实 mutation、提交 verifier cross-check 均通过。清理后该临时根不存在；Pilot-2、真实 app、网络、P3-111 历史写入及风险／冻结／阶段账本写入均为 0。

最终计数：**P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0**。本任务专项结论：**Pass（待 PM 正式验收）**；不代表 P3-111 风险关闭、资产冻结、工程基线恢复、Stage 4 准入或用户采纳。

Rework Evidence 根：lifeos/reviews/LIFEOS-P3-112/evidence/rework-1/；逐行闭环：closure-matrix.json；复跑入口：tools/review_runner.py；正式独立 Review：lifeos/reviews/LIFEOS-P3-112/independent_review.md。

## 需 PM 确认

请仅决定是否采纳本轮 Rework 1 的独立 Pass。若采纳，仍须按既有治理流程分别处理任何后续风险、冻结、阶段或用户决定；本专项不自行推进它们。
