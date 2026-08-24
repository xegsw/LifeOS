# LIFEOS-P3-091 PM Evidence Manifest

- PM 复跑时间：2026-08-21。
- 命令：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node lifeos/engineering/LIFEOS-P3-091/tests/static_check.mjs lifeos/engineering/LIFEOS-P3-091`。
- 结果：退出码 0；`97 PASS / 0 FAIL`。逐项结果：`lifeos/reviews/LIFEOS-P3-091_pm_static_results.json`。
- Evidence hash：执行侧 Manifest 列出的 15 项非自指文件 SHA-256 已复算一致。
- 视觉抽查：预检、确认恢复、失败清理、受限离线和窄屏快照存在，内容为固定非敏感合成演示。
- 完整性缺口：动态 JSON 与操作日志只记录 refresh 后清除；没有 Chrome 关闭标签后重新打开的逐项结果或视觉记录。键盘项仅称 AX 树暴露可聚焦控件，没有实际 Tab／Enter 交互记录。两项均为任务卡与 P3-074 包内自检要求的动态验证，不能由静态 runner 或 AX 暴露替代。
- 本地预检：执行侧已完成本地预检；PM 本轮不将其作为 P0 验收依据。
