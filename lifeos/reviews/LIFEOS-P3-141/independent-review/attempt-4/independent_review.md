# LIFEOS-P3-141 Phase B 独立评审（Attempt 4）

## 评审信息

- 对应任务 ID：LIFEOS-P3-141
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：`d35a72bf6fbcb9d6cdc905eac100679b69c97e61`；候选树 `78469762ec4be5dfa5a7b4728139d3703b96f396`
- 对应交付物路径：`lifeos/engineering/LIFEOS-P3-141/candidate/`
- 独立评审角色：隔离独立评审
- 协审视角：受控运行时、SQLite 生命周期、Provider 锁定、actual-Tauri 与 native AX
- 评审关卡：P3-141 Phase B / L3 Evidence Gate
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-4/`
- 评审结论：**Rework**
- 风险等级：L3 / Gate
- 独立评审触发事实：任务卡明确要求全新隔离、动态验证、actual-Tauri 和非自引用 Manifest。

## 独立性与回流规则

- 执行侧与评审侧是否隔离：Yes。启动时先写入并哈希本轮 `test_design.md`、`write_allowlist.md` 与 `precontact_seal.json`；候选只读。
- 是否只评审能力包的最终 Evidence／hash：Yes。12/12 固定输入通过；P3-139 77/77、P3-140 79/79 谱系逐文件哈希通过；候选树在前后均保持不变。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：Yes，见 `tools/` 与 `evidence/matrices/`。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes。本轮 runner 为评审自写的 `tools/attempt4_independent_runtime_tests.rs`；仅在唯一受控临时根的候选副本中编译运行。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：发现两个 P0；无 P1；P2 无；外部真实 Provider 派发为 Not Implemented。
- 若需整改：回到同一 P3-141 能力包 Closure Cycle，修正后以全新隔离 Attempt 重新独立复评，不创建微型整改任务。
- 更新时间：2026-08-30（Asia/Shanghai）

## 评审摘要

- 静态与独立动态主矩阵大部分通过：精确 20 IPC、四选一 Provider、首发锁定、Work 7–14 天、Memory ≤3、根所有权、Context/Today/feedback/budget 的失败关闭，以及 7/7 review-owned mutation 都被验证。
- 12/12 固定输入、P3-139 77/77、P3-140 79/79 和候选 79 文件谱系全部通过；未发现 P3-133/P3-131 残留。P3-140 Today 兼容引用为任务/ABF 明确保留项，不视为残留。
- receipt 缺失时，离线构建在解析或探测 runtime root 前即失败；fresh missing root 唯一成功，既有空目录、文件、链接、祖先链接、非规范路径、未拥有 DB、未知文件和 sidecar 均失败关闭。
- **P0-IR-141-01：actual-Tauri 的启动 receipt 尺寸不等于本次实际 AXWindow 尺寸。** 700×760、560×640 两档均已在同次 launch PID 上直接绑定到 `AXWindow → AXWebArea`，但 receipt 仍记录 1280×949；1280×1024 档亦实际/receipt 为 1280×949。receipt 在平台 resize 落定前采样，未满足 AC-16 的 actual inner/outer 核对。
- **P0-IR-141-02：receipt-enabled 受控实际运行下，Today Health UI 的合法五字段保存请求会在写前被拒。** UI real-mode payload 发送 `source:local:user-confirmed`，而同一受控 fixture mode 要求 `source:synthetic:controlled-fixture`；独立动态调用精确 UI payload 得到 `source_refs_rejected` 且未创建 root/DB。因此未形成所需的 UI→SQLite→Today/feedback 一致成功链。
- Computer Use 已用于一次本地 app 定向尝试；debug Tauri bundle 不在其 app inventory。随后以**本次 launch PID**做直接 Accessibility 绑定成功，未全局枚举窗口，且没有出现 macOS Accessibility 未授权。
- 无真实文本、真实 Provider、凭据或网络；未访问受保护的真实自用根。Phase C/D/E 均保持 Pending / Not Implemented。

## 已通过内容

- 受控 write-before-failure：daily/total Work、第四条 confirmed Memory、非法 Health、receipt 缺失、授权/预算失败均无意外写入。
- Provider 定义及首发锁定：OpenAI、Anthropic、Ollama、LM Studio 四档；Custom 拒绝；锁后切换拒绝；未执行外部调用。
- owned restart 无重复 capture/day 或发送；Context Resolver、Today、feedback 与 budget 的受控正负路径保留一致的前后计数。
- review-owned mutation 对 receipt、root ownership、provider lock、Work limit、Health、Memory、feedback-budget 7 个核心哨兵全部杀死。
- 三档真实 Tauri launch 均为新的 PID，title、`AXWindow` 和 WebView accessibility descendant (`AXWebArea`) 直接绑定；截图仅含固定合成脱敏 UI。

## 关键问题

### P0-IR-141-01：启动 receipt 记录了过早的尺寸

证据：`evidence/matrices/actual_tauri_viewports.json`。实际 PID-scoped AX frame 为 700×760 与 560×640，但相应 receipt 均为 1280×949；1280×1024 请求也被平台限制为 1280×949。该 receipt 不能证明、也没有如实记录三个实际窗口档位的 inner/outer 尺寸。

### P0-IR-141-02：Today Health UI 与受控 fixture 来源合同不一致

证据：`evidence/matrices/dynamic_runtime_matrix.json` 的 DYN-04，以及评审自写测试 `attempt4_today_health_ui_payload_rejects_in_controlled_fixture_mode`。合法五字段值本身和 SQLite 约束可通过，但 UI 在 receipt-enabled fixture mode 的精确 payload 被 `source_refs_rejected` 写前拒绝，故契约要求的 UI 成功链未达成。

## Closure List

1. 令 `write_startup_ready_receipt` 在窗口尺寸真正稳定后取得 inner/outer，或将 receipt 与 AX/平台实际 frame 的语义明确一致；在 1280×1024、700×760、560×640 三档以新的 PID 复测，receipt 必须逐档相符。
2. 统一 Today Health UI 与 runtime 的 fixture-source 合同，使 receipt-enabled 受控实际运行可保存合法五字段，并证明 UI、SQLite、Today 与 feedback 的一致性；保留非法/extra free_text 写前拒绝。
3. 完成以上两项后，在同一 P3-141 能力包中用全新隔离目录重做 Phase B 独立复评；不得将真实 Provider 派发替代为本轮完成项。

## 条件通过项

不适用。存在 P0，不能给出 Pass with Conditions。

## 关卡检查

- Gate 1 产品一致性评审：**Rework**。Health 的实际 UI 受控路径无法完成合法保存。
- Gate 2 数据与来源评审：**Rework**。受控 fixture mode 的 UI 来源引用与 runtime 要求冲突；其他 root ownership/写前拒绝通过。
- Gate 3 AI 权限与信任评审：**部分通过 / 外部派发 Not Implemented**。四 Provider、锁定及无 fallback 通过；真实 Provider/凭据/网络按合同未运行。
- Gate 4 技术可行性评审：**Rework**。PID scoped AX/WebView 绑定通过，但 actual receipt geometry 失败。
- Gate 5 用户价值验证评审：**Pending / Not Implemented**。本 Phase B 只允许合成离线验证。

## 风险

- P0：将错误或过早的 startup receipt 当作真实三档窗口 Evidence，会导致 AC-16 误判。
- P0：若不统一 UI/runtime fixture source，Phase B 的无真实数据 UI Health 验收无法完成。
- Unknown：真实 Provider 派发、用户真实自用与后续 Phase C/D/E 均不在本轮授权内，不能由合成验证推断为已完成。

## 需要 PM 决策

需要 PM 将上述两项 P0 回流同一 P3-141 Closure Cycle，并在修复完成后安排新的隔离独立复评。无需用户处理 macOS Accessibility：本机定向 AX 绑定已成功。

## 最终建议

**Rework。** 不建议声称 PM Accepted、风险关闭、Frozen 或 Stage 4。本轮只完成了 Phase B 的隔离审查并识别 P0；Phase C/D/E 必须继续标为 Pending / Not Implemented。
