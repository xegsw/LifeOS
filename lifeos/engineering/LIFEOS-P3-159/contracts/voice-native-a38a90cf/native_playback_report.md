# P3-160 native 播放完成与背压增量

状态 Technical Partial / A3 Pending。响应159同任务的最小native端口需求。仅语音native层增量：新增PlaybackLedger.swift，修改AudioEngine.swift与native.rs；既有create/push ABI和NativeAudio::enqueue保留兼容，公共interaction协议/host registry/投影/持久业务没有改动。旧快照及manifest保留。

## 语义与适配

PlaybackLedger是生产AudioEngine使用的设备无关状态机，固定容量48000个24kHz单声道samples（2秒）。每个接受buffer分配生命周期内不复用token；回调包含native generation、token、该generation累计已播放samples、回调时queued samples。仅AVAudioPlayerNode的dataPlayedBack回调计入已消费，不把schedule成功或HTTP EOF计为播放。

停止/打断先推进generation并清空ledger，再停止player、清零释放buffer。回调先按generation/token消费ledger，通过后才访问buffer对象ID，防止旧回调误删新buffer。重复/未知token和旧generation无反馈。Rust侧独立有界反馈channel（8条），interrupt/stop排空旧反馈；poll_playback再过滤旧generation。channel溢出沿healthy失败关闭并stop，不能以丢反馈后的计数宣称完成。

| 新Rust方法/反馈 | 159调用方式 |
|---|---|
| interrupt(); playback_generation() | 在新输出前停止旧播放并取得native generation，存入host request→local playback epoch→native generation映射。原来的interrupt签名不变。 |
| enqueue_for(generation, pcm) → buffer_token | 先voice_validate_playback并核对request/local epoch，然后按保存的native generation入队；禁止用“当前generation”重标旧PCM。空/奇数/超96000bytes拒绝；实际剩余容量由原生锁内再检。旧enqueue仅兼容，159新链使用enqueue_for。 |
| playback_status(generation) | 原生同一锁下快照：queued_samples、available_samples=48000-queued、consumed_samples累计、sealed、drained。旧generation报错。快照不预留容量，enqueue仍重新检查；回调里的queued是当时值，当前容量以快照为准。 |
| finish_stream(generation) | Host收到HTTP EOF先进入draining，并确保其所有已验证PCM（含本地待入队数据）都已enqueue后调用一次。封闭后禁止再enqueue。此调用本身不等于播放完成；无buffer/重复seal/旧generation/未启动设备拒绝。 |
| poll_playback() → PlaybackFeedback | 普通反馈buffer_token>0、drained=false；累计consumed_samples不是增量。当前generation所有已入队buffer dataPlayedBack且finish_stream已封闭后，仅一次token=0、drained=true。可能最后buffer先于EOF播放完，此时finish_stream同步排入drained反馈。Host再次voice_validate_playback，且确认当前request为draining，再调用其voice_playback_completed。 |
| healthy() | 每轮事件处理/入队/宣称完成前检查。false即停原生、清本地队列并失效host播放，不凭旧回调升级完成。 |

C ABI新增create_v2、push_v2（out token）、finish_stream、playback_status、generation，全部同进程。Rust Input::Samples/DeviceStopped枚举不变，播放反馈独立获取；不增加IPC或服务。159编译Swift库和real分支typecheck时，需将candidate/src/voice/native/PlaybackLedger.swift加入原有两个Swift文件列表。两个本线verify脚本已更新，host build.rs仍由159唯一修改。

取消TTS时同时停止本地Playback和NativeAudio，取消Gateway TTS并丢弃待入队PCM/stream完成信号。不要finish_stream已取消generation；不要把旧drained归到新request。保留原文字链、并发ASR和业务状态。真实用途未授权时不得调用start/真实enqueue；A只使用fake。

## 验证与证据

复跑入口：python3 lifeos/engineering/LIFEOS-P3-160/tools/verify_playback.py。实际结果 evidence/native-playback-20260912T213025/result.json：生产ledger纯fake测试通过，Swift A库构建及real分支仅typecheck通过，3项Rust→Swift测试通过（原A麦克风拒绝、HTTP凭据读取前拒绝、新反馈generation/溢出测试）。新测试没有start；两个原拒绝测试只调用A硬禁用分支，不打开设备。

ledger fake覆盖满队列拒绝、重复token、乱序完成、EOF后draining、全部buffer先于EOF播放完成、重复seal、取消/旧epoch回调、跨代token、无音频封闭拒绝、1000次容量释放重用。3个mutation均先编译成功，再被precondition杀死：放宽容量、移除seal的generation核验、未seal即drained。失败mutation日志保留为负向证据。Rust新测试以显式fake C回调验证旧反馈排空/过滤、字段传递和channel溢出失败关闭；不是实际设备完成回调证明。

本轮设备实际打开0、实际播放0、MiMo/ASR/TTS/DeepSeek POST0、凭据读取0。真实dataPlayedBack触发时序、声学及同一App host联调仍Unknown/Pending。此前30 Rust/4 fake测试及旧UI失败保持历史归属，本轮不冒充重新复跑所有App回归。

## 交接与关卡

相对93c98bb0（也是59d8e2ef的生产源码）仅1新增2修改，delta_since_93c98bb0.json给before/after，delta_manifest_v4.json给全量18项voice身份。不得覆盖182基底。PM/159按固定blob接入并用其稳定SpeechOutput端口完成同一App离线联合验证。专项工程检查通过上述范围，不是A Pass、Independent Pass或真实能力验收；无需新的Task Contract。

## 159 TTS稳定接口对账（同轮收到）

已读取voice-speech-handoff-20260912T133014/manifest.json及其中voice_speech.rs固定拷贝，后者SHA256 b6bb254225c77247cd72a2f6d267840a6e6c5d170674b1f880103bc2dc2852eb校验通过；本线保留inputs/A3-speech-20260912T133014/，未读其余4项活跃或拷贝文件，不宣称复核其完整测试。

该接口的voice_gateway_poll_tts返回Complete只记draining，与本增量finish_stream及drained反馈匹配。159只需在其已保存request/native generation映射匹配、healthy通过、收到drained且快照queued_samples=0后，重新voice_validate_playback并调用voice_playback_completed。可见性继续使用其宿主回调，原生层不制造visible=true。取消顺序使用其voice_gateway_interrupt_tts前先清本地/native队列的约定。本次只做稳定接口对账，没有把建议安装到159候选，也未验证同一App运行。
