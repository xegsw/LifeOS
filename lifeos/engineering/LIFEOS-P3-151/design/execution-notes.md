# P3-151 执行与恢复说明

当前入口仅 health_ui → HealthConversation/HealthFlow → health_context（复用 core.resolve）→ 两个 OfflineAdapter → 固定合成 Host。Rust仍在事务边界复验domain、授权、来源版本、时效、草稿版本、模型、取消、预算与用户状态声明。Provider配置和加密模块原文件保留，151 main不编译这些模块。

## 范围与预算

固定根 `/private/tmp/lifeos-p3-151-health-conversation-v1`，marker/目录验证后仅访问其synthetic库；无路径参数或真实分支。复用9类业务表和requests/audit/meta，没有第二记忆库。五个既有command的v4语义已获PM批准（pm-approval.md）。严格Raw JSON、重复字段/未知字段/null/超16KiB拒绝。

Host候选按domain/来源授权/状态/时间限量，至多16条record、8192字节；Context Resolver进一步选≤3来源+≤2状态/记忆、4096字节。Host按实际引用重新算预算，不信任客户端声明。会话快照≤30轮、32768字节、含refs在内≤40项；超出只截去返回中的较早轮，持久记录保留。无历史分页UI是明确的有限快照策略，不代表删除历史。

短期状态24小时；available_time必须绑定用户文本中的分钟值，自述睡眠不改来源测量。纠正保留旧raw，supersede旧state并使依赖旧raw的answer/packet失效。无普通回答→Durable Memory的写入路径。澄清忽略抑制当前会话；暂缓30分钟；回答24小时内不重复追问。裸时间答复仅绑定待答澄清/明确纠正的领域。

中文重叠双字检索修正自然句中“报告”漏匹配；仍是有界词面检索，不宣称语义模型。OfflineA/B均为合成有限规则，B延迟用于取消验证；`[模拟失败]`只注入当前packet的一次可重试离线失败。没有开放域、医学、网络或真实Provider能力。

## 实际 GUI 与边界

严格按launch receipt PID、固定binary路径与hash、精确标题、AXWindow/AXWebArea、CG几何匹配截图。非目标PID 0在创建AXApplication前拒绝，见rejected-nontarget-pid.txt。未操作150真实App，也未读取对应数据或AX；所有GUI文本为本轮自建合成输入。

初次CUA typeText中文只输入了标点“，？”，该合成负样本仍保留，未算中文输入正证据；改用paste后完整中文通路通过。锁屏发生在纠正之后，失败的截图调用没有生成正截图；恢复后从GUI阶段续接。原初始/澄清图绑定PID18824；授权展示边界补丁后PID19139验证重启/纠正、键盘依据、失败草稿；中文检索补丁后最终binary在PID19289复验工作/未知/取消/窄屏，PID19407重启后复验状态/记忆/AdapterB继续5分钟。各阶段receipt保留，旧图只证明未受补丁影响的对应交互，不冒充同一binary的全阶段复跑。

16个Host测试、10个Application→实际Host集成用例通过。后者使用同一Host代码的synthetic-driver测试feature，独立库，生产App未启用此feature。test-only修改来源/授权用于负例，不作用于演示App库。GUI只对已启动的本轮syntheticApp做本地交互。

## 复跑与手工恢复

`bash tools/rerun.sh`只在已验证本轮固定根内写独立rerun目录，不改封装报告/历史Evidence，不自动启动或操作GUI。依赖均locked/offline。先verify_inputs/verify_package；测试和构建后输出日志目录。

`python3 tools/launch.py`仅用于根内首次新App封装，已有App拒绝覆盖。关闭仅使用`stop_synthetic.py`严格验证当前receipt；同一binary重启用`launch.py --restart`，覆盖的是当前运行receipt，若需保留当次证据先复制receipt到新文件。GUI继续用当前receipt guard；完成态保留App，不清除本轮数据。暂未提供跨机器/新根迁移功能。
