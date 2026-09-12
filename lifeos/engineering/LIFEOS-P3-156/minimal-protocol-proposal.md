# P3-156 最小协议差异提案 v1 — 需 PM 确认

2026-09-10。任务卡明确要求“新增关键实体、Schema/API/公共IPC/权限必须先明确差异并获批准”。当前只完成方案与基线复制，未实施以下协议。不请求重复启动授权。

## 唯一结果与不变边界

正常聊天中明确表达直接记下/更新本地安排，只有歧义才问一句；没有采纳/保存/完成按钮。完整继承155，不新增导航、任务看板或第二任务库。仅固定156合成根、离线模型和合成数据库；不访问或迁移真实库，不启动controlled-real，不替换当前App。14个公共命令名称及v4/v5既有请求/响应保持兼容。

## 请求批准的有限差异

1. 在TypeScript新增Action领域DTO、纯状态迁移函数、ActionRepositoryPort及Application服务。Action是架构已有领域的本轮接线；字段为id、version、confirmedContent、status(planned/completed/cancelled)、createdAt、updatedAt、confirmationRawRef、sourceRefs。历史事件有eventId、previousVersion、operation、rawRef、timestamp；不得覆盖原始表达。sourceRefs保留id/version/authorizationGeneration；展示状态独立为valid或needs_user_judgment，不把来源内容复制进Action。
2. 物理SQL Schema不变：在同一records表追加schemaVersion=6、kind=action_event的版本事件，以独立事件ID INSERT，禁止upsert旧事件；在feedback表追加kind=action_feedback，与用户raw record、turnId和eventId关联。当前Action由该ID的连续合法事件投影得到，禁止从最近N条记录推测完整历史。既有states/memories语义不变，不自动生成长期事实。RepositoryPort按业务命名，UI和Domain看不到表名。
3. 仅合成模式允许三个v6操作：resolve_request_context/prepare_action_turn，resolve_request_context/commit_action_turn，get_context_recovery/action_snapshot。未知字段、null、超限、错误命令/版本/模式拒绝；现有16384字节请求上限保持。原v4 draft_turn继续保存草稿。v6不进入send_source_ai_request，不调外部模型。
4. prepare输入requestId、turnId、expectedDraftRevision，返回packetId、expiresAt、原始表达、当前可用来源refs、当前目标集合及版本和可用的最近对话指代上下文。目标集合由Repository读取并绑定本轮packet，不接受模型自报的目标集合。普通恢复不调用prepare。
5. commit输入requestId、turnId、packetId、expectedDraftRevision、candidate及modelId(OfflineA或OfflineB)。candidate只允许create/adjust/complete/cancel/clarify，包含原文跨度、确定目标ID+expectedVersion（create无旧目标）与匹配packet的sourceRefs；不得接受用户外的文本作“确认”。Application确定性校验明确意图、非引用/假设/否定、原文跨度、当前唯一目标、上下文有效期和版本；Host在写事务内重新核对原始草稿/packet、目标版本、来源授权及操作约束。模型置信度不是授权。协议不承诺任意自然语言都可无歧义解析，未支持或不确定表达留在对话并必要澄清，不猜写。
6. clarify只保存对话澄清状态及候选目标引用，使用既有questions表新增kind=action_clarification；不创建Action。澄清回复仍走正常聊天，绑定未过期且版本未变的原始表达/问题/唯一目标；跨重启恢复后继续有效校验。一次只问目标或意图中必要的一项。草稿失败或普通读取不能成为隐式确认。
7. 单事务原子追加raw record、action_event、action_feedback及简短回复，更新草稿已提交和request结果；同request重放原结果，同turn不得创建第二事件，同request不同payload拒绝。失败回滚保留草稿；complete/cancel只从planned迁移，adjust只从planned增加版本；不提供reopen。来源失效不阻止用户明确取消/完成本地记录，但不能将失效refs重新披露为有效或用作新建议；新增/调整所引依据须当前有效。
8. action_snapshot纯读取，返回有界分页的Action DTO、历史版本引用及依据可用状态，最多一个Today Focus；分页与单ID仓储查询保证不会因列表截断把多目标误作唯一。恢复只读，不重新解析模型、不重发请求、不重建安排。受撤权影响的来源正文不返回，Action自身用户确认内容保持；需用户判断用简短中文说明。

## 实现影响与验收

新增领域/仓储/应用文件；改现有会话编排、Today展示、Host v6路由/Adapter与task-local运行配置。原14命令、v4/v5DTO、Provider/加密无TTL和Settings结构不变。Host只做存储边界复核，TS Domain/Application负责核心状态语义。

测试覆盖清晰四操作、唯一/多目标/澄清、引用/假设/否定/沉默、伪造解析/refs/版本、相同提交/响应丢失/重启、事务失败草稿保留、只读恢复零模型零写、来源过期/纠正/撤权、完成取消不复活、OfflineA/B切换及旧能力影响回归。相关视觉只验证聊天输入、状态反馈、Today单Focus与窄窗，不触碰真实窗口。

请PM批准或具体修订上述合成内部v6 DTO及持久化kind语义，并确认此有限接线可留在156；若需用户单次批准，由PM展示本差异后收口。在明确批准前不改候选协议或运行新Action持久化。没有把“SQL表未变”等同于“无关键协议变更”。
