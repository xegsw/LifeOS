# P3-152 健康辅助查看兼容IPC提案

状态：Pending PM approval before wiring。独立增量以ui-restoration完整candidate副本为底，原172项Manifest不改；当前真实App与bundle不操作。本增量只恢复150 R1辅助查看，不取代152对话主入口及142设置。

唯一新增公开命令 get_today，复用150 R1严格 Raw JSON DTO：version=2、operation=health_view、payload={metric,days,endDay?,source?,offset?,groupPage?}。未知字段、重复键、非Raw、超4096 bytes、错误版本/operation均拒绝；不接受路径、SQL、网络地址或授权声明。原152七命令及v4/v5不变，无Schema变化。

metric仅sleep/steps/exercise；days仅7/30/90；endDay可省略或null，表示选中来源最近有数据日期，显式值为0..47481日索引（1970-01-01..2099-12-31）；按所选来源offset的日界线，不能当设备当前时区或今天。source/offset必须同时提供或同时缺省，source非空≤640 UTF-8 bytes/无控制字符，offset -840..840分钟；groupPage默认0、≤1000。缺省选择最近有数据的来源名称组+offset，不合并设备或跨来源总量。传入具体来源只能过滤既有授权健康投影，不能创建来源或扩大根。

Response原样复用150 Reader：metric/days/source/offset/endDay/latestDay/observedAt/receivedAt/importedAt/groups/groupPage/nextGroupPage/points，缺省分支保留原null/缺失字段语义。每页32来源、最多90日点、源查询最多91行用于冲突检测；重复投影失败关闭。3秒SQL progress预算，150ms busy timeout，序列化结果≤128KiB。Reader::open原有7日steps校验查询保留，因此一次打开至多有初始化校验与实际查询两个分别有界阶段，不声称整个IPC仅3秒。

主路由：get_today Raw body → Reader的纯DTO解析校验（先于文件打开）→ Store内source_connected与health-demo授权校验 → 固定health_source::path(fixture) → Reader::open → 原query。Store锁覆盖授权检查和本次查询，阻止本地授权在返回前变化；每次用户请求独立打开只读连接并重新校验文件身份，不缓存旧真实连接。Reader增加包内纯解析/已校验Query入口，不改原查询SQL/日期/估算语义。get_today不经过ModelPort/凭据初始化，不读取模型设置，不创建packet/写state/保存记录，不授权AI使用资料。

真实目标仅沿runtime_root已有HEALTH_DB常量；Agent不探测真实目标。合成使用Store既有fixture派生路径，用户不能指定。沿原no-follow、0700/0600/UID/nlink、只读SQLite/query_only、DB身份及sidecar拒绝。错误返回固定readonly_*或source_not_authorized，绝不返回正文/路径诊断。

UI：在“我”的当前状态后加“查看健康来源”按需入口。未进入不查询；进入默认仅150R1批次状态与最近日期，再展开数据详情/趋势，保留指标/日期/来源组控件。返回“我”不丢对话草稿或设置。移出独立readonly.js自动挂载，复用其Controller/内容渲染与readonly.css，不加载旧Shell，不新增看板、自动刷新或AI按钮。切走后迟到结果不得重新打开页面；初始三个查询串行，不在后台轮询。

验证：新增真实禁用的合成IPC/Reader正负测试（日期/分组/未知/预算边界/拒绝字段/权限/只读不写），复用原150 Controller测试并补组合入口/退出迟到/草稿不变。共享main/gateway变动跑原44 Host和10集成仅一次；构建synthetic与controlled-real但不启动真实。视觉只在结构接回存在必要时少量合成核验，不重拍历史。

请PM批准上述唯一IPC兼容及按需UI接线。没有请求新真实数据、写库、ZIP、权限或网络；若这些边界变化另报，不默认为本提案已授权。
