# S1 无样本ID窗口快照：实施前精确设计

仅本任务合成环境。iOS26.6.1用户所示字段菜单未见ID/revision；不是对整个系统的结论。原161包及报告只读，S1另存candidate/报告/Evidence，不改PM历史。0新IPC、0新operation、0新SQLite表列，沿用health_batch/source/current_state JSON。

## 输入

严格UTF8 JSON，递归拒绝重复/未知字段，128KiB、256行、窗口正长≤7天；超限拒绝不截断。schema="health-window-snapshot-v1"，batchId为导出重试身份，capturedAtMs为查询观察批次时间（2020–2100，≥windowEndMs），windowStartMs/windowEndMs、timezoneOffsetMinutes（-840…840）、metric（sleep/steps/exercise）、source:{key,name,identityStrategy:"configured-name-group"}、query:{key,intervalRule:"fully-contained",sleepCategory:"explicit-asleep"或"not-applicable"}、completeness（complete/partial/unknown）、pagination（complete/incomplete/unknown）、completenessEvidence="synthetic-fixture"、samples:[{startMs,endMs,value,unit}]。无sampleId/revision。

key/batchId均1–80 ASCII字母数字-_，name1–80可见字符。时间/指标单位和范围继承原规则；samples完全位于窗口。sleep必须query.sleepCategory明确explicit-asleep，其他必须not-applicable；不从名称/类型推断睡眠类别。

source.key标识事先配置的逻辑“来源名称组”，不是设备ID；同名设备未区分。来源展示名不能单独证明唯一性；同key改名称/策略拒绝，不静默改源。query.key表示固定查询口径，intervalRule完整包含才接收。不增加逐样本人工确认。

## 身份、完整性与历史

scope=source策略+metric+精确窗口+offset+query的规范化摘要。batchId按source.key命名空间，仅重试；同batch不同内容拒绝。样本顺序规范排序用于包内容等价比较，摘要不证明逐样本更正。health_batch保存完整合成快照/摘要/接收时间/处置与内部投影generation，原批次永不改写。

仅complete+pagination complete+synthetic-fixture且非空的包能激活。partial/unknown/分页未完/空包保存等待历史和来源接收状态，**不更新已有State**，不认定删除；源端字段本身不证明真实HealthKit权限完整。畸形/超限无任何写入。

同scope按capturedAtMs比较所有已接受完整非空批次的水位：较旧只保留历史，不能覆盖；同时间内容冲突整批拒绝；同时间同内容或新时间相同内容保留幂等收据，不刷新State观察/收到时间或generation；更新完整包原子替代同scope，generation递增，supersedes指前一批次（批次级，不伪造样本级谱系）。等待包不提高有效完整快照水位。重放同batch完全零写入。

任何同metric的**部分重叠或不同scope重叠窗口**均拒绝激活（跨来源/查询/offset同样如此），不合并/叠加；非重叠窗口单独显示，不组成日权威总量。先接收范围拥有该范围，后续变更边界需要先明确新的替代合同。并发由SQLite IMMEDIATE事务串行化。

v1和S1双向守卫：已有v1日State所覆盖UTC区间与S1窗口同metric相交，则S1拒绝；已有S1有效窗口与新v1待更新日相交，则v1整批回滚。旧v1解析和幂等保留，但不自动升级或把两协议计入同组State。

## 投影与呈现

每scope一个窗口State（不是日总量），UI明确显示窗口起止、逻辑来源组、合成完整性及批次generation。counts/duration非重叠才求和；同组重叠输出不确定，重复行也不能靠无ID假设去重；sleep明确区间取并集。无跨日按日分摊，窗口汇总标识清晰。

observedAt为样本最大endMs，receivedAt为此次实际入库时间，capturedAt用于顺序而不当作指标新鲜度。完整更正只修改相同scope State，不改其他State。raw快照只存合成health_batch，modelEligible=false/status=observed；现有resolver/后端prepare实际拒绝需回归。原v1 UI兼容；S1批次refs显示批次版本，不显示虚构sampleId。Settings显示等待不完整/空包，保留已有状态。

## 验证范围

幂等、同范围完整更正、顺序规范化、未知/部分/空/分页未完、相同时间冲突、晚到旧包、水位重放、防重叠、同名来源不冒充设备、超限/未知字段/类别、事务失败/重启、双向v1互斥、模型守卫；补必要actual App快照来源/状态/等待展示。原87/16按影响面继承，仅受影响模块复跑。真实iCloud/健康/网络/模型/凭据不执行。
