# P3-151 最小接口与JSON语义差异（待PM确认）

仅151固定合成编译，无real分支/运行环境切换。复用5个既有IPC名称，各自新增version:4封闭分支，不伪称148/150原契约不变。外层{version:4,operation,payload}，Raw UTF-8≤16KiB，每层deny unknown/duplicate；ID 1..120 ASCII；问题≤2000 scalar/8192bytes；固定conversationId=health-chat，无路径/URL/SQL/secret/任意授权布尔。

| IPC / operation | payload字段 |
|---|---|
| capture_record / draft_turn | requestId, turnId, revision, text |
| get_context_recovery / conversation_snapshot | {} |
| resolve_request_context / prepare_turn | requestId, turnId, expectedDraftRevision |
| resolve_request_context / commit_turn | requestId,turnId,packetId,modelId:OfflineA或OfflineB,text,inputRefs:[{id,version,authorizationGeneration}],clarification?:{field:available_time或domain},state?:{key:available_time或sleep_hours,value,domain:health或work},answerTo?:questionId,corrects?:stateId |
| resolve_request_context / cancel_turn | requestId,turnId |
| decide_understanding_feedback / clarification_decision | requestId,questionId,decision:ignore或defer |
| save_ai_provider_settings / select_offline_adapter | requestId,modelId:OfflineA或OfflineB |

snapshot≤30轮（有更多时明确仅最近30轮），返回该会话草稿、少量有效状态/已确认memory/待澄清与Adapter设置。prepare由已存草稿取得原文，按Host保守领域过滤、授权/有效期限16个候选与8192字节，TS Resolver再做意图/时间/词项排序，最终≤3个来源、≤2个有效状态/记忆、4096字节上下文；超预算失败不调用Adapter。refs来自本请求候选且提交时逐项重新校验。Work/歧义不得包含Health，未授权Health零披露。选用的Adapter和请求基线由packet固定。

同一业务库使用原records/memories/states/sources/questions/packets/derivations/feedback/drafts及requests/audit/meta结构；无新增表/第二记忆库。新对象JSON schemaVersion=4，kind以health_conversation_*区分，新增临时状态/澄清语义明确批准后使用。Provider/加密配置不更改，此模式选择仅存业务meta/合成设置对象，既有Provider路径不执行。

prepare不提前把一次失败问题变成成功对话；commit原子写用户原文、AI候选回答、request-scoped refs和必要短期状态/澄清、消费对应草稿与幂等receipt。普通回答永不自动写confirmed memory/正式Action。state只接受原文可核对的用户补充，不能由模型文字充当事实；corrects需指向同域当前状态，保存独立纠正原文、旧状态superseded、依赖stale，原文历史不覆盖。

requestId相同同DTO回放、异DTO冲突；同turn成功只一组记录。cancel tombstone防迟到提交；提交已先完成则如实completed，不声称撤回成功。新编辑与迟到结果通过148 serial语义隔离。defer固定短窗口、ignore抑制本会话同字段追问，未答不写状态。离线B延迟模拟用于取消验证；显式合成失败问题标记用于一次失败/原草稿重试，不是网络故障注入。

这是合成对话行为验证的最小差异，不扩展真实健康读取/模型发送/网络授权，不新增核心领域实体或关系引擎。请PM确认上述v4分支、同表新JSON语义及限额；其余151允许工作继续。
