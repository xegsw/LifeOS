# 供 PM 向用户说明的单项只读元数据差异（未执行）

唯一目的：对当前选中 Provider 对应的那一个已有 AEAD 材料条目，判断解密访问控制是否要求用户交互；不读取材料或 API Key，不改权限，不恢复后台、不运行模型。

定位：仅在同一完整 B Host 内，沿已准许的固定配置获取当前 credentialRevision/keyReference，并由既有 reference_lineage 映射固定 service；这些值只在进程内使用，不回传、不写文件。只查当前默认钥匙串对象中的精确 generic-password service+account，不使用全搜索列表或宽查询，不读取其他条目。不将任何定位值传入 shell 参数。当前实现必须另做审核和纯假对象测试后才可启用；没有现成可执行诊断入口。

读取机制：不用现有会返回材料的 Rust find_generic_password 包装；专用 FFI 将 SecKeychainFindGenericPassword 的 passwordLength 和 passwordData 都设为 NULL，仅返回 itemRef。Apple 明确支持此用法。以只读 SecKeychainItemCopyAccess、SecAccessCopyACLList、SecACLCopyAuthorizations、SecACLCopyContents 检查该条目解密相关 ACL；其他 ACL 类型不展开。仅保留固定授权标签类别、prompt selector 数字/是否需密码提示、受信应用计数及列表是否为空，不输出 description、应用路径、签名blob、account/service/reference或条目其他属性。未知类型只输出 unknown。不得调用 CopyData 导出可信应用内部数据。

进一步比较：第一轮不枚举/输出受信应用身份，也不试探其他 App。若仅计数/提示位仍不足，需另向 PM 说明是否需要对当前与已知旧签名 App 做布尔匹配；本差异不含该操作。

边界：一次单项只读；非交互、5秒上限，忙/超时/系统要求交互立即停止，不能解锁/改锁状态或弹密码框重试。无 add/update/delete/setAccess/setContents/setTrust/export；不缓存解密材料；不发网络；不修改现有 grant/预留/失败历史；返回字段白名单且不含秘密或自由文本。条目不存在或不唯一可验证时停止，不做兜底搜索。

允许输出仅：stage、numeric OSStatus、itemLocated布尔、decryptAclCount、trustedApplicationCount（必要时按解密ACL逐项计数）、trustedListEmpty布尔、promptSelector数字、requiresPassphrase布尔或unknown。结果只写本任务 evidence。前提为 PM 向用户一次解释并取得明确批准；当前尚未批准或执行。

依据：[Apple API](https://developer.apple.com/documentation/security/seckeychainfindgenericpassword%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_1)、[ACL API](https://developer.apple.com/documentation/security/access-control-lists?changes=lat_1_1%2Clat_1_1)。本提案不宣称元数据读取完全无需系统授权；遇到系统拒绝就保留结果停止。
