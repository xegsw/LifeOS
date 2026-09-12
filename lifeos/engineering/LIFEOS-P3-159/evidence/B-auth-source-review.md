# P3-159 后台认证失败：源码与公开文档核对

状态：只读调查；无新 App 启动、凭据读取、ACL 枚举、签名修改或 POST。B 保留 generation5、analysis5、response0、POST0、暂停。

## 已确认

- 当前收据 single_item_read/-25293 表示实际失败在 `SecKeychainFindGenericPassword`，此前获取默认钥匙串和进程交互策略调用没有返回失败。未到 AES 解密或模型调用，不是模型服务拒绝。
- Cargo.lock 固定 security-framework 3.5.1（checksum b3297343eaf830f66ede390ea39da1d462b6b0c1b000f420d0a83f898bbbe6ef），security-framework-sys 2.15.0 的 base.rs 将 -25293 定义为 errSecAuthFailed。[Apple 定义](https://developer.apple.com/documentation/security/errsecauthfailed)是授权和/或认证失败，不能进一步唯一推导密码、ACL或操作系统版本原因。
- provider_store 的手动与后台路径均读取既有固定配置 envelope，使用相同 lineage/service/reference/AAD 解码；区别是后台选择 NonInteractiveCredentialPort。两条路径均调用默认钥匙串的 find_generic_password，没有从签名钥匙串自动改选目标条目的逻辑。
- 固定依赖 os/macos/passwords.rs:96/194 最终传递一个明确默认钥匙串对象、service/account，以及非空 passwordLength/passwordData 来读取材料。不是遍历所有钥匙串，不是 SecItem 的 Data Protection 查询。
- 非交互 RAII 调用 SecKeychainSetUserInteractionAllowed(false)，仅原状态 true 时创建依赖的恢复 guard，Drop 恢复 true；原状态 false 不强开。现有互斥覆盖手动和后台读取，不添加信任或修改条目。
- [Apple FindGenericPassword 文档](https://developer.apple.com/documentation/security/seckeychainfindgenericpassword%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_1)说明条目访问控制不允许解密时可返回 errSecAuthFailed。因此条目访问控制是有根据的调查方向，而不是已证实根因；单次手动成功不能证明未来免交互读取许可。
- PM 报告新旧公开签名指定要求互相验证均 exit0；该 PM 观察未在本增量重跑。leaf/root 文本差异不能单独证明不兼容，不建议盲改签名。

## 未确认与下一步

当前源码和公开资料不能唯一解释目标条目为什么拒绝本次非交互解密。既有协议不能授权枚举真实 ACL；没有执行任何此类读取。若 PM 决定继续定位，可审议同目录 B-single-item-metadata-scope.md 中的精准只读差异。此方案不是执行授权，也不保证能够定位全部系统策略。

语音的离线接线与该凭据依赖分离；现有禁用态与 fake 测试不构成真实音频授权或声学通过。
