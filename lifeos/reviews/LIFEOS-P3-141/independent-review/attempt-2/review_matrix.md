# LIFEOS-P3-141 Phase B Mandatory Independent Review — Attempt 2 Matrix

## 范围与独立性

- 审查对象：本 worktree 的只读 `lifeos/engineering/LIFEOS-P3-141/candidate/`；全程以封签后的 before／after 快照确认未改动。
- 写入仅在本 Attempt 目录；动态夹具仅在批准的 task-local 临时目录。未启动 Phase C，未接触真实数据、既有 Pilot、真实 Provider、凭据或网络。
- 前次 Blocked attempt 仅作只读历史保全；本次没有复用其正结论。

| 检查项 | 独立证据 | 结果 |
|---|---|---|
| A→B→C 启动顺序与封签 | `precontact_seal.json`、`precontact_hashes.sha256`；三项封签 SHA 均匹配 | PASS |
| 固定输入 12 项 | `evidence/fixed_input_verification.json`：12/12 路径、字节数与 SHA-256 一致 | PASS |
| P3-140 79 文件 lineage | `evidence/p3_140_lineage.json`：79/79 文件与冻结清单逐项匹配 | PASS |
| 前次失败历史 | `evidence/prior_attempt_history.json`：11 个历史普通文件只读保全；历史结论仍为 Blocked | PASS |
| 候选不可变 | `candidate_before.json` 与 `candidate_after.json`：均为 79 文件、树 SHA `63878534…b55859` | PASS |
| 合成回归 | `independent_candidate_regression.json`：离线、合成 runtime，42/42 tests passed | PASS |
| 运行根反例 | `path_boundary_cases.json`：已有真目录仅成功；symlink、普通文件、缺失目录、词法非规范路径均失败关闭，临时夹具已删 | PASS |
| Phase B receipt 先于真实根解析 | `phase_c_pre_root_gate.json`：无 receipt 的 real 模式在 build 时以规定错误失败，未解析 runtime-root | PASS |
| Exactly 20 IPC | `static_contract.json` 独立解析 20；回归中状态闭集测试通过 | PASS |
| 四 Provider 闭集及单 Provider 生命周期 | `static_contract.json`、42/42 回归：固定 openai/anthropic/ollama/lm_studio；save→test→enable→send、首发锁、重启锁与拒绝路径均覆盖 | PASS |
| request-scoped 最小披露、预算与 Health 当次移除 | 42/42 回归；`semantic_mutation.json` 的预算变异被拒绝 | PASS |
| 身份分离、feedback stale/recompute、安全停止 | 42/42 回归；`semantic_mutation.json` 中 Health 身份、feedback stale 变异均被拒绝 | PASS |
| 失败写前关闭、request_id 与重启 | 42/42 回归；无 receipt gate 与路径反例均无成功写入 | PASS |
| 评审自有 semantic mutation | `semantic_mutation.json`：4/4 baseline 通过、变异后失败（Provider 闭集、预算、Health stop、feedback stale） | PASS |
| actual Tauri—desktop | `desktop_pid_bound.json` 与截图：直接返回 PID 30330；精确标题；1 AXWindow、1 个平台 AXWebArea WebView 表示 | PASS（见 P2） |
| actual Tauri—compact | `compact_pid_bound.json` 与截图：直接返回 PID 30350；精确标题；1 AXWindow、1 个平台 AXWebArea WebView 表示 | PASS（见 P2） |
| actual Tauri—narrow | `narrow_pid_bound.json` 与截图：直接返回 PID 30372；精确标题；1 AXWindow、1 个平台 AXWebArea WebView 表示 | PASS（见 P2） |
| 截图内容与内容排除 | 三图已人工目视；仅见固定合成 UI、合成引用和离线状态。`content_exclusion.json` 无凭据／私密内容标记 | PASS |
| 临时资源精确清理 | `evidence/cleanup_receipt.json`：literal 根为真目录、非链接，清理后不存在 | PASS |
| Phase C 专属 M-008 / M-009 / M-017 | 本任务范围外 | `PENDING_PHASE_C` |

## 评审发现

- P0：0。
- P1：0。
- P2：2。
  1. 候选自带 `replay_phase_a.sh` 假定本 worktree 有固定输入文件；本隔离 worktree 没有该副本，脚本不能作为本次正证据（`evidence/engineering_replay_path_diagnostic.json`）。本 Attempt 的 `replay_attempt_2.md` 和 review-owned runners 是可复跑入口。
  2. macOS Accessibility 对实际 Tauri WebView 暴露的角色为 `AXWebArea`（三次均为 1），而非字面 `AXWebView`；且未提供 `AXWindowNumber`。本次以直接返回 PID + 精确标题 + 唯一 AXWindow + AX 几何精确截屏绑定。原始角色和值均保留，未把它伪称为 `AXWebView`。
- Unknown：0（限 Phase B 合成范围）。
- Not Implemented：M-008、M-009、M-017 仅为 `PENDING_PHASE_C`，未作为本次缺陷关闭。
