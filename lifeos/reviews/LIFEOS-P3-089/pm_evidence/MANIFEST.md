# LIFEOS-P3-089 PM Evidence Manifest

- PM 独立静态复跑：退出码 `0`，`87 PASS / 0 FAIL`；命令和结果 hash 见 `verification.json`。
- 执行侧 Chrome `file:` Evidence：Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 的预检与动态／视觉矩阵为 `15 PASS / 0 FAIL`；PM 已抽查确认／恢复、失败清理、键盘焦点与窄屏快照。
- 完整性：P3-089 五项 source hash、P3-079／P3-087／P3-088 指定只读输入 hash以及 Manifest 列示结果 hash 均对齐；P3-089 runner 不与 P3-087 runner 相同。
- 本地预检：本地模型不可用，按规则跳过；报告路径见 `verification.json`。
- 本目录仅含 PM 验收证据；未覆盖执行侧或历史资产。
