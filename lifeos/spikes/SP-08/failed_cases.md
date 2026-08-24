# 失败样例与降级语言

| 机器状态 | 校验行为 | 用户可理解语言 |
|---|---|---|
| checksum mismatch | 拒绝该包 | 文件内容与清单不一致，可能已损坏或被修改 |
| content file missing | 拒绝或明确部分恢复 | 清单引用的文件缺失，未静默跳过 |
| broken reference | 拒绝关系恢复 | 来源或证据关系不完整，需要修复导出包 |
| incompatible manifest | 拒绝导入 | 此导出包版本当前不受支持，不承诺猜测转换 |
| restriction note missing | 拒绝导入 | 权限 / 删除控制信息不完整，无法安全恢复 |
| external pointer only | 部分导出 | 已保留来源指针，但许可不允许包含外部全文 |
| deleted / revoked | 只保留控制说明 | 内容已停止使用，旧包不会将其恢复为活跃正文 |
| source disconnected | 只恢复未授权指针 | 来源已断开；不会自动重新连接或授权 |
| evidence invalid | 保留确认历史，退出活跃证据 | 原决定 / 行动历史仍在，但证据已不可用，需要复核 |
| existing original differs | 保留目标原文并建冲突分支 | 已有原文未被覆盖；发现一个需要处理的冲突版本 |

这些是 Spike 状态语言建议，不是正式 UI 文案。

