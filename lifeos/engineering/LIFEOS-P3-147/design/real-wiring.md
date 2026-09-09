# source-pilot-1 实施记录

原任务卡顶部“真实本地接入与存储授权”已由PM投递。design/real-entry-activation-proposal.md的待批准叙述保留为旧方案历史，当前由本记录和最新任务卡取代该待批准状态。

固定source-pilot-1 profile已实现。root_profiles.json唯一配置批准源/根/marker；build.rs固化profile/source/root。runtime_root管理进程内点击激活、目录FD初始化及重启访问复位。测试编译仅将该profile的两个路径替换为固定engineering fixtures，生产binary无路径注入参数。

main真实模式不打开DB、不resume、不提供stdio诊断；WebView初始脚本只传只读编译模式boolean，不能修改后端权限。UI启动/说明零IPC，点击后现有connect_source_directory激活后端并开始普通接入。source_api拒绝真实外部目标，来源读取由FileGrant固定源映射；source_worker parser/helper使用App Resources。repository只在激活后打开capture.sqlite，主文件FD约束/NOFOLLOW/0600，保留原事务语义。

恢复不重授权目录外内容；App重开后用户点击才重新打开数据，暂停保留。真实浏览器缓存非持久；正文只进已授权本地存储和用户界面。工程侧不使用真实App的AX、截图或stdio，只用纯合成UI stub、cfg(test)普通生命周期和engineering actual App检查。

User-directed review waiver / No Independent Pass。不重跑平台拦截测试，不声明安全独立确认或风险关闭。已获授权不是实际真实数据闭环成功；本次App未启动，最后一步交PM安排用户点击。
