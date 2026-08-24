# LIFEOS-P3-071 PM Replay Evidence Manifest

- 复跑方式：在新建临时副本中复制 P3-070 与 P3-071 工程目录；原工程及其 Evidence 未写入。
- P3-071 独立 runner：退出码 0，13 PASS / 0 FAIL。
- P3-070 原始回归入口：退出码 0，8 PASS / 0 FAIL。
- 复核的 P3-070 `src/export_plan.py` 与四项 Evidence SHA-256 均与 P3-071 Manifest 的 before/after 值一致。
- 结构化摘要：`pm_replay_summary.json`。
- 结论范围：只证明合成计划／本地回执与关闭态；没有真实文件、路径、网络、Tauri/IPC、Vault、云、同步、多设备、L3 或外部用户动作。
