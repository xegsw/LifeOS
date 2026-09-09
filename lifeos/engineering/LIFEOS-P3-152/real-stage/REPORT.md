# P3-152 真实阶段增量交付

状态：Partial / Awaiting user action。真实App已启动，尚未由用户确认实际回答成功。需PM跟踪用户结果；独立评审继续暂停，不宣称Independent Pass、风险关闭或整体Complete。

## 授权与实现

PM根据用户对精确新配置清单的“好吧”“继续吧”确认，批准新根与加密配置；随后完整核对R01–R08，明确合成回归和构建通过后可直接启动。提案与摘要/审批依据见design/acceptance-supplement-proposal.md和pm-approval.json。本增量未扩大旧配置库或旧Keychain权限。

真实运行固定 /Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1；根/.runtime/tmp为0700，marker/DB/sidecars为0600。App检查所有权、no-follow、marker和外来顶层内容，冲突停止。conversation.sqlite按已披露方案保存本地未加密对话；provider.sqlite保存加密API Key及必要本地模型配置。未改成session-only。

密钥材料使用com.lifeos.p3-152.aead-key.v1及精确p3-152-key-32lowerhex账户，拒绝旧引用。设置读取仅元数据；用户保存/替换/删除或确认发送的解密才进入CredentialPort。没有模型列表/连接测试/旧凭据fallback。

新增controlled-real编译开关，与编译环境模式严格匹配；真实synthetic-driver组合编译拒绝，真实test构建也有静态拒绝。UI/IPC不能切换运行根。真实初始库没有合成来源记录、确认记忆或短期状态，健康Reader仅连接既有精确只读目标。真实本地澄清由Host固定文案生成，客户端不能经本地commit伪造真实模型回答。

真实UI显示实际受控连接、API Key、本地存储说明和“确认发送给DeepSeek”；原披露/单次确认/失败草稿/取消语义保留。真实模型回答只能来自ModelPort。模型ID由用户本地输入或已有选项选择，不自动联网。

## 验证和阶段矩阵

| 增量 | 结果与证据 |
|---|---|
| R01 | 编译与启动通过；runtime_root固定路径/marker权限实现，synthetic根内新根及外来内容拒绝测试；real-driver-rejected.log明确拒绝real driver。 |
| R02 | App启动成功意味着其本地根/业务库初始化守卫通过；Agent未读取真实目录/DB/内容或hash。代码保证，不冒称独立文件审计。 |
| R03 | 既有只读Reader和合成正负路径复用；真实分支禁止fixture初始化/seed，实际健康读取体验等待用户。 |
| R04 | 合成AES-GCM/revision/删除/泄漏回归通过；新service/account静态核对；真实Keychain保存和解密尚待用户App操作。 |
| R05 | 既有IPC字段/表保留，mode=real及文案增量；no-seed和Host固定本地答复新增测试通过；UI脚本语法检查通过，不抓取真实UI。 |
| R06 | 既有40项Host/8项集成中的预览/单次消费/取消/失败等通过；真实服务请求与回答等待用户逐次确认，不由Agent测试。 |
| R07 | 固定启动回执通过；Agent无真实AX/截图/正文/日期/Key/hash。仅自身进程core限制与输出抑制，不修改全局系统设置，不保证OS绝不诊断记录。 |
| R08 | 40/40 Host，8/8 TS→Host，真实构建成功；随后固定launch_controlled.py已执行，仅收到controlled_conversation_started。真实闭环仍Awaiting user action。 |

三组先前mutation与不受影响的GUI证据保留，不重做无关阶段；本增量无真实截图证据且不应补取。原合成189项及报告未改写，完整副本置synthetic-baseline，原Manifest原样保留。原根新增real-stage后其旧“精确文件库存”校验不适用于整个扩展目录；使用本阶段tools/verify_synthetic.py复算原189项内容，或在归档副本运行verify_package.py。

五类计数：P0=0、P1=0、P2=0、Unknown=1、Not Implemented=0。Unknown归并为真实端到端用户操作结果（含实际Keychain/健康上下文/真实回答），不能因启动成功而关闭。合成阶段此前0/0/0/0/0不追溯改写。

## 启动事实及用户入口

evidence/controlled-launch.json记载PID25223、固定bundle二进制和SHA256 e1bcc0f6aa62cb4d3f5ae6b3abcc66b050bc570a712936451207f2fed28161b9。此为启动时身份，进程随后可能由用户关闭。Agent没有代点发送，也没有读取真实窗口。

窗口标题为“LifeOS P3-152 - Controlled Conversation”。用户进入 Settings → 模型设置，在API Key字段输入并“保存凭据”，由系统提示完成钥匙串授权；输入所用模型ID并点“选择模型”。选择模型本身不联网。输入健康问题后先点“发送”准备披露，检查实际内容，只有再点“确认发送给DeepSeek”才进行真实请求。若出现本地澄清，可直接回答。

用户只需告知是否成功看到回答或固定错误提示，无需提供Key、真实正文、健康值或截图。若失败，草稿保留，手动重试需重新准备和确认。旧配置不复用、不清理。

## 交付与保留

本增量目录real-stage包含候选、验收/审批、日志、固定启动脚本、checkpoint和非自指Manifest。自动复跑只使用合成根，不启动真实App。已启动App保持打开，真实数据资产保留；未经新授权不覆盖/清理外来内容。

本报告为同任务增量；原合成报告保持只读。没有push/merge、账本更新、风险关闭、冻结或后继任务。下一步只等待用户在已启动App内完成操作及PM记录结果。
