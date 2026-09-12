# P3-160 A3 native producer / TTS 最小接线建议与 fake 验证

状态：Technical Partial / Joint Acceptance Pending。输入为159提供的稳定只读接口拷贝，不是活跃候选或新的完整基底。本轮不修改生产源码、公共协议、host/registry/SpeechOutput投影，不开设备、不播放、不读取凭据，ASR/TTS/DeepSeek POST均0。

## 稳定输入与事实

仅先读PM指定的 A-voice-joint-closure.json / A-voice-joint-manifest.json。前者SHA256 592536bf06a2df5af964ab4e6d9545d9d4e013019a5e5e189d36d19a73350b17，后者 3ff3b7d03547b7772211b6933515b59def77b09e44ff3d45019979901cc43f75。两者的sourceFiles映射221项相同；closure自身hash与manifest条目一致。仅核对已读两文件，不声称复跑其308测试/23步骤/2mutation，也不访问manifest中的其他路径。

159随后提供 contracts/voice-joint-handoff-20260912T131710/manifest.json 和3份固定拷贝，本线逐字hash校验并复制至 inputs/A3-host-20260912T131710/。voice_host.rs 7f81fe011ba47e9c88c9035d9d1b656ac230bbfd83ce88bf810063d34b5fa846；interaction_contract.rs ab830136df81f3bc59fd97e0ac3ae3bbd6594501200d9b27675a25537a38666d；interaction.rs 8e20eeb76dc5ca0e084797cb9d68928cd2d8563f372463d906355007bec33e11。只读拷贝不参与本线candidate构建，voice基线仍93c98bb0826b98778dbf4b3daa9ccf102e61de69。

稳定接口事实：Store::voice_gateway_begin_asr生成并返回host Binding，且它内部已经调用Gateway::begin_asr，调用侧不得再调用一次。Store::voice_gateway_poll_asr仅在Gateway完整Final时返回canonical UserTurn。VoiceAsrAuthority拒绝所有非ASR用途，projection返回voice_speech_registry_unavailable；interaction_outputs给出空speechRequests，speech_interrupted拒绝。因而目前不存在可合法接入的生产TTS投影端口。

## ASR native producer 最小适配（由159宿主唯一写入）

| 边界 | 使用已有端口的接线要求 |
|---|---|
| 同线程所有者 | 在宿主现有串行音频循环中拥有NativeAudio、Worker、Gateway、NativeTransport。NativeWake/Vad持有Rc，不跨线程搬运；Store的借用仅在同步begin/poll调用期间保留，不把DB借用放到音频回调。A测试使用fake帧/transport，不调用NativeAudio::start或真实Transport。 |
| 输入 | 每次读取NativeAudio.events前检查healthy；Samples交Worker::accept，随后zeroize原Vec；DeviceStopped/overflow使native.stop、worker.release、Gateway.cancel_all并丢弃残帧。不要把音频、日志、身份或凭据暴露为前端注入入口。 |
| Woke | 本地Worker generation是本地失效令牌，不擅自充当持久registry授权。宿主保存本地epoch与当前host session/generation/revision的绑定；A fixture由159自己的tests显式建立，生产用途仍不开放。 |
| Utterance | 先核对事件本地epoch仍匹配、宿主会话仍有效，再调用worker.session.begin_asr；随后一次调用Store::voice_gateway_begin_asr(&mut gateway, host_session, host_generation, policy_revision, audio, &mut net)。保存返回Binding和本地epoch。不要从前端生成asr/segment/turn id，不重复Gateway::begin_asr。失败释放该音频与本地ASR状态，不自动重发。 |
| 网络帧 | NativeTransport.events中的(request_id,Frame)按已保存Binding路由到Store::voice_gateway_poll_asr。迟到旧id不得取消新的请求。定时调用Frame::Connecting推动超时；healthy失败取消并停输出。 |
| Final | poll返回Some(UserTurn)才提交现有interaction-v1 submit_user_turn路径；Partial、PCM、Utterance均不当文本提交。先确认本地epoch未变，再对worker.session.asr_final使用该本地epoch。canonical turn、授权预览、去重和恢复仍由原host负责，不在voice再建记录。 |
| 完成/错误 | HTTP请求终结时调用NativeTransport::completed(id)释放句柄（fake无需）；ASR错误走现有session.fail或既定恢复入口，保留已消耗预算，不重试。结束/撤权时先停并排空NativeAudio输入队列，再重置Worker；恢复时重新绑定epoch，不能只修改Session忽略native队列。 |

上述是现有方法的调用顺序建议，不是已安装的host补丁。159应在其gateway_joint_tests里，以相同setup/Fake注入Worker输出替代Audio(vec![...])，使用上述实际begin/poll函数，断言只有完整final进入原preview、draft只一份、Actions为空；同时保留其原文字链回归。这样验证同一完整App候选，避免另一套假业务实现。

## TTS / playback 最小衔接（等待159定义其实现）

不新增SpeechOutput协议。沿现有SpeechOutputRequest和Gateway::Authority即可：宿主按requestId解析registry，绑定session/generation/policyRevision、assistantTurnRef/projectionRef，以及主动输出的proactiveDecisionRef和当前可见性。Authority::projection只能返回宿主已核准的最终投影。当前VoiceAsrAuthority明确拒绝，保持如此直到159提供正式实现。

后续播放顺序：核验registry/用途→Session::speak获得播放generation→Gateway::begin_tts→每个Parts::Pcm在入队前再次核验Authority及原播放generation→Playback::push→有界drain→NativeAudio::enqueue。NativeAudio的内部play_generation与Session.playback.generation是两套令牌，不能混用；enqueue没有request参数，宿主必须保留并核验音频的request/epoch，不能把迟到PCM套上当前NativeAudio generation重新入队。首次播放/stop后播放需NativeAudio::interrupt同步其原生generation。A阶段仅用fake sink/Playback，不实例化真实播放链。

打断先同时清空逻辑Playback和NativeAudio排队，再Gateway::cancel(Purpose::Tts)，最后用已登记SpeechInterrupted报告音频事件；不得调用cancel_all取消并发ASR或把打断转成业务取消。禁用/设备丢失/会话结束才取消全部音频请求。撤权发生在parser已返回PCM但尚未入队之间时，Gateway此前的检查不够，sink所有者必须再次检查并清空队列。网络结束仅表示音频接收结束，不等于已播放完毕；实际播放结束/可用队列容量的宿主状态与native完成通知仍需159与本线对账，不能用HTTP EOF或定时猜测宣称播完。

## 本线纯 fake 验证

新增 tools/rust-tests/tests/playback_ports.rs，复跑：CARGO_TARGET_DIR=/private/tmp/lifeos-p3-160-voice-v1/worker-closure-target /Users/xxe/.cargo/bin/cargo test --offline --locked --manifest-path lifeos/engineering/LIFEOS-P3-160/tools/rust-tests/Cargo.toml --test playback_ports。

4/4通过：模拟分块音频唤醒后分段→一次Gateway ASR→仅EOF给Final；流式TTS PCM→停止→迟到旧包拒绝且并发ASR仍活跃；新TTS不受旧request污染；已返回PCM在sink前撤权被阻止；流中撤权取消transport。全部使用显式HostFake/StoreFake/HttpFake与内存Playback，未验证宿主持久registry、真实native producer、原文字链、GUI或声学。

首次新增ASR fixture缺少object字段，被真实严格parser以response_identity拒绝，已补正确fixture。失败日志A3-playback-ports-fixture-invalid.log只作非通过历史，最终A3-playback-ports-fake.log为4通过。不得删失败或将其当生产缺陷。

## 角色与待办

语音专项给出以上最小适配和纯fake证据；159仍唯一实现公共host、registry、投影并在同一完整候选联合复跑。尚需稳定TTS接口及native播放完成/背压消费接线反馈。PM协调A3，真实B/C等待原合同授权；本次没有A Pass、Independent Pass或用户验收结论，不改变历史失败/Unknown。
