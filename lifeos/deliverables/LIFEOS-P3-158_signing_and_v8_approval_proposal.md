# P3-158 本机签名与通用协调 v8：一次批准方案

2026-09-10。Design Complete / Proposed Contract / Execution Not Authorized。本文给出具体建议值，供 PM 整体收口，不请求用户逐个选择技术字段。本轮只读源码/既有调研及本机 `security help`，未创建、查询或使用证书/私钥，未签名、改信任、访问真实资料、调用网络或实现v8。

输入为5ed8的 `LIFEOS-P3-158_general_coordination_addendum_draft.md`、`LIFEOS-P3-158_signing_and_query_research.md`及原合同D-0665～0668。默认搜索范围0个有效签名身份为PM的D-0669研究事实，本轮未重复探查；不推断全机不存在证书。沿用当前176文件完整候选和D-0667修复，不从旧main/157拼装。B原开发14/24、未见0/16、总14/40保留并暂停；旧157/C不动。

## 一、拟批准的唯一增量

在同一个完整App中增加一个有限协调回合：优先已有获准资料；确有信息缺口时至多调用一个已登记查询能力，再回答或提交一项本地业务结果。三个首批Adapter仅返回公开合成资料。天气只是其中一例，不建立天气专用工作流。签名部分建立本机专用持久身份，用于本任务新包及同范围重建；不授予Provider凭据访问、不保证钥匙串免提示。

真实天气/日程/笔记/文件接口、城市定位、购买订阅、新Provider、新数据路径、自动后台执行及C的v8使用均排除。这样可批准签名与合成协调实现，无需等待真实天气供应商选定；真实能力仍须另一个完整目标补充。原合同其他边界不变，PM须以正式补充明确本次逻辑Schema/API和预算变化，不能直接把本文当执行口令。

## 二、本机持久签名的最小实施合同

### 2.1 身份和精确位置

- 证书显示名称：`LifeOS P3-158 Local Development Signing`；本机自签名、用途仅Code Signing，RSA 2048、SHA-256、有效期365天，自签名终端签名身份，不作为通用CA签发其他证书。无Developer ID、公证或对外分发声明。
- 新专用钥匙串：`/Users/xxe/Library/Keychains/lifeos-p3-158-signing.keychain-db`，当前用户所有、0600；不把私钥写入登录钥匙串或系统钥匙串。批准后才精确检查目标，已存在且身份未知则停，不接管/覆盖。
- 非秘密签名资料目录：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-158/signing/`，0700；仅保存公开证书 `public-certificate.cer`（0600）、公开指纹/用途/有效期/DR/包hash与非内容步骤收据。不得保存私钥、P12、密码、Provider密文或Key。
- 密码由用户通过系统SecurityAgent输入；不经聊天、环境、命令参数、标准输入日志或截图。本次批准不包括遗失密码后的密钥恢复或自动轮换。

### 2.2 创建、保存和访问控制

建议创建专用钥匙串使用系统 `security create-keychain -P` 的SecurityAgent路径；密码不作为参数。设置睡眠锁定及900秒闲置锁定，仅作用于新钥匙串。创建前后只读取钥匙串搜索列表的路径元数据；不更改默认钥匙串，若创建操作加入搜索列表，只移除本次新增项并保留原顺序。签名调用始终用显式 `--keychain` 指向新文件，不依赖扩大的搜索列表。

生成方式为macOS钥匙串访问的证书助理：创建自签名Code Signing证书、显式选择上述新钥匙串，由系统在钥匙串内生成并保存私钥；不使用OpenSSL落盘私钥、CSR导出/导入或P12搬运。证书助理生成前逐页核对名称、用途、有效期、RSA尺寸和目标钥匙串；若本机工具不能明确选择新钥匙串或不能保持私钥不导出，就取消并报告，不退回登录钥匙串或临时私钥文件。

新私钥仅允许当前用户在系统提示后由 `/usr/bin/codesign` 使用。不得选择“允许所有应用”、`-A`、广泛partition list或无人值守免确认；可保留系统默认逐次确认。仅调整新签名私钥本身的访问项，不能查看或修改任何Provider凭据的ACL。私钥是否具备不可导出属性仅以系统实际能力为准，不把“本流程不导出”说成硬件不可导出。此方案无需跨请求缓存Provider Key。

**信任边界**：首选不新增证书信任设置，用显式叶证书锚定的DR完成签名完整性验证。若本机codesign无法接受新自签名身份，停在未签名staging并记录固定错误，不添加系统或用户通用根信任。仅在这一步确需信任、且PM最终批准包明确包含时，可使用当前用户域、仅`codeSign`策略的该张公开证书信任；无`-d`管理员域、无SSL/basic通用策略、无过期例外，不把它默认为本方案已授权的动作。该窄策略的可用性由本机 `security help add-trusted-cert` 支持，但能否解决实际签名错误仍未验证。若要求更广信任，方案停止，报告具体限制而不绕过平台。

这意味着本次最小批准可完成身份生成与受控签名尝试；若平台需要未批准的信任变更，签名阶段仍可能暂停。不能以文档设计保证本机签名必成，亦不能保证Provider钥匙串项接受该新身份。

### 2.3 完整bundle、DR和验证

固定主bundle identifier为 `local.lifeos.p3-158.main-chain`，与当前tauri配置一致；helper为其 `.alias-metadata`。主App名沿用 `LifeOS P3-158 Online Test.app`，在唯一任务临时根 `build/signing-v1/` 独占创建；旧App不覆盖。现有 `package_signed.py` 需在获准后补显式专用keychain和DR参数及严格身份校验，再执行，不能把现有dry-run当签名验收。

DR逻辑固定为 `identifier "local.lifeos.p3-158.main-chain" and anchor H"<新自签名证书SHA-1>"`；SHA-1仅为Apple requirement的证书标识语法，公开证书和所有文件另记SHA-256。签helper后签完整bundle，不使用`--deep`修复、不联网时间戳、不公证。绑定公开证书指纹、完整Info/资源seal、candidate/build receipt、主程序及helper hash；拒绝ad-hoc、未绑定Info或缺资源封装。

验证顺序：同一已签包验签→直接启动并绑定PID/路径/窗口→正常退出重启同一包→同范围重建签第二个独占新包→比较两包DR相同、证书相同、每包strict verify通过。cdhash可以不同；不能要求重建字节完全一致作为稳定身份条件。UI仅公开合成环境，不调用Provider Key验证，当前B暂停不解除。签名/重启完整性通过不等于Keychain体验Pass；以后受控凭据测试须由PM明确恢复并由用户操作，不反复试密码。

失败保留新staging、固定错误码和非秘密收据，原运行包继续不动。重试复用同一专用身份、使用新的staging，不自动再生成证书。新钥匙串锁定时只允许用户系统交互，不保存密码。清理本次失败staging需按精确marker执行；不自动删除持久私钥、钥匙串或信任记录。身份损坏/过期/丢失则暂停，续期意味着新锚，需新的身份决定。

## 三、v8严格类型约定

所有对象均为**闭合对象**，仅允许列出的字段，全部必填，除明确标`?`者可省略；任何位置null、重复键、未知字段、NaN/Infinity及非法枚举拒绝。字符串按Unicode标量计数，另受总UTF-8字节限额。无自由形式扩展字段。

基础类型：`Id`为1～120字符、`[A-Za-z0-9_:-]+`；`Ref`为Host生成的轮内不透明Id，不能接受原路径；`Rev`为1～2^53-1整数；`Time`为0～2^53-1 Unix毫秒；`Short`为1～200非空白字符；`Content`为1～500；`Text`为0～2000。数组不允许重复引用。客户端Id仅作幂等nonce，不具有权限。

`Scalar = {type:"boolean",value:boolean} | {type:"number",value:有限number} | {type:"text",value:1..200字符}`。比较两端必须同类型；number不得隐式转换单位，text只允许eq/neq，boolean只允许eq/neq。

### 3.1 14个IPC的完整映射

入口统一 `{version:8,operation:<下表>,payload:<严格对象>}`，原16384字节上限不变。v4/5/6/7按既有精确路由保留；v8不允许借其他命令名调用相同operation。任何未列v8组合拒绝。

| IPC命令 | v8 operation及payload；未列operation均拒绝 |
|---|---|
| capture_record | `save_coordination_draft`：{requestId:Id,turnId:Id,expectedDraftRevision:0或Rev,text:1..1000}；修订0仅新草稿，空白拒绝 |
| resolve_request_context | `prepare_coordination_turn`：{requestId:Id,turnId:Id,expectedDraftRevision:Rev}；`confirm_coordination_query`：{requestId:Id,queryPreviewId:Ref,expectedRevision:Rev}；`prepare_coordination_second_send`：{requestId:Id,turnRequestId:Ref,expectedTurnRevision:Rev}；`cancel_coordination_turn`：{requestId:Id,turnRequestId:Ref,expectedTurnRevision:Rev} |
| send_source_ai_request | `confirm_coordination_model`：{requestId:Id,sendPreviewId:Ref,expectedRevision:Rev}；Host由预览决定first/second，不接受客户端phase/body/model参数 |
| get_context_recovery | `coordination_turn_status`：{turnRequestId:Ref}；`coordination_snapshot`：{offset:0..10000整数,limit:1..20整数} |
| decide_understanding_feedback | 无v8；既有反馈协议不变，不充当查询许可 |
| save_ai_provider_settings | 无v8；既有保存/测试/选择/启用语义不变 |
| get_ai_provider_settings | 无v8；既有只读设置入口不变 |
| get_today | 无v8；既有视图保持，v8行动沿原投影读取，条件另经snapshot读取 |
| connect_source_directory | 无v8；不以查询需求触发目录连接 |
| control_source_job | 无v8；不启动导入/刷新作业 |
| get_source_status | 无v8；既有来源状态不变 |
| authorize_source_target | 无v8；既有授权不转为任意工具授权 |
| get_source_evidence | 无v8；历史来源读接口不扩大 |
| import_apple_health_file | 无v8；不触发导入 |

统一成功外壳 `{version:8,operation:<对应operation>,result:<下列对应类型>}`；失败仅 `{code:<固定Code>}`，不透出原始错误、URL、Key或工具响应。

- save结果：`{turnId:Id,draftRevision:Rev,status:"saved"}`。
- prepare首轮/second结果：`{turn:TurnStatus,preview:SendPreview}`。
- confirm查询结果：`{turn:TurnStatus,query:QueryReceipt}`，查询可以失败但回合状态必须如实反映。
- confirm模型、cancel及status结果：`TurnStatus`；网络调用等待时UI只读status，不重发confirm。
- snapshot结果：`{items:SnapshotItem[0..20],nextOffset?:0..10000整数}`。`SnapshotItem={turnRequestId:Ref,turnId:Id,state:State,updatedAt:Time,receipt?:FinalReceipt}`；按updatedAt/turnRequestId稳定排序，权限过滤在Host内。

`State=first_ready|first_inflight|query_ready|query_inflight|result_ready|second_ready|second_inflight|committed|failed|cancelled|expired|outcome_unknown`。

`TurnStatus={turnRequestId:Ref,turnId:Id,revision:Rev,state:State,createdAt:Time,updatedAt:Time,deadline:Time,businessChanged:boolean,modelCalls:0..2整数,queryCalls:0..1整数,sendPreview?:SendPreview,queryPreview?:QueryPreview,receipt?:FinalReceipt,errorCode?:Code}`。未committed则businessChanged=false；ready态仅附其对应preview，committed仅附receipt；failed/expired/outcome_unknown必有errorCode。不可兼具两个preview，不向前端返回私有permit。

### 3.2 精确模型披露与许可

`SendPreview={id:Ref,revision:Rev,turnRequestId:Ref,phase:"first"|"second",expiresAt:Time,provider:"DeepSeek",modelId:1..200字符,purpose:"理解本回合并提出回答、查询或本地候选"|"依据本回合获准查询结果回答并提出本地候选",disclosure:Disclosure,systemPolicy:TextPolicy,exactBody:1..24576字节字符串}`。TextPolicy为固定版本策略文本、最多12000字节；purpose必须与phase一致。完整exactBody受24576字节限制，非客户端回传。

`Disclosure={currentUser:{ref:Ref,text:1..1000},conversation:{ref:Ref,text:1..1200}[0..4],targets:{ref:Ref,version:Rev,content:Content,status:"planned"}[0..4],conditions:{ref:Ref,version:Rev,content:Content}[0..4],sources:Evidence[0..5],capabilities:CapabilityPublic[0..3],queryResults:QueryResult[0..1]}`；targets与conditions合计最多4个且均属于本回合允许集合；conversation累计≤1200字符，sources最多3来源+2状态/记忆，全部Disclosure≤4096 UTF-8字节。first的queryResults为空；second恰1条且capabilities为空，禁止再查询。超限不截掉潜在目标使其看似唯一，返回budget错误/必要澄清。

`Evidence={ref:Ref,kind:"source"|"state"|"memory",version:Rev,text:1..800,validUntil:Time}`；仅当前获准、校验有效引用。`CapabilityPublic={id:<三Adapter枚举>,version:1,targets:{ref:Ref,label:Short}[1..4],facts:<该Adapter允许fact名数组1..4>}`。参数Schema为固定system协议，不由工具返回或模型改写。

Host私有模型许可：`{id:Ref,previewId:Ref,previewRevision:Rev,turnRequestId:Ref,phase:first|second,state:ready|consumed|cancelled|expired,expiresAt:Time,sessionId:Id,profileRevision:Rev,credentialRevision:Rev,catalogRevision:0或Rev,authorizationGeneration:Rev,disclosureRevision:Rev,consumedAt?:Time}`；字段只落本地packets，绝不发模型或作为模型权限输入。profile/model/目标/草稿/来源修订同时由不可变预览绑定；不对真实披露正文生成Evidence hash。重复确认返回原子状态，不第二次加载Key或调用。

第二模型预览由Host重新读取已验证结果及处理许可并组装，不能复用首轮个人内容许可去自动扩大；用户必须看到第二份精确披露并亲点确认。查询许可仅准读取，不准送模型；读取后可保留result_ready而不发送。没有许可时不给模型原始结果，也不新增后台发送。

### 3.3 模型输出与本地候选

第一轮/第二轮统一 `{schemaVersion:8,answerText:Text,candidate:Candidate}`，strict JSON，无工具token/SQL/路径。第二轮candidate禁止query_need。所有action/conditional均要求至少一条当前用户Span；来源不能替代用户指令。

`Span={messageRef:Ref,start:0..1200整数,end:1..1200整数}`，0≤start<end≤该消息Unicode标量长度；`Spans=1..4项`。`Action`为以下闭合联合：

- `{operation:"create",content:Content,evidenceSpans:Spans,sourceRefs:Ref[0..5]}`。
- `{operation:"adjust",targetRef:Ref,expectedVersion:Rev,content:Content,evidenceSpans:Spans,sourceRefs:Ref[0..5]}`。
- `{operation:"complete"|"cancel",targetRef:Ref,expectedVersion:Rev,evidenceSpans:Spans}`。

`Candidate = Action | {operation:"none"} | {operation:"clarify",question:Short,targetRefs:Ref[0..4],intent:create|adjust|complete|cancel|query|conditional|unknown} | QueryNeed | Conditional`。

`QueryNeed={operation:"query_need",capabilityId:<三Adapter枚举>,capabilityVersion:1,targetRef:Ref,arguments:<下节按能力唯一确定>,neededFacts:<对应fact名1..4项>}`。neededFacts须是arguments实际可返回项，模型不能用理由文本请求新信息。

`Conditional={operation:"record_condition",content:Content,evidenceSpans:Spans,condition:{join:"all"|"any",atoms:Atom[1..4]},consequence:Action,priorConditionRef?:Ref,expectedConditionVersion?:Rev}`。两个prior字段必须同现或同缺；已有条件必须属于本回合允许的条件引用（Disclosure.conditions的ref对应Host私有映射，不借行动targetRef寻找）。`Atom={factRef:Ref,operator:eq|neq|gt|gte|lt|lte,expected:Scalar}`；factRef仅指当前获准Evidence或QueryResult中的结构化fact，文本事实不能由Host自动转数值。无有效fact时必须clarify，已存在但unknown的fact可记录待定。

Host计算三值：all存在false则false，全true才true；any存在true则true，全false才false；其余unknown。模型不得返回自定truth。**record_condition仅保存条件和未执行consequence，不在同事务顺便执行Action**，因此最多一项业务结果；即使true也只是依据当前资料的条件判断，不变成未来自动任务。用户以后明确要求立即落实才在新回合提出独立Action，仍过原意图/目标/权限门禁。条件false不推出反向consequence；无第二分支，不替用户编造。此取舍须作为产品可见行为纳入批准，不能用“条件记录成功”文案假称行动已执行。

## 四、三个合成能力及严格结果

能力均为只读、无网络/路径参数，目标由Host静态公开fixture注册：`fixture.note.lookup.v1`、`fixture.schedule.lookup.v1`、`fixture.forecast.lookup.v1`，capabilityVersion=1。fixture与mock时钟在任务唯一offline/online-synthetic隔离根内；线上模型阶段工具仍是合成Adapter。以下参数不得由任意字符串扩展能力。

| 能力 | 唯一arguments与neededFacts | typedFacts精确类型及上限 |
|---|---|---|
| note | `{query:1..100,limit:1..3整数}`；仅`matches` | `{matches:{ref:Ref,title:Short,text:1..500,version:Rev,modifiedAt:Time}[0..3]}` |
| schedule | `{start:Time,end:Time}`，0<end-start≤7天；仅`entries`、`available` | `{entries:{ref:Ref,title:Short,start:Time,end:Time,version:Rev}[0..4],available:boolean}`；entries必须属于请求窗，available由完整fixture计算，不从截断列表推断 |
| forecast | `{start:Time,end:Time,fields:["rainExpected"]}`，0<end-start≤48小时；仅`rainExpected` | `{windows:{ref:Ref,start:Time,end:Time,rainExpected:"yes"|"no"|"unknown"}[1..4]}`，公开fixture直接给预测类别，不伪装真实API规则或实测天气 |

`QueryPreview={id:Ref,revision:Rev,turnRequestId:Ref,queryId:Ref,capabilityId:<枚举>,capabilityVersion:1,targetRef:Ref,targetLabel:Short,arguments:<上表>,neededFacts:<上表>,purpose:"补充本回合缺失资料",recipient:"本机公开合成适配器",dataClass:"public_synthetic",expiresAt:Time,maximumCalls:1}`。

私有查询许可：`{id:Ref,queryId:Ref,previewId:Ref,previewRevision:Rev,turnRequestId:Ref,targetIdentity:Ref,capabilityRevision:Rev,authorizationGeneration:Rev,state:ready|consumed|cancelled|expired,expiresAt:Time,consumedAt?:Time}`。只允许当前静态target对应fixture，无第二个参数解析器把ref解释成文件路径。

Adapter成功结果外壳：`{status:"ok",typedFacts:<上表>,sourceVersion:Rev,observedAt:Time,validFrom:Time,validUntil:Time,timezone:"UTC",truncated:false,issuedAt?:Time}`；forecast要求issuedAt，其他禁止issuedAt。note/schedule的observedAt为fixture版本时点，forecast为预测生成fixture时点，不冒称实际天气发生。失败结果仅`{status:"failed",code:QueryCode}`；无partial隐式成功。

Host持久并可披露的 `QueryResult={queryId:Ref,capabilityId:<枚举>,capabilityVersion:1,status:"ok",typedFacts:<上表>,sourceRef:Ref,sourceVersion:Rev,observedAt:Time,fetchedAt:Time,validFrom:Time,validUntil:Time,timezone:"UTC",authorizationGeneration:Rev,truncated:false,issuedAt?:Time,facts:Fact[1..4]}`。sourceRef/queryId/fetchedAt/generation及facts由Host从登记的typedFacts映射盖章；Adapter不能指定。`Fact={ref:Ref,name:<登记fact名>,value:Scalar|{type:"unknown"},sourceRef:Ref,sourceVersion:Rev,validFrom:Time,validUntil:Time}`；forecast yes/no映射boolean，unknown保持unknown；note matches仅生成完整返回匹配数number（含0），不自动生成语义boolean；schedule生成available boolean和entries数量number；forecast每个window各生成rainExpected boolean或unknown，最多4条。

行动sourceRefs及条件factRef只能引用当前披露中经Host映射的已有来源或QueryResult，不接受模型虚构/跨回合引用。

首批有效性明确：note/schedule取回后5分钟且sourceVersion未变；forecast取回后30分钟、issuedAt不晚于fetchedAt且过去≤6小时、完整覆盖请求时间窗。测试用固定时钟/公开fixture完成过期反例。这些时效仅适用于合成合同，不外推到任何真实供应商；缺issuedAt的真实接口未来必须另定策略，不能以fetchedAt或generationtime_ms伪充。

`QueryReceipt={queryId:Ref,state:succeeded|failed|cancelled|outcome_unknown,startedAt:Time,finishedAt?:Time,result?:QueryResult,errorCode?:QueryCode}`；succeeded必有result/finishedAt无error，其他无result且有error，outcome_unknown可缺finishedAt。总原始结果≤16KiB，任何超限/截断拒绝进入模型披露或条件判断。

## 五、状态、事务、重启和预算

### 5.1 有限协调

prepare创建turnRequestId与first_ready预览；首次model确认后first_inflight。终局候选经校验直接一次提交；query_need只落query_ready，不能先提交业务变化。查询确认原子消费唯一工具许可后query_inflight，成功校验进入result_ready。用户准备第二披露后second_ready，亲点模型确认才second_inflight；只允许终局候选。没有查询的回合不会创建工具许可或第二模型预览。second返回query_need直接失败，不递归。

整个回合180秒自首次模型许可消费时起，准备前不启动总deadline；first_ready时deadline字段为0，消费后设实际值。随后人工等待也计时。每份预览expiresAt=min(创建+5分钟,已有回合deadline)，不得自动续期。工具15秒、模型连接15秒/请求60秒，同时不得越过回合deadline。过期保留草稿和已完成查询历史，不续发。用户可用新回合重试但预算不回填。

模型调用前（含凭据等待后）、工具查询前、结果进入第二披露前、模型响应后及最终事务内复核：会话/草稿/turnRevision、许可、profile/credential/catalog修订、conversation/source/target授权generation、版本、时效、已取消/已完成标记。查询许可/模型许可分开；没有模型处理许可的结果不可进入第二exactBody。并发配置变化不能承诺“全系统瞬时撤销”，但已知失效必须阻断后续步骤；已发送不可假撤回。

### 5.2 仅追加JSON对象，原子提交

沿既有 `packets` 保存v8 turn/preview/query/permit/result/receipt，`sources` 保存独立累计预算，`requests` 保存各幂等命令，`records` 保存原文和action_event或condition_event，`feedback`/`derivations`保存本地反馈与回答，`drafts`更新提交状态。物理表/列/user_version不变，v8对象均带schemaVersion=8、kind和独立前缀`coord8:`，历史解析不重编号、不迁移；实施时验证旧投影忽略不认识的kind，若不能安全兼容则停并报差异。

`ConditionRecord={id:Ref,version:Rev,kind:"condition_record",schemaVersion:8,rawRef:Ref,content:Content,condition:<上述condition>,consequence:Action,truth:true|false|unknown,status:"pending"|"evaluated"|"superseded",basis:{factRef:Ref,sourceRef:Ref,sourceVersion:Rev,evaluatedAt:Time}[1..4],evaluatedAt:Time,consequenceExecuted:false,supersedes?:Ref}`。unknown为pending，其余evaluated；更正新版本事件指向原记录，不静默改原文。撤权使当前投影标basis无效，原事件保留，不自动执行consequence。新增事件原子使旧投影superseded，不覆写历史事件。

`FinalReceipt={operationId:Ref,turnRequestId:Ref,turnId:Id,state:"committed",resultKind:"none"|"clarify"|"action"|"condition",businessChanged:boolean,reply:Text,committedAt:Time,recordRef?:Ref,recordVersion?:Rev}`。action/condition为true且必有recordRef/version；none/clarify为false且无记录身份字段（原文/回答仍可落库）。reply来自固定本地模板或明确未更改安排的回答，condition须写“已记录条件；后续行动尚未执行”。不直接展示模型“已做完”作为事实。

最终原文、事件、反馈、回答、草稿状态、FinalReceipt、幂等结果同一BEGIN IMMEDIATE事务；失败全部回滚，无半条行动。查询过程与调用许可分别持久化，不用长事务等待人工/网络。Host分配唯一turnRequestId/queryId/model子请求Id/operationId；相同命令nonce+相同规范payload只恢复原结果，不再调用，不同payload报idempotency_conflict。每turn唯一final提交键禁止重复业务变更。

崩溃恢复：许可已消费但接收结果不明则outcome_unknown，重启不重发工具/模型；已存result_ready可只读查看，仍须时效/授权有效才允许用户准备新第二预览且不得重置deadline。已有committed恢复原回执；取消在途标cancelled并丢弃晚到响应，不把远程副作用说成已撤销。

### 5.3 完整固定预算（待批准，沿PM草案）

| 项 | 上限 |
|---|---|
| 单回合 | 1工具、2模型、1最终业务事务；无需查询仅1模型 |
| 模型每次 | Disclosure 4096 UTF-8 bytes（含查询结果）、HTTP体24576 bytes、输出1024 tokens；现有响应65536 bytes/16000字符保持 |
| 工具每次 | 16KiB响应、15秒、无重试/并发/后台 |
| 新协调开发集 | 8回合、8工具、16模型 |
| 新协调PM未见集 | 4回合、4工具、8模型 |
| 历史B | 14/40保留，开发14/24、未见0/16；不挪用原剩余额度，新增最多24模型须明确批准 |
| C/真实外部工具 | 本补充0次，不借原C8次额度 |

预算记录键`coord8:budget:development`和`coord8:budget:unseen`，各含`turns,queries,models`非负整数。模型/查询许可在不可逆进入Adapter前原子消费；若消费后进程中断也计数，禁止回填，称“许可消费数”而非全部证明已POST。另记非秘密Adapter接收次数用于区别实际调用。离线fixture测试用独立合成计数，不能写B真实累计预算。任一维度到顶则固定错误并保留草稿，不切模式/换模型/补请求。

固定错误集合：`dto_rejected,identity_rejected,operation_rejected,idempotency_conflict,revision_conflict,preview_stale,turn_expired,turn_cancelled,turn_in_flight,source_not_authorized,model_processing_not_authorized,capability_unavailable,target_rejected,argument_rejected,query_limit,model_limit,turn_limit,context_budget_rejected,query_timeout,query_response_invalid,query_response_too_large,query_result_stale,query_outcome_unknown,model_outcome_unknown,operation_response_rejected,action_version_conflict,condition_basis_invalid,confirmation_storage_failed,response_storage_failed`，以及既有固定Provider错误枚举。`QueryCode`限capability_unavailable/target_rejected/argument_rejected/source_not_authorized/query_timeout/query_response_invalid/query_response_too_large/query_result_stale/query_outcome_unknown/turn_cancelled/turn_expired。未知Adapter错误映射query_response_invalid，无原始内容透传。

## 六、验收、证据与执行门槛

三个fixture共用同一注册/路由/协调实现：已有资料足够零查询；note匹配解释；schedule查询后正确目标行动；forecast三值条件记录且false不推出相反行动。离线实际Host/IPC、故障注入、事务回滚和重启先通过，再经PM明确恢复进行真实模型+公开fixture测试。未见样本由PM在候选固定后提供，工程不能自造未见；修改后的已见样本保留为开发历史。

必须覆盖严格DTO每联合非法字段/重复/null/超限、二轮再查询、伪造许可/target、工具注入、读许可有而模型处理许可无、过期/撤权/修改/取消竞态、180秒等待、回执丢失、重启不重发、全部预算维度、条件三值/单位类型/单向逻辑、一次原子结果、中文与草稿。每个能力至少1正路径；不能靠全部拒绝Pass。语义误写、越权、重复、假成功任何一例阻断恢复C。

Evidence只含公开合成输入/fixture的内容与hash、源码/二进制/公开证书hash、固定错误/版本/调用计数/非内容收据。真实工具结果或个人正文不记Evidence、日志、截图或内容hash；私钥/密码/Provider Key从不记录。内部业务需要的原文/结果仍只按获准本地持久范围处理，不能以内部保存权推导导出Evidence权。

主责Codex工程/自检；PM唯一合同/验收者；独立评审按用户例外暂停，不能写Independent Pass。仅本任务目录增量交付，不改Frozen、ABF或PM账本，不创建新任务、不自动main合并、不关闭风险或切Stage。最终提交完整候选差异Manifest、单命令默认离线入口、v8逐行矩阵、调用预算及签名DR/实际包身份；已通过未受影响阶段不重做。

## 七、静态可行性结论和一次批准文本建议

事实：现有main注册恰14IPC；`Store::tx`已有requests幂等+BEGIN IMMEDIATE，JSON表容纳新kind；ModelPort不拥有仓库/工具权限；source-engine已有context/valid/send_fence和显式COMMANDS。需新增的是v8 DTO/分支、小型能力描述表与有限子状态、条件投影；不能声称现有v7不变即可完成。静态核对不等于编译/迁移/运行验证，本轮未修改候选。

本机命令help确认create-keychain可用SecurityAgent密码提示、add-trusted-cert支持用户域codeSign限定；未验证证书助理实际页面或密钥生成能力，执行遇到不符必须停在精确步骤。**不存在已验证的无任何信任调整、又保证免密码提示方案**；本文选择默认不改信任且允许签名尝试失败，绝不以扩大Provider ACL解决。

建议PM最终给用户一个整体选择：“批准在新专用钥匙串内建立上述本机签名身份并尝试完整包签名；不修改任何证书信任或Provider ACL，失败保留暂停。同时批准本合同v8协议及三个公开合成Adapter实现、离线验收和独立新增24次模型预算；每次真实模型发送仍由我亲点，B恢复需签名与离线门槛通过。真实外部接口和C不开放。”

该选择明确不包含窄codeSign信任；若平台必须要求它，报告该具体必要差异再决定。用户无需填写DTO或选择阈值。当前仍是待批准方案，不执行以上引用口令。
