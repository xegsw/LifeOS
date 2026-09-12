# 元数据绑定缺陷同范围修正

首次真实检查失败是新代码错误使用 raw enabled/model 作为有效配置条件，未忠实继承既有生命周期决策。初始孤立 SQL fixture 未覆盖合法 raw=false/effective=true 状态，325测试计数不能抵消这一遗漏。首次失败结果/manifest/claim只读保留；未追加真实检查。

从原 settings_lifecycle.provider_view 原样抽取 effective_view/effective_bound，原生产视图与元数据入口共享同一纯决策。元数据仅从固定profile投影 profile/credential revision、keyReference、algorithm/version及配置schemaVersion；生命周期/目录仅原合同两个固定非内容行，不经row/envelope返回/解密。算法和版本使用原crypto常量，reference使用原lineage；移除多余的aadVersion新门槛。目录/凭据/profile修订、tested state、selectedModel在models中、enabled逻辑完全复用。

新增生产Store合成对照：raw=false/effective=true成功进入同C适配源码fake FFI；raw=true/effective=false、有效模型变化、三版本不匹配、缺生命周期拒绝且FFI0。缺/多profile、非法修订/版本/引用/查询失败通过同metadata_from_connections入口拒绝，固定白名单分类；无后端自由错误输出。fake FFI断言密码两个出参NULL、唯一条目、opaque description释放。真实OS读不在回归内。

最终24步完整回归与双模式构建通过。真实后台 -25293 根因仍Unknown；本代码修正未作真实重测，不称已恢复。producer离线接线继续。
