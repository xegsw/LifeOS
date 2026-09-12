# P3-152 完整累积恢复 Closure Contract 提案

状态：进行中，关键接口/存储待PM核对。用户要求一次处理完整后再结束；不再按单组停止，不另建微任务。当前工程起点为health-view-restoration完整候选，其Manifest dbe63f0423a4908f14622155962862ed923533b64f8b165bde20df07ac13c7aa只证明修复起点，不自动成为整产品权威。原各包只读保留。

## 唯一结果与累积基线

在同一个Tauri候选内，保留当前设置、自然对话与辅助健康查看，接回来源管理、来源检索/原文详情/统一对话、健康文件导入。所有已实现控制须有合成运行与持久化证据，不能仅放禁用菜单。真实启用仍限既有许可；尚未允许的来源/导入操作在真实模式明确不可执行。最终累积源码和bundle均来自本目录candidate/Cargo.toml，不分别启动多个产品App。

| 继承输入（工程根均为本worktree lifeos/engineering） | 权威范围与实际能力 |
|---|---|
| LIFEOS-P3-142 candidate/ui/app.js、P3-143 candidate/src/runtime.rs | 已实现设置层级、云/本地选择与非敏感持久化；高级覆盖/fallback编辑当年非可用功能，不扩大 |
| LIFEOS-P3-147 candidate/src/source_api.rs/source_worker.rs/source_store.rs/source_file.rs 与application/ui.ts | 5命令的目录接入/任务控制/授权/状态/原文检索详情；实际来源处理。真实模式历史外链授权仍禁止 |
| LIFEOS-P3-148 candidate/application/source_conversation.ts、conversation_flow.ts、source_ui.ts及conversation_contract.rs | 来源问题/引用/披露/确认/取消/历史语义，接入当前152同一对话，不复活另一聊天Shell |
| LIFEOS-P3-149/S3/closure-3 candidate/src/apple_health.rs/apple_health_api.rs及tools/apple_health_source.py、application/apple_import.ts | XML/ZIP解析、事务/重复/skip/unprojected和合成App进度；历史真实导入是受控独立入口，不伪称原有真实文件选择器 |
| LIFEOS-P3-150/R1 Reader与readonly.js；当前health-view-restoration完整候选 | 三指标只读语义、按需辅助查看和已有对话/设置。保护已通过62/12/12影响面 |
| lifeos/prototypes/LIFEOS-P3-116 app.js/styles.css | 视觉和已确认交互依据；完整Me/Context/Memory/AI Workspace/Quick Capture原型不凭名字算生产能力 |

精确历史hash继承inheritance-audit/input-identity.json，新增读取的代码在本包输入清单记录。未逐项证实的其它旧能力标未知，不声称本提案覆盖全仓历史。

## 集中IPC与存储差异

1. 保留现8命令/v4/v5及get_today v2。新增/接回147同名5命令，Raw version1 payload严格继承：connect_source_directory、control_source_job、get_source_status、authorize_source_target、get_source_evidence。不新增任意路径输入。另接import_apple_health_file Raw version1 payload action=list/status/start、file为固定合成文件列表标识，继承149严格类型/4096byte边界。上述总计14公开命令。
2. 工程实现采用包内私有source-engine Rust库模块（path dependency），复用149中累积147来源实现及149解析器/事务逻辑。该库不是另一个App、服务或外部进程；原来源/健康解析子进程预算沿用。原因：旧repository与152typed Store同名但接口/生命周期不同，直接替换会破坏设置/对话。来源库保持独立SourcePort适配，不暴露旧对话/Provider/凭据API。新增path dependency仅本地Cargo锁条目，不新增网络依赖或技术栈。
3. 新合成来源资产根固定 `/private/tmp/lifeos-p3-152-health-conversation-v1/complete-source-engine`，属于当前已授权自有任务根，独立0700/0600所有权marker及fixtures/.runtime/tmp/artifacts。根内按Host已有fixture标识分隔库；UI不能选fixture或路径。来源仓储复用历史repository/source_store私有表及apple-file记录，不将这些表迁入真实conversation.sqlite。真实模式必须在任何source-engine文件访问前拒绝未授权的来源/导入操作。旧运行根/个人目录字面量不作为任何回退路径。
4. 仅在合成模式，已完成导入的当前fixture健康库可作为辅助Reader/健康SourcePort的输入；未导入继续既有合成fixture。不写当前真实健康库；导入失败不发布新健康观察、原库不清空。导入不自动授权AI：仍经过152既有health-demo授权记录与逐次披露。更新/重复/失败在同一候选内可观察。
5. 来源对话通过桥接将当前有效的有限来源片段转换为152 typed source_projection引用。来源身份、sourceRef/version/grant generation必须保留；最多3来源+2状态/记忆、4096字节及既有披露预算不扩大。从来源搜索结果提问进入同一全局输入；不把点击详情等同发送。准备/最终确认再次检查SourcePort当前授权、版本、断开/刷新状态；失效旧packet/引用。可将有限派生投影保存到现有合成records/sources，原文仍在来源仓储且不可被静默改写。真实模式不生成Obsidian派生记录或外发来源。
6. 来源状态与手动刷新可串行拉取有界结果，活动导入进度仅在当前管理页可见时轮询，离开停止；目录worker沿既有授权任务动作运行。无云/HTTP/DNS外链新增；合成外链仍注入离线adapter，真实外链关闭。

这些为组合接线与兼容适配，不冻结新架构/Schema；请PM批准私有SourcePort仓储隔离、14命令总量、合成健康输入选择和typed引用桥接后实施。实现中若发现该最小设计不能维持原合同，集中补充精确差异，不暗中换成重新实现的简化功能。

## 接回顺序与综合验收

先固定新私有引擎和权限守卫 → 来源管理/检索/原文详情 → 统一对话引用及失效 → 真实隔离的健康导入/进度/幂等/失败/Reader关联 → 同候选综合回归。设置/草稿/健康辅助全程保留。

综合合成行为覆盖：启动空态不自动读来源；连接→处理状态→检索→分页详情→暂停/恢复/刷新/断开/目标授权与撤权；同对话提问→实际有限披露→明确确认→回答引用→来源改变旧确认拒绝；XML/ZIP导入→概要/详情可读→同文件不重复→坏文件保持先前观察→非支持/未知计数诚实；保存设置/重启、切页草稿、失败/取消/迟到；任意路径/错误DTO/越界/权限/旧根访问拒绝。明确原实现未支持的模式，不用假成功或静态菜单补数。

验证优先代码diff/实际Rust与TS→Host测试，复用未受影响测试和GUI。增加少量合成实际Tauri证明所有入口共存，至少完成一条来源到对话和导入到辅助查看的跨页链。真实仅构建统一bundle，不启动、不关闭当前25223、不覆盖当前bundle或并发同库。每个阶段写checkpoint，完整目标未满足不报Complete。

## 新真实权限集中清单（尚未执行）

当前授权仅既有健康库只读、新对话/加密配置库及DeepSeek逐次健康发送。恢复合成工程不需新增个人目标。

仍待PM向用户集中明确的真实delta：
- 来源管理/检索：唯一允许源目录与来源缓存/派生库存储的精确路径、读/复制/写及后台worker范围；此刻没有授权精确路径，禁止猜测或探测旧Source根。
- 非健康来源真实对话：哪些来源/片段可在逐次披露后给DeepSeek；不能从健康外发许可推导Obsidian外发许可。
- 真实健康重新导入：唯一XML/ZIP原件精确路径、目标健康库写入、重试次数/并发锁/资产保留要求；152当前只读不覆盖这些动作。历史受控尝试不可直接延续。
- 安全切换：用户保留草稿并退出当前真实App后，才能安排新bundle；不由Agent自动关闭或并发启动。

上述合成集成全部完成后统一汇报真实差异与切换，不要求用户逐条批准工程细节。若缺少真实新权限，工程继续完成可授权部分，但最终结论仍区分“统一候选已恢复并合成验证”和“真实启用尚未完整”，不称完整真实产品已验收。
