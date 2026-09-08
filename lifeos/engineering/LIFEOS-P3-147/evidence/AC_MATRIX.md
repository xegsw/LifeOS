# P3-147 合成工程逐行矩阵

执行侧自检，不是Frozen ABF或独立评审。正式独立安全及真实亲验未开始。原始日志均保留；本表指向最后覆盖相应变动的成功结果。

证据简称：R=`checks-20260908T052426412687Z/rust.log`（16）；P=`checks-20260908T052535959595Z/parser.log`（11）；W=`checks-20260908T043508621304Z/web.log`（14，Web策略源码未改，显式复用）；A=`checks-20260908T052426412687Z/inherited.log`（31）；I=同目录`public_api.log`（1）；G=`checks-20260908T052535959595Z/root_profiles.log`（4）。本轮实际复跑63项，另复用14项未受影响Web检查，组合覆盖77项。根构建四项见`root-build-20260908T052514/results.json`：review只编译、未知/缺少profile/任意根覆盖均拒绝。最终binary为engineering profile。

| 合同 | 工程验证与结果 | 原始证据 | 后续关卡 |
|---|---|---|---|
| AC-01 | 合成侧通过：多格式/隐藏配置/附件，FD根边界、特殊文件、内外链接、bookmark别名、循环与读中变化；配置不进入普通记录 | R文件适配/扫描测试；P格式矩阵；I配置诱饵 | 真实目标禁止接触 |
| AC-02 | 合成侧通过：5201项、24层、300KiB读流；125+文件持久队列；256分页；暂停/取消/刷新；目录变动停止提示刷新；无逐篇导入 | R scale、persisted_scan、scan_change、recovery；I自动6文件；早期native状态记录 | 真目录容量未宣称 |
| AC-03 | 合成侧通过：原文分段与完整缓存保留；标题/时间/版本/定位可查；不确认长期事实 | R long_source；I详情/分页/配置；`app-root-closure-desktop-detail.*` | 独立复核待进行 |
| AC-04 | 合成侧通过：同请求回放、异payload拒绝、乱序/事务50上限、回执故障原子回滚、原件孤儿隔离、失败新版本保留旧有效版本 | R transactions、batch、failed_new_parse、recovery、target_publication；I连接/目标receipt故障 | 无旧库迁移 |
| AC-05 | 合成侧通过：最多8个词项匹配片段，配置/旧版/撤权退出；空结果为空；既有上下文预算二次验证 | R search/cursor；A来源上下文；I有限检索；`app-sources-context.*`与最后UI不改该链路 | 无真实模型发送 |
| AC-06 | 合成侧通过：断开、源缺失/版本更新及父引用变化失效记录/packet/派生；刷新拒绝旧cursor；重启不恢复旧grant | R missing/target_parent/worker；A packet重放/重启；I generation/cursor；`app-root-closure-narrow-restart.*` | 不等于风险关闭 |
| AC-07 | 合成侧通过：原30项继承回归；Provider目录及未链接凭据文件逐字一致；实际App保存一次、3依据、桌面/窄窗口、详情自动定位 | A；`app-sources-context.*`；`app-root-closure-desktop-detail.*`；`app-root-closure-narrow-empty-search.*` | 非阻断P2见主报告 |
| AC-08 | 合成侧通过：无真实HTTP/DNS/socket或Provider调用；目标/重定向/地址/秘密URL/资源上限/非递归反例；字节保留的凭据代码不链接 | W；A边界/代码继承；I明确两类合成目标 | 真实网络和凭据仍禁止 |
| AC-09 | 合成侧通过：配置诱饵不进入snapshot、检索/packet、错误；解析超预算回执无正文；URL不走子进程命令行 | P配置/真实子进程预算反例；I诱饵；A来源上下文；W敏感URL | 无真实数据回执或截图 |
| AC-10 | 合成工程链通过：导入→检索/上下文→刷新/取消→断开→重启；桌面1280和窄窗口700均有直接PID→同名AXWindow→AXWebArea→图像/几何链 | I、A；各`app-root-closure-*`及`launch-rootclosure*` | **独立安全评审、用户真实亲验、PM终局全部Pending** |
| AC-11 | 合成侧通过：直接外链两类正文、单独grant/revoke、父版本失效、获取时间与内容事务一致、不递归 | R target_publication；I两个目标生命周期；W；`app-root-closure-desktop-targets.*` | 不代表任意真实URL可访问 |

新API保留原20+批准5；输入精确约束仍以批准的Task Contract与实施检查点为准。详情/状态额外本地展示元数据不提供客户端路径或权限写入入口。

## 同合同根授权 Closure

PM发现原候选无法在原卡review根运行；现由单一root_profiles.json与build.rs显式选择、Rust runtime_root统一验证仓储/文件/worker/target/parser，Python/Node/Swift辅助链同源。无新增IPC（仍25项）；UI/Cargo依赖/Schema不变。G覆盖运行时混用、任意root覆盖、未知profile、纯review配置；R新增2项覆盖纯双模式混用与工程根内注入marker/目录模式/符号链接反例。独立review根未访问/stat/create/cleanup，review动态运行是待独立会话执行项，不记为本工程Independent Pass。

旧259工程文件及报告保全在history/pre-root-closure，与固定e5cb31a3 Git blobs逐项复算；原69项更早历史亦未修改。新App直接PID42432与42528验证接入/双目标/检索/原文/断开/重启；最终全部停止，工程root retained。复跑隔离步骤见REPLAY。
