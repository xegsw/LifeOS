# LIFEOS-P3-141 Phase A Closure engineering report

## 工程门结论

**Phase A Ready for Independent Review**。本 Closure 已修复 Phase-B intake 所报的同合同 P0：receipt-enabled `real_self_use` 现在进入同一候选 source/20-IPC 合同的 real-mode 代码；而无 receipt 仍在读取 runtime root 前失败关闭。结论只覆盖受控合成工程，绝非独立评审 Pass、真实 Pilot Pass、PM 验收、风险关闭、冻结或 Stage 推进。新的独立评审尚未开始，Phase C 未启动。

## 实现与验证事实

- 候选保留 P3-140 的 79 文件基线与恰好 20 IPC；当前树 SHA-256 为 `6a45b656a7bd1203485818872242d4ce2b9db572f197bec869356a6d807a87e1`。Provider 闭集保持 OpenAI、Anthropic、Ollama、LM Studio，测试的唯一派发端为 task-local loopback；没有 Custom、第二 Provider、fallback 或后台发送。
- `build.rs` 先验证 embedded Phase-B receipt，之后才读取 `LIFEOS_RUNTIME_ROOT`。缺 receipt 配合故意非规范 root 的 offline build 仍返回 101 与 `phase_b_independent_pass_required before runtime-root inspection`；正确 receipt 的同 source real build 运行 fresh-root / reopen 单测 1/1。
- real mode 首次只接收缺失 root 与缺失 `capture.sqlite`，应用在唯一临时根创建 DB 及严格 ownership/schema marker。已有空目录、预置 DB、未知文件、root/ancestor 链接、非普通 DB、未知 SQLite 与 sidecar 均在写前失败关闭；只允许候选已初始化且 marker/DB/权限/schema 均可验证的重开。单测同时验证 reopen 的读取不改变 DB，不重写 capture。
- 合成 replay 以显式 `--input-root` 支持隔离 worktree，已验证固定输入 12/12、P3-140 79/79 tree hash、candidate 79 files/20 IPC，并完成 Rust 43/43。Provider save → test → enable → loopback send、首次成功后的 profile lock、重启不自动 enable/dispatch、request-scoped 最小 Context、Memory/State/Understanding 身份分离、Today 反馈/Health 安全停止及失败原子性均保留。
- receipt-enabled real-mode actual Tauri bundle 只在临时根和固定合成 fixture 下三次启动：desktop PID 49613、compact PID 49643、narrow PID 49714。每个 PID 均由直接 `ps` 定位到本次 bundle executable；原生可访问性适配器对同一 bundle 返回 1 个标准窗口与 1 个 HTML/WebView，标题与 HTML title 都是 `LifeOS · P3-141 Controlled Pilot Candidate`。三张人工可见标题的无敏感截图位于 `evidence/screenshots/real_mode_*_redacted_state.jpeg`。
- 这三次 GUI 启动的 Today 合成请求各有新 request id；数据库没有 capture、Understanding、Provider 设置或 Provider/网络 dispatch。重启不复用 request id，且根级 fresh/reopen 单测证明相同 capture 不会被再次写入。没有真实内容、Health、凭据、真实 Provider 或网络进入测试。

## Evidence 与保留项

- 逐行状态：[ABF_PHASE_A_MATRIX.md](evidence/ABF_PHASE_A_MATRIX.md)。real-mode root lifecycle：[real_mode_root_lifecycle.json](evidence/real_mode_root_lifecycle.json)。actual-Tauri：[actual_tauri_viewports.json](evidence/actual_tauri_viewports.json) 与 [real_mode_screenshot_identity_review.md](evidence/real_mode_screenshot_identity_review.md)。
- 失败历史保留在 [failure_history.md](evidence/failure_history.md)：包括此前标题冲突截图、Phase-B intake、错误 receipt、错误 exact test filter、首次 real-mode fixture 缺失和系统拒绝 terminal AppleScript AX 的尝试；它们均不作正 Evidence。
- P0: 0；P1: 0（一次无敏感外部 verifier 临时输出已立即移入唯一临时根并精确清理，完整保留为失败历史，非开放项）；P2: 1（供应工具链没有 `cargo-fmt` 组件，格式检查未运行）；Unknown: 0（限本 Phase-A 合成合同）；Not Implemented：新的独立 Phase-B 评审，以及 Phase-C 受控真实使用。

## 后续

复跑入口为 [tools/replay_phase_a.sh](tools/replay_phase_a.sh)（要求显式或默认的 workspace `--input-root`）和 [tools/verify_phase_a.py](tools/verify_phase_a.py)。唯一临时根最终由 [tools/cleanup_temp.sh](tools/cleanup_temp.sh) 精确清理。PM 的下一步只能是新鲜隔离的独立评审；本工程会话没有启动真实 Pilot，也没有触达任何禁止目标。
