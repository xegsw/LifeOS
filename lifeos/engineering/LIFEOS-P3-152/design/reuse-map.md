# P3-152 最小复用表（工程代码核对）

151 FINAL_MANIFEST178项及外部报告复算通过后保全，不修改151 App或根。152只在新工程根与新synthetic根实现/测试。

| 层 | 直接输入 | 复用/最小增量 |
|---|---|---|
| UI/Flow | 151 health_ui / health_conversation / health_context，116/142基础CSS | 保留自然输入、草稿队列、迟到取消、来源折叠、有限Context；真实发送增加实际正文预览与用户确认，不由Agent代点 |
| Host | 151 health_conversation_host | 复用9表、原文/状态/候选身份和bounded refs；新增preview/确认消费状态的事务语义，关键IPC另交PM批准 |
| 来源 | 150 R1只读reader +149closure3语义 | 只读健康sqlite三指标，有限相关日期/来源组；保留unknown/estimated/offset、不强行聚合多来源；禁止源库写入 |
| ModelPort | 148 model_port / provider_transport | 重用generate_with_receipt接收边界与DeepSeek固定官方域、错误分类/无重定向/无日志；152不接models()/测试连接路径 |
| CredentialPort | 148 secure_credentials / provider_store | 复用AES-256-GCM、Keychain密钥材料、encrypted envelope/AAD/revision/失败关闭；真实读写目标尚未授权，不调用 |
| 设置 | 148 config字段与服务目录 | 保留模型选项及本地选择，不固定新模型名、不自动联网列模型。其余Provider目录明确本任务不可发送 |
| Evidence | 151精确synthetic PID/标题/几何guard | 全部动态测试/截图限定152 synthetic；打开real后禁用Agent AX/截图/真实正文/内容hash |

已确认健康源只读及逐次DeepSeek发送，尚未确定凭据配置来源和真实会话目标，见real-target-proposal.md。开发仅以synthetic Ports验证这条链路。真实模式不以环境变量任意路径切换，目标授权后固定编译合同。
