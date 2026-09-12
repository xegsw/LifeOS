# 确认发送后的固定分支

用户只提供非内容事实：点击确认发送后报错。本包不含问题、截图、真实DB或响应。

|分支|隔离合成方法|ModelPort次数|固定结果|
|---|---|---|---|
|确认/令牌/版本重验|继承token、stale、credential revision反例|0|confirmation_rejected/context_stale等|
|确认前存储锁|独立SQLite连接BEGIN IMMEDIATE|0|confirmation_storage_failed；未消费令牌|
|凭据端口不可用|cfg(test)单次CredentialPort失败；持久旧密文|0|credential_unavailable；旧密文不变|
|生产响应解析|生产decode_chat_response接收合成非JSON/null/空content|1|provider_protocol/response_too_large；重启/重复确认不再发|
|模型调用后存储锁|测试ModelPort持有独立SQLite写锁再返回|1|response_storage_failed；重启outcome_unknown，不重发|
|结果事务写入失败|仅合成库derivations触发器RAISE|1|dispatch_outcome_unknown；无半条answer、草稿保留|

旧通用提示不能区分以上情况。特别是credential_unavailable来自本机凭据端口，不等于Provider拒绝Key；response_storage_failed是ModelPort调用后保存失败，也不证明Provider已经成功返回实际答案。

修正只把固定错误阶段显式化，保持原失败关闭、预算、重试和持久化语义。生产解析代码提取为无I/O函数，逻辑未放宽；fake lookup为cfg(test)，真实构建不可用。实际用户错误码仍未知，不能替用户选定其中一条根因，也不能自动真实重发。

C1早期216项包及P154原270项包保持只读。当前包是同一Closure内的确认后定向增量，不是新任务，不新增真实权限。用户需要在本版亲自完成一次披露确认后，仅反馈固定code或成功；因为原版把code隐藏且禁止读取真实日志，静态/合成无法恢复其实际错误。此前仅准备阶段的反例不能替代此确认后判断。
