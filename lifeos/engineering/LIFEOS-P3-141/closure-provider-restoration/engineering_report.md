# LIFEOS-P3-141 Provider Restoration Closure 工程报告

## 工程门结论

`READY_FOR_FRESH_INDEPENDENT_REVIEW`。本包仅恢复 P3-140 Closure-1 的五类 Provider profile 与 Adapter/mode mapping，并保持既有 P3-141 安全、Health/Work、Memory/State/Resolver、反馈、重启、receipt gate 与精确 20 IPC。旧 Phase-B Pass 已撤回；本报告不声称独立评审 Pass、PM 验收、风险关闭、真实 Pilot 或 Phase C 授权。

## 已实现的 Provider delta

- profile 闭集为 `OpenAI`、`Anthropic`、`Ollama`、`LM Studio`、`Custom OpenAI-compatible`；没有新 enum 或 IPC。
- `CustomOpenaiCompatible` 在 Cloud 和 Local mode 均有明确 mapping，并以 OpenAI-compatible `/v1/models` 与 `/v1/chat/completions` 合成 loopback 协议实现。
- Cloud UI 明确显示“DeepSeek、Kimi 或 OpenAI-compatible 服务”；Local UI 保留“本地兼容服务”。DeepSeek/Kimi 没有成为独立 Provider。
- save→test→enable 是唯一启用链；首次发送后 profile 锁定；无 Custom fallback、第二 Provider、后台发送或网络访问。

## 验证摘要

- 离线 Rust 合成回归：`cargo test --bin lifeos-p3-141`，50/50 通过。结果、完整日志与动态用例名见 `evidence/test_result.json` 和 `evidence/cargo_test.log`。
- Provider 动态协议：既有四类 loopback Adapter 覆盖加上本轮 Custom OpenAI-compatible loopback 正例；Custom 覆盖错误 models envelope、错误 chat response、错误 mode 与未 test/enable 的顺序拒绝。详情见 `evidence/provider_protocol_dynamic.json`。
- Provider 状态机：本轮 Custom positive test 证明一次成功发送后锁定，并在锁定后拒绝改为 LM Studio；持久化、失败关闭与不重发由既有合成回归覆盖。详情见 `evidence/provider_state_machine.json`。
- actual Tauri：desktop、compact、narrow 分别由直接启动 PID 链接到唯一精确标题 AXWindow 与原生 AXWebArea。每个 receipt 与同 PID 的 AX 尺寸一致，三张截图都来自本轮启动且只含合成 UI。详情见 `evidence/actual_tauri_provider_viewports.json`。
- 20 IPC 与非 Provider 能力：状态契约测试和非 Provider 回归均通过，见 `evidence/non_provider_regression.json`。

## 边界与保留历史

唯一临时根为 `/private/tmp/lifeos-p3-141-provider-restoration-closure-v1`。所有 runtime、cargo target、bundle、loopback、PID、AX、收据和清理均限定在其中或本包 Evidence 中；无真实 Provider、网络、凭据、真实内容或被禁止目标操作。此前无效桌面抓取、辅助程序构建及日志包装错误均在 `evidence/failure_history/` 只读保留，未作为正证据。

复跑入口为 `zsh replay.sh`：它只在唯一临时根不存在时创建新的合成 runtime 与 cargo target，离线运行回归；actual-Tauri 与 Manifest 必须由新一轮 direct-PID 取证生成，不能复用本包截图或 PID。

## 严重度与后续

- P0：0
- P1：0
- P2：0
- Unknown：0（本 Closure 合同内）
- Not Implemented：0（本 Closure 合同内）

独立评审、PM 验收、真实 self-use／Phase C、D、E：`PENDING`，且不由本工程会话启动。
