# LIFEOS-P3-109 独立评审｜启动前 ABF 路径冲突

## 评审信息

- 对应任务 ID：`LIFEOS-P3-109`
- 是否为受控能力包：Yes；只读独立复评。
- 能力包边界／被评审最终 hash：固定 P3-106 candidate；未复制、未构建、未启动。
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-109_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_final_successor.md`
- 独立评审角色：独立 QA／安全与数据生命周期评审。
- 协审视角：体验设计、可访问性、技术架构、数据／领域、AI 信任安全。
- 评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅固定非敏感内部理解核对。
- 独立评审路径：新建 Codex 会话；用户投递任务卡路径构成执行授权。
- 评审结论：`Blocked`

## 能力包独立性与回流规则

- 执行侧与评审侧是否隔离：Yes。本轮为新会话；未复用 P3-104/P3-106/P3-107/P3-108 工程或评审会话。
- 是否只评审能力包的最终 Evidence／hash：尚未进入候选最终评审；只核对冻结输入和启动前边界。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：仅保留未执行的 task-local runner 源码和启动前分析；没有伪造结构化结果、Manifest 或复跑 PASS。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes；`evidence/runner/review_runner.py` 是本轮新建源码，未执行，且没有导入、调用或复制 P3-107/P3-108 runner/tool/Evidence。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：发现 Frozen ABF 的 P0 路径授权与必需 test Evidence 冲突。它不能在本能力包中修改 ABF。
- 更新时间：2026-08-24T03:54:00Z

## 评审摘要

- 已在工程动作前核对任务卡、Frozen ABF 和固定输入；ABF hash 与任务卡一致。
- 实际会话配置为 `gpt-5.6-terra` / `xhigh`，符合不得降级条件。
- 独立测试设计先于 P3-107/P3-108 runner／结果访问落盘并固定 hash；本轮未复制、导入或执行旧 runner/tool/Evidence。
- 只读候选源码表明 `cargo test` 将在 `/private/tmp/lifeos-p3-104-unit-*` 写入测试夹具。
- Frozen ABF 又要求所有写入只能命中其 14 个逐字枚举的 P3-109 路径；unit-test 路径不在其中。执行或跳过 test 都无法满足 M-005/I-03 与 I-04。
- 已在任何 candidate copy、build、fixture、GUI／app 操作前停止；因此没有以旧动态 Evidence 或自报状态替代当前验证。
- ABF 第 22 行的 14 个精确临时路径均经只读检查为不存在；见 `evidence/cleanup_pre_execution.md`。
- 已对已生成的静态 Evidence 作 JSON、hash 与语法只读自检；见 `evidence/preflight_validation.md`。

## 已通过内容

- M-001：任务投递、ABF ID／hash、模型与推理强度及六张固定图／两个历史输入 hash 已核对；见 `evidence/authorization.json` 与 `evidence/fixed-inputs.json`。
- M-002：先测设计与旧 P3-107/P3-108 runner／结果隔离已记录；见 `evidence/test_design.md` 和 `evidence/read_order.json`。
- 静态启动前路径冲突已可复核；见 `evidence/startup_scope_analysis.md`。

## 关键问题

P3-109 ABF 第 22 行的精确路径授权与 M-005/I-03 的 `cargo test --locked` 要求矛盾。候选测试按其自身源码必然写入未授权的 `lifeos-p3-104-unit-*`。这属于 L1 授权不漂移／可复核性和 L2 I-04 的边界问题，不是候选 P0/P1 缺陷结论。

## 必须整改项

本任务内不得整改 Frozen ABF。PM 必须关闭或 supersede 本任务，并在新的任务卡与 ABF 中二选一：

1. 明确逐字授权候选 unit-test 所需的临时目录及其精确清理；或
2. 重新冻结不执行该 unit-test 时仍可验证 M-005/I-03 的独立方法和验收公式。

新任务必须重新授权、重新冻结 ABF，并在执行前再次检查路径与 test 行为。

## 条件通过项

无。`Blocked` 不构成条件通过或候选通过。

## 关卡检查

- Gate 1 产品一致性评审：Blocked，未进入 actual-app／视觉／响应式矩阵。
- Gate 2 数据与来源评审：Blocked，I-04 路径授权冲突阻止使用任何新 DB／夹具。
- Gate 3 AI 权限与信任评审：Blocked，未进入 runtime／IPC／关闭态实际验证；未发现授权范围外访问。
- Gate 4 技术可行性评审：Blocked，M-005 的必需离线 test 与 I-04 不能同时满足。
- Gate 5 用户价值验证评审：N/A；任务卡仅要求固定非敏感内部理解核对，且未作为阶段 Pass。

## 风险

- 不更新项目账本。请 PM 关注 Frozen ABF 许可路径与候选测试行为的冲突；现有 R-0040、R-0051、R-0052 状态不因本评审改变。
- P0/P1/P2/Unknown：`0/0/0/0` 仅表示尚未对候选形成缺陷裁决；不得解读为候选通过。
- Not Implemented：`14`（M-003 至 M-016）。它们未执行的原因是启动前 Frozen ABF 冲突。

## 需要 PM 决策

确认关闭／supersede P3-109 并新建含一致路径授权与 M-005 验收依据的任务；专项执行方不得在当前 Frozen ABF 下继续。

## 最终建议

不建议冻结、不建议进入下一阶段，也不建议以历史动态 Evidence 补足当前矩阵。保持 P3-109 为 `Blocked`，等待 PM 按 D-0401 新建任务和 ABF。

## 本地预检

已跳过。本任务是 P0 独立性、路径授权、真实 Tauri/IPC、native geometry 和 Evidence 真实性的最终评审；本地模型预检可能将启动前治理冲突误导为候选技术结论，且任务卡明确允许跳过。
