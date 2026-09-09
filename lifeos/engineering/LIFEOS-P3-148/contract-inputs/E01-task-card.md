# LIFEOS-P3-148｜来源支撑的 AI 对话与可追溯反馈闭环

## 生效授权：工程启动（优先于以下设计期记录）

### PM 同包勘误 E01：当前会话草稿恢复

为满足已批准A01及重启恢复，允许既有v3 `get_context_recovery` 返回的 `ConversationPage` 增加可选 `pendingDraft:{draftId,conversationId,turnId,revision,text,requestId}`。字段沿用01既有ID/整数/草稿文本规则；只返回后端绑定当前已激活会话的最新pending草稿，无草稿则省略，不接收客户端正文覆盖，不返回其他会话或已提交草稿。requestId必须是该草稿绑定的非秘密操作ID，不能携带凭据、确认token或其他请求payload。

此为原验收目标所必需的返回契约漏项补齐，不增加IPC、持久表、写路径、权限或真实数据类型；PM批准同包实现，无需用户重复授权。五份原封存输入保持只读，另存E01增量及摘要。补齐T01/T02/T25相关草稿恢复测试及未知字段拒绝、跨会话隔离、已提交草稿不复活测试；不要为此重做无关阶段。该批准不是新增真实操作或完整任务Pass。

用户在完整边界清单与两处澄清已展示后明确回复“开始开发吧”。PM据此授权同一P3-148进入工程实现，不再要求重复创建/启动确认。以下原“只读设计”“待批准”文字仅保留历史语境，以本节为当前合同。

正式继承b3f6工作树 `lifeos/engineering/LIFEOS-P3-148/design/01-ipc-contract.md`、`02-storage-mapping.md`、`03-credentials-and-transport.md`、`04-state-machine.md`、`05-validation-and-approval.md` 的当前补正版本，包括recover_credentials显式动作、26 IPC/11项v3分支、两张provider表、零旧业务库DDL、启动零OS操作和148锁不约束147的限制。工程开始前将这五份输入及摘要保存在148包内contract-inputs，不得之后静默改合同。

立即允许：在b3f6工程会话切换至新本地分支 `codex/l3-p3-148-source-ai`，保留现有148设计与报告；只在 `lifeos/engineering/LIFEOS-P3-148/`、`lifeos/deliverables/LIFEOS-P3-148_source_backed_ai_conversation.md`、`lifeos/reviews/LIFEOS-P3-148/` 写入本任务成果。只读复制固定147 candidate至148，不修改147。唯一合成临时根 `/private/tmp/lifeos-p3-148-source-ai-v1` 可按marker合同创建、构建、测试、运行合成actual Tauri、检查点恢复和精确清理；不得接触其他临时根或真实数据作夹具。无网络依赖下载，使用已有工具链离线构建。共享CI文件本次不改，可先提供任务内CI调用入口。

验收采用A01–A09及设计T01–T25；实现、回归、合成GUI、Manifest和包内普通修正均在本任务完成。全功能风险L3，必须诚实区分工程Pass/独立安全评审/PM验收/用户真实亲验。专项可准备逐行ABF候选，但不得自行冻结或自评为独立Pass；新增真实安全边界的评审由PM在工程包提交后安排，147 waiver不自动继承。平台拒绝测试不得改名/转派规避；环境问题按checkpoint续跑。

用户此次批准已展示05末节真实范围：已有Source-Pilot-1业务库对话读写及必要副文件、148锁；新p3-148-provider.sqlite及148唯一OS service；用户输入Key加密持久化；用户测试DeepSeek models及逐次预览确认chat请求。**执行顺序仍先合成与安全Gate、后用户亲自在App激活**。本轮工程Agent不得打开真实profile、探测真实根/DB/凭据、停止用户旧App或发送网络请求；这不是新的授权问题，而是已批准的阶段门禁。真实操作前提醒用户关闭147且使用148期间不重开。真实内容不进入日志/AX/截图/hash/Evidence。

保持所有视觉/Provider目录、持久化语义不回退；不迁移、覆盖、清理旧数据、不后台发送、不fallback、不工具调用、不push/merge、不改变风险、Frozen或Stage。PM状态：P3-148 Engineering In Progress；旧CURRENT_STATUS的144索引不是当前专项分派权威，按本节与147固定报告执行，不重启144。全局账本对齐由PM负责，专项不改。

状态：In Progress — 合同补齐阶段已启动；产品实现与真实阶段按下述门禁执行。风险：完整结果 L3，当前只读技术设计 L0。2026-09-08。授权依据：用户“那就补充，然后启动”。未展示的真实网络、凭据和数据库变更不由此自动授权。

## 当前执行合同（优先于文末旧 Draft 记录）

主责：PM；专项执行复用已结束 P3-147 的工程会话，只进行本任务的技术合同补齐，不再修改147。当前允许专项立即执行：只读固定代码与项目文档，在 `lifeos/engineering/LIFEOS-P3-148/design/` 写出可实施的存储、IPC/DTO、凭据和发送集成设计，以及 `lifeos/deliverables/LIFEOS-P3-148_source_backed_ai_conversation.md` 阶段报告。不得编译、启动App、扫描用户Vault、探测Pilot、访问凭据或网络。不得先修改生产代码再补合同。此阶段不另建任务号。

固定只读输入：b3f6 工作树提交 `5c26431ca43d68b77ab3d91a715dd59444a62e2e` 中 P3-147 candidate、design、最终报告和非内容 local-functional-final-status；本卡及 PM closeout `/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-147/pm-delivery-closeout.md`。读取最小启动包、TASK_BRIEF_TEMPLATE、SESSION_REPORT_TEMPLATE；定向补读 ACCEPTANCE_GOVERNANCE、CI_CD_GOVERNANCE、PM_OPERATING_MODEL 的授权/验收章节及 Frozen V1.0 的 SourcePort、ModelPort、权限/存储章节。旧 CURRENT_STATUS 停在144须披露，不据此复活历史任务。专项不得改PM账本。

设计必须给出五项可复核结果：1）准确列出现有25项IPC与建议最小差异、严格DTO及错误码；2）复用 records/drafts/feedback 的映射及是否确需新表，禁止先迁移真实库；3）保持 API Key AES-256-GCM 密文持久化、独立OS密钥材料，列出新引用策略，禁止借用/枚举旧凭据；4）本地检索→预览→确认→网络→回答→引用→纠正→重启的状态机和幂等合同；5）完整离线验收矩阵、合成夹具、复跑/恢复入口以及真实阶段单次批准清单。

已核对 secure_credentials.rs 保留 AES-256-GCM 与 P3-144/145 历史 service 常量，但当前 main.rs 未链接它；不得直接启用历史常量并访问旧 Keychain。新的存储/引用策略须在设计中明确后由PM核对，不改变用户已确认的加密持久化产品行为。

当前阶段 Pass：上述五项具体到实现位置，列出真实边界和未知项，所有路径由代码/文档支持；不要求大型Manifest或独立评审。阶段输出不得写完整任务Pass。随后PM将精确API/存储合同纳入本卡，启动合成工程；若涉及新增关键Schema/API或未获准真实边界，集中一次展示并确认，不把技术选型抛给用户逐条回答。

后续工程拟唯一合成根 `/private/tmp/lifeos-p3-148-source-ai-v1`，当前不创建/探测。真实阶段继续暂停，直到真实存储、凭据、目标和安全验证合同明确。独立评审针对新增真实安全边界，147豁免不自动继承。锁屏/截图异常按checkpoint续跑；禁止测试仍禁止，不更换表述或执行方规避平台检查。普通包内缺口在本任务修正。当前不push/merge、不冻结、不关闭风险、不改变Stage。

## 唯一结果

### 技术设计提交与待批准增量（2026-09-08）

已收到b3f6工作树 `lifeos/engineering/LIFEOS-P3-148/design/01-ipc-contract.md` 至 `05-validation-and-approval.md`，设计阶段文档已交付，尚无工程或真实验证。PM建议采用25→26 IPC（新增显式send_source_ai_request）及11个既有命令的v3分支；复用现有records/drafts/packets/derivations/feedback，不对旧业务库执行DDL。JSON语义仍属于待批准关键存储合同。

真实阶段拟在已批准来源根内读写capture.sqlite中的对话对象，新增p3-148-provider.sqlite（provider_profile/provider_operations两表及SQLite副文件），保留API Key AES-GCM密文跨重启；新OS service com.lifeos.p3-148.aead-key.v1，不读取或复制旧Key。以上新文件/OS操作/业务库新写入和网络尚待一次明确批准。

网络仅用户测试GET https://api.deepseek.com/models及逐次确认POST https://api.deepseek.com/chat/completions；最多3个相关片段、每片800字符，总来源2400字符；问题和纠正分别最多2000字符，总请求24KiB。禁止背景发送、fallback、自动重试；结果未知必须明确显示。原文、问题、回答不进入Evidence。8云/4本地目录和原视觉保持，不将受控DeepSeek范围解释为删除其他Provider。

PM已要求两项包内文档澄清：启动不得自动查询/清理OS凭据，恢复只能用户明确触发；148锁仅保证148实例间互斥，旧147须先由用户关闭，不能宣称该锁约束147。澄清不扩大范围、不启动实现。设计尚非完整L3 Pass，合成测试/必要新边界独立评审/真实亲验仍未执行。

用户自然提问，LifeOS从已导入Obsidian资料本地检索最小相关片段，展示本次请求及披露内容；用户确认后仅向DeepSeek发送，回答在当前对话清楚可见并能回到来源；用户纠正后旧理解失效，重启保持状态。一个结果任务包含实现、回归、Evidence、用户亲验和同范围修正，不拆微任务。

## 依赖和准确状态

P3-147固定交付仓库 `/Users/xxe/.codex/worktrees/b3f6/No.2`，提交 `5c26431ca43d68b77ab3d91a715dd59444a62e2e`，产品代码与父提交 `e4b4aed9140e05541a23e7f871b89cfda8e71b85` 相同。本地导入/检索/重启是User Verified；不是独立全库验证或L3完整Pass。复评为User-directed review waiver / No Independent Pass，剩余安全风险保留。未推送/合并，不以main旧版本替代此固定输入。

P3-146本地对话/草稿/有限上下文可复用；P3-143/144历史真实DeepSeek与凭据合同需定向核对，P3-145不视为真实最终Pass。不能为省事复制旧真实DB/凭据，也不能恢复“仅会话保存Key”或缩减Provider列表。

## 架构与交互

沿用UI→Application→Domain/Capability→Ports→Adapters。Source、Memory、Context Resolver与ModelPort单一权威，不新增第二记忆库。提问后本地自动检索，不要求手点组装；提问保存失败保留草稿、幂等重试。无匹配时诚实说明，不用固定建议伪装真实模型回答。

披露预览包括用户问题、实际来源片段、目标Provider/模型以及预算；配置/秘密疑似内容、未解析附件、撤权或失效版本不进入模型。片段不是全文件、更不是全目录上传；模型接收的文本必须与获准预览一致。来源变化、移除或撤权后旧预览失效；提交后防重复发送，失败重试不得自动发送。

回答有明确发送中/成功/失败/超时状态。引用ID从实际请求来源集合映射，模型虚构引用不得成为证据；模型理解不自动变为用户确认事实。普通回答不强制反馈；用户纠正只更新受影响状态，保留时间与来源关系。此任务不做OCR、转写、真实网页抓取或目录外文件读取。

## 允许范围与禁止范围

拟工程写入 `lifeos/engineering/LIFEOS-P3-148/`，主报告 `lifeos/deliverables/LIFEOS-P3-148_source_backed_ai_conversation.md`，评审/证据 `lifeos/reviews/LIFEOS-P3-148/`。精确临时根、IPC/DTO和新表方案在工程启动前固定；源候选只读，不能混改147。无关文件、Frozen资产、风险和Stage不变。

拟复用已导入本地数据，不重新扫描Vault、不重复导入；实际 `/Users/xxe/Documents/LifeOS-Source-Pilot-1/capture.sqlite` 的访问与对话/反馈保存需要本任务明确批准。优先无旧库迁移方案；若需Schema变化、备份或复制真实数据，单独展示方案，当前不实施。

真实DeepSeek仅用户逐次确认后的最小披露，无后台发送/自动fallback/其他Provider/工具调用/同步。API Key用户在App输入，保持既有批准的加密凭据语义；不让用户把Key发给Agent。凭据实现路径和存储边界需核对固定代码后明确，不凭历史印象设计。真实问题/来源/回答不进日志、截图、AX、Evidence、hash或Git。

## 验收合同

| ID | 必须结果 |
|---|---|
| A01 | 提问一次保存，失败保留草稿，重复重试不重复写 |
| A02 | 本地按相关性/版本/权限/预算检索，来源无匹配诚实为空 |
| A03 | 预览与实际发送逐字绑定，变更/撤权使旧预览失效 |
| A04 | 只向获准DeepSeek目标发送，未确认零发送，无隐式fallback |
| A05 | 请求状态、答案和错误均可见；重复点击/超时不自动重复发送 |
| A06 | 引用能回到真实获准来源，不接受模型伪造引用或提升为事实 |
| A07 | 反馈与纠正影响对应理解，重启保持且旧版本不复活 |
| A08 | 现有Settings/Provider/凭据/来源和高保真交互不回退 |
| A09 | 合成验证、用户真实亲验与安全结论分别记录，不外推 |

按L3处理新增真实发送和凭据边界，但不机械重做旧安全评审。P3-147跳过复评的决定不自动免除新增148边界；也不重试/改写被平台拦截测试。正式工程合同必须明确本任务可执行的验证与用户风险决策，未明确不宣称安全Pass。环境暂停checkpoint续跑，包内普通修正无需新任务。

## 两条互补路线

147本地功能交付（主线推送/合并待用户授权）→本任务来源支撑的AI对话。

同时保留B线：iPhone健康采集方案（不另装App的用户偏好继续继承，具体可用机制尚未验证）、真实外链内容获取（147仅注入式模拟）。二者的方案核对可并行，不依赖148全部结束；真实设备/网络/目录外授权与实现另列完整结果范围。不能把“已导入健康示例”写成持续同步。

## 当前允许的下一步

### 2026-09-08 续办核对

用户要求“继续下个任务”。本轮只读核对确认：P3-147 `candidate/src/main.rs` 明确未链接生产凭据和 Provider 模块；因此不能把已有本地来源 App 当成已具备真实 DeepSeek 发送能力。`candidate/src/repository.rs` 已有 drafts、feedback、conversation records 和 turn_identity 唯一索引，可复用，不先新建另一套对话存储。上述为源码事实，不代表真实数据库已检查或无需迁移。

同时，b3f6 的 CURRENT_STATUS 仍停在 P3-144，与 P3-147 交付及用户亲验进度不一致。工程启动前须由 PM 对齐最新任务登记与该固定交付的关系；不得让专项按旧状态重启历史工作。本轮未修改旧账本、未读取真实 DB、未启用凭据或网络。

下一执行顺序仍在同一 P3-148 内：先完成代码级存储/凭据/API差异清单与账本对齐；完整展示新增真实边界后取得一次批准；再实现、合成验证、必要安全评审和用户逐次真实发送。当前文件仍是 Draft，不虚报工程已启动。

仅合同设计与只读代码核对，形成精确存储/凭据/网络/API清单后一次向用户展示，不连续追问技术细节、不启动真实发送。P3-147可先准备只读Git差异与敏感资产排查，未获明确L3推送/合并授权不执行外部写入。本文件不自动创建专项会话或后继任务。
