# LIFEOS-P3-144 Closure-1 后 Phase B 全新隔离独立复评 1

## 评审信息

- 对应任务 ID：LIFEOS-P3-144。
- 是否为受控能力包：Yes；本轮只覆盖 Phase B 合成／离线边界。
- 被评审候选：commit `4115f2958d8fa08fa30fccc90217bdc404769363`，Git tree `91fd9af221c8615fca99b760d4317370966defb2`。
- 独立评审角色：独立评审；协审视角为数据／来源、AI 信任与安全、技术可行性。
- 评审关卡：ABF-P3-144-v1 的 Phase B 独立复评（M-001～M-024、M-032）。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-144/independent-re-review-1/`。
- 风险等级：L3 / Gate。
- 独立评审触发事实：Closure-1 后的全新隔离独立复评。
- 评审结论：**Rework / Not Pass**。

## 独立性与回流规则

- 先封存后接触：在接触 candidate、工程 Evidence、首次 Review、deliverable 或 Manifest 前，本评审已自写并 SHA-256 封存 `precontact/test_design.md`、`allowlist.md`、`prohibited_path_declaration.md`；见 `precontact/seal.json`。
- 范围：仅固定候选、固定输入、评审自有目录及固定合成临时根。Phase B 中没有访问真实内容、真实 Provider、其他 Provider、网络或 Pilot-7。
- 候选／工程／历史：只读。评审写入只在本目录；`git status --short` 最终只出现本评审目录。
- runner 独立性：`review_tools/` 为本评审自有源码，未导入或复制候选 verifier／测试。候选测试只作为明确标注的 `support` 回归信息，不作为独立 Pass 依据。
- Closure-1 早期 Review：只读保留；其固定根 authority P0 已由 Closure-1 修正。本轮在精确冻结根实际运行。

## 评审摘要

1. 固定输入、Closure-1 Manifest、候选树与 Git identity 复算通过：85/85 candidate 文件、3 fixed inputs、3 preserved-history、12 closure Evidence 均匹配；见 `evidence/lineage_verification_closure_2.json`。
2. review-owned 静态审计通过 17 项：exact 20 IPC、编译期 synthetic 模式、固定根 profile、3×200、最小披露、确认、Health 非医疗、DeepSeek 精确 authority、无 proxy／redirect／fallback／第二网络面等；见 `evidence/static_phase_b_audit.json`。
3. 新鲜实际 Tauri 在 desktop、compact、narrow 三档均取得 direct-launch PID → 唯一精确 AXWindow → AXWebArea → CG target-window 链。desktop/compact 截图清晰；narrow 的 target-window 截图链有效但 raster 仅 178×314，故不将其上升为可读的窄布局视觉 Pass。
4. desktop App 实测了合成 Work/Health 三条上限、第四条拒绝、非医疗提示、DeepSeek-only 本地披露、显式配置／测试／选择／启用、逐次确认、AI Understanding 与五种反馈入口；只用了评审自写合成字符串，数据库摘要无正文与秘密。
5. 负向 marker 变异被拒绝且没有删除根；恢复原 marker 后，精确 marker-gated cleanup、三个 PID 停止、合成 Keychain key 与 build target 清理均通过。
6. **P1：完整串行回归失败。** `cargo test --locked --offline -- --test-threads=1` 为 18 passed / 3 failed / 21 total。前序 `p3_144_phase_a_context_limits_disclosure_and_confirmation_are_fail_closed` 保留固定 review root，导致随后三个要求“根初始不存在”的测试失败。三项各自隔离运行均通过，证实是候选测试顺序依赖；详见 `evidence/candidate_serial_regression.json` 与 `isolated_regression_support.json`。

## 逐行 Phase B 矩阵

| ABF 行 | 状态 | 本轮事实与 Evidence |
|---|---|---|
| M-001 | Pass | 固定候选／历史／Closure lineage 复算通过；`lineage_verification_closure_2.json`。 |
| M-002 | Pass | seal、allowlist、禁止路径声明在候选接触前完成；本轮零接触审计。 |
| M-003 | Pass（合成实际） | desktop App 写入 3 条 Work；仅 aggregate DB 计数保留。 |
| M-004 | Pass（合成实际） | desktop App 写入 3 条非医疗 Health Current State。 |
| M-005 | Partial | 两域第四条在实际 UI 写前拒绝；3×200／DTO guard 为 review-owned 静态审计，未把它单独宣称为完整黑盒 mutation Pass。 |
| M-006～M-009 | Partial | relevance／validity／budget guards 静态审计通过；候选 support test 覆盖 Work-only、restart、stale 及 invalidation，但未作为独立 mutation Pass。 |
| M-010 | Partial | 实际 UI 披露精确显示 3 条 Work、DeepSeek authority 与“移除”控件；删除操作未以 GUI 执行。 |
| M-011 | Partial | 无配置时确认被实际拒绝；有显式 synthetic 配置后确认才产生 Understanding；未单独执行 cancel mutation。 |
| M-012 | Partial | candidate support test 覆盖 restart、变更集合及 confirmation replay；未形成独立 black-box replay harness。 |
| M-013～M-014 | Pass（静态／离线） | DeepSeek-only、无 fallback/background、exact HTTPS authority、proxy／redirect 守卫均由 review-owned 静态审计复核；Phase B 未联网。 |
| M-015 | Pass（合成实际） | 合成 credential 保存后输入框清空、SQLite 仅 AES-256-GCM aggregate、Keychain 分离；缺 key／篡改为 isolated candidate regression support，最终 synthetic key 已删除。 |
| M-016 | Pass（合成实际） | 确认后形成 AI Understanding，provider/model/source identity 可见，且 UI 明示无网络。 |
| M-017 | Pass（合成实际） | UI 显示 confirm/edit/reject/ignore/correct 五项；`ignore` 已实际写入并显示 recomputed。 |
| M-018 | Partial | correction/revocation invalidation 由 support test 与静态审计确认，未另写黑盒 dependency harness。 |
| M-019 | Pass（合成实际＋静态） | UI 明示诊断／治疗／用药／紧急判断非范围；support test 的 medical fixture 拒绝。 |
| M-020 | Pass | PID 19293；唯一 AXWindow、AXWebArea、CG target window、desktop target screenshot。 |
| M-021 | Pass | PID 19550；唯一 AXWindow、AXWebArea、CG target window、compact target screenshot。 |
| M-022 | Evidence Gap（已界定） | PID 19591、唯一 AXWindow、AXWebArea、CG target-window 截图均成立；但 target raster 低清，错误的几何重截取已隔离且不纳入 Evidence。 |
| M-023 | Not Pass | Closure-1 Manifest/lineage 本身匹配，但完整候选 serial regression 有 P1，故不得宣布 Phase A Gate Pass。 |
| M-024 | Rework | 因 P1 且若干 mutation 只具静态／support 覆盖，不能构成 Independent Pass。 |
| M-025～M-030 | N/A — 未进入 | 仅 Phase C／用户真实操作；没有访问 Pilot-7、真实 DB、真实凭据或网络。 |
| M-031 | N/A | 本轮没有可恢复环境中断，不创建 checkpoint。 |
| M-032 | Pass（结构） | 本评审 final Manifest 排除自身，由独立 verifier 重算；不能抵消 M-023/M-024 的 Rework。 |

## 已通过内容

- Closure-1 已将独立 root authority 固定到冻结的 `/private/tmp/lifeos-p3-144-independent-review-v1`，实际 App 能在该 root 运行。
- 20 IPC、DeepSeek 精确 authority、合成离线 mode、UI 内本地披露与再次确认的可观察边界均未见回退。
- 合成凭据显示为掩码、SQLite 只以加密结构计数复核；没有原文或真实秘密进入 Evidence。
- 三档 direct PID 的 AXWindow／AXWebArea 绑定完成；desktop 与 compact 视觉证据可读。

## 关键问题与 Closure List

### P1 — 完整串行回归不具顺序独立性

候选的 Phase-A context 测试留下冻结 review root；后续 root-symlink、wrong-profile/run-id 和 credential-ciphertext 测试均假设根初始不存在。因此 required serial command 失败，即使三项单独运行通过也不能替代完整回归。

同一 Closure Cycle 的工程整改应：

1. 使每一个根 authority 测试自给自足地建立／清理根，或引入严格的统一 setup/teardown，保证任意固定 serial 顺序下完整 suite 通过。
2. 在候选目录以固定 independent-review profile 重跑完整 `cargo test --locked --offline -- --test-threads=1`，并记录 root／Keychain cleanup。
3. 产生新候选 identity 后，启动**全新隔离**独立复评，从新 precontact seal 重新执行矩阵；本复评不得被追认成 Pass。

### 有界 Evidence Gap — 窄视口 raster

窄视口的 PID/AX/target-window 链为正，但原生目标窗口截图只有 178×314。用 AX 坐标做的 fallback 视觉上捕获到 Codex 而非 LifeOS，已放入 `excluded/`，不用于结论。下一次独立复评应在同一 PID target 上取得可读的 narrow target-only raster，或在执行前把 screen/coordinate capture 方法固定为能自验证 target content 的工具。

## 关卡检查

- Gate 1 产品一致性：未做产品冻结判断；本轮不改变产品范围。
- Gate 2 数据与来源：Phase B 合成边界、内容零 Evidence 和 lineage 结构通过；不构成真实数据批准。
- Gate 3 AI 权限与信任：离线／DeepSeek-only／显式披露确认有正证据，但因 P1 未达到 Gate Pass。
- Gate 4 技术可行性：实际 Tauri PID/AX 链通过；完整 serial regression P1 使本 Gate 不通过。
- Gate 5 用户价值验证：Phase B 不适用。

## 计数与边界

- P0=0；P1=1；P2=0；Unknown=0。
- `Partial` 与 narrow `Evidence Gap` 不会被解释成候选 Pass；Phase C 行为为合同内 N/A，不是已完成的真实验证。
- 本结论不是 PM Pass、风险关闭、冻结、Phase C 授权、Stage 4 准入或真实 DeepSeek／其他 Provider 批准。

## 需要 PM 决策

1. 令 P3-144 回到同一 Closure Cycle 修复 P1 测试隔离；不改变 Task Contract 即无需新产品任务。
2. 修复后，以新 candidate identity 启动全新隔离独立复评；不得复用本轮 seal、PID、DB、Keychain、截图、fixture 或结论。
3. 在新的独立复评明确补足 readable narrow target-only screenshot 与本轮标记为 Partial 的 review-owned negative mutation；随后才可由 PM 判断是否具备“允许进入 Phase C”的前置 Independent Pass。

## 最终建议

**不建议进入 Phase C。** 先关闭 P1，再以新隔离会话完成新的 Phase B 独立复评。即使将来复评 Pass，也只表示可交由 PM 决定是否允许 Phase C；不自动形成 PM Pass、风险关闭、产品冻结或 Stage 4 准入。
