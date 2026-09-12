# P3-159 A SpeechOutput Registry 与 TTS Host Adapter

A-only，实际设备、播放、MiMo、凭据读取为0。production voice模块仍P3-160固定93c98bb0，本增量独占Host实现，未另建App或声音权限入口。

## 已实现接线

- voice_register_speech：只接受Host当前AssistantTurn引用、已唤醒的A session/gen/policy和Host可见性事实，不接受任意TTS文字。持久登记不可变SpeechOutputRequest、当前输出digest和投影引用。相同session/output登记去重；主动输出另登记Host surface decisionRef，不冒用原suggestionRef充当decisionRef。
- SpeechAuthority：按注册request校验session/gen、tts用途、conversation许可、当前AssistantTurn全文digest/projection、主动输出当前surfaced状态与动态可见性。每send/chunk/final重核；TTS文本只取Host最终投影，建议包含whyNow。无有效对象则拒绝。
- voice_gateway_begin_tts/poll_tts：沿原Gateway、VoiceBudgetStore CAS和固定协议，单在途；失败/取消保留预算，不重试。network_enabled仍拒绝A-only会话。
- voice_validate_playback：Gateway已经返回PCM后，在native入队及播放交付边界再次校验；request和local/native播放epoch的映射由串行播放所有者保持，禁止给迟到PCM套新epoch。
- HTTP EOF只进入draining。voice_playback_completed只允许后续native消费完成通知关闭draining，不能根据网络EOF、定时猜测或空HTTP流宣称播完。真实native完成/容量通知仍待160交付，不宣称已接设备。
- SpeechInterrupted：严格匹配已登记请求、session/gen、assistantRef，只写音频状态与幂等事件，不改Action、原文、业务请求或主动反馈。native须先停逻辑/原生队列，再调用TTS-only取消。旧重复打断不会取消新TTS；并发ASR保持。
- ASR joint正向测试改由真实Worker类处理纯fake帧生成Utterance，经实际Host begin/poll到canonical UserTurn与原待授权preview。测试明确Host generation与Worker local epoch不同，不能混用。

## 仍未完成

实际NativeAudio/NativeTransport串行producer、播放完成/背压回调接入和设备/声学/KWS验证；前端可用语音开关仍禁用，interaction_outputs仍不自动发出speechRequests，只有内部Host登记入口可供未来已授权native orchestration使用。本增量不能算语音可用、真实B/C或整体任务Pass。
