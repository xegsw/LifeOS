# P3-110 UI 动态 Evidence 闭环

| ID | 实际操作 | 可观察结果 | 结构化结果 ID | 视觉／日志路径与 SHA-256 | 结论 |
|---|---|---|---|---|---|
| D-01 | 在实际窗口由 1280×949 拖拽到 700×760 | default 状态保持可见 | `geometry-nominal-700x760-default.json` | `screenshots/m008-700x760-default.png` / `73bdb87fe18d0f8604b755c0e400777273f5f4f9deff09e4d9dc50289e1a83f7` | PASS |
| D-02 | 点击“暂无可靠建议” | 空态、选择 Project 与 Inbox 入口可见；AX/CG 同报 700×760 | `geometry-no-suggestion-700x760.json` | `screenshots/m008-700x760-no-suggestion.png` / `7465415429facce0b1999ae5ab3d0e1f9eaf69505ed9dbb4836b892abbfb3bf1` | PASS |
| D-03 | 点击“权限受限与离线”，再滚动到底 | 受限说明、捕获区可达；AX/CG 同报 700×760 | `geometry-restricted-700x760.json` | `screenshots/m008-700x760-restricted-scrolled.png` / `6d01a241a8a85a1aa3bc4b95be1314776e83040a9ddbdbadebe1cc76a46acbbc` | PASS |
| D-04 | 名义 DB 首次点击“明确保存固定非敏感文本” | UI 仅在后端保存后显示成功 | `snapshot-nominal-after-first.json` | `screenshots/m009-first-capture.png` / `1103b3430846feef26ea11898f235b766829c41e540b90ff6c006a4fb3adc27c` | PASS |
| D-05 | 点击“重复同一幂等保存” | UI 披露幂等重复，record=1/audit=2 | `snapshot-nominal-after-repeat.json` | `screenshots/m010-repeat.png` / `f64a4fc2e7e991b26b3b6d0a3d2517808fad1b8d842da72f9c2eadd5bf15f255` | PASS |
| D-06 | 点击“验证同 key 异文本阻断” | UI 显示 `idempotency_conflict`，DB/audit 未变 | `snapshot-nominal-after-conflict.json` | `screenshots/m010-conflict.png` / `63efc21cb9d33a2158b58febfabfe4b888ddbe1e9eef5cb9a9a671baf7c5e014` | PASS |
| D-07 | 有 sentinel 时点击“验证注入失败” | UI 显示 `injected_atomic_failure`，sentinel/DB/audit 不变 | `snapshot-nominal-after-sentinel-failure.json` | `screenshots/m010-sentinel-failure.png` / `ae3deedcfd0980e2a36e46a89076a5a989e3444f35db20eb449227cb95e9fd23` | PASS |
| D-08 | 以 `super+r` 刷新实际 app | 后端权威记录恢复，record=1/audit=1/sentinel hash 不变 | `snapshot-nominal-refresh-after-capture.json`、`snapshot-nominal-refresh-after.json` | `screenshots/m011-refresh-after.png` / `0d5beaeb4dfc3428b26e63b53143ee549203bf03835c6dca1f1531cf785c4d61` | PASS |
| D-09 | 三页往返后关闭并以同一名义 DB 重开 | 后端权威记录恢复且 record=1/audit=2 | `snapshot-nominal-after-reopen.json` | `screenshots/m011-reopen.png` / `172549bffda6a6f9084f3efc6f3862664d34ca45b47c498d830f41b2f92404b1` | PASS |
| D-10 | 点击 settings、search、AI confirm；检查附件/语音禁用 | UI 明示未启用；记录/audit 未变 | `snapshot-nominal-after-unimplemented-controls.json` | `screenshots/m012-search-ai-unimplemented.png` / `97872df27e71686fda38bc540f93c0c4f3588e086b6b3369b746666a214e2db6` | PASS |
| D-11 | 点击 unknown IPC 与 extra-field 诊断 | UI 分别报告 unknown deny 与路径/SQL/shell extra fields reject | `snapshot-nominal-after-ipc-negative.json` | `screenshots/m012-extra-field.png` / `190fe230e313e4fed59745cb75bc6053abbf5880ca6af6438593dca404c8758f` | PASS |
| D-12 | 内容篡改 DB 启动并尝试保存 | 无缓存/成功态，UI 报 `record_identity_rejected` | `negative-path-results.json` 与 `actual-app-tamper.log` | `screenshots/m014-tamper-capture-rejected.png` / `3ccd590aef14040b1d99a93d048a624cdf73fe14ee363a7f0bc99bc46f84e9f6` | PASS |
| D-13 | schema 篡改 DB 启动 | UI 报启动读取失败、未展示缓存成功态 | `schema-tamper-prepare.json`、`snapshot-tamper-schema.json` | `screenshots/m014-schema-tamper.png` / `f2e6c9d3bcf09e1ea6cb1725e46c3cda2113d6582b5b8babe82c7da9c12c494c` | PASS |
| D-14 | Tab 到 skip link，Enter 激活 | AX 焦点从 skip link 进入 main-content，scroll=0.1957774 | `a11y-raw-transcript.md`；`static-scan.json` confirms local-only app surface | `screenshots/m015-skip-focus.png` / `689ea47ecc68f276387b1451d7f258d27536f6f8ae87d7140d6cd844a5166614` | PASS |

说明：每行的“实际操作”均在本次 P3-110 wrapper 启动的候选中执行；未把刷新、可聚焦或历史图像当作动作替代。`defaults read -g AppleReduceMotion` 返回“键不存在”，故只记录当前未显式设置；应用披露为“系统未请求”。
