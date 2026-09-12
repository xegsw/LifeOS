# P3-158 自然对话本地操作主链修复——完整修订合同

2026-09-10，Approved / Authorized to Start，L3，用户明确回复“确认启动”（D-0665）。本完整合同及ABF v1获同次批准；新增真实模型用途、v7协议、披露、预算、真实目标与条件式App切换按下文执行，不借旧D-0661/0662代替。本结果级任务包含A/B/C三阶段及同范围修复，不拆微任务。157保持真实验收未通过/停止旧路线，不追认Complete。先启动A，B/C必须满足前置门槛及逐次云端确认。

## 1. 唯一结果

同一个完整LifeOS App内，正常表达经模型理解后正确作用于正确本地事项，状态与事务反馈一致，正常重启后保持。歧义仅问必要问题，不要求固定句式、任务卡或同义确认。模型返回操作候选，宿主拥有最终执行权；只限本地安排创建/调整/完成/取消，非外部执行或自动规划。有限测试不保证开放域零误解。

## 2. 身份与直接输入

权威身份表：`LIFEOS-P3-158_identity_and_reconciliation.md`。待修复完整源码为`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-157/closure-1/candidate`（174文件）。其169个Git快照文件与e78d6feab07f2328b5f0bac680c6c7aad5f73995完全一致；剩余5项为快照未收录资产，不冒称174全部已远端同步。以完整本地Manifest及构建入口Cargo.toml为输入，不从main/旧HEAD重建。

只读输入：用户`/Users/xxe/Downloads/lifeos_repair_handoff.md`（SHA256 51ba1d2c3c77f77c50783330a339405c1c1211b41b69bffc1078923ba7bf244b）、157主合同/ABF/更正说明、157 Closure-1交付/Manifest、155限定真实及156限定离线PM Review。历史全部只读。原工程会话`01a07f0e-dbbd-7d23-9e6d-68f2152f9484`顺序实现，PM唯一账本/验收负责人；不新开缩减演示App或独立评审任务。

## 3. 修改范围与保留能力

新工程目录：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-158/`。唯一新合成/构建根：`/private/tmp/lifeos-p3-158-main-chain-v1`，0700根、0600精确owner marker，必须独占，子目录offline、online-synthetic、build各隔离；不得接管未知既有根。

继承清单：Shell/Settings布局及Provider配置选择、Key加密持久无TTL、保存/测试/选择/启用分离；来源浏览/授权/更新、Obsidian及Apple Health已验收范围；普通对话、草稿、154错误归属、155更新恢复；156/157既有Action事件、反馈及身份。逐文件差异→接线→受影响行为回归，不用CSS未变替代功能证明。

必须改通controlled_conversation.ts统一回合、action_application.ts实际ModelPort、action_domain.ts候选校验、Host actions.rs/controlled Provider边界、health_ui.ts回执展示。移除旧词句分类器作为生产必经入口及“候选必须等于本地句式解析”校验；不静默回退旧规则。UI/TS不直连网络、Keychain或SQL，真实网络仍在既有Host Adapter；OfflineA/B只作为测试替身。

## 4. v7请求、模型候选和持久化语义（本次拟批准差异）

14个公共IPC命令名不新增，v4/v5/v6历史读取兼容；新增version=7，不能声称无API变更。保留旧数据解析但新实际对话入口不调用旧v6句式链。物理SQL表、列及user_version不变：沿既有JSON表追加v7请求/披露/候选状态与回执，复用Action event/feedback投影，不重编号旧事项、不迁移旧行、不新建第二库。若现有表不能原子满足则停止该阶段提出精确增量，不能绕过。

| 命令/operation | 严格payload与输出 |
|---|---|
| resolve_request_context / prepare_operation_turn | 输入requestId、turnId、expectedDraftRevision；Host读取真实草稿和相关上下文，创建request/preview/operation身份及绑定；返回previewId、revision、expiresAt、provider/model、用途、精确披露内容和refs，无候选写操作 |
| send_source_ai_request / confirm_operation_turn | 输入requestId、previewId、expectedPreviewRevision；Host读取持久预览和授权，原子消费发送许可，最多一次模型调用；不接受前端或模型提供的body、modelId、目标全集或授权令牌 |
| get_context_recovery / operation_turn_status | 输入宿主返回的requestId；纯读取持久发送/执行回执，不重发、不重写、不重新理解 |
| get_context_recovery / action_snapshot | v7沿已有有界分页语义，提供身份/当前状态/历史refs/依据有效性 |
| resolve_request_context / cancel_operation_preview | 输入previewId、expectedPreviewRevision；只撤销未发送许可；发送后标停止等待，不假称撤回网络或自动撤销已提交行动 |

未知/null/重复字段、非法版本/操作组合、超限严格拒绝。传输IPC原16384字节上限保持；不把大上下文从UI回传，Host内部组装。

模型输入为明确分区的system policy、current_user原文、conversation_context、allowed_targets、evidence_sources；refs均为本轮不透明引用并在Host映射原ID/版本/授权generation。来源/引用/旧模型回答不能充当当前用户指令；用户回合与讨论主题绑定，不能因历史只有一个待办就认定“那个”。

返回严格JSON：schemaVersion=1，answerText（最多2000字符），candidate。candidate是判别联合：

- none：仅operation=none。
- clarify：operation、question（最多200字符）、targetRefs（0至4个当前允许目标）、intent（create/adjust/complete/cancel/unknown）。
- create：operation、content（1至500字符）、evidenceSpans、sourceRefs。
- adjust：operation、targetRef、expectedVersion、content、evidenceSpans、sourceRefs。
- complete/cancel：operation、targetRef、expectedVersion、evidenceSpans。

evidenceSpans为最多4项{messageRef,start,end}，偏移统一Unicode标量、必须指向已披露用户消息，至少一项当前用户表达。它们是模型主张，不是授权证明；模型不得返回requestId/token/path/SQL/tool/可生效authorization。未知字段和越权refs拒绝。不得把合法JSON、高confidence或模型“已确认”当意图证明。Adapter是否支持JSON格式提示先在A离线验证构造，B验证真实兼容；不自动换模型/协议，格式约束仅辅助本地校验。

Host保留请求与预览可信关联，复核当前草稿版本、主题/指代链、候选目标在本轮允许集合、来源权限/有效性、expectedVersion、合法状态迁移。条件/引用/否定或目标无法证明无歧义时不执行并澄清；不靠全部拒绝达标。语义判错残余风险由非执行策略、用户可纠正历史和独立于实现的验收样本限制，不声称确定性守卫证明语言含义。

宿主分配operationId，在同事务内追加原始表达/行动事件/反馈/执行回执、更新草稿与幂等结果；同请求同payload返回原结果，不同payload拒绝，同turn同操作至多一次业务变更。模型候选只能被本已确认请求接收一次，晚到/超时废弃响应不事后执行。提交结果不明按operationId只读恢复。取消/完成不复活；来源失效不静默删除原行动。

操作成功显示固定本地事务回执文案；校验/提交前不流式显示模型“已完成”。none/clarify可显示回答/问题，但要明确“本轮未更改安排”，模型答复区域不成为持久状态权威；任何失败不能冒充成功。成功反馈与Today仅从存储结果读取。无新增必经按钮，已有云端逐次确认继续。

## 5. 最小披露、调用预算与Provider（一次锁定）

仅当前已配置并启用的DeepSeek及已选model ID，不自动升级、换Provider、fallback或更改凭据。当前ID本轮未读真实配置；B开始由用户在既有Settings确认，Host记录非敏感配置指纹并固定B批次，配置变化使预览失效且停止该批次，不猜ID。

每次预览显示用途“回答本次问题并理解本地安排”、目标Provider/model、精确用户内容/对话/目标内容/来源摘录，用户可取消或缩减；不披露Key。用户点发送仅授权本次网络，不等于任意写入。明确意图及无歧义目标仍必需。预览5分钟过期，发送前及事务前复核版本/权限；上下文或配置变化需新预览，不静默补内容。

固定预算：当前用户原文最多1000字符；相关旧消息最多4条、最多1200字符；候选安排最多4个；来源最多3项、状态/确认记忆最多2项。**全部个人披露JSON（含原文、对话、目标内容/refs、来源）总计最多4096 UTF-8字节**，比旧仅items4096更严格；预算不足不得因截断目标集合误认为唯一，可澄清或拒绝发送。system/schema等固定内容加完整请求体不超过旧24576字节。输出max_tokens=1024不扩大；总响应沿旧65536字节及16000字符上限，解析后以上字段限额更小。连接15秒、请求60秒，截断/空响应/非JSON/错误类型/未知操作一律无行动变更，保留草稿。

每次确认最多1次POST https://api.deepseek.com/chat/completions，stream=false；不拆解析+回答两次，不工具循环、不自动重试/修复JSON请求、不隐式/models探测。失败重试也必须新预览和用户确认，算新调用。C真实验收最多8次确认请求（含失败/重试），仅用户操作；预算用尽停止，不以重新开会话清零。

## 6. 三阶段、真实目标及凭据边界

**A 离线安全**：仅新根内合成库、替身响应，真实凭据/库/网络零接触。必须实际Host/IPC及完整App回合覆盖，非仅纯函数。只调整必要合成/real-online-test构建隔离，三模式强互斥，不把旧synthetic-driver可直接接真实数据。

**B 真实模型＋公开合成资料**：A通过后，同完整App同生产Host/Provider代码，仅存储根换online-synthetic，不混入真实对话或来源。只从既有provider.sqlite读取非内容配置与加密凭据引用，由Credential Port取钥匙串对应密钥在Host内解密；不拷贝真实库/密文/密钥到测试根，不把Key放命令行/日志/脚本/环境。固定service `com.lifeos.p3-152.aead-key.v1`和严格旧account `p3-152-key-[0-9a-f]{32}`，不枚举/重建/重录。B不关闭真实App、不夺真实库写锁；若只读凭据接口无法与当前App共存，停止报告，不能私自停App或复制库。

B总上限40次真实POST，开发集最多24、PM未见表达最多16；失败/重试均计入，不自动重试，预算持久化并跨重启保持。每个完整App预览仍需用户逐次确认（Agent可在合成模式准备输入和核验状态，但不代点云端批准）；本合同批准测试用途不代替逐次发送。PM在实现之外准备未见样本，执行方在候选固定后才获其内容；失败修改后原未见集不得冒称仍未见，剩余预算内换新样本。所有真实返回可能含异常敏感串，脱敏后方可记录公开合成结果，Key及原始传输日志禁存。无新的Provider或测试API Key。

**C 真实最小验收**：A/B全部业务门槛通过才准正常切换。现有固定范围：

| 目标 | 允许 |
|---|---|
| `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/conversation.sqlite` | existing-only，App读取相关对话/安排，按新v7语义追加请求/披露/操作/反馈/回执，保留旧记录；不迁移物理Schema |
| 同父目录provider.sqlite、`.lifeos-p3-152-owner.json`、`.runtime`及必要SQLite副文件 | 沿既有读取配置、密文和单实例锁语义，不更名/补建/重置 |
| 同父目录source-engine-v1/sources.sqlite及已有artifacts缓存 | 只在请求需要且授权时读取少量上下文；不刷新/重导/全库总结 |
| `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite` | 已有授权只读上下文；无医疗用途，无再导入 |
| 上述既有Credential Port | 仅既有选中凭据，Host内部使用，不暴露明文 |

Agent不读C真实正文/安排值/DB内容/Key/AX/截图/内容日志/hash，不重放真实操作。用户仅回复结果或固定错误码。原始Obsidian目录、Downloads ZIP、新来源和其他Pilot均不访问。原有来源/导入模块保留代码与合成兼容验证，不代表本合同授权Agent操作。

旧包精确目标`/private/tmp/lifeos-p3-157-real-actions-v1/closure-1/LifeOS P3-157 C1 Real Actions.app`；切换前重核实时PID及binary身份（历史89047不是永久PID）。正常退出、确认锁释放后，启动新根下`LifeOS P3-158 Main Chain.app`完整最终包；claim先写，回执和proc_pidpath绑定。身份/锁/Schema不符则停止，不强杀模糊PID、删除锁或盲启。旧包保留，但新v7写入后不得让不兼容旧包回退写库。当前合成/其他实例不擅自清理。

## 7. 验收、交付及治理

独立任务ABF见`LIFEOS-P3-158_acceptance_basis.md`，已随D-0665锁定v1，仅本任务验收依据，不改变全局冻结。关键标准是正确目标、真实本地状态、诚实反馈及重启连续，不以检查数量替代。A/B/C缺一不Complete。误写、重复业务变更、越权、假成功在验收集任一项阻断真实切换；明确创建/更新不能靠全部澄清拒绝过关。

L3逐行结果、身份Manifest、关键守卫反例/mutation、历史保全；角色：原Codex工程实现/自检/修复，PM测试未见表达并验收，独立评审依用户决定暂停、不伪称Independent Pass。PM首次问题一次列齐合同内Closure，同任务修复。环境锁屏/截图/容量Paused—Resumable，checkpoint记录candidate/config/budget/许可/操作身份及resume_from；恢复只做受影响阶段，不重发或清零预算。只读历史被改或禁止真实内容接触等不可分离污染按治理记录，不掩盖。

CI只放确定性合成测试，B/C不进无人值守CI。UI仅回合处理和回执，按影响复用未变视觉，不造缩减App或堆截图。不得绕过平台URL限制。未经批准不调用在线模型、不操作App/真实数据/凭据、不同步远程；本次仅合同落盘。批准后安全代码文档可按用户长期同步边界推任务分支，不自动合并main，不上传真实资产，不关闭风险/冻结/切Stage或启动后继。

四项交付：完整累积App及源码构建身份；受影响能力差异/兼容表；单命令离线复跑和分开的A/B/C结果；最新源码/参照验收/运行版本/下一步身份记录。主报告`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/deliverables/LIFEOS-P3-158_main_chain_repair.md`，工程根含checkpoint/矩阵/Manifest。复跑入口必须默认离线，在线路径需App逐次批准。

必读：5ed8 AGENTS、CURRENT_STATUS、本卡/ABF/身份对账、SESSION_REPORT_TEMPLATE、D-0663及155/156 Review；原157/C1最终报告与上述主链源码；PM_OPERATING_MODEL/ROLE_MATRIX/STAGE_GATES/ACCEPTANCE_GOVERNANCE的真实权限、协议与用户暂停例外，CI_CD_GOVERNANCE的完整继承/可恢复执行，架构V1.0 Action/ModelPort/权限及IA Today/GlobalAI。不全文翻所有历史，不减少直接高风险输入。

用户已批准本完整范围，一次授权A/B/C实施、测试、包内修复及条件式切换，不把各阶段另拆审批任务；逐次云端确认作为产品权限动作仍保留。新增真实目标、预算、Provider、关键协议/迁移等实质差异才再批准。当前派发原工程会话从A启动；旧App暂保持不变。
