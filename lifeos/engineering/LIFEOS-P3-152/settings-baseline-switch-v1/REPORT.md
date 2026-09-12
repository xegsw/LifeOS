# P3-152 设置恢复版安全切换

状态：切换完成，等待用户真实验证；整体不Complete，独立复评仍暂停。

授权：用户针对保留数据、凭据、草稿且正常关闭当前版的切换问题回复“打开修复版本”，由PM明确转达本次切换授权。

实时NSRunningApplication识别当前Credential Fix.app的可执行路径和bundle id，得到PID40787；正常terminate前再次核对身份，exited=true。随后精确旧/新实例及四个已知同根可执行路径均无运行实例，修复二进制hash校验通过，启动一次PID43099。固定启动状态controlled_conversation_started，原共享conversation.lock排他门禁有效；NS再次验证新路径和bundle id，activation_requested=true。

已打开：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Model Settings Restored.app

Binary SHA256：3a0f72dfca5caa27c013b1ae91a7aa455c45910c282acaff82c69e48df0127c4。

准确窗口名（由已绑定候选确认，未读取真实AX）：LifeOS P3-152 - Controlled Conversation。

未强杀、删锁、清理凭据/用户数据、读取真实AX/截图/DB/Keychain/来源正文。未代保存Key、测试/models、选择/启用或发送。草稿由原App正常退出及持久化机制保留；未读取正文作内容验证。

用户下一步：设置 → 模型设置 → 手动测试并读取模型 → 从返回列表确认选择 → 显式启用。若尚无凭据，由用户先在App内保存。真实结果仍未知，仅由用户报告成功或固定错误码，不需提供Key。

195项原工程Manifest再次校验通过；本次切换独立receipt，不修改原工程/历史。主责Codex切换执行；PM待用户结果验收。无新增授权要求。
