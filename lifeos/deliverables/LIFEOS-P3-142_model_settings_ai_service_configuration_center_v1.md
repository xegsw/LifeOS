# LIFEOS-P3-142｜模型设置与 AI 服务配置中心 V1｜执行报告

## 任务信息

- 任务：`LIFEOS-P3-142_model_settings_ai_service_configuration_center_v1`
- 执行角色：Codex（Engineering）
- 风险等级：L2
- 状态：**Engineering Complete — Awaiting PM Acceptance**
- 当前检查点：[checkpoint.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/checkpoint.json)

## 事实

- 已在独立候选目录实现合成离线的模型设置与 AI 服务配置中心：8 个 Cloud、4 个 Local Provider；模型选择、Capabilities、credential reference、连接测试、启用和 routing policy 均经既有 20 个 IPC 的严格版本化 DTO 完成。
- 已落实“一个主服务”、Cloud/Local 草稿隔离、Cloud 不自动兜底、Local 优先、自动切换默认关闭及保存前不成为活动服务。持久化仅含固定合成 credential reference，不含真实凭据。
- Rust 单元测试串行通过 **9/9**；离线合同检查通过 **15/15**，确认 IPC 数量为 20 且前后端无网络符号。`cargo fmt --all -- --check` 已通过。
- 已构建实际 macOS Tauri `.app`，并以每档直接启动 PID 绑定到标题为 `LifeOS · 模型设置（合成离线）` 的 AXWindow，再到 HTML/Tauri WebView 区域。三档均取得清晰、仅目标窗口的截图并完成视觉检查；此前已确认 Narrow 切换 Local 草稿时，已保存的 Cloud 主服务仍保持活动且草稿未生效。
- PM Closure Cycle 的 skip-link 缺口已关闭：链接保留在 DOM 中，默认安全移出视区；Desktop 与 Narrow 的 Tab 焦点态均在窗口内完整显示。修正后的三档 PID 为 53553／53600／53674，默认截图均无可见或裁切的 skip-link。
- 用户一次性授权的唯一网络动作已完成：官方 Rustup 仅为固定 `1.98.0-aarch64-apple-darwin` toolchain 安装 `rustfmt`；未更新 toolchain、Cargo.lock、依赖或系统包，未连接 Provider、模型或其他网络目标。
- 本 Closure Cycle 未发生任何网络访问；所有重跑均为 `--locked --offline` 或本机 Tauri 合成运行。
- 未接触 Pilot、真实 DB／文本、真实 Provider、API key 或环境凭据；未修改 P3-139、P3-140、P3-141 或其历史材料。

## 收口事实

Desktop `1036×768`、Compact `1160×768`、Narrow `700×760` 的当前截图均为清晰、仅目标窗口的原生 Evidence；旧缩略图已明确排除。三档视觉／可访问性检查已完成。

初次 format check 仅发现 `src/runtime.rs` 机械排版差异，已用 `cargo fmt` 收口；其后 format check、9/9 串行 Rust 测试、15/15 合同检查与任务根负例均通过。Manifest 工具曾因工程根解析为 `candidate/candidate` 而在读取前安全失败，已作两行路径修正并通过最终生成／验证；未改变运行时语义，无需重跑三档 GUI。

App、写入器均已停止，合成 SQLite 已关闭。marker-gated 唯一根 `/private/tmp/lifeos-p3-142-ai-service-config-center-v1` 已精确清理并验证不存在。

## 证据与交付物

- 候选与本地 CI 检查定义：[candidate](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/candidate)
- 静态合同报告：[static_contract_report.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/static_contract_report.json)
- Formatter 本机预检：[formatter_preflight.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/formatter_preflight.json)
- Rustfmt 联网操作记录：[rustfmt_installation.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/rustfmt_installation.json)
- 格式化后回归：[regression_after_rustfmt.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/regression_after_rustfmt.json)
- Skip-link Closure：[skiplink_closure.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/skiplink_closure.json) 与 [skiplink_regression.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/skiplink_regression.json)
- 原生 PID／窗口／WebView 绑定及截图排除记录：[native_window_evidence.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/native_window_evidence.json)
- 本轮 AX 明细：[ax-desktop-resume.txt](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/ax-desktop-resume.txt)、[ax-compact-resume.txt](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/ax-compact-resume.txt)、[ax-narrow-resume.txt](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/ax-narrow-resume.txt)
- Narrow Local 草稿隔离记录：[ax-narrow-local-draft.txt](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/ax-narrow-local-draft.txt)
- 非自指 Manifest：[FINAL_MANIFEST.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/FINAL_MANIFEST.json)（117 entries）与 [manifest_verification.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/manifest_verification.json)（0 errors）。
- 精确清理收据：[cleanup_receipt.json](/Users/xxe/.codex/worktrees/f987/No.2/lifeos/engineering/LIFEOS-P3-142/evidence/cleanup_receipt.json)。已构建 App 仅存在于该唯一临时根，随获授权清理一并移除。

## AC-01～AC-26 工程自检

| AC | 结果 | 核心 Evidence |
|---|---|---|
| AC-01 | PASS | 三档原生截图、AX 与 Settings Shell |
| AC-02 | PASS | 三档视觉检查；skip-link 默认隐藏、焦点态完整显示 |
| AC-03 | PASS | 中文文案与二级 Settings 导航 |
| AC-04 | PASS | 主服务 configured/unconfigured state |
| AC-05 | PASS | Registry：8 Cloud + 4 Local |
| AC-06 | PASS | Registry metadata 与 disposable provider mutation |
| AC-07 | PASS | 严格 DTO 正负矩阵 |
| AC-08 | PASS | metadata fixture/provider-name mutation |
| AC-09 | PASS | UI/AX walkthrough |
| AC-10 | PASS | Router 默认拒绝云端补齐 |
| AC-11 | PASS | Router 自动切换授权矩阵 |
| AC-12 | PASS | 视觉弱化的可选备用服务 |
| AC-13 | PASS | Advanced 默认折叠／自动 |
| AC-14 | PASS | UI/Runtime 零 SDK/SQL/网络/credential 直连扫描 |
| AC-15 | PASS | 合成引用持久化与重启恢复 |
| AC-16 | PASS | 固定非秘密夹具 redaction |
| AC-17 | PASS | 输入负例在持久化前失败关闭 |
| AC-18 | PASS | Cloud/Local 草稿与 active mode 隔离 |
| AC-19 | PASS | 20 IPC 精确清单与 schema mutation |
| AC-20 | PASS | P3-139/140/141 只读边界 |
| AC-21 | PASS | zero-network 静态合同 |
| AC-22 | PASS | PID 53553／53600／53674、AXWindow→WebView、三档截图与焦点态 |
| AC-23 | PASS | CI 检查、format、串行 Rust 9/9、离线合同 15/15 |
| AC-24 | PASS | checkpoint 暂停→定向恢复 |
| AC-25 | PASS | marker／wrong-marker／symlink／traversal 与 root absence |
| AC-26 | PASS | 非自指 Manifest 117/117、verifier 0 errors |

## 风险、关卡与 PM 决策

- P0：0；P1：0；P2：2（预 marker 构建缓存不作为正 Evidence；`rust-objcopy` 调试符号处理告警但 bundle 已成功生成）；Unknown：0；Not Implemented：0。
- Engineering 自检完成；任务未触发独立评审（未发生禁止边界接触）。本结论不等于 PM 验收、独立评审、风险关闭、冻结或 Stage 变更。
- **需要 PM 决策：需要 PM 验收，但不需要新的产品／架构／风险决策。** 当前候选 hash：`f56b359f4b37a79f5bf3639effbde96561097ea5f948d0d928e541c3a3c48e92`。
