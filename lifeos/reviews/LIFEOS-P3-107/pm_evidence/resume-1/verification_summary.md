# LIFEOS-P3-107 PM Evidence｜resume-1

- 正确配置与新会话成立：`gpt-5.6-terra + xhigh`；session ID `01a02ef2-ac6e-7971-b1a6-6c5a40933725`。独立测试设计 SHA-256 有效，mtime 早于 runner 与结果。
- PM 独立复算：固定输入 17/17、P3-106 Engineering Manifest 325/325、P3-107 resume Manifest 13/13；离线 locked test/build/Tauri build 三项退出 0；静态 8/8；固定三态视觉 3/3。
- `PM-P3-107-R1-IND-01`／P0：`independent_runner.py` 第 137 行只排除 `target` 后复制整个 P3-106 树。PM 仅按文件名／类型检查确认 work-r1 与 work-r2 均包含 `evidence/rework-1/tools/` 的 13 个提交工具；Review、交付物和 Manifest 却声明未复制提交 runner／Evidence。违反独立性与 Evidence 诚实合同。
- `PM-P3-107-R1-GOV-02`／Unknown：固定 P3-104 Engineering Manifest 记录 PM Review 更新前 hash `da83…`，当前 Review 为 `8d888…`；当前字面 no-bad 复算必然失败。要使后续任务可 Pass 必须时间化 M-003 或建立新固定快照，属于实质修改 ABF，不能在 P3-107 内继续。
- `PM-P3-107-R1-EV-03`／P2：final verifier 文案称剩余两条路径，但同文件 ledger 与 PM lstat 均为三条。
- 实际 app 动态 M-007–M-014 与清理 M-016 未完成；当前残留三个 ABF allowlist 精确目录。PM 未删除，等待用户明确确认精确清理；禁止 broad cleanup。
- PM 调整计数：P0=1、P1=0、P2=1、Unknown=1、Not Implemented=9。没有确认 P3-104/P3-106 候选缺陷。
- 治理结论：`Closed — Acceptance Not Met / Frozen ABF Conflict`。正式 Rework 记 1/2，但因需要实质修改 ABF，不得继续同任务 resume；若用户采纳并授权，应新建 P3-108 与新 ABF。
- 本地预检跳过：本轮涉及 P0 独立性、实际 Tauri 控制、本地删除残留与 ABF 终止判断，本地模型不得代判。
