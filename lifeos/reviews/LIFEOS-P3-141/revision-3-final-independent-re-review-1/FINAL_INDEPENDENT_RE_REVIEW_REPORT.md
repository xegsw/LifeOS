# LIFEOS-P3-141 Revision 3｜Final Independent Re-review 1

## 结论

**Rework**。计数为 **P0=0、P1=0、P2=1、Unknown=0、Not Implemented=0**。

本轮是新的、已封存、只读的独立复评，覆盖固定候选 `476e5f069671dc7d0dc53be88f9d328901d6d543`。候选未被修改；旧 Engineering GUI v2 与旧 Blocked Review 仅作只读谱系输入，未复用任何正向动态 Evidence。P2-001 使 ABF3-M-003／M-004／M-007 的用户可操作性无法作为全量 PASS 接受，因此本轮不能给出 Independent PASS。

这不是 PM 验收、风险关闭、Phase C 恢复、产品冻结或 Stage 4 结论。

## 封存、谱系与范围

- 候选接触前已写入并哈希 `test_design.md`、`write_allowlist.md`、`prohibited_paths.md` 与 `precontact_seal.md`；seal SHA-256 为 `3d3989c2bac6e7c6065958b56184e96c500a105257e639ec05eaf79bb8abc9be`。
- `lineage_and_fixed_inputs.json`：4/4 固定输入哈希一致；候选工作树与固定 commit 字节一致；Engineering GUI v2 commit 为 `2e39acfdf0d3a740d0e672037ba5c8e802cfa39e`；旧 Blocked review commit 为 `beca425560a74a73457802034db77484391a8231`。
- 唯一写入位置为本 review 目录与已清理的 `/private/tmp/lifeos-p3-141-revision-3-independent-review-final-v4`。未访问 Pilot-6、真实数据／DB／文本／Health、真实 Provider／凭据／网络，亦未触及任何旧 P3-141 临时根。

## ABF 矩阵

| ABF 行 | 结果 | 本轮证据 |
|---|---|---|
| M-001 Cloud 五项 | Pass | `static_results.json`、`gui/*.json` 的设置页 AX 内容 |
| M-002 Local 三项 | Pass | `static_results.json`、真实 UI local 模式观察 |
| M-003 模式隔离 | Rework | 后端 SQLite Cloud／Local 行隔离和失败关闭通过；但 P2-001 显示模式切换后 UI 与 backend mode 不一致 |
| M-004 凭据持久化 | Rework | 保存、重启、更新、删除均可复现；P2-001 阻断未保存模式切换后的直接删除 |
| M-005 明文排除 | Pass | `credential-*-db.json` 仅含密文摘要，两个合成 canary 均未出现在原始 SQLite；UI 仅掩码 |
| M-006 密钥管理 | Pass | 单独 `keys/credential-aead.key`、普通文件、0600、32 字节、与 runtime DB 目录分离 |
| M-007 用户流程 | Rework | 保存／测试／选择／启用／发送均分离，且本轮未调用网络动作；P2-001 的可见删除控件失败破坏操作一致性 |
| M-008 恰好 20 IPC | Pass | `static_results.json`，20/20，旧 session credential IPC 不存在 |
| M-009 视觉与响应式 | Pass | 3 次直启 PID→唯一精确标题 AXWindow→AXWebArea/WebView→Settings→截图；desktop 实际 1280×949，compact 1160×768，narrow 700×760 |
| M-010 继承防回退 | Pass | 14/14 review-owned 静态断言、5/5 语义 mutation 检出 |
| M-011 独立性与历史 | Pass | precontact seal、只读谱系、全新 PID/窗口/截图/临时根 |
| M-012 数据边界 | Pass | synthetic-only、无网络动作、清理前后受控根验证 |

## 动态验证摘要

- 离线实际构建：`build_result.json` return code 0；构建产物 binary SHA-256 为 `cefec4b7a4b6e432fc5eb20263dbdf9d7d3fdc99e2e9ae1e19cd01234f66ab3e`。
- 原生 GUI：desktop PID 92475、compact PID 92485、narrow PID 92493；均为本轮直启 PID，唯一标题 `LifeOS · P3-141 Controlled Pilot Candidate`、`AXWindow` 与 `AXWebArea/WebView`，均已退出。原生窗口截图见 `gui/`。
- 合成凭据：空值保存被 UI 拒绝且 DB 无行；保存后为一行 cloud/openai 密文且 key 0600 分离；重启仍掩码；更新仍一行且 ciphertext SHA-256 改变；真实 UI 删除后 DB 行数为 0，重启后无掩码和删除控件。
- local 隔离：真实 UI 点击 local，并保存合成 loopback endpoint 后，SQLite 的 active mode 为 local 且 cloud/local 状态行分离；cloud 密文行不在 local UI 中暴露。
- `environmental_transient_92739.json` 保存一次未绑定 AXWindow 的环境重试；替代直启 PID 92833 成功，未被作为替代旧窗口或正向重用。

## P2-001

从已持久化 local 模式真实点击 Cloud radio 后，UI 显示 Cloud、已掩码 API Key 和“删除已保存 API Key”，但不先保存 Cloud 配置时，删除请求被 backend 以 `credential_mode_rejected` 拒绝。凭据行未删除、未触网，故为失败关闭的 P2 而非 P1；但它使可见用户控制与实际模式状态不一致。完整重现和修复方向见 `P2-001_mode_display_backend_divergence.json`。

## 清理与完整性

- `cleanup-wrong-marker-refusal.json`：将 marker 改为 0644 时，清理器拒绝，根仍存在。
- `cleanup-correct-marker-validation.json`：恢复普通 0600 marker 后验证成功。
- `cleanup-correct-marker-result.json`：仅精确授权根被清理，之后根不存在。
- `candidate-integrity-pre-cleanup.json` 与 `candidate-integrity-post-cleanup.json`：候选均为 80 文件、tree SHA-256 `805152496725b538b29f23a0f910f9a5ef78192301b90c2daa3141cbb5adf33f`，与固定 commit 字节一致；清理后 binary 不存在，符合精确清理预期。

## 后续边界

建议工程 Closure 仅修复 P2-001，并加入“local 已保存 → 切 cloud card → 直接删除 cloud credential”的 GUI 回归。修复后必须由新的隔离独立复评验证；本轮不得用于 Phase C、真实 Provider、真实数据、风险关闭或 PM 验收。
