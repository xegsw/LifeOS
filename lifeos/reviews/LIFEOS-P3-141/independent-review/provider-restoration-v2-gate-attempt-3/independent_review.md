# LIFEOS-P3-141 Provider Restoration v2 Gate — Attempt 3 独立复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-141
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：主仓库 `26c08409e83a01caea7388223e51a76182a22a3c`，工程来源 `5837fb4ffd4203a24d5908d990d1996b3aae4dcf`
- 对应交付物路径：`lifeos/engineering/LIFEOS-P3-141/closure-provider-restoration-v2-gate/candidate/`
- 独立评审角色：第三个全新隔离独立复评会话
- 协审视角：无；未采信工程 runner、fixture、PID、截图或结论
- 评审关卡：ABF-P3-141-v2，ABF2-M-001～009
- 独立评审路径：本目录
- 评审结论：**Rework — P0 fail closed**
- 风险等级：L3 / Gate
- 独立评审触发事实：v1 receipt binding 修复后必须全新隔离复评；attempt-2 又因 precontact 时序失效。

## 独立性与回流规则

- 执行侧与评审侧是否隔离：是。预接触前只读取指定治理输入；随后在本 worktree 先创建并立即 hash `test_design.md`、`write_allowlist.md`、`precontact_seal.json`，才首次接触 Git／候选。
- 是否只评审能力包的最终 Evidence／hash：是。候选固定为 `26c08409`，使用 review-owned sparse local clone；原候选零写入。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：已保留本轮自写 PID/AX、loopback、精确清理和校验工具；P0 后不产生完整正向 runner 结论。
- 是否可验证 runner 未导入、调用或复制执行侧测试：本轮 loopback、PID/AX、input tooling 均为 review-owned。候选 54 项测试仅作为回归信息，不作为独立 Pass 证明。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：P0=1；P1=0；P2=0；Unknown=0；Not Implemented=6。
- 若需整改：同一 P3-141 Closure 内修正后，必须由另一全新隔离会话重新执行完整独立复评；不得复用本轮正向片段。
- 更新时间：2026-08-30

## 评审摘要

- precontact seal 完整有效；本轮没有重演 attempt-2 的候选先接触错误。
- 固定提交在合成离线构建中候选自带 54/54 测试通过；该结果不替代独立证明。
- 实际 Tauri desktop 直接绑定到 PID 87046、精确临时 binary、唯一 AXWindow、AXWebArea 与 CG window 87433；截图和 AX 树显示云端与本地五 Provider 的 UI 入口。
- review-owned 127.0.0.1 loopback 证明 `Custom OpenAI-compatible` 能在实际 Tauri 中保存、连接测试、发现 `fixture-model` 并显式启用；两个请求均为无内容的 `GET /fixture/v1/models`。
- **P0：实际合成 Capture 失败关闭。** `candidate/ui/runtime-adapter.js:12` 仍定义并由 `:331` 发送 `p3-130-capture-001`，而 `candidate/src/runtime.rs:32` 只接受 `p3-141-synthetic-capture-001`；点击“仅保存这条 Work，不创建长期关联”得到 `argument_schema_rejected`。因此无法合法进入首发锁定、fallback、重启或其余正向动态行。
- P0 后立即终止 Tauri 与 loopback，未修候选；唯一临时根已 marker-gated 精确清理。

## 已通过内容

- precontact 时序、review 写入隔离、禁止目标零触达和精确临时根清理。
- desktop 上 Settings 的 P3-140 五 profile 表达：云端显示 OpenAI、Anthropic、DeepSeek、Kimi／OpenAI-compatible，本地显示 Ollama、LM Studio、本地兼容服务。
- 实际 Tauri Custom profile 的保存→测试→模型选择→显式启用分离；此有限动态事实不外推为首次发送锁定或完整 Provider Pass。

## 关键问题

- P0 / ABF2-M-002：`candidate/ui/runtime-adapter.js:12` 的 synthetic capture key 停留在 P3-130，且 `:331` 将该 key 传给 `capture_record`；它与 `candidate/src/runtime.rs:32` 的 P3-141 固定 key 不一致，使实际应用不能记录本轮唯一固定合成 Work，构成 P3-141 20 IPC/Runtime 能力回归。

## Closure List

- CL-IR-V2-04：工程在同一 P3-141 Closure 内将 UI adapter 的 synthetic capture key 与 P3-141 Runtime 合同精确对齐，并补充该实际 Tauri 反例的工程回归。
- CL-IR-V2-05：修正后另起全新隔离独立评审，从新的 precontact seal 起完整执行 ABF2-M-001～009、五 profile/Custom 正负 loopback、20 IPC、四类 mutation、三档 PID-bound actual-Tauri、Manifest 与 cleanup；不得复用本轮的正向片段。

## 条件通过项

无。P0 fail-closed，不适用条件通过。

## 关卡检查

- Gate 1 产品一致性评审：未通过；P3-141 实际合成 Capture 回归。
- Gate 2 数据与来源评审：未通过；P0 使完整来源／动态闭环不能完成。
- Gate 3 AI 权限与信任评审：未通过；首次发送锁定／无 fallback 未获独立动态证明。
- Gate 4 技术可行性评审：未通过；虽然 desktop/UI/Custom discovery 可用，完整动态合同被 P0 阻断。
- Gate 5 用户价值验证评审：不适用；未进入 Phase C 或真实 Pilot。

## 风险

- 不关闭 R-0056；不恢复 Phase C，不生成真实 receipt，不冻结，不进入 Stage 4。

## 需要 PM 决策

- 接收同一 P3-141 Closure 的 P0，安排工程修正和另一全新隔离复评；不得把本轮 Custom 连接成功误读为独立 Gate Pass。

## 最终建议

结论为 Rework。候选确有 P0；本轮不提供任何 Phase-C、真实 Provider、真实 receipt、风险关闭、冻结或 Stage 4 的正向结论。
