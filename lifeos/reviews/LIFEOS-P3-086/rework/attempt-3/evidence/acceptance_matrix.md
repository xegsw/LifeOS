# LIFEOS-P3-086 attempt-3 验收标准 → 独立步骤 → Evidence 矩阵

| 任务卡验收标准 | 独立步骤／反例 | 结果 | Evidence |
|---|---|---|---|
| 当前五项工程与 P3-082 历史资产 hash | 源、task-local 副本和历史只读文件重新 SHA-256 | Pass | `MANIFEST.md` |
| 新写独立 runner，且不复用执行侧测试 | 创建并在副本运行独立静态 runner | Pass，28/28 | `independent_static_runner.mjs`、`independent_static_results.json` |
| 新 Chrome 标签页 `file:` 预检 | `com.google.Chrome` 直接加载副本默认页 | Pass | `01-preflight-default.jpeg`、`operation_log.md` |
| 三页与显式本地导航 | 点击默认、无建议、受限／离线三态导航 | Pass | `dynamic_results.json` DYN-02、`06`、`08` |
| 空文本、确认、重复确认、失败披露 | 固定非敏感文本的正向与负向交互 | Pass | DYN-03 至 DYN-06、`02` 至 `04` |
| 两条无建议人工路径与离线受限 | 点击两条路径、核对 fail-closed 文案 | Pass | DYN-07 至 DYN-08、`06` 至 `08` |
| 刷新与关闭重开清除 | 确认后刷新；关闭再开新标签页 | Pass | DYN-09 至 DYN-10、`05`、`09` |
| 禁止能力关闭态 | 静态扫描 URL、网络、持久化、文件、Tauri/IPC、导出、同步、模型／第三方标识 | Pass | `independent_static_results.json` |
| 可复查视觉记录、日志与复跑说明 | Chrome 截图、结构化结果、hash、Manifest | Pass | 本目录 Evidence 文件 |
