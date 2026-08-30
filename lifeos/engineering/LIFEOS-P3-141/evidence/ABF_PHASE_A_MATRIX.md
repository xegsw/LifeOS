# LIFEOS-P3-141 Phase A ABF matrix

`PASS_SYNTHETIC_ONLY` 只表示该行的合成合同已复核，绝不是 ABF 最终 Pass、独立评审 Pass、真实 Pilot Pass、PM 验收、风险关闭、冻结或 Stage 结论。`PENDING_PHASE_B` / `PENDING_PHASE_C` 按合同保留为未通过；Phase D/E 同样未启动。

| Row | Phase A status | Evidence / successful test | Boundary statement |
|---|---|---|---|
| ABF-M-001 | PASS_SYNTHETIC_ONLY | `attempt-8-rework/current_candidate_tree.json`, `source_lineage.json` | 固定输入 12/12、P3-140 79-file tree、current candidate 79 files/20 IPC 均匹配；current framed tree=`ffde1eaa…8d6ef`。attempt-6/7 与 attempt-8 pre-peer-ownership tree 值保留在失败历史。 |
| ABF-M-002 | PASS_SYNTHETIC_ONLY | `closure_real_root_requires_fresh_absence_and_owned_restart`, `closure_limit_file_type_and_database_boundary_fail_closed` | 首次仅 root/DB 均不存在；空目录、文件、link、sidecar、非普通/未知 DB 均写前拒绝；owned reopen 无重写。 |
| ABF-M-003 | PASS_SYNTHETIC_ONLY | `phase_b_receipt_gate_regression.json` (1 synthetic positive + 17 negative) | 旧环境字符串一律拒绝；`phase_c_real` 缺少未来独立、peer-worktree-owned、committed Pass receipt 时在 runtime-root 解析前失败。工程未、也不能生成可接受 receipt；实际 Phase-C build/launch 继续 Pending。 |
| ABF-M-004 | PASS_SYNTHETIC_ONLY | `provider_activation.json`, loopback fixture tests | 显式 save → test → enable → synthetic send；四 profile 闭集。 |
| ABF-M-005 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, loopback request tests | 仅 selected Capture ref 进入 request-scoped fixture dispatch。 |
| ABF-M-006 | PASS_SYNTHETIC_ONLY | final replay content scanner | scanner 0 hit；截图和 DB 均为明显合成夹具。 |
| ABF-M-007 | PASS_SYNTHETIC_ONLY | Memory/State tests; real closure 8/8 | Original、Memory、State、Understanding 身份分离；confirmed Durable Memory 仅允许 3，第4条写前拒绝且重启后仍生效。 |
| ABF-M-008 | PENDING_PHASE_C | — | 七个真实用户日期不可在 Phase A 合成。 |
| ABF-M-009 | PENDING_PHASE_C | — | 真实 paired daily-fact 结果要求真实受控使用证据。 |
| ABF-M-010 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, `synthetic_behavior.json` | request-local refs、预算与不泄漏路径已测。 |
| ABF-M-011 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Today tests | 校正/拒绝只使相关候选切片 stale/recompute。 |
| ABF-M-012 | PASS_SYNTHETIC_ONLY | `attempt-4-rework/health_ui_route.json`, five-field Health real closure, Today tests | `update_current_state` 写入 sleep range、energy 1–5、pain boolean、L/M/H load、available time；受控 real-mode UI 使用唯一授权 fixture source 并通过 SQLite → Today → feedback；Health 移除不跨 request 继承。 |
| ABF-M-013 | PASS_SYNTHETIC_ONLY | five-field Health real closure, Today safety tests, `attempt-4-rework/health_ui_route.json` | 不接受自由文本、非法值、非法来源或医疗诊断；高风险夹具仅给出保守、非诊断停止。 |
| ABF-M-014 | PASS_SYNTHETIC_ONLY | closure / Provider negative tests | 同日第2条、总第15条、Memory第4条、Health 非法值、授权、stale、budget、DB、root 与 Provider failure 均在业务写/dispatch 前关闭。 |
| ABF-M-015 | PASS_SYNTHETIC_ONLY | synthetic lifecycle 48/48; real closure paths | 7–14 day Work trial 的每天最多1条、总数14可重启审计；相同 request 不二次 dispatch，owned reopen 不二次写 capture 或发送。 |
| ABF-M-016 | PASS_SYNTHETIC_ONLY | `attempt-8-rework/actual_tauri_viewports.json`, three `*_native_ax.json`, `manual_screenshot_review.md`, `ax_helper_counterexamples.json` | 当前 synthetic-review bundle 的三个 fresh direct PID 均在 exact-title 唯一 AXWindow 下发现原生 `AXWebArea`；helper 拒绝 window-only 与 `AXHTMLContent`。receipt 在 set_size 后 220ms + 3 个稳定样本写入，desktop 诚实记录 host-clamped 1280×949。不能代替未来独立 Pass receipt。 |
| ABF-M-017 | PENDING_PHASE_C | — | 用户操作的非内容真实使用 receipt 不在本 Phase A。 |
| ABF-M-018 | PENDING_PHASE_B | — | 新鲜独立评审尚未开始。 |
| ABF-M-019 | PASS_SYNTHETIC_ONLY | attempt-7 final cleanup receipt; `cleanup_temp.sh` | 只清理精确临时根，最终 postcondition 为根不存在；未访问或清理任何禁止目标。 |
| ABF-M-020 | PASS_SYNTHETIC_ONLY | regenerated non-self-referential `FINAL_MANIFEST.json` | Manifest 仅列 task-root 文件，排除自身，纳入 attempt-8 receipt-gate contract、16 负例、48/48 replay、历史与 pending 行。 |

工程门：所有 Phase-A-applicable 行 **Ready for Independent Review**；Phase B/C/D/E 均继续 pending，尤其 Phase-C real build/launch 只能等待未来独立 receipt。
