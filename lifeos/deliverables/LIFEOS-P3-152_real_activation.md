# P3-152 真实适配与安全切换

状态：In progress，技术接线与单实例启动完成，等待用户手动操作结果及PM验收；风险L3，独立评审继续暂停。

用户已授权集中真实合同及Agent正常退出旧App。精确旧实例正常退出，新统一真实App已启动（PID39248）；未自动扫描、导入、重试或发送。65 Host、23集成、17 UI合成检查通过，旧1092项文件hash一致。真实正文/凭据未进入Agent或Evidence。

完整报告：[REPORT.md](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/real-activation/REPORT.md)。检查点：[checkpoint.json](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/real-activation/checkpoint.json)。待用户从设置→数据与隐私手动连接资料目录/导入健康文件，并逐次确认来源对话；只需反馈成功或错误码，不提供正文/Key。

需要PM决策：本增量验收；实际用户结果尚未知，当前不报Complete。
