# B阶段配置读取精确差异（待批准，不执行）

provider_store.rs的provider_profile只保存底层配置及加密引用；当前用户已测试、选中和启用状态权威是conversation.sqlite的sources._provider_lifecycle，Settings配置为sources._settings_catalog。原B权限不足以读取这两个固定行。

拟新增：Host以SQLITE_OPEN_READ_ONLY | SQLITE_OPEN_NOFOLLOW、query_only，只对固定conversation.sqlite执行SELECT body FROM sources WHERE id=?，参数仅上述两个固定常量；禁止调用通用snapshot/list/Store::open，不持有写锁、不读取其他行。单行限额、严格JSON字段与旧profile/credential/catalog revision关联；模型必须启用且出现在既有测试目录。全部值只在Host内存使用，不输出Agent/Evidence/日志。仅存非敏感配置指纹用于批次不变性检查；不复制DB、密文或密钥，不更改配置。确认前和执行前重核变化并停止批次。

读取前仍须验证精确existing-only文件/marker安全属性；这不是读取许可。当前online配置入口明确失败online_configuration_not_authorized；A只用隔离合成配置。PM已要求等待用户批准此增量。
