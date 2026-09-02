# LIFEOS-P3-143 Mandatory Independent Re-review 1

## 评审信息

- 对应任务：`LIFEOS-P3-143`（L3）。
- 对应候选：`767301fb051d11a6bf11488413f8b03aabfc2d99`，分支 `codex/l3-p3-143-real-ai-activation`。
- 评审路径：`lifeos/reviews/LIFEOS-P3-143/independent-re-review-1/`。
- 评审角色：独立技术架构／AI 信任与安全复评；协审视角为数据生命周期与 Evidence 可信度。
- 独立性：全新隔离会话；candidate、历史和 PM 账本均未修改。
- 触发事实：L3 凭据、Keychain、网络与真实能力边界；工程 Closure 旨在关闭 `IR-P0-001`。
- 结论：**Rework**。

## 评审摘要

1. 在任何候选或工程 Evidence 接触前，评审已新建、hash 并封存 test design、allowlist、禁止路径声明和 precontact seal；时序有效。
2. review-owned verifier 独立复算 P3-143 Final Manifest `125/125`、P3-142 Final Manifest `117/117`，均为零 hash error；candidate worktree 与指定 commit 一致。
3. `independent-review / rereviewb20260902` 是合法的编译期 profile/run-id，候选可离线构建。
4. P0：对预先创建的 0700、直接位于 `/private/tmp` 的合法形状 review 根，故意省略 marker 后，候选没有写前拒绝，反而创建了 marker、`runtime/` 和 `secure-provider-settings.sqlite` 并继续运行。
5. 此行为直接违反本轮“marker 缺失／错误／权限错误及 DB symlink 必须在 DB、Keychain、网络或其它状态写前 fail closed”的根权威合同。环境注入根没有被创建，不能抵消 marker-missing 的 DB 写入。
6. 依停止规则，评审在 P0 后停止其余候选动态、Keychain、网络、真实 Provider、GUI 和 mutation 操作；不把候选自测、历史 GUI 或工程 verifier 当作独立正 Evidence。
7. 写入者已停止；该 review-owned 根在正确 marker 被验证后已 marker-gated 精确清理，且没有触碰任何 Pilot、真实 DB／路径／文本、真实 Provider、API Key 或网络。

## 独立性与固定输入

- Precontact controls：`controls/test_design.md`、`controls/allowlist.md`、`controls/prohibited_path_declaration.md`、`controls/precontact_seal.json`。
- 当前 commit、P3-143 root-authority Closure、P3-143 Final Manifest、P3-142 task/deliverable/PM Review/Manifest 均以精确路径、只读方式绑定。
- Review-owned verifier／attack 位于 `review_tools/`；没有导入、调用或复制 candidate verifier 作为独立结论。
- 历史 P3-139～P3-142、候选和 PM 账本保持只读。

## 逐项矩阵与五类计数

完整 ABF-M-001～022 结果见 [review_matrix.json](evidence/review_matrix.json)。

- P0：1（`IR-RR1-P0-001`，existing-root missing-marker 可导致 SQLite 初始化）。
- P1：0。
- P2：0。
- Unknown：0。
- Not Implemented：20（P0 后依合同停止；这不是对候选其余能力的否定）。

## 关卡检查

- Gate 3（AI 权限与信任）：**未通过**。根权威失败使凭据／本地数据写入的安全前置条件不可成立；未执行真实 Provider、Keychain凭据或个人内容动作。
- Gate 4（技术可行性）：**Rework**。闭合 build-time profile 不足以约束一个预先存在但缺 marker 的 authoritative-shaped root。
- Gate 1／2／5：本轮不形成通过结论；没有把静态谱系或历史 Evidence 外推为 Gate Pass。
- Stage 3→4：不适用；本评审不授权 Stage 变更。

## Closure List

1. 在 `verify_authorized_root` 中区分“root 新建”与“root 已存在”。仅新建根可原子创建 identity-bound marker；任何已存在但缺 marker 的 root 必须在创建 `runtime/` 或 SQLite 前拒绝。
2. 在修复后的固定 commit 上，另起全新隔离 independent review，从新的 precontact seal 开始，覆盖所有原合同 root / DB / marker / symlink / environment-injection 攻击与 fresh GUI PID 证据。
3. 不在本评审会话修改候选、工程 Evidence、PM 账本、风险、冻结或 Stage。

## 非结论与 PM 决策

- 本结论不是 PM Accepted、真实 Phase C Pass、风险关闭、产品 Frozen 或 Stage 4 结论。
- 需要 PM 决策：按同一 P3-143 Closure Cycle 回工程侧修复 `IR-RR1-P0-001`；修复后必须分派全新独立复评。真实网络／Keychain凭据／DeepSeek Gate 继续禁止，直至新的独立复评满足合同。
