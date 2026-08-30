# LIFEOS-P3-141 Phase A synthetic engineering report

## 工程门结论

**Phase A Ready for Independent Review**。这是受控合成工程结论，不是独立评审 Pass、真实 Pilot Pass、PM 验收、风险关闭、Frozen 或 Stage 推进。Phase B 独立评审与 Phase C 真实使用均未开始。

## 实现事实

- 以 P3-140 的 79 文件候选为唯一基线，修改仍限候选内 6 个允许文件；当前候选保持 79 文件。
- IPC 仍为恰好 20 项；未新增 IPC。
- Provider 闭集为 OpenAI、Anthropic、Ollama、LM Studio。Phase A 的唯一可派发路径是 task-local loopback fixture；Custom、第二 Provider、fallback 和后台发送均没有实现路径。
- Provider 明确执行保存 → 测试 → 启用 → 发送。首个成功合成发送后持久化锁定 Provider；切换被 `provider_locked_after_first_send` 拒绝，重启后锁仍存在但不会自动启用或重发。
- Phase C 编译入口在无独立 Phase B receipt 时由 `build.rs` 在任何 runtime-root 检查前拒绝；即使未来 receipt 存在，Phase A runtime 仍以 `phase_c_operator_only` 停止。
- P3-139 Resolver 与 P3-140 Today/Feedback/Health 路径保留。最小 Context、身份分离、Health request-local 移除、非诊断安全停止、stale/recompute、写前失败关闭、重启及不复用 request id 都由合成测试覆盖。

## 验证摘要

- 固定输入：12/12 SHA-256 匹配；P3-140 基线为 79 文件、树 SHA-256 `6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e`。
- 预接触封存：`test_design.md` 和 `write_allowlist.md` 的 SHA-256 在接触候选前写入 seal，复核未变。
- 最终可复跑合成命令：`sh lifeos/engineering/LIFEOS-P3-141/tools/replay_phase_a.sh`；最终结果为 Rust 42/42 passed。
- Phase gate：无 receipt 的 `real_self_use` offline build 返回 101，报出 `phase_b_independent_pass_required before runtime-root inspection`。
- actual Tauri：桌面、compact、narrow 三次独立启动均以各自返回 PID 绑定 1 个 `AXWindow` 和 1 个 `AXWebArea`；桌面档通过原生 AX 执行了 Health 本次移除和失败关闭，界面显示 `context_budget_rejected`。
- 内容排除 scanner：禁止 Pilot 标记 0 命中；Evidence 只记录虚构夹具和非内容状态。
- 清理：唯一临时根已精确移除；任何真实目标均未访问或清理。

完整逐行状态见 [ABF_PHASE_A_MATRIX.md](evidence/ABF_PHASE_A_MATRIX.md)。实际 GUI 记录见 [actual_tauri_viewports.json](evidence/actual_tauri_viewports.json)。

## 问题与保留项

- P0: 0
- P1: 0
- P2: 1 — 提供的 Rust 工具链没有 `cargo-fmt` 组件，格式检查未执行；离线编译和 42 个测试均通过，未影响候选行为或 Evidence 边界。
- Unknown: 0（仅限 Phase A 合成合同）。
- Not Implemented / PENDING：ABF-M-008、M-009、M-017 为 `PENDING_PHASE_C`；ABF-M-018 为 `PENDING_PHASE_B`。这些不是失败，也不得被本报告表述为已通过。

## 交付与后续关卡

- 测试与复跑入口：[tools/replay_phase_a.sh](tools/replay_phase_a.sh)、[tools/verify_phase_a.py](tools/verify_phase_a.py)。
- Evidence 根：[evidence](evidence)。
- 后续只可由 PM 创建新鲜隔离的 Phase B 独立评审；本工程会话不创建评审、不接触真实 Pilot，也不更新 PM 账本、风险、冻结或 Stage。
