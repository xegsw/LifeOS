# 合并单项元数据提案：API可行性与假对象测试设计

状态：仅源码/SDK/Apple公开代码调查，无真实元数据读取，无新诊断入口。PM合并提案取代旧分两次提案；此调查不扩大提案权限。

## 精确结论

1. 只取itemRef不取密码数据：公开SecKeychainFindGenericPassword支持passwordLength/passwordData均NULL，不能复用security-framework返回材料的便利包装。
2. 解密ACL数量、授权标签、提示位与trusted application对象数组：公开SecKeychainItemCopyAccess/CopyACLList/CopyAuthorizations/CopyContents可提供。SDK中CopyContents的description出参为nonnull；Host须接受不透明CFString引用并立即CFRelease，不能转换字符串/输出。若“不读取description”被解释为连不透明返回引用也不接收，则公开该接口不满足；当前提案写的是“不输出”，可做到不转换/不导出。
3. 空列表和不限应用必须按返回NULL与空CFArray区分，不能仅count=0合并；不支持/复杂ACL保持unknown，不为凑布尔结论降格。
4. 当前SDK SecTrustedApplication.h公开接口只有GetTypeID/CreateFromPath/CopyData/SetData；没有可信规则匹配函数。不能把CFEqual或新建App的designated requirement相等当作ACL规则满足。
5. Apple开源SecTrustedApplicationPriv.h明确标注非公开接口，其中ValidateWithPath可返回规则验证状态，CopyRequirement可给出内存SecRequirement，但两者属于私有SPI。当前提案没有明确采用私有SPI的实现依据，不擅自调用、动态解析或导出blob绕过。故在仅公开SDK、禁止导出条件下，currentAppMatches/priorAppMatches目前必须Unknown，未证明可实现。
6. 两固定公开App可以用公开SecStaticCodeCheckValidity验证自身签名，但这无法取得ACL中保存的要求，也不能替代匹配。PM现有互相指定要求验证仍不是条目ACL验证。
7. 现有provider_store::row会SELECT整个envelope_json；不能复用到“不读密文”新诊断。需新增只读SQL列投影，仅返回credentialRevision与json_extract(envelope_json,'$.keyReference')及必要非内容版本，Host只取这些返回值。SQLite底层同页可能含其他字段，不能把SQL投影描述成物理磁盘零接触；若要求连数据库页也不接触密文，现存储布局下不能保证，须保持Unknown而非偷偷读取整行。

## 固定假对象测试设计（无真实执行）

- FFI fake记录所有调用参数；passwordLength/passwordData必须NULL，itemRef必须非NULL；只有exact默认钥匙串+固定service/account，未知/空/多目标先拒绝。
- 假profile行含secret/ciphertext canary；投影结果只含允许字段，缺失/类型错/版本变化停止。禁止调用row()/decode()；schema查询审计拒绝整行/envelope返回。
- ACL fake分别NULL列表、空列表、一项、多项、复杂未知授权；仅解密规则进入摘要，description只释放，不读取字符串，所有opaque引用只在Host内。
- App匹配fake只允许两个固定标签和固定摘要；对象缺失/摘要变更/无公开API/未知状态均unknown，不试第三对象。只有有依据的匹配返回0才能true，无法判断不能false。
- whitelist序列化测试植入账户、service、ref、路径、description、blob、自由错误canary，输出不得含任一；仅stage/数字OSStatus/计数/明确布尔或unknown。
- 单worker、5秒、取消、迟到、权限拒绝、并发拒绝：无第二次调用，无解锁或Set*，超时即使OS调用未停也丢弃迟到结果。Fake网络与材料读取计数必须0；既有B策略/预留/失败不变。

## 依据

- [Apple FindGenericPassword](https://developer.apple.com/documentation/security/seckeychainfindgenericpassword%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_1)
- [Apple私有头声明](https://raw.githubusercontent.com/apple-oss-distributions/Security/main/OSX/libsecurity_keychain/lib/SecTrustedApplicationPriv.h)，第23–24、36–42、63–80行。
- [Apple实现](https://raw.githubusercontent.com/apple-oss-distributions/Security/main/OSX/libsecurity_keychain/lib/SecTrustedApplication.cpp)，ValidateWithPath验证磁盘对象、CopyRequirement保留opaque对象；公开CopyData返回路径而不是可用于此任务的规则桥。
- 本机Xcode SDK：System/Library/Frameworks/Security.framework/Headers/SecTrustedApplication.h（93行）、SecACL.h:133–146。

无需用户重复解锁或手动检查。请PM先评估Unknown缺口对一次提案价值的影响；此文不请求第二次碎片批准，不执行私有API。
