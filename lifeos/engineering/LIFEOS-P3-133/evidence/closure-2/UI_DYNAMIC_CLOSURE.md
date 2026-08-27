# P3-133 Closure-2｜real-mode actual Tauri 动态闭环

本表只记录固定合成夹具的非内容状态；不保留输入正文、正文 hash 或包含正文的截图。真实自用未运行。

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| D-133-C2-01 | fresh real-mode UI（0/3）输入合规非空夹具 | Capture 保存后 UI 显示 1/3 | ACT-C2-01 | `actual-tauri.json` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-02 | 尝试第 201 个 Unicode 字符 | textarea 写前限制为 200；Rust 201 请求写前拒绝 | ACT-C2-02 | `input-limit.json`；`test-logs/cargo-test-real-mode.log` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-03 | 合规 Capture 达 3/3 | 第四条入口在写前不可用，非内容状态保持 | ACT-C2-03 | `input-limit.json`；`failure-sentinel.json` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-04 | 明确确认 Context | Confirmed link=1，Action=0 | ACT-C2-04 | `lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-05 | 明确接受 Candidate | Action=1/open=1，Today Focus=1 | ACT-C2-05 | `lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-06 | 关闭并重开 bundle | 3 captures 与 1 open Action/Focus 一致 | ACT-C2-06 | `actual-tauri.json`；`lifecycle-noncontent.json` | 由 Final Manifest 覆盖 | PASS |  |
| D-133-C2-07 | real-mode Understanding | model disabled，Understanding=0，no noticed | ACT-C2-05 | `privacy-taint.json` | 由 Final Manifest 覆盖 | PASS |  |
