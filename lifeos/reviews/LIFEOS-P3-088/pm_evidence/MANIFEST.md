# LIFEOS-P3-088 PM Evidence Manifest

- PM 复跑本轮独立 static runner：退出码 `0`，`53 PASS / 0 FAIL`；命令和结果 hash 见 `verification.json`。
- 独立性：runner 与 P3-087、P3-085 执行侧 runner 均不相同；其 import 仅为 Node 内置 `fs/path/crypto`。
- Chrome `file:` Evidence：Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 的预检与动态矩阵为 `13 PASS / 0 FAIL`；PM 已抽查键盘焦点、失败披露、缩放及关闭重开快照。
- 完整性：P3-087 当前五项 source hash、P3-085 五项历史只读 hash及本轮 Manifest 列示 Evidence hash 均对齐。
- 本地预检：本地模型不可用，按规则跳过；报告路径见 `verification.json`。
- 本目录不覆盖独立评审或历史 Evidence。
