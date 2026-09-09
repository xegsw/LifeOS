# P3-148 状态机、发送幂等与纠正

状态：设计提案，尚未执行。01定义外部DTO，02定义存储，03定义凭据/Transport。

## 用户完整路径

App启动只显示本地会话说明，不打开真实DB、不扫描、不访问OS凭据或网络。用户点击“打开已有本地会话”后只连接已有业务库、恢复草稿与会话；不会调用147的connect_source_directory自动导入。对话输入→本地保存→自动检索→披露预览；用户不需手点“组装上下文”。无匹配显示“当前已导入资料中未找到相关依据”，本任务不做无来源自动回答。

凭据遗留操作仅在用户激活本地存储后按本地日志显示“待恢复”，read_settings不查询或删除OS条目。用户明确点击“恢复凭据操作”（01新增拟operation），或执行保存/删除动作后，才按03处理获准148引用；无后台OS清理。恢复会话、网络测试、发送、退出都不能隐式执行凭据恢复。

Settings保留Cloud/Local目录、主导航、高保真样式和独立配置状态。固定代码`application/ui.ts:9`的8个云端目录项和4个本地目录项逐项保留：OpenAI、Anthropic、Google Gemini、DeepSeek、Kimi、OpenRouter、其他OpenAI-compatible服务、自定义兼容接口；Ollama、LM Studio、OpenAI-compatible本地接口、自定义本地服务。DeepSeek仅在相应Gate后可用，其他项状态说明真实，不缩减目录、不隐式启用或探测。现有来源检索/详情和断开可用；148真实会话模式的扫描按钮明确显示未启用，不悄悄沿用147授权。

## 状态转移

| 当前状态 | 事件/前置 | 原子结果与可见行为 |
|---|---|---|
| draft | 自动保存草稿 | CAS revision，成功显示已保存；DB失败保留当前编辑器文本，不能谎报已持久化 |
| draft_saved | 点击“提问” | 消费确切draft revision，records/draft/receipt事务提交→question_stored；同turn身份只一条 |
| question_stored | 自动本地检索 | 有界查询已导入当前授权段→preview_ready；失败仍保留问题，无二次保存 |
| retrieving | 无可用匹配/全被排除 | no_match，显示原因，无token、无发送按钮，不调用OfflineA/B伪造答案 |
| preview_ready | 用户移除片段或改问题/配置/纠正、来源版本/grant/epoch变化，或5分钟过期 | 旧包status=stale，token失效；明确重新生成预览，绝不沿用旧确认 |
| preview_ready | 用户取消 | cancelled，零发送；再次提问/预览须新ID/token |
| preview_ready | 用户点击“确认并发送”且所有CAS/有效性通过 | 先事务持久化dispatching并消费token，再触发一次Transport；UI显示发送中 |
| dispatching | 有效响应、结果落库成功 | succeeded，显示回答+来源；answer/dispatch结果同一业务DB事务 |
| dispatching | 服务商明确失败且状态落库成功 | failed，显示固定类别；没有自动重试 |
| dispatching | 超时/连接不确定/进程崩溃/发送后落库失败 | outcome_unknown；显示“可能已发送，结果未确认”，不自动重新发送 |
| succeeded | 用户helpful/reject | 仅对应feedback；helpful不是确认用户事实，不要求每条必评 |
| succeeded | 用户correct | 保存独立纠正原文+feedback；受影响回答和待发送预览失效，历史原文不改 |
| 任意 | 重启 | 恢复可见状态；ready预览统一stale需重新预览；dispatching变outcome_unknown；成功回答/反馈保留；零后台发送 |

人工重试网络必须显式“重新预览”，生成新preview/dispatch并再次确认；原不确定尝试永远保留。用户更改问题形成新turn，不能改写已发送问题。仅本地保存/读取失败可沿用requestId无副作用重试。DB不可用时编辑器可保留内存草稿但跨崩溃持久化Unknown，不承诺无法保证的恢复。

## 检索和预览权威

SourcePort针对已导入、授权有效、当前版本、parsed、非配置/疑似秘密段进行本地查询。沿用`source_store.rs:536–581`词项评分，去中文停用双字/英文停用词后稳定score DESC、ordinal、ID排序；仅允许已导入Obsidian根connector，排除外部目标connector。最多8候选→去重→最多3片段，每片从首个命中位置取最多800 scalar连续窗口，保留offset/locator，总计≤2400。不切全文件上传；无词项或无匹配为空，不从通用snapshot任意补满。

SourceRef绑定segment/record/file版本、connector grant和scanEpoch；预览生成、发送前和来源点击分别复核。授权/已知版本的判断由同一SourceValidity能力实现，不创建第二grant账本。记忆/state不自动加入，只有当前问题、本次相关来源、与这些inputRefs对应的用户纠正进入显式预览。旧resolver的L1/L2保留给旧离线用途，不在148暗中带入。

纠正条目标为用户表达F1…，不能成为Source Citation C1…。一次最多3条相关最新纠正且总计≤2000 scalar；如果存在相关有效纠正超出预算，返回context_budget_rejected并提示收窄问题，不能静默丢掉纠正后复活被否定理解。移除片段后该片段相关纠正同步重算；所有变化生成新包与token。

后端根据已保存问题和数据库片段形成完整bodyJson、随机previewId/token，不接受UI提供的“授权=true”、新文本或哈希作为权威。token仅当前会话有效、5分钟过期、一次消费，重启失效。真实性不是由token本身保证，而是后端精确保存包、字段绑定和最后有效性复查。真实内容不做hash；字节相等在App内比较，不能导出到Evidence。

## 并发、撤权与发送线性化

所有148写入/凭据更改/发送前检查通过单一进程协调器，锁顺序固定为profile锁→业务事务，禁止反向获取。先验证provider/credential revision并短时解密，再取得业务写事务复核question/version/grant/epoch、预览字节和token。提交dispatching作为发送许可消费点；**提交失败零Transport调用**。事务提交至Transport接收不可再被本进程配置修改或撤权插入，协调器串行完成这一步，然后释放锁；不得持有SQLite事务等待完整网络响应。

在受148协调器控制的操作内，撤权若在许可消费点之前生效，必须零发送；如果之后发生，属于已授权开始的请求，只能使后续使用失效，不能保证召回已发送字节。响应回来再校验，已撤权/版本变化的回答仍可作为历史显示，但status=stale、引用不可当当前有效证据、不进入后续上下文。`p3-148-session.lock`只防多个遵守锁的148实例，不约束147；用户先关闭147且使用148期间不重开147是操作前提，锁不能自动阻止147重开。上述线性化断言不覆盖跨版本147并发写入；跨版本并发安全未证明，也不声称任意同UID外部修改的全局原子性。不修改147、不新增进程探测来填补此限制；合成互斥验证仅覆盖148实例。

同preview重复点击（即使不同requestId）返回同dispatchId；有唯一的preview→dispatch映射，状态不能退回ready。同requestId异参数冲突。崩溃点“已持久dispatching、尚未实际发送”也记outcome_unknown，宁可要求重新明确确认，不承诺服务商恰好一次处理。超时/已调度错误不会再次调用Transport；不会轮询模型接口找回回答。read_answer/恢复只读取本地。

## 引用与反馈

引用格式仅`[C1]`…`[C3]`，来源集合由本次bodyJson产生。模型返回C99、外部链接、任意路径或HTML均作为不可信纯文本，未绑定ID不成为链接/证据；记录invalidCitationCount并显示“部分引用无法核实”。有效citation只代表确有提交该段，不代表段落支持模型全部断言或事实已确认。来源命令/提示注入作为原文，不赋予工具、权限或系统指令地位；UI转义文字，不加载远程图片。

点击有效引用→固定sourceRef/expectedVersion的本地分段详情；若版本改变/撤权，显示旧依据失效，不跳转到另一新版制造引用成立。不启动网页、OCR、播放器或外部文件程序。

correct反馈事务：校验answer revision及所有affectedCitationIds归属→保存用户纠正record与feedback→目标回答stale/revision+1→使依赖目标或相同受影响inputRefs的未发送包及派生失效→meta递增/回执提交。范围仅当前会话及明确依赖链，不按相似文本全库污染。无affectedCitationIds时仅目标回答/其派生依赖失效。后续检索保留原始来源、单独展示纠正；纠正不是修改来源事实。拒绝旧answer revision重复消费，重启之后相同规则有效。

## 恢复与结论边界

动态阶段才写checkpoint，合同/候选/基线摘要及禁止接触情况绑定；锁屏/AX/截图环境问题Paused — Resumable，只复跑受影响阶段。工程测试、actual合成App、用户真实亲验、安全独立结论分列。本设计没有动态状态或真实截图，不伪造checkpoint、完整任务Pass或安全Pass。
