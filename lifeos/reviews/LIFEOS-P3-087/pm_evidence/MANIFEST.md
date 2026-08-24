# LIFEOS-P3-087 PM Evidence Manifest

- PM 独立静态复跑：`verification.json` 记录的命令，退出码 `0`，`61 PASS / 0 FAIL`。
- 执行侧 Chrome `file:` 预检 Evidence：`lifeos/engineering/LIFEOS-P3-087/evidence/dynamic_results.json`，`12 PASS / 0 FAIL`；PM 已抽查键盘、失败清理与窄屏快照。
- 完整性：当前五项工程 source hash 与执行侧 Manifest 一致；P3-085 五项只读 hash 与既有记录一致。P3-087 runner 为本任务本地 runner，不与 P3-085 runner 相同。
- 本地预检：本地模型不可用，已按规则跳过；报告路径见 `verification.json`。
- 本目录仅含 PM 验收证据；未覆盖执行侧或历史 Evidence。
