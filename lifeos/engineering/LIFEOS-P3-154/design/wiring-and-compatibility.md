# P3-154 接线与兼容矩阵（执行中）

完整继承153 Closure-1的163文件，不删旧能力；152真实接线作为差异依据。全部已有398项Manifest输入已复算。合同SHA c363c40f137fc0e460d716c0395f1b2ceef6d9fcde8d345dc336f9e1639d3047；ABF SHA 8c18d68c79676e5a4fe2c7e50ecf6f2941ac85f630fc1c68196ae74f504a3995。

|路径|继承/154变化|验证|
|---|---|---|
|Shell/Settings及14 IPC|完整继承，只有App标题/独立bundle标识变化|既有UI25/集成14/组合11，最终结果见Evidence|
|153 Orchestrator/Host|保留Closure-1时效、问题实例及反馈语义|连续性8/时效6/Host回归|
|controlled-real|恢复152编译门禁、保持real+driver互斥；无生产路径/时钟覆盖|正负构建、源代码检查|
|conversation/provider|真实固定旧路径/旧marker/旧表/旧AAD，只打开现有库；缺失拒绝|合成旧库重启、缺失/不兼容反例|
|Keychain|service仅com.lifeos.p3-152.aead-key.v1；account为旧provider_profile.envelope_json.keyReference，严格p3-152-key-[0-9a-f]{32}|MemoryCredentialPort缺失/不匹配/144拒绝；不访问真实Keychain|
|来源|复用旧索引和授权；主动提问可读已授权来源，无启动扫描；不创建平行库/补表|现有授权/撤回/重启与Schema拒绝|
|健康|保留导入实现与合成覆盖；本轮真实模式返回health_import_not_authorized；既有只读Reader不变|组合导入/只读健康回归；不触真实ZIP|
|Provider|固定DeepSeek，手动/models、用户逐次确认chat；无启动网络/自动重试|生命周期、确认调用计数、Key泄漏反例|
|切换|先合成安全关卡，后固定bundle/binary/PID、正常退出旧152，单实例锁|只收固定状态码；真实界面/正文禁止采集|

account的随机后缀不是源码常量。工程仅列格式及唯一解析路径，具体旧引用仅App内部使用，不枚举Keychain、不输出引用/密文/个人内容。不存在144 fallback。缺密钥的解密路径不调用add/delete，不生成新密钥替换旧密文。

独立评审依用户例外暂停，不是Independent Pass。真实结果ABF-10待用户完成；不以合成替代。所有新增反例只使用154独占合成根。无历史清理，无提交/推送/账本修改。
