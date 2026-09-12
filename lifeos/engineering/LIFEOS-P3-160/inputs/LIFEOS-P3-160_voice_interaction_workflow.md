# LIFEOS-P3-160｜实时语音交互并行工作流完整合同

日期：2026-09-12。Revision 1。唯一结果：原来的完整 LifeOS + 统一主动引擎 + 语音输入输出，在同一个 App 中联合验收。
状态：A 离线实施由用户本次“启动语音并行工作流”明确授权；B/C 新真实麦克风、MiMo、免点击云端发送、凭据配置和联合真实切换为本合同待一次批准部分。不能用旧“允许”代替。
用户明确要求并行，因此新增独立工程工作流，不让同一专项混做两个活动任务；P3-159 原合同、工程、进度和授权不暂停/回滚/重开。

## 1. 组织、角色、风险与成功定义

主责：新 Codex 语音工程任务，能力要求本地 Rust/Tauri/音频适配、确定性测试、受控完整 App 构建。隔离是避免并发写文件，不是另起产品。
原工程任务 01a07f0e-dbbd-7d23-9e6d-68f2152f9484 独占对话/主动/行动及最终合并。PM 维护协议、基线、任务账本与验收。
专业检查点：技术/音频可靠性，数据/凭据与传输最小化，AI 信任/权限，体验/原 UI 延续；Gate 1～5 分别记录，不宣称全局 Stage 变化。
整体 L3，A 离线执行按 L2 行为证据，B/C 使用独立任务验收依据及 Manifest/逐行矩阵。沿用户此前暂停独立评审的明确安排，不另开评审；状态 User Exception / Paused，不称 Independent Pass、不关闭风险。
只有正常无键盘唤醒、多轮、插话、自然业务回应持久化、旧能力不回退及联合验收成立，才可申报完整交付；音频单项通过仅 Technical Partial。

## 2. 共同完整产品基线与运行身份

- 已核对完整快照提交：46829c74eeb83c270a3258949c5d27db5bdea296，当前分支 codex/p3-159-unified-proactive。
- 完整源对象：该提交 lifeos/engineering/LIFEOS-P3-159/baseline/candidate/ 全部 182 文件。清单摘要 27e0dbc86579157fbf148c3959fdb3e6beb4f73de77b9bf03e56e7747b719879。
- 清单权威输入：PM 树 tasks/LIFEOS-P3-159_baseline_identity.json；快照内 baseline/identity.json 同时核对。不得从 main、旧 HEAD 工作工程或文件夹标题推断完整产品。
- P3-159 当前增量：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-159/candidate/，正在修改，仍 A 阶段，尚未验收。182 是共同祖先，不是“已包含主动引擎全部最新变动”的谎称。
- P3-160 worktree 必须从上述精确 commit 建立，自己的 candidate 原样继承完整 182 文件，再只增加语音 delta。工作流不写 b3f6，不复制其正在写的未提交文件充当稳定输入。
- 最终集成以原工程 P3-159 当时最新完整候选为目标，仅移入经核对语音增量及原工程自己完成的共享接线；绝不能用 P3-160 的旧基底覆盖 P3-159 新增能力。
- 实际产品血统：D0674 完整在线合成包 /private/tmp/lifeos-p3-158-main-chain-v1/build/signing-v1/D0674/LifeOS P3-158 Online Test.app；bundle local.lifeos.p3-158.main-chain。D0674 binary SHA256 5da41bea4fb18da7e8e8d12f796b68fbe7d949906328f334cb9170e5d54b4443。
- 最新工程报告 P3-159 实际完整离线 App 试运行后为修复布局正常退出；不把这个 PID 或历史真实 PID 当当前存活状态。本任务不停止任何现有 App。
- 真实用户数据链仍为 P3-159 合同列出的既有生产根；旧 P3-157 真实验收未通过事实保持，不能因并行启动追认。
- 继承既有 Cargo/Tauri/frontend/source-engine 构建；禁止 Voice App、第二套 Shell、业务运行时、导航、Provider 体系、用户库和专用 Memory。

继承清单：Shell/Today/Global AI/键盘草稿；资料来源/授权/附件/健康导入和恢复；原记录/记忆/安排/行动与事务回执；设置/模型目录/API Key 保存及重启；D0673 输出策略/D0674 长停顿恢复；P3-159 主动生命周期和自然回应。先差异和行为测试，再必要视觉补证，不重做已验收模块。

## 3. 公共接口和唯一写入者

规范为 PM 树 lifeos/contracts/LIFEOS-INTERACTION-V1.ts 及 .md，双方必须同一 hash。
UserTurn 统一键盘/语音 final；AssistantTurn 统一宿主终局文字/问题/建议/真实回执；ProactiveCandidate 直接封装原 Evaluation；ProactiveDecision 仍由原引擎产生；SpeechOutputRequest 仅宿主发；SpeechInterrupted 无业务状态含义。
细节、幂等、会话关联、失效和晚到规则见规范，属于本合同一体附件，不得各自重定义。
对普通聊天的语音免点击发送是新许可，不改变原键盘逐次发送确认。没有许可时可离线完成全部接线，但不能偷偷自动联网。

| 写入者 | 独占范围 | 其他方怎么接 |
|---|---|---|
| PM | 上述公共规范及本合同/验收/账本 | 同语义补齐由 PM 对账；扩大边界再问用户 |
| P3-159 原工程 | proactive_*、上下文/反馈/事务、Today/Global AI 原入口、InteractionPort host bridge、现有主文件注册/路由/设置容器、最终构建入口 | voice 提供独立模块和明确 patch 建议，不直接改这些源文件 |
| P3-160 | 自己 candidate 的 src/voice/、application/voice/、audio 原生适配、MiMo voice adapter、wake/VAD/playback/session、语音专属测试/构建依赖说明 | 不写主动业务、原行动提交、通用 Provider/凭据生命周期或设置主文件 |
| 最终集成 | 仍是 P3-159 原工程，在同一完整候选应用 voice delta | PM 发精确 source/commit/hash/diff，先检查无基线文件倒退 |

A 阶段语音若需 lib.rs/Cargo.toml/build.rs/Tauri capability/设置主入口注册，提交 integration_patch.md 和最小补丁，由唯一集成人应用；可在自己的完整候选建立未应用补丁下的测试 target，不对外宣称已集成。
允许新增 audio-only host adapter 边界，建议 voice_control / voice_status 两个严格 IPC（enable/disable/end_session/stop_playback/status），由集成人登记；不是把旧 14 业务 command 改义。不得接受任意文件、URL、系统命令、key 回读或 caller authorized=true。全部业务仍调用原入口。
实际原生采集/播放只在同一 Tauri host 内，FFI helper/library 不是另一个业务进程；不引入本地 HTTP 服务或第二 Runtime。

## 4. 实现链路与真实服务事实

本地唤醒检测 -> 唤醒后音频/VAD -> MiMo ASR -> final UserTurn -> 既有对话/DeepSeek/记忆/主动/Action -> validated AssistantTurn -> LifeOS 明确 SpeechOutputRequest -> MiMo TTS -> 流式播放 -> 本地插话中断 -> 下一 UserTurn。

公开官方协议已核对：
- ASR：mimo-v2.5-asr，https://api.xiaomimimo.com/v1/chat/completions；单个 wav/mp3 base64 音频消息；stream=true 是 SSE 转写文字输出。第一版用 VAD 分句后上传，不能宣称麦克风音频 WebSocket 实时上行。ASR 仅转写，不带历史、记忆或指令式业务提示。
- TTS：mimo-v2.5-tts，同一官方 API 路由，使用内置 mimo_default，目标文本放 assistant；stream=true、pcm16 输出。实现按官方实际 delta/audio 及采样规格验证，先合成 fixture 再真实验证。禁止 voiceclone/voicedesign、参考用户音频或第二个 MiMo 推理脑。
- 本地 wake/VAD：优先 sherpa-onnx keyword spotting + 本地 VAD，通过可替换端口。默认拟用“你好，小欧”（可本地改）；用实际模型验证词表，不将识别测试脚本假作产品唤醒。锁定发布版本/模型 hash/许可证后才打包；代码许可证不等于模型商用许可。模型许可不明时保留准确缺口，不擅自替换成云唤醒。
- 首轮平台 macOS，复用当前 Tauri 产品；原生麦克风/回声消除优先 AVAudioEngine voice processing。接口保留跨平台适配，但 Windows/安卓实机未经验证不能称已支持。

官方依据：
ASR https://mimo.mi.com/docs/en-US/api/audio/Speech-Recognition
TTS https://mimo.mi.com/docs/usage-guide/speech-synthesis-v2.5
价格 https://mimo.mi.com/docs/en-US/price/pay-as-you-go
本地 KWS https://k2-fsa.github.io/sherpa/onnx/kws/index.html
模型许可边界 https://k2-fsa.github.io/sherpa/onnx/kws/apk-cn.html
这些页面是事实输入，不能把示例脚本的文件写入/联网行为当用户授权。

## 5. 音频生命周期与交互

voice 默认关闭。用户启用后、App 运行且系统未锁定时，本地麦克风持续检测唤醒；不是唤醒后才第一次开麦克风。系统麦克风权限由用户操作，不代点、不绕过。
唤醒前只用有界 RAM 环形缓冲做本地识别，不上传、不写盘；检测完成后仅采集唤醒后的话语上传，默认不带唤醒前音频。界面持续有清楚但克制的麦克风状态。
本地状态：disabled / wake_listening / capturing / transcribing / awaiting_assistant / speaking / recovering。它们是音频会话状态，不是任务/建议业务状态。
VAD 结束初值连续静音 800ms，可用合成声学场景调到 500～1200ms；单段最多 60 秒（资源边界），到边界完成一段后允许继续下一段，不使整个话题失效。不把空白/背景噪声提交成用户意图。
ASR 有效 final 后释放音频；失败/取消/超时同样释放，不自动重传。用户可重说或用文字；已形成的文字草稿保留，部分识别明确不完整且不自动执行。
插话先本地停播，无需等 ASR/云端；停止目标为本地 speech onset 到停播 p95<=250ms，在固定硬件/环境记录实测，不能只测 mock 时间。取消 TTS、清队列、隔离迟到 chunk。保留前一真实回执和下一句开头。
播放与监听共享单一设备链并有回声抑制/AEC，测试自己播报不会自唤醒/自提交、不会吞掉用户插话。不能靠播放时关麦克风冒充可打断。
无声持续 60 秒退出活跃语音会话、回本地 wake listening；不清业务会话、不丢长停顿输入、不改 D0674。不用 session idle 计时中断仍在录音/播放或处理中操作；结束会话后的晚到回答保留文字、不自行发声。
窗口失焦不销毁文本输入；App 隐藏时不新增主动分析/主动播报（P3-159 原规则）；用户正在语音交互的普通语音会话可完成当前句。锁屏/设备丢失/权限撤回立刻停采集停播、释放 RAM；恢复须符合开关/权限，绝不重放旧音频。
无需新导航：现有设置内一个“语音”折叠区（开关、状态、MiMo 配置、唤醒词、用量），现有对话一个状态/停止入口。不要再做管理面板或密集按钮。

## 6. 服务、披露、凭据与预算：B/C 待一次批准

下列全部是本轮新提案，不冒称旧许可已经覆盖。A 可实现其关闭默认和拒绝/撤回测试。

### 6.1 三个分开的用途

1. voice_asr.v1：MiMo 接收用户唤醒后当次话语音频（单段<=60秒），只为转写。环境声在录音时可能一起上传，启用页必须说明，不能声称只传说话者或已匿名。
2. voice_tts.v1：MiMo 接收当前允许播报的 AssistantTurn 文本，含必要建议/依据简述，且仅在已唤醒活跃会话内。DeepSeek 旧授权不等于向 MiMo 分享回答。不上传整段历史、资料正文包、个人路径、附件、密钥或隐藏推理。
3. voice_session_turn.v1：在已唤醒会话中，final 文本经现有 LifeOS 网关自动发送至现有已选 DeepSeek deepseek-v4-pro / https://api.deepseek.com/chat/completions，无需逐句点“发送”；这是新的会话内发送许可，不扩大理解/行动用途、原工具/写入权限，也不修改键盘模式。新许可关闭/会话结束后普通逐次确认恢复。主动回应仍走 P3-159 原语义及范围，两项许可均满足；该许可不覆盖日常无唤醒后台监听外发。

MiMo 的服务端保存/删除/训练政策不能由本地“释放录音”保证，真实启用前须在范围页给出适用服务条款/隐私链接和已核实说明；未知如实标示，不能声称零留存。
最小披露：ASR 无生活上下文；TTS 无业务背景包，仅核准输出；DeepSeek 复用既有有界 packet，但每次上限仍须满足本合同和 P3-159 中更严格者。语音不新增可读来源集合。
C 初始范围限定普通项目/安排/当前会话回应及已在 P3-159 勾选的来源；高敏健康/医疗/心理/财务/法律、凭据、二进制不纳入自动 TTS/背景发送。用户自己说出的音频无法在上传前可靠语义筛选，启用页清楚提示勿说未愿上传内容；权限层不能虚称先识别再保证音频不外发。

### 6.2 现有存储和 Key

真实目标唯一沿用 /Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/ 现有 conversation.sqlite/provider.sqlite/owner/锁和 SQLite 副文件。A Agent 不探测/读取/复制这些真实资产；B/C 获批后仅 App Host 按用途操作。
MiMo Key 由用户在同一个完整 App 的原设置系统输入，复用 backend CredentialPort/加密存储和现有解锁生命周期，只加独立 voice profile/用途绑定，不覆盖 DeepSeek 选中模型。前端仅输入瞬间持有字段并立即清空，不存 localStorage、日志、明文配置或 IPC 返回值。
不增加 Key 过期 TTL，不逐句弹密码，不改钥匙串 ACL/信任、不导出密钥、不另建 vault。若后台取凭据需系统交互，停语音并在设置提示一次，由用户处理；不能绕过。
允许在既有 typed JSON 控制命名空间新增 voice:policy/voice:budget/voice:profile 引用等小字段；沿现有 provider 存储协议增加 MiMo voice 类型。它们是用途配置，不是独立业务库。若实际需 DDL、迁移、加密/owner/核心 Provider 协议改变，先给出精确差异一次审批。
ASR final 按原 records/conversation 流保存，与键盘文字相同，标语音转写来源；不双写 voice memory。会话音频、PCM/TTS cache 均 RAM-only，不落库、不留调试文件、不发遥测。
A 合成音频 fixtures 允许保存在自己的测试根；不能误用用户录音当合成样本。B/C Agent 不看/取音频、真实正文、Key/密文或内容 hash；只收非内容事件/计数/错误码。

### 6.3 可执行资源边界（不是厂商限额）

| 项目 | B 真实服务+合成资料 | C 日常语音初值 |
|---|---|---|
| ASR | 开发32、未见16，共48次POST；音频总<=20分钟 | <=10次/分钟、300次/本地日、60分钟/日；单段<=60秒 |
| TTS | 开发32、未见16，共48次POST；文本总<=24000 Unicode字符 | <=10次/分钟、300次/日；一次文本<=4000 Unicode字符，长回复由同一请求投影分段，最多3段/回复；多余完整文字仍保留 |
| DeepSeek语音接线 | 新工作流独立开发32、未见16，共48次POST；不得消费P3-159未见额度 | <=60次/日；每UserTurn现有协调最多6次模型/2次已有只读工具，每次输入<=24576字节且正文<=8192；原更严格规则优先 |
| 并发 | ASR1、TTS1、业务提交1；B按场景顺序 | 同左，播放/采集可重叠以便打断 |
| 超时 | 连接15秒、ASR单请求60秒、TTS首音15秒/闲置15秒/单请求120秒；0自动重试 | 同左；不是整轮对话倒计时 |
| 资源 | wav单声道16kHz PCM16，base64请求<=4MiB；ASR响应<=256KiB；TTS解码音频<=8MiB/请求、播放队列<=2秒 | 同左，超出明确失败/保留文字，不执行部分识别 |

失败、超时和发送未知均消耗预留次数；取消不能退款重置，跨重启/时钟回拨/开关不清账。HTTP429区分厂商限流与本地预算；无自动重试/备用服务/模型切换。闭环多轮不限固定话题时长，但仍受这些明确费用/资源边界。

截至2026-09-12官方国内价格为 ASR ¥0.5/小时，TTS限时免费。这不是永久价格承诺。当前B20分钟对应ASR公开标价约¥0.17，C每日60分钟约¥0.50，另有DeepSeek实际token费用。
合同承诺的是以上次数/时长/字符/响应资源上限，不承诺人民币总额封顶；DeepSeek输出沿D0673不加任意偏低max_tokens，usage缺失记Unknown。禁止自动充值/买套餐。
真实启用前核实账户区域/普通API计费和当时价格；若TTS开始收费、价格/模型/区域不同，显示具体差异一次确认，不能依据旧“限时免费”放行无限费用。用户未批准本节前 POST=0。

### 6.4 关闭和撤回

设置随时一键关语音：停本地麦克风、播放器/ASR/TTS、新网络请求，generation隔离在途结果；关ASR/TTS/语音自动发送可分别撤回用途。已发数据不能声称撤回服务端。
保留原业务记录/记忆/推迟/拒绝/真实回执与计数，不清用户数据；重新启用不重播、不重新提交旧 ASR。故障始终可回文字，没有MiMo Key也不影响DeepSeek原文字能力。
用量通知只在既有语音状态区一次呈现，不能循环抢焦点/密码弹窗；不因语音失败把主动引擎关掉。

## 7. 一个并行工作流内的实现顺序

A0 立即：核对共同精确快照、规范hash、创建完整继承candidate和checkpoint；声明文件所有权、无真实访问，向PM回报。P3-159照常开发。
A1 立即：本地音频/VAD/wake端口、流解析/队列/generation、InteractionPort consumer、权限/预算/关闭/错误恢复。使用合成PCM/网络stub/可控时钟，不开真实麦克风/扬声器、不取Key、不POST。
A2 立即：MiMo协议adapter、原生驱动编译、设置子组件、真实代码路径的离线故障/竞态/回归；形成最小集成patch，由原工程接线。不得等159全部结束才开始这些工程。
依赖下载仅公开官方代码/模型/文档，无用户资料；需先核许可证/固定版本hash，工程报告列下载目标与是否需要新的执行环境权限。未下载可编译端口/替身，但不能把缺模型记成wake通过。
A3 联调离线：两个增量可以在159阶段边界逐步集成；不要求159先宣布Complete。固定共同机器协议，键盘/语音同路径行为、主动安静与播报分离、原设置/数据/Action回归。先做，不等真实许可。
B 待一次真实批准：A关键安全/继承通过、MiMo Key在App输入、用户麦克风授权后，用同一完整合成App做真实MiMo+非敏感合成语音/文字+有限DeepSeek接线验证。禁止纯裸API结果当App通过；开发和未见场景分离；测试合成源不得假声冒充真人麦克风通过。
C 待批准且A/B通过：原工程以最新159+160完整累积源构建、签名、核对单实例，在第8节同一个正式验收包运行；正常切换用户授权旧包，不重建库。用户实际无键盘联合验收，Agent只取非内容回执。延期实际到期未观察则Pending，不假装周末已实测。
实现/测试/同范围修复/证据/联调/最终验收留同一160工作流；不拆唤醒、ASR、TTS、打断为多次需开工的小任务。

## 8. 合并与最终 App 切换

唯一最终候选仍为 b3f6 lifeos/engineering/LIFEOS-P3-159/candidate/ 加已核对语音delta；最终用户验收包仍 /private/tmp/lifeos-p3-159-unified-proactive-v1/build/LifeOS.app。
bundle ID local.lifeos.p3-158.main-chain；沿既有签名 LifeOS P3-158 Local Development Signing（SHA1 7490dc97208f45420c4dfc9c48ddf6f59113b6f4），不创建第二身份/修改ACL/信任。该联合包切换为B/C待批准部分，不由voice线自动打开覆盖。
P3-160 test根 /private/tmp/lifeos-p3-160-voice-v1/ 只存合成夹具/构建/测试完整包，窗口清楚标合成；不是第二套真实产品或用户数据。不使用其中的包替换真实App。
集成前双方提交 scoped code delta 和文件/hash/依赖列表；必要本地代码提交只含本任务文件，不推main、不git add全仓。原工程在其最新候选逐项应用并跑联合矩阵；共享文件冲突由其处理，不重置/回滚另一线。
切换只允许批准后精确识别当前生产App正常退出、确认锁释放、签名/模式/源摘要/DB owner检查成功再启动。同一时刻一个真实写入者，不强杀/删锁/迁移/清旧数据。
原对话、API Key、Provider选中项、资料与健康、任务、主动snooze/suppress/correct必须跨联合构建及正常重启保持。新音频结构不得让旧库不可读；发现无法不迁移则停C，不影响可继续的A。

## 9. 验收、证据与失败

独立判据：tasks/LIFEOS-P3-160_acceptance_basis.md（A执行判据确定；B/C待一次批准锁定，不冒称当前全合同获批）。
先代码/配置/接线差异和继承防回退，再实际行为、声学计时及必要UI；截图不证明唤醒/识别/打断/事务。真实音频不得进入证据，B合成音频可留版本/许可，C仅非内容计时/事件和用户判断。
任何漏接主链、错目标写入、声学回声自执行、拒绝/延期失效、越权传输/泄Key、原App回退、假成功都是阻断。关键Unknown/NotImplemented不能用测试数抵消。
真实联合场景：免键盘唤醒 -> 当前确有价值的主动建议播报 -> 用户中途插话“这个周末再说”及变体 -> 本地停播 ->ASR标准UserTurn ->原引擎持久推迟 ->正常重启不提前提醒 ->到期有效则重评，已完成/撤权/过期则安静。键盘始终可用，拒绝/纠正/多目标/话题切换同链验证。
真实“周末”未到不能改系统时间假验收；可用户明确一个近期真实时间验证到期，周末语义由B受控时钟验证并区分报告。

## 10. 输入、输出、边界与可恢复执行

最小启动包以PM树 /Users/xxe/.codex/worktrees/5ed8/No.2 为当前治理权威，不用新worktree旧索引覆盖它：
根AGENTS.md、CURRENT_STATUS.md顶部现行条目、本合同/验收依据/两个公共规范、P3-159合同/identity/批准记录；执行worktree根AGENTS同时读取，有冲突回PM，不混用旧任务权限。
定向必读：PM_OPERATING_MODEL.md风险触发评审/累积产品责任/核验职责/恢复/一次性授权；ROLE_MATRIX.md PM/数据/AI信任/技术/体验；STAGE_GATES.md Gate1～5及例外；ACCEPTANCE_GOVERNANCE.md累积产品/核验顺序/状态；CI_CD_GOVERNANCE.md；模板SESSION_REPORT_TEMPLATE.md。不要求全历史评审。
允许写本工作tree的 lifeos/engineering/LIFEOS-P3-160/、deliverables/LIFEOS-P3-160_voice_interaction.md；不修改PM账本、159工程、旧deliverables/Evidence/真实根。integration_patch是建议，不自行改别线。
输出：完整delta/manifest、依赖许可证记录、协议适配/联合集成清单、tools/verify_voice.py --offline（要实现，不冒称现成）、ABF逐行结果、checkpoint.json、简短增量报告。Manifest只含代码/合成资产/非内容计数，不hash真实内容。
checkpoint含合同/基线/接口hash、共同祖先/本线/已合并source身份、完成/未完行、真实POST计数、排除失败、精确测试根、resume_from。锁屏/runner/凭据等待记Paused—Resumable，只暂停受影响阶段，不停159。
合同边界外真实权限/接收方/数据/存储协议/外部系统/不可逆操作必须一次差异确认；同范围实现、缺陷修复、性能调优、接口语义不变的字段补齐直接继续。
非范围：外部设备/全天系统后台/声纹/克隆/远场阵列/系统控制/语音自有任务状态/第二数据库/大UI重做/公证上架/自动购买或GitHub发布。

## 当前可执行与待批结论

当前立即启动 A0～A3，读取/研究公开技术资料及合成离线实现；不等待主动引擎完成。
第6～8节 B/C 的真实麦克风、MiMo用途与凭据、语音会话内免点击发送、所列调用预算/数据使用/联合真实App切换，需要用户对本完整合同一次批准。批准后仅产品内启用及系统权限操作，不再逐项询问工程开工。
最终验收仍是同一个完整LifeOS，无“voice单项通过=产品完成”。产品方向不重新确认。

