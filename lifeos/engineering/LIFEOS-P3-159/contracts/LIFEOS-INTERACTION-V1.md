# LifeOS 公共交互协议 v1

状态：2026-09-12 PM 协调定义，允许两工作流进行离线加法适配；不新增真实权限，不冻结全局领域模型。
规范类型：同目录 LIFEOS-INTERACTION-V1.ts。类型与本语义文件一起使用，TypeScript 不是安全验证器。

## 单一入口与权限

键盘与 ASR final 进入同一 submitUserTurn。由既有对话宿主确定话题、主动关联、理解、权限和 Action 事务。
语音 final 原样保留，标记 voice/asr 来源，不冒充核对过的录音原文；中途转写只作易失预览，不提交、不写记忆。保留原键盘草稿。
turnId 由宿主分配；sessionId+segmentId 绑定唯一 turnId 和请求摘要。重送相同对象恢复原回执，换文本沿旧 ID 拒绝，换 ID 不能重用已消费 segment。
只有正常完成、合法终止原因和非空的 ASR final 可提交；断流部分文本不假装 final。识别错字通过正常对话纠正；涉及有歧义/高影响操作由原链澄清/确认。
conversationRef、replyTo、presentedProactiveRef 是输入开始时的上下文快照，不是自动确定目标，更不是授权。宿主复核版本、会话、当前话题；晚到结果不得注入别的对话。
UI/音频回调不能持有数据库、Action、Memory、SQL、文件或任意网络工具入口。

## 输出与主动决定

AssistantTurn 来自现有宿主终局输出，原文回复/问题/建议/真实事务回执/错误分别标明。模型原始候选、推理流、工具流及尚未提交的“成功”不得进入播报。
ProactiveCandidate<T> 的 T 直接复用 P3-159 src/proactive_contract.rs 的 Evaluation 类型及其机器协议，不再定义一份模型 Schema。
ProactiveDecision 由 P3-159 在权限、价值、依据、抑制/推迟、预算、免打扰和当前版本检查后产生；voice 不生成或修改决定。
surface 不必然播报。LifeOS 的会话语音策略还须核对活跃已唤醒会话、语音用途授权、内容范围和预算，才发 SpeechOutputRequest。
silence 没有可播对象；不能播“我保持安静”，也不能开 TTS 连接制造提示。
无用户活跃语音会话时，首版保持 Today 文字建议，不因 voice enabled 自动在房间出声。唤醒进入会话后，可表达一条仍有效、值得关注的建议；不绕过 P3-159 的打扰决策。
同一 assistantTurnRef 的恢复展示不重复发声。后续用户明确“再读一遍”可发新 request，但不能当一次新主动展示。
projectionRef 是宿主 registry 内对当前可播文本的只读引用；只包含这次回答和必要 whyNow/依据简述，不转发上下文包、记忆、原始资料或日志。
建议朗读必须保留推断和依据身份。事务回执播报内容从真实 receipt 渲染，不能从模型“已经完成”推导。

## 中断、竞态与多轮

本地有效插话首先停止声卡队列、递增播放 generation、取消当前 TTS 和丢弃晚到音频，再报告 SpeechInterrupted。
SpeechInterrupted 只反映播放，不代表用户拒绝、同意、取消 Action、推迟提醒或回滚事务。
插话录音走 ASR -> 新 UserTurn -> 原业务链。语音层不得匹配“周末”“取消”等词处理业务。
打断之前事务已提交则仍已提交，反馈依真实回执；网络返回晚到则按原提交隔离规则处理，不擅自撤销。
音频 generation 与业务 requestId 分离；停止说话不删除业务结果。更换会话、撤权、依据失效时尚未播完的旧输出停播；不影响文字回执恢复。
来源撤权/完成/纠正导致主动对象失效，P3-159 发失效/新投影，桥接层撤销关联播放许可；无需语音层自行读来源库。
一次 ASR/一次 TTS 可分别并发以支持插话；单一麦克风/播放器/用户 turn 提交通道，带背压，不无限排队。
语音会话闲置退出只停止音频收集/返回本地唤醒状态，不使用户对话回合过期；数小时后仍能在原对话继续。

## 公共文件所有权与版本

PM 独占这两份规范文件。P3-159 原工程拥有 InteractionPort 生产实现、主对话入口/路由、主动适配及最终集成。
P3-160 只实现 voice 侧适配与注入的 InteractionPort consumer。A 可用明确标识的 contract fake 验证端口，不得假称已联调。
两边使用同一规范字节 hash；Rust mirror 由原工程接线所有者维护并做跨语言往返 fixture 一致性测试。
原 v5/v7/v8 及 proactive-v1 业务 DTO 保留不改义。新增 envelope 不作为第二份业务对象/数据库表；从既有 records/requests/receipt 派生。
需要新增物理 schema/加密/核心 API 语义时回 PM 给出一次差异；模块内部参数/同语义字段纠错留在本任务。

