# P3-149 最小合成输入与投影合同（实施前）

状态：工程包内固定实施依据，非产品/Schema/API冻结。任务卡授权合成离线L2；真实健康/iCloud/手机/网络/凭据及旧运行根不接触。148仅只读candidate复制，未复制DB/凭据或Evidence作为149夹具。

## 输入 health-envelope-v1

UTF-8 JSON对象，严格递归拒绝未知/重复字段，文件最多128 KiB，批次最多256样本。顶层恰好：schema="health-envelope-v1"、batchId（1–80 ASCII字母数字/连字符/下划线）、exportedAtMs、windowStartMs、windowEndMs、timezoneOffsetMinutes（-840…840整数）、source:{id,name}（id规则同上，name1–80字符）、samples数组。时间均UTC Unix毫秒整数，范围2020–2100年；窗口正长且最多7天，exportedAtMs不早于windowEndMs。显示的汇总日使用本批固定UTC offset，不能宣称支持任意IANA时区/DST推断。

每样本恰好：sampleId、revision（1…1000000整数）、metric（sleep/steps/exercise）、startMs、endMs、value、unit。身份为source.id+sampleId，revision为源版本。区间在批次窗口内，start<end；steps单位count且value非负整数；exercise单位minutes且value非负有限数、不得超区间分钟数；sleep单位milliseconds且value恰等于区间长度，仅表示“睡眠区间”，不接收卧床/清醒/阶段混合标签。源端需先筛选睡眠类型，是否能稳定取得身份/版本由设备验证决定。

相同batchId与相同规范化内容重放幂等；相同batchId不同内容拒绝。相同样本身份/版本且内容一致无新增；同版本不同内容整批拒绝；低版本迟到不覆盖；高版本更正保留旧版本来源关系、仅重算旧日与新日受影响投影。未返回样本不删除；空批次不清空旧有效数据。

## 内部Source/State映射（无新表、无新Tauri命令）

使用既有records/sources/states JSON扩展机制及一个SQLite事务：records保存health_sample版本对象与health_batch收据；sources保存health_source连接/最近接收元数据；states保存health_current_state日汇总。复用既有主键/JSON表结构，不DDL迁移，不改147/148库。新149新合成库按既有初始化创建。

health_sample是外部来源样本，不是用户确认事实；health_current_state是确定性派生，status="observed"、domain="Health"、modelEligible=false。source保留ingestAuthorized=true及authorized=false；后者继承既有模型/上下文active守卫的默认拒绝，不把健康接收授权提升为模型读取。raw样本status="observed"同样不满足既有active守卫。UI只将这些扩展对象投影到Me/Memory/Settings，不写memories。

Source Adapter仅从固定149合成inbox读取有界普通JSON文件，转换类型化SourceItem；纯健康规则模块校验与计算；Ingestion Application通过HealthRepository Port要求单事务保存；SQLite Adapter实现存储。后台仅为本App进程内定时接收，App退出即结束；无系统注册服务。文件不删除、不移动，成功收据与内容摘要去重，失败不部分写入，旧有效结果保留。

现有get_today v2 snapshot已返回sources/states/records数组。UI复用此读取，不添加命令/operation或修改Request DTO；只消费带health kind的扩展对象。UI在当前App打开时定期读取已有快照以显示新状态，Health不会进入SourceSegment模型检索或当前source-chat确认包。

## 汇总与新鲜度

以offset本地日拆分区间；睡眠按区间并集计时（跨来源的明确睡眠区间重叠不重复累计），不代表健康App权威睡眠量。steps/exercise跨日按时长比例分摊，明确标“估算”；同一来源重叠非同样本的计数量不直接相加，输出uncertain/null；多来源分别计算；steps/exercise无来源优先级依据时个人汇总为null，展示分来源数值与“暂无法可靠合并”，不取最大值。不同offset分开显示。缺失指标不创建零值。来源/样本版本refs、观测区间、汇总日/offset、最近收到时间及计算方法随状态保留。

更正仅影响样本旧/新区间涉及的日+metric+offset；不更新无关State。旧有效状态不会因坏包或未返回而清空。新鲜度用最近样本时间与当前时间确定，显示过期/最近接收时间；不推断疼痛、疲劳或诊断。

## 需要PM核对的精确差异

新增Tauri IPC：0；新增Request operation：0；新增SQLite表/列：0。新增内部扩展kind：health_source、health_sample、health_batch、health_current_state；新合成输入schema如上；仅本任务合成目录接收。PM已批准本任务合成JSON扩展映射，未批准真实授权或核心Schema冻结。快捷指令方案后续核对Apple官方资料，并列出待设备验证项与真实阶段一次性边界清单。

收到时间receivedAt与观察时间observedAt分离，旧记录重放不能刷新观察新鲜度。批内同身份/同版本内容冲突整批拒绝；一致重复折叠，不同版本保留历史但仅最高版本投影。128KiB/256样本/7天仅是合成单包界限，超限拒绝不截断，真实分批/身份/修订策略待设备验证。snapshot完整健康原文仅限本合成库，未来真实默认字段披露未批准。
