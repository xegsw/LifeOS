# LIFEOS-P3-143 Mandatory Independent Review

## 评审信息

- 对应任务 ID：LIFEOS-P3-143
- 被评审结果：真实 AI 服务与加密凭据安全启用闭环；候选由独立工程会话产生。
- 评审角色：AI 信任与安全负责人（主审）；技术架构与数据／来源视角协审。
- 评审关卡：L3 强制独立评审／Phase C。
- 评审路径：`lifeos/reviews/LIFEOS-P3-143/independent-review/`
- 评审结论：**Rework**
- 风险等级：L3
- 触发事实：真实凭据、Keychain、受控第三方网络与删除安全边界；合同强制全新隔离独立评审。

## 独立性与输入核验

- 本评审为全新隔离会话。任何候选、工程交付物、工程 Evidence、P3-143 Final Manifest 或 Phase-B 收据接触前，已创建并哈希 `test_design.md`、`allowlist.md`、`prohibited_paths.md` 与 `precontact_seal.json`。封签 SHA-256：`90082eb8cf878be86c78d713dedd2c66eb0fd88c28af80c7666d7287caea773b`。
- 冻结输入复算 10/10 一致；候选 Final Manifest 以评审自有 runner 复算 124/124 一致且非自指。评审 runner 未导入、执行或复制候选 verifier/test。
- Phase-B 收据仅作只读、字段净化后的非内容核对。未读取或记录 API Key、prompt、response、模型标识或错误正文。
- 评审自有 root 已创建为 `/private/tmp/lifeos-p3-143-independent-review-v1`，0600 marker 经核验；离线编译产物仅写入该 root。没有运行候选 test、App、Keychain、SQLite 生命周期或网络动作。

## 决定性问题

### IR-P0-001｜固定候选不能绑定全新的 review-owned DB/root

**事实。** `candidate/src/runtime.rs` 将 `TASK_ROOT` 固定为工程 Phase-B 根 `/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1`，`verify_task_root()`只使用该常量并会在缺失时创建它；候选没有受验证的 review-root 参数或环境覆盖入口。评审自有静态 runner 的 IR-S-008 因此失败。

**影响。** ABF-I-13 与 ABF-M-022 要求 fresh reviewer、fresh DB/root/PID。启动固定候选来做凭据、篡改、删除或三档 actual-Tauri 测试会接触工程保留的 Phase-B root，而不是评审自有 root。这会混合独立性、破坏评审的 synthetic lifecycle 证据，并可能改变保留的工程 handoff 状态。

**处置。** 本评审在任何运行期写入前停止；未把静态通过、工程测试或 Phase-B 收据误作独立动态证明。该问题属于同一 Task Contract 的工程 Closure Cycle，必须由工程侧提供可验证且 fail-closed 的 fresh review-root 绑定方案，并重新形成 fixed candidate 后，再以全新隔离独立评审重做受影响矩阵。

## 已通过的有限事实

- Frozen task/ABF 与 predecessor freeze entries 的当前 SHA-256 全部匹配。
- P3-143 Final Manifest：124/124 当前文件 hash 一致，`self_referential=false`。
- 静态精确 IPC 列表为 20 项；UI 未发现直接浏览器网络 primitive。
- 静态 DeepSeek adapter 声明精确 HTTPS authority、清空环境、禁止 proxy、限制 redirect；凭据实现使用 AEAD ciphertext 与 Keychain 物理分离。
- review-owned `cargo check --locked --offline` 成功，未启动 App、候选测试、Keychain、DB runtime 或网络。

这些仅是有限静态／编译事实，不构成凭据生命周期、泄漏攻击、mutation、fresh PID、actual-Tauri 三档或独立真实 Gate 的通过。

## Evidence 一致性

- 工程交付物前段仍称 Phase B “未开始”，而后段及 `phase_b_checkpoint.json` 已记为完成并等待 Phase C。后者与逐项非内容收据序列一致；前者应在同一 Closure Cycle 内纠正为无歧义状态。该项为 P2，不改变本评审的 P0 结论。
- 评审首个静态 runner 的 IPC 全文正则产生了错误计数，已保留为 excluded review-tool artifact；仅修正后的 rerun 被用作事实。未影响候选或历史资产。

## 关卡检查

- Gate 1 产品一致性：**有限通过**。Cloud 8／Local 4、Settings 基线与 20 IPC 的静态谱系仍在；最终动态体验未完成。
- Gate 2 数据与来源：**Rework**。密文／Keychain 静态设计可读，但 fresh DB、DB-only、tamper、delete/restart 独立实测被 P0 合法阻断。
- Gate 3 AI 权限与信任：**Rework**。DeepSeek single-authority 静态边界存在，但无法建立合格的 review-owned action/network lifecycle。
- Gate 4 技术可行性：**Rework**。离线编译通过，但 runtime root 设计不支持合同所需独立验证。
- Gate 5 用户价值验证：**Not Assessed**。本任务不是用户价值／Stage 4 验证；不得把既有用户操作视为本关卡结论。

## 计数与未实施项

- P0：1（IR-P0-001）。
- P1：0。
- P2：1（工程交付物的累积状态文字未收口）。
- Unknown：0；阻断原因已由固定候选源码确定。
- Not Implemented：16 个受 P0 安全停止影响的独立动态项，详见 `review_matrix.json`（凭据保存／复制／篡改／更新／删除、独立 action/network counter、三档 fresh PID/AX/screenshot、checkpoint resume 和新的用户真实 Gate）。

## Closure List

1. 工程侧在不放宽原生产根 marker/authority/Keychain 安全约束的前提下，提供可审计、受限且 fail-closed 的 fresh independent-review runtime-root 绑定；不得让任意环境变量或任意路径绕过 root policy。
2. 使用该修正后的固定候选重做工程 Gate 受影响的 root／DB／Keychain 生命周期与 Manifest。保留本次 Review 和工程 Phase-B 历史为只读。
3. 再建立全新隔离 Review：先封签，再用全新 synthetic DB/root/canary 重做 ABF-M-002～016、M-021、M-022 及三档 direct-PID native Evidence。只有新的合成独立 Gate 全通过，才可请求用户在 Review App 内手工输入 DeepSeek Key 并逐次操作。
4. 仅在新的独立 Gate 通过后，用户在 App 内进行新的 DeepSeek-only、非内容 Real Gate；不得聊天粘贴 Key、不得代点、不得使用其他 Provider。

## PM 决策与最终建议

- **需要 PM 决策：No new authority required.** 建议 PM 将本结论送回同一 P3-143 Closure Cycle；修正不改变用户结果、Provider、20 IPC、数据类别、凭据方案或已冻结 ABF。
- 本评审不做 PM 验收、不关闭／重开风险、不冻结产品／工程、不恢复基线，也不触发 Stage 变化。
- 不请求用户提供 Key，也不建议在当前候选上继续真实 Provider 操作。
