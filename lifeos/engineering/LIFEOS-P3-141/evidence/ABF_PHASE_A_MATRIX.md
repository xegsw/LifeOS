# LIFEOS-P3-141 Phase A ABF matrix

`PASS_SYNTHETIC_ONLY` 只表示该行的合成合同已复核，绝不是 ABF 最终 Pass、独立评审 Pass、真实 Pilot Pass、PM 验收、风险关闭、冻结或 Stage 结论。`PENDING_PHASE_B` / `PENDING_PHASE_C` 按合同保留为未通过。

| Row | Phase A status | Evidence / successful test | Boundary statement |
|---|---|---|---|
| ABF-M-001 | PASS_SYNTHETIC_ONLY | `source_lineage.json`, replay verifier | 12/12 fixed hashes、P3-140 79-file tree 与 candidate 79 files/20 IPC 均匹配。 |
| ABF-M-002 | PASS_SYNTHETIC_ONLY | `pilot_root_boundary.json`, `closure_real_root_requires_fresh_absence_and_owned_restart` | 首次仅 root/DB 均不存在；空目录、文件、link、sidecar、非普通/未知 DB 均写前拒绝。 |
| ABF-M-003 | PASS_SYNTHETIC_ONLY | `phase_gate.json`, receipt-enabled real test | 无 receipt 先于 root 解析失败；正确 receipt 可进入同一 candidate real-mode 合同但只在 fresh 临时子根验证。 |
| ABF-M-004 | PASS_SYNTHETIC_ONLY | `provider_activation.json`, loopback fixture tests | 显式 save → test → enable → synthetic send；四 profile 闭集。 |
| ABF-M-005 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, loopback request tests | 仅 selected Capture ref 进入 request-scoped fixture dispatch。 |
| ABF-M-006 | PASS_SYNTHETIC_ONLY | `content_exclusion.json` | scanner 0 hit，截图与 DB 均为明显合成夹具。 |
| ABF-M-007 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Memory/State tests | Original、Memory、State、Understanding 身份分离。 |
| ABF-M-008 | PENDING_PHASE_C | — | 七个真实用户日期不可在 Phase A 合成。 |
| ABF-M-009 | PENDING_PHASE_C | — | 真实 paired daily-fact 结果要求真实受控使用证据。 |
| ABF-M-010 | PASS_SYNTHETIC_ONLY | `minimal_disclosure.json`, `synthetic_behavior.json` | request-local refs、预算与不泄漏路径已测。 |
| ABF-M-011 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Today tests | 校正/拒绝只使相关候选切片 stale/recompute。 |
| ABF-M-012 | PASS_SYNTHETIC_ONLY | `actual_tauri_viewports.json`, Today tests | 真实 bundle 的固定合成 UI 与 request-local Health 移除无持久继承。 |
| ABF-M-013 | PASS_SYNTHETIC_ONLY | `synthetic_behavior.json`, Today safety tests | 高风险夹具仅给出保守、非诊断停止。 |
| ABF-M-014 | PASS_SYNTHETIC_ONLY | closure / Provider negative tests | 授权、stale、budget、DB、root 与 Provider failure 均在受保护写/dispatch 前关闭。 |
| ABF-M-015 | PASS_SYNTHETIC_ONLY | lifecycle tests, `real_mode_root_lifecycle.json` | 相同 request 返回既有结果不二次 dispatch；real root reopen 不二次写 capture 或发送。 |
| ABF-M-016 | PASS_SYNTHETIC_ONLY | `actual_tauri_viewports.json`, `real_mode_screenshot_identity_review.md`, `screenshots/real_mode_*` | 三个直接 launch PID 均对应同一 final bundle、一个原生窗口/HTML WebView 与 exact P3-141 title；图像人工确认无敏感内容。 |
| ABF-M-017 | PENDING_PHASE_C | — | 用户操作的非内容真实使用 receipt 不在本 Phase A。 |
| ABF-M-018 | PENDING_PHASE_B | — | 新鲜独立评审尚未开始。 |
| ABF-M-019 | PASS_SYNTHETIC_ONLY | `cleanup_and_retention.json`, cleanup tool | 只清理精确临时根；禁止 real target 未被访问或清理。 |
| ABF-M-020 | PASS_SYNTHETIC_ONLY | `FINAL_MANIFEST.json` | 非自引用 Manifest 列出本 Closure 及 pending 行。 |

工程门：所有 Phase-A-applicable 行 **Ready for Independent Review**；Phase B/C 行继续 pending。
