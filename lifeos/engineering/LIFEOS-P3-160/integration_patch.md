# P3-160 最小集成建议（A 离线，尚未应用）

唯一接收者：P3-159 原工程；目标是其最新完整 candidate。禁止整体复制本线 candidate 或 cherry-pick 182 文件基底覆盖159。先按 delta_manifest.json 只取 src/voice/ 与 application/voice/；共享文件由159独占修改。

共同祖先 46829c74eeb83c270a3258949c5d27db5bdea296，182文件摘要27e0dbc86579157fbf148c3959fdb3e6beb4f73de77b9bf03e56e7747b719879。
公共 TS 8234e7eb9523f5b8ea7114f50ef24acece5cbadfce8b98d92cdcc6b14b2bbafc；语义MD 8dfdda556dfc05274d1cdf155614023122601f17d765725e56fd163a48a547f7。

## 共享接线由159应用

1. `src/main.rs`（已核对现有主模块注册位置）增 `mod voice;`。模块仅依赖已有 serde/serde_json/zeroize，不修改核心业务DTO。Rust interaction-v1 mirror归159，按公共TS往返fixture对账。
2. `application/voice/consumer.ts` 构造参数为既有 `InteractionPort` 和 `VoiceHostPort`。只订阅host final和SpeechOutputRequest，不订阅模型候选/partial，不改键盘草稿或发送确认。真实final的turnId由host分配，session+segment+摘要绑定和回执恢复必须由既有requests事务持久去重；consumer的RAM去重只作辅助。`SpeechInterrupted`只更新播放状态，不能修改Action/推迟/拒绝。
3. `application/voice/settings.ts` 的折叠片段放入原设置，由原容器绑定purpose/control事件；默认available=false。不新建导航/Provider UI。MiMo配置走现有加密CredentialPort，前端不回读Key。两个严格音频IPC建议 `voice_control` / `voice_status`；control仅enable/disable/end_session/stop_playback/status，未知字段拒绝，不能接受key/URL/path/authorized=true。
4. `BudgetStore::compare_save`在原控制命名空间`voice:budget`短事务实现；持久预留成功后才可POST。load失败/损坏必须拒绝，不能初始化空账抹额度；只有首次用途配置在事务中创建新账。开关/重启/失败不退款。当前ledger算法提供离线行为，宿主需落实持久事务和可信本地日。B的开发/未见额度不可混用。
5. Host SpeechOutputRequest registry解析：检查活跃唤醒session/generation/policyRevision、对应已验证AssistantTurn、projectionRef/assistantTurnRef版本、proactive surface决定及可见性、撤权/完成/纠正失效和内容范围；按同一回复最多3个投影片段、单请求最多4000 Unicode字符。原文完整保留。不得将frontend任意文本传给tts_request。同turn恢复展示不重播；明确再读才新request。
6. `mimo.rs`只构造官方协议与增量SSE，不自己取凭据/网络。语音侧`native/MiMoHTTP.swift`已实现固定URL、ephemeral无缓存/无cookie、拒绝重定向、流分片/取消/背压。由同一host把该transport接入`gateway.rs`，复用原CredentialPort；语音链不需159重写。固定ENDPOINT，禁止重定向/代理/自动重试。ASR上传仅唤醒后单声道16k PCM16 WAV；TTS24kHz PCM16LE mono。真实凭据只在原backend生命周期，后台需要交互时暂停并给一次设置状态提示。
7. macOS原生：`AudioEngine.swift`与`MiMoHTTP.swift`编译为同进程library，正常A编译没有LIFEOS_VOICE_REAL，start恒拒绝。真实代码目前只编译验证。实际B/C未授权，不添加该编译定义、麦克风usage/capability或自动启动设备。B/C后由159构建集成Swift库、framework/rpath/签名/麦克风用途声明；使用相同AVAudioEngine做AEC采集与播放。宿主须在App退出、锁屏、权限撤回、设备丢失时调用stop，并隔离所有回调；不得自动点击系统权限。
8. sherpa-onnx v1.13.7 C adapter已编译/链接官方arm64 no-tts库，固定下载hash见依赖证据。后续模型作者README的Apache-2.0声明、固定Revision/SHA256与“你好小欧”词表已经核对，见assets.lock.json。真实模型已加载并执行合成静音/噪声/本机合成话语测试；不代表真人麦克风通过。模型路径只由host解析已核hash的打包资源，不受IPC caller控制。VAD/KWS在音频worker串行调用；不在UI线程或音频tap内跑推理。A fake必须标签contract fake。

## A3 联调所需回执

原工程可先在阶段边界接离线consumer及BudgetStore/registry contract fake，再替换为其生产InteractionPort。回传共同接口hash、集成source/hash、联合测试结果。原设置/Provider/Key保存重启、资料/健康/Action/主动snooze/suppress/correct由最新159候选回归。未提供此回执前本线只记Technical Partial，不称生产联调通过。

本建议不改变159合同、进度、共享所有权或真实权限。ASR/TTS/DeepSeek实际POST=0，真实麦克风/扬声器未开；B/C待完整合同一次批准。


## f5a64094 后的同范围运行链补充

`native.rs`提供NativeAudio有界回调通道/停播/释放、NativeWake/NativeVad、NativeTransport和瞬态CredentialAccess。音频/HTTP回调只传PCM/固定状态，宿主在一个音频worker上驱动`Worker::accept`和Gateway；不须重新实现采集、解析或网络主体。新Swift availability入口使A在取CredentialPort之前就拒绝网络。库必须从同一编译模式配套链接；不得把真实库混入A。

Host需把Worker的Woke绑定canonical session；Utterance只送Gateway ASR；Gateway完整Final交canonical UserTurn映射；SpeechOutputRequest由Authority registry解析后送Gateway TTS；Pcm经Playback有界队列送NativeAudio；Interrupted先NativeAudio.interrupt和Gateway.cancel(Tts)，再reportSpeechInterrupted。来源/权限失效同样停播隔离。每次驱动都核healthy，overflow立即停设备/取消请求并恢复到文字。Poll timer覆盖连接/首音/闲置/总时限，终局调用NativeTransport.completed释放callback context。

语音自动发送预算Purpose::SessionTurn须在原协调每一次实际模型POST前预留，不能只按一个UserTurn预留一次而放行其最多6次内部调用；原159更严格限制继续适用。

assets.lock.json固定6个模型/词表/许可文件，可用tools/prepare_voice_assets.py离线校验，显式--download-public才从锁定公开URL获取。现仅放task-local测试缓存，不把系统Tingting合成语音或第三方示例录音打包进产品。最终打包/资源许可副本由唯一构建者随同一App保留，缺asset时失败关闭。
