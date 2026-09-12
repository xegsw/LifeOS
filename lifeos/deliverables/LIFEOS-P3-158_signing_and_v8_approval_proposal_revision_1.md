# P3-158 签名与 v8 待批方案 Revision 1：条件执行与人工等待修订

2026-09-10。Design Revision / Execution Not Authorized。仅修订PM指出的两处产品收缩，本文与原 `LIFEOS-P3-158_signing_and_v8_approval_proposal.md` 合读；冲突处以本修订为准。原195行方案及其Manifest保留只读，不追改历史。签名方案、14个IPC命令名、三个公开合成Adapter、真实接口/C禁区和调用数量提案保持；未生成身份、签名、改代码、调用工具/模型或修改信任。

## 1. 差异定位

| 原方案位置 | 本次替代内容 |
|---|---|
| 3.3 Conditional及“true仍只记录” | 当前意图明确且true、权限/目标/版本有效时，同一最终事务保存条件依据并执行最多一项本地Action；不要求另开回合同义确认 |
| 5.2 ConditionRecord/FinalReceipt/幂等 | 闭合联合明确条件记录与Action执行的不同结果；条件事件及Action事件共同原子提交，关联元数据不计第二个外部动作 |
| 3.1 confirm_coordination_query | 首批获准公开本地fixture由Host自动消费限定读取许可，无额外工具确认按钮；这是待批准的明确产品权限差异，当前未执行 |
| 5.1/5.3 180秒整回合墙钟 | 改为累计活动预算180秒，人工等待不计入；恢复生成新TTL预览且复核，不延长或复用过期预览，不重置已消费预算 |
| 6及7批准文本 | 按本修订验收及文末整体批准文本；不将合成验证外推真实通用能力或终局完成 |

本次“最多一项Action”只限既有本地create/adjust/complete/cancel，条件依据、原文、反馈及回执均是该操作的关联记录，不构成另一项外部行动。没有外部执行、未来定时执行或自动监测授权。

## 2. 闭合条件候选及Host判断

沿用原方案基础类型、Action、Spans、Atom和三值计算。以以下对象完整替代原Conditional，仍占Candidate联合中的一个分支：

`Conditional={operation:"conditional_action",content:Content,evidenceSpans:Spans,condition:{join:"all"|"any",atoms:Atom[1..4]},intent:{kind:"apply_if_true"|"record_only",evidenceSpans:Spans},consequence:Action,priorConditionRef?:Ref,expectedConditionVersion?:Rev}`。

所有字段必填，两个prior字段必须同现或同缺，未知/null/重复字段拒绝。intent.kind是模型对用户表达的主张，不是权限token；Host须根据当前已披露原文、当前回合/目标关联及证据跨度验证。不能仅凭kind或模型“用户已授权”执行，亦不能因出现条件句就一律降成record_only。已有意图清楚不追加同义确认；意图、目标或条件本身存在实质歧义才clarify。普通来源文本和工具结果均不能提供用户执行意图。

| Host核对结果 | 最终行为 |
|---|---|
| apply_if_true与当前表达一致，truth=true，Action所有权限/版本/来源/合法转换通过 | 原子写条件依据及一项Action；同回合显示实际本地事务结果 |
| apply_if_true，truth=unknown | 只写条件待定，无Action；明确尚不能判断，不假成功 |
| apply_if_true，truth=false | 保存本次条件判断，无Action；不推出相反安排 |
| record_only与当前表达一致 | 保存条件及判断，无Action；即使true也尊重用户仅记录的表达 |
| intent/目标/条件有实质歧义 | 返回clarify；无Action，不把不明意图当已授权或已完成 |
| truth=true但权限/目标版本/合法迁移失效 | 最终事务失败，无Action/无半条条件提交，保留草稿；不能把它混成用户只想记录 |

无有效证据或预测资料失效不得形成true；未知保留为unknown。来源和预测类别仍明确标识，不把预测当未来事实。false不推非consequence，单向条件不变双向决定。执行的是用户当下明确要求的本地安排创建/修改等，不是替用户实际出门或调用未来外部动作。

## 3. 闭合持久类型、回执与幂等

基础类型扩充：`Truth="true"|"false"|"unknown"`（字符串枚举，避免把unknown混入JSON boolean）；`EntityRef={id:Ref,version:Rev}`；`ActionApplied={action:EntityRef,eventRef:Ref,operation:"create"|"adjust"|"complete"|"cancel"}`。

`ConditionEffect={kind:"action_applied",applied:ActionApplied} | {kind:"not_applied",reason:"condition_unknown"|"condition_false"|"record_only"}`。

原ConditionRecord替换为：

`ConditionRecord={id:Ref,version:Rev,kind:"condition_record",schemaVersion:8,operationId:Ref,rawRef:Ref,content:Content,condition:{join:"all"|"any",atoms:Atom[1..4]},intent:{kind:"apply_if_true"|"record_only",evidenceSpans:Spans},consequence:Action,truth:Truth,status:"pending"|"evaluated"|"superseded",basis:{factRef:Ref,sourceRef:Ref,sourceVersion:Rev,evaluatedAt:Time}[1..4],evaluatedAt:Time,effect:ConditionEffect,supersedes?:Ref}`。

truth=unknown时status=pending，其他为evaluated（历史投影可superseded）。effect.action_applied只允许truth=true且Host核实apply_if_true，action/event必须实际来自同事务。reason=condition_unknown/condition_false须与truth一致；reason=record_only要求Host核实record_only。移除原consequenceExecuted恒false字段。旧条件原文/事件不覆写；更正追加版本。撤权或后续来源失效只标当前依据不可继续使用，不自动撤销已提交Action、不重复执行旧条件。

FinalReceipt替换为公共头与一个闭合结果联合：

`FinalReceipt={operationId:Ref,turnRequestId:Ref,turnId:Id,state:"committed",committedAt:Time,reply:Text,result:FinalResult}`。

`FinalResult`只允许：

- `{kind:"none",businessChanged:false}`。
- `{kind:"clarify",businessChanged:false,question:Short}`。
- `{kind:"action",businessChanged:true,applied:ActionApplied}`。
- `{kind:"condition_only",businessChanged:true,condition:EntityRef,truth:Truth,reason:"condition_unknown"|"condition_false"|"record_only"}`。
- `{kind:"condition_and_action",businessChanged:true,condition:EntityRef,truth:"true",applied:ActionApplied}`。

TurnStatus.businessChanged取result.businessChanged；condition_only的true表示持久条件记录发生变化，不表示Action执行。UI必须按result.kind判断，不能凭businessChanged显示“安排已执行”。condition_and_action固定回执同时说明“条件依据已保存；本地记录已创建/调整/完成/取消”，condition_only说明“条件已记录；安排未更改”，并给出待定/未满足/仅记录的原因。ActionApplied缺失或引用无法核验时禁止显示执行成功。

Host生成每turn唯一operationId；最终规范候选和依据引用修订绑定至私有提交对象：

`CommitPayload={schemaVersion:8,operationId:Ref,turnRequestId:Ref,turnRevision:Rev,candidate:<终局Candidate，禁止query_need>,basisVersions:{ref:Ref,version:Rev,authorizationGeneration:Rev}[0..9]}`。

该对象仅Host生成和本地存储，不接受模型/前端注入。使用既有requests的`coord8:commit:<operationId>`幂等键（所有生成Id仍满足120字符上限），同规范payload恢复原FinalReceipt，不同payload报idempotency_conflict。turn唯一提交标记与请求幂等同事务；预览/确认重试不能新分配operationId绕过。

condition_and_action在同一BEGIN IMMEDIATE中完成最后权限/时效/目标版本检查，写原文、条件事件、唯一Action事件、关联反馈、回答、草稿状态、FinalReceipt及幂等记录。任意一步失败全部回滚，无“条件写了但Action没写却显示成功”。两类事件共用operationId及rawRef，通过condition.effect.applied/eventRef和回执互相绑定。单turn最多一个Action事件；条件事件是关联事实，不为维持“一个结果”拆第二次用户操作。普通无条件Action复用原事务，已提交/丢回执/重启只读恢复，晚到候选不得再执行。

## 4. 公开fixture查询免额外确认：明确待批边界

**本修订建议批准**：在三个固定公开本地fixture Adapter、固定注册目标、参数与原提案调用上限内，Host接收并校验第一轮query_need后可自动进行唯一一次只读查询，不增加工具确认按钮。查询继承的是补充合同批准的精确本地能力许可，不能由首轮云端点击推导任意读取权。本项尚未实施或获正式执行授权。

只限 `fixture.note.lookup.v1 / fixture.schedule.lookup.v1 / fixture.forecast.lookup.v1`。许可不覆盖真实文件/日程/天气/城市/定位/网络；Adapter变更为非fixture必须拒绝。无需查询时零工具调用。UI显示正在补充公开合成资料且可取消，不弹重复批准；工具结果向DeepSeek的第二次精确披露仍由用户亲点，不能随本地自动读取一起默许。离线替身阶段的模型处理依离线测试合同，不冒称真实云端确认。

IPC命令名仍14个。原v8 `resolve_request_context/confirm_coordination_query`从拟议允许表删除，该组合严格拒绝；查询只由Host内部路由执行。原QueryPreview改名 `QueryDescriptor`（字段保持不含客户端可用授权），只用于本地记录和UI说明；TurnStatus的queryPreview字段移除，增加可选queryDescriptor。私有查询许可完整替换为：

`QueryPermit={id:Ref,queryId:Ref,descriptorId:Ref,descriptorRevision:Rev,turnRequestId:Ref,targetIdentity:Ref,capabilityRevision:Rev,authorizationGeneration:Rev,grantKind:"approved_public_fixture_read",contractRevision:Ref,state:"ready"|"consumed"|"cancelled"|"expired",expiresAt:Time,consumedAt?:Time}`。

contractRevision绑定未来获批补充合同版本，不接受客户端设置；还必须检查运行模式为offline或online-synthetic、dataClass为public_synthetic、target在注册集合且未撤销。descriptor生成后立即复核和消费，不等待额外query确认。查询/模型许可分离的原则不变。

## 5. 活动预算与人工等待分离

用以下规则替代原方案所有“整回合墙钟180秒”“人工等待也计时”“重启不得重置总deadline”的表述：**累计活动上限180000毫秒；人工等待和应用关闭期间不计入活动用时**。模型每次15秒连接/60秒请求、工具每次15秒及调用次数上限保持。签名/系统凭据交互等待不因此延长任何发送预览的五分钟TTL。

`ActivityBudget={limitMs:180000,usedMs:0..180000整数,reservedMs:0..180000整数,activeStage:"none"|"host"|"model_first"|"query"|"model_second"}`；usedMs+reservedMs≤limitMs。Host/查询/模型开始前持久记录活动阶段及预算预留；结束后按单调时钟耗时结算，预留不足立即停止。网络阶段的墙钟上限为min(各阶段上限,剩余活动预算)。无法在崩溃后可信测量的预留量保守转usedMs，不清零/补回已消费调用；重启不重发在途步骤。不要把多线程CPU时间当活动墙钟。

显式用户交互等待不计活动用时，进入等待前结束当前host活动段；原生CredentialPort整个阻塞交互调用可作为等待段排除（不声称能细分系统内部每毫秒），返回后进入新的活动段并完整复核，再允许网络。等待不是长数据库写事务；不能靠持有锁阻止取消或恢复。后台不轮询用户、不自动续授权、不趁恢复自动发网络。

每份发送预览仍expiresAt=创建时刻+300000毫秒。过期预览及对应未消费许可永久失效，不能就地改expiresAt。等待中的turn可以保持可恢复，不因人工三分钟未操作就整回合必死。取消和不可恢复错误仍终止，活动预算耗尽仍失败。

State扩充`paused`；TurnStatus移除deadline字段，增加`activityBudget:ActivityBudget`和可选：

`pause={reason:"user_wait"|"preview_expired"|"credential_wait"|"app_restarted",resumeFrom:"first_ready"|"result_ready"|"second_ready",pausedAt:Time}`。

paused必含pause、无可用sendPreview；其他状态禁止pause。query_ready现在是Host内部短暂校验态，后接query_inflight，无人工许可等待。已有first_ready/second_ready未过期时仍可直接由用户确认，不为暂停再添按钮。

增加允许映射：`resolve_request_context/resume_coordination_turn` payload `{requestId:Id,turnRequestId:Ref,expectedTurnRevision:Rev}`；返回`{turn:TurnStatus}`，若恢复成功在turn.sendPreview附新预览，沿其phase等待用户确认。客户端不能指定恢复phase、续期秒数或重置计数。UI可把“继续”接到这一动作，仅过期/暂停时出现，不要求正常每回合点击。

恢复步骤：核对同一turn/草稿/用户意图、profile/credential/catalog、全部授权generation与目标版本、查询结果来源/时效、活动剩余额度及已消费调用。原预览标失效，Host创建新previewId/revision和五分钟TTL并显示精确当前披露；绝不复用旧许可/静默续期。恢复本身不消费新的turn/query/model额度，也不清零历史。只有用户确认新的有效模型预览才可消费该阶段尚未使用的模型许可。

- first模型尚未进入Adapter：可在同turn恢复新的first预览；若旧许可已消费，其预算不退还，恢复前仍须满足2次上限，不以phase标签无限重试。已进入Adapter且结果不明则outcome_unknown，不自动再发。
- 查询已成功且结果仍有效：可在同turn生成新second预览；保留原queryId，零重复读取。已过期或来源版本改变：不能刷新fetchedAt或重新调用唯一工具来伪造有效性，明确query_result_stale，保留结果历史/草稿。若确需重查，由用户新回合明确发起并计入剩余累计预算；这由真实证据失效触发，不因单纯人工等待超三分钟强迫重来。
- 用户意图/目标集合发生实质变化：不能借resume把旧请求换成新任务；保留旧历史，按新回合生成明确披露。取消、committed、outcome_unknown不可作为未发送步骤恢复；committed直接返回原回执，其他返回固定状态。

固定错误集合新增`activity_budget_exceeded,resume_rejected`。不再把单纯人工等待映射为turn_expired；预览过期返回preview_stale并提供paused可恢复状态。业务证据时效保持各Adapter既有严格规则，不以暂停冻结天气/日程时间。

## 6. 本修订验收与整体批准文本

新增必要合成验证：true+明确意图同turn写条件和一项Action且回执正确；unknown无Action；false不反推；record_only不执行；真条件但目标版本/权限失效零半提交；模拟Action插入失败使条件一并回滚；相同operationId重试/重启不重复事件；工具结果伪造意图不能自授权。

等待验证：人工等待超过180秒不耗活动预算；超过五分钟使旧preview失效，用户恢复后新preview/TTL且预算不清零；凭据等待返回后旧授权已过期零新增网络；second预览恢复复用仍有效结果不重查；结果过期诚实停止；Adapter在途重启outcome_unknown不重发；自动fixture读取仅命中三个固定能力，真实目标/网络模式拒绝且第二次模型仍须亲点。测试应使用可控时钟，不真实睡眠/Key试验。

本地业务上限改写为“每turn一个最终事务、最多一项Action；允许同事务附条件依据/记录”，非两个外部动作。原草案新增开发8回合/8工具/16模型、未见4回合/4工具/8模型仍只是待批提案，旧B14/40保持。签名仍未授权，原方案的失败暂停/无信任修改默认保持。

建议整体批准文本替代原第七节引用：

> 批准原签名方案及本Revision 1修正后的v8合成协调实施；本机专用签名身份不修改证书信任或Provider ACL，失败保留暂停。三个固定公开本地fixture可由Host在批准参数/目标/次数内自动读取，不另加工具确认；每次真实模型发送仍由我亲点精确披露。人工等待与活动预算分开，恢复须新预览并重新校验，调用预算不重置。条件成立且我的当前意图明确时，同一事务保存依据并落实一项本地安排，不要求重复同义确认。新增协调模型预算最多24次单列，历史14/40不变；B恢复仍须签名和离线门槛通过。真实外部接口和C不开放。

该引用仅建议，当前没有执行授权。三个fixture通过只能证明合成协调范围，不能宣称真实通用查询能力或P3-158终局。真实接口、来源许可/参数/目标及C真实验收缺口继续明确保留，最终任务范围与完成裁定由PM/用户收口。无新任务、无工程包、无其他范围扩展。
